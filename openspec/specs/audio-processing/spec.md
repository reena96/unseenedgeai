# Audio Processing Capability

## Purpose

The Audio Processing capability handles classroom audio ingestion, transcription via Google Cloud Speech-to-Text, speaker diarization, and student-speaker mapping. This is the primary data source for linguistic feature extraction and skill inference.

## Requirements

### Requirement: Audio File Upload

The system SHALL provide secure audio file upload for classroom recordings.

#### Scenario: Teacher uploads classroom audio
- **GIVEN** a teacher is authenticated
- **WHEN** they upload an audio file (MP3, WAV, or M4A format)
- **THEN** the file is stored in Cloud Storage with a unique identifier
- **AND** an upload confirmation is returned with estimated transcription completion time

#### Scenario: Large audio file handling
- **GIVEN** a classroom audio file up to 6 hours duration
- **WHEN** the file is uploaded
- **THEN** the system accepts files up to 2GB in size
- **AND** provides progress feedback during upload

#### Scenario: Invalid file format rejection
- **GIVEN** a teacher attempts to upload an unsupported file type
- **WHEN** the upload is initiated
- **THEN** the system rejects the file with a clear error message
- **AND** lists supported formats (MP3, WAV, M4A)

### Requirement: Speech-to-Text Transcription

The system SHALL transcribe classroom audio using Google Cloud Speech-to-Text with speaker diarization.

#### Scenario: Transcription job creation
- **GIVEN** an audio file has been uploaded to Cloud Storage
- **WHEN** the upload completes
- **THEN** an async transcription job is queued via Cloud Tasks
- **AND** the job status is set to "queued"

#### Scenario: Audio transcription with diarization
- **GIVEN** a transcription job is processing
- **WHEN** Google Cloud STT processes the audio
- **THEN** the system uses the `latest_long` model with enhanced audio
- **AND** enables speaker diarization with up to 10 speakers
- **AND** enables automatic punctuation
- **AND** returns a full transcript with word-level timestamps

#### Scenario: Transcription completion
- **GIVEN** transcription is complete
- **WHEN** the STT API returns results
- **THEN** the transcript is stored in the database
- **AND** word-level diarization data is stored as JSONB
- **AND** average confidence score is calculated
- **AND** job status is set to "completed"
- **AND** a "transcription-completed" event is published to Pub/Sub

#### Scenario: Transcription failure handling
- **GIVEN** a transcription job fails
- **WHEN** the STT API returns an error or times out
- **THEN** the error is logged with full details
- **AND** job status is set to "failed"
- **AND** the job is retried up to 3 times
- **AND** teachers are notified if all retries fail

### Requirement: Speaker Diarization and Student Mapping

The system SHALL map speaker tags to individual students based on voice patterns and classroom context.

#### Scenario: Speaker tag extraction
- **GIVEN** a completed transcript with diarization
- **WHEN** processing the diarization data
- **THEN** each unique speaker tag is identified (e.g., speaker_1, speaker_2)
- **AND** speech segments are grouped by speaker tag
- **AND** each segment includes start time, end time, and text

#### Scenario: Student-speaker mapping
- **GIVEN** diarization data with multiple speakers
- **WHEN** the system performs student mapping
- **THEN** speaker tags are matched to student IDs
- **AND** teacher has the ability to manually verify/correct mappings
- **AND** mapping confidence scores are calculated
- **AND** segments with low confidence (<0.6) are flagged for review

#### Scenario: Unidentified speaker handling
- **GIVEN** a speaker cannot be confidently mapped to a student
- **WHEN** processing transcript segments
- **THEN** the segment is marked as "unidentified speaker"
- **AND** the segment is excluded from individual student analysis
- **AND** the teacher is notified of unidentified segments

### Requirement: Transcript Segmentation

The system SHALL segment transcripts into analyzable units for feature extraction.

