#!/bin/bash

# Comprehensive AI Assessment Testing Script
# Tests all endpoints and edge cases

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Comprehensive AI Assessment Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test counter
PASS=0
FAIL=0

test_pass() {
    echo -e "${GREEN}✓ PASS${NC} - $1"
    ((PASS++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC} - $1"
    ((FAIL++))
}

# ==========================================
# SECTION 1: Core Assessment Creation Tests
# ==========================================
echo -e "${BLUE}SECTION 1: Core Assessment Creation${NC}"
echo ""

# Test 1.1: Create Empathy Assessment
echo -e "${YELLOW}Test 1.1: Create empathy assessment${NC}"
EMPATHY_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": false}')

EMPATHY_SCORE=$(echo "$EMPATHY_RESPONSE" | jq -r '.score' 2>/dev/null)
if [ "$EMPATHY_SCORE" != "null" ] && [ ! -z "$EMPATHY_SCORE" ]; then
    test_pass "Empathy assessment created (Score: $EMPATHY_SCORE)"
else
    test_fail "Empathy assessment failed: $(echo "$EMPATHY_RESPONSE" | jq -r '.detail // "Unknown error"')"
fi
sleep 2

# Test 1.2: Create Problem-Solving Assessment
echo -e "${YELLOW}Test 1.2: Create problem-solving assessment${NC}"
PS_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "problem_solving", "use_cached": false}')

PS_SCORE=$(echo "$PS_RESPONSE" | jq -r '.score' 2>/dev/null)
if [ "$PS_SCORE" != "null" ] && [ ! -z "$PS_SCORE" ]; then
    test_pass "Problem-solving assessment created (Score: $PS_SCORE)"
else
    test_fail "Problem-solving assessment failed"
fi
sleep 2

# Test 1.3: Create Self-Regulation Assessment
echo -e "${YELLOW}Test 1.3: Create self-regulation assessment${NC}"
SR_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "self_regulation", "use_cached": false}')

SR_SCORE=$(echo "$SR_RESPONSE" | jq -r '.score' 2>/dev/null)
if [ "$SR_SCORE" != "null" ] && [ ! -z "$SR_SCORE" ]; then
    test_pass "Self-regulation assessment created (Score: $SR_SCORE)"
else
    test_fail "Self-regulation assessment failed"
fi
sleep 2

# Test 1.4: Create Resilience Assessment
echo -e "${YELLOW}Test 1.4: Create resilience assessment${NC}"
RES_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "resilience", "use_cached": false}')

RES_SCORE=$(echo "$RES_RESPONSE" | jq -r '.score' 2>/dev/null)
if [ "$RES_SCORE" != "null" ] && [ ! -z "$RES_SCORE" ]; then
    test_pass "Resilience assessment created (Score: $RES_SCORE)"
else
    test_fail "Resilience assessment failed"
fi
sleep 2

echo ""

# ==========================================
# SECTION 2: Batch Endpoints
# ==========================================
echo -e "${BLUE}SECTION 2: Batch Endpoints${NC}"
echo ""

# Test 2.1: Create All Assessments at Once
echo -e "${YELLOW}Test 2.1: Create all assessments at once${NC}"
START_TIME=$(date +%s)
ALL_RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}/all?use_cached=false" \
    --max-time 120)
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

ASSESSMENT_COUNT=$(echo "$ALL_RESPONSE" | jq -r '.assessments | length' 2>/dev/null)
OVERALL_SCORE=$(echo "$ALL_RESPONSE" | jq -r '.overall_score' 2>/dev/null)

if [ "$ASSESSMENT_COUNT" == "4" ]; then
    test_pass "All 4 assessments created (Overall: $OVERALL_SCORE, Time: ${DURATION}s)"
else
    test_fail "All assessments failed: Expected 4, got $ASSESSMENT_COUNT"
fi

echo ""

# ==========================================
# SECTION 3: Retrieval Endpoints
# ==========================================
echo -e "${BLUE}SECTION 3: Retrieval Endpoints${NC}"
echo ""

# Test 3.1: Get All Assessments for Student
echo -e "${YELLOW}Test 3.1: Get all assessments for student${NC}"
ALL_ASSESSMENTS=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}")
ALL_COUNT=$(echo "$ALL_ASSESSMENTS" | jq -r 'length' 2>/dev/null)

