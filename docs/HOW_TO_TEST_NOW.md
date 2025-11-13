# How to Test Everything Right Now

**Date:** 2025-11-12
**Status:** Practical guide for testing current implementation
**Time Required:** 15-30 minutes for complete testing

---

## Quick Start - Test Everything in 5 Minutes

```bash
# 1. Run automated tests (2 minutes)
cd backend
source venv/bin/activate
pytest tests/ -v

# 2. Start the API (1 minute)
uvicorn app.main:app --reload &
sleep 3

# 3. Test health endpoints (30 seconds)
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/readiness

# 4. Test authentication (1 minute)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword"

# 5. Open Swagger UI (30 seconds)
open http://localhost:8000/docs  # macOS
# or xdg-open http://localhost:8000/docs  # Linux
```

---

## Part 1: Automated Testing (What's Already Working)

### 1.1 Run All Tests

```bash
cd backend
source venv/bin/activate

# Run all tests with verbose output
pytest tests/ -v

# Expected output:
# ✅ 20 tests PASSING
# ❌ 12 tests FAILING (database issues - known, fixable)
```

**What This Tests:**
- ✅ Health check endpoints (4 tests)
- ✅ CORS middleware (2 tests)
- ✅ API documentation endpoints (4 tests)
- ✅ Request/response middleware (4 tests)
- ✅ Transcription service unit tests (6 tests)

### 1.2 Run Specific Test Categories

```bash
# Only health checks
pytest tests/test_health.py -v

# Only middleware
pytest tests/test_middleware.py -v

# Only transcription (unit tests)
pytest tests/test_transcription.py -v -k "not (process_audio_file or get_transcript or upload_audio)"

# Only API endpoints
pytest tests/test_api_endpoints.py -v
```

### 1.3 Generate Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Open the report
open backend/htmlcov/index.html  # macOS
# or xdg-open backend/htmlcov/index.html  # Linux

# Expected coverage: 75% overall
```

**Coverage Highlights:**
- 🟢 100% - Health endpoints
- 🟢 100% - Middleware (request_id, logging)
- 🟢 93-100% - Database models
- 🟡 58% - Transcription service
- 🔴 44% - Authentication (needs tests)

---

## Part 2: Manual API Testing

### 2.1 Start the Backend Server

**Option A: Development Mode (with auto-reload)**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server starts at: http://localhost:8000
# Swagger UI at: http://localhost:8000/docs
# ReDoc at: http://localhost:8000/redoc
```

**Option B: Production-like Mode**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify Server Started:**
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","version":"0.1.0",...}
```

### 2.2 Test with Swagger UI (Recommended - Easiest)

**Access:** http://localhost:8000/docs

**Step-by-Step Testing:**

#### Test 1: Health Checks
1. Find "health" section in Swagger UI
2. Click `GET /api/v1/health`
3. Click "Try it out"
4. Click "Execute"
5. ✅ Verify: Status 200, `"status": "healthy"`

#### Test 2: Authentication
1. Find "auth" section
2. Click `POST /api/v1/auth/login`
3. Click "Try it out"
4. Fill in:
   - `username`: `test@example.com`
   - `password`: `testpassword`
5. Click "Execute"
6. ✅ Verify: Status 200, get `access_token` and `refresh_token`
7. Copy the `access_token` value

#### Test 3: Authenticated Endpoints
1. Click the "Authorize" button at top of Swagger UI
2. Paste token in format: `Bearer YOUR_TOKEN_HERE`
3. Click "Authorize"
4. Click "Close"
5. Try `GET /api/v1/auth/me`
6. Click "Try it out" → "Execute"
7. ✅ Verify: Status 200, see user info

#### Test 4: Audio Upload (Requires Auth)
1. Ensure you're authenticated (green lock icon)
2. Find `POST /api/v1/audio/upload`
3. Click "Try it out"
4. Fill in:
   - `file`: Upload a test audio file (WAV, MP3)
   - `student_id`: `student-123`
   - `source_type`: `classroom`
5. Click "Execute"
6. ✅ Verify: Status 201, get audio file metadata

**Note:** This will fail if Google Cloud credentials aren't configured. That's expected for local testing.

### 2.3 Test with cURL (Command Line)

Create a test script:

```bash
# Save as: test_api.sh
#!/bin/bash

echo "🧪 Testing MASS Platform API"
echo "================================"

API_BASE="http://localhost:8000"

