# Evidence Normalization Documentation

## Overview

The evidence fusion system combines multiple sources of evidence to produce skill assessments. Each evidence source provides data in different scales and formats, requiring normalization to ensure fair weighting and combination.

## Evidence Sources

### 1. ML Inference Evidence
**Source:** `app/services/skill_inference.py`
**Raw Scale:** 0.0 - 1.0 (model predictions)
**Normalization:** Already normalized (no transformation needed)

ML inference provides predictions directly in the 0-1 range from trained XGBoost regression models.

```python
# Example ML evidence
ml_score = 0.75  # Already in [0, 1]
```

### 2. Linguistic Features Evidence
**Source:** `app/models/features.py` → `LinguisticFeatures`
**Raw Scales:** Various (counts, ratios, scores)
**Normalization Method:** Z-score normalization + sigmoid transformation

Linguistic features include:
- **Counts** (word_count, noun_count, verb_count): 0 - ∞
- **Ratios** (empathy_markers, problem_solving_language): 0.0 - 1.0
- **Sentiment scores** (positive_sentiment, negative_sentiment): -1.0 - 1.0
- **Complexity metrics** (syntactic_complexity, readability_score): 0.0 - 100.0+

#### Normalization Formula

```python
# Step 1: Z-score normalization
z_score = (value - mean) / std_dev

# Step 2: Sigmoid transformation to [0, 1]
normalized = 1 / (1 + exp(-z_score))
```

#### Skill-Specific Normalization Parameters

**Empathy:**
```python
{
    'empathy_markers': {'mean': 0.15, 'std': 0.08},
    'social_processes': {'mean': 0.12, 'std': 0.06},
    'positive_sentiment': {'mean': 0.3, 'std': 0.2},
}
```

**Problem Solving:**
```python
{
    'problem_solving_language': {'mean': 0.10, 'std': 0.05},
    'cognitive_processes': {'mean': 0.08, 'std': 0.04},
    'syntactic_complexity': {'mean': 3.5, 'std': 1.2},
}
```

**Self-Regulation:**
```python
{
    'word_count': {'mean': 150, 'std': 75},
    'avg_sentence_length': {'mean': 12.0, 'std': 4.0},
}
```

**Resilience:**
```python
{
    'perseverance_indicators': {'mean': 0.08, 'std': 0.04},
    'negative_sentiment': {'mean': -0.1, 'std': 0.15},
}
```

### 3. Behavioral Features Evidence
**Source:** `app/models/features.py` → `BehavioralFeatures`
**Raw Scales:** Various (rates, counts, durations)
**Normalization Method:** Min-max normalization

Behavioral features include:
- **Rates** (task_completion_rate, recovery_rate): 0.0 - 1.0
- **Efficiency metrics** (time_efficiency): 0.0 - 2.0+ (ratio)
- **Counts** (retry_count, event_count): 0 - ∞
- **Durations** (focus_duration): 0 - ∞ seconds

#### Normalization Formula

```python
# Min-max scaling to [0, 1]
normalized = (value - min_value) / (max_value - min_value)

# With clipping for outliers
normalized = clip(normalized, 0.0, 1.0)
```

#### Skill-Specific Normalization Ranges

**Empathy:**
```python
{
    'collaboration_indicators': {'min': 0, 'max': 10},
    'leadership_indicators': {'min': 0, 'max': 8},
}
```

**Problem Solving:**
```python
{
    'task_completion_rate': {'min': 0.0, 'max': 1.0},
    'time_efficiency': {'min': 0.0, 'max': 2.0},
    'retry_count': {'min': 0, 'max': 5},  # Clipped at 5
}
```

**Self-Regulation:**
```python
{
    'distraction_resistance': {'min': 0.0, 'max': 1.0},
    'focus_duration': {'min': 0, 'max': 3600},  # seconds (1 hour)
}
```

**Resilience:**
```python
{
    'recovery_rate': {'min': 0.0, 'max': 1.0},
    'retry_count': {'min': 0, 'max': 10},
}
```

## Fusion Weight Configuration

After normalization, evidence sources are combined using weighted averaging. Weights are skill-specific and configurable via `app/core/fusion_config.py`.

### Default Weights

**Empathy:**
- ML Inference: 0.50
- Linguistic Features: 0.25 (higher - language indicators important)
- Behavioral Features: 0.15
- Confidence Adjustment: 0.10

