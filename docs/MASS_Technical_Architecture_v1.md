# MASS Technical Architecture Document
## Version 1.0 - Engineering Implementation Guide

**Project:** Middle School Non-Academic Skills Measurement System
**Date:** January 2025
**Status:** Implementation Ready
**Target Audience:** Engineering Team

---

## Table of Contents

1. System Overview
2. Technology Stack
3. Architecture Diagrams
4. Component Specifications
5. Data Models
6. API Specifications
7. Infrastructure & Deployment
8. Security & Compliance
9. Performance & Scalability
10. Monitoring & Observability

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        MASS Architecture                        │
└────────────────────────────────────────────────────────────────┘

External Systems:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Unity Game     │    │ Audio Recorder  │    │  SIS/LMS       │
│  (Student)      │    │  (Classroom)    │    │  (Roster Sync) │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   API Gateway       │
                    │   (Cloud Run)       │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐           ┌────▼────┐          ┌────▼────┐
    │Telemetry│           │   STT   │          │ Project │
    │ Ingest  │           │Pipeline │          │  Text   │
    └────┬────┘           └────┬────┘          └────┬────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Event Processing   │
                    │  (Cloud Pub/Sub +   │
                    │   Cloud Tasks)      │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐           ┌────▼────┐          ┌────▼────┐
    │Behavioral│          │Linguistic│         │  ML     │
    │Features  │          │Features  │         │Inference│
    └────┬────┘           └────┬────┘          └────┬────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Evidence Fusion    │
                    │  + GPT-4 Reasoning  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PostgreSQL +      │
                    │   TimescaleDB       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  React Dashboard    │
                    │  (Teacher View)     │
                    └─────────────────────┘
```

### 1.2 Data Flow

```
Student Activity → Data Ingestion → Processing → Storage → Presentation

1. Student plays game:
   Unity → Telemetry API → Pub/Sub → Behavioral Features → DB

2. Classroom audio:
   Audio File → Cloud Storage → Google STT → Transcript →
   Linguistic Features → DB

3. Skill inference (nightly batch):
   DB Features → ML Models → Skill Scores → Evidence Extraction →
   GPT-4 Reasoning → DB Assessments

4. Teacher views:
   Dashboard → API → DB Query → JSON Response → React Render
```

---

## 2. Technology Stack

### 2.1 Core Technologies

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Cloud Platform** | Google Cloud Platform | Current | AI/ML support, managed services |
| **Container Orchestration** | Cloud Run | Current | Serverless, auto-scaling |
| **Primary Database** | PostgreSQL | 15+ | Mature, reliable, JSONB support |
| **Time-Series DB** | TimescaleDB | 2.x | PostgreSQL extension for temporal data |
| **Cache** | Redis | 7.x | Fast in-memory for sessions/cache |
| **API Framework** | FastAPI | 0.109+ | Modern Python, async, auto-docs |
| **Game Engine** | Unity | 2022.3 LTS | Industry standard, stable LTS |
| **Frontend Framework** | React | 18.x | Component-based, large ecosystem |
| **Language (Backend)** | Python | 3.11+ | ML/data science ecosystem |
| **Language (Game)** | C# | 11+ | Unity native |
| **Language (Frontend)** | TypeScript | 5.x | Type safety for React |

### 2.2 ML/AI Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Speech-to-Text** | Google Cloud STT | Classroom audio → transcripts |
| **NLP Framework** | spaCy | Linguistic analysis, POS tagging |
| **Sentiment Analysis** | VADER | Emotion/tone detection |
| **Text Analysis** | LIWC-22 | Psychological language categories |
| **ML Framework** | Scikit-learn | Model training, preprocessing |
| **Gradient Boosting** | XGBoost | Primary skill inference models |
| **LLM Reasoning** | OpenAI GPT-4 | Human-readable explanations |
| **Embeddings** | sentence-transformers | Semantic text representations |

### 2.3 Development & Operations

| Purpose | Technology |
|---------|-----------|
| **Version Control** | Git + GitHub |
| **CI/CD** | GitHub Actions |
| **Infrastructure-as-Code** | Terraform |
| **Container Registry** | Google Artifact Registry |
| **Monitoring** | Google Cloud Monitoring |
| **Logging** | Google Cloud Logging |
| **Error Tracking** | Sentry |
| **API Documentation** | Swagger/OpenAPI 3.0 |
| **Testing (Backend)** | Pytest |
| **Testing (Frontend)** | Jest + React Testing Library |
| **Testing (Game)** | Unity Test Framework |

---

## 3. Architecture Diagrams

### 3.1 Cloud Infrastructure (GCP)

```
┌─────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                    │
│                    Project: mass-production                  │
└─────────────────────────────────────────────────────────────┘