# Test 1: Health Check
echo -e "\n1️⃣ Testing Health Check..."
HEALTH=$(curl -s "$API_BASE/api/v1/health")
echo "$HEALTH" | jq '.'
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Detailed Health
echo -e "\n2️⃣ Testing Detailed Health..."
curl -s "$API_BASE/api/v1/health/detailed" | jq '.'

# Test 3: Authentication
echo -e "\n3️⃣ Testing Authentication..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "✅ Login successful"
    echo "Token: ${TOKEN:0:20}..."
else
    echo "❌ Login failed"
    echo "$LOGIN_RESPONSE" | jq '.'
    exit 1
fi

# Test 4: Get Current User
echo -e "\n4️⃣ Testing Get Current User..."
USER_INFO=$(curl -s -X GET "$API_BASE/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")
echo "$USER_INFO" | jq '.'

if echo "$USER_INFO" | jq -e '.id' > /dev/null; then
    echo "✅ Get user info passed"
else
    echo "❌ Get user info failed"
fi

# Test 5: Refresh Token
echo -e "\n5️⃣ Testing Token Refresh..."
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh_token')
REFRESH_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/refresh?refresh_token=$REFRESH_TOKEN")
echo "$REFRESH_RESPONSE" | jq '.'

# Test 6: Logout
echo -e "\n6️⃣ Testing Logout..."
LOGOUT_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/logout" \
  -H "Authorization: Bearer $TOKEN")
echo "$LOGOUT_RESPONSE" | jq '.'

# Test 7: OpenAPI Schema
echo -e "\n7️⃣ Testing OpenAPI Schema..."
OPENAPI=$(curl -s "$API_BASE/openapi.json")
if echo "$OPENAPI" | jq -e '.openapi' > /dev/null; then
    echo "✅ OpenAPI schema available"
    echo "Endpoints: $(echo "$OPENAPI" | jq '.paths | keys | length')"
else
    echo "❌ OpenAPI schema failed"
fi

echo -e "\n✅ All tests completed!"
```

**Run the script:**
```bash
chmod +x test_api.sh
./test_api.sh
```

### 2.4 Test Individual Endpoints with cURL

```bash
# Set base URL
API="http://localhost:8000"

# 1. Health Check
curl -X GET "$API/api/v1/health" | jq '.'

# 2. Readiness Probe
curl -X GET "$API/api/v1/readiness" | jq '.'

# 3. Liveness Probe
curl -X GET "$API/api/v1/liveness" | jq '.'

# 4. Login and Save Token
TOKEN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 5. Get Current User
curl -X GET "$API/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 6. Test CORS (from different origin)
curl -X OPTIONS "$API/api/v1/health" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep -i "access-control"

# 7. OpenAPI Specification
curl -X GET "$API/openapi.json" | jq '.info'

# 8. Swagger UI (open in browser)
open "$API/docs"

# 9. ReDoc (alternative documentation)
open "$API/redoc"
```

---

## Part 3: Database Testing

### 3.1 Check Database Connection

**Local PostgreSQL (if running):**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Connect to database
psql -h localhost -p 5432 -U mass_api -d mass_db

# Inside psql:
\dt  -- List tables
SELECT COUNT(*) FROM students;  -- Check students table
SELECT COUNT(*) FROM audio_files;  -- Check audio files
\q  -- Quit
```

**Cloud SQL (production):**
```bash
# Via Cloud SQL Proxy
gcloud sql connect unseenedgeai-db-production --user=mass_api

# Or check connection in Python
cd backend
python -c "
from app.core.database import engine
import asyncio

async def test_connection():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT 1')
        print('✅ Database connection successful')

asyncio.run(test_connection())
"
```

### 3.2 Run Database Migrations

```bash
cd backend

# Check current migration status
alembic current

# Run migrations
alembic upgrade head

# Check migration history
alembic history

# Downgrade if needed
alembic downgrade -1
```

### 3.3 Test Database Models

```bash
# Test model imports
python -c "
from app.models import *
from app.models.base import Base

print('Registered tables:')
for table in Base.metadata.sorted_tables:
    print(f'  ✅ {table.name}')
"

# Expected output: 14 tables
# students, teachers, schools, users, audio_files, transcripts, etc.
```

---

## Part 4: Infrastructure Testing

### 4.1 Test Google Cloud Services

