# Implementation Tasks: Speech-to-Text Pipeline

## 1. Database Schema
- [ ] 1.1 Create audio_files table with status tracking
- [ ] 1.2 Create transcripts table
- [ ] 1.3 Create transcript_segments table with speaker mapping
- [ ] 1.4 Add indexes for performance (classroom_id, student_id, status)
- [ ] 1.5 Write and apply Alembic migrations

## 2. Audio Upload API
- [ ] 2.1 POST /api/v1/audio/upload endpoint
  - [ ] 2.1.1 Validate file format (MP3, WAV, FLAC)
  - [ ] 2.1.2 Validate file size (max 2GB per file)
  - [ ] 2.1.3 Validate classroom_id and teacher permissions
  - [ ] 2.1.4 Generate unique filename with timestamp
  - [ ] 2.1.5 Upload to Cloud Storage bucket
  - [ ] 2.1.6 Create audio_files record with "uploaded" status
  - [ ] 2.1.7 Enqueue transcription job in Cloud Tasks
  - [ ] 2.1.8 Return job ID and estimated completion time
- [ ] 2.2 Add multipart file upload support
- [ ] 2.3 Implement upload progress tracking
- [ ] 2.4 Add resumable upload for large files
- [ ] 2.5 Test with sample audio files (10 min, 1 hour, 6 hours)

## 3. Google Cloud STT Integration
- [ ] 3.1 Create STTService class
  - [ ] 3.1.1 Initialize Speech-to-Text client with credentials
  - [ ] 3.1.2 Configure RecognitionConfig (MP3, 16kHz, en-US)
  - [ ] 3.1.3 Enable automatic punctuation
  - [ ] 3.1.4 Enable speaker diarization (up to 10 speakers)
  - [ ] 3.1.5 Use "latest_long" model with enhanced accuracy
- [ ] 3.2 Implement async transcription method
  - [ ] 3.2.1 Submit long_running_recognize request
  - [ ] 3.2.2 Poll operation status with exponential backoff
  - [ ] 3.2.3 Handle timeout (max 1 hour for 6-hour audio)
  - [ ] 3.2.4 Extract transcript text and confidence scores
  - [ ] 3.2.5 Parse diarization data (speaker tags per word)
- [ ] 3.3 Add error handling for STT failures
  - [ ] 3.3.1 Handle network errors (retry 3 times)
  - [ ] 3.3.2 Handle invalid audio format errors
  - [ ] 3.3.3 Handle quota exceeded errors
  - [ ] 3.3.4 Handle timeout errors
- [ ] 3.4 Test with various audio qualities (clean, noisy, overlapping speech)
- [ ] 3.5 Measure and log STT API costs per transcription

## 4. Transcription Worker
- [ ] 4.1 Create Cloud Tasks handler for transcription jobs
- [ ] 4.2 Implement job processing logic:
  - [ ] 4.2.1 Fetch audio file metadata from database
  - [ ] 4.2.2 Update status to "processing"
  - [ ] 4.2.3 Retrieve audio file from Cloud Storage
  - [ ] 4.2.4 Call STT service
  - [ ] 4.2.5 Store transcript in database
  - [ ] 4.2.6 Update status to "completed" or "failed"
  - [ ] 4.2.7 Publish "transcription-completed" event to Pub/Sub
- [ ] 4.3 Add retry logic (max 3 retries with exponential backoff)
- [ ] 4.4 Log processing time and performance metrics
- [ ] 4.5 Test worker with concurrent jobs (10 jobs simultaneously)

## 5. Speaker Diarization and Student Mapping
- [ ] 5.1 Implement speaker clustering algorithm
  - [ ] 5.1.1 Group words by speaker tag
  - [ ] 5.1.2 Identify distinct speakers in classroom
  - [ ] 5.1.3 Calculate speaker statistics (word count, speaking time)
- [ ] 5.2 Create student-speaker mapping algorithm
  - [ ] 5.2.1 Use roster data to match speakers to students
  - [ ] 5.2.2 Handle teacher speaker identification
  - [ ] 5.2.3 Handle ambiguous or overlapping speech
  - [ ] 5.2.4 Apply confidence thresholds for mapping
- [ ] 5.3 Create transcript_segments with student_id assignment
- [ ] 5.4 Handle unmapped speakers (labeled as "Unknown Speaker")
- [ ] 5.5 Test with simulated classroom audio (5-30 students)