Region: us-central1 (Iowa - cost-effective)

┌──────────────────┐
│   Cloud Run      │
│  ┌────────────┐  │
│  │ mass-api   │  │  ← Main API (FastAPI)
│  │ (0-10 inst)│  │
│  └────────────┘  │
└────────┬─────────┘
         │
┌────────▼──────────┐
│   Cloud SQL       │
│  ┌────────────┐   │
│  │ PostgreSQL │   │  ← Primary DB + TimescaleDB
│  │  (HA mode) │   │
│  └────────────┘   │
└───────────────────┘

┌──────────────────┐
│  Cloud Storage   │
│  ┌────────────┐  │
│  │ Audio Files│  │  ← Classroom recordings
│  │  (30-day)  │  │     Delete after transcription
│  └────────────┘  │
└──────────────────┘

┌──────────────────┐
│  Cloud Tasks     │
│  ┌────────────┐  │
│  │ STT Queue  │  │  ← Async transcription jobs
│  │ ML Queue   │  │  ← Skill inference jobs
│  └────────────┘  │
└──────────────────┘

┌──────────────────┐
│  Cloud Pub/Sub   │
│  ┌────────────┐  │
│  │ Events     │  │  ← Real-time event streaming
│  │ Topics     │  │     (telemetry, transcripts)
│  └────────────┘  │
└──────────────────┘

┌──────────────────┐
│  Cloud Logging + │
│  Monitoring      │  ← Observability
└──────────────────┘

┌──────────────────┐
│  Secret Manager  │  ← API keys, DB passwords
└──────────────────┘

┌──────────────────┐
│  Cloud IAM       │  ← Access control
└──────────────────┘
```

### 3.2 Backend Services Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
└────────────────────────────────────────────────────────────┘

src/
├── api/
│   ├── v1/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── audio.py             # Audio upload endpoints
│   │   ├── telemetry.py         # Game telemetry ingestion
│   │   ├── skills.py            # Skill assessment endpoints
│   │   ├── evidence.py          # Evidence retrieval
│   │   └── dashboard.py         # Dashboard data endpoints
│   └── dependencies.py          # Shared dependencies
│
├── core/
│   ├── config.py                # Environment config
│   ├── security.py              # Auth, encryption
│   └── database.py              # DB connections
│
├── services/
│   ├── stt_service.py           # Google Cloud STT integration
│   ├── feature_extraction.py   # Linguistic + behavioral features
│   ├── ml_inference.py          # Skill prediction
│   ├── evidence_fusion.py      # Multi-source fusion
│   ├── reasoning_service.py    # GPT-4 integration
│   └── telemetry_processor.py  # Game event processing
│
├── models/
│   ├── database/
│   │   ├── student.py          # SQLAlchemy models
│   │   ├── transcript.py
│   │   ├── skill.py
│   │   └── evidence.py
│   └── ml/
│       ├── empathy_model.pkl   # Trained XGBoost models
│       ├── adaptability_model.pkl
│       └── ... (7 total)
│
├── schemas/
│   ├── student.py              # Pydantic schemas (validation)
│   ├── skill.py
│   └── telemetry.py
│
├── workers/
│   ├── transcription_worker.py # Async STT processing
│   ├── inference_worker.py     # Async skill inference
│   └── fusion_worker.py        # Evidence fusion
│
└── main.py                     # Application entry point
```

---

## 4. Component Specifications

### 4.1 API Server (FastAPI)

**File:** `src/main.py`

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import auth, audio, telemetry, skills, dashboard
from core.config import settings

