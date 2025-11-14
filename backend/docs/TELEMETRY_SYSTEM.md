# Game Telemetry Ingestion System

## Overview

The telemetry system ingests, processes, and analyzes game events from Flourish Academy to extract behavioral features for skill assessment.

## Architecture

### Components

1. **Telemetry Endpoints** (`app/api/endpoints/telemetry.py`)
   - `/api/v1/telemetry/events` - Ingest single event
   - `/api/v1/telemetry/batch` - Ingest batch of events
   - `/api/v1/telemetry/session/{session_id}/close` - Close session and extract features

2. **Telemetry Processor** (`app/services/telemetry_processor.py`)
   - Event processing and storage
   - Session management
   - Behavioral feature extraction

3. **Database Models**
   - `GameSession` - Track game sessions
   - `GameTelemetry` - Store telemetry events (TimescaleDB hypertable)
   - `BehavioralFeatures` - Extracted behavioral metrics

## Event Types

The system recognizes the following event types:

### Session Events
- `mission_start` - Mission begins
- `mission_complete` - Mission completes
- `task_start` - Task begins
- `task_complete` - Task completes

### Behavioral Events
- `choice_made` - Student makes a decision
- `retry` - Student retries a task
- `restart` - Student restarts
- `failure` - Task failure
- `mistake` - Student makes a mistake
- `recovery` - Student recovers from failure
- `success_after_failure` - Success following failure

### Focus Events
- `distraction` - Student gets distracted
- `pause` - Student pauses

### Social Events
- `collaboration` - Collaboration detected
- `help_given` - Student helps others
- `help_received` - Student receives help
- `leadership` - Leadership behavior
- `initiative` - Student takes initiative
- `decision_made` - Student makes a decision

## Behavioral Features Extracted

The system automatically extracts the following behavioral metrics when a session is closed:

1. **Task Completion Rate** - Percentage of started tasks completed
2. **Time Efficiency** - How quickly tasks are completed relative to expected duration
3. **Retry Count** - Number of retry/restart attempts
4. **Recovery Rate** - Success rate after failures
5. **Distraction Resistance** - Ability to maintain focus (1 - distraction rate)
6. **Focus Duration** - Time between first and last event (minutes)
7. **Collaboration Indicators** - Count of collaboration events
8. **Leadership Indicators** - Count of leadership events

## API Usage Examples

### Ingest Single Event

```bash
POST /api/v1/telemetry/events
Authorization: Bearer <token>

{
  "event_id": "evt-123",
  "student_id": "student-456",
  "event_type": "mission_start",
  "timestamp": "2025-11-13T12:00:00Z",
  "data": {
    "mission": "alpha",
    "difficulty": "medium"
  },
  "session_id": "session-789",
  "mission_id": "mission-alpha",
  "game_version": "1.0.0"
}
```

### Ingest Batch of Events

```bash
POST /api/v1/telemetry/batch
Authorization: Bearer <token>

{
  "batch_id": "batch-001",
  "client_version": "1.0.0",
  "events": [
    {
      "event_id": "evt-1",
      "student_id": "student-456",
      "event_type": "mission_start",
      "timestamp": "2025-11-13T12:00:00Z",
      "data": {},
      "session_id": "session-789"
    },
    {
      "event_id": "evt-2",
      "student_id": "student-456",
      "event_type": "choice_made",
      "timestamp": "2025-11-13T12:00:30Z",
      "data": {"choice": "help_friend"},
      "session_id": "session-789"
    }
  ]
}
```

### Close Session

```bash
POST /api/v1/telemetry/session/session-789/close
Authorization: Bearer <token>
```

Response:
```json
{
  "session_id": "session-789",
  "status": "closed",
  "started_at": "2025-11-13T12:00:00Z",
  "ended_at": "2025-11-13T12:15:00Z",
  "message": "Session closed and behavioral features extracted"
}
```

## Database Schema

### game_sessions
```sql
CREATE TABLE game_sessions (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  mission_id VARCHAR(100),
  game_version VARCHAR(20) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### game_telemetry (TimescaleDB Hypertable)
```sql
CREATE TABLE game_telemetry (
  id UUID,
  timestamp TIMESTAMPTZ NOT NULL,
  student_id UUID NOT NULL,
  session_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  mission_id VARCHAR(100),
  choice_made VARCHAR(255)
);

SELECT create_hypertable('game_telemetry', 'timestamp');
```

### behavioral_features
```sql
CREATE TABLE behavioral_features (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL,
  session_id UUID NOT NULL,
  task_completion_rate FLOAT DEFAULT 0.0,
  time_efficiency FLOAT DEFAULT 0.0,
  retry_count INTEGER DEFAULT 0,
  recovery_rate FLOAT DEFAULT 0.0,
  distraction_resistance FLOAT DEFAULT 0.0,
  focus_duration FLOAT DEFAULT 0.0,
  collaboration_indicators INTEGER DEFAULT 0,
  leadership_indicators INTEGER DEFAULT 0,
  features_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Performance Considerations

### TimescaleDB Optimization
- Events are stored in a TimescaleDB hypertable partitioned by timestamp
- Automatic data compression after 7 days
- Retention policy: keep detailed data for 90 days, aggregates for 1 year

### Batch Processing
- Batch ingestion is optimized for high throughput
- Recommended batch size: 50-200 events
- Maximum batch size: 1000 events

### Concurrency
- Supports high concurrent event submissions
- Uses async database operations
- Connection pooling configured for production load

## Testing

Run telemetry tests:
```bash
cd backend
source venv/bin/activate
pytest tests/test_telemetry_ingestion.py -v
```

Performance test:
```bash
pytest tests/test_telemetry_ingestion.py::TestTelemetryEndpoints::test_performance_under_load -v
```

## Monitoring

### Key Metrics
- Event ingestion rate (events/second)
- Processing latency (ms)
- Batch processing time
- Feature extraction time
- Error rate

### Health Check
```bash
GET /api/v1/health
```

## Future Enhancements

1. **Kafka Integration** - For high-throughput event streaming
2. **Real-time Analytics** - Live dashboards for ongoing sessions
3. **Anomaly Detection** - Identify unusual behavioral patterns
4. **Advanced Feature Engineering** - ML-based feature extraction
5. **Data Retention Policies** - Automated archival and compression

## Related Documentation
- [Architecture Overview](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/api/v1/docs)
