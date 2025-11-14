# System Architecture Documentation

## Overview

The UnseenEdge AI Skill Assessment System is a production-ready, ML-powered platform for assessing student social-emotional skills. The system combines XGBoost machine learning models, multi-source evidence fusion, and GPT-4-powered reasoning generation to provide accurate, growth-oriented skill assessments.

**Assessed Skills:**
- Empathy
- Problem-Solving
- Self-Regulation
- Resilience

**Key Characteristics:**
- Sub-200ms inference latency per student
- Batch processing (10-20 students/second)
- Multi-source evidence fusion
- Production-hardened with rate limiting and monitoring
- Horizontally scalable architecture

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│                    (Web, Mobile, Admin Tools)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Layer (FastAPI)                           │ │
│  │  - Authentication (JWT)                                    │ │
│  │  - Inference Endpoints (/infer, /infer/batch)             │ │
│  │  - Configuration Endpoints (/fusion/weights)              │ │
│  │  - Metrics & Health Checks                                │ │
│  └───────────────────┬────────────────────────────────────────┘ │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────────┐ │
│  │              Service Layer                                 │ │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌───────────┐ │ │
│  │  │ ML Inference    │  │ Evidence Fusion  │  │ Reasoning │ │ │
│  │  │ Service         │  │ Service          │  │ Generator │ │ │
│  │  │                 │  │                  │  │ (GPT-4)   │ │ │
│  │  │ - XGBoost       │  │ - Multi-source   │  │           │ │ │
│  │  │ - Feature       │  │   combination    │  │ - Growth  │ │ │
│  │  │   extraction    │  │ - Weight config  │  │   oriented│ │ │
│  │  │ - Confidence    │  │ - Normalization  │  │ - Token   │ │ │
│  │  │   calculation   │  │                  │  │   limits  │ │ │
│  │  └─────────────────┘  └──────────────────┘  └───────────┘ │ │
│  └───────────────────┬────────────────────────────────────────┘ │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────────┐ │
│  │              Core Infrastructure                           │ │
│  │  - Metrics Store (Redis)                                   │ │
│  │  - Rate Limiter (Token Bucket)                            │ │
│  │  - Secret Manager (GCP/Env)                               │ │
│  │  - Fusion Config Manager                                  │ │
│  │  - Model Registry & Versioning                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────┐ ┌────────────┐
      │ PostgreSQL   │ │  Redis   │ │   OpenAI   │
      │              │ │          │ │  GPT-4 API │
      │ - Students   │ │ - Metrics│ │            │
      │ - Features   │ │ - Cache  │ │ - Reasoning│
      │ - Assessments│ │          │ │ - Rate     │
      │              │ │          │ │   limited  │
      └──────────────┘ └──────────┘ └────────────┘
              │
              ▼
      ┌──────────────┐
      │     GCS      │
      │ (ML Models)  │
      │              │
      │ - XGBoost    │
      │ - Versions   │
      └──────────────┘
```

---

## Service Components

### 1. ML Inference Service

**File:** `app/services/skill_inference.py` (476 lines)

**Responsibilities:**
- Load and manage trained XGBoost models (4 skills)
- Extract 26-dimensional feature vectors
- Run ML inference with confidence scoring
- Track model versions and integrity
- Optimize database queries (parallel execution)

**Key Features:**
- **Feature Extraction:** Combines 16 linguistic + 9 behavioral + 1 derived feature
- **Confidence Scoring:** 3-component method (tree variance, prediction extremity, feature completeness)
- **Model Caching:** In-memory singleton for fast inference
- **Parallel Queries:** Async database operations reduce latency by 3x
- **Version Tracking:** Model registry with checksums

**API:**
```python
class SkillInferenceService:
    async def infer_skill(
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType
    ) -> Tuple[float, float, Dict[str, float]]
    # Returns: (score, confidence, feature_importance)

    async def infer_all_skills(
        session: AsyncSession,
        student_id: str
    ) -> Dict[SkillType, Tuple[float, float, Dict[str, float]]]
