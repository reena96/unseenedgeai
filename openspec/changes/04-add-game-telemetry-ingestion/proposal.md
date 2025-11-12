# Change: Game Telemetry Ingestion System

## Why
Capture behavioral data from the Flourish Academy Unity game to extract behavioral features for skill inference. Game choices, timing, persistence, and interaction patterns provide critical signals for skills like Adaptability, Resilience, and Self-Regulation that are difficult to detect from transcripts alone.

## What Changes
- Telemetry API endpoints for Unity game integration
- Game session management (create, update, complete)
- Event ingestion endpoint with batch support
- TimescaleDB for efficient time-series event storage
- Event validation and schema enforcement
- Behavioral feature extraction from game events
- Session analytics and completion tracking
- Real-time event streaming via Pub/Sub
- API for querying game sessions and events

## Impact
- Affected specs: game-telemetry
- Affected code: New telemetry endpoints, event processors, behavioral feature extractors
- Database: New tables (game_sessions, game_telemetry_events, behavioral_features)
- Infrastructure: Uses Pub/Sub for event streaming, TimescaleDB hypertables
