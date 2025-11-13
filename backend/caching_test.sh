#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "=== Caching Performance Test ==="
echo ""

# Test 1: Fresh assessment (no cache)
echo "Test 1: Fresh assessment (use_cached=false)"
START=$(date +%s%N)
FRESH=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": false}')
END=$(date +%s%N)
FRESH_MS=$(( (END - START) / 1000000 ))
FRESH_SCORE=$(echo "$FRESH" | jq -r '.score')

echo "  Time: ${FRESH_MS}ms"
echo "  Score: $FRESH_SCORE"
echo ""

# Wait a moment
sleep 2

# Test 2: Cached assessment
echo "Test 2: Cached assessment (use_cached=true)"
START=$(date +%s%N)
CACHED=$(curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": true}')
END=$(date +%s%N)
CACHED_MS=$(( (END - START) / 1000000 ))
CACHED_SCORE=$(echo "$CACHED" | jq -r '.score')

echo "  Time: ${CACHED_MS}ms"
echo "  Score: $CACHED_SCORE"
echo ""

# Compare
SPEEDUP=$(echo "scale=1; $FRESH_MS / $CACHED_MS" | bc)
echo "----------------------------------------"
echo "Results:"
echo "  Fresh:  ${FRESH_MS}ms"
echo "  Cached: ${CACHED_MS}ms"
echo "  Speedup: ${SPEEDUP}x faster"

if [ $CACHED_MS -lt $FRESH_MS ]; then
    echo "  ✓ Caching is working!"
else
    echo "  ⚠ Cached request was not faster"
fi