```

**Performance:**
- Single skill inference: ~50ms
- All skills inference: ~150ms
- Batch optimized with parallel DB queries

---

### 2. Evidence Fusion Service

**File:** `app/services/evidence_fusion.py` (533 lines)

**Responsibilities:**
- Collect evidence from multiple sources
- Normalize evidence to 0-1 scale
- Apply skill-specific weights
- Fuse evidence into final assessment
- Manage fusion configuration

**Evidence Sources:**
1. **ML Inference** (50% weight) - Primary predictions
2. **Linguistic Features** (10-25% weight) - Language patterns
3. **Behavioral Features** (15-30% weight) - Task completion, focus
4. **Teacher Observations** (10% weight) - Optional
5. **Peer Feedback** (5% weight) - Optional

**Normalization Methods:**
- **ML Predictions:** Already normalized (0-1)
- **Linguistic Features:** Z-score + sigmoid transformation
- **Behavioral Features:** Min-max scaling with clipping

**Weight Configuration (Skill-Specific):**
```python
# Empathy: Language-heavy
{
    "ml_inference": 0.50,
    "linguistic_features": 0.25,  # Higher
    "behavioral_features": 0.15,
    "confidence_adjustment": 0.10
}

# Self-Regulation: Behavior-heavy
{
    "ml_inference": 0.50,
    "linguistic_features": 0.10,  # Lower
    "behavioral_features": 0.30,  # Higher
    "confidence_adjustment": 0.10
}
```

**API:**
```python
class EvidenceFusionService:
    async def fuse_skill_evidence(
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType
    ) -> Tuple[float, float, List[EvidenceItem]]
    # Returns: (fused_score, fused_confidence, evidence_items)

    async def fuse_all_skills(
        session: AsyncSession,
        student_id: str
    ) -> Dict[SkillType, Tuple[float, float, List[EvidenceItem]]]
```

**Performance:**
- Parallel evidence collection (3x speedup)
- Concurrent async operations
- Graceful degradation if sources fail

---

### 3. Reasoning Generator Service

**File:** `app/services/reasoning_generator.py` (484 lines)

**Responsibilities:**
- Generate growth-oriented feedback using GPT-4
- Monitor token limits and truncate evidence
- Rate limit API calls (50/min, 500/hour)
- Provide template fallbacks
- Validate API keys at startup

**Key Features:**
- **Token Management:** tiktoken-based counting, automatic evidence truncation
- **Rate Limiting:** Token bucket algorithm with per-minute and per-hour limits
- **Growth Orientation:** Focuses on strengths and actionable suggestions
- **Fallback Logic:** Template-based reasoning when GPT-4 unavailable
- **Secret Management:** GCP Secret Manager or environment variables

**Token Limits:**
```python
MODEL_TOKEN_LIMITS = {
    "gpt-4o-mini": 128000,    # Used by default
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
}

SAFE_TOKEN_LIMITS = {
    "gpt-4o-mini": 120000,    # 8k buffer for response
    "gpt-4o": 120000,
    "gpt-4-turbo": 120000,
    "gpt-4": 6000,            # 2k buffer for response
}
```

**API:**
```python
class ReasoningGeneratorService:
    @rate_limit("openai_reasoning")
    async def generate_reasoning(
        skill_type: SkillType,
        score: float,
        confidence: float,
        evidence: List[EvidenceItem],
        student_grade: Optional[int] = None
    ) -> SkillReasoning
    # Returns: reasoning, strengths, growth_suggestions
