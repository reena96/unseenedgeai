#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "=== Quick Test Results ==="
echo ""

# Test 1: Get existing assessments
echo "1. Existing assessments:"
curl -s "${BASE_URL}/assessments/${STUDENT_ID}" | jq -r 'length as $count | "   Found: \($count) assessments"'

# Test 2: Get latest empathy
echo ""
echo "2. Latest empathy assessment:"
curl -s "${BASE_URL}/assessments/${STUDENT_ID}/empathy/latest" | jq -r '"   Score: \(.score), Confidence: \(.confidence)"'

# Test 3: Invalid student
echo ""
echo "3. Invalid student ID test:"
curl -s -X POST "${BASE_URL}/assessments/invalid-id" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy"}' | jq -r '.detail' | head -c 80

# Test 4: Invalid skill type
echo ""
echo ""
echo "4. Invalid skill type test:"
curl -s "${BASE_URL}/assessments/${STUDENT_ID}?skill_type=invalid" | jq -r '.detail'

echo ""
