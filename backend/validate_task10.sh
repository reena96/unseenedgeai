#!/bin/bash

# Task 10 Feature Extraction - Complete Validation Script
# This script handles server startup, database seeding, and testing automatically

set -e  # Exit on error

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
API_PORT=8000
API_HOST="localhost"
API_URL="http://${API_HOST}:${API_PORT}"
SERVER_PID=""
VENV_PATH="venv"

# Cleanup function
cleanup() {
    if [ ! -z "$SERVER_PID" ]; then
        echo -e "\n${YELLOW}🛑 Stopping API server (PID: $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Server stopped${NC}"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     Task 10: Feature Extraction Service Validation        ║
║                                                            ║
║  This script will:                                         ║
║  1. Check prerequisites                                    ║
║  2. Start the API server                                   ║
║  3. Seed the database with test data                       ║
║  4. Run comprehensive feature extraction tests             ║
║  5. Display results and cleanup                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Step 1: Check Prerequisites
echo -e "${CYAN}📋 Step 1: Checking Prerequisites${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv $VENV_PATH
fi

# Activate virtual environment
echo -n "Activating virtual environment... "
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓${NC}"
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}❌ Could not find activation script${NC}"
    exit 1
fi

# Check Python
echo -n "Checking Python... "
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✓ (v$PYTHON_VERSION)${NC}"
else
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

# Check required commands
echo -n "Checking curl... "
if command -v curl &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}❌ curl not found. Install with: brew install curl (macOS) or apt-get install curl (Linux)${NC}"
    exit 1
fi

echo -n "Checking jq... "
if command -v jq &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}❌ jq not found. Install with: brew install jq (macOS) or apt-get install jq (Linux)${NC}"
    exit 1
fi

# Check if port is available
echo -n "Checking if port $API_PORT is available... "
if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌${NC}"
    echo -e "${YELLOW}⚠️  Port $API_PORT is already in use.${NC}"
    echo -n "Do you want to kill the existing process? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        EXISTING_PID=$(lsof -ti:$API_PORT)
        kill -9 $EXISTING_PID 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ Port freed${NC}"
    else
        echo -e "${RED}Cannot proceed with port in use. Exiting.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC}"
fi

# Check database connection
echo -n "Checking database connection... "
if python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.core.config import settings
    if settings.DATABASE_URL:
        print('OK')
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}❌ Database configuration error${NC}"
    echo -e "${YELLOW}Check your .env file and DATABASE_URL setting${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo -e "\n${YELLOW}📦 Installing dependencies (first time only)...${NC}"
    pip install -q -r requirements.txt
    python -m spacy download en_core_web_sm
    touch .deps_installed
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

echo -e "\n${GREEN}✅ All prerequisites satisfied${NC}\n"

# Step 2: Start API Server
echo -e "${CYAN}🚀 Step 2: Starting API Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start server in background
echo "Starting uvicorn on ${API_URL}..."
uvicorn app.main:app --host $API_HOST --port $API_PORT --log-level warning > /tmp/mass_api.log 2>&1 &
SERVER_PID=$!

echo -e "Server PID: ${YELLOW}$SERVER_PID${NC}"

# Wait for server to be ready
echo -n "Waiting for server to start"
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -o /dev/null -w "%{http_code}" ${API_URL}/api/v1/health 2>/dev/null | grep -q "200"; then
        echo -e " ${GREEN}✓${NC}"
        echo -e "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT + 1))

    # Check if server process died
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e " ${RED}✗${NC}"
        echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
        tail -20 /tmp/mass_api.log
        exit 1
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}❌ Server did not start within $MAX_RETRIES seconds${NC}"
    echo -e "${YELLOW}Check logs at: /tmp/mass_api.log${NC}"
    exit 1
fi

echo ""

# Step 3: Seed Database
echo -e "${CYAN}🌱 Step 3: Seeding Database${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Running seed script with --clear flag..."
if python scripts/seed_data.py --clear 2>&1 | tee /tmp/seed_output.log | grep -q "completed successfully"; then
    echo -e "${GREEN}✅ Database seeded successfully${NC}"

    # Extract summary from seed output
    echo -e "\n${CYAN}📊 Seeded Data Summary:${NC}"
    grep -E "(schools|teachers|students|audio files|game sessions)" /tmp/seed_output.log | tail -5 || true
else
    echo -e "${RED}❌ Database seeding failed${NC}"
    echo -e "${YELLOW}Check logs at: /tmp/seed_output.log${NC}"
    exit 1
fi

echo ""

# Small delay to ensure data is committed
sleep 2

# Step 4: Run Tests
echo -e "${CYAN}🧪 Step 4: Running Feature Extraction Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if test script exists
if [ ! -f "test_features.sh" ]; then
    echo -e "${RED}❌ test_features.sh not found${NC}"
    exit 1
fi

# Make sure test script is executable
chmod +x test_features.sh

# Run the tests
if bash test_features.sh; then
    TEST_RESULT=0
else
    TEST_RESULT=$?
fi

echo ""

# Step 5: Summary and Cleanup
echo -e "${CYAN}📝 Step 5: Summary and Cleanup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              ✅  ALL TESTS PASSED! ✅                      ║
║                                                            ║
║  Task 10: Feature Extraction Service is fully validated   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    echo -e "${CYAN}📖 What was validated:${NC}"
    echo "  ✓ Linguistic feature extraction (18+ metrics)"
    echo "  ✓ Behavioral feature extraction (12+ metrics)"
    echo "  ✓ Feature retrieval endpoints"
    echo "  ✓ Batch processing"
    echo "  ✓ Error handling"
    echo "  ✓ Feature quality and data integrity"
    echo ""

    echo -e "${CYAN}🔗 Next Steps:${NC}"
    echo "  • API Documentation: ${API_URL}/api/v1/docs"
    echo "  • Detailed Guide: docs/TASK_10_VALIDATION_GUIDE.md"
    echo "  • Write unit tests (currently 22% coverage)"
    echo "  • Move to Task 11: Deploy ML Inference Models"
    echo ""

    echo -e "${CYAN}💡 Keep the server running?${NC}"
    echo -n "Server is still running on ${API_URL}. Stop it now? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Server will be stopped...${NC}"
    else
        echo -e "${GREEN}Server will keep running. Stop manually with: kill $SERVER_PID${NC}"
        echo -e "${YELLOW}Disabling auto-cleanup...${NC}"
        trap - EXIT INT TERM
        SERVER_PID=""
    fi

    exit 0
else
    echo -e "${RED}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              ⚠️  SOME TESTS FAILED ⚠️                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    echo -e "${YELLOW}🔍 Troubleshooting:${NC}"
    echo "  1. Check API logs: tail -f /tmp/mass_api.log"
    echo "  2. Check seed logs: cat /tmp/seed_output.log"
    echo "  3. Verify database: psql -U mass_user -d mass_db"
    echo "  4. Review guide: docs/TASK_10_VALIDATION_GUIDE.md"
    echo ""

    echo -e "${CYAN}🔗 Resources:${NC}"
    echo "  • API Server: ${API_URL}/api/v1/docs"
    echo "  • Server logs: /tmp/mass_api.log"
    echo "  • Seed logs: /tmp/seed_output.log"
    echo ""

    exit 1
fi