```

**Output Format:**
```json
{
  "reasoning": "2-3 sentence growth-oriented explanation",
  "strengths": ["strength 1", "strength 2"],
  "growth_suggestions": ["actionable suggestion 1", "suggestion 2"]
}
```

---

## API Layer

**File:** `app/api/endpoints/inference.py` (513 lines)

### Endpoints

#### 1. Single Student Inference
```
POST /api/v1/infer/{student_id}
```

**Flow:**
1. Authenticate user (JWT)
2. Run ML inference for all 4 skills
3. Record metrics to Redis
4. Return scores with confidence and feature importance

**Response:**
```json
{
  "student_id": "student_123",
  "skills": [
    {
      "skill_type": "empathy",
      "score": 0.75,
      "confidence": 0.85,
      "feature_importance": {...},
      "inference_time_ms": 45.2,
      "model_version": "1.0.0"
    },
    ...
  ],
  "total_inference_time_ms": 152.3,
  "timestamp": "2025-11-13T10:30:00Z",
  "model_versions": {...}
}
```

#### 2. Single Skill Inference
```
POST /api/v1/infer/{student_id}/{skill_type}
```

**Use Case:** Targeted assessment for specific skill
**Performance:** ~50ms per skill

#### 3. Batch Inference
```
POST /api/v1/infer/batch
```

**Request:**
```json
{
  "student_ids": ["student_1", "student_2", ..., "student_100"]
}
```

**Constraints:**
- Max 100 students per batch
- Parallel processing with asyncio.gather
- Individual error handling (failures don't block successes)

**Performance:**
- 10-20 students/second
- 100 students in ~8-10 seconds

**Response:**
```json
{
  "total_students": 100,
  "successful": 98,
  "failed": 2,
  "total_time_ms": 8452.1,
  "results": [
    {
      "student_id": "student_1",
      "status": "success",
      "skills": [...],
      "total_inference_time_ms": 145.2
    },
    {
      "student_id": "student_2",
      "status": "error",
      "error_message": "Student not found"
    },
    ...
  ]
}
```

#### 4. Metrics Endpoints
```
GET /api/v1/metrics              # Recent inference metrics
GET /api/v1/metrics/summary      # Aggregated statistics
```

**Metrics Tracked:**
- Inference latency (avg, p95, p99)
- Success/failure rates
- Error messages
- Per-skill performance

#### 5. Configuration Endpoints
```
GET /api/v1/fusion/weights                    # Get all weights
GET /api/v1/fusion/weights/{skill_type}       # Get skill weights
PUT /api/v1/fusion/weights/{skill_type}       # Update weights
POST /api/v1/fusion/weights/reload            # Reload from file
```

**Weight Update Example:**
```json
{
  "ml_inference": 0.55,
  "linguistic_features": 0.20,
  "behavioral_features": 0.15,
  "confidence_adjustment": 0.10
}
```

#### 6. Health Check
```
GET /api/v1/health
```

**Checks:**
- Database connectivity
- Redis connectivity
- Model loading status
- API key validity

---

## Core Infrastructure

### 1. Metrics Store

**File:** `app/core/metrics.py` (247 lines)

**Storage:** Redis (with in-memory fallback)

**Features:**
- Sorted set for time-series data
- Automatic cleanup (keeps last 10,000 metrics)
- Aggregated statistics (avg, p95, success rate)
- Graceful degradation to memory

**API:**
```python
class MetricsStore:
    def record_metric(
        student_id: str,
        inference_time_ms: float,
        skill_type: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    )

    def get_recent_metrics(limit: int = 100) -> List[InferenceMetrics]

    def get_metrics_summary() -> dict
    # Returns: total, successful, failed, avg_time, p95_time, success_rate
```

---

### 2. Rate Limiter

**File:** `app/core/rate_limiter.py` (207 lines)

**Algorithm:** Token Bucket

**Features:**
- Per-minute and per-hour limits
- Gradual token refill
- Burst allowance
- Async-safe with locking

**Configuration:**
```python
@dataclass
class RateLimitConfig:
    calls_per_minute: int = 60
    calls_per_hour: int = 1000
    burst_size: int = 10
```

**Usage:**
```python
# Decorator-based rate limiting
@rate_limit("openai_reasoning")
async def call_gpt4(...):
    ...

# Registered limits
registry.register("openai_reasoning", RateLimitConfig(
    calls_per_minute=50,
    calls_per_hour=500,
    burst_size=10
))
```

**Behavior:**
- Blocks when limit exceeded
- Raises RuntimeError with retry-after time
- Logs warnings for monitoring

---

### 3. Fusion Config Manager

**File:** `app/core/fusion_config.py` (278 lines)

**Storage:** JSON file with in-memory cache

**Features:**
- Skill-specific weight configuration
- Hot reload without restart
- Validation (weights must sum to 1.0)
- Version tracking

**Config Format:**
```json
{
  "version": "1.0.0",
  "description": "Production fusion weights",
  "weights": {
    "empathy": {
      "ml_inference": 0.50,
      "linguistic_features": 0.25,
      "behavioral_features": 0.15,
      "confidence_adjustment": 0.10
    },
    ...
  }
}
```

**API:**
```python
class FusionConfigManager:
    def get_config() -> FusionConfig
    def update_config(config: FusionConfig, save: bool = True)
    def reload()  # Reload from file
