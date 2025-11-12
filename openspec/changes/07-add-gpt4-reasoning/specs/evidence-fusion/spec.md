# Evidence Fusion Capability Delta - GPT-4 Reasoning

## ADDED Requirements

### Requirement: AI-Generated Reasoning

The system SHALL generate human-readable explanations for skill assessments using OpenAI GPT-4.

#### Scenario: Generate reasoning for assessment
- **GIVEN** a skill assessment with evidence and feature importance
- **WHEN** reasoning generation is requested
- **THEN** a prompt is constructed with student name, skill, score, evidence snippets, and key features
- **AND** OpenAI GPT-4 API is called with temperature=0.3 and max_tokens=150
- **AND** reasoning text (2-3 sentences) is generated
- **AND** reasoning is growth-oriented and actionable
- **AND** reasoning references provided evidence

#### Scenario: Reasoning quality validation
- **GIVEN** GPT-4 has generated reasoning text
- **WHEN** quality validation runs
- **THEN** text length is between 50-200 words
- **AND** tone is positive and growth-focused (no negative judgments)
- **AND** text references specific evidence or behaviors
- **AND** text avoids hallucinations (no invented details)

#### Scenario: Reasoning caching
- **GIVEN** identical evidence and features have been seen before
- **WHEN** reasoning is requested
- **THEN** cached reasoning is retrieved from Redis
- **AND** GPT-4 API is not called
- **AND** generation cost is zero

#### Scenario: API failure fallback
- **GIVEN** OpenAI API is unavailable or fails
- **WHEN** reasoning generation is attempted
- **THEN** system falls back to template-based reasoning
- **AND** template is selected based on skill and score level
- **AND** reasoning is still provided to user

### Requirement: Cost Management

The system SHALL track and manage GPT-4 API costs to stay within budget.

#### Scenario: Track generation costs
- **GIVEN** a reasoning is generated via GPT-4
- **WHEN** the API response is received
- **THEN** tokens used are logged
- **AND** cost is calculated (approx $0.03-0.05 per reasoning)
- **AND** cost is stored in reasoning_explanations table
- **AND** daily total is tracked

#### Scenario: Budget alert
- **GIVEN** daily API costs exceed threshold ($100/day)
- **WHEN** cost monitoring runs
- **THEN** alert is sent to administrators
- **AND** cost report is generated
- **AND** system can be configured to pause reasoning generation

### Requirement: Reasoning Retrieval

The system SHALL provide API endpoints to retrieve reasoning for assessments.

#### Scenario: Retrieve reasoning
- **GIVEN** an assessment has generated reasoning
- **WHEN** GET /api/v1/reasoning/{assessment_id} is called
- **THEN** reasoning text is returned
- **AND** generation method is included (gpt4 or template)
- **AND** generated_at timestamp is included

#### Scenario: Reasoning included in assessment response
- **GIVEN** a skill assessment is retrieved
- **WHEN** GET /api/v1/skills/{student_id} is called
- **THEN** each skill includes its reasoning text
- **AND** reasoning provides context for the score
