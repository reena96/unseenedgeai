# Game Telemetry Capability Delta

## ADDED Requirements

### Requirement: Game Session Management

The system SHALL manage game sessions for students playing Flourish Academy.

#### Scenario: Create new game session
- **GIVEN** a student starts the Flourish Academy game
- **WHEN** the Unity client calls POST /api/v1/game/sessions
- **THEN** a new session record is created with student_id and started_at timestamp
- **AND** a unique session_id is returned to the client
- **AND** mission_progress is initialized as empty JSON object

#### Scenario: Complete game session
- **GIVEN** a student finishes playing
- **WHEN** the client calls PATCH /api/v1/game/sessions/{session_id} with ended_at
- **THEN** the session is marked as complete
- **AND** total_playtime_seconds is calculated and stored
- **AND** mission completion status is updated

### Requirement: Telemetry Event Ingestion

The system SHALL ingest gameplay events from Unity with schema validation.

#### Scenario: Single event ingestion
- **GIVEN** the Unity game generates a telemetry event
- **WHEN** it calls POST /api/v1/game/telemetry/events
- **THEN** the event is validated against the schema
- **AND** the event is stored in game_telemetry_events table
- **AND** the event is published to Pub/Sub for real-time processing
- **AND** 201 Created is returned

#### Scenario: Batch event ingestion
- **GIVEN** the Unity game has buffered multiple events
- **WHEN** it calls POST /api/v1/game/telemetry/batch with up to 100 events
- **THEN** each event is validated
- **AND** valid events are batch inserted to database
- **AND** invalid events are reported in response
- **AND** response indicates count of received and failed events

#### Scenario: Invalid event rejection
- **GIVEN** an event with invalid schema is submitted
- **WHEN** the API validates it
- **THEN** the request is rejected with 400 Bad Request
- **AND** error message indicates schema validation failure
- **AND** invalid event is logged for debugging

### Requirement: Event Schema Definition

The system SHALL define and validate event schemas for all game event types.

#### Scenario: Choice made event
- **GIVEN** a student makes a choice in the game
- **WHEN** choice_made event is sent
- **THEN** event includes mission_id, choice_id, time_taken_sec
- **AND** event is timestamped accurately
- **AND** choice is linked to skill being measured

#### Scenario: Mission completion event
- **GIVEN** a student completes a mission
- **WHEN** mission_completed event is sent
- **THEN** event includes mission_id, completion_time_sec, choices_made count
- **AND** mission_progress is updated in session record
- **AND** behavioral features are extracted

### Requirement: Behavioral Feature Extraction

The system SHALL extract behavioral features from game events for skill inference.

#### Scenario: Extract problem-solving features
- **GIVEN** a completed game session with choice events
- **WHEN** feature extraction runs
- **THEN** task_completion_rate is calculated (completed tasks / total tasks)
- **AND** planning_efficiency is calculated from choice sequences
- **AND** features are stored in behavioral_features table

#### Scenario: Extract resilience features
- **GIVEN** a session with retry attempts after failures
- **WHEN** feature extraction runs
- **THEN** retry_count is calculated
- **AND** average recovery_time is calculated (time between failure and retry)
- **AND** persistence_score is calculated based on retry patterns

#### Scenario: Extract adaptability features
- **GIVEN** a session with multiple strategy switches
- **WHEN** feature extraction runs
- **THEN** strategy_switching_count is calculated
- **AND** flexibility_score is calculated based on choice variety
- **AND** features indicate how well student adapts to changes
