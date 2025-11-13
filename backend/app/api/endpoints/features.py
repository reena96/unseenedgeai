"""API endpoints for feature extraction."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.feature_extraction import (
    LinguisticFeatureExtractor,
    BehavioralFeatureExtractor,
)
from app.models.features import LinguisticFeatures, BehavioralFeatures

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/features", tags=["features"])

# Initialize extractors (singleton pattern)
linguistic_extractor = LinguisticFeatureExtractor()
behavioral_extractor = BehavioralFeatureExtractor()


@router.post(
    "/linguistic/{transcript_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def extract_linguistic_features(
    transcript_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Extract linguistic features from a transcript.

    Args:
        transcript_id: ID of the transcript to process
        db: Database session

    Returns:
        Extracted linguistic features

    Raises:
        HTTPException: If transcript not found or extraction fails
    """
    try:
        logger.info(f"Extracting linguistic features for transcript {transcript_id}")
        features = await linguistic_extractor.process_transcript(db, transcript_id)

        return {
            "transcript_id": features.transcript_id,
            "student_id": features.student_id,
            "features": features.features_json,
            "created_at": (
                features.created_at.isoformat() if features.created_at else None
            ),
        }

    except ValueError as e:
        logger.error(f"Transcript not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error extracting linguistic features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature extraction failed: {str(e)}",
        )


@router.post(
    "/behavioral/{session_id}", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def extract_behavioral_features(
    session_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Extract behavioral features from a game session.

    Args:
        session_id: ID of the game session to process
        db: Database session

    Returns:
        Extracted behavioral features

    Raises:
        HTTPException: If session not found or extraction fails
    """
    try:
        logger.info(f"Extracting behavioral features for session {session_id}")
        features = await behavioral_extractor.process_game_session(db, session_id)

        return {
            "session_id": features.session_id,
            "student_id": features.student_id,
            "features": features.features_json,
            "created_at": (
                features.created_at.isoformat() if features.created_at else None
            ),
        }

    except ValueError as e:
        logger.error(f"Game session not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error extracting behavioral features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature extraction failed: {str(e)}",
        )


@router.post(
    "/batch/linguistic", response_model=dict, status_code=status.HTTP_202_ACCEPTED
)
async def batch_extract_linguistic_features(
    transcript_ids: List[str], db: AsyncSession = Depends(get_db)
):
    """
    Extract linguistic features for multiple transcripts.

    Args:
        transcript_ids: List of transcript IDs to process
        db: Database session

    Returns:
        Summary of batch processing

    Raises:
        HTTPException: If extraction fails
    """
    logger.info(
        f"Batch extracting linguistic features for {len(transcript_ids)} transcripts"
    )

    results = {"total": len(transcript_ids), "successful": 0, "failed": 0, "errors": []}

    for transcript_id in transcript_ids:
        try:
            await linguistic_extractor.process_transcript(db, transcript_id)
            results["successful"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"transcript_id": transcript_id, "error": str(e)})
            logger.error(f"Failed to process transcript {transcript_id}: {e}")

    return results


@router.post(
    "/batch/behavioral", response_model=dict, status_code=status.HTTP_202_ACCEPTED
)
async def batch_extract_behavioral_features(
    session_ids: List[str], db: AsyncSession = Depends(get_db)
):
    """
    Extract behavioral features for multiple game sessions.

    Args:
        session_ids: List of game session IDs to process
        db: Database session

    Returns:
        Summary of batch processing

    Raises:
        HTTPException: If extraction fails
    """
    logger.info(f"Batch extracting behavioral features for {len(session_ids)} sessions")

    results = {"total": len(session_ids), "successful": 0, "failed": 0, "errors": []}

    for session_id in session_ids:
        try:
            await behavioral_extractor.process_game_session(db, session_id)
            results["successful"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"session_id": session_id, "error": str(e)})
            logger.error(f"Failed to process session {session_id}: {e}")

    return results


@router.get("/linguistic/{transcript_id}", response_model=dict)
async def get_linguistic_features(
    transcript_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Get extracted linguistic features for a transcript.

    Args:
        transcript_id: ID of the transcript
        db: Database session

    Returns:
        Linguistic features

    Raises:
        HTTPException: If features not found
    """
    from sqlalchemy import select

    result = await db.execute(
        select(LinguisticFeatures).where(
            LinguisticFeatures.transcript_id == transcript_id
        )
    )
    features = result.scalar_one_or_none()

    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Linguistic features not found for transcript {transcript_id}",
        )

    return {
        "transcript_id": features.transcript_id,
        "student_id": features.student_id,
        "features": features.features_json,
        "created_at": features.created_at.isoformat() if features.created_at else None,
        "updated_at": features.updated_at.isoformat() if features.updated_at else None,
    }


@router.get("/behavioral/{session_id}", response_model=dict)
async def get_behavioral_features(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get extracted behavioral features for a game session.

    Args:
        session_id: ID of the game session
        db: Database session

    Returns:
        Behavioral features

    Raises:
        HTTPException: If features not found
    """
    from sqlalchemy import select

    result = await db.execute(
        select(BehavioralFeatures).where(BehavioralFeatures.session_id == session_id)
    )
    features = result.scalar_one_or_none()

    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Behavioral features not found for session {session_id}",
        )

    return {
        "session_id": features.session_id,
        "student_id": features.student_id,
        "features": features.features_json,
        "created_at": features.created_at.isoformat() if features.created_at else None,
        "updated_at": features.updated_at.isoformat() if features.updated_at else None,
    }
