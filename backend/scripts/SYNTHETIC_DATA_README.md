# Synthetic Training Data Generation Pipeline

## Overview

This pipeline generates synthetic training data for ML-based skill assessment models using a combination of GPT-4 API, NLP feature extraction, behavioral simulation, and automated labeling.

**Pipeline Stages:**
1. **Text Generation** - Generate realistic student responses (GPT-4 or templates)
2. **Linguistic Feature Extraction** - Extract 16 NLP features (spaCy, NLTK)
3. **Behavioral Feature Simulation** - Generate 9 game telemetry features
4. **Derived Features** - Compute 4 skill-specific composite features
5. **Auto-Labeling** - Label skill scores 0.0-1.0 (GPT-4 or heuristics)

---

## Quick Start

### Option 1: Free Pipeline (No API Costs)

Generate 100 samples using template expansion and heuristic labeling:

```bash
cd backend
source venv/bin/activate

# Install dependencies
pip install spacy nltk textblob
python -m spacy download en_core_web_sm
python -m nltk.downloader vader_lexicon

# Generate training data (FREE, ~2 minutes)
python scripts/generate_training_data.py \
    --count 100 \
    --output data/training_100_free.csv
```

**Output:** 100 samples, 30+ features, ready for XGBoost training

---

### Option 2: GPT-4 Pipeline (Best Quality)

Generate 1,000 samples using GPT-4 for text and labels:

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Generate training data (PAID ~$10-15, ~30 minutes)
python scripts/generate_training_data.py \
    --count 1000 \
    --output data/training_1000_gpt.csv \
    --use-openai
```

**Output:** 1,000 high-quality samples with GPT-4 generated text and labels

---

### Option 3: Hybrid Pipeline (Good Balance)

Generate text with GPT-4, use heuristic labeling:

```bash
# PAID ~$5, ~10 minutes
python scripts/generate_training_data.py \
    --count 500 \
    --output data/training_500_hybrid.csv \
    --use-openai \
    --no-auto-label
```

**Output:** 500 samples with GPT-4 text quality, fast heuristic labels

---

## Individual Pipeline Scripts

Each stage can be run independently:

### Stage 1: Generate Responses

```bash
# Template-based (FREE)
python scripts/generate_synthetic_responses.py \
    --count 200 \
    --output data/responses.csv

# GPT-4 based (PAID)
python scripts/generate_synthetic_responses.py \
    --count 200 \
    --output data/responses_gpt.csv \
    --use-openai
```

### Stage 2: Extract Linguistic Features

```bash
python scripts/extract_linguistic_features.py \
    --input data/responses.csv \
    --output data/responses_with_linguistic.csv
```

### Stage 3: Generate Behavioral Features

```bash
python scripts/generate_behavioral_features.py \
    --input data/responses_with_linguistic.csv \
    --output data/full_features.csv
```

### Stage 4: Auto-Label Skill Scores

```bash
# Heuristic labeling (FREE)
python scripts/auto_label_skills.py \
    --input data/full_features.csv \
    --output data/training_data.csv

# GPT-4 labeling (PAID)
python scripts/auto_label_skills.py \
    --input data/full_features.csv \
    --output data/training_data_gpt_labeled.csv \
    --use-openai
```

---

## Training Models

Once you have training data, train XGBoost models:

```bash
python app/ml/train_models.py \
    --data data/training_1000_gpt.csv \
    --models-dir models/
```

**Expected Performance:**
- With 100 samples: R² ~0.45-0.60 (proof-of-concept)
- With 500 samples: R² ~0.60-0.75 (decent)
- With 1,000 samples: R² ~0.70-0.85 (good)
- With 5,000 samples: R² ~0.80-0.90 (production-ready)

---

## Cost Estimates

| Configuration | Samples | API Calls | Estimated Cost | Time |
|--------------|---------|-----------|----------------|------|
| Free (templates + heuristics) | 100 | 0 | $0 | 2 min |
| Free (templates + heuristics) | 1,000 | 0 | $0 | 15 min |
| Hybrid (GPT text + heuristics) | 100 | 100 | ~$0.50 | 3 min |
| Hybrid (GPT text + heuristics) | 1,000 | 1,000 | ~$5 | 25 min |
| Full GPT-4 (text + labels) | 100 | 200 | ~$1 | 5 min |
| Full GPT-4 (text + labels) | 1,000 | 2,000 | ~$10-15 | 30 min |
| Full GPT-4 (text + labels) | 5,000 | 10,000 | ~$50-75 | 2 hours |

**Note:** Using `gpt-4o-mini` model (cheaper than `gpt-4`)

---

## Output Data Format

### CSV Structure

```csv
response,skill,skill_level,grade,source,empathy_markers,problem_solving_language,...,empathy_score,problem_solving_score,self_regulation_score,resilience_score
"I helped my friend when they were sad...",empathy,high,3,gpt-4o-mini,0.15,0.08,...,0.82,0.55,0.48,0.51
```

### Columns

**Metadata (5):**
- `response` - Student text
- `skill` - Primary skill (empathy, problem_solving, self_regulation, resilience)
- `skill_level` - Proficiency (high, medium, developing)
- `grade` - Grade level (2-8)
- `source` - Generation method (gpt-4o-mini, template_expansion)

**Linguistic Features (16):**
- `empathy_markers`, `problem_solving_language`, `perseverance_indicators`
- `social_processes`, `cognitive_processes`
- `positive_sentiment`, `negative_sentiment`
- `avg_sentence_length`, `syntactic_complexity`
- `word_count`, `unique_word_count`, `readability_score`
- `noun_count`, `verb_count`, `adj_count`, `adv_count`

**Behavioral Features (9):**
- `task_completion_rate`, `time_efficiency`, `retry_count`
- `recovery_rate`, `distraction_resistance`, `focus_duration`
- `collaboration_indicators`, `leadership_indicators`, `event_count`

**Derived Features (4):**
- `empathy_social_interaction` - Social language × collaboration
- `problem_solving_cognitive` - Cognitive processes × efficiency
- `self_regulation_focus` - Focus × distraction resistance
- `resilience_recovery` - Recovery rate × perseverance

**Target Labels (4):**
- `empathy_score` (0.0-1.0)
- `problem_solving_score` (0.0-1.0)
- `self_regulation_score` (0.0-1.0)
- `resilience_score` (0.0-1.0)

**Total:** 38 columns (5 metadata + 29 features + 4 targets)

---

## Data Augmentation with SMOTE

To expand dataset further using SMOTE:

```python
from imblearn.over_sampling import SMOTE
import pandas as pd