```bash
# Check GCP authentication
gcloud auth list

# Test Cloud Run deployment
gcloud run services describe mass-api \
  --region=us-central1 \
  --project=unseenedgeai

# Test health endpoint on production
curl https://mass-api-w7d2tjlzyq-uc.a.run.app/api/v1/health

# Test Cloud SQL connection
gcloud sql instances describe unseenedgeai-db-production

# List Cloud Storage buckets
gsutil ls

# Check Cloud Tasks queues
gcloud tasks queues list

# Check Pub/Sub topics
gcloud pubsub topics list
```

### 4.2 Test Docker Build

```bash
cd backend

# Build Docker image
docker build -t mass-api:test .

# Run container locally
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e GOOGLE_CLOUD_PROJECT="unseenedgeai" \
  mass-api:test

# Test container
curl http://localhost:8000/api/v1/health

# Stop container
docker ps  # Get container ID
docker stop <container_id>
```

---

## Part 5: Performance Testing

### 5.1 Load Testing with Apache Bench

```bash
# Install Apache Bench (if needed)
# macOS: brew install httpd
# Linux: apt-get install apache2-utils

# Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# Test with authentication
ab -n 100 -c 10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me

# Expected results:
# - Time per request: < 50ms
# - Requests per second: > 200
# - Failed requests: 0
```

### 5.2 Stress Testing with wrk

```bash
# Install wrk (if needed)
# macOS: brew install wrk
# Linux: apt-get install wrk

# Basic load test (30 seconds, 10 connections)
wrk -t10 -c10 -d30s http://localhost:8000/api/v1/health

# With authentication
wrk -t10 -c10 -d30s \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/auth/me

# Expected results:
# - Latency: < 10ms
# - Requests/sec: > 1000
# - No errors
```

---

## Part 6: Security Testing

### 6.1 Test Authentication Security

```bash
# Test 1: Access protected endpoint without token (should fail)
curl -X GET http://localhost:8000/api/v1/auth/me
# Expected: 401 Unauthorized

# Test 2: Access with invalid token (should fail)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized

# Test 3: Login with wrong credentials (should fail)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=wrong@email.com&password=wrongpassword"
# Expected: 401 Unauthorized

# Test 4: Check token expiration
# Wait for token to expire (default 60 minutes)
# Then try to use it (should fail with 401)
```

### 6.2 Test CORS Security

```bash
# Test allowed origin
curl -X OPTIONS http://localhost:8000/api/v1/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep "access-control-allow-origin"
# Expected: http://localhost:3000

# Test disallowed origin
curl -X OPTIONS http://localhost:8000/api/v1/health \
  -H "Origin: http://evil-site.com" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep "access-control-allow-origin"
# Expected: No CORS headers
```

---

## Part 7: Test Checklist

### Daily Development Testing
- [ ] Run `pytest tests/ -v` (should have 20 passing)
- [ ] Check `http://localhost:8000/docs` loads
- [ ] Test login flow in Swagger UI
- [ ] Verify health endpoints respond

### Before Committing Code
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Linters pass: `black . && flake8`
- [ ] Coverage acceptable: `pytest --cov=app`
- [ ] Manual test in Swagger UI

### Before Deploying
- [ ] All tests pass locally
- [ ] Docker build succeeds: `docker build -t test .`
- [ ] Health check works: `curl http://localhost:8000/api/v1/health`
- [ ] Database migrations current: `alembic current`

### Weekly Testing
- [ ] Run full test suite with coverage report
- [ ] Test production deployment health
- [ ] Check Cloud SQL connection
- [ ] Verify Cloud Storage accessible
- [ ] Review test failures and fix

---

## Part 8: Troubleshooting

### Tests Failing?

**Problem: "no such table: students"**
```bash
# Fix: Database not initialized
cd backend
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"
```

**Problem: "Google Cloud credentials not found"**
```bash
# Fix: Set credentials for local testing
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Or mock in tests (already done in test_transcription.py)
```

**Problem: "Connection refused to localhost:8000"**
```bash
# Fix: Server not running
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Problem: "ModuleNotFoundError"**
```bash
# Fix: Dependencies not installed
cd backend
pip install -r requirements.txt
```

### Server Not Starting?

```bash
# Check port not in use
lsof -i :8000
# Kill process if needed: kill -9 <PID>

# Check Python version (need 3.11+)
python --version

# Check virtual environment active
which python
# Should show: .../backend/venv/bin/python

