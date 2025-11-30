#!/bin/bash
# ============================================================================
# MASS Demo Startup Script
# ============================================================================
# This script starts all services for demo without retraining models.
# Pre-trained models and sample data are already included in the repository.
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  MASS - Student Skills Assessment System"
echo "  Demo Startup Script"
echo "=============================================="
echo ""

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found. Run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Verify models exist (no training needed)
echo "[1/5] Checking pre-trained models..."
MODEL_COUNT=$(ls -1 models/*.pkl 2>/dev/null | wc -l)
if [ "$MODEL_COUNT" -lt 14 ]; then
    echo "[ERROR] Missing model files. Expected 14, found $MODEL_COUNT"
    echo "        Models should be in the 'models/' directory."
    exit 1
fi
echo "      Found $MODEL_COUNT model files (7 skills x 2 files each)"

# Check database connection
echo "[2/5] Checking database connection..."
if ! PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "[ERROR] Cannot connect to PostgreSQL database."
    echo "        Make sure PostgreSQL is running with database 'mass_db'"
    exit 1
fi
echo "      Database connection OK"

# Check existing data
echo "[3/5] Checking existing data..."
STUDENT_COUNT=$(PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -t -c "SELECT COUNT(*) FROM students" 2>/dev/null | tr -d ' ')
ASSESSMENT_COUNT=$(PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -t -c "SELECT COUNT(*) FROM skill_assessments" 2>/dev/null | tr -d ' ')
echo "      Students: $STUDENT_COUNT"
echo "      Assessments: $ASSESSMENT_COUNT"

# Start services
echo "[4/5] Starting services..."
echo ""

# Kill any existing processes on our ports
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
lsof -ti:8502 | xargs kill -9 2>/dev/null || true
lsof -ti:8503 | xargs kill -9 2>/dev/null || true

sleep 1

# Start FastAPI backend
echo "      Starting FastAPI backend on port 8080..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > logs/api.log 2>&1 &
API_PID=$!
echo "      API PID: $API_PID"

sleep 2

# Start main dashboard
echo "      Starting Main Dashboard on port 8501..."
nohup streamlit run dashboard/app_template.py --server.port=8501 --server.headless=true > logs/dashboard.log 2>&1 &
DASH_PID=$!
echo "      Dashboard PID: $DASH_PID"

# Start admin dashboard
echo "      Starting Admin Dashboard on port 8502..."
nohup streamlit run dashboard/admin_dashboard.py --server.port=8502 --server.headless=true > logs/admin.log 2>&1 &
ADMIN_PID=$!
echo "      Admin PID: $ADMIN_PID"

# Start student portal
echo "      Starting Student Portal on port 8503..."
nohup streamlit run dashboard/student_portal.py --server.port=8503 --server.headless=true > logs/student.log 2>&1 &
STUDENT_PID=$!
echo "      Student Portal PID: $STUDENT_PID"

sleep 3

# Verify services are running
echo ""
echo "[5/5] Verifying services..."
if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo "      API: OK"
else
    echo "      API: FAILED"
fi

echo ""
echo "=============================================="
echo "  Demo Ready!"
echo "=============================================="
echo ""
echo "  Access URLs:"
echo "    API:             http://localhost:8080/api/v1/health"
echo "    Main Dashboard:  http://localhost:8501"
echo "    Admin Dashboard: http://localhost:8502"
echo "    Student Portal:  http://localhost:8503"
echo ""
echo "  Pre-loaded Data:"
echo "    - $STUDENT_COUNT students"
echo "    - $ASSESSMENT_COUNT assessments"
echo "    - 7 skill models (pre-trained)"
echo ""
echo "  To stop all services: ./demo_stop.sh"
echo "=============================================="
