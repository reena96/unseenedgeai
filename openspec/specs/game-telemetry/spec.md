# Game Telemetry Capability

## Purpose

The Game Telemetry capability collects behavioral data from the Flourish Academy Unity game, processes telemetry events to extract behavioral features for skill inference, and provides APIs for game session management. This is the primary source for measuring skills with low transcript detectability (Adaptability, Resilience, Self-Regulation).

## Requirements

### Requirement: Game Session Management

The system SHALL create and track game sessions for each student's gameplay.

#### Scenario: Session initialization
- **GIVEN** a student launches Flourish Academy
- **WHEN** the game authenticates the student
- **THEN** a new game session is created in the database
- **AND** session ID is returned to the game client
- **AND** session start time is recorded
- **AND** mission progress is initialized as empty

#### Scenario: Session resumption
- **GIVEN** a student has an incomplete game session
- **WHEN** they relaunch the game
- **THEN** the previous session is retrieved
- **AND** mission progress is restored
- **AND** student can continue from last checkpoint

#### Scenario: Session completion
- **GIVEN** a student completes all 3 missions
- **WHEN** the final mission ends
- **THEN** session end time is recorded
- **AND** total playtime is calculated
- **AND** session status is set to "completed"
- **AND** completion event triggers behavioral feature extraction

### Requirement: Telemetry Event Ingestion

The system SHALL ingest real-time telemetry events from the game client.

#### Scenario: Single event ingestion
- **GIVEN** a student makes a choice in the game
- **WHEN** the game client sends a telemetry event
- **THEN** the event is validated (required fields: event_type, timestamp, session_id)
- **AND** event is stored in the database with millisecond precision
- **AND** acknowledgment is returned to game client within 100ms

#### Scenario: Batch event ingestion
- **GIVEN** the game has queued multiple events (e.g., network interruption)
- **WHEN** connectivity is restored
- **THEN** events are sent as a batch (up to 100 events)
- **AND** all events are processed atomically
- **AND** events are ordered by timestamp
- **AND** batch confirmation is returned

#### Scenario: Event validation failure
- **GIVEN** an event with missing required fields
- **WHEN** the event is received
- **THEN** the event is rejected with a specific error code
- **AND** the game client is notified to retry with correct format
- **AND** invalid event is logged for debugging

### Requirement: Mission-Specific Telemetry

The system SHALL collect mission-specific behavioral data for all 3 Flourish Academy missions.

#### Scenario: Mission 1 - Understanding Perspectives (Empathy)
- **GIVEN** a student is playing Mission 1
- **WHEN** telemetry events are generated
- **THEN** the system tracks:
  - Choice selections (empathetic vs self-focused)
  - Time spent reading dialogue (perspective-taking indicator)
  - Re-reading character dialogue (understanding effort)
  - Help-seeking behaviors
- **AND** events include choice_id with empathy classification

#### Scenario: Mission 2 - Group Project Challenge (Collaboration + Problem-Solving)
- **GIVEN** a student is playing Mission 2
- **WHEN** telemetry events are generated
- **THEN** the system tracks:
  - Task delegation patterns (fair vs autocratic)
  - Conflict resolution strategies
  - Resource allocation decisions
  - Planning approach (systematic vs random)
  - Turn-taking behaviors
- **AND** events include collaboration and problem-solving markers

#### Scenario: Mission 3 - Unexpected Change (Adaptability + Resilience + Self-Regulation)
- **GIVEN** a student is playing Mission 3
- **WHEN** telemetry events are generated
- **THEN** the system tracks:
  - Initial reaction to setback (frustration vs adaptive)
  - Strategy switching frequency (rigid vs flexible)
  - Persistence after failure (quit vs retry)
  - Emotional regulation indicators (time to recover)
  - Help-seeking patterns
- **AND** events include adaptability, resilience, and self-regulation markers

### Requirement: Behavioral Feature Extraction

