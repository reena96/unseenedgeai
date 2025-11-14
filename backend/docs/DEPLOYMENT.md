# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the UnseenEdge AI Skill Assessment System in various environments. The system is designed for production deployment on Google Cloud Platform (GCP) but can also run locally for development.

**Deployment Options:**
- Local development setup (Docker or native)
- GCP Cloud Run (production recommended)
- Docker Compose (alternative production)
- Kubernetes (enterprise scale)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment (GCP Cloud Run)](#production-deployment-gcp-cloud-run)
4. [Docker Compose Deployment](#docker-compose-deployment)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Model Files Storage](#model-files-storage)
8. [Health Checks & Monitoring](#health-checks--monitoring)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Scaling Configuration](#scaling-configuration)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

**Development:**
- Python 3.10+ (3.11 recommended)
- PostgreSQL 14+
- Redis 7+
- Git

**Production (GCP):**
- Google Cloud SDK (`gcloud` CLI)
- Docker
- kubectl (for Kubernetes deployments)

**Optional:**
- Docker Desktop (for local containerized development)
- pgAdmin (database management)
- Redis Commander (Redis management)

### Required Accounts & Access

**Development:**
- OpenAI API account (for GPT-4 reasoning)
- Optional: GCP account (for Secret Manager)

**Production:**
- GCP account with billing enabled
- OpenAI API account
- Domain name (for production URL)

### Required Permissions (GCP)

```bash
# Service account permissions needed:
- roles/cloudsql.client
- roles/secretmanager.secretAccessor
- roles/storage.objectViewer
- roles/redis.viewer
- roles/run.developer
```

---

## Local Development Setup

### Option 1: Native Setup (Recommended for Development)

#### Step 1: Clone Repository

```bash
git clone https://github.com/unseenedgeai/mass-backend.git
cd mass-backend/backend
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Download spaCy language model (required for NLP)
python -m spacy download en_core_web_sm
```

#### Step 4: Set Up PostgreSQL

```bash
# Option A: Using Docker
docker run -d \
  --name mass-postgres \
  -p 5432:5432 \
  -e POSTGRES_DB=mass_db \
  -e POSTGRES_USER=mass_app_user \
  -e POSTGRES_PASSWORD=dev_password \
  -v mass_postgres_data:/var/lib/postgresql/data \
  postgres:14

# Option B: Native PostgreSQL installation
# Install PostgreSQL 14 from https://www.postgresql.org/download/

# Create database
createdb mass_db

# Create user
createuser -P mass_app_user
# Enter password: dev_password

# Grant permissions
psql mass_db
GRANT ALL PRIVILEGES ON DATABASE mass_db TO mass_app_user;
\q
```

#### Step 5: Set Up Redis

```bash
# Option A: Using Docker
docker run -d \
  --name mass-redis \
  -p 6379:6379 \
  -v mass_redis_data:/data \
  redis:7-alpine

# Option B: Native Redis installation
# macOS (using Homebrew):
brew install redis
brew services start redis

# Linux (Ubuntu/Debian):
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Step 6: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimum required configuration:**

```bash
# .env
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-this
JWT_SECRET_KEY=dev-jwt-secret-change-this

# Database
DATABASE_URL=postgresql+asyncpg://mass_app_user:dev_password@localhost:5432/mass_db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (required for reasoning generation)
OPENAI_API_KEY=sk-your-openai-api-key-here

# GCP (optional for local development)
GOOGLE_CLOUD_PROJECT=unseenedgeai-dev
GOOGLE_CLOUD_REGION=us-central1

# Models directory
MODELS_DIR=./models

# Fusion config
FUSION_CONFIG_PATH=./config/fusion_weights.json
```

#### Step 7: Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic upgrade head

# Verify migrations
alembic current
```

#### Step 8: Load ML Models

```bash
# Create models directory
mkdir -p models

# Option A: Download from GCS (if you have trained models)
gsutil -m cp -r gs://unseenedgeai-models/v1.0.0/* models/

# Option B: Train models locally (see TRAINING_DATA_FORMAT.md)
python app/ml/train_models.py \
  --data-path data/training_data.csv \
  --models-dir models/ \
  --version 1.0.0

# Verify models loaded
ls -lh models/
# Should see:
# empathy_model.pkl
# empathy_features.pkl
# problem_solving_model.pkl
# problem_solving_features.pkl
# self_regulation_model.pkl
# self_regulation_features.pkl
# resilience_model.pkl
# resilience_features.pkl
```

#### Step 9: Create Fusion Config

```bash
# Create config directory
mkdir -p config

# Create default fusion weights
cat > config/fusion_weights.json <<EOF
{
  "version": "1.0.0",
  "description": "Default fusion weights for development",
  "weights": {
    "empathy": {
      "ml_inference": 0.50,
      "linguistic_features": 0.25,
      "behavioral_features": 0.15,
      "confidence_adjustment": 0.10
    },
    "problem_solving": {
      "ml_inference": 0.50,
      "linguistic_features": 0.20,
      "behavioral_features": 0.20,
      "confidence_adjustment": 0.10
    },
    "self_regulation": {
      "ml_inference": 0.50,
      "linguistic_features": 0.10,
      "behavioral_features": 0.30,
      "confidence_adjustment": 0.10
    },
    "resilience": {
      "ml_inference": 0.50,
      "linguistic_features": 0.15,
      "behavioral_features": 0.25,
      "confidence_adjustment": 0.10
    }
  }
}
EOF
```

#### Step 10: Run Development Server

```bash
# Start development server with auto-reload
uvicorn app.main:app --reload --port 8000 --log-level debug

# Server will start at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
# Health check: http://localhost:8000/api/v1/health
```

#### Step 11: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "models_loaded": 4,
#   "version": "0.1.0"
# }

# Run tests
pytest tests/ -v

# Check code quality
black app/ tests/ --check
flake8 app/ tests/
mypy app/
```

---

### Option 2: Docker Development Setup

#### Step 1: Build Docker Image

```bash
# Build image
docker build -t unseenedgeai/mass-backend:dev .

# Verify build
docker images | grep mass-backend
```

#### Step 2: Create Docker Network

```bash
# Create network for services
docker network create mass-network
```

#### Step 3: Run PostgreSQL

```bash
docker run -d \
  --name mass-postgres \
  --network mass-network \
  -e POSTGRES_DB=mass_db \
  -e POSTGRES_USER=mass_app_user \
  -e POSTGRES_PASSWORD=dev_password \
  -v mass_postgres_data:/var/lib/postgresql/data \
  postgres:14
```

#### Step 4: Run Redis

```bash
docker run -d \
  --name mass-redis \
  --network mass-network \
  -v mass_redis_data:/data \
  redis:7-alpine
```

#### Step 5: Run Application

```bash
docker run -d \
  --name mass-backend \
  --network mass-network \
  -p 8000:8080 \
  -e DATABASE_URL=postgresql+asyncpg://mass_app_user:dev_password@mass-postgres:5432/mass_db \
  -e REDIS_URL=redis://mass-redis:6379/0 \
  -e OPENAI_API_KEY=your-openai-key \
  -e SECRET_KEY=dev-secret-key \
  -e JWT_SECRET_KEY=dev-jwt-secret-key \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/config:/app/config \
  unseenedgeai/mass-backend:dev
```

#### Step 6: Verify

```bash
# Check logs
docker logs -f mass-backend

# Test health
curl http://localhost:8000/api/v1/health
```

---

## Production Deployment (GCP Cloud Run)

### Architecture Overview

```
Internet
    │
    ▼
Cloud Load Balancer
    │
    ▼
Cloud Run Service
    │
    ├─────► Cloud SQL (PostgreSQL)
    ├─────► Memorystore (Redis)
    ├─────► Secret Manager
    └─────► Cloud Storage (Models)
```

### Step 1: Set Up GCP Project

```bash
# Set project
export PROJECT_ID=unseenedgeai-prod
export REGION=us-central1

gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 2: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create mass-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-7680 \
  --region=$REGION \
  --network=default \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --database-flags=max_connections=100

# Create database
gcloud sql databases create mass_db \
  --instance=mass-db

# Create user
gcloud sql users create mass_app_user \
  --instance=mass-db \
  --password=$(openssl rand -base64 32)

# Get connection name
gcloud sql instances describe mass-db \
  --format='value(connectionName)'
# Output: PROJECT_ID:REGION:mass-db
```

**Recommended Production Tiers:**
- **Small:** `db-custom-2-7680` (2 vCPU, 7.5 GB RAM) - 100 connections
- **Medium:** `db-custom-4-15360` (4 vCPU, 15 GB RAM) - 200 connections
- **Large:** `db-custom-8-30720` (8 vCPU, 30 GB RAM) - 400 connections

### Step 3: Create Memorystore (Redis) Instance

```bash
# Create Redis instance
gcloud redis instances create mass-redis \
  --size=5 \
  --region=$REGION \
  --tier=STANDARD_HA \
  --redis-version=redis_7_0

# Get connection details
gcloud redis instances describe mass-redis \
  --region=$REGION \
  --format='value(host,port)'
# Output: 10.0.0.3 6379
```

**Recommended Tiers:**
- **Development:** `BASIC` tier, 1 GB
- **Production:** `STANDARD_HA` tier, 5+ GB (high availability)

### Step 4: Create Cloud Storage Bucket for Models

```bash
# Create bucket
gsutil mb -l $REGION gs://$PROJECT_ID-models

# Set lifecycle policy (optional - keep last 5 versions)
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 5
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://$PROJECT_ID-models

# Upload models
gsutil -m cp -r models/* gs://$PROJECT_ID-models/v1.0.0/
```

### Step 5: Configure Secret Manager

```bash
# Create secrets
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create jwt-secret-key --data-file=-

echo -n "your-openai-api-key" | \
  gcloud secrets create openai-api-key --data-file=-

# Create service account for Cloud Run
gcloud iam service-accounts create mass-backend-sa \
  --display-name="MASS Backend Service Account"

# Grant Secret Manager access
export SERVICE_ACCOUNT=mass-backend-sa@$PROJECT_ID.iam.gserviceaccount.com

gcloud secrets add-iam-policy-binding jwt-secret-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# Grant Cloud SQL access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client"

# Grant Storage access (read models)
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectViewer \
  gs://$PROJECT_ID-models
```

### Step 6: Build and Push Docker Image

```bash
# Set up Artifact Registry
gcloud artifacts repositories create mass-backend \
  --repository-format=docker \
  --location=$REGION \
  --description="MASS Backend Docker Repository"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and tag image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/mass-backend/api:latest .

# Push image
docker push $REGION-docker.pkg.dev/$PROJECT_ID/mass-backend/api:latest
```

### Step 7: Deploy to Cloud Run

```bash
# Get Cloud SQL connection name
export SQL_CONNECTION=$(gcloud sql instances describe mass-db \
  --format='value(connectionName)')

# Get Redis host
export REDIS_HOST=$(gcloud redis instances describe mass-redis \
  --region=$REGION --format='value(host)')
export REDIS_PORT=6379

# Deploy Cloud Run service
gcloud run deploy mass-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/mass-backend/api:latest \
  --platform=managed \
  --region=$REGION \
  --service-account=$SERVICE_ACCOUNT \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=2 \
  --memory=4Gi \
  --timeout=300 \
  --concurrency=80 \
  --add-cloudsql-instances=$SQL_CONNECTION \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://mass_app_user:PASSWORD@/$PROJECT_ID:$REGION:mass-db/mass_db?host=/cloudsql/$SQL_CONNECTION" \
  --set-env-vars="REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT/0" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-env-vars="MODELS_DIR=/app/models" \
  --set-env-vars="FUSION_CONFIG_PATH=/app/config/fusion_weights.json" \
  --set-secrets="SECRET_KEY=jwt-secret-key:latest" \
  --set-secrets="JWT_SECRET_KEY=jwt-secret-key:latest" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest"

# Get service URL
gcloud run services describe mass-backend \
  --region=$REGION \
  --format='value(status.url)'
# Output: https://mass-backend-xxxxx-uc.a.run.app
```

### Step 8: Configure Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service=mass-backend \
  --domain=api.unseenedgeai.com \
  --region=$REGION

# Follow instructions to update DNS records
```

### Step 9: Set Up Cloud Armor (Optional - DDoS Protection)

```bash
# Create security policy
gcloud compute security-policies create mass-backend-policy \
  --description="Security policy for MASS Backend"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=mass-backend-policy \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600

# Apply to load balancer
# (Requires load balancer setup)
```

### Step 10: Verify Production Deployment

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe mass-backend \
  --region=$REGION --format='value(status.url)')

# Test health check
curl $SERVICE_URL/api/v1/health

# Test inference (requires authentication)
curl -X POST "$SERVICE_URL/api/v1/infer/student_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# Check logs
gcloud run services logs read mass-backend \
  --region=$REGION \
  --limit=50
```

---

## Docker Compose Deployment

### Step 1: Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14
    container_name: mass-postgres
    environment:
      POSTGRES_DB: mass_db
      POSTGRES_USER: mass_app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-dev_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mass_app_user -d mass_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: mass-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mass-backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://mass_app_user:${DB_PASSWORD:-dev_password}@postgres:5432/mass_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-unseenedgeai}
      - MODELS_DIR=/app/models
      - FUSION_CONFIG_PATH=/app/config/fusion_weights.json
    volumes:
      - ./models:/app/models:ro
      - ./config:/app/config:ro
    ports:
      - "8000:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    container_name: mass-nginx
    depends_on:
      - api
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Step 2: Create .env File

```bash
# .env for Docker Compose
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLOUD_PROJECT=unseenedgeai-prod
```

### Step 3: Deploy

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Run migrations
docker-compose exec api alembic upgrade head

# Stop services
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` | Yes |
| `SECRET_KEY` | Application secret key | `random-32-byte-string` | Yes |
| `JWT_SECRET_KEY` | JWT signing key | `random-32-byte-string` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | Yes |

### Optional Variables (with Defaults)

| Variable | Description | Default | Production Recommended |
|----------|-------------|---------|------------------------|
| `ENVIRONMENT` | Environment name | `production` | `production` |
| `DEBUG` | Debug mode | `false` | `false` |
| `REDIS_URL` | Redis connection string | - | Set explicitly |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | - | Set for GCP deployments |
| `MODELS_DIR` | ML models directory | `./models` | `/app/models` |
| `FUSION_CONFIG_PATH` | Fusion weights config | `./config/fusion_weights.json` | `/app/config/fusion_weights.json` |
| `DATABASE_POOL_SIZE` | DB connection pool size | `20` | `20-50` (based on load) |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | `40` | `40-100` |
| `REDIS_MAX_CONNECTIONS` | Redis connection pool | `50` | `50-100` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` | `true` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | `60` | `60-100` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `[]` | Set frontend URLs |
| `LOG_LEVEL` | Logging level | `INFO` | `INFO` or `WARNING` |

### Secret Management

**Development:**
```bash
# Use .env file
cat > .env <<EOF
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
OPENAI_API_KEY=sk-your-key
EOF
```

**Production (GCP Secret Manager):**
```bash
# Secrets automatically loaded from Secret Manager
# Configure via --set-secrets flag in Cloud Run deployment
```

**Production (Other):**
```bash
# Use environment-specific secret management:
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
# - Kubernetes Secrets
```

---

## Database Setup

### Initial Schema Creation

```bash
# Run Alembic migrations
alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"
```

### Required Indexes (Performance)

```sql
-- Create critical indexes for performance
CREATE INDEX CONCURRENTLY idx_linguistic_features_student_created
  ON linguistic_features(student_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_behavioral_features_student_created
  ON behavioral_features(student_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_skill_assessment_student
  ON skill_assessments(student_id);

CREATE INDEX CONCURRENTLY idx_skill_assessment_created
  ON skill_assessments(created_at DESC);

-- Verify indexes
\di
```

### Connection Pooling (Production)

**Option 1: Application-level (SQLAlchemy)**
```python
# Already configured in app/core/database.py
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 1800
```

**Option 2: pgBouncer (Recommended for high scale)**
```bash
# Install pgBouncer
apt-get install pgbouncer

# Configure /etc/pgbouncer/pgbouncer.ini
[databases]
mass_db = host=127.0.0.1 port=5432 dbname=mass_db

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25

# Update DATABASE_URL to use pgBouncer
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:6432/mass_db
```

---

## Model Files Storage

### Local Storage

```bash
# Directory structure
models/
├── empathy_model.pkl
├── empathy_features.pkl
├── problem_solving_model.pkl
├── problem_solving_features.pkl
├── self_regulation_model.pkl
├── self_regulation_features.pkl
├── resilience_model.pkl
├── resilience_features.pkl
└── metadata.json
```

### Google Cloud Storage (Production)

```bash
# Download models at container startup
# Add to Dockerfile:
RUN mkdir -p /app/models && \
    gsutil -m cp -r gs://PROJECT_ID-models/v1.0.0/* /app/models/

# Or mount as volume in Cloud Run:
gcloud run services update mass-backend \
  --region=$REGION \
  --update-volumes=models=/app/models \
  --update-volume-mounts=models:models=ro
```

### Model Versioning

```json
// models/metadata.json
{
  "version": "1.0.0",
  "created_at": "2025-11-01T00:00:00Z",
  "models": {
    "empathy": {
      "checksum": "sha256:abc123...",
      "size_bytes": 524288,
      "accuracy": 0.87,
      "features": 26
    },
    "problem_solving": {
      "checksum": "sha256:def456...",
      "size_bytes": 512000,
      "accuracy": 0.89,
      "features": 26
    },
    "self_regulation": {
      "checksum": "sha256:ghi789...",
      "size_bytes": 498432,
      "accuracy": 0.85,
      "features": 26
    },
    "resilience": {
      "checksum": "sha256:jkl012...",
      "size_bytes": 505600,
      "accuracy": 0.88,
      "features": 26
    }
  }
}
```

---

## Health Checks & Monitoring

### Health Check Endpoint

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Response
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-11-13T10:30:00Z",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "models_loaded": 4,
    "openai_api": "configured"
  }
}
```

### Cloud Run Health Checks

```bash
# Health check configuration (automatic in Dockerfile)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1
```

### Metrics Collection

```bash
# Prometheus metrics endpoint
curl http://localhost:8000/metrics

# Metrics include:
# - inference_latency_seconds (histogram)
# - inference_requests_total (counter)
# - active_connections (gauge)
# - model_predictions_total (counter by skill)
```

### Cloud Monitoring (GCP)

```bash
# Set up log-based metrics
gcloud logging metrics create inference_errors \
  --description="Count of inference errors" \
  --log-filter='resource.type="cloud_run_revision"
    AND severity>=ERROR
    AND jsonPayload.service="inference"'

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

### Application Performance Monitoring (Optional)

**New Relic:**
```bash
# Add to requirements.txt
newrelic

# Add to Docker entrypoint
CMD ["newrelic-admin", "run-program", "uvicorn", "app.main:app", ...]
```

**DataDog:**
```bash
# Add to requirements.txt
ddtrace

# Add to Docker entrypoint
CMD ["ddtrace-run", "uvicorn", "app.main:app", ...]
```

---

## Backup & Disaster Recovery

### Database Backups

**Automated Backups (Cloud SQL):**
```bash
# Configure automated backups (already set in creation)
gcloud sql instances patch mass-db \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery

# Create on-demand backup
gcloud sql backups create \
  --instance=mass-db \
  --description="Pre-deployment backup"

# List backups
gcloud sql backups list --instance=mass-db

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=mass-db \
  --backup-id=BACKUP_ID
```

**Manual Backups:**
```bash
# Dump database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore database
psql $DATABASE_URL < backup_20251113.sql
```

### Model Files Backup

```bash
# Versioned storage in GCS
gsutil -m cp -r models/* gs://PROJECT_ID-models/v1.0.0/

# Cross-region replication
gsutil -m rsync -r \
  gs://PROJECT_ID-models/ \
  gs://PROJECT_ID-models-backup/
```

### Configuration Backup

```bash
# Backup fusion config
gsutil cp config/fusion_weights.json \
  gs://PROJECT_ID-config/fusion_weights_$(date +%Y%m%d).json

# Version control (Git)
git add config/fusion_weights.json
git commit -m "Update fusion weights"
git push
```

### Disaster Recovery Plan

**Recovery Time Objective (RTO):** < 1 hour
**Recovery Point Objective (RPO):** < 1 hour

**Recovery Steps:**
1. Spin up new Cloud SQL instance from latest backup (15 min)
2. Deploy latest Cloud Run service (5 min)
3. Update DNS to point to new service (5-30 min)
4. Verify functionality with smoke tests (10 min)

---

## Scaling Configuration

### Vertical Scaling (Cloud Run)

```bash
# Update resource limits
gcloud run services update mass-backend \
  --region=$REGION \
  --cpu=4 \
  --memory=8Gi \
  --concurrency=100
```

**Recommended Configurations:**

| Load Level | CPU | Memory | Concurrency | Min Instances | Max Instances |
|------------|-----|--------|-------------|---------------|---------------|
| Small      | 1   | 2Gi    | 40          | 0             | 3             |
| Medium     | 2   | 4Gi    | 80          | 1             | 10            |
| Large      | 4   | 8Gi    | 100         | 2             | 25            |
| X-Large    | 8   | 16Gi   | 120         | 5             | 50            |

### Horizontal Scaling (Cloud Run)

```bash
# Configure autoscaling
gcloud run services update mass-backend \
  --region=$REGION \
  --min-instances=2 \
  --max-instances=25 \
  --cpu-throttling \
  --no-use-http2
```

**Autoscaling Triggers:**
- CPU utilization > 60%
- Concurrent requests > 80% of concurrency limit
- Request latency > 1000ms

### Database Scaling

**Read Replicas:**
```bash
# Create read replica
gcloud sql instances create mass-db-replica \
  --master-instance-name=mass-db \
  --tier=db-custom-2-7680 \
  --region=$REGION

# Use replica for read queries
DATABASE_READ_URL=postgresql+asyncpg://user:pass@replica-host/mass_db
```

**Connection Pooling:**
- Use pgBouncer for high connection count
- Configure max connections based on instance size
- Monitor connection usage

### Redis Scaling

```bash
# Upgrade Redis instance
gcloud redis instances update mass-redis \
  --region=$REGION \
  --size=10

# Scale to larger tier
gcloud redis instances update mass-redis \
  --region=$REGION \
  --tier=STANDARD_HA \
  --size=20
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failures

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
FATAL: remaining connection slots are reserved
```

**Solutions:**
```bash
# Check current connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Increase max connections
gcloud sql instances patch mass-db \
  --database-flags=max_connections=200

# Reduce application pool size
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

#### 2. Redis Connection Timeouts

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions:**
```bash
# Check Redis connectivity
redis-cli -h REDIS_HOST -p 6379 ping

# Verify network (GCP)
gcloud compute networks vpc-access connectors list

# Fall back to in-memory metrics
# (automatic in MetricsStore)
```

#### 3. Model Loading Failures

**Symptoms:**
```
FileNotFoundError: Model not found: empathy_model.pkl
```

**Solutions:**
```bash
# Verify models directory
ls -lh $MODELS_DIR

# Download models
gsutil -m cp -r gs://PROJECT_ID-models/v1.0.0/* $MODELS_DIR/

# Check permissions
chmod -R 755 $MODELS_DIR
```

#### 4. OpenAI API Rate Limits

**Symptoms:**
```
openai.error.RateLimitError: Rate limit exceeded
```

**Solutions:**
```python
# Already implemented: Token bucket rate limiter
# Configure limits:
GPT4_CALLS_PER_MINUTE = 50
GPT4_CALLS_PER_HOUR = 500

# Fallback to templates
# (automatic in ReasoningGeneratorService)

# Monitor rate limit usage
curl http://localhost:8000/api/v1/metrics/summary
```

#### 5. High Memory Usage

**Symptoms:**
```
Container killed due to memory limit (OOMKilled)
```

**Solutions:**
```bash
# Increase Cloud Run memory
gcloud run services update mass-backend \
  --region=$REGION \
  --memory=8Gi

# Reduce connection pool sizes
DATABASE_POOL_SIZE=10
REDIS_MAX_CONNECTIONS=25

# Enable memory profiling
pip install memory_profiler
python -m memory_profiler app/main.py
```

#### 6. Slow Inference Performance

**Symptoms:**
```
Inference latency > 1000ms
```

**Solutions:**
```bash
# Check database query performance
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT ..."

# Verify indexes exist
psql $DATABASE_URL -c "\di"

# Enable query logging
gcloud sql instances patch mass-db \
  --database-flags=log_min_duration_statement=1000

# Optimize parallel queries (already implemented)
# See: app/services/skill_inference.py

# Scale up resources
gcloud run services update mass-backend --cpu=4 --memory=8Gi
```

### Logging & Debugging

**View Cloud Run logs:**
```bash
# Real-time logs
gcloud run services logs tail mass-backend \
  --region=$REGION

# Filter by severity
gcloud run services logs read mass-backend \
  --region=$REGION \
  --filter='severity>=ERROR' \
  --limit=50

# Search logs
gcloud logging read \
  'resource.type="cloud_run_revision" AND textPayload:"inference"' \
  --limit=10 \
  --format=json
```

**Local debugging:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug

# Profile performance
python -m cProfile -o profile.stats app/main.py
```

### Health Check Failures

```bash
# Check health endpoint
curl -v http://localhost:8000/api/v1/health

# Check dependencies
psql $DATABASE_URL -c "SELECT 1"
redis-cli -h REDIS_HOST ping
ls -lh $MODELS_DIR

# Verify environment variables
env | grep -E "DATABASE|REDIS|OPENAI"
```

---

## Security Checklist

### Pre-Deployment

- [ ] Rotate all secrets (JWT, API keys)
- [ ] Enable Cloud SQL SSL connections
- [ ] Configure VPC networks
- [ ] Set up Cloud Armor (DDoS protection)
- [ ] Enable Cloud Audit Logs
- [ ] Configure IAM least-privilege
- [ ] Review CORS origins
- [ ] Enable HTTPS only
- [ ] Set security headers

### Post-Deployment

- [ ] Verify health checks pass
- [ ] Test authentication flow
- [ ] Run security scan (e.g., OWASP ZAP)
- [ ] Monitor error rates
- [ ] Verify backups running
- [ ] Test disaster recovery
- [ ] Set up alerting
- [ ] Document runbook

---

## Support & Resources

### Documentation
- Architecture: `docs/ARCHITECTURE.md`
- Training Data: `docs/TRAINING_DATA_FORMAT.md`
- Performance: `docs/PERFORMANCE_TUNING.md`
- Evidence Normalization: `docs/EVIDENCE_NORMALIZATION.md`

### External Resources
- FastAPI Docs: https://fastapi.tiangolo.com/
- Cloud Run Docs: https://cloud.google.com/run/docs
- Cloud SQL Docs: https://cloud.google.com/sql/docs
- OpenAI API: https://platform.openai.com/docs

### Getting Help
- GitHub Issues: https://github.com/unseenedgeai/mass-backend/issues
- Internal Slack: #mass-backend
- On-call: mass-backend-oncall@unseenedgeai.com

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Deployment Status:** Production Ready ✅
