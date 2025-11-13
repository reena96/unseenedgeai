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

# Get test IDs from database
echo "🔍 Getting test data IDs from database..."
TRANSCRIPT_ID=$(python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.transcript import Transcript

async def get_id():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(Transcript).limit(1))
        transcript = result.scalar_one_or_none()
        await engine.dispose()
        return transcript.id if transcript else None

print(asyncio.run(get_id()) or '')
" 2>/dev/null)

SESSION_ID=$(python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.game_telemetry import GameSession

async def get_id():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(GameSession).limit(1))
        game_session = result.scalar_one_or_none()
        await engine.dispose()
        return game_session.id if game_session else None

print(asyncio.run(get_id()) or '')
" 2>/dev/null)

if [ -z "$TRANSCRIPT_ID" ] || [ "$TRANSCRIPT_ID" = "null" ]; then
    echo -e "${RED}❌ No transcripts found. Run 'python scripts/seed_data.py --clear' first.${NC}"
    exit 1
fi

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo -e "${RED}❌ No game sessions found. Run 'python scripts/seed_data.py --clear' first.${NC}"
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

# Test 5: Batch Linguistic Extraction
echo -n "Test 5: Batch linguistic extraction... "
TRANSCRIPT_IDS=$(curl -s $BASE_URL/api/v1/transcripts 2>/dev/null | jq -c '[.[0:3][].id]' 2>/dev/null)
if [ ! -z "$TRANSCRIPT_IDS" ] && [ "$TRANSCRIPT_IDS" != "null" ]; then
    BATCH_LING=$(curl -s -X POST "$BASE_URL/api/v1/features/batch/linguistic" \
        -H "Content-Type: application/json" \
        -d "$TRANSCRIPT_IDS")
    if echo $BATCH_LING | jq -e '.total' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS_COUNT++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL_COUNT++))
    fi
else
    echo -e "${YELLOW}⊘ SKIP (no data)${NC}"
fi

# Test 6: Batch Behavioral Extraction
echo -n "Test 6: Batch behavioral extraction... "
SESSION_IDS=$(curl -s $BASE_URL/api/v1/game-sessions 2>/dev/null | jq -c '[.[0:3][].id]' 2>/dev/null)
if [ ! -z "$SESSION_IDS" ] && [ "$SESSION_IDS" != "null" ]; then
    BATCH_BEH=$(curl -s -X POST "$BASE_URL/api/v1/features/batch/behavioral" \
        -H "Content-Type: application/json" \
        -d "$SESSION_IDS")
    if echo $BATCH_BEH | jq -e '.total' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS_COUNT++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL_COUNT++))
    fi
else
    echo -e "${YELLOW}⊘ SKIP (no data)${NC}"
fi

# Test 7: Error Handling (Non-existent ID)
echo -n "Test 7: Error handling (404)... "
ERROR_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/features/linguistic/00000000-0000-0000-0000-000000000000")
if [ "$ERROR_RESPONSE" = "404" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL (got $ERROR_RESPONSE)${NC}"
    ((FAIL_COUNT++))
fi

# Test 8: Feature Quality - Word Count
echo -n "Test 8: Feature quality (word count > 0)... "
WORD_COUNT=$(echo $LING_RESPONSE | jq -r '.features.word_count')
if [ "$WORD_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ PASS (count: $WORD_COUNT)${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 9: Feature Quality - Sentiment Range
echo -n "Test 9: Feature quality (sentiment 0-1)... "
POS_SENTIMENT=$(echo $LING_RESPONSE | jq -r '.features.positive_sentiment')
NEG_SENTIMENT=$(echo $LING_RESPONSE | jq -r '.features.negative_sentiment')
if (( $(echo "$POS_SENTIMENT >= 0 && $POS_SENTIMENT <= 1" | bc -l) )) && \
   (( $(echo "$NEG_SENTIMENT >= 0 && $NEG_SENTIMENT <= 1" | bc -l) )); then
    echo -e "${GREEN}✅ PASS (pos: $POS_SENTIMENT, neg: $NEG_SENTIMENT)${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 10: Feature Quality - Event Count
echo -n "Test 10: Feature quality (events > 0)... "
TOTAL_EVENTS=$(echo $BEH_RESPONSE | jq -r '.features.total_events')
if [ "$TOTAL_EVENTS" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ PASS (events: $TOTAL_EVENTS)${NC}"
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
    echo ""
    echo "📊 Sample Feature Summary:"
    echo ""
    echo "Linguistic Features:"
    echo $LING_RESPONSE | jq '{
        word_count: .features.word_count,
        unique_words: .features.unique_word_count,
        sentiment: {
            positive: .features.positive_sentiment,
            negative: .features.negative_sentiment
        },
        readability: .features.readability_score
    }'
    echo ""
    echo "Behavioral Features:"
    echo $BEH_RESPONSE | jq '{
        total_events: .features.total_events,
        completion_rate: .features.task_completion_rate,
        retry_count: .features.retry_count,
        focus_duration: .features.focus_duration
    }'
    echo ""
    echo "🚀 Task 10 validation complete!"
    echo "📖 See docs/TASK_10_VALIDATION_GUIDE.md for detailed testing guide"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check API server is running: http://localhost:8000"
    echo "2. Verify database is seeded: python scripts/seed_data.py --clear"
    echo "3. Check logs for errors"
    exit 1
fi
