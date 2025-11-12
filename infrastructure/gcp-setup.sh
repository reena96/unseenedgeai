#!/bin/bash
# GCP Project Setup Script for MASS (Middle School Non-Academic Skills Measurement System)
# This script sets up the GCP project with all required services and configurations

set -e  # Exit on error

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-unseenedgeai}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID:-}"  # Set this to your billing account ID

echo "=== MASS GCP Project Setup ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo "Step 1: Setting active project..."
gcloud config set project "$PROJECT_ID"

# Enable billing (requires billing account ID)
if [ -n "$BILLING_ACCOUNT_ID" ]; then
    echo "Step 2: Linking billing account..."
    gcloud beta billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT_ID"
else
    echo "Step 2: Skipping billing setup (BILLING_ACCOUNT_ID not set)"
    echo "  You'll need to manually link a billing account in the GCP Console"
fi

# Enable required APIs
echo "Step 3: Enabling required GCP APIs..."
gcloud services enable \
    cloudrun.googleapis.com \
    sqladmin.googleapis.com \
    storage-api.googleapis.com \
    storage-component.googleapis.com \
    speech.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    servicenetworking.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    cloudscheduler.googleapis.com

echo "Waiting for APIs to be fully enabled..."
sleep 10

# Create service account for the application
echo "Step 4: Creating service account..."
SERVICE_ACCOUNT_NAME="mass-app-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &> /dev/null; then
    echo "  Service account already exists: $SERVICE_ACCOUNT_EMAIL"
else
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="MASS Application Service Account" \
        --description="Service account for the MASS application backend"
    echo "  Created service account: $SERVICE_ACCOUNT_EMAIL"
fi

# Grant necessary IAM roles to the service account
echo "Step 5: Granting IAM roles to service account..."
ROLES=(
    "roles/cloudsql.client"
    "roles/storage.objectAdmin"
    "roles/speech.client"
    "roles/aiplatform.user"
    "roles/logging.logWriter"
    "roles/monitoring.metricWriter"
    "roles/secretmanager.secretAccessor"
    "roles/redis.editor"
)

for role in "${ROLES[@]}"; do
    echo "  Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --condition=None \
        > /dev/null
done

# Create Cloud Storage bucket for audio files and artifacts
echo "Step 6: Creating Cloud Storage buckets..."
AUDIO_BUCKET="${PROJECT_ID}-audio-files"
ARTIFACTS_BUCKET="${PROJECT_ID}-artifacts"

for bucket in "$AUDIO_BUCKET" "$ARTIFACTS_BUCKET"; do
    if gsutil ls "gs://$bucket" &> /dev/null; then
        echo "  Bucket already exists: gs://$bucket"
    else
        gsutil mb -l "$REGION" "gs://$bucket"
        gsutil uniformbucketlevelaccess set on "gs://$bucket"
        echo "  Created bucket: gs://$bucket"
    fi
done

# Set up Secret Manager secrets (placeholders)
echo "Step 7: Setting up Secret Manager..."
SECRETS=(
    "anthropic-api-key"
    "openai-api-key"
    "perplexity-api-key"
    "jwt-secret-key"
    "database-password"
)

for secret in "${SECRETS[@]}"; do
    if gcloud secrets describe "$secret" &> /dev/null; then
        echo "  Secret already exists: $secret"
    else
        echo "placeholder-value" | gcloud secrets create "$secret" \
            --data-file=- \
            --replication-policy="automatic"
        echo "  Created secret: $secret (with placeholder value)"
        echo "    ⚠️  UPDATE THIS SECRET with the actual value!"
    fi
done

# Set project quotas (informational - requires manual setup)
echo "Step 8: Quota Configuration..."
echo "  ⚠️  The following quotas should be verified/increased in GCP Console:"
echo "    - Cloud Run: Max instances per service: 100"
echo "    - Cloud SQL: Max connections: 1000"
echo "    - Cloud Storage: Operations per second: Default should suffice"
echo "    - Speech-to-Text: Requests per minute: 1000+"
echo "    Visit: https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"

# Create service account key for local development
echo "Step 9: Creating service account key for local development..."
KEY_FILE="../secrets/${SERVICE_ACCOUNT_NAME}-key.json"
mkdir -p ../secrets
if [ -f "$KEY_FILE" ]; then
    echo "  Service account key already exists: $KEY_FILE"
else
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account="$SERVICE_ACCOUNT_EMAIL"
    echo "  Created service account key: $KEY_FILE"
    echo "  ⚠️  Keep this file secure and never commit it to git!"
fi

echo ""
echo "=== GCP Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update Secret Manager secrets with actual API keys:"
echo "   gcloud secrets versions add <secret-name> --data-file=<path>"
echo ""
echo "2. Update .env file with GCP project configuration"
echo ""
echo "3. Verify quotas and increase if needed:"
echo "   https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"
echo ""
echo "4. Create Cloud SQL instance (see infrastructure/cloudsql-setup.sh)"
echo ""
echo "5. Set up Redis instance (see infrastructure/redis-setup.sh)"
echo ""
echo "Service Account Email: $SERVICE_ACCOUNT_EMAIL"
echo "Audio Storage Bucket: gs://$AUDIO_BUCKET"
echo "Artifacts Storage Bucket: gs://$ARTIFACTS_BUCKET"
