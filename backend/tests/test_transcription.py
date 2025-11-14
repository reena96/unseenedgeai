"""Tests for transcription service and endpoints."""

import uuid
import pytest
from io import BytesIO
from unittest.mock import Mock, patch

from app.models.audio import AudioFile
from app.models.transcript import Transcript
from app.services.transcription import TranscriptionService


class TestTranscriptionService:
    """Test cases for TranscriptionService."""

    @pytest.fixture
    def transcription_service(self):
        """Create a transcription service instance for testing."""
        # Mock Google Cloud clients to avoid authentication issues in tests
        with patch(
            "app.services.transcription.speech.SpeechClient"
        ) as mock_speech, patch(
            "app.services.transcription.storage.Client"
        ) as mock_storage:

            service = TranscriptionService(
                project_id="test-project",
                audio_bucket_name="test-bucket",
                language_code="en-US",
            )

            # Replace with mocks
            service.speech_client = mock_speech.return_value
            service.storage_client = mock_storage.return_value

            return service

    def test_service_initialization(self, transcription_service):
        """Test transcription service initializes correctly."""
        assert transcription_service.project_id == "test-project"
        assert transcription_service.audio_bucket_name == "test-bucket"
        assert transcription_service.language_code == "en-US"
        assert transcription_service.enable_automatic_punctuation is True
        assert transcription_service.enable_word_time_offsets is True

    def test_get_recognition_config(self, transcription_service):
        """Test recognition config generation."""
        config = transcription_service._get_recognition_config()

        assert config.language_code == "en-US"
        assert config.enable_automatic_punctuation is True
        assert config.enable_word_time_offsets is True
        assert config.use_enhanced is True
        assert config.model == "video"
        assert config.diarization_config.enable_speaker_diarization is True

    @pytest.mark.asyncio
    async def test_upload_audio_to_gcs_success(self, transcription_service):
        """Test successful audio upload to GCS."""
        with patch.object(
            transcription_service.storage_client, "bucket"
        ) as mock_bucket:
            mock_blob = Mock()
            mock_bucket.return_value.blob.return_value = mock_blob

            result = await transcription_service.upload_audio_to_gcs(
                "/tmp/test.wav", "student1/audio.wav"
            )

            assert result == "gs://test-bucket/student1/audio.wav"
            mock_blob.upload_from_filename.assert_called_once_with("/tmp/test.wav")

    @pytest.mark.asyncio
    async def test_upload_audio_to_gcs_failure(self, transcription_service):
        """Test audio upload failure handling."""
        with patch.object(
            transcription_service.storage_client, "bucket"
        ) as mock_bucket:
            mock_bucket.side_effect = Exception("Upload failed")

            with pytest.raises(Exception, match="Upload failed"):
                await transcription_service.upload_audio_to_gcs(
                    "/tmp/test.wav", "student1/audio.wav"
                )

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, transcription_service):
        """Test successful audio transcription."""
        # Mock Speech API response
        mock_word_info = Mock()
        mock_word_info.word = "hello"
        mock_word_info.start_time.total_seconds.return_value = 0.0
        mock_word_info.end_time.total_seconds.return_value = 0.5
        mock_word_info.confidence = 0.95
        mock_word_info.speaker_tag = 1

        mock_alternative = Mock()
        mock_alternative.transcript = "Hello world"
        mock_alternative.confidence = 0.92
        mock_alternative.words = [mock_word_info]

        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]

        mock_operation = Mock()
        mock_operation.result.return_value.results = [mock_result]

        with patch.object(
            transcription_service.speech_client,
            "long_running_recognize",
            return_value=mock_operation,
        ):
            result = await transcription_service.transcribe_audio(
                "gs://test-bucket/audio.wav"
            )

            assert result["transcript"] == "Hello world"
            assert result["confidence"] == 0.92
            assert result["word_count"] == 2
            assert len(result["word_data"]) == 1
            assert result["word_data"][0]["word"] == "hello"

    @pytest.mark.asyncio
    async def test_transcribe_audio_failure(self, transcription_service):
        """Test transcription failure handling."""
        with patch.object(
            transcription_service.speech_client,
            "long_running_recognize",
            side_effect=Exception("Transcription failed"),
        ):
            with pytest.raises(Exception, match="Transcription failed"):
                await transcription_service.transcribe_audio(
                    "gs://test-bucket/audio.wav"
                )

    @pytest.mark.asyncio
    async def test_process_audio_file_success(
        self, transcription_service, db_session, test_student
    ):
        """Test successful audio file processing."""
        # Use test_student fixture (automatically creates school and teacher)

        # Create test audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.flush()

        # Mock transcription result
        mock_transcription = {
            "transcript": "Test transcript",
            "confidence": 0.85,
            "word_count": 2,
            "word_data": [],
        }

        # Mock commit and refresh to avoid transaction issues
        with patch.object(db_session, "commit", return_value=None), patch.object(
            db_session, "refresh", return_value=None
        ), patch.object(
            transcription_service,
            "transcribe_audio",
            return_value=mock_transcription,
        ):
            transcript = await transcription_service.process_audio_file(
                db_session, "audio-1"
            )

            assert transcript.text == "Test transcript"
            assert transcript.confidence_score == 0.85
            assert transcript.word_count == 2
            assert transcript.audio_file_id == "audio-1"
            assert transcript.student_id == test_student.id

            # Verify audio file status updated (in memory, since refresh is mocked)
            assert audio_file.transcription_status == "completed"

    @pytest.mark.asyncio
    async def test_process_audio_file_not_found(
        self, transcription_service, db_session
    ):
        """Test processing non-existent audio file."""
        with pytest.raises(ValueError, match="AudioFile .* not found"):
            await transcription_service.process_audio_file(db_session, "nonexistent-id")

    @pytest.mark.asyncio
    async def test_process_audio_file_already_transcribed(
        self, transcription_service, db_session, test_student
    ):
        """Test processing already transcribed audio file."""
        # Use test_student fixture

        # Create already transcribed audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)
        await db_session.flush()

        with pytest.raises(ValueError, match="already transcribed"):
            await transcription_service.process_audio_file(db_session, "audio-1")

    @pytest.mark.asyncio
    async def test_process_audio_file_failure(
        self, transcription_service, db_session, test_student
    ):
        """Test audio file processing failure updates status."""
        # Use test_student fixture

        # Create test audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.flush()

        # Mock transcription failure and db operations
        with patch.object(db_session, "commit", return_value=None), patch.object(
            db_session, "refresh", return_value=None
        ), patch.object(
            transcription_service,
            "transcribe_audio",
            side_effect=Exception("Processing failed"),
        ):
            with pytest.raises(Exception, match="Processing failed"):
                await transcription_service.process_audio_file(db_session, "audio-1")

            # Verify status updated to failed (in memory, since refresh is mocked)
            assert audio_file.transcription_status == "failed"

    @pytest.mark.asyncio
    async def test_get_transcript_success(
        self, transcription_service, db_session, test_student
    ):
        """Test retrieving existing transcript."""
        # Use test_student fixture

        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)

        transcript = Transcript(
            id=str(uuid.uuid4()),
            audio_file_id="audio-1",
            student_id=test_student.id,
            text="Test transcript",
            word_count=2,
            confidence_score=0.85,
        )
        db_session.add(transcript)
        await db_session.flush()

        # Get transcript
        result = await transcription_service.get_transcript(db_session, "audio-1")
        assert result is not None
        assert result.text == "Test transcript"
        assert result.audio_file_id == "audio-1"

    @pytest.mark.asyncio
    async def test_get_transcript_not_found(self, transcription_service, db_session):
        """Test retrieving non-existent transcript."""
        result = await transcription_service.get_transcript(
            db_session, "nonexistent-id"
        )
        assert result is None


