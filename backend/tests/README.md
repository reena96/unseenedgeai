# Testing Guide

## Overview

This directory contains the test suite for the MASS API backend. The tests cover:
- API endpoints (health, auth, transcription, etc.)
- CORS middleware
- Request tracking
- Error handling
- Database integration

## Test Results

**Current Status:**
- ✅ **20/32 tests passing** (62.5%)
- ⚠️ **12 tests failing** (database integration tests with SQLite)
- ✅ **80% code coverage**

## Quick Start

### Run All Tests (SQLite - Fast)
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Run All Tests (PostgreSQL - Full Integration)
```bash
# Requires Docker running
cd backend
source venv/bin/activate
USE_POSTGRES_TESTS=true pytest tests/ -v
```

### Run Specific Test Files
```bash
# Health tests only
pytest tests/test_health.py -v

# Auth tests only
pytest tests/test_api_endpoints.py -v

# Transcription tests only
pytest tests/test_transcription.py -v
```

### Run With Coverage
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Test Database Options

### Option 1: SQLite (Default - Fast)

**Pros:**
- ✅ Fast (< 5 seconds)
- ✅ No Docker required
- ✅ No external dependencies
- ✅ Good for unit tests

**Cons:**
- ⚠️ 12 database integration tests fail
- ⚠️ SQLite session lifecycle differs from PostgreSQL
- ⚠️ Some SQL features not supported

**Usage:**
```bash
pytest tests/ -v
```

### Option 2: PostgreSQL Test Container (Recommended for Integration Tests)

**Pros:**
- ✅ All 32 tests pass
- ✅ Identical to production database
- ✅ Tests real database behavior
- ✅ Automatic container management

**Cons:**
- ⚠️ Slower (15-30 seconds first run)
- ⚠️ Requires Docker running
- ⚠️ Uses more resources

**Usage:**
```bash
# One-time setup: Ensure Docker is running
docker ps

# Run tests
USE_POSTGRES_TESTS=true pytest tests/ -v
```

## Database Integration Tests

The 12 failing tests (with SQLite) are:

### Transcription Service Tests (6 tests)
- `test_process_audio_file_success`
- `test_process_audio_file_not_found`
- `test_process_audio_file_already_transcribed`
- `test_process_audio_file_failure`
- `test_get_transcript_success`
- `test_get_transcript_not_found`

### Transcription Endpoint Tests (6 tests)
- `test_upload_audio_success`
- `test_upload_audio_student_not_found`
- `test_start_transcription_success`
- `test_get_transcript_success`
- `test_get_transcription_status`
- `test_list_student_audio`

**Root Cause:** SQLite in-memory database has different session lifecycle than PostgreSQL, causing "no such table" errors in async tests.

**Solutions:**
1. **Use PostgreSQL test container** (recommended):
   ```bash
   USE_POSTGRES_TESTS=true pytest tests/ -v
   ```

2. **Skip integration tests** (for quick feedback):
   ```bash
   pytest tests/ -v -m "not integration"
   ```

3. **Fix SQLite session scoping** (complex, not recommended)

## Test Organization

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_api_endpoints.py          # Root, docs, OpenAPI tests
├── test_cors.py                   # CORS middleware tests
├── test_health.py                 # Health monitoring tests
├── test_middleware.py             # Request tracking, error handling
├── test_transcription.py          # Transcription service & endpoints
└── README.md                      # This file
```

## Fixtures Available

### API Testing
- `client` - FastAPI TestClient for HTTP requests
- `valid_access_token` - JWT token for authenticated requests
- `auth_headers` - Pre-formatted Authorization headers

### Database Testing
- `test_engine` - AsyncIO database engine (SQLite or PostgreSQL)
- `db_session` - Database session with transaction rollback
- `postgres_container` - PostgreSQL test container (when enabled)

### Example Usage
```python
def test_protected_endpoint(client, auth_headers):
    """Test endpoint requires authentication."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200

async def test_database_operation(db_session):
    """Test database operation."""
    user = User(email="test@example.com", role="teacher")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User))
    assert result.scalar_one().email == "test@example.com"
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests with PostgreSQL
        env:
          USE_POSTGRES_TESTS: true
        run: |
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Seed Database for Manual Testing

To populate the database with test data:

```bash
cd backend
source venv/bin/activate

# Seed with sample data
python scripts/seed_data.py

# Clear and re-seed
python scripts/seed_data.py --clear
```

This creates:
- 3 schools
- 4 teachers
- 10 students
- 10 audio files
- 6 game sessions
- Sample assessments

## Troubleshooting

### "Docker not running" Error
```bash
# Start Docker Desktop or Docker daemon
# On Mac:
open /Applications/Docker.app

# Verify Docker is running:
docker ps
```

### "No such table" Errors with SQLite
This is expected. Use PostgreSQL test container:
```bash
USE_POSTGRES_TESTS=true pytest tests/ -v
```

### "Import errors" or "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov testcontainers[postgres]
```

### Tests Hanging
- Check if Docker container is stuck
- Kill and restart:
```bash
docker ps
docker kill <container_id>
pytest tests/ -v
```

### Slow First Run with PostgreSQL
- First run downloads PostgreSQL image (~100MB)
- Subsequent runs use cached image (much faster)
- Image is pulled once per machine

## Performance Benchmarks

| Test Configuration | Duration | Tests Passing |
|-------------------|----------|---------------|
| SQLite (default) | ~5 seconds | 20/32 (62.5%) |
| PostgreSQL container | ~15-30 seconds | 32/32 (100%) |
| PostgreSQL (cached) | ~10-15 seconds | 32/32 (100%) |

## Best Practices

### During Development
1. Use SQLite for quick feedback (unit tests)
2. Run PostgreSQL tests before committing
3. Check coverage regularly: `pytest --cov=app`

### Before Pull Request
1. Run all tests with PostgreSQL: `USE_POSTGRES_TESTS=true pytest tests/ -v`
2. Ensure 100% pass rate
3. Check coverage is > 80%

### In CI/CD
1. Always use PostgreSQL container
2. Run tests on every commit
3. Block merges if tests fail

## Writing New Tests

### Unit Test Template
```python
def test_example_unit(client):
    """Test description."""
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Integration Test Template
```python
@pytest.mark.integration
async def test_example_integration(db_session):
    """Test description."""
    # Create test data
    obj = Model(field="value")
    db_session.add(obj)
    await db_session.commit()

    # Test operation
    result = await db_session.execute(select(Model))
    assert result.scalar_one().field == "value"
```

### Async Test Template
```python
@pytest.mark.asyncio
async def test_example_async():
    """Test description."""
    result = await async_function()
    assert result == expected
```

## Next Steps

1. ✅ **Run tests with PostgreSQL** to see all tests pass
2. ✅ **Seed database** for manual testing
3. ⏳ **Add more auth tests** (increase coverage to 90%+)
4. ⏳ **Add E2E tests** for complete workflows
5. ⏳ **Set up CI/CD** with automated testing

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [testcontainers-python](https://testcontainers-python.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
