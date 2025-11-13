"""Tests for transcription service and endpoints."""

import pytest
from unittest.mock import Mock, patch
from io import BytesIO

from app.services.transcription import TranscriptionService
from app.models.audio import AudioFile
from app.models.transcript import Transcript
from app.models.student import Student


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
    async def test_process_audio_file_success(self, transcription_service, db_session):
        """Test successful audio file processing."""
        # Create test student
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)
        await db_session.commit()

        # Create test audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.commit()

        # Mock transcription result
        mock_transcription = {
            "transcript": "Test transcript",
            "confidence": 0.85,
            "word_count": 2,
            "word_data": [],
        }

        with patch.object(
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
            assert transcript.student_id == "student-1"

            # Verify audio file status updated
            await db_session.refresh(audio_file)
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
        self, transcription_service, db_session
    ):
        """Test processing already transcribed audio file."""
        # Create test student
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        # Create already transcribed audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)
        await db_session.commit()

        with pytest.raises(ValueError, match="already transcribed"):
            await transcription_service.process_audio_file(db_session, "audio-1")

    @pytest.mark.asyncio
    async def test_process_audio_file_failure(self, transcription_service, db_session):
        """Test audio file processing failure updates status."""
        # Create test student
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        # Create test audio file
        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.commit()

        # Mock transcription failure
        with patch.object(
            transcription_service,
            "transcribe_audio",
            side_effect=Exception("Processing failed"),
        ):
            with pytest.raises(Exception, match="Processing failed"):
                await transcription_service.process_audio_file(db_session, "audio-1")

            # Verify status updated to failed
            await db_session.refresh(audio_file)
            assert audio_file.transcription_status == "failed"

    @pytest.mark.asyncio
    async def test_get_transcript_success(self, transcription_service, db_session):
        """Test retrieving existing transcript."""
        # Create test data
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)

        transcript = Transcript(
            audio_file_id="audio-1",
            student_id="student-1",
            text="Test transcript",
            word_count=2,
            confidence_score=0.85,
        )
        db_session.add(transcript)
        await db_session.commit()

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

    @pytest.mark.asyncio
    async def test_upload_audio_success(self, client, auth_headers, db_session):
        """Test successful audio upload."""
        # Create test student
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)
        await db_session.commit()

        # Create mock file upload
        file_content = b"fake audio data"
        files = {"file": ("test.wav", BytesIO(file_content), "audio/wav")}
        data = {
            "student_id": "student-1",
            "source_type": "classroom",
        }

        with patch(
            "app.api.endpoints.transcription.TranscriptionService.upload_audio_to_gcs"
        ) as mock_upload:
            mock_upload.return_value = "gs://test-bucket/student-1/test.wav"

            response = await client.post(
                "/api/v1/audio/upload",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["student_id"] == "student-1"
            assert data["transcription_status"] == "pending"

    @pytest.mark.asyncio
    async def test_upload_audio_student_not_found(self, client, auth_headers):
        """Test upload with non-existent student."""
        file_content = b"fake audio data"
        files = {"file": ("test.wav", BytesIO(file_content), "audio/wav")}
        data = {
            "student_id": "nonexistent-student",
            "source_type": "classroom",
        }

        response = await client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_start_transcription_success(self, client, auth_headers, db_session):
        """Test starting transcription job."""
        # Create test data
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="pending",
        )
        db_session.add(audio_file)
        await db_session.commit()

        response = await client.post(
            "/api/v1/audio/audio-1/transcribe",
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert data["audio_file_id"] == "audio-1"
        assert data["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_get_transcript_success(self, client, auth_headers, db_session):
        """Test retrieving transcript."""
        # Create test data
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="completed",
        )
        db_session.add(audio_file)

        transcript = Transcript(
            audio_file_id="audio-1",
            student_id="student-1",
            text="Test transcript",
            word_count=2,
            confidence_score=0.85,
        )
        db_session.add(transcript)
        await db_session.commit()

        response = await client.get(
            "/api/v1/audio/audio-1/transcript",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test transcript"
        assert data["word_count"] == 2

    @pytest.mark.asyncio
    async def test_get_transcription_status(self, client, auth_headers, db_session):
        """Test getting transcription status."""
        # Create test data
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        audio_file = AudioFile(
            id="audio-1",
            student_id="student-1",
            storage_path="gs://test-bucket/audio.wav",
            source_type="classroom",
            transcription_status="processing",
        )
        db_session.add(audio_file)
        await db_session.commit()

        response = await client.get(
            "/api/v1/audio/audio-1/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["audio_file_id"] == "audio-1"

    @pytest.mark.asyncio
    async def test_list_student_audio(self, client, auth_headers, db_session):
        """Test listing student audio files."""
        # Create test data
        student = Student(
            id="student-1",
            first_name="Test",
            last_name="Student",
            grade_level=5,
            school_id="school-1",
        )
        db_session.add(student)

        for i in range(3):
            audio = AudioFile(
                student_id="student-1",
                storage_path=f"gs://test-bucket/audio{i}.wav",
                source_type="classroom",
                transcription_status="pending",
            )
            db_session.add(audio)
        await db_session.commit()

        response = await client.get(
            "/api/v1/student/student-1/audio",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
