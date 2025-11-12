# MASS Infrastructure Setup

This directory contains infrastructure configuration and setup scripts for the Middle School Non-Academic Skills Measurement System (MASS).

## Overview

The MASS system is deployed on Google Cloud Platform (GCP) with the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Google Cloud Platform                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Cloud Run   │───▶│  Cloud SQL   │    │Cloud Storage │  │
│  │ (FastAPI)    │    │ (PostgreSQL) │    │ (Audio Files)│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                     │                              │
│         ▼                     ▼                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Celery     │    │    Redis     │    │Speech-to-Text│  │
│  │  (Workers)   │───▶│ (Task Queue) │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Vertex AI   │    │Secret Manager│    │  Monitoring  │  │
│  │ (ML Models)  │    │ (API Keys)   │    │  & Logging   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Google Cloud SDK**: Install from https://cloud.google.com/sdk/docs/install
2. **GCP Project**: Create a project at https://console.cloud.google.com
3. **Billing Account**: Link a billing account to your project
4. **Project ID**: Note your project ID (set in `.env` as `GOOGLE_CLOUD_PROJECT`)

## Setup Steps

### 1. Initial GCP Project Setup

```bash
# Set your project ID and region in .env file
export GOOGLE_CLOUD_PROJECT="unseenedgeai"
export GOOGLE_CLOUD_REGION="us-central1"
export BILLING_ACCOUNT_ID="your-billing-account-id"

# Run the GCP setup script
cd infrastructure
./gcp-setup.sh
```

This script will:
- Enable all required GCP APIs
- Create service accounts with appropriate IAM roles
- Set up Cloud Storage buckets for audio files and artifacts
- Create Secret Manager secrets (with placeholder values)
- Generate service account keys for local development

### 2. Update Secret Manager

After running `gcp-setup.sh`, update the secrets with actual values:

```bash
# Update API keys
echo -n "your-anthropic-api-key" | gcloud secrets versions add anthropic-api-key --data-file=-
echo -n "your-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-
echo -n "your-perplexity-api-key" | gcloud secrets versions add perplexity-api-key --data-file=-

# Update JWT secret (generate a secure random string)
openssl rand -base64 32 | gcloud secrets versions add jwt-secret-key --data-file=-

# Update database password (will be set during Cloud SQL setup)
echo -n "your-secure-database-password" | gcloud secrets versions add database-password --data-file=-
```

### 3. Set Up Cloud SQL (PostgreSQL + TimescaleDB)

```bash
./cloudsql-setup.sh
```

### 4. Set Up Redis

```bash
./redis-setup.sh
```

### 5. Deploy FastAPI Application

```bash
./deploy-cloudrun.sh
```

## Resource Configuration

### Compute Resources

- **Cloud Run**: Auto-scaling 0-100 instances
  - CPU: 2 vCPU per instance
  - Memory: 4 GB per instance
  - Max concurrent requests: 80

- **Cloud SQL**: High availability configuration
  - Tier: db-n1-standard-2 (2 vCPU, 7.5 GB RAM)
  - Storage: 100 GB SSD (auto-expanding)
  - Backup: Automated daily backups

- **Redis**: Managed Memory Store
  - Tier: Standard (5 GB)
  - High availability: Regional

### Cost Estimates

Based on usage for 1,000 students:

| Service | Monthly Cost (est.) |
|---------|---------------------|
| Cloud Run | $150-300 |
| Cloud SQL | $200-400 |
| Cloud Storage | $50-100 |
| Speech-to-Text | $400-800 |
| Redis | $100-150 |
| Vertex AI | $100-200 |
| **Total** | **$1,000-1,950** |

**Per student cost**: ~$1.00-2.00/month

## Security

### IAM Roles

The application service account has the following roles:
- `roles/cloudsql.client` - Database access
- `roles/storage.objectAdmin` - Storage bucket access
- `roles/speech.client` - Speech-to-Text API
- `roles/aiplatform.user` - Vertex AI access
- `roles/logging.logWriter` - Logging
- `roles/monitoring.metricWriter` - Monitoring
- `roles/secretmanager.secretAccessor` - Secrets access
- `roles/redis.editor` - Redis access

### Data Encryption

- **At rest**: All data encrypted with Google-managed encryption keys
- **In transit**: TLS 1.3 for all communications
- **Secrets**: Stored in Secret Manager with automatic rotation support

### Compliance

- FERPA compliant data handling
- COPPA compliant (parental consent required)
- SOC 2 Type II ready (with proper audit logging)

## Monitoring and Logging

Access monitoring dashboards:
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# View metrics
gcloud monitoring dashboards list

# Set up alerts
gcloud alpha monitoring policies create --notification-channels=<channel-id> \
  --condition-threshold-value=0.95 \
  --condition-threshold-duration=300s
```

## Troubleshooting

### Service Account Permission Issues

```bash
# Verify service account has required roles
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:serviceAccount:mass-app-service-account@*"
```

### API Enablement Issues

```bash
# Verify APIs are enabled
gcloud services list --enabled
```

### Storage Access Issues

```bash
# Test bucket access
gsutil ls gs://$GOOGLE_CLOUD_PROJECT-audio-files
```

## Cleanup

To remove all resources (⚠️ DESTRUCTIVE):

```bash
./cleanup.sh  # Creates a cleanup script that removes all resources
```

## Support

For issues or questions:
1. Check GCP Console logs: https://console.cloud.google.com/logs
2. Review Cloud Run logs: `gcloud run logs read <service-name>`
3. Contact DevOps team for infrastructure issues
