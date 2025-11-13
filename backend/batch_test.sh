#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "=== Batch Assessment Test ==="
echo ""

echo "Creating all 4 assessments at once..."
START=$(date +%s)

RESPONSE=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}/all?use_cached=false" \
    --max-time 120)

END=$(date +%s)
DURATION=$((END - START))

echo ""
echo "Time taken: ${DURATION} seconds"
echo ""

# Parse response
ASSESSMENT_COUNT=$(echo "$RESPONSE" | jq -r '.assessments | length' 2>/dev/null)
OVERALL_SCORE=$(echo "$RESPONSE" | jq -r '.overall_score' 2>/dev/null)

if [ "$ASSESSMENT_COUNT" == "4" ]; then
    echo "✓ Successfully created all 4 assessments"
    echo "  Overall Score: $OVERALL_SCORE"
    echo ""
    echo "Individual Scores:"
    echo "$RESPONSE" | jq -r '.assessments[] | "  • \(.skill_type): \(.score) (confidence: \(.confidence))"'
else
    echo "✗ Failed: Expected 4 assessments, got $ASSESSMENT_COUNT"
    echo "Error: $(echo "$RESPONSE" | jq -r '.detail // "Unknown error"')"
fi