```

---

### 4. Secret Manager

**File:** `app/core/secrets.py` (221 lines)

**Sources:**
1. **GCP Secret Manager** (production)
2. **Environment variables** (development/fallback)

**Secrets Managed:**
- OpenAI API key
- JWT secret key
- Database credentials
- Redis credentials

**API:**
```python
def get_openai_api_key() -> Optional[str]
def get_jwt_secret() -> str
```

**Features:**
- Startup validation (fail fast if missing)
- Caching to reduce API calls
- Fallback to environment variables
- Logging (without exposing secrets)

---

## Data Models

### 1. Student
**File:** `app/models/student.py`

```python
class Student(Base):
    id: str (UUID)
    external_id: str
    first_name: str
    last_name: str
    grade: int
    school_id: UUID
    created_at: datetime
    updated_at: datetime
```

---

### 2. Linguistic Features
**File:** `app/models/features.py`

```python
class LinguisticFeatures(Base):
    id: UUID
    student_id: UUID
    features_json: dict  # 16 features
    created_at: datetime

# Features (16):
{
    "empathy_markers": float,
    "problem_solving_language": float,
    "perseverance_indicators": float,
    "social_processes": float,
    "cognitive_processes": float,
    "positive_sentiment": float,
    "negative_sentiment": float,
    "avg_sentence_length": float,
    "syntactic_complexity": float,
    "word_count": int,
    "unique_word_count": int,
    "readability_score": float,
    "noun_count": int,
    "verb_count": int,
    "adj_count": int,
    "adv_count": int
}
```

---

### 3. Behavioral Features
**File:** `app/models/features.py`

```python
class BehavioralFeatures(Base):
    id: UUID
    student_id: UUID
    features_json: dict  # 9 features
    created_at: datetime

# Features (9):
{
    "task_completion_rate": float,
    "time_efficiency": float,
    "retry_count": int,
    "recovery_rate": float,
    "distraction_resistance": float,
    "focus_duration": float,
    "collaboration_indicators": int,
    "leadership_indicators": int,
    "event_count": int
}
```

---

### 4. Skill Assessment
**File:** `app/models/assessment.py`

```python
class SkillAssessment(Base):
    id: UUID
    student_id: UUID
    skill_type: SkillType  # Enum
    score: float (0-1)
    confidence: float (0-1)
    reasoning: str
    evidence: List[Evidence]
    created_at: datetime

class SkillType(Enum):
    EMPATHY = "empathy"
    PROBLEM_SOLVING = "problem_solving"
    SELF_REGULATION = "self_regulation"
    RESILIENCE = "resilience"
```

---

### 5. Evidence
**File:** `app/models/assessment.py`

```python
class Evidence(Base):
    id: UUID
    assessment_id: UUID
    evidence_type: EvidenceType
    content: str
    score: float
    confidence: float
    relevance: float
    source: str

class EvidenceType(Enum):
    LINGUISTIC = "linguistic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"
```

---

## Sequence Diagrams

### 1. Single Student Inference Flow

```
Client          API Layer       ML Service      Evidence Fusion    DB/Redis
  |                |                |                  |              |
  |--POST /infer-->|                |                  |              |
  |   student_id   |                |                  |              |
  |                |                |                  |              |
  |                |--Authenticate--|                  |              |
  |                |                |                  |              |
  |                |--infer_all---->|                  |              |
  |                |   skills       |                  |              |
  |                |                |                  |              |
  |                |                |--Query features--|------------->|
  |                |                |    (parallel)    |              |
  |                |                |<-----------------|--------------|
  |                |                |  ling + beh data |              |
  |                |                |                  |              |
  |                |                |--Extract 26D-----|              |
  |                |                |   feature vector |              |
  |                |                |                  |              |
  |                |                |--Run XGBoost-----|              |
  |                |                |   (4 models)     |              |
  |                |                |                  |              |
  |                |                |--Calculate-------|              |
  |                |                |   confidence     |              |
  |                |                |   (3 components) |              |
  |                |                |                  |              |
  |                |<--scores-------|                  |              |
  |                |   confidence   |                  |              |
  |                |   importance   |                  |              |
  |                |                |                  |              |
  |                |--Record--------|------------------|------------->|
  |                |   metrics      |                  |              |
  |                |                |                  |              |
  |<--Response-----|                |                  |              |
  |   (152ms)      |                |                  |              |
  |                |                |                  |              |
