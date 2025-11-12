#!/bin/bash
# Script to retrieve all secret values for GitHub Actions configuration
# Run this script and copy the values to GitHub repository secrets

set -e

echo "=========================================="
echo "GitHub Actions Secrets Values"
echo "=========================================="
echo ""
echo "⚠️  WARNING: These are sensitive values!"
echo "⚠️  Only use in a secure environment"
echo "⚠️  Never commit these values to git"
echo ""
echo "=========================================="
echo ""

# GCP Configuration
echo "📋 GCP Configuration"
echo "--------------------"
echo "GCP_PROJECT_ID: unseenedgeai"
echo "GCP_REGION: us-central1"
echo "GCP_SERVICE_ACCOUNT: mass-api@unseenedgeai.iam.gserviceaccount.com"
echo ""

# Database Configuration
echo "📋 Database Configuration"
echo "-------------------------"
echo "DB_CONNECTION_NAME: unseenedgeai:us-central1:unseenedgeai-db-production"
echo "DB_NAME: mass_db"
echo "DB_USER: mass_api"
echo ""
echo "DB_PASSWORD:"
gcloud secrets versions access latest --secret=db-password 2>/dev/null || echo "Error: Could not retrieve db-password"
echo ""

# Application Secrets
echo "📋 Application Secrets"
echo "----------------------"
echo "JWT_SECRET:"
gcloud secrets versions access latest --secret=jwt-secret-key 2>/dev/null || echo "Error: Could not retrieve jwt-secret-key"
echo ""

echo "OPENAI_API_KEY:"
gcloud secrets versions access latest --secret=openai-api-key 2>/dev/null || echo "Error: Could not retrieve openai-api-key"
echo ""

# Optional secrets
echo "📋 Optional Secrets"
echo "-------------------"
echo "SENTRY_DSN (optional):"
gcloud secrets versions access latest --secret=sentry-dsn 2>/dev/null || echo "Not configured (optional)"
echo ""

echo "=========================================="
echo "Service Account Key"
echo "=========================================="
echo ""
echo "To create a service account key for GitHub Actions:"
echo ""
echo "1. Run this command:"
echo "   gcloud iam service-accounts keys create github-actions-key.json \\"
echo "     --iam-account=mass-api@unseenedgeai.iam.gserviceaccount.com"
echo ""
echo "2. Base64 encode it:"
echo "   base64 github-actions-key.json > github-actions-key-base64.txt"
echo ""
echo "3. Copy the base64 content for GCP_SA_KEY secret:"
echo "   cat github-actions-key-base64.txt"
echo ""
echo "4. Delete the local files:"
echo "   rm github-actions-key.json github-actions-key-base64.txt"
echo ""
echo "=========================================="
echo ""
echo "✅ Copy these values to GitHub:"
echo "   Repository → Settings → Secrets and variables → Actions"
echo ""