The system SHALL extract behavioral features from game telemetry for ML inference.

#### Scenario: Problem-solving features
- **GIVEN** completed Mission 2 telemetry
- **WHEN** extracting problem-solving features
- **THEN** the system calculates:
  - task_completion_rate: Percentage of tasks completed
  - task_sequencing_efficiency: Optimal vs actual sequence similarity
  - planning_score: Pre-planning time vs trial-and-error ratio
- **AND** features are normalized to 0-1 scale

#### Scenario: Adaptability features
- **GIVEN** completed Mission 3 telemetry
- **WHEN** extracting adaptability features
- **THEN** the system calculates:
  - strategy_switching_count: Number of approach changes
  - flexibility_score: Speed of adaptation to new constraints
  - initial_reaction_quality: First choice after setback
- **AND** features capture both frequency and quality of adaptation

#### Scenario: Resilience features
- **GIVEN** completed Mission 3 telemetry with failure events
- **WHEN** extracting resilience features
- **THEN** the system calculates:
  - retry_count: Number of attempts after failure
  - recovery_time_avg: Average time between failure and retry
  - persistence_score: Retry rate without external prompting
- **AND** features distinguish giving up vs persisting

#### Scenario: Self-regulation features
- **GIVEN** telemetry across all missions
- **WHEN** extracting self-regulation features
- **THEN** the system calculates:
  - distraction_resistance: Time on task vs time idle
  - time_on_task: Focus duration before distraction
  - impulse_control: Pause time before choices vs immediate clicks
- **AND** features capture sustained attention patterns

#### Scenario: Collaboration features (from Mission 2)
- **GIVEN** Mission 2 telemetry
- **WHEN** extracting collaboration features
- **THEN** the system calculates:
  - delegation_fairness: Distribution of task assignments
  - turn_taking_score: Equitable participation with NPCs
  - conflict_resolution_quality: Choice quality during conflicts
- **AND** features reflect cooperative vs competitive behaviors

#### Scenario: Empathy features (from Mission 1)
- **GIVEN** Mission 1 telemetry
- **WHEN** extracting empathy features
- **THEN** the system calculates:
  - empathetic_choice_rate: Percentage of empathetic choices
  - perspective_taking_time: Time spent considering others' views
  - emotion_recognition_accuracy: Correct emotion identifications
- **AND** features align with transcript-based empathy markers

### Requirement: Real-Time Progress Tracking

The system SHALL provide real-time progress updates to teachers and students.

#### Scenario: Teacher monitoring
- **GIVEN** students are playing the game
- **WHEN** a teacher views the dashboard
- **THEN** they see real-time completion status for each student
- **AND** mission progress (0/3, 1/3, 2/3, 3/3) is displayed
- **AND** estimated time remaining is shown
- **AND** dashboard updates every 30 seconds

#### Scenario: Student progress save
- **GIVEN** a student completes Mission 1
- **WHEN** they exit the game
- **THEN** mission progress is saved
- **AND** student can resume from Mission 2 later
- **AND** no telemetry data is lost

### Requirement: Data Quality and Validation

The system SHALL ensure telemetry data quality and handle anomalies.

#### Scenario: Duplicate event detection
- **GIVEN** the game accidentally sends the same event twice
- **WHEN** the duplicate is received
- **THEN** the system detects duplicate based on (session_id, event_type, timestamp, event_data hash)
- **AND** duplicate is silently discarded
- **AND** no error is returned to game client

#### Scenario: Out-of-order events
- **GIVEN** events arrive out of chronological order
- **WHEN** processing events
- **THEN** events are reordered by timestamp before feature extraction
- **AND** causality is preserved (e.g., mission_started before choice_made)

#### Scenario: Incomplete session handling
- **GIVEN** a student abandons the game mid-mission
- **WHEN** 24 hours have passed without activity
- **THEN** session is marked as "incomplete"
- **AND** partial telemetry is still processed for features
- **AND** incomplete sessions are flagged in analysis