app = FastAPI(
    title="MASS API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

**Deployment:** Cloud Run
- Min instances: 0 (cost savings)
- Max instances: 10 (Phase 1)
- Memory: 2GB
- CPU: 2 vCPU
- Timeout: 300s (for long-running requests)

---

### 4.2 Speech-to-Text Pipeline

**File:** `src/services/stt_service.py`

```python
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import asyncio

class STTService:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.storage_client = storage.Client()

    async def transcribe_audio(self, audio_gcs_uri: str) -> dict:
        """
        Transcribe classroom audio using Google Cloud STT.

        Args:
            audio_gcs_uri: GCS path (gs://bucket/file.mp3)

        Returns:
            {
                'transcript': str,
                'confidence': float,
                'diarization': [...],  # Speaker labels
                'duration_sec': float
            }
        """
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True,
            enable_speaker_diarization=True,
            diarization_speaker_count=10,  # Classroom setting
            model="latest_long",
            use_enhanced=True
        )

        audio = speech.RecognitionAudio(uri=audio_gcs_uri)

        # Async long-running operation
        operation = self.client.long_running_recognize(
            config=config,
            audio=audio
        )

        # Wait for completion (can take minutes for long audio)
        response = operation.result(timeout=3600)

        # Process results
        transcript_parts = []
        diarization_data = []
        total_confidence = 0

        for result in response.results:
            alternative = result.alternatives[0]
            transcript_parts.append(alternative.transcript)
            total_confidence += alternative.confidence

            # Extract speaker labels
            for word in alternative.words:
                diarization_data.append({
                    'word': word.word,
                    'start_time': word.start_time.total_seconds(),
                    'end_time': word.end_time.total_seconds(),
                    'speaker': word.speaker_tag
                })

        return {
            'transcript': ' '.join(transcript_parts),
            'confidence': total_confidence / len(response.results),
            'diarization': diarization_data,
            'word_count': len(diarization_data)
        }
```

**Cost:** ~$0.024/minute ($34.55/student/month for 24 hours)

---

### 4.3 Feature Extraction Service

**File:** `src/services/feature_extraction.py`

```python
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

class LinguisticFeatureExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Skill-specific patterns
        self.patterns = {
            'empathy': {
                'perspective_taking': [
                    r'\b(understand|imagine|feel like|seems like)\b',
                    r'\b(I see|I get it|makes sense)\b'
                ],
                'emotion_words': [
                    r'\b(frustrated|happy|sad|angry|worried)\b'
                ]
            },
            'adaptability': {
                'flexibility': [
                    r'\b(different way|another approach|instead|alternatively)\b',
                    r'\b(change plan|try something else)\b'
                ]
            },
            # ... more patterns for other skills
        }

    def extract(self, text: str) -> dict:
        """Extract linguistic features from text."""
        doc = self.nlp(text)

        # Basic features
        features = {
            'word_count': len([t for t in doc if not t.is_punct]),
            'sentence_count': len(list(doc.sents)),
            'avg_sentence_length': self._avg_sentence_length(doc),
            'lexical_diversity': self._lexical_diversity(doc),
        }

        # Sentiment
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        features.update({
            'sentiment_positive': sentiment['pos'],
            'sentiment_negative': sentiment['neg'],
            'sentiment_neutral': sentiment['neu'],
            'sentiment_compound': sentiment['compound']
        })

        # Skill-specific patterns
        for skill, patterns in self.patterns.items():
            for pattern_name, pattern_list in patterns.items():
                count = sum(
                    len(re.findall(pattern, text, re.IGNORECASE))
                    for pattern in pattern_list
                )
                features[f'{skill}_{pattern_name}'] = count

        # Pronoun analysis (empathy/collaboration indicator)
        pronouns = [t.text.lower() for t in doc if t.pos_ == 'PRON']
        features['first_person_plural'] = pronouns.count('we') + pronouns.count('us')
        features['second_person'] = pronouns.count('you') + pronouns.count('your')

        return features
```

---

### 4.4 ML Inference Service

**File:** `src/services/ml_inference.py`

```python
import joblib
import numpy as np
from typing import Dict, List

class SkillInferenceService:
    def __init__(self, model_dir: str = "src/models/ml"):
        """Load all 7 trained skill models."""
        self.models = {}
        self.scalers = {}

        skills = ['empathy', 'adaptability', 'problem_solving',
                  'self_regulation', 'resilience', 'communication', 'collaboration']

        for skill in skills:
            self.models[skill] = joblib.load(f"{model_dir}/{skill}_model.pkl")
            self.scalers[skill] = joblib.load(f"{model_dir}/{skill}_scaler.pkl")

    def infer_skill(self, skill: str, features: dict) -> dict:
        """
        Infer skill score from features.

        Returns:
            {
                'score': float (0-1),
                'confidence': float (0-1),
                'feature_importance': dict
            }
        """
        # Convert features dict to numpy array (in correct order)
        feature_vector = self._dict_to_vector(features, skill)

        # Scale features
        scaled_features = self.scalers[skill].transform([feature_vector])

        # Predict
        model = self.models[skill]

        # Get probability (for XGBoost)
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(scaled_features)[0]
            score = proba[1]  # Probability of "high skill" class
        else:
            score = model.predict(scaled_features)[0]

        # Calculate confidence based on prediction certainty
        if hasattr(model, 'predict_proba'):
            confidence = abs(proba[1] - proba[0])  # Margin from 0.5
            confidence = min(confidence * 2, 1.0)   # Normalize to 0-1
        else:
            confidence = 0.7  # Default for regression models

        # Feature importance (for XGBoost)
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            feature_names = self._get_feature_names(skill)
            importances = model.feature_importances_
            feature_importance = dict(zip(feature_names, importances))

        return {
            'score': float(np.clip(score, 0, 1)),
            'confidence': float(confidence),
            'feature_importance': feature_importance
        }
```

---

### 4.5 Evidence Fusion Service

**File:** `src/services/evidence_fusion.py`

```python
from typing import List, Dict
import numpy as np

class EvidenceFusionService:
    # Learned weights from Phase 0 validation
    SKILL_WEIGHTS = {
        'empathy': {'transcript': 0.35, 'game': 0.40, 'teacher': 0.25},
        'adaptability': {'transcript': 0.20, 'game': 0.50, 'teacher': 0.30},
        'problem_solving': {'transcript': 0.30, 'game': 0.45, 'teacher': 0.25},
        'self_regulation': {'transcript': 0.25, 'game': 0.40, 'teacher': 0.35},
        'resilience': {'transcript': 0.25, 'game': 0.50, 'teacher': 0.25},
        'communication': {'transcript': 0.50, 'game': 0.25, 'teacher': 0.25},
        'collaboration': {'transcript': 0.40, 'game': 0.35, 'teacher': 0.25},
    }

    def fuse_scores(self, skill: str, sources: Dict[str, float]) -> Dict:
        """
        Fuse scores from multiple sources.

        Args:
            skill: Skill name
            sources: {'transcript': 0.75, 'game': 0.80, 'teacher': 0.70}

        Returns:
            {'score': 0.76, 'confidence': 0.85, 'sources': {...}}
        """
        weights = self.SKILL_WEIGHTS[skill]

        # Calculate weighted average
        fused_score = sum(
            sources.get(source, 0) * weight
            for source, weight in weights.items()
            if source in sources
        )

        # Normalize if missing sources
        total_weight = sum(
            weight for source, weight in weights.items()
            if source in sources
        )
        if total_weight > 0:
            fused_score /= total_weight

        # Calculate confidence (based on agreement between sources)
        available_scores = [s for s in sources.values() if s is not None]
        if len(available_scores) >= 2:
            std_dev = np.std(available_scores)
            # Low std = high agreement = high confidence
            confidence = max(0, 1.0 - (std_dev * 2))
        else:
            # Only one source, lower confidence
            confidence = 0.6

        return {
            'score': float(np.clip(fused_score, 0, 1)),
            'confidence': float(np.clip(confidence, 0, 1)),
            'sources': sources,
            'weights_used': weights
        }
```

---

### 4.6 GPT-4 Reasoning Service

**File:** `src/services/reasoning_service.py`

```python
import openai
from typing import List, Dict

class ReasoningService:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    async def generate_reasoning(
        self,
        student_name: str,
        skill: str,
        score: float,
        evidence: List[Dict],
        features: Dict
    ) -> str:
        """
        Generate growth-oriented reasoning using GPT-4.

        Args:
            student_name: Student's first name
            skill: Skill being assessed
            score: Fused score (0-1)
            evidence: List of evidence items
            features: Feature dict with counts/metrics

        Returns:
            2-3 sentence reasoning text
        """
        # Build evidence summary
        evidence_text = "\n".join([
            f"- {e['evidence_text']} (Source: {e['source_type']})"
            for e in evidence[:3]  # Top 3 pieces
        ])

        # Score interpretation
        score_level = "strong" if score >= 0.75 else \
                     "developing" if score >= 0.50 else \
                     "emerging"

        prompt = f"""You are an educational assessment expert providing feedback to middle school
teachers about student non-academic skills.

Student: {student_name}
Skill: {skill}
Score: {score:.2f}/1.00 ({score_level})

Evidence from observations:
{evidence_text}

Key metrics:
{self._format_features(features, skill)}

Provide 2-3 sentences explaining why this student received this score for {skill}.
Use growth-oriented, asset-based language. Focus on observable behaviors, not judgments.
Be specific and actionable. Mention opportunities for growth if score < 0.75.

Format: Direct explanation without preamble."""

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower = more consistent
            max_tokens=150
        )

        reasoning = response.choices[0].message.content.strip()
        return reasoning

    def _format_features(self, features: Dict, skill: str) -> str:
        """Format relevant features for prompt."""
        relevant = {
            k: v for k, v in features.items()
            if skill in k or k in ['word_count', 'sentiment_positive']
        }
        return "\n".join([f"- {k}: {v}" for k, v in relevant.items()])
```

**Cost:** ~$0.03-0.05 per reasoning generation

---

## 5. Data Models

### 5.1 Complete Database Schema

**File:** `src/models/database/schema.sql`

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================
-- CORE ENTITIES
-- ============================================

CREATE TABLE districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    state VARCHAR(2),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district_id UUID REFERENCES districts(id),
    name VARCHAR(200) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE classrooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id),
    teacher_id UUID REFERENCES teachers(id),
    name VARCHAR(200),
    grade_level INTEGER CHECK (grade_level BETWEEN 6 AND 8),
    academic_year VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id),
    external_id VARCHAR(100),  -- School's student ID
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    grade_level INTEGER CHECK (grade_level BETWEEN 6 AND 8),
    demographics JSONB,
    enrolled_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(school_id, external_id)
);

