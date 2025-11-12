# Audio Processing Capability Delta

## ADDED Requirements

### Requirement: Audio File Upload and Storage

The system SHALL accept classroom audio recordings and store them securely in Cloud Storage.

#### Scenario: Successful audio upload
- **GIVEN** a teacher has a classroom recording
- **WHEN** they upload the file via the API
- **THEN** the file is validated for format (MP3, WAV, FLAC) and size (max 2GB)
- **AND** the file is uploaded to Cloud Storage with unique filename
- **AND** an audio_files record is created with "uploaded" status
- **AND** a transcription job is enqueued
- **AND** the API returns job ID and estimated completion time

#### Scenario: Invalid audio format
- **GIVEN** a teacher uploads an unsupported file format
- **WHEN** the API validates the upload
- **THEN** the request is rejected with 400 Bad Request
- **AND** error message indicates "Unsupported file format. Use MP3, WAV, or FLAC"

### Requirement: Speech-to-Text Transcription

The system SHALL transcribe audio files using Google Cloud Speech-to-Text with speaker diarization.

#### Scenario: Async transcription processing
- **GIVEN** an audio file has been uploaded
- **WHEN** the transcription worker processes the job
- **THEN** the audio file is retrieved from Cloud Storage
- **AND** Google Cloud STT API is called with diarization enabled
- **AND** the operation completes within expected time (5s per minute of audio)
- **AND** transcript text and confidence scores are extracted
- **AND** speaker diarization data is parsed

#### Scenario: High-quality transcription
- **GIVEN** a clear classroom recording with minimal background noise
- **WHEN** transcription completes
- **THEN** overall confidence score is >75%
- **AND** speaker tags are assigned to each word
- **AND** transcript includes proper punctuation

#### Scenario: Low-quality audio handling
- **GIVEN** an audio file with poor quality or heavy background noise
- **WHEN** transcription completes
- **THEN** confidence score is <75%
- **AND** low-confidence segments are flagged for review
- **AND** teacher is notified about quality issues

### Requirement: Speaker Diarization and Student Mapping

The system SHALL identify distinct speakers and map them to students in the classroom.

#### Scenario: Speaker identification
- **GIVEN** a classroom recording with multiple speakers
- **WHEN** diarization data is processed
- **THEN** speakers are clustered by their speaker tags
- **AND** each speaker's total speaking time is calculated
- **AND** teacher speaker is identified (longest speaking time typically)

#### Scenario: Student-speaker mapping
- **GIVEN** speaker clusters and classroom roster
- **WHEN** mapping algorithm runs
- **THEN** speakers are matched to student IDs based on enrollment data
- **AND** teacher speaker is mapped to teacher ID
- **AND** unmapped speakers are labeled as "Unknown"
- **AND** mapping confidence scores are calculated

### Requirement: Transcript Segmentation

The system SHALL split transcripts into segments by speaker and logical boundaries.

#### Scenario: Speaker turn segmentation
- **GIVEN** a completed transcript with speaker tags
- **WHEN** segmentation runs
- **THEN** transcript is split each time speaker changes
- **AND** each segment includes student_id, start_time, end_time, text
- **AND** segment timestamps are accurate to within 1 second

#### Scenario: Long monologue segmentation
- **GIVEN** a speaker talks continuously for >500 words
- **WHEN** segmentation runs
- **THEN** the monologue is split into logical segments (e.g., by sentences)
- **AND** each segment is ≤500 words
- **AND** context is preserved (references to adjacent segments)

### Requirement: Transcript Retrieval

The system SHALL provide API endpoints to retrieve transcripts and segments.

#### Scenario: Retrieve classroom transcripts
- **GIVEN** a teacher requests transcripts for their classroom
- **WHEN** they call GET /api/v1/transcripts/{classroom_id}
- **THEN** all transcripts for that classroom are returned
- **AND** results include status, date, duration, confidence score
- **AND** results are paginated (50 per page)
- **AND** results can be filtered by date range

#### Scenario: Retrieve full transcript
- **GIVEN** a teacher requests a specific transcript
- **WHEN** they call GET /api/v1/transcripts/{transcript_id}
- **THEN** full transcript text is returned
- **AND** all segments with speaker information are included
- **AND** confidence scores are included
- **AND** diarization metadata is included

### Requirement: Audio Lifecycle Management

The system SHALL automatically delete audio files after 30 days while retaining transcripts.

#### Scenario: Automatic audio deletion
- **GIVEN** an audio file was uploaded 30 days ago
- **WHEN** the lifecycle job runs
- **THEN** the audio file is deleted from Cloud Storage
- **AND** the audio_files record is updated with deleted_at timestamp
- **AND** the corresponding transcript is retained in the database
- **AND** deletion is logged for audit

#### Scenario: Manual deletion
- **GIVEN** an admin wants to delete an audio file
- **WHEN** they call DELETE /api/v1/audio/{audio_id}
- **THEN** the audio file is immediately deleted from Cloud Storage
- **AND** transcript is retained unless also requested for deletion
- **AND** deletion is logged with admin user ID
