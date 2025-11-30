#!/bin/bash
# Stop all MASS demo services

echo "Stopping MASS demo services..."

lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "  Stopped API (8080)" || echo "  API not running"
lsof -ti:8501 | xargs kill -9 2>/dev/null && echo "  Stopped Dashboard (8501)" || echo "  Dashboard not running"
lsof -ti:8502 | xargs kill -9 2>/dev/null && echo "  Stopped Admin (8502)" || echo "  Admin not running"
lsof -ti:8503 | xargs kill -9 2>/dev/null && echo "  Stopped Student Portal (8503)" || echo "  Student Portal not running"

echo "All services stopped."
