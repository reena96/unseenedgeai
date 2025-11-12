# Cloud Run Deployment Guide

## Overview

This guide explains how to complete Task 6 by deploying the MASS API to Google Cloud Run.

## Current Status

✅ **Infrastructure Code Complete:**
- Cloud SQL (PostgreSQL 15) - Deployed
- Cloud Storage buckets - Deployed
- Cloud Tasks queues - Deployed
- Pub/Sub topics - Deployed
- Artifact Registry - Ready to create
- Secret Manager secrets - Ready to create
- Cloud Run service - Configuration ready

❌ **Not Yet Deployed:**
- Cloud Run service (waiting for Docker image)
- New secrets (app-secret-key, database-url, redis-url)

## Prerequisites

1. **Docker installed** locally
2. **gcloud CLI authenticated** with project access
3. **Terraform 1.5+** installed
4. **API credentials** in `.env` file

## Deployment Steps

### Step 1: Build the Docker Image

```bash
# Navigate to project root
cd /Users/reena/gauntletai/unseenedgeai

# Build the Docker image
cd backend
docker build -t us-central1-docker.pkg.dev/unseenedgeai/mass-api/mass-api:latest .

# Test locally (optional)
docker run -p 8080:8080 --env-file .env \
  us-central1-docker.pkg.dev/unseenedgeai/mass-api/mass-api:latest
```

### Step 2: Create Artifact Registry and Push Image

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Apply Terraform (creates Artifact Registry + secrets)
cd ../infrastructure/terraform
terraform apply tfplan

# Push the image
cd ../../backend
docker push us-central1-docker.pkg.dev/unseenedgeai/mass-api/mass-api:latest
```

### Step 3: Verify Cloud Run Deployment

```bash
# Check Cloud Run service status
gcloud run services describe mass-api \
  --region=us-central1 \
  --project=unseenedgeai

# Get the service URL
gcloud run services describe mass-api \
  --region=us-central1 \
  --project=unseenedgeai \
  --format='value(status.url)'

# Test health endpoint
curl https://mass-api-<hash>-uc.a.run.app/api/v1/health
```

### Step 4: Verify All Infrastructure

```bash
# Cloud SQL
gcloud sql instances list --project=unseenedgeai

# Cloud Storage
gsutil ls -p unseenedgeai

# Cloud Tasks
gcloud tasks queues list --location=us-central1 --project=unseenedgeai

# Pub/Sub
gcloud pubsub topics list --project=unseenedgeai

# Cloud Run
gcloud run services list --region=us-central1 --project=unseenedgeai

# Secrets
gcloud secrets list --project=unseenedgeai
```

## Important Notes

### Docker Image Requirements

The Docker image must:
1. Expose port 8080
2. Respond to health checks at `/api/v1/health`
3. Support Cloud SQL connections via Unix socket
4. Load environment variables from Secret Manager

### Current Terraform Plan

Running `terraform apply tfplan` will create:
- ✅ Artifact Registry repository `mass-api`
- ✅ Cloud Run service `mass-api`
- ✅ Secret `app-secret-key` (auto-generated)
- ✅ Secret `database-url` (auto-generated from Cloud SQL)
- ✅ Secret `redis-url` (placeholder: `redis://localhost:6379/0`)
- ✅ IAM permissions for service account to access secrets

**Total: 14 new resources**

### Environment Variables in Cloud Run

The following environment variables are automatically configured from Secret Manager:
- `ENVIRONMENT` - Set to `production`
- `GOOGLE_CLOUD_PROJECT` - Set to `unseenedgeai`
- `SECRET_KEY` - From Secret Manager (`app-secret-key`)
- `JWT_SECRET_KEY` - From Secret Manager (`jwt-secret-key`)
- `DATABASE_URL` - From Secret Manager (`database-url`)
- `REDIS_URL` - From Secret Manager (`redis-url`)
- `AUDIO_BUCKET_NAME` - Set to bucket name
- `ARTIFACTS_BUCKET_NAME` - Set to bucket name

### Known Limitations

1. **No Docker image exists yet** - Must be built and pushed before Cloud Run can deploy
2. **Redis URL is placeholder** - Update when Redis is deployed:
   ```bash
   echo -n "redis://real-redis-url:6379/0" | \
     gcloud secrets versions add redis-url --data-file=-
   ```
3. **Celery not configured** - Will need separate workers for background tasks

## Troubleshooting

### Cloud Run Service Won't Start

Check logs:
```bash
gcloud run services logs read mass-api \
  --region=us-central1 \
  --project=unseenedgeai \
  --limit=50
```

### Database Connection Issues

Verify Cloud SQL connection:
```bash
# Check database instance is running
gcloud sql instances describe unseenedgeai-db-production --project=unseenedgeai

# Test connection from Cloud Shell
gcloud sql connect unseenedgeai-db-production --user=mass_user --database=mass_db
```

### Secret Access Issues

Verify service account has access:
```bash
gcloud secrets get-iam-policy app-secret-key --project=unseenedgeai
gcloud secrets get-iam-policy database-url --project=unseenedgeai
```

## Next Steps After Deployment

1. **Task 29: CI/CD Pipeline**
   - Set up GitHub Actions to build and deploy automatically
   - Configure blue-green deployments

2. **Task 34: Authentication Testing**
   - Test JWT token generation
   - Test login/refresh/logout flows

3. **Task 9: Speech-to-Text Integration**
   - Begin data pipeline development

## Verification Checklist

After deployment, verify Task 6 completion:

- [ ] Cloud Run service `mass-api` deployed and accessible
- [ ] Health endpoint returns 200 OK
- [ ] Cloud SQL connection working
- [ ] All 4 buckets exist (audio, models, terraform-state)
- [ ] All 2 Cloud Tasks queues exist
- [ ] All 4 Pub/Sub topics exist
- [ ] Service account has access to all secrets
- [ ] Monitoring dashboards show metrics

## Cost Estimates

**Current Infrastructure (Monthly):**
- Cloud SQL (db-custom-2-7680, HA): ~$300-400
- Cloud Storage (minimal usage): ~$1-5
- Cloud Run (scaled to zero): ~$0 when idle, ~$20-50 under load
- Cloud Tasks: ~$0.40 per million tasks
- Pub/Sub: ~$0.60 per million messages
- Secret Manager: ~$0.06 per secret per month

**Total Estimated: $320-460/month** (with moderate usage)

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL with Cloud Run](https://cloud.google.com/sql/docs/mysql/connect-run)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)
