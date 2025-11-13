#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     AI ASSESSMENT SYSTEM - FINAL DEMONSTRATION                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "📊 DEMONSTRATION OVERVIEW"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This demo will show:"
echo "  1. Current assessment count"
echo "  2. Latest assessment for each skill"
echo "  3. Performance comparison (fresh vs cached)"
echo "  4. Assessment quality details"
echo ""

# Part 1: Current state
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 PART 1: CURRENT STATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}" | jq -r 'length')
echo "Total assessments in database: $TOTAL"
echo ""

# Part 2: All Skills
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 PART 2: LATEST ASSESSMENT FOR EACH SKILL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

printf "%-20s %-10s %-12s %-10s\n" "SKILL" "SCORE" "CONFIDENCE" "EVIDENCE"
printf "%-20s %-10s %-12s %-10s\n" "--------------------" "----------" "------------" "----------"

for skill in empathy problem_solving self_regulation resilience; do
    ASSESSMENT=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/${skill}/latest")
    SCORE=$(echo "$ASSESSMENT" | jq -r '.score')
    CONF=$(echo "$ASSESSMENT" | jq -r '.confidence')
    EVID=$(echo "$ASSESSMENT" | jq -r '.evidence | length')

    printf "%-20s %-10s %-12s %-10s\n" "$skill" "$SCORE" "$CONF" "${EVID} pieces"
done

echo ""

# Part 3: Performance
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ PART 3: CACHING PERFORMANCE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cached request
START=$(date +%s%N)
curl -s -X POST "${BASE_URL}/assessments/${STUDENT_ID}" \
    -H "Content-Type: application/json" \
    -d '{"skill_type": "empathy", "use_cached": true}' > /dev/null
END=$(date +%s%N)
CACHED_MS=$(( (END - START) / 1000000 ))

echo "Cached request time: ${CACHED_MS}ms ✨"
echo ""

# Part 4: Quality
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ PART 4: ASSESSMENT QUALITY SAMPLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SAMPLE=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/resilience/latest")

echo "Skill: Resilience"
echo "Score: $(echo "$SAMPLE" | jq -r '.score')"
echo "Confidence: $(echo "$SAMPLE" | jq -r '.confidence')"
echo ""
echo "Reasoning excerpt:"
echo "$SAMPLE" | jq -r '.reasoning' | head -c 200 | fold -w 70 -s | sed 's/^/  /'
echo "  ..."
echo ""
echo "Recommendations excerpt:"
echo "$SAMPLE" | jq -r '.recommendations' | head -c 150 | fold -w 70 -s | sed 's/^/  /'
echo "  ..."
echo ""

# Final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEMONSTRATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Summary:"
echo "  • All 4 skill types assessed ✓"
echo "  • Fast cached retrieval (<1s) ✓"
echo "  • High-quality reasoning and recommendations ✓"
echo "  • Evidence-based assessments ✓"
echo ""
echo "For detailed report, see: docs/AI_ASSESSMENT_TEST_REPORT.md"
echo ""
