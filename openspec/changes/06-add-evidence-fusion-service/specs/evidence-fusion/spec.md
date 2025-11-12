# Evidence Fusion Capability Delta

## ADDED Requirements

### Requirement: Multi-Source Score Fusion

The system SHALL combine skill scores from multiple sources using learned weights.

#### Scenario: Fuse scores with all sources available
- **GIVEN** a student has transcript-based score, game-based score, and teacher rubric score for a skill
- **WHEN** fusion algorithm runs
- **THEN** skill-specific weights are applied (e.g., Empathy: 0.35, 0.40, 0.25)
- **AND** weighted average is calculated
- **AND** fused score is between 0 and 1
- **AND** source breakdown is stored in skill_assessments

#### Scenario: Fuse scores with missing sources
- **GIVEN** a student has only transcript and game scores (no teacher rubric yet)
- **WHEN** fusion algorithm runs
- **THEN** weights are normalized to sum to 1.0
- **AND** available sources are weighted proportionally
- **AND** confidence is reduced due to missing source

#### Scenario: Confidence calculation from agreement
- **GIVEN** source scores are 0.75, 0.78, 0.73 (high agreement)
- **WHEN** confidence is calculated
- **THEN** standard deviation is low (<0.1)
- **AND** confidence score is high (>0.8)
- **AND** assessment is marked as reliable

#### Scenario: Low confidence due to disagreement
- **GIVEN** source scores are 0.30, 0.75, 0.60 (high disagreement)
- **WHEN** confidence is calculated
- **THEN** standard deviation is high (>0.2)
- **AND** confidence score is low (<0.6)
- **AND** assessment is flagged for review

### Requirement: Evidence Extraction

The system SHALL extract relevant evidence snippets from each data source.

#### Scenario: Extract transcript evidence
- **GIVEN** a student has transcript segments with skill-relevant language
- **WHEN** evidence extraction runs for a skill
- **THEN** segments are scored for relevance using pattern matching
- **AND** top 3-5 most relevant segments are selected
- **AND** each segment includes: text, timestamp, context, relevance score
- **AND** evidence is stored in evidence_items table

#### Scenario: Extract game evidence
- **GIVEN** a student has game telemetry events
- **WHEN** evidence extraction runs
- **THEN** skill-relevant choices and events are identified
- **AND** events are scored for relevance to the skill
- **AND** top 3-5 most relevant events are selected
- **AND** evidence includes: choice description, mission context, relevance score

#### Scenario: Extract teacher feedback evidence
- **GIVEN** a teacher has submitted qualitative feedback
- **WHEN** evidence extraction runs
- **THEN** feedback text is linked to the skill assessment
- **AND** evidence includes: feedback text, assessment date, teacher name

### Requirement: Evidence Relevance Scoring

The system SHALL score each piece of evidence for relevance to the skill being assessed.

#### Scenario: High relevance transcript segment
- **GIVEN** a transcript segment contains multiple skill-specific patterns (e.g., empathy words)
- **WHEN** relevance is calculated
- **THEN** score is high (>0.8)
- **AND** segment is prioritized for inclusion

#### Scenario: Low relevance evidence
- **GIVEN** an evidence item has weak connection to the skill
- **WHEN** relevance is calculated
- **THEN** score is low (<0.5)
- **AND** evidence is excluded from top items

### Requirement: Evidence Retrieval API

The system SHALL provide API endpoints to retrieve evidence for skill assessments.

#### Scenario: Retrieve evidence for assessment
- **GIVEN** a skill assessment exists
- **WHEN** GET /api/v1/evidence/{assessment_id} is called
- **THEN** all evidence items are returned
- **AND** evidence is grouped by source type (transcript, game, teacher)
- **AND** each item includes: text, source, relevance score, timestamp, context
- **AND** items are sorted by relevance score descending