#### Scenario: Anomalous behavior detection
- **GIVEN** telemetry shows impossible patterns (e.g., 100 choices in 10 seconds)
- **WHEN** processing events
- **THEN** session is flagged for manual review
- **AND** features are still extracted but marked with low confidence
- **AND** alert is sent to administrator

### Requirement: Privacy and Security

The system SHALL protect student privacy in game telemetry.

#### Scenario: Data minimization
- **GIVEN** telemetry event design
- **WHEN** determining what to collect
- **THEN** only behavioral actions are tracked (no personally identifiable content)
- **AND** no free-text input from students is collected
- **AND** no screenshots or recordings are captured

#### Scenario: Anonymized telemetry
- **GIVEN** telemetry for analysis
- **WHEN** exporting for research purposes
- **THEN** student IDs are replaced with anonymous hashes
- **AND** school IDs are removed
- **AND** timestamps are rounded to nearest hour

#### Scenario: Parental consent enforcement
- **GIVEN** a student under 13
- **WHEN** attempting to create a game session
- **THEN** system verifies parental consent is on file
- **AND** session is blocked if consent is missing
- **AND** teacher is notified to obtain consent

### Requirement: Performance and Scalability

The system SHALL handle high-frequency telemetry ingestion efficiently.

#### Scenario: High-frequency event stream
- **GIVEN** 30 students playing simultaneously
- **WHEN** events are generated at 10 events/second per student (300 events/sec total)
- **THEN** all events are ingested without loss
- **AND** API latency remains <100ms p95
- **AND** database write performance is maintained

#### Scenario: TimescaleDB optimization
- **GIVEN** game_telemetry_events table is a hypertable
- **WHEN** querying events for a specific session
- **THEN** queries execute in <500ms even with millions of events
- **AND** time-based partitioning is automatic
- **AND** old partitions can be archived efficiently

## Non-Functional Requirements

### Performance
- **Event ingestion latency:** <100ms p95
- **Batch ingestion:** 100 events in <500ms
- **Feature extraction:** <5 seconds per student per session
- **Throughput:** 300 events/second sustained

### Reliability
- **Event loss rate:** <0.01% (99.99% delivery)
- **Uptime:** 99.5% for telemetry API
- **Data durability:** 100% (no data loss after acknowledgment)

### Scalability
- **Phase 1:** 100 students, ~300 game sessions
- **Phase 2:** 500 students, ~1,500 game sessions
- **Phase 3:** 5,000 students, ~15,000 game sessions
- **Event volume:** Up to 10M events/month in Phase 3

### Compliance
- **FERPA:** Game data is educational record, subject to access controls
- **COPPA:** Parental consent required for students under 13
- **Data retention:** Telemetry retained for 2 years, then archived

## Dependencies

### External Services
- **Google Cloud Pub/Sub:** Real-time event streaming (optional for high volume)
- **TimescaleDB:** Time-series optimized storage

### Internal Services
- **Authentication Service:** Student identity verification
- **Skill Inference Service:** Consumes behavioral features
- **Database:** PostgreSQL with TimescaleDB extension

### Unity Client
- **Unity 2022.3 LTS:** Game engine
- **Telemetry SDK:** Custom C# library for event tracking
- **Network layer:** UnityWebRequest for HTTP calls

## API Endpoints

### POST /api/v1/game/sessions/start
Start a new game session.

**Request:**
```json
{
  "student_id": "uuid",
  "device_info": {
    "platform": "Windows",
    "version": "1.0.0"
  }
}
```

**Response:** 201 Created
```json
{
  "session_id": "uuid",
  "student_id": "uuid",
  "started_at": "2024-01-15T14:20:00Z",
  "mission_progress": {}
}
```

### POST /api/v1/game/telemetry/events
Submit telemetry events.

