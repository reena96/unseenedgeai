# Evidence Fusion Capability

## Purpose

The Evidence Fusion capability combines skill scores from multiple sources (transcripts, game telemetry, teacher rubrics) using learned weights, calculates confidence based on source agreement, extracts supporting evidence, and generates human-readable reasoning via GPT-4.

## Requirements

### Requirement: Multi-Source Score Fusion

The system SHALL combine skill scores from transcript analysis, game telemetry, and teacher rubrics using skill-specific learned weights.

#### Scenario: Three-source fusion
- **GIVEN** a student has scores from all three sources for a skill
- **WHEN** performing evidence fusion
- **THEN** the system applies skill-specific weights (e.g., Empathy: transcript 0.35, game 0.40, teacher 0.25)
- **AND** calculates weighted average as the fused score
- **AND** fused score is clamped between 0 and 1

#### Scenario: Two-source fusion (missing data)
- **GIVEN** a student has scores from only two sources
- **WHEN** performing evidence fusion
- **THEN** weights are normalized to sum to 1.0 across available sources
- **AND** fused score is calculated from available sources only
- **AND** confidence is reduced due to missing source

#### Scenario: Single-source fallback
- **GIVEN** a student has score from only one source
- **WHEN** performing evidence fusion
- **THEN** the single source score is used as the fused score
- **AND** confidence is capped at 0.60
- **AND** assessment is flagged for additional data collection

### Requirement: Skill-Specific Weight Configuration

The system SHALL use different fusion weights for each skill based on source detectability.

#### Scenario: High transcript detectability (Communication)
- **GIVEN** inference for Communication skill
- **WHEN** applying fusion weights
- **THEN** transcript weight is 0.50 (highest)
- **AND** game weight is 0.25
- **AND** teacher weight is 0.25

#### Scenario: Low transcript detectability (Adaptability)
- **GIVEN** inference for Adaptability skill
- **WHEN** applying fusion weights
- **THEN** transcript weight is 0.20 (lowest)
- **AND** game weight is 0.50 (highest)
- **AND** teacher weight is 0.30

#### Scenario: Weight configuration update
- **GIVEN** Phase 0 validation determines updated optimal weights
- **WHEN** deploying new weight configuration
- **THEN** weights are updated via configuration (not code change)
- **AND** historical assessments preserve weights used at time of creation
- **AND** weight version is tracked

### Requirement: Confidence Calculation

The system SHALL calculate confidence based on agreement between sources and data quality.

#### Scenario: High agreement confidence
- **GIVEN** all three source scores are within 0.15 of each other
- **WHEN** calculating confidence
- **THEN** standard deviation is low (<0.08)
- **AND** confidence is calculated as 1.0 - (std * 2)
- **AND** confidence exceeds 0.85

#### Scenario: Low agreement confidence
- **GIVEN** source scores diverge significantly (e.g., 0.3, 0.7, 0.5)
- **WHEN** calculating confidence
- **THEN** standard deviation is high (>0.15)
- **AND** confidence is reduced proportionally
- **AND** confidence is below 0.70
- **AND** divergence triggers evidence review

#### Scenario: Missing data confidence penalty
- **GIVEN** only one source is available
- **WHEN** calculating confidence
- **THEN** confidence is capped at 0.60 regardless of score
- **AND** missing source count is recorded
- **AND** recommendation to collect more data is generated

### Requirement: Evidence Extraction

The system SHALL extract top 3-5 pieces of supporting evidence for each skill assessment.

#### Scenario: Evidence from transcripts
- **GIVEN** a student's transcript segments for a period
- **WHEN** extracting evidence for Empathy
- **THEN** the system identifies segments with high empathy markers
- **AND** ranks segments by relevance score
- **AND** extracts top 3 segments with context (before/after text)
- **AND** includes timestamp and confidence

#### Scenario: Evidence from game telemetry
- **GIVEN** a student's game session data
- **WHEN** extracting evidence for Resilience
- **THEN** the system identifies retry events and recovery patterns
- **AND** creates human-readable descriptions (e.g., "Retried challenge 4 times before succeeding")
- **AND** includes mission name and timestamp