```

---

### 2. Batch Inference Flow

```
Client          API Layer                  ML Service           DB/Redis
  |                |                           |                    |
  |--POST /batch-->|                           |                    |
  | [100 students] |                           |                    |
  |                |                           |                    |
  |                |--Authenticate-------------|                    |
  |                |                           |                    |
  |                |--asyncio.gather---------->|                    |
  |                |  [spawn 100 tasks]        |                    |
  |                |                           |                    |
  |                |   Task 1: student_1 ----->|--Query DB--------->|
  |                |   Task 2: student_2 ----->|--Query DB--------->|
  |                |   Task 3: student_3 ----->|--Query DB--------->|
  |                |   ...                     |                    |
  |                |   Task 100: student_100-->|--Query DB--------->|
  |                |                           |                    |
  |                |   [All execute in parallel]                    |
  |                |                           |                    |
  |                |<--Results (98 success)----|                    |
  |                |   (2 failures)            |                    |
  |                |                           |                    |
  |                |--Record batch metrics-----|------------------>|
  |                |                           |                    |
  |<--Response-----|                           |                    |
  | (8-10 seconds) |                           |                    |
  |   10-20/sec    |                           |                    |
  |                |                           |                    |
```

---

### 3. Evidence Fusion Flow

```
Fusion Service  ML Service   DB (Ling)   DB (Beh)   Config Manager
     |              |            |           |             |
     |--Collect---->|            |           |             |
     |   evidence   |            |           |             |
     |   (parallel) |            |           |             |
     |              |            |           |             |
     |--ML-------->|             |           |             |
     |   inference |             |           |             |
     |<--score-----|             |           |             |
     |   confidence|             |           |             |
     |              |            |           |             |
     |--Query-------|----------->|           |             |
     |   linguistic |            |           |             |
     |<--features---|------------|           |             |
     |              |            |           |             |
     |--Query-------|------------|---------->|             |
     |   behavioral |            |           |             |
     |<--features---|------------|-----------|             |
     |              |            |           |             |
     |--Get---------|------------|-----------|------------>|
     |   weights    |            |           |             |
     |<--config-----|------------|-----------|-------------|
     |   (skill)    |            |           |             |
     |              |            |           |             |
     |--Normalize---|            |           |             |
     |   evidence   |            |           |             |
     |   (z-score,  |            |           |             |
     |    min-max)  |            |           |             |
     |              |            |           |             |
     |--Apply-------|            |           |             |
     |   weights    |            |           |             |
     |   (skill-    |            |           |             |
     |    specific) |            |           |             |
     |              |            |           |             |
     |--Fuse--------|            |           |             |
     |   (weighted  |            |           |             |
     |    average)  |            |           |             |
     |              |            |           |             |
     |<--Return-----|            |           |             |
     |   fused_score|            |           |             |
     |   confidence |            |           |             |
     |   top_evidence            |           |             |
     |              |            |           |             |