## 6. Transcript Segmentation
- [ ] 6.1 Split transcript by speaker turns
- [ ] 6.2 Split long monologues into logical segments (max 500 words)
- [ ] 6.3 Preserve timestamps for each segment
- [ ] 6.4 Store context (previous and next segment) for analysis
- [ ] 6.5 Calculate segment-level confidence scores

## 7. Transcript Retrieval API
- [ ] 7.1 GET /api/v1/transcripts/{classroom_id}
  - [ ] 7.1.1 List all transcripts for a classroom
  - [ ] 7.1.2 Filter by date range
  - [ ] 7.1.3 Include status and metadata
  - [ ] 7.1.4 Implement pagination (50 transcripts per page)
- [ ] 7.2 GET /api/v1/transcripts/{transcript_id}
  - [ ] 7.2.1 Return full transcript with segments
  - [ ] 7.2.2 Include speaker information
  - [ ] 7.2.3 Include confidence scores
  - [ ] 7.2.4 Support format options (JSON, plain text)
- [ ] 7.3 GET /api/v1/transcripts/{transcript_id}/segments
  - [ ] 7.3.1 Return segments filtered by student_id
  - [ ] 7.3.2 Support time-range filtering
  - [ ] 7.3.3 Include context segments
- [ ] 7.4 Add caching for frequently accessed transcripts
- [ ] 7.5 Test API performance with large transcripts (6 hours)

## 8. Quality Validation
- [ ] 8.1 Calculate overall transcript confidence score
- [ ] 8.2 Flag low-confidence segments (<50%) for review
- [ ] 8.3 Detect and flag segments with overlapping speech
- [ ] 8.4 Identify segments with background noise
- [ ] 8.5 Generate quality report for each transcript
- [ ] 8.6 Alert teachers when transcription quality is poor

## 9. Lifecycle Management
- [ ] 9.1 Implement scheduled job to delete old audio files (30+ days)
- [ ] 9.2 Retain transcripts while deleting source audio
- [ ] 9.3 Add manual deletion endpoint for admins
- [ ] 9.4 Log all file deletions for audit
- [ ] 9.5 Test lifecycle policy enforcement

## 10. Job Status Tracking
- [ ] 10.1 GET /api/v1/jobs/{job_id}/status endpoint
  - [ ] 10.1.1 Return current status (queued, processing, completed, failed)
  - [ ] 10.1.2 Return progress percentage estimate
  - [ ] 10.1.3 Return estimated completion time
  - [ ] 10.1.4 Return error message if failed
- [ ] 10.2 Implement WebSocket for real-time status updates (future)
- [ ] 10.3 Send email notification when transcription completes

## 11. Performance Optimization
- [ ] 11.1 Implement batch processing for multiple audio files
- [ ] 11.2 Optimize Cloud Storage read/write operations
- [ ] 11.3 Use streaming uploads for large files
- [ ] 11.4 Cache frequently accessed transcript segments
- [ ] 11.5 Measure and optimize processing latency (<5s per min of audio)

## 12. Testing
- [ ] 12.1 Unit tests for STT service methods
- [ ] 12.2 Unit tests for speaker diarization algorithm
- [ ] 12.3 Integration tests for upload → transcription → retrieval flow
- [ ] 12.4 Test with various audio qualities and lengths
- [ ] 12.5 Test concurrent transcription jobs (10+)
- [ ] 12.6 Test error handling and retries
- [ ] 12.7 Load test with 100 uploads/hour
- [ ] 12.8 Validate STT accuracy with manual review (sample 10 transcripts)

## 13. Monitoring and Logging
- [ ] 13.1 Log all transcription job starts and completions
- [ ] 13.2 Track processing time metrics
- [ ] 13.3 Monitor STT API costs and usage
- [ ] 13.4 Set up alerts for failed transcriptions (>5% failure rate)
- [ ] 13.5 Create dashboard for transcription pipeline health

## 14. Documentation
- [ ] 14.1 Document audio upload API with examples
- [ ] 14.2 Document transcript retrieval API
- [ ] 14.3 Create guide for teachers on recording best practices
- [ ] 14.4 Document speaker diarization limitations
- [ ] 14.5 Create troubleshooting guide for poor transcription quality

## 15. Deployment
- [ ] 15.1 Deploy STT service to Cloud Run
- [ ] 15.2 Configure Cloud Tasks queue for transcription jobs
- [ ] 15.3 Test in staging environment with sample audio
- [ ] 15.4 Run smoke tests in production
- [ ] 15.5 Monitor initial production transcriptions