#### Scenario: Time-based segmentation
- **GIVEN** a full classroom transcript
- **WHEN** segmenting for analysis
- **THEN** the transcript is divided into 30-second windows
- **AND** each segment includes full context (preceding and following text)
- **AND** segments are attributed to individual students when speaker is identified

#### Scenario: Turn-based segmentation
- **GIVEN** a diarized transcript
- **WHEN** a student's speaking turn is complete
- **THEN** the turn is extracted as a complete segment
- **AND** metadata includes turn duration and position in conversation
- **AND** overlapping speech is flagged

### Requirement: Transcription Quality Validation

The system SHALL validate transcription quality and flag low-quality audio for review.

#### Scenario: Confidence score calculation
- **GIVEN** a completed transcription
- **WHEN** calculating overall quality
- **THEN** average word-level confidence is computed
- **AND** segments with confidence <0.70 are flagged
- **AND** overall transcript confidence is stored

#### Scenario: Audio quality issues detection
- **GIVEN** a transcription with low confidence scores
- **WHEN** quality is below 75% average confidence
- **THEN** the teacher is notified of potential quality issues
- **AND** specific low-quality segments are identified
- **AND** recommendations for improved recording are provided

### Requirement: Audio File Lifecycle Management

The system SHALL manage audio file storage with automatic deletion after transcription.

#### Scenario: Audio file retention
- **GIVEN** an audio file has been successfully transcribed
- **WHEN** 30 days have passed since upload
- **THEN** the audio file is automatically deleted from Cloud Storage
- **AND** the transcript and diarization data remain in the database
- **AND** deletion is logged for audit purposes

#### Scenario: Failed transcription retention
- **GIVEN** an audio file failed transcription after all retries
- **WHEN** 7 days have passed since final failure
- **THEN** the audio file is retained for manual review
- **AND** after 90 days, the file is deleted regardless of status

### Requirement: Performance and Scalability

The system SHALL process audio efficiently to meet performance targets.

#### Scenario: Processing speed requirement
- **GIVEN** a 6-hour classroom audio file
- **WHEN** transcription is complete
- **THEN** processing completes in less than 2 hours (real-time ratio 3:1)
- **AND** p95 processing time is tracked

#### Scenario: Concurrent processing
- **GIVEN** multiple classrooms upload audio simultaneously
- **WHEN** 10 transcription jobs are queued
- **THEN** the system processes them concurrently
- **AND** no job is starved of resources
- **AND** each job completes within SLA

#### Scenario: Cost monitoring
- **GIVEN** STT API usage
- **WHEN** processing audio files
- **THEN** API costs are tracked per school
- **AND** monthly costs are monitored against budget ($34.55/student target)
- **AND** alerts are triggered if costs exceed 120% of expected

## Non-Functional Requirements

### Performance
- **Latency:** Transcription processing at 3:1 real-time ratio (6hr audio → <2hr processing)
- **Throughput:** Support 10 concurrent transcription jobs
- **Availability:** 99% uptime for upload and status endpoints

### Security
- **Encryption:** Audio files encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Access Control:** Only authorized teachers can upload/view audio for their classrooms
- **Audit:** All audio access logged with user, timestamp, and action

### Compliance
- **FERPA:** Audio files are educational records subject to FERPA protections
- **COPPA:** Parental consent required before recording students under 13
- **Retention:** Audio deleted after 30 days; transcripts retained per retention policy

### Scalability
- **Phase 1:** 2-3 schools, ~10 classrooms, ~100 audio files/month
- **Phase 2:** 10 schools, ~50 classrooms, ~500 audio files/month
- **Phase 3:** 50+ schools, ~500 classrooms, ~5,000 audio files/month

## Dependencies

### External Services
- **Google Cloud Speech-to-Text API:** v1p1beta1 (for diarization)
- **Google Cloud Storage:** Audio file storage with lifecycle rules
- **Google Cloud Tasks:** Async job queue for transcription processing
- **Google Cloud Pub/Sub:** Event streaming for transcription completion