# Load existing synthetic data
df = pd.read_csv('data/training_1000_gpt.csv')

# Separate features and targets
feature_cols = [col for col in df.columns if col not in [
    'response', 'skill', 'skill_level', 'grade', 'source',
    'empathy_score', 'problem_solving_score',
    'self_regulation_score', 'resilience_score'
]]

X = df[feature_cols].values
y_empathy = df['empathy_score'].values

# Apply SMOTE to create 5,000 samples from 1,000
smote = SMOTE(sampling_strategy='auto', k_neighbors=5, random_state=42)
X_augmented, y_augmented = smote.fit_resample(X, (y_empathy * 10).astype(int))

# Save augmented data
# ... (implement save logic)
```

---

## Validation & Quality Checks

The pipeline performs automatic validation:

✅ **Column Completeness** - All 29 features + 4 targets present
✅ **No Missing Values** - NaN detection and reporting
✅ **Score Ranges** - All scores in [0.0, 1.0]
✅ **Distribution Balance** - Skills/levels/grades evenly distributed

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'spacy'`

**Solution:**
```bash
pip install spacy nltk textblob
python -m spacy download en_core_web_sm
```

### Issue: `openai.AuthenticationError`

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
# Or add to .env file
```

### Issue: Rate limit errors from OpenAI

**Solution:** Reduce batch size:
```bash
python scripts/auto_label_skills.py --batch-size 5 --input data.csv --output labeled.csv --use-openai
```

### Issue: Scores not in [0, 1] range

**Solution:** This shouldn't happen, but if it does:
```python
df['empathy_score'] = df['empathy_score'].clip(0.0, 1.0)
```

---

## Recommendations

### For MVP Testing (Quick Start)
```bash
# Generate 100 samples, FREE, 2 minutes
python scripts/generate_training_data.py --count 100 --output data/mvp_training.csv
python app/ml/train_models.py --data data/mvp_training.csv --models-dir models/
```

### For Production (Best Quality)
```bash
# Generate 1,000 samples with GPT-4, ~$15, 30 minutes
python scripts/generate_training_data.py --count 1000 --output data/prod_training.csv --use-openai

# Optional: Augment with SMOTE to 5,000 samples
# ... (implement SMOTE augmentation)

# Train models
python app/ml/train_models.py --data data/prod_training.csv --models-dir models/
```

### For Budget-Conscious
```bash
# Generate 500 hybrid samples, ~$5, 15 minutes
python scripts/generate_training_data.py --count 500 --output data/budget_training.csv --use-openai --no-auto-label
python app/ml/train_models.py --data data/budget_training.csv --models-dir models/
```

---

## Next Steps

1. **Generate initial dataset** (start with 100 free samples)
2. **Train baseline models** to validate pipeline
3. **Evaluate model performance** (R², MAE, MSE)
4. **Scale up** to 1,000+ samples if performance is good
5. **Collect real data** to fine-tune models (5-10% real data can significantly improve performance)
6. **Deploy models** to production

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  SYNTHETIC DATA PIPELINE                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  1. TEXT GENERATION                   │
        │  • GPT-4o-mini OR Template Expansion  │
        │  • 4 skills × 3 levels × 7 grades     │
        └───────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  2. LINGUISTIC FEATURES (16)          │
        │  • spaCy: POS, syntax, complexity     │
        │  • NLTK: Sentiment (VADER)            │
        │  • Custom: Skill-specific keywords    │
        └───────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  3. BEHAVIORAL FEATURES (9)           │
        │  • Simulated game telemetry           │
        │  • Based on skill level + grade       │
        │  • Realistic distributions            │
        └───────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  4. DERIVED FEATURES (4)              │
        │  • Skill-specific composites          │
        │  • Combine linguistic + behavioral    │
        └───────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  5. AUTO-LABELING (4 scores)          │
        │  • GPT-4o-mini OR Heuristic Rules     │
        │  • Expert-level skill scores 0.0-1.0  │
        └───────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────┐
        │  OUTPUT: training_data.csv            │
        │  • 38 columns (29 features + 4 labels)│
        │  • Ready for XGBoost training         │
        └───────────────────────────────────────┘
```

---

## Contact & Support

For issues or questions about the synthetic data pipeline, see:
- `backend/docs/TRAINING_DATA_FORMAT.md` - Feature specifications
- `backend/docs/ARCHITECTURE.md` - System architecture
- `backend/app/ml/train_models.py` - Model training code
