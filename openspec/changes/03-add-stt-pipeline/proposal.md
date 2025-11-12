# Change: Speech-to-Text Pipeline Implementation

## Why
Implement the core audio transcription pipeline using Google Cloud Speech-to-Text to convert classroom recordings into text transcripts with speaker diarization. This is essential for extracting linguistic features that feed into skill inference models.

## What Changes
- Google Cloud STT API integration with async processing
- Audio file upload endpoint with validation
- Cloud Storage integration for audio file management
- Speaker diarization and student mapping algorithm
- Transcript segmentation by speaker and time
- Confidence scoring and quality validation
- Cloud Tasks integration for async transcription jobs
- Lifecycle policy enforcement (delete audio after 30 days)
- Transcription status tracking and error handling
- API endpoints for transcript retrieval

## Impact
- Affected specs: audio-processing
- Affected code: New STT service, audio upload endpoints, worker processes
- Database: New tables (audio_files, transcripts, transcript_segments)
- Infrastructure: Uses Cloud Storage, Cloud Tasks, Cloud STT API
