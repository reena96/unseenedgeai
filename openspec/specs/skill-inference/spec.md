# Skill Inference Capability

## Purpose

The Skill Inference capability uses machine learning models to predict student skill levels from linguistic and behavioral features. It provides quantitative skill scores (0-1 scale) for all 7 non-academic skills with confidence metrics.

## Requirements

### Requirement: Feature Extraction

The system SHALL extract linguistic and behavioral features from student data for ML inference.

#### Scenario: Linguistic feature extraction from transcripts
- **GIVEN** transcript segments attributed to a student
- **WHEN** extracting features for a time period (e.g., 1 week)
- **THEN** the system computes linguistic patterns using spaCy, VADER, and LIWC
- **AND** features include word count, sentiment, POS tags, and skill-specific markers
- **AND** features are normalized and stored in the database
- **AND** extraction completes within 10 seconds per student

#### Scenario: Behavioral feature extraction from game telemetry
- **GIVEN** game session data for a student
- **WHEN** extracting behavioral features
- **THEN** the system analyzes choice patterns, timing, and persistence
- **AND** features include task completion, strategy switching, and resilience indicators
- **AND** features are aggregated across all completed missions

#### Scenario: Missing data handling
- **GIVEN** a student has no transcript data for a period
- **WHEN** extracting features
- **THEN** linguistic features are set to null
- **AND** inference uses game and teacher data only
- **AND** confidence score reflects missing data source

### Requirement: ML Model Inference

The system SHALL use trained XGBoost models to predict skill scores from features.

#### Scenario: Single skill inference
- **GIVEN** extracted features for a student and time period
- **WHEN** inferring a specific skill (e.g., empathy)
- **THEN** the system loads the trained skill-specific XGBoost model
- **AND** applies feature scaling using the stored scaler
- **AND** generates a probability score between 0 and 1
- **AND** computes feature importance for interpretability
- **AND** inference completes in <5 seconds

#### Scenario: All skills inference
- **GIVEN** extracted features for a student
- **WHEN** inferring all 7 skills
- **THEN** the system runs inference for each skill in parallel
- **AND** all 7 skill scores are returned
- **AND** total processing time is <30 seconds per student

#### Scenario: Model versioning
- **GIVEN** multiple trained model versions
- **WHEN** performing inference
- **THEN** the system uses the configured active model version
- **AND** the model version is recorded with each assessment
- **AND** historical assessments preserve the model version used

### Requirement: Confidence Scoring

The system SHALL calculate confidence scores based on data quality and model certainty.

#### Scenario: High confidence inference
- **GIVEN** complete data from all sources (transcript, game, teacher)
- **WHEN** calculating confidence
- **THEN** confidence is based on prediction margin from 0.5 threshold
- **AND** confidence is weighted by data source completeness
- **AND** high-quality data yields confidence >0.80

#### Scenario: Low confidence due to missing data
- **GIVEN** only one data source is available (e.g., game only)
- **WHEN** calculating confidence
- **THEN** confidence is penalized for missing sources
- **AND** maximum confidence is capped at 0.70 for single-source
- **AND** confidence score reflects uncertainty

#### Scenario: Low confidence due to model uncertainty
- **GIVEN** model prediction is near the decision boundary (score ~0.5)
- **WHEN** calculating confidence
- **THEN** confidence is proportional to distance from 0.5
- **AND** predictions near boundaries have confidence <0.60
- **AND** low confidence triggers manual review recommendation

### Requirement: Assessment Period Management

The system SHALL generate skill assessments for configurable time periods.

#### Scenario: Weekly assessment generation
- **GIVEN** one week of student data has been collected
- **WHEN** generating assessments
- **THEN** features are aggregated over the 7-day period
- **AND** one assessment per skill is created
- **AND** the assessment period (start/end dates) is recorded

#### Scenario: Overlapping period handling
- **GIVEN** an assessment already exists for a student and period
- **WHEN** attempting to create a duplicate assessment
- **THEN** the system prevents duplicate creation
- **AND** existing assessment can be updated if new data is available
- **AND** update timestamp is recorded

#### Scenario: Historical trend calculation
- **GIVEN** multiple assessments over time for a student
- **WHEN** querying skill history
- **THEN** assessments are ordered by period end date
- **AND** trend direction (improving, stable, declining) is calculated
- **AND** statistical significance of trends is tested

### Requirement: Batch Processing

The system SHALL support batch inference for entire classrooms.

#### Scenario: Classroom batch inference
- **GIVEN** a classroom with 30 students
- **WHEN** triggering batch inference
- **THEN** all students are processed in parallel
- **AND** processing completes within 15 minutes
- **AND** progress updates are provided every 10%
- **AND** failures for individual students don't block others