#### Scenario: Evidence from teacher rubrics
- **GIVEN** a teacher's rubric assessment for a student
- **WHEN** extracting evidence
- **THEN** the system includes teacher's qualitative feedback
- **AND** maps rubric score (1-4) to context
- **AND** includes assessment date

#### Scenario: Evidence diversity
- **GIVEN** evidence extraction for a skill
- **WHEN** selecting top evidence items
- **THEN** the system ensures diversity across sources (at least 1 from each available source)
- **AND** avoids redundant similar evidence
- **AND** total evidence count is 3-5 items

### Requirement: GPT-4 Reasoning Generation

The system SHALL generate 2-3 sentence growth-oriented explanations using GPT-4.

#### Scenario: Reasoning for proficient skill
- **GIVEN** a student has a high fused score (≥0.75)
- **WHEN** generating reasoning
- **THEN** GPT-4 is prompted with skill, score, evidence, and features
- **AND** output is 2-3 sentences explaining why score is high
- **AND** language is asset-based and specific (cites evidence)
- **AND** temperature is 0.3 for consistency

#### Scenario: Reasoning for developing skill
- **GIVEN** a student has a medium score (0.50-0.74)
- **WHEN** generating reasoning
- **THEN** GPT-4 output acknowledges strengths
- **AND** identifies specific growth opportunities
- **AND** language is growth-oriented, not deficit-focused

#### Scenario: Reasoning for emerging skill
- **GIVEN** a student has a low score (<0.50)
- **WHEN** generating reasoning
- **THEN** GPT-4 output focuses on incremental progress
- **AND** suggests specific actionable next steps
- **AND** avoids negative or judgmental language

#### Scenario: Reasoning caching
- **GIVEN** reasoning has been generated for an assessment
- **WHEN** the same assessment is queried again
- **THEN** cached reasoning is returned (no GPT-4 call)
- **AND** regeneration only occurs if evidence changes
- **AND** cache is invalidated after 7 days

### Requirement: Cost Management

The system SHALL monitor and optimize GPT-4 API costs.

#### Scenario: Cost tracking
- **GIVEN** reasoning generation via GPT-4
- **WHEN** each API call completes
- **THEN** token count (input + output) is recorded
- **AND** estimated cost is calculated ($0.03/1K input, $0.06/1K output)
- **AND** costs are aggregated per school and per month

#### Scenario: Cost alerts
- **GIVEN** monthly GPT-4 costs for 100 students
- **WHEN** costs exceed $35 (target is $28)
- **THEN** an alert is triggered for review
- **AND** admin is notified to check usage patterns

#### Scenario: Rate limiting
- **GIVEN** high volume of reasoning requests
- **WHEN** approaching OpenAI rate limits (10K requests/day Tier 1)
- **THEN** requests are queued and throttled
- **AND** rate limit is respected to avoid API errors

### Requirement: Fusion Pipeline Orchestration

The system SHALL orchestrate the complete fusion workflow.

#### Scenario: End-to-end fusion
- **GIVEN** skill scores are available from all sources
- **WHEN** fusion is triggered
- **THEN** the system performs these steps in order:
  1. Retrieve source scores from database
  2. Apply skill-specific fusion weights
  3. Calculate confidence from source agreement
  4. Extract evidence from each source
  5. Generate GPT-4 reasoning
  6. Store fused assessment with evidence and reasoning
- **AND** total pipeline latency is <10 seconds per student per skill

#### Scenario: Async batch fusion
- **GIVEN** nightly inference has generated source scores for 30 students
- **WHEN** batch fusion is triggered
- **THEN** all students are processed in parallel
- **AND** fusion completes within 10 minutes
- **AND** progress is tracked and logged

### Requirement: Historical Assessment Updates

The system SHALL handle updates when new data sources become available.

#### Scenario: Late teacher rubric submission
- **GIVEN** an assessment was created with only transcript + game sources
- **WHEN** teacher submits a rubric 2 days later
- **THEN** the assessment is regenerated with all three sources
- **AND** confidence score improves
- **AND** previous assessment is archived with "superseded" status
- **AND** update timestamp is recorded

#### Scenario: Assessment versioning
- **GIVEN** multiple versions of an assessment exist
- **WHEN** querying historical data
- **THEN** the system returns the most recent version by default
- **AND** historical versions are accessible via API
- **AND** version history shows what changed (new sources, updated weights)

