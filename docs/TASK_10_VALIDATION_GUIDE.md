# Task 10: Feature Extraction Service - Manual Validation Guide

This guide provides step-by-step instructions to manually validate the feature extraction service implemented in Task 10.

## Prerequisites

Before starting validation:

1. **Database is running** (PostgreSQL)
2. **Python environment is activated** with all dependencies installed
3. **API server is running** (`uvicorn app.main:app --reload`)
4. **Database is seeded** with test data

## Quick Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 3. Install/verify dependencies (if not already done)
pip install -r requirements.txt

# 4. Download spaCy model (if not already done)
python -m spacy download en_core_web_sm

# 5. Seed the database
python scripts/seed_data.py --clear

# 6. Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server should start at `http://localhost:8000`

---

## Test Plan Overview

| Test | Feature | Method | Expected Result |
|------|---------|--------|-----------------|
| 1 | API Documentation | Manual | Endpoints visible in Swagger |
| 2 | Linguistic Extraction (Single) | cURL/Swagger | Features extracted and saved |
| 3 | Behavioral Extraction (Single) | cURL/Swagger | Features extracted and saved |
| 4 | Linguistic Retrieval | cURL/Swagger | Previously extracted features returned |
| 5 | Behavioral Retrieval | cURL/Swagger | Previously extracted features returned |
| 6 | Batch Linguistic Extraction | cURL/Swagger | Multiple transcripts processed |
| 7 | Batch Behavioral Extraction | cURL/Swagger | Multiple sessions processed |
| 8 | Error Handling | cURL/Swagger | Proper 404/500 responses |
| 9 | Feature Quality | Manual | Feature values are reasonable |
| 10 | Database Storage | PostgreSQL | Data persisted correctly |

---

## Validation Tests

### Test 1: Check API Documentation

**Purpose**: Verify feature extraction endpoints are registered and documented

**Steps**:
1. Open browser to `http://localhost:8000/api/v1/docs`
2. Look for the **"features"** section
3. Verify these 6 endpoints exist:
   - `POST /api/v1/features/linguistic/{transcript_id}`
   - `POST /api/v1/features/behavioral/{session_id}`
   - `POST /api/v1/features/batch/linguistic`
   - `POST /api/v1/features/batch/behavioral`
   - `GET /api/v1/features/linguistic/{transcript_id}`
   - `GET /api/v1/features/behavioral/{session_id}`

**Expected Result**: ✅ All 6 endpoints visible in Swagger UI

**Alternative (cURL)**:
```bash
curl -s http://localhost:8000/api/v1/openapi.json | jq '.paths | keys | map(select(contains("features")))'
```

---

### Test 2: Extract Linguistic Features (Single Transcript)

**Purpose**: Verify linguistic feature extraction from a transcript

**Method A: Using Swagger UI**
1. Navigate to `http://localhost:8000/api/v1/docs`
2. Find `POST /api/v1/features/linguistic/{transcript_id}`
3. Click **"Try it out"**
4. Get a transcript ID from seeded data (see "Getting Test IDs" section below)
5. Enter the transcript ID
6. Click **"Execute"**
7. Check the response

**Method B: Using cURL**
```bash
# Get a transcript ID first
TRANSCRIPT_ID=$(curl -s http://localhost:8000/api/v1/transcripts | jq -r '.[0].id')

# Extract features
curl -X POST "http://localhost:8000/api/v1/features/linguistic/${TRANSCRIPT_ID}" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response** (Status 201):
```json
{
  "transcript_id": "uuid-here",
  "student_id": "uuid-here",
  "features": {
    "empathy_markers": 0.05,
    "problem_solving_language": 0.10,
    "perseverance_indicators": 0.03,
    "social_processes": 0.15,
    "cognitive_processes": 0.20,
    "positive_sentiment": 0.65,
    "negative_sentiment": 0.10,
    "neutral_sentiment": 0.25,
    "avg_sentence_length": 12.5,
    "syntactic_complexity": 0.42,
    "word_count": 125,
    "unique_word_count": 85,
    "lexical_diversity": 0.68,
    "readability_score": 7.2,
    "noun_count": 30,
    "verb_count": 25,
    "adj_count": 15,
    "adv_count": 8
  },
  "created_at": "2025-01-13T10:30:00"
}
```

**What to Check**:
- ✅ Status code is 201 Created
- ✅ Response includes `transcript_id`, `student_id`, `features`, `created_at`
- ✅ Features object contains expected keys (empathy_markers, sentiment, word_count, etc.)
- ✅ Feature values are numeric and within reasonable ranges
- ✅ No error messages

---

### Test 3: Extract Behavioral Features (Single Session)

**Purpose**: Verify behavioral feature extraction from game telemetry

**Method A: Using Swagger UI**
1. Navigate to `http://localhost:8000/api/v1/docs`
2. Find `POST /api/v1/features/behavioral/{session_id}`
3. Click **"Try it out"**
4. Get a game session ID from seeded data
5. Enter the session ID
6. Click **"Execute"**