if [ "$ALL_COUNT" -gt "0" ]; then
    test_pass "Retrieved $ALL_COUNT assessments"
else
    test_fail "No assessments retrieved"
fi

# Test 3.2: Filter by Skill Type
echo -e "${YELLOW}Test 3.2: Filter assessments by skill type${NC}"
FILTERED=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}?skill_type=empathy")
FILTERED_COUNT=$(echo "$FILTERED" | jq -r 'length' 2>/dev/null)

if [ "$FILTERED_COUNT" -gt "0" ]; then
    FIRST_SKILL=$(echo "$FILTERED" | jq -r '.[0].skill_type' 2>/dev/null)
    if [ "$FIRST_SKILL" == "empathy" ]; then
        test_pass "Filtered to empathy: $FILTERED_COUNT assessments"
    else
        test_fail "Filter returned wrong skill type: $FIRST_SKILL"
    fi
else
    test_fail "Filter returned no results"
fi

# Test 3.3: Get Latest Assessment for Specific Skill
echo -e "${YELLOW}Test 3.3: Get latest assessment for specific skill${NC}"
LATEST=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/empathy/latest")
LATEST_SCORE=$(echo "$LATEST" | jq -r '.score' 2>/dev/null)

if [ "$LATEST_SCORE" != "null" ] && [ ! -z "$LATEST_SCORE" ]; then
    test_pass "Latest empathy assessment retrieved (Score: $LATEST_SCORE)"
else
    test_fail "Latest assessment retrieval failed"
fi

# Test 3.4: Limit Results
echo -e "${YELLOW}Test 3.4: Limit results parameter${NC}"
LIMITED=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}?limit=2")
LIMITED_COUNT=$(echo "$LIMITED" | jq -r 'length' 2>/dev/null)

if [ "$LIMITED_COUNT" -le "2" ]; then
    test_pass "Limit parameter working (Returned: $LIMITED_COUNT)"
else
    test_fail "Limit parameter not working (Expected ≤2, got $LIMITED_COUNT)"
fi

echo ""

# ==========================================
# SECTION 4: Caching Behavior
# ==========================================
echo -e "${BLUE}SECTION 4: Caching Behavior${NC}"
echo ""

# Test 4.1: Fresh Assessment (Uncached)
echo -e "${YELLOW}Test 4.1: Fresh assessment timing${NC}"
START_MS=$(date +%s%N | cut -b1-13)
FRESH=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": false}')
END_MS=$(date +%s%N | cut -b1-13)
FRESH_TIME=$((END_MS - START_MS))

test_pass "Fresh assessment time: ${FRESH_TIME}ms"

# Test 4.2: Cached Assessment
echo -e "${YELLOW}Test 4.2: Cached assessment timing${NC}"
sleep 1
START_MS=$(date +%s%N | cut -b1-13)
CACHED=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": true}')
END_MS=$(date +%s%N | cut -b1-13)
CACHED_TIME=$((END_MS - START_MS))

if [ "$CACHED_TIME" -lt "$FRESH_TIME" ]; then
    test_pass "Cached assessment faster: ${CACHED_TIME}ms vs ${FRESH_TIME}ms"
else
    test_fail "Cached assessment not faster: ${CACHED_TIME}ms vs ${FRESH_TIME}ms"
fi

echo ""

# ==========================================
# SECTION 5: Assessment Quality Validation
# ==========================================
echo -e "${BLUE}SECTION 5: Assessment Quality Validation${NC}"
echo ""

# Get a fresh assessment for quality checks
TEST_ASSESSMENT=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": false}')

# Test 5.1: Score Range
echo -e "${YELLOW}Test 5.1: Score in valid range (0-1)${NC}"
SCORE=$(echo "$TEST_ASSESSMENT" | jq -r '.score')
if (( $(echo "$SCORE >= 0 && $SCORE <= 1" | bc -l) )); then
    test_pass "Score valid: $SCORE"
else
    test_fail "Score out of range: $SCORE"
fi

# Test 5.2: Confidence Range
echo -e "${YELLOW}Test 5.2: Confidence in valid range (0-1)${NC}"
CONFIDENCE=$(echo "$TEST_ASSESSMENT" | jq -r '.confidence')
if (( $(echo "$CONFIDENCE >= 0 && $CONFIDENCE <= 1" | bc -l) )); then
    test_pass "Confidence valid: $CONFIDENCE"
