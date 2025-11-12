# Skill Inference Capability Delta

## ADDED Requirements

### Requirement: Model Loading and Management

The system SHALL load and manage trained XGBoost models for all 7 skills.

#### Scenario: Model initialization on service startup
- **GIVEN** the inference service starts
- **WHEN** initialization runs
- **THEN** all 7 XGBoost models are loaded from Cloud Storage
- **AND** corresponding feature scalers are loaded
- **AND** models are cached in memory for fast inference
- **AND** model versions are logged

#### Scenario: Model version update
- **GIVEN** a new model version is deployed to Cloud Storage
- **WHEN** the service receives a reload signal
- **THEN** new models are downloaded and loaded
- **AND** old models are kept until new models are validated
- **AND** switchover happens atomically to avoid downtime

### Requirement: Skill Score Prediction

The system SHALL predict skill scores from linguistic and behavioral features using trained models.

#### Scenario: Single skill inference
- **GIVEN** extracted features for a student and skill
- **WHEN** POST /api/v1/skills/infer is called with skill name and features
- **THEN** features are converted to numpy array in correct order
- **AND** features are scaled using the skill-specific scaler
- **AND** model.predict_proba() returns probability of high skill
- **AND** score is clipped to 0-1 range
- **AND** confidence is calculated from prediction margin
- **AND** top 5 feature importances are included in response

#### Scenario: Batch inference
- **GIVEN** features for multiple students
- **WHEN** POST /api/v1/skills/infer/batch is called
- **THEN** inference runs in vectorized mode for performance
- **AND** all predictions are returned in array
- **AND** processing completes in <30s per student for all 7 skills

#### Scenario: Inference with missing features
- **GIVEN** some features are missing from input
- **WHEN** inference is attempted
- **THEN** missing features are imputed with default values (e.g., 0 or mean)
- **AND** warning is logged about missing features
- **AND** confidence score is reduced due to incomplete data

### Requirement: Confidence Scoring

The system SHALL calculate confidence scores based on prediction certainty.

#### Scenario: High confidence prediction
- **GIVEN** model predicts with strong probability (0.9 vs 0.1)
- **WHEN** confidence is calculated
- **THEN** confidence score is high (>0.8)
- **AND** confidence is based on margin from decision boundary

#### Scenario: Low confidence prediction
- **GIVEN** model predicts with weak probability (0.55 vs 0.45)
- **WHEN** confidence is calculated
- **THEN** confidence score is low (<0.5)
- **AND** prediction is flagged for additional review

### Requirement: Feature Importance Extraction

The system SHALL extract feature importance for model explainability.

#### Scenario: Feature importance for prediction
- **GIVEN** a skill inference has completed
- **WHEN** feature importance is extracted
- **THEN** model.feature_importances_ is queried
- **AND** top 5 most important features are identified
- **AND** feature names and importance scores are returned
- **AND** features are ranked by contribution to prediction