**Request:**
```json
{
  "session_id": "uuid",
  "events": [
    {
      "event_type": "mission_started",
      "timestamp": "2024-01-15T14:20:15.234Z",
      "event_data": {
        "mission_id": "M01",
        "mission_name": "Understanding Perspectives"
      }
    },
    {
      "event_type": "choice_made",
      "timestamp": "2024-01-15T14:22:30.567Z",
      "event_data": {
        "mission_id": "M01",
        "choice_id": "C05_empathy_high",
        "choice_text": "Listen to Morgan's perspective",
        "time_taken_sec": 12.4,
        "previous_dialogue_reread": true
      }
    }
  ]
}
```

**Response:** 200 OK
```json
{
  "received": 2,
  "processed": 2,
  "session_id": "uuid"
}
```

### POST /api/v1/game/telemetry/batch
Submit large batch of events (up to 100).

**Request:** Same format as /events but larger array

**Response:** 200 OK
```json
{
  "received": 87,
  "processed": 87,
  "duplicates_discarded": 0,
  "session_id": "uuid"
}
```

### POST /api/v1/game/sessions/{session_id}/complete
Mark session as complete.

**Request:**
```json
{
  "ended_at": "2024-01-15T15:05:00Z",
  "total_playtime_seconds": 2700,
  "missions_completed": ["M01", "M02", "M03"]
}
```

**Response:** 200 OK
```json
{
  "session_id": "uuid",
  "status": "completed",
  "total_playtime_seconds": 2700
}
```

### GET /api/v1/game/sessions/{student_id}
Retrieve student's game sessions.

**Query Params:**
- `status`: "active" | "completed" | "incomplete"
- `limit`: Number of sessions to return (default: 10)

**Response:** 200 OK
```json
{
  "student_id": "uuid",
  "sessions": [
    {
      "session_id": "uuid",
      "started_at": "2024-01-15T14:20:00Z",
      "ended_at": "2024-01-15T15:05:00Z",
      "status": "completed",
      "total_playtime_seconds": 2700,
      "mission_progress": {
        "M01": "completed",
        "M02": "completed",
        "M03": "completed"
      }
    }
  ]
}
```

### GET /api/v1/game/features/{session_id}
Retrieve extracted behavioral features (for debugging).

**Response:** 200 OK
```json
{
  "session_id": "uuid",
  "student_id": "uuid",
  "features": {
    "empathy_empathetic_choice_rate": 0.85,
    "adaptability_strategy_switching_count": 3,
    "resilience_retry_count": 4,
    "resilience_persistence_score": 0.78,
    "problem_solving_task_completion_rate": 0.92,
    "collaboration_delegation_fairness": 0.88,
    "self_regulation_time_on_task": 0.76
  },
  "extracted_at": "2024-01-15T15:06:23Z"
}
```

## Data Models

### game_sessions Table
```sql
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- active, completed, incomplete
    total_playtime_seconds INTEGER,
    mission_progress JSONB DEFAULT '{}',  -- {"M01": "completed", "M02": "in_progress"}
    device_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_game_sessions_student ON game_sessions(student_id);
CREATE INDEX idx_game_sessions_status ON game_sessions(status);
```

### game_telemetry_events Table (TimescaleDB Hypertable)
```sql
CREATE TABLE game_telemetry_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES game_sessions(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('game_telemetry_events', 'timestamp');

CREATE INDEX idx_game_events_session ON game_telemetry_events(session_id);
CREATE INDEX idx_game_events_type ON game_telemetry_events(event_type);
```

### behavioral_features Table
```sql
CREATE TABLE behavioral_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    session_id UUID REFERENCES game_sessions(id),
    extracted_at TIMESTAMP DEFAULT NOW(),

    -- Problem-solving
    task_completion_rate FLOAT,
    task_sequencing_efficiency FLOAT,

    -- Adaptability
    strategy_switching_count INTEGER,
    flexibility_score FLOAT,

    -- Resilience
    retry_count INTEGER,
    recovery_time_avg FLOAT,
    persistence_score FLOAT,

    -- Collaboration
    delegation_fairness FLOAT,
    turn_taking_score FLOAT,

    -- Self-regulation
    distraction_resistance FLOAT,
    time_on_task FLOAT,

    -- Empathy
    empathetic_choice_rate FLOAT,

    -- All features as JSONB
    all_features JSONB
);

CREATE INDEX idx_behavioral_features_student ON behavioral_features(student_id);
CREATE INDEX idx_behavioral_features_session ON behavioral_features(session_id);
```