# Check DATABASE_URL set
grep DATABASE_URL backend/.env
# Should use postgresql+asyncpg://
```

---

## Part 9: Quick Test Recipes

### Recipe 1: "I just pulled latest code"
```bash
cd backend
pip install -r requirements.txt  # Get new dependencies
pytest tests/ -v                  # Run tests
uvicorn app.main:app --reload     # Start server
open http://localhost:8000/docs   # Test manually
```

### Recipe 2: "I changed the API"
```bash
pytest tests/ -v                          # Run all tests
pytest tests/test_api_endpoints.py -v     # Test specific endpoints
open http://localhost:8000/docs           # Test in Swagger UI
curl http://localhost:8000/openapi.json   # Check OpenAPI schema
```

### Recipe 3: "I'm deploying to production"
```bash
# Local testing first
pytest tests/ -v
docker build -t mass-api:test .
docker run -p 8000:8000 mass-api:test

# Then deploy
gcloud run deploy mass-api --source . --region us-central1

# Verify deployment
curl https://mass-api-<hash>.run.app/api/v1/health
```

### Recipe 4: "I want to see code coverage"
```bash
cd backend
pytest tests/ --cov=app --cov-report=html --cov-report=term
open htmlcov/index.html  # View in browser

# Focus on specific module
pytest tests/ --cov=app.api.endpoints.auth --cov-report=term
```

### Recipe 5: "I need to test performance"
```bash
# Start server
uvicorn app.main:app --workers 4 &

# Quick load test
ab -n 1000 -c 50 http://localhost:8000/api/v1/health

# Or with wrk
wrk -t10 -c100 -d30s http://localhost:8000/api/v1/health
```

---

## Part 10: What You Can't Test Yet

### ❌ Features Not Implemented
- **Feature Extraction Service** (Task 10 - next)
- **Skills Inference** (requires ML models)
- **Student CRUD operations** (endpoints exist, no integration tests)
- **Teacher CRUD operations** (endpoints exist, no integration tests)
- **Game telemetry processing** (endpoint exists, no tests)
- **Real audio transcription** (requires Google Cloud setup)

### ❌ Tests That Need Fixing
- Database integration tests (12 tests failing due to SQLite session issues)
- Authentication endpoint tests (0 tests written - HIGH PRIORITY)
- Transcription integration tests (need real database)

### ⏳ Coming Soon
- End-to-end tests
- Frontend testing (when UI built)
- Contract testing (Pact)
- Visual regression testing

---

## Summary: Testing Status

### ✅ What Works (Test This Now)
| Category | Method | Status |
|----------|--------|--------|
| Health Endpoints | Automated tests | ✅ 4/4 passing |
| CORS Middleware | Automated tests | ✅ 2/2 passing |
| API Documentation | Automated tests | ✅ 4/4 passing |
| Middleware | Automated tests | ✅ 4/4 passing |
| Transcription Service | Unit tests (mocked) | ✅ 6/6 passing |
| Manual API Testing | Swagger UI | ✅ Works great |
| Manual API Testing | cURL | ✅ Works great |
| Production Deployment | Cloud Run | ✅ Healthy |

### ⚠️ What Needs Work
| Category | Issue | Priority |
|----------|-------|----------|
| Authentication Tests | 0 tests written | 🔴 HIGH |
| Database Tests | 12 tests failing (SQLite) | 🟡 MEDIUM |
| Integration Tests | Need real database | 🟡 MEDIUM |
| Transcription Integration | Need GCP setup | 🟢 LOW |

### 🎯 Next Steps
1. **Run tests right now:** `cd backend && pytest tests/ -v`
2. **Manual test with Swagger:** http://localhost:8000/docs
3. **Write auth tests** (high priority, high security value)
4. **Fix database test fixtures** (unblocks 12 tests)

---

## Quick Reference Commands

```bash
# Start Testing
cd backend && source venv/bin/activate

# Essential Tests
pytest tests/ -v                                    # All tests
pytest tests/test_health.py -v                      # Health only
pytest --cov=app --cov-report=html                  # With coverage

# Manual Testing
uvicorn app.main:app --reload                       # Start server
curl http://localhost:8000/api/v1/health            # Quick test
open http://localhost:8000/docs                     # Swagger UI

# Production Testing
curl https://mass-api-w7d2tjlzyq-uc.a.run.app/api/v1/health

# Database
alembic upgrade head                                # Run migrations
alembic current                                     # Check status

# Performance
ab -n 100 -c 10 http://localhost:8000/api/v1/health
wrk -t10 -c10 -d30s http://localhost:8000/api/v1/health

# Coverage Report
pytest --cov=app --cov-report=html && open htmlcov/index.html
```

---

**Ready to test?** Start with: `cd backend && pytest tests/ -v` 🧪
