# Inference vs Assessment Endpoints - Key Differences

## Summary

The backend has **two different systems** for skill assessments:

1. **ML Inference Endpoints** (`/infer/*`) - Run trained ML models on extracted features
2. **AI Assessment Endpoints** (`/assessments/*`) - Use AI to generate assessments with reasoning

## ML Inference Endpoints (`/infer/*`)

### Purpose
Run trained XGBoost machine learning models to predict skill scores based on extracted features.

### Requirements
- **Linguistic features** must be extracted from transcripts/conversations
- **Behavioral features** must be extracted from game telemetry
- **Trained ML models** must exist for each skill type

### Workflow
```
Game Telemetry → Feature Extraction → ML Model → Skill Score
     ↓                    ↓                ↓
Transcripts → Linguistic Features → XGBoost → Confidence
```

### Endpoints

#### POST `/api/v1/infer/{student_id}`
Run inference for all skills for a student.

**Requirements:**
- Student must have extracted linguistic_features
- Student must have extracted behavioral_features
- ML models must be trained

**Returns:**
```json
{
  "student_id": "uuid",
  "skills": [
    {
      "skill_type": "empathy",
      "score": 0.85,
      "confidence": 0.92,
      "feature_importance": {...},
      "inference_time_ms": 45.2,
      "model_version": "1.0.0",
      "evidence": [...],
      "reasoning": "AI-generated reasoning"
    }
  ],
  "total_inference_time_ms": 180.5,
  "timestamp": "2025-11-19T12:00:00"
}
```

#### POST `/api/v1/infer/{student_id}/{skill_type}`
Run inference for a single skill.

#### POST `/api/v1/infer-batch`
Run inference for multiple students in parallel.

### When to Use
- Production system with real game telemetry
- After features have been extracted
- When ML models are trained and validated
- Real-time scoring during gameplay

### Current Status
❌ **Not Ready** - Requires:
- Feature extraction from telemetry data
- Trained ML models
- Linguistic and behavioral feature tables populated

---

## AI Assessment Endpoints (`/assessments/*`)

### Purpose
Generate AI-powered skill assessments using OpenAI/Claude with detailed reasoning and recommendations.

### Requirements
- **OpenAI API key** (or other AI provider)
- Student exists in database
- Optional: Historical data for context

### Workflow
```
Student Data → AI Prompt → OpenAI/Claude → Assessment with Reasoning
     ↓             ↓              ↓
Demographics → Context → Analysis → Recommendations
```

### Endpoints

#### POST `/api/v1/assessments/{student_id}`
Generate an AI assessment for a single skill.

**Request:**
```json
{
  "skill_type": "empathy",
  "use_cached": true
}
```