```

---

### 4. GPT-4 Reasoning Generation Flow

```
Reasoning      Rate         Token        OpenAI       Secret
Generator     Limiter      Counter        API        Manager
    |            |            |            |            |
    |--Check---->|            |            |            |
    |   rate     |            |            |            |
    |<--OK-------|            |            |            |
    |  (tokens   |            |            |            |
    |   available)            |            |            |
    |            |            |            |            |
    |--Get-------|------------|------------|----------->|
    |   API key  |            |            |            |
    |<--key------|------------|------------|------------|
    |            |            |            |            |
    |--Build-----|            |            |            |
    |   prompt   |            |            |            |
    |   (evidence,            |            |            |
    |    score)  |            |            |            |
    |            |            |            |            |
    |--Count-----|----------->|            |            |
    |   tokens   |            |            |            |
    |<--count----|------------|            |            |
    |   (5,234)  |            |            |            |
    |            |            |            |            |
    |--Check-----|            |            |            |
    |   limit    |            |            |            |
    |   (120k)   |            |            |            |
    |            |            |            |            |
    |--Truncate--|            |            |            |
    |   evidence |            |            |            |
    |   if needed|            |            |            |
    |            |            |            |            |
    |--Call------|------------|----------->|            |
    |   GPT-4    |            |            |            |
    |   (async)  |            |            |            |
    |            |            |            |            |
    |            |            |       [2-5 seconds]     |
    |            |            |            |            |
    |<--Response-|------------|------------|            |
    |   (JSON)   |            |            |            |
    |   reasoning|            |            |            |
    |   strengths|            |            |            |
    |   growth   |            |            |            |
    |            |            |            |            |
    |--Consume-->|            |            |            |
    |   token    |            |            |            |
    |   (rate    |            |            |            |
    |    limit)  |            |            |            |
    |            |            |            |            |
```

---

## External Dependencies

### 1. PostgreSQL
**Version:** 14+
**Purpose:** Primary data store

**Tables:**
- `students` - Student records
- `linguistic_features` - Language analysis data
- `behavioral_features` - Task/game telemetry
- `skill_assessments` - Assessment results
- `evidence` - Supporting evidence for assessments
- `schools`, `teachers`, `users` - Supporting entities

**Indexes:**
```sql
-- Critical performance indexes
CREATE INDEX idx_linguistic_features_student_created
  ON linguistic_features(student_id, created_at DESC);

CREATE INDEX idx_behavioral_features_student_created
  ON behavioral_features(student_id, created_at DESC);

CREATE INDEX idx_skill_assessment_student
  ON skill_assessments(student_id);
```

**Connection Pooling:**
```python
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
```

---

### 2. Redis
**Version:** 7+
**Purpose:** Metrics storage and caching

**Usage:**
- **Metrics:** Sorted set with timestamp scores
- **TTL:** Automatic cleanup (keeps last 10,000 entries)
- **Fallback:** In-memory storage if Redis unavailable

**Configuration:**
```python
REDIS_URL = "redis://localhost:6379/0"
REDIS_MAX_CONNECTIONS = 50
```

---

### 3. OpenAI API
**Purpose:** GPT-4 reasoning generation

**Model:** `gpt-4o-mini` (default)
- Context window: 128k tokens
- Cost-effective for reasoning
- Fallback to template-based reasoning

**Rate Limits:**
```python
CALLS_PER_MINUTE = 50
CALLS_PER_HOUR = 500
BURST_SIZE = 10
```

**Token Management:**
- Automatic evidence truncation
- Safe buffer (8k tokens for response)
- tiktoken-based counting

---

### 4. GCP Secret Manager
**Purpose:** Secure credential storage (production)

**Secrets:**
- `openai-api-key` - OpenAI API key
- `jwt-secret-key` - JWT signing key
- Database credentials
- Redis credentials

**Fallback:** Environment variables for development

---

### 5. Google Cloud Storage
**Purpose:** ML model storage

**Structure:**
```
gs://unseenedge-models/
  v1.0.0/
    empathy_model.pkl
    empathy_features.pkl
    problem_solving_model.pkl
    problem_solving_features.pkl
    self_regulation_model.pkl
    self_regulation_features.pkl
    resilience_model.pkl
    resilience_features.pkl
    metadata.json