## Event Types

### Core Event Types
- `session_started`: Game session begins
- `session_paused`: Student pauses game
- `session_resumed`: Student resumes game
- `session_completed`: All missions finished
- `mission_started`: Mission begins
- `mission_completed`: Mission ends
- `choice_made`: Student makes a dialogue/action choice
- `task_started`: Specific task initiated
- `task_completed`: Specific task finished
- `task_failed`: Task failed, retry possible
- `help_requested`: Student clicks help button
- `dialogue_reread`: Student re-reads previous dialogue
- `strategy_changed`: Student switches approach
- `retry_attempted`: Student retries after failure

### Event Data Schemas

**choice_made:**
```json
{
  "mission_id": "M01",
  "choice_id": "C05_empathy_high",
  "choice_text": "Listen to Morgan's perspective",
  "time_taken_sec": 12.4,
  "previous_dialogue_reread": true,
  "skill_markers": ["empathy"]
}
```

**task_completed:**
```json
{
  "mission_id": "M02",
  "task_id": "T07_resource_allocation",
  "completion_time_sec": 45.2,
  "optimal_sequence": false,
  "attempts": 1
}
```

**retry_attempted:**
```json
{
  "mission_id": "M03",
  "challenge_id": "CH_02_setback",
  "retry_number": 3,
  "time_since_failure_sec": 8.5,
  "strategy_changed": true
}
```

## Error Codes

- `GAME_001`: Invalid session ID
- `GAME_002`: Session already completed
- `GAME_003`: Missing required event fields
- `GAME_004`: Event timestamp in future
- `GAME_005`: Duplicate event detected
- `GAME_006`: Unsupported event type
- `GAME_007`: Session not found
- `GAME_008`: Student not authorized for this session

## Monitoring and Metrics

### Key Metrics
- **Event ingestion rate:** Events/second
- **Event processing latency:** p50, p95, p99
- **Session completion rate:** Target 80%+
- **Average playtime:** Target 30-45 minutes
- **Mission completion rates:** Track per mission
- **Event loss rate:** Target <0.01%

### Alerts
- Event ingestion latency p95 >500ms
- Event loss rate >0.1% in 15 minutes
- Session completion rate <70% (indicates game issues)
- API error rate >5%
- Database write lag >10 seconds

## Testing Strategy

### Unit Tests
- Event validation logic
- Feature extraction calculations
- Duplicate detection
- Out-of-order event handling

### Integration Tests
- End-to-end: Game client → API → Database
- Batch event submission with 100 events
- Session lifecycle (start → events → complete)
- Feature extraction from real telemetry

### Load Tests
- 300 events/second sustained for 10 minutes
- 100 concurrent game sessions
- 1000-event batch submission

### Validation Tests
- **Feature validity:** Compare extracted features with manual coding
- **Completion rate:** 80%+ of students complete all 3 missions
- **Engagement:** 75%+ rate game as fun

## Future Enhancements (Out of Scope for Phase 1)

- **Real-time analytics:** Live dashboards for teachers during gameplay
- **Adaptive difficulty:** Adjust game challenge based on performance
- **Expanded missions:** Add 2 more missions (5 total) for fuller assessment
- **Voice acting:** Replace text-to-speech with professional voice acting
- **Multi-platform:** Mobile (iOS, Android) and web versions
- **Offline mode:** Play without internet, sync telemetry later
- **Game analytics:** Detailed funnel analysis, drop-off points
