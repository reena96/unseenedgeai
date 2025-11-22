# MASS Technical Overview: ML Pipeline & Feature Architecture

## System Overview
**MASS (Middle School Non-Academic Skills Measurement)** - AI-powered assessment system measuring 7 non-academic skills through multi-source data fusion: classroom transcripts, game telemetry, and teacher ratings.

**Tech Stack:** FastAPI • PostgreSQL + TimescaleDB • Google Cloud (STT, Storage, Run) • XGBoost • GPT-4 • spaCy • VADER

---

## Data Pipeline (4 Stages)

### 1. Data Creation & Ground Truth (Tasks 18-20)
- **2,100 classroom transcript segments** manually annotated by 4 expert coders
- **Validated rubrics** with 1-4 scale for each skill + behavioral anchors
- **Target IRR:** Krippendorff's Alpha ≥ 0.75 (agreement between coders)
- **Training split:** 70% train / 30% test (300 segments per skill minimum)

### 2. Transcription (Task 9) - Google Cloud Speech-to-Text
- **Audio → Cloud Storage** → Speech-to-Text API (video model, speaker diarization)
- **Output:** Full transcript + word-level timestamps + confidence scores (75%+ accuracy target)
- **Features:** Enhanced models, 1-6 speaker detection, automatic punctuation

### 3. Feature Extraction (Task 10) - 26 Features Total
**Linguistic (16):** spaCy NLP + VADER Sentiment + LIWC-style patterns
**Behavioral (9):** Game telemetry event analysis
**Derived (1):** Multi-source interaction metrics

### 4. Model Training & Inference (Tasks 11-13)
- **Algorithm:** XGBoost (7 models, one per skill)
- **Validation:** Correlation r ≥ 0.40 with teacher ratings on test set
- **Inference:** Multi-source fusion → XGBoost prediction → GPT-4 reasoning generation
- **Latency:** < 30 seconds per student, full 7-skill profile

---

## Complete Feature List (26 Total)

### Linguistic Features (16) - From Classroom Transcripts
| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | `empathy_markers` | int | "understand", "feel", "empathy", "care", "support", "help", "listen" |
| 2 | `problem_solving_language` | int | "solve", "analyze", "think", "plan", "strategy", "test", "find" |
| 3 | `perseverance_indicators` | int | "continue", "persist", "keep", "try", "again", "determined", "effort" |
| 4 | `social_processes` | int | Social pronouns: "i", "we", "you", "they", "us", "our", "your" |
| 5 | `cognitive_processes` | int | "think", "know", "understand", "believe", "reason", "learn", "wonder" |
| 6 | `positive_sentiment` | 0-1 | VADER positive sentiment score |
| 7 | `negative_sentiment` | 0-1 | VADER negative sentiment score |
| 8 | `avg_sentence_length` | float | Average words per sentence |
| 9 | `syntactic_complexity` | 0-1 | Flesch Reading Ease (inverted/normalized) |
| 10 | `word_count` | int | Total words (excluding punctuation) |
| 11 | `unique_word_count` | int | Unique lemmatized words |
| 12 | `readability_score` | float | Flesch-Kincaid Grade Level |
| 13 | `noun_count` | int | Count via spaCy POS tagging |
| 14 | `verb_count` | int | Count via spaCy POS tagging |
| 15 | `adj_count` | int | Count via spaCy POS tagging |
| 16 | `adv_count` | int | Count via spaCy POS tagging |

### Behavioral Features (9) - From Game Telemetry
| # | Feature | Type | Description |
|---|---------|------|-------------|
| 17 | `task_completion_rate` | 0-1 | % of tasks completed successfully |
| 18 | `time_efficiency` | 0-1 | Speed of completion (normalized, higher = faster) |
| 19 | `retry_count` | int | Number of retry attempts after failures |
| 20 | `recovery_rate` | 0-1 | Success rate after failures |
| 21 | `distraction_resistance` | 0-1 | Focus ability (fewer distractions = higher) |
| 22 | `focus_duration` | float | Average focus period (seconds) |
| 23 | `collaboration_indicators` | int | "share_resource", "help_peer", "team_decision" events |
| 24 | `leadership_indicators` | int | "delegate_task", "lead_discussion", "make_decision" events |
| 25 | `event_count` | int | Total game telemetry events |

