# Training Data Format Specification

## Overview

This document specifies the format and structure of training data required to train XGBoost models for skill assessment. The training data combines linguistic analysis, behavioral telemetry, and expert-labeled skill scores into a single CSV file.

**Model Architecture:** XGBoost Regression (one model per skill)

**Skills Trained:**
- Empathy
- Problem-Solving
- Self-Regulation
- Resilience

**Total Features:** 26 per skill (16 linguistic + 9 behavioral + 1 derived)

---

## CSV Structure

### File Format

- **Format:** CSV (comma-separated values)
- **Encoding:** UTF-8
- **Header Row:** Required (column names)
- **Missing Values:** Not allowed (use 0 or imputed values)
- **File Extension:** `.csv`

### Column Order

Columns must appear in this exact order:

```
student_id,
empathy_markers, problem_solving_language, perseverance_indicators, ...  # 16 linguistic
task_completion_rate, time_efficiency, retry_count, ...                   # 9 behavioral
empathy_social_interaction, problem_solving_cognitive, ...                # 4 derived (1 per skill)
empathy_score, problem_solving_score, ...                                 # 4 target labels
```

---

## Feature Columns

### 1. Linguistic Features (16 columns)

Extracted from student speech transcripts using NLP techniques.

#### 1.1 Skill-Specific Language Markers

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `empathy_markers` | float | 0.0 - 1.0 | Frequency of empathy-related words (feel, understand, care) | 0.15 |
| `problem_solving_language` | float | 0.0 - 1.0 | Frequency of problem-solving terms (solution, analyze, solve) | 0.08 |
| `perseverance_indicators` | float | 0.0 - 1.0 | Frequency of perseverance words (try, persist, continue) | 0.12 |

**Calculation Method:**
```python
empathy_markers = count(empathy_words) / total_words
```

**Empathy Word List:** feel, feelings, understand, care, help, support, concern, compassionate, empathize

**Problem-Solving Word List:** solve, solution, analyze, think, figure, plan, strategy, approach, method

**Perseverance Word List:** try, persist, continue, keep going, don't give up, persevere, determined

---

#### 1.2 Psychological Process Markers

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `social_processes` | float | 0.0 - 1.0 | Frequency of social words (we, friend, talk, share) | 0.12 |
| `cognitive_processes` | float | 0.0 - 1.0 | Frequency of cognitive words (think, know, consider) | 0.08 |

**Based on:** LIWC (Linguistic Inquiry and Word Count) dictionaries

---

#### 1.3 Sentiment Scores

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `positive_sentiment` | float | -1.0 to 1.0 | Overall positive sentiment of speech | 0.3 |
| `negative_sentiment` | float | -1.0 to 1.0 | Overall negative sentiment of speech | -0.1 |

**Calculation:** VADER sentiment analysis

**Interpretation:**
- `positive_sentiment`: 0.0 = neutral, +1.0 = very positive
- `negative_sentiment`: 0.0 = neutral, -1.0 = very negative

---

#### 1.4 Linguistic Complexity Metrics

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `avg_sentence_length` | float | 0.0+ | Average words per sentence | 12.5 |
| `syntactic_complexity` | float | 0.0+ | Syntactic parse tree depth | 3.8 |
| `readability_score` | float | 0.0 - 100.0 | Flesch-Kincaid readability | 65.2 |

**Formulas:**
```python
avg_sentence_length = total_words / total_sentences

readability_score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
```

---

#### 1.5 Word Counts

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `word_count` | int | 0+ | Total word count in transcript | 250 |
| `unique_word_count` | int | 0+ | Number of unique words | 120 |
| `noun_count` | int | 0+ | Count of nouns (POS tagging) | 45 |
| `verb_count` | int | 0+ | Count of verbs | 38 |
| `adj_count` | int | 0+ | Count of adjectives | 22 |
| `adv_count` | int | 0+ | Count of adverbs | 15 |

**Extraction:** spaCy POS tagging

---

### 2. Behavioral Features (9 columns)

Extracted from game telemetry and task completion data.

#### 2.1 Task Performance Metrics

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `task_completion_rate` | float | 0.0 - 1.0 | Proportion of tasks completed | 0.85 |
| `time_efficiency` | float | 0.0+ | Ratio of expected/actual time | 1.2 |
| `retry_count` | int | 0+ | Number of task retries | 3 |
| `recovery_rate` | float | 0.0 - 1.0 | Success rate after failure | 0.67 |