### Internal Services
- **Authentication Service:** User identity and authorization
- **Database:** PostgreSQL for metadata, JSONB for diarization data
- **Feature Extraction Service:** Consumes transcript segments

## API Endpoints

### POST /api/v1/audio/upload
Upload classroom audio file.

**Request:** Multipart form-data
```
classroom_id: uuid
recording_date: YYYY-MM-DD
audio_file: binary
```

**Response:** 201 Created
```json
{
  "audio_file_id": "uuid",
  "status": "queued_for_transcription",
  "estimated_completion": "2024-01-15T15:30:00Z",
  "job_id": "uuid"
}
```

### GET /api/v1/audio/{audio_file_id}/status
Get transcription job status.

**Response:** 200 OK
```json
{
  "audio_file_id": "uuid",
  "status": "completed",
  "progress": 100,
  "transcript_id": "uuid",
  "confidence": 0.82,
  "completed_at": "2024-01-15T15:28:45Z"
}
```

### GET /api/v1/transcripts/{transcript_id}
Retrieve completed transcript.

**Response:** 200 OK
```json
{
  "transcript_id": "uuid",
  "audio_file_id": "uuid",
  "full_text": "...",
  "confidence_score": 0.82,
  "word_count": 15420,
  "diarization_speakers": 8,
  "created_at": "2024-01-15T15:28:45Z"
}
```

### GET /api/v1/transcripts/{transcript_id}/segments
Retrieve transcript segments by student.

**Query Params:**
- `student_id` (optional): Filter by student
- `min_confidence` (optional): Minimum confidence threshold

**Response:** 200 OK
```json
{
  "segments": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "text": "I think we should try a different approach...",
      "start_time": 125.4,
      "end_time": 128.7,
      "confidence": 0.89,
      "speaker_tag": 3
    }
  ]
}
```

## Error Handling

### Error Codes
- `AUDIO_001`: Unsupported file format
- `AUDIO_002`: File size exceeds limit (2GB)
- `AUDIO_003`: Transcription job failed
- `AUDIO_004`: STT API rate limit exceeded
- `AUDIO_005`: Audio quality too poor for transcription
- `AUDIO_006`: Speaker diarization failed

### Retry Strategy
- Transcription failures: Retry 3 times with exponential backoff (1min, 5min, 15min)
- STT API rate limits: Exponential backoff up to 30 minutes
- Transient errors: Immediate retry, then backoff

## Monitoring and Metrics

### Key Metrics
- **Transcription success rate:** Target 95%+
- **Average confidence score:** Target 80%+
- **Processing time p95:** Target <2hr for 6hr audio
- **API cost per audio file:** Track against $34.55/student/month budget
- **Job queue depth:** Alert if >20 jobs queued

### Alerts
- Transcription failure rate >5% in 1 hour
- Average confidence <75% for any classroom
- STT API errors >10% in 15 minutes
- Processing time p95 >3 hours
- Monthly STT costs >120% of budget

## Testing Strategy

### Unit Tests
- Audio file validation (format, size)
- Diarization data parsing
- Confidence score calculation
- Segment extraction logic

### Integration Tests
- End-to-end: Upload → STT → Database storage
- Speaker mapping with test diarization data
- Retry logic with simulated failures

### Validation Tests
- STT accuracy: Manual validation on sample of 50 segments
- Speaker mapping accuracy: Verify against teacher-labeled data
- Performance: 6hr audio file processing time

## Future Enhancements (Out of Scope for Phase 1)

- **Whisper Migration:** Replace Google STT with self-hosted Whisper for cost optimization
- **Real-time Transcription:** Live transcription during class
- **Voice Biometrics:** Automated student-speaker identification
- **Multi-language Support:** Transcription in languages beyond English
- **Noise Filtering:** Pre-processing to improve audio quality