**Problem Solving:**
- ML Inference: 0.50
- Linguistic Features: 0.20
- Behavioral Features: 0.20 (balanced)
- Confidence Adjustment: 0.10

**Self-Regulation:**
- ML Inference: 0.50
- Linguistic Features: 0.10 (lower)
- Behavioral Features: 0.30 (higher - focus/distraction data)
- Confidence Adjustment: 0.10

**Resilience:**
- ML Inference: 0.50
- Linguistic Features: 0.15
- Behavioral Features: 0.25 (higher - retry/recovery patterns)
- Confidence Adjustment: 0.10

### Updating Weights

Weights can be updated via API or configuration file:

```python
# Via API
PUT /api/v1/fusion/weights/empathy
{
    "ml_inference": 0.55,
    "linguistic_features": 0.20,
    "behavioral_features": 0.15,
    "confidence_adjustment": 0.10
}

# Via config file
# Edit config/fusion_weights.json
{
    "version": "1.1.0",
    "description": "Updated weights after validation study",
    "weights": {
        "empathy": {
            "ml_inference": 0.55,
            ...
        }
    }
}
```

## Evidence Combination Formula

```python
# Final skill score calculation
final_score = (
    weights['ml_inference'] * ml_score +
    weights['linguistic_features'] * normalized_ling_score +
    weights['behavioral_features'] * normalized_beh_score
) * (1 + weights['confidence_adjustment'] * (confidence - 0.5))
```

Where:
- `ml_score`: ML model prediction [0, 1]
- `normalized_ling_score`: Normalized linguistic evidence [0, 1]
- `normalized_beh_score`: Normalized behavioral evidence [0, 1]
- `confidence`: Model confidence [0, 1]
- Weights sum to 1.0

## Confidence Adjustment

The confidence adjustment factor modifies the final score based on prediction confidence:

```python
adjustment = 1 + weight * (confidence - 0.5)

# Examples:
# High confidence (0.9): adjustment = 1 + 0.1 * (0.9 - 0.5) = 1.04
# Medium confidence (0.5): adjustment = 1 + 0.1 * (0.5 - 0.5) = 1.00
# Low confidence (0.3): adjustment = 1 + 0.1 * (0.3 - 0.5) = 0.98
```

This means:
- High confidence predictions are slightly boosted (up to 4%)
- Low confidence predictions are slightly reduced (down to 2%)

## Data Quality Considerations

### Missing Data Handling

**Linguistic Features Missing:**
- Default to zeros for all linguistic features
- Confidence adjustment factor reduces final score
- Weight redistributes to ML inference and behavioral features

**Behavioral Features Missing:**
- Default to baseline values (distraction_resistance=1.0, others=0)
- Similar confidence and weight adjustments

**Both Missing:**
- Fall back to ML inference only
- Heavy confidence penalty applied
- Explicit warning logged

### Outlier Handling

**Linguistic Features:**
- Z-scores clamped to [-3, 3] range
- Prevents extreme values from dominating

**Behavioral Features:**
- Hard limits on maximum values (e.g., retry_count ≤ 10)
- Time-based features capped at reasonable maximums

## Validation Approach

To validate normalization parameters:

1. **Collect validation dataset**
   - 500+ students with expert ratings
   - Diverse demographic representation

2. **Calculate statistics**
   ```python
   mean = np.mean(feature_values)
   std = np.std(feature_values)
   min_val = np.percentile(feature_values, 5)  # 5th percentile
   max_val = np.percentile(feature_values, 95)  # 95th percentile
   ```

3. **Validate correlation**
   - Compare normalized scores to expert ratings
   - Target Pearson correlation > 0.7

4. **A/B test weight configurations**
   - Test alternative weight combinations
   - Measure against held-out validation set

## Implementation Files

- **Normalization Logic:** `app/services/evidence_fusion.py`
- **Weight Configuration:** `app/core/fusion_config.py`
- **API Endpoints:** `app/api/endpoints/fusion_config.py`
- **Models:** `app/models/features.py`

## Future Improvements

1. **Adaptive normalization**
   - Update parameters based on incoming data
   - Maintain rolling statistics

2. **Contextual weights**
   - Different weights for different age groups
   - Subject-specific weight profiles

3. **Uncertainty quantification**
   - Provide confidence intervals on final scores
   - Flag high-uncertainty predictions

4. **Feature selection**
   - Identify most predictive features per skill
   - Remove redundant or noisy features

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
