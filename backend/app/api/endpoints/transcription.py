"""Transcription endpoints for audio processing."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import tempfile
import os
import uuid

from app.api.endpoints.auth import get_current_user, TokenData
from app.core.database import get_db
from app.core.config import settings
from app.models.audio import AudioFile
from app.models.transcript import Transcript
from app.models.student import Student
from app.services.transcription import TranscriptionService

router = APIRouter()


# Pydantic models for request/response
class AudioUploadRequest(BaseModel):
    """Request model for audio upload."""

    student_id: str = Field(..., description="Student ID associated with audio")
    source_type: str = Field(
        ..., description="Source type: classroom, interview, assessment, etc."
    )
    recording_date: Optional[str] = Field(
        None, description="Recording date (ISO format)"
    )


class AudioFileResponse(BaseModel):
    """Response model for audio file metadata."""

    id: str
    student_id: str
    storage_path: str
    duration_seconds: Optional[float]
    file_size_bytes: Optional[int]
    source_type: str
    recording_date: Optional[str]
    transcription_status: str
    created_at: str
    updated_at: str


class TranscriptResponse(BaseModel):
    """Response model for transcript."""

    id: str
    audio_file_id: str
    student_id: str
    text: str
    word_count: int
    confidence_score: Optional[float]
    language_code: str
    word_data: Optional[Dict[str, Any]]
    created_at: str


class TranscriptionJobResponse(BaseModel):
    """Response model for transcription job status."""

    audio_file_id: str
    status: str
    message: str


def get_transcription_service() -> TranscriptionService:
    """Dependency for getting transcription service."""
    return TranscriptionService(
        project_id=settings.GOOGLE_CLOUD_PROJECT,
        audio_bucket_name=settings.AUDIO_BUCKET_NAME,
        language_code="en-US",
    )


@router.post(
    "/audio/upload",
    response_model=AudioFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload audio file",
    description="Upload an audio file to Cloud Storage and create metadata record",
)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to upload"),
    student_id: str = Form(..., description="Student ID"),
    source_type: str = Form(
        default="classroom", description="Source type: classroom, interview, etc."
    ),
    recording_date: Optional[str] = Form(None, description="Recording date"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    transcription_service: TranscriptionService = Depends(get_transcription_service),
):
    """Upload audio file to Cloud Storage and create database record.

    Args:
        file: Audio file (WAV, MP3, FLAC, etc.)
        student_id: ID of student associated with audio
        source_type: Type of recording (classroom, interview, etc.)
        recording_date: Optional recording date
        db: Database session
        current_user: Authenticated user
        transcription_service: Transcription service instance

    Returns:
        AudioFileResponse with metadata

    Raises:
        HTTPException: If student not found or upload fails
    """
    # Verify student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found",
        )

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".wav"
        unique_filename = f"{student_id}/{uuid.uuid4()}{file_extension}"

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp:
            temp_file = temp.name
            content = await file.read()
            temp.write(content)
            file_size = len(content)

        # Upload to GCS
        gcs_uri = await transcription_service.upload_audio_to_gcs(
            temp_file, unique_filename
        )

        # Create database record
        audio_file = AudioFile(
            student_id=student_id,
            storage_path=gcs_uri,
            file_size_bytes=file_size,
            source_type=source_type,
            recording_date=recording_date,
            transcription_status="pending",
        )

        db.add(audio_file)
        await db.commit()
        await db.refresh(audio_file)

        return AudioFileResponse(
            id=audio_file.id,
            student_id=audio_file.student_id,
            storage_path=audio_file.storage_path,
            duration_seconds=audio_file.duration_seconds,
            file_size_bytes=audio_file.file_size_bytes,
            source_type=audio_file.source_type,
            recording_date=audio_file.recording_date,
            transcription_status=audio_file.transcription_status,
            created_at=audio_file.created_at.isoformat(),
            updated_at=audio_file.updated_at.isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}",
        )
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


@router.post(
    "/audio/{audio_file_id}/transcribe",
    response_model=TranscriptionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start transcription",
    description="Start transcription job for an audio file",
)
async def start_transcription(
    audio_file_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    transcription_service: TranscriptionService = Depends(get_transcription_service),
):
    """Start transcription job for an audio file.

    Args:
        audio_file_id: ID of audio file to transcribe
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user
        transcription_service: Transcription service instance

    Returns:
        TranscriptionJobResponse with job status

    Raises:
        HTTPException: If audio file not found
    """
    # Verify audio file exists
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_file_id))
    audio_file = result.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file {audio_file_id} not found",
        )

    if audio_file.transcription_status == "completed":
        return TranscriptionJobResponse(
            audio_file_id=audio_file_id,
            status="completed",
            message="Audio file already transcribed",
        )

    # Start transcription in background
    # Note: In production, this should be handled by Cloud Tasks or Celery
    background_tasks.add_task(
        transcription_service.process_audio_file, db, audio_file_id
    )

    return TranscriptionJobResponse(
        audio_file_id=audio_file_id,
        status="accepted",
        message="Transcription job started",
    )


@router.get(
    "/audio/{audio_file_id}/transcript",
    response_model=TranscriptResponse,
    status_code=status.HTTP_200_OK,
    summary="Get transcript",
    description="Get transcript for an audio file",
)
async def get_transcript(
    audio_file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get transcript for an audio file.

    Args:
        audio_file_id: ID of audio file
        db: Database session
        current_user: Authenticated user

    Returns:
        TranscriptResponse with transcript data

    Raises:
        HTTPException: If audio file or transcript not found
    """
    # Verify audio file exists
    audio_result = await db.execute(
        select(AudioFile).where(AudioFile.id == audio_file_id)
    )
    audio_file = audio_result.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file {audio_file_id} not found",
        )

    # Get transcript
    transcript_result = await db.execute(
        select(Transcript).where(Transcript.audio_file_id == audio_file_id)
    )
    transcript = transcript_result.scalar_one_or_none()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript for audio file {audio_file_id} not found",
        )

    return TranscriptResponse(
        id=transcript.id,
        audio_file_id=transcript.audio_file_id,
        student_id=transcript.student_id,
        text=transcript.text,
        word_count=transcript.word_count,
        confidence_score=transcript.confidence_score,
        language_code=transcript.language_code,
        word_data=transcript.word_data,
        created_at=transcript.created_at.isoformat(),
    )


