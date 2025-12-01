FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all dashboard files
COPY *.py ./

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port (Railway uses $PORT)
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Use entrypoint script for proper variable expansion
# Set DASHBOARD_APP env var in Railway for different dashboards:
#   teacher-dashboard: (leave empty - defaults to app_template.py)
#   admin-dashboard: admin_dashboard.py
#   student-portal: student_portal.py
ENTRYPOINT ["/entrypoint.sh"]
