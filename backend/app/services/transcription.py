"""Google Cloud Speech-to-Text transcription service."""

import logging
from typing import Optional, Dict, Any
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audio import AudioFile
from app.models.transcript import Transcript

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio files using Google Cloud Speech-to-Text."""

    def __init__(
        self,
        project_id: str,
        audio_bucket_name: str,
        language_code: str = "en-US",
        enable_automatic_punctuation: bool = True,
        enable_word_time_offsets: bool = True,
    ):
        """Initialize the transcription service.

        Args:
            project_id: GCP project ID
            audio_bucket_name: Cloud Storage bucket name for audio files
            language_code: Language code for transcription (default: en-US)
            enable_automatic_punctuation: Enable automatic punctuation
            enable_word_time_offsets: Enable word-level timestamps
        """
        self.project_id = project_id
        self.audio_bucket_name = audio_bucket_name
        self.language_code = language_code
        self.enable_automatic_punctuation = enable_automatic_punctuation
        self.enable_word_time_offsets = enable_word_time_offsets

        # Initialize clients
        self.speech_client = speech.SpeechClient()
        self.storage_client = storage.Client(project=project_id)

    def _get_recognition_config(self) -> speech.RecognitionConfig:
        """Create recognition config for Speech-to-Text API.

        Returns:
            RecognitionConfig object with settings optimized for classroom audio
        """
        return speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language_code,
            enable_automatic_punctuation=self.enable_automatic_punctuation,
            enable_word_time_offsets=self.enable_word_time_offsets,
            # Enhanced models for better accuracy
            use_enhanced=True,
            model="video",  # Video model works well for classroom scenarios
            # Speaker diarization for multi-speaker scenarios
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=6,  # Teacher + students
            ),
        )

    async def upload_audio_to_gcs(
        self, local_file_path: str, gcs_file_name: str
    ) -> str:
        """Upload audio file to Google Cloud Storage.

        Args:
            local_file_path: Path to local audio file
            gcs_file_name: Destination filename in GCS

        Returns:
            GCS URI (gs://bucket/file)
        """
        try:
            bucket = self.storage_client.bucket(self.audio_bucket_name)
            blob = bucket.blob(gcs_file_name)

            blob.upload_from_filename(local_file_path)

            gcs_uri = f"gs://{self.audio_bucket_name}/{gcs_file_name}"
            logger.info(f"Uploaded audio file to {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logger.error(f"Failed to upload audio to GCS: {str(e)}")
            raise

    async def transcribe_audio(self, gcs_uri: str) -> Dict[str, Any]:
        """Transcribe audio file from Cloud Storage.

        Args:
            gcs_uri: Google Cloud Storage URI (gs://bucket/file)

        Returns:
            Dictionary containing:
                - transcript: Full transcript text
                - confidence: Average confidence score
                - word_count: Number of words
                - word_data: Word-level timestamps and confidence scores
        """
        try:
            audio = speech.RecognitionAudio(uri=gcs_uri)
            config = self._get_recognition_config()

            logger.info(f"Starting transcription for {gcs_uri}")

            # Use long_running_recognize for files > 1 minute
            operation = self.speech_client.long_running_recognize(
                config=config, audio=audio
            )

            response = operation.result(timeout=600)  # 10 minute timeout

            # Process results
            transcript_parts = []
            word_data = []
            confidence_scores = []

            for result in response.results:
                alternative = result.alternatives[0]
                transcript_parts.append(alternative.transcript)
                confidence_scores.append(alternative.confidence)

                # Extract word-level information
                if self.enable_word_time_offsets:
                    for word_info in alternative.words:
                        word_data.append(
                            {
                                "word": word_info.word,
                                "start_time": word_info.start_time.total_seconds(),
                                "end_time": word_info.end_time.total_seconds(),
                                "confidence": getattr(word_info, "confidence", None),
                                "speaker_tag": getattr(word_info, "speaker_tag", None),
                            }
                        )

            full_transcript = " ".join(transcript_parts)
            avg_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores
                else 0.0
            )
            word_count = len(full_transcript.split())

            logger.info(
                f"Transcription completed: {word_count} words, "
                f"confidence: {avg_confidence:.2f}"
            )

            return {
                "transcript": full_transcript,
                "confidence": avg_confidence,
                "word_count": word_count,
                "word_data": word_data,
            }

        except Exception as e:
            logger.error(f"Transcription failed for {gcs_uri}: {str(e)}")
            raise

    async def process_audio_file(
        self,
        db: AsyncSession,
        audio_file_id: str,
    ) -> Transcript:
        """Process an audio file: transcribe and save to database.

        Args:
            db: Database session
            audio_file_id: ID of AudioFile record

        Returns:
            Created Transcript object

        Raises:
            ValueError: If audio file not found or already transcribed
            Exception: If transcription fails
        """
        # Get audio file record
        result = await db.execute(
            select(AudioFile).where(AudioFile.id == audio_file_id)
        )
        audio_file = result.scalar_one_or_none()

        if not audio_file:
            raise ValueError(f"AudioFile {audio_file_id} not found")

        if audio_file.transcription_status == "completed":
            raise ValueError(f"AudioFile {audio_file_id} already transcribed")

        try:
            # Update status to processing
            audio_file.transcription_status = "processing"
            await db.commit()

            # Transcribe audio
            transcription_result = await self.transcribe_audio(audio_file.storage_path)

            # Create transcript record
            transcript = Transcript(
                audio_file_id=audio_file.id,
                student_id=audio_file.student_id,
                text=transcription_result["transcript"],
                word_count=transcription_result["word_count"],
                confidence_score=transcription_result["confidence"],
                language_code=self.language_code,
                word_data=transcription_result["word_data"],
            )

            db.add(transcript)

            # Update audio file status
            audio_file.transcription_status = "completed"

            await db.commit()
            await db.refresh(transcript)

            logger.info(
                f"Successfully created transcript {transcript.id} "
                f"for audio file {audio_file_id}"
            )

            return transcript

        except Exception as e:
            # Update status to failed
            audio_file.transcription_status = "failed"
            await db.commit()
            logger.error(f"Failed to process audio file {audio_file_id}: {str(e)}")
            raise

    async def get_transcript(
        self, db: AsyncSession, audio_file_id: str
    ) -> Optional[Transcript]:
        """Get transcript for an audio file.

        Args:
            db: Database session
            audio_file_id: ID of AudioFile record

        Returns:
            Transcript object or None if not found
        """
        result = await db.execute(
            select(Transcript).where(Transcript.audio_file_id == audio_file_id)
        )
        return result.scalar_one_or_none()
