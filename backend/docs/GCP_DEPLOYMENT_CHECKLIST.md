# GCP Deployment Checklist: Step-by-Step Guide

**Last Updated:** 2025-11-13
**Purpose:** Complete checklist for deploying UnseenEdge AI backend to Google Cloud Platform

---

## Table of Contents

1. [Pre-Deployment Verification](#pre-deployment-verification)
2. [GCP Project Setup](#gcp-project-setup)
3. [Cloud SQL (PostgreSQL) Setup](#cloud-sql-postgresql-setup)
4. [Memorystore (Redis) Setup](#memorystore-redis-setup)
5. [Secret Manager Configuration](#secret-manager-configuration)
6. [Cloud Storage for Models](#cloud-storage-for-models)
7. [Docker Image Build & Push](#docker-image-build--push)
8. [Cloud Run Deployment](#cloud-run-deployment)
9. [Post-Deployment Testing](#post-deployment-testing)
10. [Monitoring & Alerting](#monitoring--alerting)
11. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Verification

### Local Testing Checklist

Before deploying to GCP, verify everything works locally:

- [ ] **All tests pass**
  ```bash
  cd backend
  pytest tests/ -v
  ```

- [ ] **API endpoints respond correctly**
  ```bash
  # Start local server
  uvicorn app.main:app --reload --port 8000

  # Test health endpoint
  curl http://localhost:8000/api/v1/health
  ```

- [ ] **Models are trained and available**
  ```bash
  ls models/*.pkl
  # Should see: empathy.pkl, problem_solving.pkl, self_regulation.pkl, resilience.pkl
  ```

- [ ] **Environment variables are documented**
  ```bash
  cat .env.example
  # Verify all required vars are listed
  ```

- [ ] **Dependencies are locked**
  ```bash
  cat requirements.txt
  # Ensure all versions are pinned
  ```

- [ ] **Docker build succeeds locally**
  ```bash
  docker build -t skill-assessment:test .
  docker run -p 8000:8000 skill-assessment:test
  ```

---

## GCP Project Setup

### 1. Create GCP Project

- [ ] **Go to GCP Console**
  - Navigate to: https://console.cloud.google.com

- [ ] **Create new project**
  ```
  Project Name: unseenedge-ai-production
  Project ID: unseenedge-ai-prod-12345 (auto-generated, note this down)
  Organization: (your org)
  ```

- [ ] **Enable billing**
  - Link project to billing account
  - Set up billing alerts ($50, $100, $200 thresholds)

- [ ] **Note your Project ID**
  ```bash
  export PROJECT_ID="unseenedge-ai-prod-12345"
  echo $PROJECT_ID
  ```

### 2. Install & Configure gcloud CLI

- [ ] **Install gcloud CLI**
  ```bash
  # macOS
  brew install google-cloud-sdk

  # Linux
  curl https://sdk.cloud.google.com | bash
  exec -l $SHELL

  # Windows
  # Download from: https://cloud.google.com/sdk/docs/install
  ```

- [ ] **Initialize gcloud**
  ```bash
  gcloud init
  # Follow prompts to authenticate and select project
  ```

- [ ] **Set default project**
  ```bash
  gcloud config set project $PROJECT_ID
  ```

- [ ] **Enable required APIs**
  ```bash
  gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    storage-api.googleapis.com \
    cloudresourcemanager.googleapis.com
  ```

  Wait 2-3 minutes for APIs to propagate.

### 3. Set Up Service Accounts

- [ ] **Create Cloud Run service account**
  ```bash
  gcloud iam service-accounts create skill-assessment-runner \
    --display-name="Cloud Run Service Account"
  ```

- [ ] **Grant necessary permissions**
  ```bash
  SA_EMAIL="skill-assessment-runner@${PROJECT_ID}.iam.gserviceaccount.com"

  # Cloud SQL Client
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudsql.client"

  # Secret Manager Accessor
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

  # Storage Object Viewer (for model files)
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectViewer"
  ```

---

## Cloud SQL (PostgreSQL) Setup

### 1. Create Cloud SQL Instance

- [ ] **Create PostgreSQL instance**
  ```bash
  gcloud sql instances create skill-assessment-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=CHANGE_THIS_PASSWORD \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=03:00
  ```

  **Note:** This takes 5-10 minutes. Use `db-g1-small` for pilot (more memory).

- [ ] **Wait for creation to complete**
  ```bash
  gcloud sql instances list
  # STATUS should be RUNNABLE
  ```

- [ ] **Create database**
  ```bash
  gcloud sql databases create skilldb \
    --instance=skill-assessment-db
  ```

- [ ] **Create database user**
  ```bash
  gcloud sql users create skillapp \
    --instance=skill-assessment-db \
    --password=STRONG_PASSWORD_HERE
  ```

- [ ] **Get connection name**
  ```bash
  INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe skill-assessment-db \
    --format='value(connectionName)')

  echo "Connection Name: $INSTANCE_CONNECTION_NAME"
  # Should be: PROJECT_ID:REGION:INSTANCE_NAME
  ```

- [ ] **Construct DATABASE_URL**
  ```bash
  # For Cloud SQL Proxy (Cloud Run automatic)
  DATABASE_URL="postgresql://skillapp:STRONG_PASSWORD_HERE@/skilldb?host=/cloudsql/$INSTANCE_CONNECTION_NAME"

  # For public IP (if enabled)
  # DATABASE_URL="postgresql://skillapp:STRONG_PASSWORD_HERE@PUBLIC_IP:5432/skilldb"

  echo $DATABASE_URL
  ```

### 2. Initialize Database Schema

- [ ] **Install Cloud SQL Proxy locally (for migration)**
  ```bash
  # macOS
  brew install cloud-sql-proxy

  # Linux
  wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
  chmod +x cloud_sql_proxy
  ```

- [ ] **Start Cloud SQL Proxy**
  ```bash
  cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:5432 &
  ```

- [ ] **Run Alembic migrations**
  ```bash
  cd backend

  # Temporarily set DATABASE_URL for local migration
  export DATABASE_URL="postgresql://skillapp:STRONG_PASSWORD_HERE@localhost:5432/skilldb"

  # Run migrations
  alembic upgrade head
  ```

- [ ] **Verify tables exist**
  ```bash
  psql $DATABASE_URL -c "\dt"
  # Should list: students, linguistic_features, behavioral_features, skill_assessments, etc.
  ```

- [ ] **Stop Cloud SQL Proxy**
  ```bash
  pkill cloud_sql_proxy
  ```

---

## Memorystore (Redis) Setup

**Note:** Redis is optional. Skip this section if using in-memory fallback.

### 1. Create Redis Instance

- [ ] **Create Basic tier Redis instance**
  ```bash
  gcloud redis instances create skill-assessment-redis \
    --size=1 \
    --region=us-central1 \
    --tier=basic \
    --redis-version=redis_7_0
  ```

  **Note:** This takes 5-10 minutes. Use `--tier=standard` for high availability.

- [ ] **Wait for creation**
  ```bash
  gcloud redis instances list --region=us-central1
  # STATE should be READY
  ```

- [ ] **Get Redis host and port**
  ```bash
  REDIS_HOST=$(gcloud redis instances describe skill-assessment-redis \
    --region=us-central1 --format='value(host)')

  REDIS_PORT=$(gcloud redis instances describe skill-assessment-redis \
    --region=us-central1 --format='value(port)')

  echo "Redis Host: $REDIS_HOST"
  echo "Redis Port: $REDIS_PORT"
  ```

- [ ] **Construct REDIS_URL**
  ```bash
  REDIS_URL="redis://$REDIS_HOST:$REDIS_PORT/0"
  echo $REDIS_URL
  ```

### 2. Configure VPC Connector (for Cloud Run)

Cloud Run needs a VPC connector to access Memorystore.

- [ ] **Enable VPC Access API**
  ```bash
  gcloud services enable vpcaccess.googleapis.com
  ```

- [ ] **Create VPC connector**
  ```bash
  gcloud compute networks vpc-access connectors create skill-assessment-connector \
    --region=us-central1 \
    --range=10.8.0.0/28
  ```

  **Note:** This takes 3-5 minutes.

- [ ] **Verify connector is READY**
  ```bash
  gcloud compute networks vpc-access connectors list --region=us-central1
  ```

---

## Secret Manager Configuration

### 1. Create Secrets

- [ ] **Create OPENAI_API_KEY secret**
  ```bash
  echo -n "sk-YOUR_OPENAI_API_KEY_HERE" | gcloud secrets create openai-api-key --data-file=-
  ```

- [ ] **Create JWT_SECRET_KEY secret**
  ```bash
  # Generate a random secret
  openssl rand -base64 32 | gcloud secrets create jwt-secret-key --data-file=-
  ```

- [ ] **Create DATABASE_URL secret**
  ```bash
  echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=-
  ```

- [ ] **Create REDIS_URL secret (if using Redis)**
  ```bash
  echo -n "$REDIS_URL" | gcloud secrets create redis-url --data-file=-
  ```

### 2. Grant Access to Service Account

- [ ] **Grant secret access**
  ```bash
  SA_EMAIL="skill-assessment-runner@${PROJECT_ID}.iam.gserviceaccount.com"

  for SECRET in openai-api-key jwt-secret-key database-url redis-url; do
    gcloud secrets add-iam-policy-binding $SECRET \
      --member="serviceAccount:$SA_EMAIL" \
      --role="roles/secretmanager.secretAccessor"
  done
  ```

### 3. Verify Secrets

- [ ] **List secrets**
  ```bash
  gcloud secrets list
  ```

- [ ] **Test secret access (optional)**
  ```bash
  gcloud secrets versions access latest --secret="openai-api-key"
  # Should print your API key
  ```

---

## Cloud Storage for Models

### 1. Create GCS Bucket

- [ ] **Create bucket**
  ```bash
  gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://${PROJECT_ID}-models
  ```

- [ ] **Verify bucket exists**
  ```bash
  gsutil ls
  # Should show: gs://PROJECT_ID-models/
  ```

### 2. Upload Trained Models

- [ ] **Upload model files**
  ```bash
  cd backend
  gsutil -m cp models/*.pkl gs://${PROJECT_ID}-models/models/v1.0/
  ```

- [ ] **Upload model metadata**
  ```bash
  gsutil -m cp models/*.json gs://${PROJECT_ID}-models/models/v1.0/
  ```

- [ ] **Set public read permissions (optional, for public access)**
  ```bash
  # Skip this if models should be private
  gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-models
  ```

- [ ] **Verify files uploaded**
  ```bash
  gsutil ls -r gs://${PROJECT_ID}-models/
  ```

### 3. Configure Cloud Run to Use GCS Models

We'll mount models as a volume in Cloud Run (alternative: download on startup).

**Option A: Download on Startup (Recommended)**

Update `app/main.py` to download models from GCS on startup:

```python
from google.cloud import storage

@app.on_event("startup")
async def download_models():
    client = storage.Client()
    bucket = client.bucket(f"{PROJECT_ID}-models")

    for skill in ["empathy", "problem_solving", "self_regulation", "resilience"]:
        blob = bucket.blob(f"models/v1.0/{skill}.pkl")
        blob.download_to_filename(f"models/{skill}.pkl")
```

**Option B: Mount as Volume (Advanced)**

Use Cloud Run volume mounts (requires Cloud Run v2).

---

## Docker Image Build & Push

### 1. Build Docker Image

- [ ] **Ensure Dockerfile is optimized**
  ```bash
  cd backend
  cat Dockerfile
  # Verify it copies models/ directory or downloads from GCS
  ```

- [ ] **Build image**
  ```bash
  docker build -t gcr.io/${PROJECT_ID}/skill-assessment:latest .
  ```

- [ ] **Test image locally**
  ```bash
  docker run -p 8000:8000 \
    -e DATABASE_URL="$DATABASE_URL" \
    -e OPENAI_API_KEY="sk-..." \
    gcr.io/${PROJECT_ID}/skill-assessment:latest

  # In another terminal:
  curl http://localhost:8000/api/v1/health
  ```

- [ ] **Stop test container**
  ```bash
  docker ps  # Get container ID
  docker stop <CONTAINER_ID>
  ```

### 2. Push to Google Container Registry

- [ ] **Configure Docker for GCP**
  ```bash
  gcloud auth configure-docker
  ```

- [ ] **Push image**
  ```bash
  docker push gcr.io/${PROJECT_ID}/skill-assessment:latest
  ```

  **Note:** This may take 5-10 minutes depending on image size.

- [ ] **Verify image in GCR**
  ```bash
  gcloud container images list
  # Should show: gcr.io/PROJECT_ID/skill-assessment

  gcloud container images list-tags gcr.io/${PROJECT_ID}/skill-assessment
  # Should show: latest
  ```

---

## Cloud Run Deployment

### 1. Deploy to Cloud Run

- [ ] **Deploy with all configurations**
  ```bash
  gcloud run deploy skill-assessment \
    --image gcr.io/${PROJECT_ID}/skill-assessment:latest \
    --platform managed \
    --region us-central1 \
    --service-account $SA_EMAIL \
    --add-cloudsql-instances $INSTANCE_CONNECTION_NAME \
    --vpc-connector skill-assessment-connector \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest,SECRET_KEY=jwt-secret-key:latest,DATABASE_URL=database-url:latest,REDIS_URL=redis-url:latest" \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO,GCP_PROJECT_ID=${PROJECT_ID}" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --allow-unauthenticated
  ```

  **Note:** This takes 2-3 minutes.

**Configuration Breakdown:**
- `--add-cloudsql-instances`: Enables Cloud SQL Proxy sidecar
- `--vpc-connector`: Connects to Redis (if using Memorystore)
- `--set-secrets`: Injects secrets as environment variables
- `--memory 2Gi`: Allocates 2GB RAM (adjust based on load)
- `--cpu 2`: Allocates 2 vCPUs
- `--min-instances 0`: Scales to zero when idle (cost savings)
- `--max-instances 10`: Limits scaling (cost protection)
- `--allow-unauthenticated`: Public access (change to `--no-allow-unauthenticated` for auth)

### 2. Get Service URL

- [ ] **Get deployed URL**
  ```bash
  SERVICE_URL=$(gcloud run services describe skill-assessment \
    --region us-central1 --format='value(status.url)')

  echo "Service URL: $SERVICE_URL"
  ```

- [ ] **Save URL for testing**
  ```bash
  export API_URL="$SERVICE_URL/api/v1"
  echo $API_URL
  ```

---

## Post-Deployment Testing

### 1. Health Check

- [ ] **Test health endpoint**
  ```bash
  curl $SERVICE_URL/api/v1/health
  ```

  **Expected:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-11-13T...",
    "version": "1.0.0"
  }
  ```

- [ ] **Test detailed health**
  ```bash
  curl $SERVICE_URL/api/v1/health/detailed
  ```

  **Expected:**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "models_loaded": 4,
    "openai_api_key": "configured"
  }
  ```

### 2. Database Connectivity

- [ ] **Verify database connection**
  ```bash
  curl $SERVICE_URL/api/v1/students | jq
  # Should return students list (or empty array if no data)
  ```

### 3. Model Inference

- [ ] **Create test student (if needed)**
  ```bash
  # Use your existing test scripts or seed data
  cd backend
  python scripts/seed_data.py  # If you have test data
  ```

- [ ] **Test single inference**
  ```bash
  curl -X POST $SERVICE_URL/api/v1/infer/student_1 | jq
  ```

  **Expected:**
  ```json
  {
    "student_id": "student_1",
    "skills": [
      {"skill_type": "empathy", "score": 0.75, "confidence": 0.85},
      ...
    ],
    "inference_time_ms": 150
  }
  ```

### 4. GPT-4 Reasoning

- [ ] **Verify reasoning generation**
  ```bash
  curl -X POST $SERVICE_URL/api/v1/infer/student_1 | jq '.skills[0].reasoning'
  ```

  **Expected:** Non-empty reasoning text

### 5. Batch Inference

- [ ] **Test batch endpoint**
  ```bash
  curl -X POST $SERVICE_URL/api/v1/infer/batch \
    -H "Content-Type: application/json" \
    -d '{"student_ids": ["student_1", "student_2", "student_3"]}' | jq
  ```

  **Expected:**
  ```json
  {
    "total_students": 3,
    "successful": 3,
    "failed": 0,
    "results": [...]
  }
  ```

### 6. Performance Test

- [ ] **Test response time**
  ```bash
  time curl -X POST $SERVICE_URL/api/v1/infer/student_1
  # Should complete in <2 seconds
  ```

- [ ] **Test concurrent requests (optional)**
  ```bash
  # Install apache bench
  apt-get install apache2-utils  # Linux
  brew install httpd  # macOS

  # Run load test (100 requests, 10 concurrent)
  ab -n 100 -c 10 -p student.json -T application/json \
    $SERVICE_URL/api/v1/infer/student_1
  ```

---

## Monitoring & Alerting

### 1. Set Up Cloud Monitoring

- [ ] **Navigate to Cloud Monitoring**
  - Go to: https://console.cloud.google.com/monitoring

- [ ] **Create custom dashboard**
  - Name: "Skill Assessment Production"
  - Add charts for:
    - Request count (per minute)
    - Request latency (p50, p95, p99)
    - Error rate (4xx, 5xx)
    - Instance count
    - CPU utilization
    - Memory utilization

### 2. Configure Alerts

- [ ] **Create alert for high error rate**
  ```bash
  # Via gcloud (or use Console UI)
  gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=300s
  ```

- [ ] **Create alert for high latency**
  - Alert if p95 latency > 2 seconds for 5 minutes

- [ ] **Create alert for database connection failures**
  - Alert if DB connection errors > 0 for 2 minutes

- [ ] **Create billing alert**
  - Alert if monthly costs > $50, $100, $200

### 3. Set Up Logging

- [ ] **Configure log retention**
  ```bash
  gcloud logging sinks list
  # Verify default retention is 30 days
  ```

- [ ] **Create log-based metrics**
  - Metric: Inference errors (filter on "error" in logs)
  - Metric: GPT-4 API failures (filter on "openai" errors)

- [ ] **Set up Log Explorer filters**
  - Error logs: `severity >= ERROR`
  - Slow requests: `httpRequest.latency > 2s`

---

## Rollback Procedures

### 1. Quick Rollback (Previous Image)

If deployment fails or has critical bugs:

- [ ] **Deploy previous image version**
  ```bash
  # List available tags
  gcloud container images list-tags gcr.io/${PROJECT_ID}/skill-assessment

  # Deploy specific version
  gcloud run deploy skill-assessment \
    --image gcr.io/${PROJECT_ID}/skill-assessment:PREVIOUS_TAG \
    --region us-central1
  ```

### 2. Full Rollback Procedure

- [ ] **Revert to last known good configuration**
  ```bash
  # Get previous revision
  gcloud run revisions list --service skill-assessment --region us-central1

  # Route 100% traffic to previous revision
  gcloud run services update-traffic skill-assessment \
    --to-revisions PREVIOUS_REVISION=100 \
    --region us-central1
  ```

- [ ] **Verify rollback**
  ```bash
  curl $SERVICE_URL/api/v1/health
  ```

### 3. Database Rollback

- [ ] **Restore from backup**
  ```bash
  # List backups
  gcloud sql backups list --instance=skill-assessment-db

  # Restore from backup ID
  gcloud sql backups restore BACKUP_ID \
    --backup-instance=skill-assessment-db \
    --backup-id=BACKUP_ID
  ```

---

## Post-Deployment Checklist

### Immediate (Day 1)

- [ ] Verify all health checks pass
- [ ] Test all API endpoints
- [ ] Monitor error logs for first hour
- [ ] Verify database connections stable
- [ ] Check Cloud Run metrics (request count, latency)
- [ ] Confirm billing is within expected range

### Short-Term (Week 1)

- [ ] Review Cloud Monitoring dashboards daily
- [ ] Check error logs for patterns
- [ ] Monitor API costs (OpenAI usage)
- [ ] Verify backup jobs running
- [ ] Test rollback procedure (in staging if available)
- [ ] Document any issues and resolutions

### Long-Term (Month 1)

- [ ] Review monthly costs against budget
- [ ] Analyze performance trends
- [ ] Optimize instance sizes if needed
- [ ] Review alert policies (too many/too few alerts?)
- [ ] Plan for scaling if user growth expected
- [ ] Update documentation with lessons learned

---

## Troubleshooting Guide

### Issue: Cloud Run deployment fails

**Symptoms:**
- Deployment stuck at "Creating Revision..."
- Error: "container failed to start"

**Solutions:**
1. Check Cloud Run logs: `gcloud run services logs read skill-assessment --region us-central1`
2. Verify Docker image works locally
3. Check environment variables are set correctly
4. Ensure service account has all permissions

---

### Issue: Database connection errors

**Symptoms:**
- Health check fails with "database: disconnected"
- 500 errors on API requests

**Solutions:**
1. Verify Cloud SQL instance is RUNNABLE: `gcloud sql instances list`
2. Check connection name is correct in deployment
3. Ensure Cloud SQL Proxy is enabled: `--add-cloudsql-instances`
4. Verify service account has `cloudsql.client` role
5. Check DATABASE_URL format is correct

---

### Issue: Redis connection errors

**Symptoms:**
- Logs show "Redis connection failed"
- Metrics not persisting

**Solutions:**
1. Verify Redis instance is READY: `gcloud redis instances list --region us-central1`
2. Ensure VPC connector is created and attached
3. Check REDIS_URL format: `redis://HOST:PORT/0`
4. Verify Cloud Run has `--vpc-connector` flag
5. Test connectivity from Cloud Shell:
   ```bash
   gcloud compute ssh test-vm --zone us-central1-a
   redis-cli -h $REDIS_HOST ping
   ```

---

### Issue: Models not loading

**Symptoms:**
- Error: "Model file not found"
- Inference requests fail with 500

**Solutions:**
1. Verify models exist in GCS: `gsutil ls gs://${PROJECT_ID}-models/models/v1.0/`
2. Check service account has `storage.objectViewer` role
3. Ensure models are downloaded on startup (check logs)
4. Increase Cloud Run memory if OOM errors
5. Verify model file paths in code match GCS structure

---

### Issue: High costs

**Symptoms:**
- Billing alert triggered
- Costs higher than expected

**Solutions:**
1. Check Cloud Run metrics for unexpected traffic
2. Review OpenAI API usage: https://platform.openai.com/usage
3. Verify min-instances = 0 (scale to zero when idle)
4. Check for log retention settings (default 30 days)
5. Review Cloud SQL instance size (downgrade if oversized)
6. Enable Redis caching for GPT-4 reasoning

---

## Summary

You've successfully deployed UnseenEdge AI backend to GCP!

**What's Deployed:**
- ✅ FastAPI backend on Cloud Run
- ✅ PostgreSQL database on Cloud SQL
- ✅ Redis on Memorystore (optional)
- ✅ Secrets in Secret Manager
- ✅ Models in Cloud Storage
- ✅ Monitoring and alerts configured

**Next Steps:**
1. Build Streamlit dashboard (see `NEXT_STEPS_ROADMAP.md`)
2. Set up CI/CD pipeline (see `.github/workflows/ml-pipeline.yml.template`)
3. Collect real student data for fine-tuning
4. Iterate on model quality

**Support:**
- GCP Documentation: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs

---

**Last Updated:** 2025-11-13
**Version:** 1.0
**Deployment Target:** Production
