#!/bin/bash

# Start the MASS Backend API Server
# Usage: ./start_server.sh [dev|prod]

MODE=${1:-dev}  # Default to dev mode

echo "🚀 Starting MASS Backend API Server in $MODE mode..."

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

# Start server based on mode
if [ "$MODE" = "prod" ]; then
    echo "📊 Starting in PRODUCTION mode (no auto-reload, 4 workers)..."
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
elif [ "$MODE" = "dev" ]; then
    echo "🔧 Starting in DEVELOPMENT mode (auto-reload enabled)..."
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
else
    echo "❌ Unknown mode: $MODE"
    echo "Usage: ./start_server.sh [dev|prod]"
    exit 1
fi