#### Scenario: Scheduled nightly inference
- **GIVEN** daily data collection is complete
- **WHEN** the nightly batch job runs (e.g., 2 AM)
- **THEN** assessments are generated for all active students
- **AND** new assessments are available by morning
- **AND** job status and errors are logged

### Requirement: Feature Importance and Interpretability

The system SHALL provide interpretable explanations of model predictions.

#### Scenario: Feature importance extraction
- **GIVEN** a skill inference has been completed
- **WHEN** extracting feature importance
- **THEN** the top 5 contributing features are identified
- **AND** importance scores are normalized to sum to 1.0
- **AND** feature importance is stored as JSONB

#### Scenario: Human-readable feature names
- **GIVEN** technical feature names (e.g., "empathy_perspective_taking")
- **WHEN** presenting to teachers
- **THEN** features are translated to readable labels (e.g., "Perspective-taking language")
- **AND** brief descriptions explain what each feature measures

### Requirement: Model Retraining Pipeline

The system SHALL support periodic model retraining with new ground truth data.

#### Scenario: Model training with new data
- **GIVEN** updated ground truth annotations from Phase 0 or teacher feedback
- **WHEN** initiating model retraining
- **THEN** new models are trained for all 7 skills
- **AND** train/test split is 70/30
- **AND** models are evaluated on held-out test set
- **AND** performance metrics (MAE, RMSE, correlation) are calculated

#### Scenario: Model deployment
- **GIVEN** newly trained models pass validation thresholds
- **WHEN** deploying to production
- **THEN** models are versioned with timestamp and performance metrics
- **AND** previous model version is archived but remains accessible
- **AND** A/B testing capability allows gradual rollout

#### Scenario: Model performance monitoring
- **GIVEN** a model is deployed in production
- **WHEN** generating assessments over time
- **THEN** correlation with teacher ratings is continuously tracked
- **AND** if correlation drops below 0.45, an alert is triggered
- **AND** model drift is detected and flagged for retraining

### Requirement: Error Handling and Fallbacks

The system SHALL handle inference errors gracefully.

#### Scenario: Feature extraction failure
- **GIVEN** feature extraction fails for a student
- **WHEN** attempting inference
- **THEN** the error is logged with full context
- **AND** inference is retried once
- **AND** if retry fails, assessment is marked as "pending" not "failed"
- **AND** teacher is notified to check data quality

#### Scenario: Model loading failure
- **GIVEN** a model file is corrupted or missing
- **WHEN** attempting inference
- **THEN** the system falls back to the previous model version
- **AND** an alert is sent to engineering team
- **AND** assessments are marked with fallback model version

## Non-Functional Requirements

### Performance
- **Single inference:** <5 seconds per skill
- **All skills inference:** <30 seconds per student
- **Batch processing:** 30 students in <15 minutes
- **Feature extraction:** <10 seconds per student

### Accuracy
- **Target correlation:** r ≥ 0.50 vs teacher ratings (optimal: r ≥ 0.55)
- **Minimum per-skill correlation:** r ≥ 0.40
- **Decision gate:** If any skill falls below r = 0.30, trigger review

### Scalability
- **Phase 1:** 100 students, weekly assessments
- **Phase 2:** 500 students, weekly assessments
- **Phase 3:** 5,000 students, weekly assessments

### Reliability
- **Uptime:** 99% for inference service
- **Error rate:** <1% of inference jobs fail
- **Retry success:** 90% of failed jobs succeed on retry

## Dependencies

### External Services
- **OpenAI GPT-4 API:** (used by Evidence Fusion for reasoning, not by Skill Inference directly)

### Internal Services
- **Audio Processing:** Provides transcript segments
- **Game Telemetry:** Provides behavioral data
- **Evidence Fusion:** Consumes skill scores for multi-source fusion
- **Database:** Feature storage and assessment storage

### ML Libraries
- **XGBoost:** Gradient boosting models (v2.0+)
- **Scikit-learn:** Feature scaling, preprocessing (v1.4+)
- **spaCy:** NLP processing (v3.7+, model: en_core_web_sm)
- **VADER:** Sentiment analysis (v3.3+)
- **LIWC-22:** Psychological language categories
- **joblib:** Model serialization
- **NumPy:** Numerical operations (v1.26+)
- **pandas:** Data manipulation (v2.2+)

## API Endpoints

### POST /api/v1/skills/infer
Trigger skill inference for a student.

**Request:**
```json
{
  "student_id": "uuid",
  "skills": ["empathy", "adaptability"],  // or "all"
  "period_start": "2024-01-01",
  "period_end": "2024-01-07"
}
```

**Response:** 202 Accepted
```json
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_completion": "2024-01-08T10:05:00Z"
}
```

### GET /api/v1/jobs/{job_id}/status
Check inference job status.

