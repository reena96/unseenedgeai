#!/bin/bash

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 MASS API Test Suite${NC}"
echo "======================"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Test 1: Health Check
echo -n "Testing health endpoint... "
HEALTH=$(curl -s $BASE_URL/api/v1/health)
if echo $HEALTH | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 2: Readiness
echo -n "Testing readiness probe... "
READY=$(curl -s $BASE_URL/api/v1/readiness)
if echo $READY | grep -q "true"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 3: Liveness
echo -n "Testing liveness probe... "
LIVE=$(curl -s $BASE_URL/api/v1/liveness)
if echo $LIVE | grep -q "true"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 4: Root endpoint
echo -n "Testing root endpoint... "
ROOT=$(curl -s $BASE_URL/)
if echo $ROOT | grep -q "MASS API"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 5: Login
echo -n "Testing login... "
LOGIN=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test@example.com&password=testpassword')
if echo $LOGIN | grep -q "access_token"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 6: Swagger UI (CORRECTED PATH)
echo -n "Testing Swagger UI... "
DOCS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/docs)
if [ "$DOCS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 7: OpenAPI JSON (CORRECTED PATH)
echo -n "Testing OpenAPI JSON... "
OPENAPI=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/openapi.json)
if [ "$OPENAPI" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 8: ReDoc (CORRECTED PATH)
echo -n "Testing ReDoc... "
REDOC=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/redoc)
if [ "$REDOC" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 9: CORS Headers
echo -n "Testing CORS headers... "
CORS=$(curl -s -I $BASE_URL/api/v1/health | grep -i "access-control-allow-origin")
if [ ! -z "$CORS" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

# Test 10: Request ID Header
echo -n "Testing request ID header... "
REQ_ID=$(curl -s -I $BASE_URL/api/v1/health | grep -i "x-request-id")
if [ ! -z "$REQ_ID" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL_COUNT++))
fi

echo ""
echo "=============================="
echo -e "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"
echo "=============================="

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "   • Open http://localhost:8000/api/v1/docs in browser"
    echo "   • Try interactive API testing with Swagger UI"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    exit 1
fi