```

**Metadata Format:**
```json
{
  "version": "1.0.0",
  "created_at": "2025-11-01T00:00:00Z",
  "models": {
    "empathy": {
      "checksum": "sha256:...",
      "size_bytes": 524288,
      "accuracy": 0.87
    },
    ...
  }
}
```

---

## Design Decisions

### 1. Why XGBoost for ML Models?

**Decision:** Use XGBoost for all skill predictions

**Rationale:**
- **Performance:** Fast inference (<50ms per prediction)
- **Accuracy:** High performance on tabular data (0.85-0.90 accuracy)
- **Interpretability:** Feature importance for explainability
- **Small model size:** ~500KB per model (fast loading)
- **Production-ready:** Mature library with strong community

**Alternatives Considered:**
- Neural networks: Overkill for 26 features, slower inference
- Random Forest: Similar performance, larger model size
- Linear models: Insufficient accuracy for complex patterns

---

### 2. Evidence Fusion Approach

**Decision:** Weighted averaging with skill-specific weights

**Rationale:**
- **Flexibility:** Different skills benefit from different evidence sources
- **Interpretability:** Clear contribution of each source
- **Tunable:** Weights can be adjusted based on validation data
- **Robust:** Graceful degradation if sources unavailable

**Weight Distribution:**
- ML inference primary (50%) - Most reliable
- Linguistic/behavioral secondary (10-30%) - Context-specific
- Confidence adjustment (10%) - Uncertainty handling

**Example (Self-Regulation):**
- Behavioral features weighted higher (30%) - Focus/distraction data critical
- Linguistic features lower (10%) - Less predictive for self-regulation

---

### 3. Confidence Calculation Methodology

**Decision:** 3-component confidence scoring

**Components:**
1. **Tree Variance** (50% weight)
   - Lower variance = higher confidence
   - Captures model uncertainty

2. **Prediction Extremity** (30% weight)
   - Mid-range predictions more confident
   - Scores near 0 or 1 treated cautiously

3. **Feature Completeness** (20% weight)
   - More non-zero features = higher confidence
   - Missing data reduces confidence

**Rationale:**
- **Multi-faceted:** Captures different uncertainty sources
- **Validated:** Correlates with prediction accuracy
- **Bounded:** Always returns 0.3-0.95 (prevents over-confidence)

**Formula:**
```python
confidence = (
    0.5 * tree_variance_confidence +
    0.3 * extremity_confidence +
    0.2 * completeness_confidence
)
confidence = clip(confidence, 0.3, 0.95)
```

---

### 4. Caching and Performance Strategies

**Decision:** Multi-level caching with singleton services

**Caching Layers:**
1. **Model Caching** - In-memory, application lifetime
2. **Secret Caching** - In-memory, per-request
3. **Config Caching** - In-memory, hot-reloadable
4. **Metrics** - Redis, with memory fallback

**Performance Optimizations:**
1. **Parallel DB Queries** - 3x speedup
   ```python
   # Before: Sequential (150ms total)
   ling = await get_linguistic_features()
   beh = await get_behavioral_features()

   # After: Parallel (50ms total)
   ling, beh = await asyncio.gather(
       get_linguistic_features(),
       get_behavioral_features()
   )
   ```

2. **Batch Processing** - 10-20 students/second
   - Async parallel execution
   - Individual error handling
   - Connection pool optimization

3. **Evidence Collection** - Concurrent sources
   - ML, linguistic, behavioral in parallel
   - Graceful degradation if one fails

**Rationale:**
- **Sub-200ms target:** Achieved through parallel execution
- **Scalability:** Horizontal scaling with stateless services
- **Reliability:** Graceful degradation preserves availability

---

### 5. Rate Limiting Strategy

**Decision:** Token bucket with dual limits (per-minute, per-hour)

**Configuration:**
```python
GPT4_CALLS_PER_MINUTE = 50
GPT4_CALLS_PER_HOUR = 500
BURST_SIZE = 10
```

**Rationale:**
- **Cost Control:** Prevents runaway API costs
- **API Compliance:** Respects OpenAI rate limits
- **Burst Handling:** Allows short spikes with burst allowance
- **Graceful Degradation:** Fallback to templates when exhausted

**Implementation:**
- Gradual token refill (not step function)
- Async-safe with locking
- Clear error messages with retry-after times

---

### 6. Normalization Methods

**Decision:** Different normalization for different feature types

**Linguistic Features: Z-score + Sigmoid**
```python
z_score = (value - mean) / std_dev
normalized = 1 / (1 + exp(-z_score))
```
**Reason:** Handles wide range distributions, centers around 0.5

**Behavioral Features: Min-Max Scaling**
```python
normalized = (value - min) / (max - min)
normalized = clip(normalized, 0.0, 1.0)
```
**Reason:** Natural bounds (e.g., rates 0-1), preserves relative differences

**ML Predictions: No Transformation**
- Already in 0-1 range from regression models

---

### 7. GPT-4 Token Management

**Decision:** Automatic evidence truncation with token counting

**Strategy:**
1. Count tokens with tiktoken
2. Compare to safe limit (120k for gpt-4o-mini)
3. Iteratively reduce evidence (10 → 5 → 3 items)
4. Fallback to templates if still over limit

**Rationale:**
- **Cost Control:** Prevents expensive calls
- **Reliability:** Always succeeds (fallback)
- **Quality:** Prioritizes highest-quality evidence

**Evidence Prioritization:**
```python
sorted_evidence = sorted(
    evidence,
    key=lambda x: x.weight * x.relevance * x.confidence,
    reverse=True
)
truncated = sorted_evidence[:max_items]
```

---

## System Properties

### Scalability
- **Horizontal:** Stateless services, shared nothing
- **Vertical:** Connection pooling, async I/O
- **Database:** Read replicas for query scaling
- **Redis:** Clustering for metrics storage

### Reliability
- **Fallbacks:** Memory cache, template reasoning
- **Error Handling:** Per-student failures in batch don't block others
- **Health Checks:** Database, Redis, model loading status
- **Graceful Degradation:** System functional with reduced capabilities

### Performance
- **Latency:** <200ms per student (target: <30s)
- **Throughput:** 10-20 students/second (batch)
- **Database:** Optimized indexes, parallel queries
- **Caching:** Multi-level (models, secrets, config)

### Security
- **Authentication:** JWT tokens
- **Secrets:** GCP Secret Manager (production)
- **API Keys:** Validated at startup
- **Rate Limiting:** Prevents abuse and cost overruns
- **Input Validation:** Pydantic models, SQL injection prevention

### Observability
- **Metrics:** Redis-backed inference tracking
- **Logging:** Structured logs with correlation IDs
- **Health Checks:** Database, Redis, OpenAI connectivity
- **Error Tracking:** Detailed error messages with context

---

## Future Improvements

### Short Term (1-3 months)
1. **Response Caching:** Cache inference results for 5 minutes
2. **Connection Pooling:** pgbouncer for database connections
3. **APM Integration:** New Relic or DataDog for distributed tracing
4. **Feature Store:** Dedicated feature storage for faster access

### Medium Term (3-6 months)
1. **Model Versioning:** A/B testing for model updates
2. **Adaptive Weights:** Learn fusion weights from validation data
3. **Real-time Features:** Stream processing for behavioral data
4. **Multi-region:** Deploy in multiple GCP regions

### Long Term (6-12 months)
1. **Model Retraining:** Automated pipeline with new data
2. **Personalization:** Student-specific weight adjustments
3. **Explainability:** SHAP values for prediction explanations
4. **Multi-modal:** Image/video analysis for richer evidence

---

## References

### Implementation Files
- **ML Inference:** `app/services/skill_inference.py`
- **Evidence Fusion:** `app/services/evidence_fusion.py`
- **Reasoning Generation:** `app/services/reasoning_generator.py`
- **API Endpoints:** `app/api/endpoints/inference.py`
- **Metrics Store:** `app/core/metrics.py`
- **Rate Limiter:** `app/core/rate_limiter.py`
- **Fusion Config:** `app/core/fusion_config.py`
- **Secret Manager:** `app/core/secrets.py`

### Related Documentation
- **Evidence Normalization:** `docs/EVIDENCE_NORMALIZATION.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md` (pending)
- **Training Data Format:** `docs/TRAINING_DATA_FORMAT.md` (pending)
- **Performance Tuning:** `docs/PERFORMANCE_TUNING.md` (pending)

### External Resources
- **XGBoost:** https://xgboost.readthedocs.io/
- **FastAPI:** https://fastapi.tiangolo.com/
- **OpenAI API:** https://platform.openai.com/docs/
- **GCP Secret Manager:** https://cloud.google.com/secret-manager/docs

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Status:** Production Ready