**Calculations:**
```python
task_completion_rate = completed_tasks / total_tasks

time_efficiency = expected_time / actual_time
# > 1.0 = faster than expected
# < 1.0 = slower than expected

recovery_rate = successful_retries / total_retries
```

---

#### 2.2 Attention & Focus Metrics

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `distraction_resistance` | float | 0.0 - 1.0 | Ability to maintain focus | 0.92 |
| `focus_duration` | float | 0.0+ | Average focus duration (seconds) | 245.5 |

**Calculations:**
```python
distraction_resistance = 1.0 - (distraction_events / total_events)

focus_duration = sum(focus_periods) / count(focus_periods)
```

---

#### 2.3 Social Interaction Metrics

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `collaboration_indicators` | int | 0+ | Count of collaborative actions | 8 |
| `leadership_indicators` | int | 0+ | Count of leadership actions | 5 |

**Collaboration Actions:**
- Helping another student
- Asking for help
- Sharing resources
- Working together

**Leadership Actions:**
- Initiating group activities
- Organizing others
- Making group decisions
- Encouraging peers

---

#### 2.4 General Activity Metric

| Column Name | Data Type | Valid Range | Description | Example |
|------------|-----------|-------------|-------------|---------|
| `event_count` | int | 0+ | Total interaction events | 127 |

**Event Types:**
- Clicks
- Key presses
- Task submissions
- Navigation actions

---

### 3. Derived Features (4 columns - 1 per skill)

Skill-specific composite features calculated from base features.

| Column Name | Data Type | Valid Range | Description | Calculation |
|------------|-----------|-------------|-------------|-------------|
| `empathy_social_interaction` | float | 0.0 - 1.0 | Empathy × social interaction | `empathy_markers * social_processes` |
| `problem_solving_cognitive` | float | 0.0 - 1.0 | Problem-solving × cognition | `problem_solving_language * cognitive_processes` |
| `self_regulation_focus` | float | 0.0+ | Self-regulation × focus | `distraction_resistance * focus_duration` |
| `resilience_recovery` | float | 0.0+ | Resilience × recovery | `retry_count * recovery_rate` |

**Purpose:** Capture interaction effects between related features

---

### 4. Target Labels (4 columns)

Expert-labeled skill scores (ground truth).

| Column Name | Data Type | Valid Range | Description | Labeling Criteria |
|------------|-----------|-------------|-------------|-------------------|
| `empathy_score` | float | 0.0 - 1.0 | Expert-rated empathy skill | 3+ raters, average score |
| `problem_solving_score` | float | 0.0 - 1.0 | Expert-rated problem-solving | 3+ raters, average score |
| `self_regulation_score` | float | 0.0 - 1.0 | Expert-rated self-regulation | 3+ raters, average score |
| `resilience_score` | float | 0.0 - 1.0 | Expert-rated resilience | 3+ raters, average score |

**Scoring Rubric (0.0 - 1.0 scale):**
- **0.0 - 0.25:** Emerging skill (limited evidence)
- **0.26 - 0.50:** Developing skill (inconsistent application)
- **0.51 - 0.75:** Proficient skill (consistent application)
- **0.76 - 1.00:** Advanced skill (mastery level)

**Inter-Rater Reliability:** Require Krippendorff's alpha ≥ 0.80

---

## Example CSV Rows

### Header Row
```csv
student_id,empathy_markers,problem_solving_language,perseverance_indicators,social_processes,cognitive_processes,positive_sentiment,negative_sentiment,avg_sentence_length,syntactic_complexity,word_count,unique_word_count,readability_score,noun_count,verb_count,adj_count,adv_count,task_completion_rate,time_efficiency,retry_count,recovery_rate,distraction_resistance,focus_duration,collaboration_indicators,leadership_indicators,event_count,empathy_social_interaction,problem_solving_cognitive,self_regulation_focus,resilience_recovery,empathy_score,problem_solving_score,self_regulation_score,resilience_score
```

### Sample Data Row 1 (High Empathy Student)
```csv
student_001,0.15,0.08,0.10,0.12,0.06,0.30,-0.05,12.5,3.2,250,120,65.0,45,38,22,15,0.85,1.2,3,0.67,0.92,245.5,8,5,127,0.018,0.005,225.86,2.01,0.82,0.75,0.88,0.79
```

**Interpretation:**
- High empathy markers (0.15) and social processes (0.12)
- Strong task completion (0.85) and focus (0.92)
- Expert-rated empathy score: 0.82 (proficient/advanced)