CREATE TABLE classroom_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    classroom_id UUID REFERENCES classrooms(id),
    student_id UUID REFERENCES students(id),
    enrolled_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(classroom_id, student_id)
);

-- ============================================
-- AUDIO & TRANSCRIPTION
-- ============================================

CREATE TABLE audio_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    classroom_id UUID REFERENCES classrooms(id),
    recording_date DATE NOT NULL,
    duration_seconds INTEGER,
    file_path VARCHAR(500),  -- GCS path
    file_size_bytes BIGINT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded',  -- uploaded, processing, completed, failed
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_audio_files_classroom ON audio_files(classroom_id);
CREATE INDEX idx_audio_files_status ON audio_files(status);

CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_file_id UUID REFERENCES audio_files(id),
    full_text TEXT,
    confidence_score FLOAT,  -- Average STT confidence
    word_count INTEGER,
    diarization_data JSONB,  -- Speaker labels
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transcript_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transcript_id UUID REFERENCES transcripts(id),
    student_id UUID REFERENCES students(id),  -- Inferred speaker
    start_time FLOAT,  -- Seconds from audio start
    end_time FLOAT,
    text TEXT,
    confidence FLOAT,  -- STT confidence for this segment
    speaker_tag INTEGER,  -- Raw speaker number from diarization
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transcript_segments_student ON transcript_segments(student_id);

