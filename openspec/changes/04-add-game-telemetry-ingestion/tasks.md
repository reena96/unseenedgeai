# Implementation Tasks: Game Telemetry Ingestion

## 1. Database Schema
- [ ] 1.1 Create game_sessions table
- [ ] 1.2 Create game_telemetry_events table
- [ ] 1.3 Convert game_telemetry_events to TimescaleDB hypertable
- [ ] 1.4 Create behavioral_features table
- [ ] 1.5 Add indexes for performance (session_id, event_type, timestamp)
- [ ] 1.6 Write and apply Alembic migrations

## 2. Session Management API
- [ ] 2.1 POST /api/v1/game/sessions endpoint
  - [ ] 2.1.1 Create new game session for student
  - [ ] 2.1.2 Return session ID to Unity client
  - [ ] 2.1.3 Initialize mission_progress JSON
  - [ ] 2.1.4 Record started_at timestamp
- [ ] 2.2 PATCH /api/v1/game/sessions/{session_id} endpoint
  - [ ] 2.2.1 Update mission progress
  - [ ] 2.2.2 Update playtime
  - [ ] 2.2.3 Mark session as ended
- [ ] 2.3 GET /api/v1/game/sessions/{student_id} endpoint
  - [ ] 2.3.1 List all sessions for student
  - [ ] 2.3.2 Include completion status
  - [ ] 2.3.3 Calculate total playtime

## 3. Event Ingestion API
- [ ] 3.1 POST /api/v1/game/telemetry/events endpoint
  - [ ] 3.1.1 Accept single event JSON
  - [ ] 3.1.2 Validate event schema (event_type, timestamp, session_id, event_data)
  - [ ] 3.1.3 Store in game_telemetry_events table
  - [ ] 3.1.4 Publish to Pub/Sub topic
  - [ ] 3.1.5 Return 201 Created
- [ ] 3.2 POST /api/v1/game/telemetry/batch endpoint
  - [ ] 3.2.1 Accept array of events (max 100 per batch)
  - [ ] 3.2.2 Validate each event
  - [ ] 3.2.3 Batch insert to database
  - [ ] 3.2.4 Handle partial failures
  - [ ] 3.2.5 Return summary (received, failed)
- [ ] 3.3 Add rate limiting (1000 events/minute per session)
- [ ] 3.4 Test with high-volume event streams

## 4. Event Schema Validation
- [ ] 4.1 Define event schemas for each event type:
  - [ ] 4.1.1 choice_made (mission_id, choice_id, time_taken_sec)
  - [ ] 4.1.2 mission_started (mission_id)
  - [ ] 4.1.3 mission_completed (mission_id, completion_time_sec, choices_made)
  - [ ] 4.1.4 dialogue_read (dialogue_id, time_spent_sec)
  - [ ] 4.1.5 retry_attempt (mission_id, failure_reason)
  - [ ] 4.1.6 help_requested (context)
- [ ] 4.2 Create Pydantic models for validation
- [ ] 4.3 Reject invalid events with 400 Bad Request
- [ ] 4.4 Log validation errors for debugging

## 5. Behavioral Feature Extraction
- [ ] 5.1 Create BehavioralFeatureExtractor service
- [ ] 5.2 Extract problem-solving features:
  - [ ] 5.2.1 Task completion rate
  - [ ] 5.2.2 Planning efficiency (choice sequence analysis)
- [ ] 5.3 Extract adaptability features:
  - [ ] 5.3.1 Strategy switching count
  - [ ] 5.3.2 Flexibility score (variety of choices)
- [ ] 5.4 Extract resilience features:
  - [ ] 5.4.1 Retry count after failures
  - [ ] 5.4.2 Recovery time average
  - [ ] 5.4.3 Persistence score
- [ ] 5.5 Extract collaboration features:
  - [ ] 5.5.1 Delegation fairness (Mission 2)
  - [ ] 5.5.2 Turn-taking score
- [ ] 5.6 Extract self-regulation features:
  - [ ] 5.6.1 Time on task
  - [ ] 5.6.2 Distraction resistance (focus metrics)
- [ ] 5.7 Store extracted features in behavioral_features table
- [ ] 5.8 Test feature extraction with simulated game data

## 6. Event Query API
- [ ] 6.1 GET /api/v1/game/sessions/{session_id}/events
  - [ ] 6.1.1 Return all events for session
  - [ ] 6.1.2 Filter by event_type
  - [ ] 6.1.3 Filter by time range
  - [ ] 6.1.4 Pagination support
- [ ] 6.2 GET /api/v1/game/analytics/{student_id}
  - [ ] 6.2.1 Aggregate game statistics
  - [ ] 6.2.2 Mission completion breakdown
  - [ ] 6.2.3 Average playtime per mission
  - [ ] 6.2.4 Choice distribution analysis

## 7. Real-Time Event Streaming
- [ ] 7.1 Publish events to "game-events" Pub/Sub topic
- [ ] 7.2 Create subscriber for real-time processing
- [ ] 7.3 Trigger behavioral feature extraction on mission completion
- [ ] 7.4 Test event streaming with Unity client

## 8. Unity Integration
- [ ] 8.1 Create C# telemetry SDK for Unity
- [ ] 8.2 Implement event buffering in client (send batches)
- [ ] 8.3 Add retry logic for network failures
- [ ] 8.4 Test telemetry from Unity game
- [ ] 8.5 Document integration guide for game developers

## 9. Analytics and Reporting
- [ ] 9.1 Calculate mission completion rates
- [ ] 9.2 Track average playtime per mission
- [ ] 9.3 Identify stuck students (no progress >3 days)
- [ ] 9.4 Generate game engagement report for teachers
- [ ] 9.5 Create dashboard visualizations (future)

## 10. Testing
- [ ] 10.1 Unit tests for event validation
- [ ] 10.2 Unit tests for feature extraction algorithms
- [ ] 10.3 Integration tests for event ingestion → feature extraction
- [ ] 10.4 Load test with 1000 events/second
- [ ] 10.5 Test TimescaleDB query performance
- [ ] 10.6 Validate extracted features match expected values

## 11. Monitoring
- [ ] 11.1 Track event ingestion rate
- [ ] 11.2 Monitor database write latency
- [ ] 11.3 Alert on high event rejection rate (>5%)
- [ ] 11.4 Monitor Pub/Sub message backlog
- [ ] 11.5 Create telemetry pipeline health dashboard

## 12. Documentation
- [ ] 12.1 Document telemetry API endpoints
- [ ] 12.2 Document event schemas and examples
- [ ] 12.3 Create Unity integration guide
- [ ] 12.4 Document behavioral feature definitions
- [ ] 12.5 Create troubleshooting guide for telemetry issues

## 13. Deployment
- [ ] 13.1 Deploy telemetry service to Cloud Run
- [ ] 13.2 Test with Unity game in staging
- [ ] 13.3 Monitor initial production events
- [ ] 13.4 Verify feature extraction runs correctly