### Sample Data Row 2 (High Problem-Solving Student)
```csv
student_002,0.08,0.18,0.12,0.08,0.15,0.25,-0.10,14.2,4.1,320,145,58.5,62,48,28,18,0.92,1.5,2,0.85,0.88,280.0,6,7,156,0.006,0.027,246.4,1.70,0.68,0.89,0.85,0.82
```

**Interpretation:**
- High problem-solving language (0.18) and cognitive processes (0.15)
- Excellent task completion (0.92) and time efficiency (1.5)
- Expert-rated problem-solving score: 0.89 (advanced)

### Sample Data Row 3 (Developing Skills Student)
```csv
student_003,0.06,0.05,0.04,0.05,0.04,0.10,-0.20,8.5,2.1,120,65,72.0,28,22,10,8,0.55,0.7,8,0.40,0.65,120.0,3,1,68,0.003,0.002,78.0,3.20,0.45,0.48,0.52,0.50
```

**Interpretation:**
- Lower across most linguistic features
- Moderate task completion (0.55) with more retries (8)
- Expert-rated scores: 0.45-0.52 (developing range)

---

## Data Quality Requirements

### Minimum Sample Size

| Dataset Split | Minimum Size | Recommended Size |
|--------------|--------------|------------------|
| Training | 800 students | 2,000+ students |
| Validation | 100 students | 300+ students |
| Test | 100 students | 300+ students |

**Total Minimum:** 1,000 students
**Recommended Total:** 2,500+ students

---

### Missing Data Handling

**Policy:** No missing values allowed in training data

**Imputation Strategies:**

1. **Linguistic Features:**
   - If transcript empty → all linguistic features = 0
   - If partial transcript → calculate from available text

2. **Behavioral Features:**
   - `task_completion_rate` → use 0 if no tasks attempted
   - `distraction_resistance` → default to 1.0 if no tracking
   - `focus_duration` → use 0 if no tracking
   - Other behavioral → use 0

3. **Target Labels:**
   - Must have valid expert scores (0.0 - 1.0)
   - No imputation allowed - exclude student if label missing

---

### Outlier Treatment

**Detection Criteria:**
- Values outside expected ranges (see column specifications)
- Z-score > 3.0 for continuous features
- Extreme values that fail domain validation

**Handling:**
```python
# Clip to valid ranges
empathy_markers = np.clip(empathy_markers, 0.0, 1.0)
retry_count = np.clip(retry_count, 0, 20)  # Cap at reasonable maximum
focus_duration = np.clip(focus_duration, 0, 3600)  # Cap at 1 hour
```

---

### Class Balance Considerations

**Target Distribution Recommendations:**

| Skill Level | Score Range | Target % of Dataset |
|-------------|-------------|---------------------|
| Emerging | 0.00 - 0.25 | 15-20% |
| Developing | 0.26 - 0.50 | 30-35% |
| Proficient | 0.51 - 0.75 | 30-35% |
| Advanced | 0.76 - 1.00 | 15-20% |

**If Imbalanced:**
- Use stratified sampling for train/val/test splits
- Consider SMOTE or class weights during training
- Evaluate model performance per skill level

---

## Data Preparation Pipeline

### Step 1: Feature Extraction

```bash
# Extract linguistic features from transcripts
python scripts/extract_linguistic_features.py \
  --transcripts data/transcripts/ \
  --output data/linguistic_features.csv

# Extract behavioral features from telemetry
python scripts/extract_behavioral_features.py \
  --telemetry data/telemetry/ \
  --output data/behavioral_features.csv
```

### Step 2: Feature Merging

```python
import pandas as pd

# Load feature sets
linguistic = pd.read_csv('data/linguistic_features.csv')
behavioral = pd.read_csv('data/behavioral_features.csv')
labels = pd.read_csv('data/expert_labels.csv')

# Merge on student_id
df = linguistic.merge(behavioral, on='student_id')
df = df.merge(labels, on='student_id')

# Calculate derived features
df['empathy_social_interaction'] = \
    df['empathy_markers'] * df['social_processes']
df['problem_solving_cognitive'] = \
    df['problem_solving_language'] * df['cognitive_processes']
df['self_regulation_focus'] = \
    df['distraction_resistance'] * df['focus_duration']
df['resilience_recovery'] = \
    df['retry_count'] * df['recovery_rate']

# Save combined dataset
df.to_csv('data/training_data.csv', index=False)
```