-- ============================================
-- GAME TELEMETRY
-- ============================================

CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    mission_progress JSONB DEFAULT '{}',  -- Which missions completed
    total_playtime_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_game_sessions_student ON game_sessions(student_id);

CREATE TABLE game_telemetry_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES game_sessions(id),
    event_type VARCHAR(100) NOT NULL,  -- choice_made, mission_started, etc.
    event_data JSONB NOT NULL,  -- Event-specific data
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_game_events_session ON game_telemetry_events(session_id);
CREATE INDEX idx_game_events_type ON game_telemetry_events(event_type);

-- Convert to TimescaleDB hypertable for efficient queries
SELECT create_hypertable('game_telemetry_events', 'timestamp');

-- ============================================
-- PROJECT SUBMISSIONS
-- ============================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    classroom_id UUID REFERENCES classrooms(id),
    title VARCHAR(200),
    description TEXT,
    assigned_date DATE,
    due_date DATE,
    project_type VARCHAR(50),  -- essay, reflection, group_work
    rubric_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE project_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    project_id UUID REFERENCES projects(id),
    submission_text TEXT,  -- Extracted text content
    submission_type VARCHAR(50),
    word_count INTEGER,
    submitted_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- FEATURE EXTRACTION
-- ============================================

CREATE TABLE linguistic_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    source_type VARCHAR(50),  -- transcript_segment, project_submission
    source_id UUID,  -- References source
    extracted_at TIMESTAMP DEFAULT NOW(),

    -- Empathy features
    empathy_perspective_taking INTEGER DEFAULT 0,
    empathy_emotion_words INTEGER DEFAULT 0,
    empathy_social_words INTEGER DEFAULT 0,

    -- Adaptability features
    adaptability_flexibility INTEGER DEFAULT 0,
    adaptability_change_response INTEGER DEFAULT 0,

    -- Problem-solving features
    problem_solving_causal INTEGER DEFAULT 0,
    problem_solving_planning INTEGER DEFAULT 0,

    -- Communication features
    communication_clarity FLOAT,
    communication_complexity FLOAT,

    -- Collaboration features
    collaboration_inclusive INTEGER DEFAULT 0,
    collaboration_help_seeking INTEGER DEFAULT 0,

    -- Baseline linguistic
    word_count INTEGER,
    sentence_count INTEGER,
    lexical_diversity FLOAT,
    sentiment_positive FLOAT,
    sentiment_negative FLOAT,

    -- Store all features as JSONB for flexibility
    all_features JSONB
);

CREATE INDEX idx_linguistic_features_student ON linguistic_features(student_id);

CREATE TABLE behavioral_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    session_id UUID REFERENCES game_sessions(id),
    extracted_at TIMESTAMP DEFAULT NOW(),

    -- Problem-solving
    task_completion_rate FLOAT,
    task_sequencing_efficiency FLOAT,

    -- Adaptability
    strategy_switching_count INTEGER,
    flexibility_score FLOAT,

    -- Resilience
    retry_count INTEGER,
    recovery_time_avg FLOAT,
    persistence_score FLOAT,

    -- Collaboration
    delegation_fairness FLOAT,
    turn_taking_score FLOAT,

    -- Self-regulation
    distraction_resistance FLOAT,
    time_on_task FLOAT,

    -- Store all features
    all_features JSONB
);

