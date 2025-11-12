# MASS Backend API

FastAPI backend for the Middle School Non-Academic Skills Measurement System (MASS).

## Features

- **FastAPI** framework with async support
- **JWT authentication** with OAuth2
- **Role-based access control** (RBAC)
- **Telemetry ingestion** for game events
- **Health checks** for Kubernetes
- **Structured logging** with request tracing
- **OpenAPI documentation** (Swagger/ReDoc)
- **Docker containerization**

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Google Cloud SDK (for GCP services)

### Installation

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**:
```bash
uvicorn app.main:app --reload --port 8080
```

5. **Access the API**:
- API: http://localhost:8080
- Swagger docs: http://localhost:8080/api/v1/docs
- ReDoc: http://localhost:8080/api/v1/redoc

## Docker

### Build image:
```bash
docker build -t mass-backend:latest .
```

### Run container:
```bash
docker run -p 8080:8080 --env-file .env mass-backend:latest
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Health
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check
- `GET /api/v1/readiness` - Kubernetes readiness probe
- `GET /api/v1/liveness` - Kubernetes liveness probe

### Telemetry
- `POST /api/v1/telemetry/events` - Ingest single event
- `POST /api/v1/telemetry/batch` - Ingest event batch
- `GET /api/v1/telemetry/status/{batch_id}` - Get batch status

### Students
- `GET /api/v1/students` - List students
- `GET /api/v1/students/{student_id}` - Get student details

### Skills
- `GET /api/v1/skills/{student_id}` - Get student skill profile
- `GET /api/v1/skills/{student_id}/history` - Get skill history
- `GET /api/v1/skills/{student_id}/{skill_name}/evidence` - Get evidence

## Development

### Running tests:
```bash
pytest
```

### Code formatting:
```bash
black app/
```

### Linting:
```bash
flake8 app/
mypy app/
```

### Type checking:
```bash
mypy app/
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/     # API route handlers
│   │   ├── middleware/    # Custom middleware
│   │   └── dependencies/  # Dependency injection
│   ├── core/
│   │   └── config.py      # Configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # Application entry point
├── tests/                 # Test suite
├── Dockerfile
├── requirements.txt
└── README.md
```

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - JWT signing key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `OPENAI_API_KEY` - OpenAI API key

## Deployment

### Google Cloud Run:
```bash
gcloud run deploy mass-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=unseenedgeai"
```

### Kubernetes:
```bash
kubectl apply -f k8s/deployment.yaml
```

## Authentication

The API uses JWT tokens for authentication:

1. Login with credentials to get access and refresh tokens
2. Include access token in requests: `Authorization: Bearer <token>`
3. Refresh tokens when access token expires

## Rate Limiting

Rate limiting is enforced at 60 requests per minute per user.

## Monitoring

- Prometheus metrics: `/metrics`
- Health checks: `/api/v1/health`
- Request tracing via `X-Request-ID` header

## Support

For issues or questions, contact the development team.