### Step 3: Data Validation

```python
# Validate data quality
python scripts/validate_training_data.py \
  --input data/training_data.csv \
  --output data/validation_report.json

# Expected output:
# {
#   "total_rows": 2500,
#   "missing_values": 0,
#   "outliers_detected": 15,
#   "outliers_clipped": 15,
#   "class_distribution": {
#     "empathy": {"emerging": 0.18, "developing": 0.32, ...},
#     ...
#   }
# }
```

### Step 4: Train/Validation/Test Split

```python
from sklearn.model_selection import train_test_split

# Read data
df = pd.read_csv('data/training_data.csv')

# Stratify by empathy_score bins
df['empathy_bin'] = pd.cut(df['empathy_score'], bins=4, labels=[0,1,2,3])

# 70% train, 15% validation, 15% test
train, temp = train_test_split(
    df, test_size=0.3, random_state=42, stratify=df['empathy_bin']
)
val, test = train_test_split(
    temp, test_size=0.5, random_state=42, stratify=temp['empathy_bin']
)

# Save splits
train.to_csv('data/train.csv', index=False)
val.to_csv('data/validation.csv', index=False)
test.to_csv('data/test.csv', index=False)

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
# Train: 1750, Val: 375, Test: 375
```

---

## Model Training

### Training Command

```bash
python app/ml/train_models.py \
  --data-path data/train.csv \
  --models-dir models/ \
  --version 1.0.0 \
  --validate-data

# Optional flags:
# --cross-validate      # Perform 5-fold cross-validation
# --tune-hyperparams    # Run hyperparameter search
# --verbose            # Show detailed training logs
```

### Training Process

**For each skill (empathy, problem_solving, self_regulation, resilience):**

1. Load and prepare data
   - Extract 26 features for the skill
   - Extract target label (e.g., `empathy_score`)
   - Split into train/validation sets

2. Train XGBoost model
   ```python
   model = xgb.XGBRegressor(
       n_estimators=100,
       max_depth=6,
       learning_rate=0.1,
       subsample=0.8,
       colsample_bytree=0.8,
       random_state=42
   )
   model.fit(X_train, y_train)
   ```

3. Evaluate performance
   - MSE (Mean Squared Error)
   - R² Score
   - MAE (Mean Absolute Error)

4. Save model artifacts
   - `{skill}_model.pkl` - Trained XGBoost model
   - `{skill}_features.pkl` - Feature names list
   - `metadata.json` - Model version and metrics

### Expected Performance Metrics

**Target Benchmarks:**

| Skill | R² Score | MAE | MSE |
|-------|----------|-----|-----|
| Empathy | ≥ 0.75 | ≤ 0.10 | ≤ 0.02 |
| Problem-Solving | ≥ 0.78 | ≤ 0.09 | ≤ 0.018 |
| Self-Regulation | ≥ 0.72 | ≤ 0.11 | ≤ 0.022 |
| Resilience | ≥ 0.76 | ≤ 0.10 | ≤ 0.020 |

**If metrics below target:**
- Increase training data size
- Check for data quality issues
- Tune hyperparameters
- Add more relevant features

---

## Model Evaluation

### Evaluation Script

```bash
python app/ml/evaluate_models.py \
  --test-data data/test.csv \
  --models-dir models/ \
  --output results/evaluation_report.json
```

### Evaluation Metrics

```json
{
  "empathy": {
    "r2_score": 0.82,
    "mse": 0.015,
    "mae": 0.087,
    "feature_importance": {
      "empathy_markers": 0.18,
      "social_processes": 0.15,
      "empathy_social_interaction": 0.12,
      ...
    }
  },
  "problem_solving": {
    "r2_score": 0.85,
    "mse": 0.013,
    "mae": 0.079,
    ...
  },
  ...
}
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

# 5-fold cross-validation
cv_scores = cross_val_score(
    model, X, y, cv=5, scoring='r2'
)
print(f"Cross-val R² scores: {cv_scores}")
print(f"Mean R²: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
```

---

## Feature Importance Analysis

After training, analyze which features contribute most to predictions:

```python
import matplotlib.pyplot as plt

# Get feature importance
importance = model.feature_importances_
feature_names = get_feature_names(SkillType.EMPATHY)

# Sort by importance
indices = np.argsort(importance)[::-1][:10]  # Top 10

# Plot
plt.figure(figsize=(10, 6))
plt.bar(range(10), importance[indices])
plt.xticks(range(10), [feature_names[i] for i in indices], rotation=45)
plt.title('Top 10 Features for Empathy Prediction')
plt.tight_layout()
plt.savefig('empathy_feature_importance.png')
```