CREATE INDEX idx_behavioral_features_student ON behavioral_features(student_id);

-- ============================================
-- SKILL ASSESSMENTS (PRIMARY OUTPUT)
-- ============================================

CREATE TABLE skill_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    skill VARCHAR(50) NOT NULL,  -- empathy, adaptability, etc.
    score FLOAT CHECK (score BETWEEN 0 AND 1),  -- PRIMARY METRIC
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),

    assessment_period_start DATE,
    assessment_period_end DATE,

    -- Source scores (before fusion)
    transcript_score FLOAT,
    game_score FLOAT,
    teacher_score FLOAT,

    -- Fusion weights used
    fusion_weights JSONB,

    -- Model metadata
    model_version VARCHAR(50),
    feature_importance JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(student_id, skill, assessment_period_start, assessment_period_end)
);

CREATE INDEX idx_skill_assessments_student ON skill_assessments(student_id);
CREATE INDEX idx_skill_assessments_skill ON skill_assessments(skill);
CREATE INDEX idx_skill_assessments_period ON skill_assessments(assessment_period_start, assessment_period_end);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('skill_assessments', 'created_at');

-- ============================================
-- EVIDENCE & REASONING (EXPLAINABILITY)
-- ============================================

CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES skill_assessments(id),
    evidence_type VARCHAR(50),  -- linguistic, behavioral, contextual
    source_type VARCHAR(50),  -- transcript, game, project
    source_id UUID,

    evidence_text TEXT,  -- The actual evidence snippet
    context_before TEXT,
    context_after TEXT,
    timestamp_in_source FLOAT,

    relevance_score FLOAT,  -- How relevant to the skill (0-1)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evidence_assessment ON evidence_items(assessment_id);

CREATE TABLE reasoning_explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES skill_assessments(id) UNIQUE,

    reasoning_text TEXT NOT NULL,  -- GPT-4 generated explanation
    reasoning_type VARCHAR(50) DEFAULT 'llm_generated',

    generated_by VARCHAR(50),  -- gpt4, template_v1, etc.
    generation_cost FLOAT,  -- Track API costs
    generated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TEACHER RUBRICS
-- ============================================

CREATE TABLE teacher_rubric_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    teacher_id UUID REFERENCES teachers(id),
    skill VARCHAR(50),
    score INTEGER CHECK (score BETWEEN 1 AND 4),  -- 1=Low, 4=Advanced
    qualitative_feedback TEXT,
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rubric_assessments_student ON teacher_rubric_assessments(student_id);

-- ============================================
-- PROCESSING JOBS (FOR MONITORING)
-- ============================================

CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL,  -- transcription, feature_extraction, inference
    status VARCHAR(50) DEFAULT 'queued',  -- queued, running, completed, failed
    payload JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX idx_processing_jobs_type ON processing_jobs(job_type);

-- ============================================
-- AUDIT LOGS
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,  -- Could be teacher_id or system
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

---

## 6. API Specifications