class TestTranscriptionEndpoints:
    """Test cases for transcription API endpoints."""

    @pytest.fixture(scope="class", autouse=True)
    def mock_gcs_clients(self):
        """Mock GCS clients before any endpoint test runs."""
        with patch(
            "app.services.transcription.speech.SpeechClient"
        ) as mock_speech, patch(
            "app.services.transcription.storage.Client"
        ) as mock_storage:
            yield mock_speech, mock_storage

    @pytest.mark.asyncio
    async def test_upload_audio_success(
        self, async_client, auth_headers, db_session, test_student
    ):
        """Test successful audio upload."""
        # Use test_student fixture

        # Create mock file upload
        file_content = b"fake audio data"
        files = {"file": ("test.wav", BytesIO(file_content), "audio/wav")}
        data = {
            "student_id": test_student.id,
            "source_type": "classroom",
        }

        with patch(
            "app.api.endpoints.transcription.TranscriptionService.upload_audio_to_gcs"
        ) as mock_upload:
            mock_upload.return_value = "gs://test-bucket/student-1/test.wav"

            response = await async_client.post(
                "/api/v1/audio/upload",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["student_id"] == test_student.id
            assert data["transcription_status"] == "pending"

    @pytest.mark.asyncio
    async def test_upload_audio_student_not_found(self, async_client, auth_headers):
        """Test upload with non-existent student."""
        file_content = b"fake audio data"
        files = {"file": ("test.wav", BytesIO(file_content), "audio/wav")}
        data = {
            "student_id": "nonexistent-student",
            "source_type": "classroom",
        }

        response = await async_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_start_transcription_success(
        self, async_client, auth_headers, db_session, test_student
    ):
        """Test starting transcription job."""
        # Use test_student fixture

        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.flush()

        response = await async_client.post(
            "/api/v1/audio/audio-1/transcribe",
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["audio_file_id"] == "audio-1"
        assert data["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_get_transcript_success(
        self, async_client, auth_headers, db_session, test_student
    ):
        """Test retrieving transcript."""
        # Use test_student fixture

        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)

        transcript = Transcript(
            id=str(uuid.uuid4()),
            audio_file_id="audio-1",
            student_id=test_student.id,
            text="Test transcript",
            word_count=2,
            confidence_score=0.85,
        )
        db_session.add(transcript)
        await db_session.flush()

        response = await async_client.get(
            "/api/v1/audio/audio-1/transcript",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test transcript"
        assert data["word_count"] == 2

    @pytest.mark.asyncio
    async def test_get_transcription_status(
        self, async_client, auth_headers, db_session, test_student
    ):
        """Test getting transcription status."""
        # Use test_student fixture

        audio_file = AudioFile(
            id="audio-1",
            student_id=test_student.id,
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="processing",
        )
        db_session.add(audio_file)
        await db_session.flush()

        response = await async_client.get(
            "/api/v1/audio/audio-1/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["audio_file_id"] == "audio-1"

    @pytest.mark.asyncio
    async def test_list_student_audio(
        self, async_client, auth_headers, db_session, test_student
    ):
        """Test listing student audio files."""
        # Use test_student fixture

        for i in range(3):
            audio = AudioFile(
                id=str(uuid.uuid4()),
                student_id=test_student.id,
                storage_path=f"gs://test-bucket/audio{i}.wav",
                source_type="classroom",
                transcription_status="pending",
            )
            db_session.add(audio)
        await db_session.flush()

        response = await async_client.get(
            f"/api/v1/student/{test_student.id}/audio",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
