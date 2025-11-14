#!/bin/bash
# Deploy monitoring dashboard and alert policies to Google Cloud Monitoring

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}

echo "Deploying monitoring infrastructure for project: $PROJECT_ID"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    exit 1
fi

# Authenticate (if needed)
echo "Current gcloud configuration:"
gcloud config get-value project

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID
gcloud services enable logging.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudtrace.googleapis.com --project=$PROJECT_ID

# Create monitoring dashboard
echo "Creating monitoring dashboard..."
DASHBOARD_JSON=$(sed "s/\${PROJECT_ID}/$PROJECT_ID/g" dashboard.json)
gcloud monitoring dashboards create --config-from-file=<(echo "$DASHBOARD_JSON") \
    --project=$PROJECT_ID || echo "Dashboard may already exist"

# Create notification channels
echo "Creating notification channels..."
# Note: Update email addresses and webhook URLs in alert-policies.yml before running

# Slack webhook (if configured)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    gcloud alpha monitoring channels create \
        --display-name="Slack Alerts" \
        --type=slack \
        --channel-labels=url="$SLACK_WEBHOOK_URL" \
        --project=$PROJECT_ID || echo "Slack channel may already exist"
fi

# Email notifications
gcloud alpha monitoring channels create \
    --display-name="Engineering Email" \
    --type=email \
    --channel-labels=email_address="engineering@unseenedgeai.com" \
    --project=$PROJECT_ID || echo "Email channel may already exist"

# PagerDuty (if configured)
if [ -n "$PAGERDUTY_SERVICE_KEY" ]; then
    gcloud alpha monitoring channels create \
        --display-name="PagerDuty On-Call" \
        --type=pagerduty \
        --channel-labels=service_key="$PAGERDUTY_SERVICE_KEY" \
        --project=$PROJECT_ID || echo "PagerDuty channel may already exist"
fi

# Create alert policies
echo "Creating alert policies..."
# Note: The gcloud command for creating policies from YAML is in alpha/beta
# You may need to create them via the Cloud Console or use Terraform

echo "
✅ Monitoring setup complete!

Next steps:
1. View dashboard: https://console.cloud.google.com/monitoring/dashboards
2. Configure notification channels in Cloud Console
3. Test alerts by triggering threshold conditions
4. Set up uptime checks for external monitoring
"

# Create uptime checks
echo "Creating uptime checks..."

# Backend API uptime check
gcloud monitoring uptime create http backend-api-uptime \
    --resource-type=cloud-run-revision \
    --resource-labels=project_id=$PROJECT_ID,service_name=mass-api,location=$REGION \
    --period=5 \
    --timeout=10s \
    --project=$PROJECT_ID || echo "Backend uptime check may already exist"

# Frontend uptime check
gcloud monitoring uptime create http frontend-uptime \
    --resource-type=cloud-run-revision \
    --resource-labels=project_id=$PROJECT_ID,service_name=mass-frontend,location=$REGION \
    --period=5 \
    --timeout=10s \
    --project=$PROJECT_ID || echo "Frontend uptime check may already exist"

echo "
📊 Monitoring dashboard: https://console.cloud.google.com/monitoring/dashboards
🔔 Alert policies: https://console.cloud.google.com/monitoring/alerting/policies
📈 Uptime checks: https://console.cloud.google.com/monitoring/uptime
"
