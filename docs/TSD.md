
# Middle School Non-Academic Skills Measurement System (MASS) – Technical Specification
### Version 1.0 — Engineering-Ready

---

## 1. System Overview
MASS is a cloud-native platform that ingests:
- Game telemetry
- Classroom audio
- Project deliverables
- Rubric scores

Processes them through:
- STT
- NLP feature extraction
- Skill inference models
- Evidence fusion

Outputs:
- Dashboards
- Reports
- Growth curves

---

## 2. Architecture Summary

```
                        UI Layer
           Teacher | Admin | Student Dashboards
                            |
                        API Layer
                        FastAPI/GraphQL
                            |
      -------------------------------------------------
      | Telemetry Engine | NLP/ML Engine | Data Storage |
      -------------------------------------------------
                            |
                    Evidence Fusion Engine
                            |
                      Skill Scoring Engine
```

---

## 3. Component Specifications

### Backend (FastAPI)
- Authentication
- Telemetry ingestion
- ML job orchestration
- Evidence serving
- User roles & permissions

### ML Layer
- Transcript STT
- Embedding generation (transformers)
- Feature extraction
- Skill inference (XGBoost/logistic regression)
- Evidence selection
- Explainability (SHAP)

### Game Engine
- Unity
- Sends structured JSON telemetry
- Sync via WebSockets/REST

### Storage Layer
- PostgreSQL
- TimescaleDB
- Redis cache
- GCS/S3 for audio files

---

## 4. Data Flow

### Game Data Flow
```
Unity → Telemetry API → Feature Extractor → DB → Fusion → Dashboard
```

### Audio Data Flow
```
Mic → Upload → STT → NLP → Features → Fusion → Dashboard
```

---

## 5. Data Models

### Students
- id
- name
- school_id
- demographic_info
- timestamps

### GameTelemetry
- id
- student_id
- mission_id
- choice
- timestamps
- metadata

### Transcript
- transcript text
- diarization info
- confidence score

### SkillAssessment
- skill
- score
- confidence
- evidence JSON
- trend data

---

## 6. APIs

### Authentication
- POST /auth/login

### Telemetry
- POST /telemetry/event

### Audio
- POST /audio/upload

### Skills
- GET /skills/{student_id}
- GET /skills/{student_id}/history

---

## 7. Machine Learning

### Inputs
- behavioral telemetry
- linguistic features
- project metadata
- rubric scoring signals

### Models
- Transformer embeddings
- Task-specific XGBoost models
- Logistic regression fallback

### Explainability
- Extract relevant sentences
- Highlight linguistic markers
- Provide summary reasoning

---

## 8. Pipelines

### STT Pipeline
- Noise reduction
- Diarization
- Transcript generation

### NLP Pipeline
- Chunking
- Embedding
- Feature extraction
- Scoring

### Fusion Pipeline
- Weight signals
- Compute final score
- Generate evidence

---

## 9. Game Telemetry Specification

```
{
  "event_type": "choice",
  "mission_id": "M01",
  "choice_id": "C12",
  "time_taken": 3.4,
  "recovery_time": 1.2,
  "empathy_flag": true,
  "collaboration_flag": false,
  "timestamp": 173654321
}
```

---

## 10. Classroom Audio Specifications
- Recommended mic setup
- 16kHz sampling
- Multi-speaker environment
- Automatic diarization

---

## 11. Evidence Fusion Engine
Steps:
1. Normalize features
2. Weight based on reliability
3. Extract top evidence snippets
4. Generate skill score
5. Compute confidence
6. Produce reasoning

---

## 12. Dashboards
- Teacher dashboard: evidence + insights
- Admin dashboard: heatmaps + trends
- Student dashboard: growth view

---

## 13. Deployment Architecture
- Cloud Run / AWS Lambda
- Load-balanced API
- Autoscaling workers
- CI/CD with GitHub Actions
- Monitoring via Cloud Monitoring

---

## 14. Scalability Strategy
- Horizontal scaling
- Cached embeddings
- Batch + streaming pipelines
- Async job queues

---

## 15. Security & Compliance
- TLS 1.3
- AES-256 at rest
- RBAC
- Audit logs
- FERPA/COPPA compliance
- Data retention policies

---

## 16. Failure Recovery
- Auto-retry queues
- Graceful degradation
- Fallback inference
- Rollback support

---

## 17. Testing Strategy
- Unit tests
- Integration tests
- Pipeline validation
- ML accuracy checks
- Usability tests

---

## 18. Dependencies
- Python
- AWS/GCP
- Unity
- NLP libraries

---

# END OF TSD