**Response:** 200 OK
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "results": {
    "empathy": 0.78,
    "adaptability": 0.65
  },
  "completed_at": "2024-01-08T10:04:32Z"
}
```

### POST /api/v1/skills/batch
Trigger batch inference for a classroom.

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
  "batch_job_id": "uuid",
  "student_count": 28,
  "status": "queued"
}
```

### GET /api/v1/features/{student_id}
Retrieve extracted features for debugging.

**Query Params:**
- `period_start`: Date
- `period_end`: Date
- `source`: "linguistic" | "behavioral" | "all"

**Response:** 200 OK
```json
{
  "student_id": "uuid",
  "period": {"start": "2024-01-01", "end": "2024-01-07"},
  "linguistic_features": {
    "word_count": 1520,
    "sentiment_positive": 0.32,
    "empathy_perspective_taking": 12,
    "collaboration_inclusive": 8
  },
  "behavioral_features": {
    "task_completion_rate": 0.85,
    "strategy_switching_count": 3,
    "persistence_score": 0.78
  }
}
```

## Data Models

### linguistic_features Table
```sql
CREATE TABLE linguistic_features (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    source_type VARCHAR(50),  -- 'transcript_segment', 'project'
    source_id UUID,
    extracted_at TIMESTAMP DEFAULT NOW(),

    -- Empathy
    empathy_perspective_taking INTEGER DEFAULT 0,
    empathy_emotion_words INTEGER DEFAULT 0,

    -- Adaptability
    adaptability_flexibility INTEGER DEFAULT 0,

    -- Communication
    communication_clarity FLOAT,

    -- Collaboration
    collaboration_inclusive INTEGER DEFAULT 0,

    -- Baseline
    word_count INTEGER,
    sentiment_positive FLOAT,

    all_features JSONB  -- Complete feature vector
);
```

### behavioral_features Table
```sql
CREATE TABLE behavioral_features (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    session_id UUID REFERENCES game_sessions(id),
    extracted_at TIMESTAMP DEFAULT NOW(),

    -- Problem-solving
    task_completion_rate FLOAT,

    -- Adaptability
    strategy_switching_count INTEGER,

    -- Resilience
    retry_count INTEGER,
    persistence_score FLOAT,

    all_features JSONB
);
```

### skill_assessments Table (Output)
```sql
CREATE TABLE skill_assessments (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    skill VARCHAR(50) NOT NULL,
    score FLOAT CHECK (score BETWEEN 0 AND 1),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),

    assessment_period_start DATE,
    assessment_period_end DATE,

    -- Pre-fusion source scores
    transcript_score FLOAT,
    game_score FLOAT,
    teacher_score FLOAT,

    model_version VARCHAR(50),
    feature_importance JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, skill, assessment_period_start, assessment_period_end)
);
```

## Error Codes

- `SKILL_001`: Feature extraction failed
- `SKILL_002`: Model file not found or corrupted
- `SKILL_003`: Invalid date range for assessment period
- `SKILL_004`: Insufficient data for inference
- `SKILL_005`: Model inference timeout
- `SKILL_006`: Batch job failed

## Monitoring and Metrics

### Key Metrics
- **Inference latency p95:** <30 seconds per student (all 7 skills)
- **Correlation with teacher ratings:** Target r ≥ 0.50 per skill
- **Assessment generation success rate:** >99%
- **Feature extraction success rate:** >98%
- **Model drift:** Monitor correlation trend over time

### Alerts
- Correlation drops below 0.45 for any skill
- Inference failure rate >2% in 1 hour
- Feature extraction failure rate >5% in 1 hour
- Batch job processing time >30 minutes for 30 students
- Model loading failures

## Testing Strategy

### Unit Tests
- Feature extraction logic (linguistic patterns, sentiment)
- Confidence score calculation
- Feature importance extraction
- Model version management

### Integration Tests
- End-to-end: Features → Inference → Database storage
- Batch processing with 30 test students
- Retry logic on simulated failures

### Validation Tests
- **Correlation validation:** Compare against 100 teacher ratings
- **Feature importance consistency:** Verify top features align with skill definitions
- **Confidence calibration:** Low confidence predictions should have higher error rates

### Performance Tests
- Single inference: 100 students, measure p95 latency
- Batch inference: 30 students, verify <15 min completion
- Load test: 1,000 simultaneous inference requests

## Future Enhancements (Out of Scope for Phase 1)

- **Deep Learning Models:** Experiment with neural networks for higher accuracy
- **Transfer Learning:** Use pre-trained language models (BERT, RoBERTa)
- **Active Learning:** Prioritize samples for teacher annotation based on uncertainty
- **Causal Inference:** Identify interventions that improve skills
- **Multi-Task Learning:** Train single model for all 7 skills jointly
- **Explainable AI:** SHAP values or LIME for detailed explanations