## Non-Functional Requirements

### Performance
- **Fusion latency:** <10 seconds per student per skill
- **Batch fusion:** 30 students × 7 skills in <10 minutes
- **GPT-4 reasoning:** <5 seconds per generation (with caching: <100ms)

### Cost
- **GPT-4 monthly cost:** ~$28 for 100 students (7 skills × weekly assessment)
- **Target cost per reasoning:** $0.03-0.05
- **Alert threshold:** $35/month for 100 students (125% of target)

### Accuracy
- **Fusion validity:** Fused scores should correlate r ≥ 0.55 with ground truth
- **Confidence calibration:** Low confidence (<0.70) assessments should have higher error
- **Evidence relevance:** 80%+ of evidence rated relevant by teachers

### Reliability
- **Uptime:** 99% for fusion service
- **GPT-4 error handling:** 100% of failures trigger fallback (cached or template reasoning)

## Dependencies

### External Services
- **OpenAI GPT-4 API:** Reasoning generation
  - Model: `gpt-4`
  - Rate limit: 10,000 requests/day (Tier 1)
  - Max tokens: 150 per completion

### Internal Services
- **Skill Inference:** Provides transcript-based and game-based scores
- **Teacher Rubrics Service:** Provides teacher-assessed scores
- **Database:** Stores fused assessments, evidence, reasoning

### Libraries
- **openai:** Python client (v1.10+)
- **NumPy:** Statistical calculations (v1.26+)

## API Endpoints

### POST /api/v1/fusion/assess
Trigger evidence fusion for a student and skill.

**Request:**
```json
{
  "student_id": "uuid",
  "skill": "empathy",
  "period_start": "2024-01-01",
  "period_end": "2024-01-07",
  "sources": {
    "transcript": 0.78,
    "game": 0.82,
    "teacher": 0.75
  }
}
```

**Response:** 201 Created
```json
{
  "assessment_id": "uuid",
  "student_id": "uuid",
  "skill": "empathy",
  "fused_score": 0.79,
  "confidence": 0.87,
  "reasoning": "Marcus demonstrates strong empathy through...",
  "evidence_count": 5
}
```

### GET /api/v1/evidence/{assessment_id}
Retrieve evidence for an assessment.

**Response:** 200 OK
```json
{
  "assessment_id": "uuid",
  "evidence_items": [
    {
      "id": "uuid",
      "type": "linguistic",
      "source": "transcript",
      "text": "I think I understand how you feel about this...",
      "context_before": "When Sarah mentioned she was struggling,",
      "context_after": "Marcus listened carefully.",
      "timestamp": "2024-01-03T10:23:15Z",
      "relevance_score": 0.92
    },
    {
      "type": "behavioral",
      "source": "game",
      "text": "Chose empathetic dialogue option in Mission 1",
      "mission": "Understanding Perspectives",
      "relevance_score": 0.88
    },
    {
      "type": "contextual",
      "source": "teacher_rubric",
      "text": "Shows good understanding of others' perspectives in group work",
      "assessment_date": "2024-01-05",
      "relevance_score": 0.80
    }
  ]
}
```

### GET /api/v1/reasoning/{assessment_id}
Retrieve GPT-4 reasoning.

**Response:** 200 OK
```json
{
  "assessment_id": "uuid",
  "reasoning_text": "Marcus demonstrates strong empathy through consistent use of perspective-taking language in class discussions and empathetic choices in game scenarios. His teacher also rates him highly for understanding others' perspectives. This score reflects growth in his ability to recognize and respond to peers' emotions.",
  "generated_by": "gpt-4",
  "generated_at": "2024-01-08T10:15:32Z",
  "token_count": 68,
  "cost": 0.048
}
```

### POST /api/v1/fusion/batch
Trigger batch fusion for a classroom.

**Request:**
```json
{
  "classroom_id": "uuid",
  "skills": "all",
  "period_start": "2024-01-01",
  "period_end": "2024-01-07"
}
```

**Response:** 202 Accepted
```json
{
  "batch_id": "uuid",
  "student_count": 28,
  "skill_count": 7,
  "status": "processing"
}
```