@router.get(
    "/audio/{audio_file_id}/status",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get transcription status",
    description="Get current status of audio file transcription",
)
async def get_transcription_status(
    audio_file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get transcription status for an audio file.

    Args:
        audio_file_id: ID of audio file
        db: Database session
        current_user: Authenticated user

    Returns:
        Dictionary with status information

    Raises:
        HTTPException: If audio file not found
    """
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_file_id))
    audio_file = result.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file {audio_file_id} not found",
        )

    return {
        "audio_file_id": audio_file.id,
        "status": audio_file.transcription_status,
        "student_id": audio_file.student_id,
        "created_at": audio_file.created_at.isoformat(),
        "updated_at": audio_file.updated_at.isoformat(),
    }


@router.get(
    "/student/{student_id}/audio",
    response_model=List[AudioFileResponse],
    status_code=status.HTTP_200_OK,
    summary="List student audio files",
    description="Get all audio files for a specific student",
)
async def list_student_audio(
    student_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """List all audio files for a student.

    Args:
        student_id: ID of student
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of AudioFileResponse objects

    Raises:
        HTTPException: If student not found
    """
    # Verify student exists
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found",
        )

    # Get audio files
    result = await db.execute(
        select(AudioFile)
        .where(AudioFile.student_id == student_id)
        .offset(skip)
        .limit(limit)
        .order_by(AudioFile.created_at.desc())
    )
    audio_files = result.scalars().all()

    return [
        AudioFileResponse(
            id=audio.id,
            student_id=audio.student_id,
            storage_path=audio.storage_path,
            duration_seconds=audio.duration_seconds,
            file_size_bytes=audio.file_size_bytes,
            source_type=audio.source_type,
            recording_date=audio.recording_date,
            transcription_status=audio.transcription_status,
            created_at=audio.created_at.isoformat(),
            updated_at=audio.updated_at.isoformat(),
        )
        for audio in audio_files
    ]
