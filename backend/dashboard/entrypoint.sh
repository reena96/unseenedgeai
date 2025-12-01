#!/bin/bash
# Entrypoint script for Streamlit dashboards
# Handles PORT environment variable expansion

APP="${DASHBOARD_APP:-app_template.py}"
PORT_NUM="${PORT:-8501}"

echo "Starting Streamlit with app: $APP on port: $PORT_NUM"

exec streamlit run "$APP" --server.port="$PORT_NUM" --server.address=0.0.0.0
