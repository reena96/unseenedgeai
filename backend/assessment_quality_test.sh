#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "=== AI Assessment Quality Test ==="
echo ""

# Get latest empathy assessment details
echo "Fetching latest empathy assessment..."
ASSESSMENT=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/empathy/latest")

echo ""
echo "================== ASSESSMENT DETAILS =================="
echo ""
echo "Student ID: $(echo "$ASSESSMENT" | jq -r '.student_id')"
echo "Skill Type: $(echo "$ASSESSMENT" | jq -r '.skill_type')"
echo "Score: $(echo "$ASSESSMENT" | jq -r '.score')"
echo "Confidence: $(echo "$ASSESSMENT" | jq -r '.confidence')"
echo ""
echo "--- Reasoning ---"
echo "$ASSESSMENT" | jq -r '.reasoning' | fold -w 80 -s
echo ""
echo "--- Evidence ($(echo "$ASSESSMENT" | jq -r '.evidence | length') pieces) ---"
echo "$ASSESSMENT" | jq -r '.evidence[] | "• " + .content' | fold -w 78 -s | sed 's/^/  /'
echo ""
echo "--- Recommendations ---"
echo "$ASSESSMENT" | jq -r '.recommendations' | fold -w 80 -s
echo ""
echo "--- Metadata ---"
echo "Created: $(echo "$ASSESSMENT" | jq -r '.created_at')"
echo "Reasoning length: $(echo "$ASSESSMENT" | jq -r '.reasoning | length') characters"
echo "Recommendations length: $(echo "$ASSESSMENT" | jq -r '.recommendations | length') characters"
echo ""
echo "======================================================="
