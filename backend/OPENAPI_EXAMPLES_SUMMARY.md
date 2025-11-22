# OpenAPI Examples Configuration Summary

## Overview
Added default example values to FastAPI Swagger UI documentation for easier API testing at http://localhost:8080/api/v1/docs

## Changes Made

### 1. Assessment Schemas (`app/schemas/assessment.py`)

#### AssessmentRequest
- Added field-level examples for `skill_type`
- Added model-level examples showing two use cases:
  - Example 1: Empathy assessment with caching enabled
  - Example 2: Problem solving assessment without caching

```python
model_config = {
    "json_schema_extra": {
        "examples": [
            {"skill_type": "empathy", "use_cached": True},
            {"skill_type": "problem_solving", "use_cached": False}
        ]
    }
}
```

#### BatchAssessmentRequest
- Added examples for `student_ids` (UUID list)
- Added examples for `skill_types` (enum list)
- Complete example showing batch assessment of 2 students

### 2. Telemetry Schemas (`app/schemas/telemetry.py`)

#### TelemetryEventCreate
- Added comprehensive examples for all fields:
  - `event_type`: mission_start, choice_made, mission_complete
  - `data`: Mission-specific event data
  - `mission_id`: mission_001, mission_002
  - `game_version`: 1.0.0, 1.1.0
- Two complete examples showing different event types:
  - Mission start event with difficulty data
  - Choice made event with timing data

```python
"examples": [
    {
        "event_id": "550e8400-e29b-41d4-a716-446655440001",
        "student_id": "550e8400-e29b-41d4-a716-446655440099",
        "event_type": "mission_start",
        "timestamp": "2025-01-19T12:00:00Z",
        "data": {"mission_name": "Empathy Quest", "difficulty": "medium"},
        "session_id": "550e8400-e29b-41d4-a716-446655440100",
        "mission_id": "mission_001",
        "game_version": "1.0.0"
    }
]
```

#### TelemetryBatchCreate
- Batch-level examples with complete event arrays
- Valid UUIDs for `batch_id` and `client_version`

#### SessionCloseRequest
- Examples for session closure with different reasons:
  - User logged out
  - Session timeout
  - Game completed

### 3. Authentication Schemas (`app/api/endpoints/auth.py`)

#### UserLogin
- Added examples for email and password fields
- Two complete login examples:
  - Teacher login: teacher@school.edu
  - Admin login: admin@school.edu

```python
model_config = {
    "json_schema_extra": {
        "examples": [
            {"email": "teacher@school.edu", "password": "password123"},
            {"email": "admin@school.edu", "password": "SecurePass456!"}
        ]
    }
}
```

### 4. Inference Schemas (`app/api/endpoints/inference.py`)

#### EvidenceItem
- Examples for evidence sources: transcript, game_telemetry
- Sample evidence text and relevance scores
- Complete example showing transcript-based evidence

### 5. Assessment Endpoint Path Parameters (`app/api/endpoints/assessments.py`)

Added `Path()` annotations with examples for all student_id and skill_type parameters:

```python
student_id: str = Path(
    ...,
    description="Student ID (UUID format)",
    examples=["550e8400-e29b-41d4-a716-446655440001"]
)

skill_type: str = Path(
    ...,
    description="Skill type to retrieve",
    examples=["empathy", "problem_solving", "self_regulation"]
)
```

Applied to endpoints:
- `POST /assessments/{student_id}`
- `POST /assessments/{student_id}/all`
- `GET /assessments/{student_id}`
- `GET /assessments/{student_id}/{skill_type}/latest`

## Benefits

1. **Easier Testing**: Developers can now test API endpoints without manually crafting valid request bodies
2. **Better Documentation**: Clear examples show expected data formats and valid values
3. **UUID Guidance**: Consistent UUID examples across all endpoints
4. **Enum Values**: Shows available skill types and event types
5. **Realistic Data**: Examples use realistic mission names, student data, and game events

## Testing the Changes

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. Visit the interactive docs:
   ```
   http://localhost:8080/api/v1/docs
   ```

3. Try any POST endpoint - you'll see pre-filled example values in the request body
4. Path parameters also show example UUIDs for easy copying

## Modified Files

- `backend/app/schemas/assessment.py` - Added examples to request models
- `backend/app/schemas/telemetry.py` - Added examples to telemetry events
- `backend/app/api/endpoints/auth.py` - Added login examples
- `backend/app/api/endpoints/inference.py` - Added evidence examples
- `backend/app/api/endpoints/assessments.py` - Added path parameter examples

## OpenAPI Schema Validation

The examples are properly included in the OpenAPI schema at:
```
http://localhost:8080/api/v1/openapi.json
```

All examples use valid UUIDs, enums, and data structures that match the actual API validation rules.