**Method B: Using cURL**
```bash
# Get a game session ID
SESSION_ID=$(curl -s http://localhost:8000/api/v1/game-sessions | jq -r '.[0].id')

# Extract features
curl -X POST "http://localhost:8000/api/v1/features/behavioral/${SESSION_ID}" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response** (Status 201):
```json
{
  "session_id": "uuid-here",
  "student_id": "uuid-here",
  "features": {
    "total_events": 50,
    "task_completion_rate": 0.80,
    "avg_time_per_task": 45.2,
    "time_efficiency": 0.75,
    "retry_count": 8,
    "recovery_rate": 0.625,
    "avg_recovery_time": 12.5,
    "distraction_resistance": 0.85,
    "focus_duration": 300.0,
    "collaboration_indicators": 0.15,
    "leadership_indicators": 0.10,
    "avg_response_time": 2500.0
  },
  "created_at": "2025-01-13T10:35:00"
}
```

**What to Check**:
- ✅ Status code is 201 Created
- ✅ Response includes `session_id`, `student_id`, `features`, `created_at`
- ✅ Features object contains expected behavioral metrics
- ✅ Feature values are numeric and reasonable
- ✅ No error messages

---

### Test 4: Retrieve Linguistic Features

**Purpose**: Verify previously extracted features can be retrieved

**Prerequisites**: Run Test 2 first to create features

**Method: Using cURL**
```bash
# Use the same transcript ID from Test 2
curl -X GET "http://localhost:8000/api/v1/features/linguistic/${TRANSCRIPT_ID}" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response** (Status 200):
- Same features object as in Test 2
- Includes `updated_at` timestamp

**What to Check**:
- ✅ Status code is 200 OK
- ✅ Features match what was extracted in Test 2
- ✅ Both `created_at` and `updated_at` are present

---

### Test 5: Retrieve Behavioral Features

**Purpose**: Verify previously extracted behavioral features can be retrieved

**Prerequisites**: Run Test 3 first