## Data Models

### skill_assessments Table (Updated with fusion data)
```sql
CREATE TABLE skill_assessments (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    skill VARCHAR(50) NOT NULL,

    -- Fused output
    score FLOAT CHECK (score BETWEEN 0 AND 1),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),

    -- Source scores
    transcript_score FLOAT,
    game_score FLOAT,
    teacher_score FLOAT,

    -- Fusion metadata
    fusion_weights JSONB,  -- {"transcript": 0.35, "game": 0.40, "teacher": 0.25}

    assessment_period_start DATE,
    assessment_period_end DATE,

    created_at TIMESTAMP DEFAULT NOW(),
    superseded_by UUID REFERENCES skill_assessments(id),  -- For versioning

    UNIQUE(student_id, skill, assessment_period_start, assessment_period_end)
);
```

### evidence_items Table
```sql
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY,
    assessment_id UUID REFERENCES skill_assessments(id),

    evidence_type VARCHAR(50),  -- linguistic, behavioral, contextual
    source_type VARCHAR(50),    -- transcript, game, teacher_rubric
    source_id UUID,

    evidence_text TEXT NOT NULL,
    context_before TEXT,
    context_after TEXT,
    timestamp_in_source FLOAT,

    relevance_score FLOAT CHECK (relevance_score BETWEEN 0 AND 1),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evidence_assessment ON evidence_items(assessment_id);
```

### reasoning_explanations Table
```sql
CREATE TABLE reasoning_explanations (
    id UUID PRIMARY KEY,
    assessment_id UUID REFERENCES skill_assessments(id) UNIQUE,

    reasoning_text TEXT NOT NULL,
    reasoning_type VARCHAR(50) DEFAULT 'llm_generated',

    generated_by VARCHAR(50),  -- 'gpt-4', 'gpt-4-turbo', 'template_v1'
    generation_cost FLOAT,
    token_count INTEGER,

    generated_at TIMESTAMP DEFAULT NOW()
);
```

## Error Codes

- `FUSION_001`: Missing source scores
- `FUSION_002`: Invalid fusion weights configuration
- `FUSION_003`: GPT-4 API call failed
- `FUSION_004`: Evidence extraction failed
- `FUSION_005`: Confidence calculation error
- `FUSION_006`: Assessment versioning conflict

## Monitoring and Metrics

### Key Metrics
- **Fusion success rate:** >99%
- **GPT-4 success rate:** >98% (with retries)
- **Evidence relevance (teacher rating):** >80%
- **Reasoning quality (teacher rating):** >75% "helpful"
- **Average confidence score:** Track by skill
- **Monthly GPT-4 cost:** Target $28/100 students

### Alerts
- GPT-4 error rate >5% in 1 hour
- Monthly GPT-4 cost >125% of target
- Fusion failure rate >2%
- Confidence scores consistently <0.60 for a skill
- Evidence extraction failure rate >5%

## Testing Strategy

### Unit Tests
- Fusion weight application
- Confidence calculation with various source agreements
- Evidence ranking logic
- Cost calculation accuracy

### Integration Tests
- End-to-end fusion pipeline
- GPT-4 reasoning generation (use test API key)
- Evidence extraction from all sources
- Assessment versioning and updates

### Validation Tests
- **Fused score validity:** Correlation with teacher ratings r ≥ 0.55
- **Evidence relevance:** Survey 10 teachers on 50 assessments
- **Reasoning quality:** Survey 10 teachers on 50 reasoning texts
- **Confidence calibration:** Verify low confidence → higher error rate

### Performance Tests
- Single fusion: <10 seconds
- Batch fusion: 30 students × 7 skills in <10 minutes
- GPT-4 caching: <100ms for cached reasoning

## Future Enhancements (Out of Scope for Phase 1)

- **Template-Based Reasoning:** Fallback to templates to reduce GPT-4 costs
- **Multi-Modal Evidence:** Include images from student work
- **Interactive Evidence Viewer:** Teachers can add/remove evidence
- **Custom Fusion Weights:** Allow teachers to adjust weights per student
- **Real-Time Fusion:** Update assessments as new data arrives
- **Student-Facing Reasoning:** Age-appropriate explanations for students
