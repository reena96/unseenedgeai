#!/bin/bash

# Stop the MASS Backend API Server

echo "🛑 Stopping MASS Backend API Server..."

# Find and kill uvicorn processes
PIDS=$(ps aux | grep '[u]vicorn app.main:app' | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ No running server found."
else
    echo "Found running server(s) with PID(s): $PIDS"
    echo "$PIDS" | xargs kill
    echo "✅ Server stopped successfully!"
fi
