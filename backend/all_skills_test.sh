#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
STUDENT_ID="31036060-258f-4fb9-9039-44f6a18bba24"

echo "=== All Skills Assessment Test ==="
echo ""

for skill in empathy problem_solving self_regulation resilience; do
    echo "----------------------------------------"
    echo "SKILL: $skill"
    echo "----------------------------------------"

    ASSESSMENT=$(curl -s "${BASE_URL}/assessments/${STUDENT_ID}/${skill}/latest" 2>/dev/null)

    SCORE=$(echo "$ASSESSMENT" | jq -r '.score' 2>/dev/null)
    if [ "$SCORE" != "null" ] && [ ! -z "$SCORE" ]; then
        echo "✓ Score: $SCORE"
        echo "✓ Confidence: $(echo "$ASSESSMENT" | jq -r '.confidence')"
        echo "✓ Evidence pieces: $(echo "$ASSESSMENT" | jq -r '.evidence | length')"
        echo "✓ Reasoning length: $(echo "$ASSESSMENT" | jq -r '.reasoning | length') chars"
        echo ""
        echo "Key insight:"
        echo "$ASSESSMENT" | jq -r '.reasoning' | head -c 150 | fold -w 70 -s | sed 's/^/  /'
        echo "..."
    else
        echo "✗ No assessment found"
    fi
    echo ""
done