### 6.1 Authentication

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "teacher@school.edu",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "teacher@school.edu",
    "first_name": "Jane",
    "role": "teacher",
    "school_id": "uuid"
  }
}
```

---

### 6.2 Audio Upload

**Endpoint:** `POST /api/v1/audio/upload`

**Request:** Multipart form-data
```
classroom_id: uuid
recording_date: 2024-01-15
audio_file: [binary]
```

**Response:**
```json
{
  "audio_file_id": "uuid",
  "status": "queued_for_transcription",
  "estimated_completion": "2024-01-15T15:30:00Z",
  "job_id": "uuid"
}
```

---

### 6.3 Game Telemetry

**Endpoint:** `POST /api/v1/telemetry/events`

**Request:**
```json
{
  "session_id": "uuid",
  "events": [
    {
      "event_type": "choice_made",
      "timestamp": "2024-01-15T14:23:45Z",
      "event_data": {
        "mission_id": "M01",
        "choice_id": "C05_empathy_high",
        "time_taken_sec": 12.4
      }
    },
    {
      "event_type": "mission_completed",
      "timestamp": "2024-01-15T14:35:20Z",
      "event_data": {
        "mission_id": "M01",
        "completion_time_sec": 720,
        "choices_made": 5
      }
    }
  ]
}
```

**Response:**
```json
{
  "received": 2,
  "session_id": "uuid",
  "status": "processed"
}
```

---

### 6.4 Get Skill Assessments

**Endpoint:** `GET /api/v1/skills/{student_id}`

**Query Params:**
- `skill` (optional): Filter by specific skill
- `period_start` (optional): Date (YYYY-MM-DD)
- `period_end` (optional): Date

**Response:**
```json
{
  "student_id": "uuid",
  "student_name": "Marcus Chen",
  "assessment_period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "skills": [
    {
      "skill": "empathy",
      "score": 0.78,
      "confidence": 0.85,
      "score_level": "proficient",
      "sources": {
        "transcript": 0.75,
        "game": 0.82,
        "teacher": 0.75
      },
      "evidence": [
        {
          "id": "uuid",
          "type": "linguistic",
          "source": "transcript",
          "text": "I think I understand how you feel about this. That must be really frustrating.",
          "timestamp": "2024-01-15T10:30:00Z",
          "relevance": 0.92
        },
        {
          "id": "uuid",
          "type": "behavioral",
          "source": "game",
          "text": "Chose 'Listen to Morgan's perspective' in empathy mission",
          "relevance": 0.88
        },
        {
          "id": "uuid",
          "type": "contextual",
          "source": "teacher_rubric",
          "text": "Shows good understanding of others' perspectives in group work",
          "relevance": 0.80
        }
      ],
      "reasoning": "Marcus demonstrates strong empathy through consistent use of perspective-taking language and empathetic choices in game scenarios. His teacher also rates him highly for understanding others' perspectives. Confidence is high due to consistent evidence across multiple sources.",
      "assessed_at": "2024-01-31T23:59:59Z"
    }
    // ... 6 more skills
  ]
}
```

---

## 7. Infrastructure & Deployment

### 7.1 GCP Setup Commands

**File:** `infrastructure/setup-gcp.sh`

```bash
#!/bin/bash
set -e

PROJECT_ID="mass-production"
REGION="us-central1"
DB_INSTANCE="mass-db"

echo "=== Setting up MASS infrastructure on GCP ==="

# 1. Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# 2. Enable billing (manual step required)
echo "⚠️  Enable billing in GCP Console: https://console.cloud.google.com/billing"
read -p "Press enter when billing is enabled..."

# 3. Enable required APIs
echo "Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  cloudtasks.googleapis.com \
  pubsub.googleapis.com \
  speech.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# 4. Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $DB_INSTANCE \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=$REGION \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04

# 5. Create database
gcloud sql databases create mass_db \
  --instance=$DB_INSTANCE

# 6. Create Cloud Storage buckets
echo "Creating storage buckets..."
gsutil mb -l $REGION gs://$PROJECT_ID-audio-files/
gsutil mb -l $REGION gs://$PROJECT_ID-ml-models/

# Set lifecycle (delete audio after 30 days)
echo '{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }]
  }
}' > /tmp/lifecycle.json
gsutil lifecycle set /tmp/lifecycle.json gs://$PROJECT_ID-audio-files/

# 7. Create Pub/Sub topics
echo "Creating Pub/Sub topics..."
gcloud pubsub topics create audio-uploaded
gcloud pubsub topics create transcription-completed
gcloud pubsub topics create features-extracted
gcloud pubsub topics create skills-inferred

# 8. Create Cloud Tasks queues
echo "Creating task queues..."
gcloud tasks queues create transcription-jobs \
  --max-concurrent-dispatches=10 \
  --location=$REGION

gcloud tasks queues create inference-jobs \
  --max-concurrent-dispatches=20 \
  --location=$REGION

# 9. Create service account
echo "Creating service account..."
gcloud iam service-accounts create mass-api \
  --display-name="MASS API Service Account"

# Grant permissions
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mass-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mass-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# 10. Store secrets
echo "Storing secrets..."
echo -n "POSTGRES_PASSWORD_HERE" | \
  gcloud secrets create db-password \
    --data-file=- \
    --replication-policy="automatic"

echo -n "OPENAI_API_KEY_HERE" | \
  gcloud secrets create openai-api-key \
    --data-file=- \
    --replication-policy="automatic"

echo "✅ GCP infrastructure setup complete!"
echo "Next steps:"
echo "1. Set database password"
echo "2. Deploy API to Cloud Run"
echo "3. Deploy frontend to Cloud Run or Firebase Hosting"
```

---

### 7.2 Docker Configuration

**File:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**File:** `requirements.txt`

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
google-cloud-speech==2.23.0
google-cloud-storage==2.14.0
google-cloud-tasks==2.15.0
google-cloud-pubsub==2.19.0
openai==1.10.0
spacy==3.7.2
vaderSentiment==3.3.2
scikit-learn==1.4.0
xgboost==2.0.3
pandas==2.2.0
numpy==1.26.3
joblib==1.3.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

---

### 7.3 Cloud Run Deployment

**File:** `infrastructure/deploy-api.sh`

```bash
#!/bin/bash
set -e

