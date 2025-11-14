# Teacher Dashboard Deployment Guide

## Quick Start

### Local Development

```bash
# 1. Install dependencies
cd backend
pip install -r dashboard/requirements.txt

# 2. Start the backend API (if not already running)
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. In a new terminal, start the dashboard
streamlit run dashboard/app_template.py
```

The dashboard will be available at `http://localhost:8501`

## Docker Deployment

### Build Image

```bash
cd backend/dashboard
docker build -t teacher-dashboard:latest -f Dockerfile .
```

### Run Container

```bash
docker run -p 8501:8501 \
  -e API_URL=http://host.docker.internal:8000/api/v1 \
  teacher-dashboard:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mass
    depends_on:
      - db

  dashboard:
    build: ./backend/dashboard
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000/api/v1
    depends_on:
      - backend

  db:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Run with:
```bash
docker-compose up -d
```

## Google Cloud Platform Deployment

### Cloud Run

#### 1. Build and Push Image

```bash
# Set project ID
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/teacher-dashboard ./backend/dashboard

# Or use Cloud Build config
gcloud builds submit --config=backend/dashboard/cloudbuild.yaml
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy teacher-dashboard \
  --image gcr.io/$PROJECT_ID/teacher-dashboard \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8501 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars API_URL=https://your-backend-api.run.app/api/v1
```

#### 3. Configure Authentication (Production)

```bash
# Deploy with authentication required
gcloud run deploy teacher-dashboard \
  --image gcr.io/$PROJECT_ID/teacher-dashboard \
  --platform managed \
  --region $REGION \
  --no-allow-unauthenticated \
  --port 8501

# Add IAM binding for specific users
gcloud run services add-iam-policy-binding teacher-dashboard \
  --member='user:teacher@school.edu' \
  --role='roles/run.invoker' \
  --region $REGION
```

### App Engine (Alternative)

```yaml
# app.yaml
runtime: python311
entrypoint: streamlit run dashboard/app_template.py --server.port $PORT

env_variables:
  API_URL: "https://your-backend.appspot.com/api/v1"

automatic_scaling:
  min_instances: 0
  max_instances: 5
  target_cpu_utilization: 0.65
```

Deploy:
```bash
gcloud app deploy app.yaml --project $PROJECT_ID
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_URL` | Backend API base URL | `http://localhost:8000/api/v1` | Yes |
| `STREAMLIT_SERVER_PORT` | Dashboard port | `8501` | No |
| `STREAMLIT_SERVER_ADDRESS` | Bind address | `0.0.0.0` | No |
| `STREAMLIT_THEME_BASE` | UI theme | `light` | No |

## Production Considerations

### Security

1. **Enable Authentication**
   ```python
   # In app_template.py
   import streamlit_authenticator as stauth

   authenticator = stauth.Authenticate(
       names=['Teacher One', 'Teacher Two'],
       usernames=['teacher1', 'teacher2'],
       passwords=['hashed_pw1', 'hashed_pw2'],
       cookie_name='teacher_dashboard',
       key='your_secret_key',
       cookie_expiry_days=30
   )

   name, authentication_status, username = authenticator.login('Login', 'main')

   if authentication_status:
       st.write(f'Welcome *{name}*')
       # Dashboard content
   ```

2. **HTTPS Only**
   - Cloud Run provides HTTPS by default
   - For custom domains, use Cloud Load Balancer with SSL

3. **API Key Management**
   - Store API keys in Secret Manager
   - Use workload identity for service-to-service auth

### Performance

1. **Caching**
   ```python
   @st.cache_data(ttl=300)  # Cache for 5 minutes
   def get_students():
       return api.get_students()
   ```

2. **Connection Pooling**
   - Configure `requests.Session()` with connection pooling
   - Use persistent HTTP connections

3. **Resource Limits**
   - Set appropriate memory and CPU limits
   - Monitor Cloud Run metrics

### Monitoring

1. **Cloud Logging**
   ```python
   import logging
   from google.cloud import logging as cloud_logging

   client = cloud_logging.Client()
   client.setup_logging()
   ```

2. **Custom Metrics**
   ```python
   from google.cloud import monitoring_v3

   def record_dashboard_access():
       # Send custom metric
       pass
   ```

3. **Health Checks**
   ```python
   # Add health check endpoint
   @app.route('/health')
   def health():
       return {'status': 'healthy'}
   ```

## Troubleshooting

### Dashboard Won't Start

```bash
# Check if port 8501 is already in use
lsof -ti:8501 | xargs kill -9

# Run with debug mode
streamlit run dashboard/app_template.py --logger.level=debug
```

### API Connection Issues

```bash
# Test API connectivity
curl $API_URL/health

# Check firewall rules (GCP)
gcloud compute firewall-rules list

# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID
```

### Slow Performance

1. Check API response times
2. Enable caching for expensive operations
3. Reduce batch sizes
4. Increase Cloud Run memory/CPU

### Authentication Errors

```bash
# Check IAM bindings
gcloud run services get-iam-policy teacher-dashboard --region $REGION

# Test with curl
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://teacher-dashboard-xyz.run.app
```

## Scaling

### Horizontal Scaling

Cloud Run automatically scales based on:
- Request volume
- CPU utilization
- Memory usage

Configure:
```bash
gcloud run services update teacher-dashboard \
  --min-instances 1 \
  --max-instances 20 \
  --concurrency 80 \
  --region $REGION
```

### Cost Optimization

1. **Set minimum instances to 0** for development
2. **Use CPU throttling** during idle time
3. **Implement request caching** to reduce backend calls
4. **Monitor Cloud Run costs** with budgets and alerts

## Backup and Recovery

### Configuration Backup

```bash
# Export Cloud Run service config
gcloud run services describe teacher-dashboard \
  --region $REGION \
  --format yaml > dashboard-config-backup.yaml
```

### Restore

```bash
# Restore from backup
gcloud run services replace dashboard-config-backup.yaml \
  --region $REGION
```

## Updates and Rollbacks

### Rolling Update

```bash
# Deploy new version
gcloud run deploy teacher-dashboard \
  --image gcr.io/$PROJECT_ID/teacher-dashboard:v2 \
  --region $REGION

# Traffic splitting (canary deployment)
gcloud run services update-traffic teacher-dashboard \
  --to-revisions teacher-dashboard-v2=20 \
  --region $REGION
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service teacher-dashboard --region $REGION

# Rollback to previous revision
gcloud run services update-traffic teacher-dashboard \
  --to-revisions teacher-dashboard-v1=100 \
  --region $REGION
```

## Related Documentation

- [Teacher Dashboard README](../../frontend/teacher-dashboard/README.md)
- [API Documentation](../docs/ARCHITECTURE.md)
- [Security Guide](../docs/DEPLOYMENT.md)