**Method: Using cURL**
```bash
# Use the same session ID from Test 3
curl -X GET "http://localhost:8000/api/v1/features/behavioral/${SESSION_ID}" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response** (Status 200):
- Same features object as in Test 3
- Includes `updated_at` timestamp

**What to Check**:
- ✅ Status code is 200 OK
- ✅ Features match what was extracted in Test 3

---

### Test 6: Batch Linguistic Feature Extraction

**Purpose**: Verify batch processing of multiple transcripts

**Method: Using cURL**
```bash
# Get multiple transcript IDs
TRANSCRIPT_IDS=$(curl -s http://localhost:8000/api/v1/transcripts | jq -r '[.[].id] | .[0:3]')

# Extract batch features
curl -X POST "http://localhost:8000/api/v1/features/batch/linguistic" \
  -H "Content-Type: application/json" \
  -d "${TRANSCRIPT_IDS}" | jq .
```

**Expected Response** (Status 202):
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

**What to Check**:
- ✅ Status code is 202 Accepted
- ✅ `total` matches number of transcript IDs sent
- ✅ `successful` + `failed` = `total`
- ✅ `errors` array is empty (or contains only expected errors)

---

### Test 7: Batch Behavioral Feature Extraction

**Purpose**: Verify batch processing of multiple game sessions

**Method: Using cURL**
```bash
# Get multiple session IDs
SESSION_IDS=$(curl -s http://localhost:8000/api/v1/game-sessions | jq -r '[.[].id] | .[0:3]')

# Extract batch features
curl -X POST "http://localhost:8000/api/v1/features/batch/behavioral" \
  -H "Content-Type: application/json" \
  -d "${SESSION_IDS}" | jq .
```

**Expected Response** (Status 202):
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

**What to Check**:
- ✅ Status code is 202 Accepted
- ✅ Batch summary is accurate

---

### Test 8: Error Handling

**Purpose**: Verify proper error responses for invalid inputs

#### Test 8a: Non-existent Transcript
```bash
curl -X POST "http://localhost:8000/api/v1/features/linguistic/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json"
```

**Expected Response** (Status 404):
```json
{
  "detail": "Transcript with ID 00000000-0000-0000-0000-000000000000 not found"
}
```

#### Test 8b: Non-existent Game Session
```bash
curl -X GET "http://localhost:8000/api/v1/features/behavioral/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json"
```

**Expected Response** (Status 404):
```json
{
  "detail": "Behavioral features not found for session 00000000-0000-0000-0000-000000000000"
}
```

**What to Check**:
- ✅ Status code is 404 Not Found
- ✅ Error message is descriptive
- ✅ No server crashes

---

### Test 9: Feature Quality Validation

**Purpose**: Verify extracted features are meaningful and accurate

**Method**: Compare extracted features against known text/behavior

#### For Linguistic Features:

**Sample Text from seed_data.py**:
```
"I like to read books about dinosaurs and space."
```

**What to Validate**:
1. **Word Count**: Should be exactly 9 words
2. **Sentiment**: Should be positive (positive_sentiment > 0.5)
3. **Readability**: Should be low grade level (simple sentence)
4. **Lexical Diversity**: Should be high (all unique words except "to")
5. **POS Counts**: Should have nouns (books, dinosaurs, space), verbs (like, read)

**Validation Script**:
```bash
# Extract features and check specific values
curl -X POST "http://localhost:8000/api/v1/features/linguistic/${TRANSCRIPT_ID}" | \
  jq '{
    word_count: .features.word_count,
    positive_sentiment: .features.positive_sentiment,
    readability: .features.readability_score,
    noun_count: .features.noun_count
  }'
```

**Expected**:
- `word_count`: Should be close to actual word count (±1-2)
- `positive_sentiment`: Should be > 0.5 for positive text
- `readability_score`: Should be < 8.0 for simple text
- Feature values should be consistent across multiple extractions

#### For Behavioral Features:

**From seed_data.py** (5 word attempts, 3 correct, 2 incorrect):

**What to Validate**:
1. **Total Events**: Should be 5
2. **Task Completion Rate**: Should be ~60% (3/5)
3. **Retry Count**: Should match incorrect attempts
4. **Values in Range**: Rates should be 0-1, times should be positive

---

### Test 10: Database Storage Verification

**Purpose**: Verify features are correctly stored in PostgreSQL

**Method: Direct Database Query**

```bash
# Connect to PostgreSQL
psql -h localhost -U mass_user -d mass_db

# Check linguistic features
SELECT
  lf.id,
  lf.transcript_id,
  lf.student_id,
  lf.features_json->>'word_count' as word_count,
  lf.features_json->>'positive_sentiment' as sentiment,
  lf.created_at
FROM linguistic_features lf
ORDER BY lf.created_at DESC
LIMIT 5;

# Check behavioral features
SELECT
  bf.id,
  bf.session_id,
  bf.student_id,
  bf.features_json->>'task_completion_rate' as completion_rate,
  bf.features_json->>'total_events' as events,
  bf.created_at
FROM behavioral_features bf
ORDER BY bf.created_at DESC
LIMIT 5;
```

**What to Check**:
- ✅ Records exist in `linguistic_features` table
- ✅ Records exist in `behavioral_features` table
- ✅ `features_json` column contains valid JSON
- ✅ `transcript_id` / `session_id` match source data
- ✅ `student_id` is correctly populated
- ✅ Timestamps are accurate

---

## Getting Test IDs

### Get Transcript IDs
```bash
# List all transcripts
curl -s http://localhost:8000/api/v1/transcripts | jq -r '.[] | "\(.id) - \(.text[0:50])..."'

# Get first transcript ID
curl -s http://localhost:8000/api/v1/transcripts | jq -r '.[0].id'
```

### Get Game Session IDs
```bash
# List all game sessions
curl -s http://localhost:8000/api/v1/game-sessions | jq -r '.[] | "\(.id) - Student: \(.student_id)"'

# Get first session ID
curl -s http://localhost:8000/api/v1/game-sessions | jq -r '.[0].id'
```

### Get Student IDs
```bash
# List all students
curl -s http://localhost:8000/api/v1/students | jq -r '.[] | "\(.id) - \(.first_name) \(.last_name)"'
```

---

## Comprehensive Test Script

Save this as `test_features.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Task 10: Feature Extraction Validation${NC}"
echo "=========================================="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Get test IDs
echo "🔍 Getting test data IDs..."
TRANSCRIPT_ID=$(curl -s $BASE_URL/api/v1/transcripts | jq -r '.[0].id')
SESSION_ID=$(curl -s $BASE_URL/api/v1/game-sessions | jq -r '.[0].id')

if [ -z "$TRANSCRIPT_ID" ] || [ "$TRANSCRIPT_ID" = "null" ]; then
    echo -e "${RED}❌ No transcripts found. Run seed_data.py first.${NC}"
    exit 1
fi

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo -e "${RED}❌ No game sessions found. Run seed_data.py first.${NC}"
    exit 1
fi

echo -e "📝 Transcript ID: ${YELLOW}${TRANSCRIPT_ID}${NC}"
echo -e "🎮 Session ID: ${YELLOW}${SESSION_ID}${NC}"
echo ""

# Test 1: Extract Linguistic Features
echo -n "Test 1: Extract linguistic features... "
LING_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/features/linguistic/${TRANSCRIPT_ID}")
if echo $LING_RESPONSE | jq -e '.features.word_count' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "Response: $LING_RESPONSE"
    ((FAIL_COUNT++))
fi

# Test 2: Extract Behavioral Features
echo -n "Test 2: Extract behavioral features... "
BEH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/features/behavioral/${SESSION_ID}")
if echo $BEH_RESPONSE | jq -e '.features.total_events' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "Response: $BEH_RESPONSE"
    ((FAIL_COUNT++))
fi

# Test 3: Retrieve Linguistic Features
echo -n "Test 3: Retrieve linguistic features... "
GET_LING=$(curl -s -X GET "$BASE_URL/api/v1/features/linguistic/${TRANSCRIPT_ID}")
if echo $GET_LING | jq -e '.features.word_count' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 4: Retrieve Behavioral Features
echo -n "Test 4: Retrieve behavioral features... "
GET_BEH=$(curl -s -X GET "$BASE_URL/api/v1/features/behavioral/${SESSION_ID}")
if echo $GET_BEH | jq -e '.features.total_events' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 5: Error Handling (Non-existent ID)
echo -n "Test 5: Error handling (404)... "
ERROR_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/features/linguistic/00000000-0000-0000-0000-000000000000")
if [ "$ERROR_RESPONSE" = "404" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL (got $ERROR_RESPONSE)${NC}"
    ((FAIL_COUNT++))
fi

# Test 6: Feature Quality Check
echo -n "Test 6: Feature quality (word count > 0)... "
WORD_COUNT=$(echo $LING_RESPONSE | jq -r '.features.word_count')
if [ "$WORD_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ PASS (count: $WORD_COUNT)${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

echo ""
echo "=========================================="
echo -e "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"
echo "=========================================="

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All validation tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    exit 1
fi
```

Make it executable and run:
```bash
chmod +x test_features.sh
./test_features.sh
```

---

## Troubleshooting

### Issue: "spaCy model not found"
**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: "No transcripts found"
**Solution**: Seed the database first
```bash
cd backend
python scripts/seed_data.py --clear
```

### Issue: "Connection refused"
**Solution**: Start the API server
```bash
uvicorn app.main:app --reload
```

### Issue: "Database connection error"
**Solution**: Check PostgreSQL is running
```bash
# macOS/Linux
pg_isready

# Check connection string
echo $DATABASE_URL
```

### Issue: Features look wrong
**Possible Causes**:
1. Text is too short (< 10 words) - features may be less meaningful
2. Text is empty or null - check transcript data
3. Game session has no telemetry events - check telemetry data

---

## Success Criteria

Task 10 is successfully validated when:

- ✅ All 6 feature extraction endpoints are accessible
- ✅ Linguistic features are extracted and contain 18+ metrics
- ✅ Behavioral features are extracted and contain 12+ metrics
- ✅ Features can be retrieved after extraction
- ✅ Batch processing works for multiple items
- ✅ Error handling returns proper 404/500 responses
- ✅ Feature values are numeric and within expected ranges
- ✅ Data is correctly persisted to PostgreSQL
- ✅ No server crashes or unhandled exceptions

---

## Next Steps After Validation

Once validation is complete:

1. **Document any issues** found during testing
2. **Create unit tests** for feature extraction logic (currently at 22% coverage)
3. **Performance testing** for large batches
4. **Integration testing** with real audio transcriptions
5. **Move to Task 11**: Deploy ML Inference Models

---

## Additional Resources

- **API Documentation**: http://localhost:8000/api/v1/docs
- **Feature Extraction Service**: `/backend/app/services/feature_extraction.py`
- **API Endpoints**: `/backend/app/api/endpoints/features.py`
- **Task 10 Details**: `.taskmaster/tasks/task-10.md`
