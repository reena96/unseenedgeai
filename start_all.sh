#!/bin/bash

# Start ALL MASS Services (Backend API + All 3 Dashboards)
# Usage: ./start_all.sh

echo "🚀 Starting MASS - Middle School Non-Academic Skills Measurement System"
echo "="*70

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using defaults."
fi

echo ""
echo "📊 Step 1/4: Starting Backend API Server (Port 8080)..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload > /tmp/mass_api.log 2>&1 &
API_PID=$!
sleep 3

# Check if API started successfully
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend API running on http://localhost:8080"
    echo "   📖 API Docs: http://localhost:8080/docs"
else
    echo "   ❌ Failed to start Backend API"
    cat /tmp/mass_api.log
    exit 1
fi

echo ""
echo "🎨 Step 2/4: Starting Teacher Dashboard (Port 8501)..."
streamlit run dashboard/app_template.py --server.port=8501 --server.headless=true > /tmp/mass_teacher.log 2>&1 &
TEACHER_PID=$!
sleep 3
echo "   ✅ Teacher Dashboard running on http://localhost:8501"
echo "      Username: teacher | Password: password123"

echo ""
echo "🎨 Step 3/4: Starting Admin Dashboard (Port 8502)..."
streamlit run dashboard/admin_dashboard.py --server.port=8502 --server.headless=true > /tmp/mass_admin.log 2>&1 &
ADMIN_PID=$!
sleep 3
echo "   ✅ Admin Dashboard running on http://localhost:8502"
echo "      Username: admin | Password: admin123"

echo ""
echo "🎨 Step 4/4: Starting Student Portal (Port 8503)..."
streamlit run dashboard/student_portal.py --server.port=8503 --server.headless=true > /tmp/mass_student.log 2>&1 &
STUDENT_PID=$!
sleep 3
echo "   ✅ Student Portal running on http://localhost:8503"
echo "      Username: student123 | Password: password"

echo ""
echo "="*70
echo "✅ ALL SERVICES STARTED SUCCESSFULLY!"
echo "="*70
echo ""
echo "📊 Service Status:"
echo "   • Backend API:        http://localhost:8080 (PID: $API_PID)"
echo "   • Teacher Dashboard:  http://localhost:8501 (PID: $TEACHER_PID)"
echo "   • Admin Dashboard:    http://localhost:8502 (PID: $ADMIN_PID)"
echo "   • Student Portal:     http://localhost:8503 (PID: $STUDENT_PID)"
echo ""
echo "📝 Logs available at:"
echo "   • API:     tail -f /tmp/mass_api.log"
echo "   • Teacher: tail -f /tmp/mass_teacher.log"
echo "   • Admin:   tail -f /tmp/mass_admin.log"
echo "   • Student: tail -f /tmp/mass_student.log"
echo ""
echo "🛑 To stop all services, run: ./stop_all.sh"
echo ""