PROJECT_ID="mass-production"
REGION="us-central1"
SERVICE_NAME="mass-api"

echo "=== Deploying MASS API to Cloud Run ==="

# 1. Build container
echo "Building container..."
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --project=$PROJECT_ID

# 2. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --service-account mass-api@$PROJECT_ID.iam.gserviceaccount.com \
  --min-instances 0 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars PROJECT_ID=$PROJECT_ID \
  --set-env-vars REGION=$REGION \
  --set-secrets DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest

echo "✅ Deployment complete!"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
```

---

## 8. Security & Compliance

### 8.1 Authentication & Authorization

**OAuth 2.0 + JWT Implementation:**

```python
# src/core/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your-secret-key-here"  # From Secret Manager
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### 8.2 Data Encryption

**At Rest:**
- Cloud SQL: AES-256 encryption (automatic)
- Cloud Storage: Google-managed encryption keys
- Secrets: Secret Manager with automatic rotation

**In Transit:**
- TLS 1.3 for all API communication
- HTTPS only (no HTTP)
- Certificate management via Cloud Run (automatic)

### 8.3 Compliance

**FERPA (Family Educational Rights and Privacy Act):**
- Data access controls (teachers see only their students)
- Audit logging of all data access
- Data retention policy (delete after student graduation + 1 year)
- Parental consent for audio recording

**COPPA (Children's Online Privacy Protection Act):**
- Parental consent required
- No advertising or marketing to students
- Data minimization (collect only what's needed)
- Right to delete student data

---

## 9. Performance & Scalability

### 9.1 Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Latency (p95) | <500ms | TBD | Phase 1 |
| Dashboard Load Time | <2s | TBD | Phase 1 |
| STT Processing | <5s per min audio | TBD | Phase 1 |
| Skill Inference | <30s per student | TBD | Phase 1 |
| System Uptime | 95%+ | TBD | Phase 1 |

### 9.2 Scalability Architecture

**Horizontal Scaling:**
- Cloud Run: Auto-scales 0-10 instances (Phase 1), 0-100 (Phase 2+)
- Database: Read replicas for query scaling
- Redis: Cluster mode for high availability

**Caching Strategy:**
```python
# Cache student skill assessments (updated daily)
@cache(ttl=86400)  # 24 hours
async def get_student_skills(student_id: str):
    pass

# Cache teacher dashboard data (updated hourly)
@cache(ttl=3600)  # 1 hour
async def get_class_overview(class_id: str):
    pass
```

---

## 10. Monitoring & Observability

### 10.1 Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Error rate (errors/total requests)
- Latency (p50, p95, p99)
- Active users (concurrent sessions)

**Business Metrics:**
- Assessments generated per day
- Student game completion rate
- Teacher dashboard usage
- STT accuracy (confidence scores)

**Infrastructure Metrics:**
- Cloud Run instance count
- Database connections
- CPU/Memory utilization
- Cloud Tasks queue depth

### 10.2 Alerting

**Critical Alerts:**
- API error rate >5% (5 min window)
- Database connection failures
- STT service unavailable
- Disk space >80% full

**Warning Alerts:**
- API latency p95 >1s
- Queue depth >100 tasks
- Model inference errors

### 10.3 Logging Strategy

```python
import logging
from google.cloud import logging as cloud_logging

# Configure Cloud Logging
client = cloud_logging.Client()
client.setup_logging(log_level=logging.INFO)

logger = logging.getLogger(__name__)

# Structured logging
logger.info(
    "Skill inference completed",
    extra={
        "student_id": student_id,
        "skill": skill,
        "score": score,
        "confidence": confidence,
        "processing_time_ms": elapsed_ms
    }
)
```

---

## Appendix A: Development Setup

**Local Development:**

```bash
# 1. Clone repository
git clone https://github.com/your-org/mass-backend.git
cd mass-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing tools

# 4. Set up local database
docker-compose up -d postgres redis

# 5. Run migrations
alembic upgrade head

# 6. Set environment variables
cp .env.example .env
# Edit .env with your local config

# 7. Run development server
uvicorn src.main:app --reload --port 8000

# 8. Run tests
pytest tests/
```

---

## Appendix B: Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing (unit + integration)
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Secrets stored in Secret Manager
- [ ] API documentation updated
- [ ] Performance benchmarks run

**Deployment:**
- [ ] Build and push Docker image
- [ ] Deploy to Cloud Run (staging first)
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Monitor logs for errors
- [ ] Verify health check endpoint

**Post-Deployment:**
- [ ] Verify all services healthy
- [ ] Check monitoring dashboards
- [ ] Test critical user flows
- [ ] Announce deployment to team

---

*This Technical Architecture Document provides the complete engineering blueprint for implementing the MASS system. All specifications are implementation-ready.*