**Returns:**
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "skill_type": "empathy",
  "score": 0.85,
  "confidence": 0.90,
  "reasoning": "Student demonstrates strong understanding of others' perspectives through collaborative interactions and supportive communication patterns. Shows consistent ability to recognize emotional cues and respond appropriately.",
  "recommendations": "Continue practicing perspective-taking through role-play activities and reflective discussions. Encourage exploring diverse viewpoints in literature and current events.",
  "evidence": [
    {
      "id": "uuid",
      "evidence_type": "linguistic",
      "source": "Session 5",
      "content": "Student demonstrated empathy during classroom activities",
      "relevance_score": 0.85
    }
  ],
  "created_at": "2025-11-19T12:00:00",
  "updated_at": "2025-11-19T12:00:00"
}
```

#### POST `/api/v1/assessments/{student_id}/all`
Generate AI assessments for all primary skills (empathy, problem_solving, self_regulation, resilience).

**Returns:**
```json
{
  "student_id": "uuid",
  "assessments": [...],
  "overall_score": 0.82,
  "assessed_at": "2025-11-19T12:00:00"
}
```

#### POST `/api/v1/assessments/batch`
Generate assessments for multiple students.

**Request:**
```json
{
  "student_ids": ["uuid1", "uuid2"],
  "skill_types": ["empathy", "problem_solving"],
  "use_cached": false
}
```

#### GET `/api/v1/assessments/{student_id}`
**Retrieve existing assessments** from database (does not generate new ones).

**Query Parameters:**
- `skill_type`: Filter by specific skill (optional)
- `limit`: Maximum assessments to return (default: 10)

**Returns:**
```json
[
  {
    "id": "uuid",
    "student_id": "uuid",
    "skill_type": "empathy",
    "score": 0.85,
    "confidence": 0.90,
    "reasoning": "...",
    "recommendations": "...",
    "evidence": [...],
    "created_at": "2025-11-19T12:00:00",
    "updated_at": "2025-11-19T12:00:00"
  }
]
```

#### GET `/api/v1/assessments/{student_id}/{skill_type}/latest`
Get the most recent assessment for a specific skill.

### When to Use
- Development and testing with sample data
- When detailed AI reasoning is needed
- Early stages before ML models are trained
- Teacher dashboards showing assessment explanations
- Generating baseline assessments

### Current Status
✅ **Ready** - Currently in use with:
- 50 students in database
- 200 assessments (4 skills × 50 students)
- AI-generated reasoning and recommendations
- Sample evidence for each assessment

---

## Dashboard Integration

### Admin/Teacher Dashboard
**Uses:** `GET /api/v1/assessments/{student_id}`
- Retrieves existing assessments with reasoning
- Displays AI explanations for each skill
- Shows recommendations for teachers

### Student Portal
**Uses:** `GET /api/v1/assessments/{student_id}`
- Shows student's current skill levels
- Displays personalized feedback
- Tracks progress over time

### Previous Issue (Fixed)
❌ **Old Code:** Used `POST /api/v1/infer/{student_id}` (ML inference)
- Failed because no features extracted
- Required trained ML models

✅ **New Code:** Uses `GET /api/v1/assessments/{student_id}`
- Retrieves existing assessments
- Works with current sample data
- Shows AI reasoning immediately

---

## Key Differences Summary

| Feature | ML Inference (`/infer/*`) | AI Assessment (`/assessments/*`) |
|---------|--------------------------|----------------------------------|
| **Data Source** | Extracted features (linguistic/behavioral) | Student records + AI generation |
| **Method** | Trained XGBoost models | OpenAI/Claude API |
| **Speed** | Very fast (~50ms) | Slower (~2-5 seconds) |
| **Reasoning** | Feature importance | Detailed AI explanation |
| **Requirements** | Features + trained models | API key + student data |
| **Cost** | Free (after training) | Per-request API costs |
| **Current Status** | Not ready (no features) | ✅ Working with sample data |
| **Best For** | Production, real-time | Development, detailed analysis |

---

## Migration Path

### Phase 1: Development (Current)
- Use `GET /assessments/{student_id}` to retrieve existing assessments
- Use `POST /assessments/*` to generate new assessments with AI
- Dashboards display AI reasoning and recommendations
- Sample data for testing

### Phase 2: Feature Extraction
- Implement telemetry event processing
- Extract linguistic features from transcripts
- Extract behavioral features from gameplay
- Populate feature tables

### Phase 3: Model Training
- Train XGBoost models on labeled data
- Validate model accuracy
- Version control for models
- Deploy trained models

### Phase 4: Production
- Switch dashboards to use `/infer/*` endpoints
- Real-time inference during gameplay
- Keep `/assessments/*` for detailed reports
- Use both systems complementarily

---

## Testing

### Test Current System (AI Assessments)
```bash
# Get existing assessments
curl http://localhost:8080/api/v1/assessments/{student_id}

# Generate new assessment
curl -X POST http://localhost:8080/api/v1/assessments/{student_id} \
  -H "Content-Type: application/json" \
  -d '{"skill_type": "empathy", "use_cached": true}'

# Get latest assessment for a skill
curl http://localhost:8080/api/v1/assessments/{student_id}/empathy/latest
```

### Test ML Inference (When Ready)
```bash
# Run inference (requires features)
curl -X POST http://localhost:8080/api/v1/infer/{student_id}

# Check if features exist
psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db \
  -c "SELECT COUNT(*) FROM linguistic_features WHERE student_id = 'uuid';"
```

---

## Files Modified

### Dashboard Files (Fixed)
- `dashboard/student_portal.py:133-168` - Changed from POST /infer to GET /assessments
- `dashboard/app_template.py:80-115` - Changed from POST /infer to GET /assessments
- `dashboard/admin_dashboard.py:150-178` - Already using assessments endpoint correctly

### API Files
- `app/api/endpoints/inference.py` - ML inference endpoints
- `app/api/endpoints/assessments.py` - AI assessment endpoints

### Service Files
- `app/services/skill_inference.py` - ML inference service
- `app/services/ai_assessment.py` - AI assessment service
- `app/services/evidence_service.py` - Evidence collection

---

**Last Updated:** 2025-11-19
**Status:** Dashboards fixed to use assessment endpoints