### Derived Feature (1) - Multi-Source
| # | Feature | Type | Description |
|---|---------|------|-------------|
| 26 | `interaction_ratio` | float | (social_processes + collaboration) / (word_count + events) |

---

## Model Architecture

### 7 XGBoost Models (One Per Skill)
```
Empathy          → empathy.pkl          (PRIMARY: empathy_markers, social_processes, positive_sentiment)
Adaptability     → adaptability.pkl     (PRIMARY: recovery_rate, time_efficiency, task_completion_rate)
Problem Solving  → problem_solving.pkl  (PRIMARY: problem_solving_language, cognitive_processes, task_completion_rate)
Self-Regulation  → self_regulation.pkl  (PRIMARY: distraction_resistance, focus_duration, syntactic_complexity)
Resilience       → resilience.pkl       (PRIMARY: perseverance_indicators, retry_count, recovery_rate)
Communication    → communication.pkl    (PRIMARY: word_count, avg_sentence_length, readability_score)
Collaboration    → collaboration.pkl    (PRIMARY: collaboration_indicators, leadership_indicators, social_processes)
```

### Training Configuration
- **Input:** 26 features per student
- **Algorithm:** XGBoost (gradient boosted trees)
- **Training data:** 1,470 segments (70% of 2,100)
- **Test data:** 630 segments (30% of 2,100)
- **Baseline comparison:** Logistic Regression (interpretable)
- **Performance target:** Correlation r ≥ 0.40 with teacher ratings
- **Feature importance:** Documented per skill for explainability

### Inference Pipeline
```
New Student Data (Transcript + Game + Teacher)
    ↓
Feature Extraction (26 features via spaCy + VADER + game analysis)
    ↓
Multi-Source Fusion (skill-specific weights: transcript 40%, game 35%, teacher 25%)
    ↓
XGBoost Models (7 parallel predictions)
    ↓
Evidence Extraction (top 2-3 supporting items per skill)
    ↓
GPT-4 Reasoning Generation (growth-oriented, 2-3 sentences)
    ↓
SkillAssessment Record:
  • Score: 0.87 (0-1 scale)
  • Confidence: 0.91
  • Reasoning: "Student demonstrates strong understanding of others' perspectives..."
  • Recommendations: "Continue practicing perspective-taking through role-play..."
  • Evidence: [Transcript #123, GameSession #456, TeacherRating #789]
```

---

## Current Status & Known Issues

### ✅ Completed
- Database schema with TimescaleDB (Task 7)
- Google Cloud STT integration (Task 9)
- Feature extraction services (Task 10)
- Evidence fusion service (Task 12)
- GPT-4 reasoning integration (Task 13)
- All 3 dashboards operational (Tasks 15, 27, 28)
- CI/CD pipeline with GitHub Actions (Task 29)
- SIS integration (OneRoster, Clever, ClassLink) (Task 30)

### ⚠️ Critical Issue: Incomplete Model Training
**File:** `backend/app/ml/train_models.py` (Lines 48-53)
- **Currently trains:** 4 skills only (Empathy, Problem Solving, Self-Regulation, Resilience)
- **Missing models:** Adaptability, Communication, Collaboration
- **Impact:** Inference service expects all 7 models to exist
- **Resolution needed:** Extend training script to include missing 3 skills before production deployment

### 📊 Sample Data
- **50 students** across grades 6-8 (seeded)
- **2,150+ assessments** with AI-generated reasoning
- **1,966 transcripts** with realistic classroom dialogue
- **Evidence items** linked to assessments (2-3 per skill)

---

**System Access:** http://localhost:8080/docs (API) • http://localhost:8501 (Teacher) • http://localhost:8502 (Admin) • http://localhost:8503 (Student)
