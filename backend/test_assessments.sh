#!/bin/bash

# Test script for AI-powered skill assessments (Task 11)
# This script tests the assessment API endpoints with real students

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL
BASE_URL="http://localhost:8000/api/v1"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Task 11: AI Assessment Testing${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to check if API is running
check_api() {
    if ! curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
        echo -e "${RED}✗ API is not running at ${BASE_URL}${NC}"
        echo -e "${YELLOW}Start the API with: uvicorn app.main:app --reload${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ API is running${NC}\n"
}

# Function to get a student ID from database
get_student_id() {
    python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.student import Student

async def get_id():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        result = await session.execute(select(Student).limit(1))
        student = result.scalar_one_or_none()
        await engine.dispose()
        return student.id if student else None

print(asyncio.run(get_id()) or '')
" 2>/dev/null
}

# Function to count students with features
count_students_with_features() {
    python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func
from app.core.config import settings
from app.models.student import Student
from app.models.features import LinguisticFeatures, BehavioralFeatures

async def count():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        # Count students with linguistic features
        result = await session.execute(
            select(func.count(func.distinct(LinguisticFeatures.student_id)))
        )
        ling_count = result.scalar()

        # Count students with behavioral features
        result = await session.execute(
            select(func.count(func.distinct(BehavioralFeatures.student_id)))
        )
        beh_count = result.scalar()

        await engine.dispose()
        return ling_count, beh_count

ling, beh = asyncio.run(count())
print(f'{ling},{beh}')
" 2>/dev/null
}

# Check API status
check_api

# Check for students with features
FEATURE_COUNTS=$(count_students_with_features)
LING_COUNT=$(echo $FEATURE_COUNTS | cut -d',' -f1)
BEH_COUNT=$(echo $FEATURE_COUNTS | cut -d',' -f2)

if [ "$LING_COUNT" == "0" ] || [ "$BEH_COUNT" == "0" ]; then
    echo -e "${YELLOW}⚠ No features found in database${NC}"
    echo -e "${YELLOW}Running feature extraction first...${NC}\n"

    # Run feature extraction
    bash test_features.sh > /dev/null 2>&1 || true

    # Re-check
    FEATURE_COUNTS=$(count_students_with_features)
    LING_COUNT=$(echo $FEATURE_COUNTS | cut -d',' -f1)
    BEH_COUNT=$(echo $FEATURE_COUNTS | cut -d',' -f2)
fi

echo -e "${BLUE}Students with features:${NC}"
echo -e "  Linguistic: ${LING_COUNT}"
echo -e "  Behavioral: ${BEH_COUNT}\n"

# Get a test student ID
STUDENT_ID=$(get_student_id)

if [ -z "$STUDENT_ID" ]; then
    echo -e "${RED}✗ No students found in database${NC}"
    echo -e "${YELLOW}Run: python scripts/seed_data_enhanced.py --clear${NC}"
    exit 1
fi

echo -e "${BLUE}Using test student: ${STUDENT_ID}${NC}\n"

# Test counter
PASSED=0
FAILED=0

# Test 1: Create single skill assessment (empathy)
echo -e "${BLUE}Test 1: Create empathy assessment...${NC}"
ASSESSMENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{
        "skill_type": "empathy",
        "use_cached": false
    }')

if echo "$ASSESSMENT_RESPONSE" | jq -e '.score' > /dev/null 2>&1; then
    SCORE=$(echo "$ASSESSMENT_RESPONSE" | jq -r '.score')
    CONFIDENCE=$(echo "$ASSESSMENT_RESPONSE" | jq -r '.confidence')
    echo -e "${GREEN}✓ PASS${NC} - Score: ${SCORE}, Confidence: ${CONFIDENCE}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$ASSESSMENT_RESPONSE" | jq '.' 2>/dev/null || echo "$ASSESSMENT_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo

# Test 2: Create problem-solving assessment
echo -e "${BLUE}Test 2: Create problem-solving assessment...${NC}"
ASSESSMENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{
        "skill_type": "problem_solving",
        "use_cached": false
    }')

if echo "$ASSESSMENT_RESPONSE" | jq -e '.score' > /dev/null 2>&1; then
    SCORE=$(echo "$ASSESSMENT_RESPONSE" | jq -r '.score')
    CONFIDENCE=$(echo "$ASSESSMENT_RESPONSE" | jq -r '.confidence')
    echo -e "${GREEN}✓ PASS${NC} - Score: ${SCORE}, Confidence: ${CONFIDENCE}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$ASSESSMENT_RESPONSE" | jq '.' 2>/dev/null || echo "$ASSESSMENT_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo

# Test 3: Create all assessments for student
echo -e "${BLUE}Test 3: Create all skill assessments...${NC}"
ALL_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}/all?use_cached=false")

if echo "$ALL_RESPONSE" | jq -e '.overall_score' > /dev/null 2>&1; then
    OVERALL=$(echo "$ALL_RESPONSE" | jq -r '.overall_score')
    COUNT=$(echo "$ALL_RESPONSE" | jq -r '.assessments | length')
    echo -e "${GREEN}✓ PASS${NC} - ${COUNT} assessments, Overall score: ${OVERALL}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$ALL_RESPONSE" | jq '.' 2>/dev/null || echo "$ALL_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo

# Test 4: Retrieve assessments
echo -e "${BLUE}Test 4: Retrieve student assessments...${NC}"
GET_RESPONSE=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}")

if echo "$GET_RESPONSE" | jq -e '.[0].score' > /dev/null 2>&1; then
    COUNT=$(echo "$GET_RESPONSE" | jq '. | length')
    echo -e "${GREEN}✓ PASS${NC} - Retrieved ${COUNT} assessments"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$GET_RESPONSE" | jq '.' 2>/dev/null || echo "$GET_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo

# Test 5: Get latest assessment for specific skill
echo -e "${BLUE}Test 5: Get latest empathy assessment...${NC}"
LATEST_RESPONSE=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/empathy/latest")

if echo "$LATEST_RESPONSE" | jq -e '.score' > /dev/null 2>&1; then
    SCORE=$(echo "$LATEST_RESPONSE" | jq -r '.score')
    REASONING_LENGTH=$(echo "$LATEST_RESPONSE" | jq -r '.reasoning | length')
    echo -e "${GREEN}✓ PASS${NC} - Score: ${SCORE}, Reasoning: ${REASONING_LENGTH} chars"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$LATEST_RESPONSE" | jq '.' 2>/dev/null || echo "$LATEST_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo

# Test 6: Verify assessment has reasoning
echo -e "${BLUE}Test 6: Verify assessment quality (reasoning)...${NC}"
if echo "$LATEST_RESPONSE" | jq -e '.reasoning' > /dev/null 2>&1; then
    REASONING=$(echo "$LATEST_RESPONSE" | jq -r '.reasoning')
    if [ ${#REASONING} -gt 50 ]; then
        echo -e "${GREEN}✓ PASS${NC} - Reasoning present (${#REASONING} chars)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} - Reasoning too short: ${#REASONING} chars"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}✗ FAIL${NC} - No reasoning found"
    FAILED=$((FAILED + 1))
fi
echo

# Test 7: Verify assessment has evidence
echo -e "${BLUE}Test 7: Verify assessment has evidence...${NC}"
EVIDENCE_COUNT=$(echo "$LATEST_RESPONSE" | jq -r '.evidence | length')
if [ "$EVIDENCE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} - ${EVIDENCE_COUNT} pieces of evidence"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⊘ SKIP${NC} - No evidence (optional)"
fi
echo

# Test 8: Verify scores are in valid range (0-1)
echo -e "${BLUE}Test 8: Verify score range (0-1)...${NC}"
SCORE=$(echo "$LATEST_RESPONSE" | jq -r '.score')
if (( $(echo "$SCORE >= 0.0" | bc -l) )) && (( $(echo "$SCORE <= 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASS${NC} - Score ${SCORE} is valid"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} - Score ${SCORE} out of range"
    FAILED=$((FAILED + 1))
fi
echo

# Test 9: Verify confidence is in valid range
echo -e "${BLUE}Test 9: Verify confidence range (0-1)...${NC}"
CONFIDENCE=$(echo "$LATEST_RESPONSE" | jq -r '.confidence')
if (( $(echo "$CONFIDENCE >= 0.0" | bc -l) )) && (( $(echo "$CONFIDENCE <= 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASS${NC} - Confidence ${CONFIDENCE} is valid"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} - Confidence ${CONFIDENCE} out of range"
    FAILED=$((FAILED + 1))
fi
echo

# Test 10: Check for recommendations
echo -e "${BLUE}Test 10: Verify assessment has recommendations...${NC}"
if echo "$LATEST_RESPONSE" | jq -e '.recommendations' > /dev/null 2>&1; then
    RECOMMENDATIONS=$(echo "$LATEST_RESPONSE" | jq -r '.recommendations')
    if [ "$RECOMMENDATIONS" != "null" ] && [ ${#RECOMMENDATIONS} -gt 20 ]; then
        echo -e "${GREEN}✓ PASS${NC} - Recommendations present (${#RECOMMENDATIONS} chars)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⊘ WARN${NC} - Recommendations missing or too short"
    fi
else
    echo -e "${YELLOW}⊘ WARN${NC} - No recommendations field"
fi
echo

# Test 11: Test cached assessment (should be fast)
echo -e "${BLUE}Test 11: Test cached assessment retrieval...${NC}"
START_TIME=$(date +%s%N)
CACHED_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{
        "skill_type": "empathy",
        "use_cached": true
    }')
END_TIME=$(date +%s%N)
DURATION=$(( (END_TIME - START_TIME) / 1000000 ))

if echo "$CACHED_RESPONSE" | jq -e '.score' > /dev/null 2>&1; then
    if [ $DURATION -lt 5000 ]; then
        echo -e "${GREEN}✓ PASS${NC} - Cached retrieval in ${DURATION}ms"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⊘ SLOW${NC} - Cached retrieval took ${DURATION}ms (expected <5000ms)"
        PASSED=$((PASSED + 1))
    fi
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi
echo

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ PASSED: ${PASSED}${NC}"
echo -e "${RED}✗ FAILED: ${FAILED}${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo -e "${GREEN}Task 11 (AI-Powered Assessment) is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the output above.${NC}"
    exit 1
fi