**Expected Top Features by Skill:**

**Empathy:**
1. empathy_markers (0.18)
2. social_processes (0.15)
3. empathy_social_interaction (0.12)
4. collaboration_indicators (0.10)
5. positive_sentiment (0.09)

**Problem-Solving:**
1. task_completion_rate (0.20)
2. problem_solving_language (0.17)
3. cognitive_processes (0.14)
4. time_efficiency (0.12)
5. problem_solving_cognitive (0.11)

---

## Versioning & Deployment

### Model Versioning

```bash
# Version format: MAJOR.MINOR.PATCH
# Example: 1.0.0

# Save model with version
python app/ml/train_models.py \
  --data-path data/train.csv \
  --models-dir models/ \
  --version 1.0.0

# Creates:
# models/
#   empathy_model.pkl
#   empathy_features.pkl
#   ...
#   metadata.json
```

### Metadata Format

```json
{
  "version": "1.0.0",
  "created_at": "2025-11-01T12:00:00Z",
  "training_data": {
    "path": "data/train.csv",
    "rows": 1750,
    "features": 26
  },
  "models": {
    "empathy": {
      "checksum": "sha256:abc123...",
      "size_bytes": 524288,
      "r2_score": 0.82,
      "mse": 0.015,
      "mae": 0.087
    },
    ...
  }
}
```

### Deployment

```bash
# Upload to GCS
gsutil -m cp -r models/* gs://unseenedgeai-models/v1.0.0/

# Update production deployment
gcloud run services update mass-backend \
  --region=us-central1 \
  --set-env-vars="MODELS_DIR=/app/models" \
  --update-volumes=models=/app/models \
  --update-volume-mounts=models:models=ro
```

---

## Common Issues & Solutions

### Issue 1: Low Model Accuracy

**Symptoms:**
- R² score < 0.70
- High prediction errors

**Solutions:**
1. Increase training data size (aim for 2,000+ students)
2. Check for labeling errors in expert scores
3. Add more relevant features
4. Tune hyperparameters:
   ```python
   from sklearn.model_selection import GridSearchCV

   param_grid = {
       'max_depth': [4, 6, 8],
       'learning_rate': [0.05, 0.1, 0.15],
       'n_estimators': [100, 200, 300]
   }

   grid_search = GridSearchCV(model, param_grid, cv=5, scoring='r2')
   grid_search.fit(X_train, y_train)
   best_model = grid_search.best_estimator_
   ```

---

### Issue 2: Class Imbalance

**Symptoms:**
- Model predicts mostly mid-range scores
- Poor performance on emerging/advanced students

**Solutions:**
1. Use stratified sampling
2. Apply class weights:
   ```python
   from sklearn.utils.class_weight import compute_sample_weight

   # Bin scores for weighting
   y_binned = pd.cut(y_train, bins=4, labels=[0,1,2,3])
   sample_weights = compute_sample_weight('balanced', y_binned)

   model.fit(X_train, y_train, sample_weight=sample_weights)
   ```
3. Oversample minority classes (SMOTE)

---

### Issue 3: Feature Scaling Issues

**Symptoms:**
- Some features dominate others
- Poor model convergence

**Solutions:**
```python
from sklearn.preprocessing import StandardScaler

# Standardize features (mean=0, std=1)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Save scaler
joblib.dump(scaler, 'models/feature_scaler.pkl')
```

---

## References

### Related Documentation
- **Architecture:** `docs/ARCHITECTURE.md`
- **Deployment:** `docs/DEPLOYMENT.md`
- **Performance:** `docs/PERFORMANCE_TUNING.md`
- **Evidence Normalization:** `docs/EVIDENCE_NORMALIZATION.md`

### Implementation Files
- **Training Script:** `app/ml/train_models.py`
- **Evaluation Script:** `app/ml/evaluate_models.py`
- **Inference Service:** `app/services/skill_inference.py`
- **Model Registry:** `app/ml/model_metadata.py`

### External Resources
- **XGBoost Documentation:** https://xgboost.readthedocs.io/
- **scikit-learn:** https://scikit-learn.org/
- **VADER Sentiment:** https://github.com/cjhutto/vaderSentiment
- **spaCy NLP:** https://spacy.io/

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Data Schema Version:** 1.0.0