else
    test_fail "Confidence out of range: $CONFIDENCE"
fi

# Test 5.3: Reasoning Quality
echo -e "${YELLOW}Test 5.3: Reasoning quality (length > 100 chars)${NC}"
REASONING=$(echo "$TEST_ASSESSMENT" | jq -r '.reasoning')
REASONING_LENGTH=${#REASONING}
if [ "$REASONING_LENGTH" -gt 100 ]; then
    test_pass "Reasoning detailed: $REASONING_LENGTH chars"
else
    test_fail "Reasoning too short: $REASONING_LENGTH chars"
fi

# Test 5.4: Evidence Present
echo -e "${YELLOW}Test 5.4: Evidence quotes present${NC}"
EVIDENCE_COUNT=$(echo "$TEST_ASSESSMENT" | jq -r '.evidence | length')
if [ "$EVIDENCE_COUNT" -gt 0 ]; then
    test_pass "Evidence present: $EVIDENCE_COUNT pieces"
else
    test_fail "No evidence provided"
fi

# Test 5.5: Recommendations Present
echo -e "${YELLOW}Test 5.5: Recommendations present${NC}"
RECOMMENDATIONS=$(echo "$TEST_ASSESSMENT" | jq -r '.recommendations')
if [ "$RECOMMENDATIONS" != "null" ] && [ ! -z "$RECOMMENDATIONS" ] && [ "$RECOMMENDATIONS" != "" ]; then
    REC_LENGTH=${#RECOMMENDATIONS}
    test_pass "Recommendations present: $REC_LENGTH chars"
else
    test_fail "No recommendations provided"
fi

echo ""

# ==========================================
# SECTION 6: Edge Cases
# ==========================================
echo -e "${BLUE}SECTION 6: Edge Cases${NC}"
echo ""

# Test 6.1: Invalid Student ID
echo -e "${YELLOW}Test 6.1: Invalid student ID${NC}"
INVALID_STUDENT=$(curl -s -X POST "${BASE_URL}/assessments/invalid-student-id" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": false}')
ERROR_DETAIL=$(echo "$INVALID_STUDENT" | jq -r '.detail' 2>/dev/null)

if [ "$ERROR_DETAIL" != "null" ] && [ ! -z "$ERROR_DETAIL" ]; then
    test_pass "Invalid student ID rejected: $ERROR_DETAIL"
else
    test_fail "Invalid student ID not properly handled"
fi

# Test 6.2: Invalid Skill Type (in URL)
echo -e "${YELLOW}Test 6.2: Invalid skill type in URL${NC}"
INVALID_SKILL=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}?skill_type=invalid_skill")
ERROR_DETAIL=$(echo "$INVALID_SKILL" | jq -r '.detail' 2>/dev/null)

if [[ "$ERROR_DETAIL" == *"Invalid skill type"* ]]; then
    test_pass "Invalid skill type rejected"
else
    test_fail "Invalid skill type not properly handled"
fi

# Test 6.3: Invalid Skill Type (in POST body)
echo -e "${YELLOW}Test 6.3: Invalid skill type in POST body${NC}"
INVALID_POST=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "invalid_skill", "use_cached": false}')
ERROR_DETAIL=$(echo "$INVALID_POST" | jq -r '.detail' 2>/dev/null)

if [ "$ERROR_DETAIL" != "null" ] && [ ! -z "$ERROR_DETAIL" ]; then
    test_pass "Invalid POST skill type rejected"
else
    test_fail "Invalid POST skill type not properly handled"
fi

# Test 6.4: Nonexistent Latest Assessment
echo -e "${YELLOW}Test 6.4: Latest assessment for nonexistent student${NC}"
NO_ASSESSMENT=$(curl -s "${BASE_URL}/assessments/nonexistent-id/empathy/latest")
ERROR_DETAIL=$(echo "$NO_ASSESSMENT" | jq -r '.detail' 2>/dev/null)

if [[ "$ERROR_DETAIL" == *"not found"* ]] || [[ "$ERROR_DETAIL" == *"No"* ]]; then
    test_pass "Nonexistent assessment properly handled"
else
    test_fail "Nonexistent assessment not properly handled"
fi

echo ""

# ==========================================
# Final Summary
# ==========================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
TOTAL=$((PASS + FAIL))
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
