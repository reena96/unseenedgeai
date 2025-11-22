#!/bin/bash

# Stop ALL MASS Services
# Usage: ./stop_all.sh

echo "🛑 Stopping MASS - All Services..."
echo "="*70

# Stop Backend API
echo "📊 Stopping Backend API Server..."
PIDS=$(ps aux | grep '[u]vicorn app.main:app' | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill
    echo "   ✅ Backend API stopped"
else
    echo "   ℹ️  Backend API not running"
fi

# Stop Teacher Dashboard
echo "🎨 Stopping Teacher Dashboard..."
PIDS=$(ps aux | grep '[s]treamlit run dashboard/app_template.py' | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill
    echo "   ✅ Teacher Dashboard stopped"
else
    echo "   ℹ️  Teacher Dashboard not running"
fi

# Stop Admin Dashboard
echo "🎨 Stopping Admin Dashboard..."
PIDS=$(ps aux | grep '[s]treamlit run dashboard/admin_dashboard.py' | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill
    echo "   ✅ Admin Dashboard stopped"
else
    echo "   ℹ️  Admin Dashboard not running"
fi

# Stop Student Portal
echo "🎨 Stopping Student Portal..."
PIDS=$(ps aux | grep '[s]treamlit run dashboard/student_portal.py' | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill
    echo "   ✅ Student Portal stopped"
else
    echo "   ℹ️  Student Portal not running"
fi

echo ""
echo "="*70
echo "✅ ALL SERVICES STOPPED!"
echo "="*70
