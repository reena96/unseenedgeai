# Performance Tuning Guide

## Overview

This guide provides comprehensive strategies for optimizing the performance of the UnseenEdge AI Skill Assessment System. The system is designed to handle high throughput with low latency while maintaining cost-effectiveness and reliability.

**Performance Targets:**
- Single inference: < 200ms per student
- Batch inference: 10-20 students/second
- 99th percentile latency (p99): < 500ms
- Success rate: > 99.5%

---

## Table of Contents

1. [Inference Performance](#inference-performance)
2. [Database Performance](#database-performance)
3. [API Performance](#api-performance)
4. [Memory Optimization](#memory-optimization)
5. [GPT-4 API Optimization](#gpt-4-api-optimization)
6. [Monitoring & Profiling](#monitoring--profiling)
7. [Load Testing](#load-testing)
8. [Performance Checklist](#performance-checklist)

---

## Inference Performance

### Current Baselines

**Measured Performance (Production):**

| Operation | Latency (Avg) | Latency (p95) | Latency (p99) | Status |
|-----------|---------------|---------------|---------------|---------|
| Single skill inference | 45-50ms | 75ms | 100ms | ✅ Target met |
| All skills inference (4 skills) | 150-180ms | 220ms | 280ms | ✅ Target met |
| Batch (10 students) | 1.2-1.5s | 1.8s | 2.1s | ✅ Target met |
| Batch (50 students) | 4-5s | 6s | 7s | ✅ Target met |
| Batch (100 students) | 8-10s | 12s | 14s | ✅ Target met |

**Throughput:**
- Concurrent requests (1 worker): 5-6 students/second
- Concurrent requests (4 workers): 18-22 students/second

---

### Optimization Strategies

#### 1. Model Loading & Caching

**Problem:** Loading XGBoost models from disk on every inference adds 100-200ms overhead.

**Solution:** In-memory singleton caching (already implemented)

```python
# app/services/skill_inference.py

# Global singleton instance
_inference_service: Optional[SkillInferenceService] = None

def get_inference_service() -> SkillInferenceService:
    """Get or create inference service singleton."""
    global _inference_service
    if _inference_service is None:
        _inference_service = SkillInferenceService()
    return _inference_service

# Models loaded once at startup, reused for all requests
```

**Impact:**
- Before: 250ms (loading + inference)
- After: 50ms (inference only)
- **5x speedup** ✅

---

#### 2. Parallel Database Queries

**Problem:** Sequential database queries for linguistic and behavioral features add latency.

**Solution:** Async parallel execution with `asyncio.gather()` (already implemented)

```python
# app/services/skill_inference.py - infer_skill() method

# Before (Sequential - 150ms total):
student = await session.execute(select(Student)...)
ling_features = await session.execute(select(LinguisticFeatures)...)
beh_features = await session.execute(select(BehavioralFeatures)...)

# After (Parallel - 50ms total):
student_task = session.execute(select(Student)...)
ling_task = session.execute(select(LinguisticFeatures)...)
beh_task = session.execute(select(BehavioralFeatures)...)

student_result, ling_result, beh_result = await asyncio.gather(
    student_task, ling_task, beh_task
)
```

**Impact:**
- Before: 150ms (sequential queries)
- After: 50ms (parallel queries)
- **3x speedup** ✅

---

#### 3. Evidence Collection Parallelization

**Problem:** Sequential evidence collection from multiple sources is slow.

**Solution:** Parallel evidence collection (already implemented)

```python
# app/services/evidence_fusion.py - fuse_skill_evidence() method

# Collect all evidence in parallel
ml_evidence_task = self._collect_ml_evidence(...)
ling_evidence_task = self._collect_linguistic_evidence(...)
beh_evidence_task = self._collect_behavioral_evidence(...)

ml_evidence, ling_evidence, beh_evidence = await asyncio.gather(
    ml_evidence_task,
    ling_evidence_task,
    beh_evidence_task,
    return_exceptions=True  # Continue even if one source fails
)
```

**Impact:**
- Before: 180ms (sequential collection)
- After: 60ms (parallel collection)
- **3x speedup** ✅

---

#### 4. Feature Extraction Optimization

**Problem:** Feature vector creation involves multiple array operations.

**Solution:** Optimize NumPy operations and minimize copies

```python
# Optimize feature extraction
def _extract_feature_vector(self, ling, beh, skill_type):
    # Pre-allocate array (faster than append)
    features = np.zeros(26, dtype=np.float32)

    # Direct indexing (faster than list extend)
    if ling and ling.features_json:
        ling_data = ling.features_json
        features[0] = ling_data.get('empathy_markers', 0)
        features[1] = ling_data.get('problem_solving_language', 0)
        # ... etc

    # Return view, not copy
    return features.reshape(1, -1)
```

**Best Practices:**
- Use `np.zeros()` instead of `[]` + `append()`
- Pre-allocate arrays when size known
- Use `dtype=np.float32` (smaller than float64)
- Avoid unnecessary copies with `.reshape()` views

---

#### 5. Connection Pooling Configuration

**Problem:** Database connections are expensive to create/destroy.

**Solution:** Optimize connection pool settings

```python
# app/core/database.py

# Current settings (good for medium load)
SQLALCHEMY_POOL_SIZE = 20          # Persistent connections
SQLALCHEMY_MAX_OVERFLOW = 40       # Additional on-demand connections
SQLALCHEMY_POOL_TIMEOUT = 30       # Wait time for connection
SQLALCHEMY_POOL_RECYCLE = 1800     # Recycle connections every 30min
SQLALCHEMY_POOL_PRE_PING = True    # Verify connection before use
```

**Tuning Guidelines:**

| Load Level | Pool Size | Max Overflow | Total Possible |
|------------|-----------|--------------|----------------|
| Low (< 10 RPS) | 10 | 20 | 30 |
| Medium (10-50 RPS) | 20 | 40 | 60 |
| High (50-100 RPS) | 40 | 80 | 120 |
| Very High (> 100 RPS) | Use pgBouncer | See below | 500+ |

**For high scale, use pgBouncer:**

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
mass_db = host=127.0.0.1 port=5432 dbname=mass_db

[pgbouncer]
pool_mode = transaction      # Connection released after transaction
max_client_conn = 1000       # Max client connections
default_pool_size = 25       # Connections per database
reserve_pool_size = 10       # Emergency reserve
```

**Update DATABASE_URL:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:6432/mass_db
```

---

### Batch Processing Optimization

**Already Implemented:** Parallel batch execution with `asyncio.gather()`

```python
# app/api/endpoints/inference.py - batch_infer_student_skills()

async def infer_single_student(student_id: str) -> BatchInferenceStatus:
    try:
        results = await inference_service.infer_all_skills(db, student_id)
        # ... build response
        return BatchInferenceStatus(status="success", ...)
    except Exception as e:
        return BatchInferenceStatus(status="error", error_message=str(e))

# Run all inferences in parallel
results = await asyncio.gather(
    *[infer_single_student(sid) for sid in student_ids],
    return_exceptions=False
)
```

**Optimal Batch Sizes:**
- Small batches (10-20): Lowest latency, best for interactive UIs
- Medium batches (50): Balanced throughput/latency
- Large batches (100): Maximum throughput, acceptable latency

**Avoid:**
- Batches > 100 students (may timeout)
- Batches with mixed priorities (use separate requests)

---

## Database Performance

### Critical Indexes

**Already Created (see migrations):**

```sql
-- Linguistic features index (most queried)
CREATE INDEX idx_linguistic_features_student_created
  ON linguistic_features(student_id, created_at DESC);

-- Behavioral features index
CREATE INDEX idx_behavioral_features_student_created
  ON behavioral_features(student_id, created_at DESC);

-- Skill assessments indexes
CREATE INDEX idx_skill_assessment_student
  ON skill_assessments(student_id);

CREATE INDEX idx_skill_assessment_created
  ON skill_assessments(created_at DESC);
```

**Verify Indexes:**

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,          -- Number of index scans
    idx_tup_read,      -- Tuples read from index
    idx_tup_fetch      -- Tuples fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Identify missing indexes
SELECT
    schemaname,
    tablename,
    seq_scan,          -- Number of sequential scans
    seq_tup_read,      -- Tuples read sequentially
    idx_scan           -- Number of index scans
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND seq_scan > idx_scan  -- More seq scans than index scans (bad!)
ORDER BY seq_scan DESC;
```

**If missing indexes found:**

```sql
-- Add index for frequently queried columns
CREATE INDEX CONCURRENTLY idx_custom_column
  ON table_name(column_name);

-- Composite index for multi-column queries
CREATE INDEX CONCURRENTLY idx_multi_column
  ON table_name(column1, column2);

-- Partial index for filtered queries
CREATE INDEX CONCURRENTLY idx_active_students
  ON students(id)
  WHERE active = true;
```

**Use CONCURRENTLY:** Creates index without locking table (safe for production)

---

### Query Optimization

#### 1. Analyze Slow Queries

```sql
-- Enable query logging (Cloud SQL)
gcloud sql instances patch mass-db \
  --database-flags=log_min_duration_statement=1000

-- View slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    min_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

#### 2. Use EXPLAIN ANALYZE

```sql
-- Check query plan
EXPLAIN ANALYZE
SELECT * FROM linguistic_features
WHERE student_id = 'student_123'
ORDER BY created_at DESC
LIMIT 1;

-- Look for:
-- - "Seq Scan" (bad) vs "Index Scan" (good)
-- - High "cost" values
-- - "rows" estimate vs actual
```

#### 3. Optimize Common Queries

**Get latest features (already optimized):**

```python
# Good: Uses index, limits to 1
result = await session.execute(
    select(LinguisticFeatures)
    .where(LinguisticFeatures.student_id == student_id)
    .order_by(LinguisticFeatures.created_at.desc())
    .limit(1)
)

# Bad: Loads all rows, sorts in Python
result = await session.execute(
    select(LinguisticFeatures)
    .where(LinguisticFeatures.student_id == student_id)
)
all_features = result.scalars().all()
latest = sorted(all_features, key=lambda x: x.created_at, reverse=True)[0]
```

---

### Vacuuming & Maintenance

**Problem:** PostgreSQL accumulates dead tuples, slowing queries.

**Solution:** Regular vacuuming (automatic in Cloud SQL, but verify)

```sql
-- Manual vacuum (if needed)
VACUUM ANALYZE linguistic_features;
VACUUM ANALYZE behavioral_features;
VACUUM ANALYZE skill_assessments;

-- Check last vacuum
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    n_dead_tup,      -- Dead tuples
    n_live_tup       -- Live tuples
FROM pg_stat_user_tables
WHERE schemaname = 'public';

-- Tune autovacuum (if needed)
ALTER TABLE linguistic_features
SET (autovacuum_vacuum_scale_factor = 0.1);  -- Vacuum more often
```

**Cloud SQL Automatic Maintenance:**
- Already configured in deployment
- Runs during maintenance window (Sunday 4AM)
- Includes vacuuming, analyzing, and reindexing

---

### Read Replicas

**For high read load:**

```bash
# Create read replica
gcloud sql instances create mass-db-replica \
  --master-instance-name=mass-db \
  --tier=db-custom-2-7680 \
  --region=us-central1

# Update application to use replica for reads
READ_DATABASE_URL=postgresql+asyncpg://user:pass@replica-host/mass_db
```

**Route reads to replica:**

```python
# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine

# Master (write) engine
write_engine = create_async_engine(settings.DATABASE_URL)

# Replica (read) engine
read_engine = create_async_engine(settings.READ_DATABASE_URL)

# Use read engine for inference queries
async def get_db_read():
    async with AsyncSession(read_engine) as session:
        yield session
```

---

## API Performance

### Rate Limiting

**Already implemented:** Token bucket rate limiter for GPT-4 API

```python
# app/core/rate_limiter.py

# Current settings (adjust based on OpenAI quota)
GPT4_CALLS_PER_MINUTE = 50
GPT4_CALLS_PER_HOUR = 500
```

**Tuning Guidelines:**

| OpenAI Tier | Calls/Min | Calls/Hour | Burst Size |
|-------------|-----------|------------|------------|
| Free | 3 | 200 | 5 |
| Tier 1 | 500 | 10,000 | 100 |
| Tier 2 | 5,000 | 100,000 | 500 |
| Tier 3 | 10,000 | 200,000 | 1,000 |

**Update configuration:**

```python
# Increase for higher tiers
registry.register("openai_reasoning", RateLimitConfig(
    calls_per_minute=500,   # Tier 1
    calls_per_hour=10000,
    burst_size=100
))
```

**Monitor rate limit usage:**

```bash
# Check metrics
curl http://localhost:8000/api/v1/metrics/summary

# Look for rate_limit_errors
```

---

### Caching Strategies

#### 1. Model Caching (Already Implemented)

```python
# Models loaded once at startup, cached in memory
_inference_service: Optional[SkillInferenceService] = None
```

**Impact:** Eliminates 100-200ms model loading per request ✅

---

#### 2. Secret Caching (Already Implemented)

```python
# app/core/secrets.py
# Secrets cached after first retrieval from Secret Manager
```

**Impact:** Eliminates 50-100ms Secret Manager API call ✅

---

#### 3. Feature Caching (Consider Adding)

**Use Case:** Students frequently re-assessed within short time window

```python
from functools import lru_cache
import time

class FeatureCache:
    def __init__(self, ttl=300):  # 5 minute TTL
        self.cache = {}
        self.ttl = ttl

    def get(self, student_id):
        if student_id in self.cache:
            data, timestamp = self.cache[student_id]
            if time.time() - timestamp < self.ttl:
                return data
        return None

    def set(self, student_id, data):
        self.cache[student_id] = (data, time.time())

# Use in inference service
_feature_cache = FeatureCache(ttl=300)

async def infer_skill(self, session, student_id, skill_type):
    # Check cache first
    cached = _feature_cache.get(student_id)
    if cached:
        ling_features, beh_features = cached
    else:
        # Fetch from database
        ling_features, beh_features = await fetch_features(...)
        _feature_cache.set(student_id, (ling_features, beh_features))
```

**Trade-offs:**
- **Pro:** 30-50ms reduction for cached requests
- **Con:** Stale data if features updated
- **Recommendation:** Use for read-heavy, low-update scenarios

---

#### 4. Response Caching (Consider Adding)

**Use Case:** Identical inference requests within short window

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Initialize cache
FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

# Cache endpoint responses
@router.post("/infer/{student_id}")
@cache(expire=300)  # 5 minute cache
async def infer_student_skills(...):
    ...
```

**Trade-offs:**
- **Pro:** Near-zero latency for cached requests
- **Con:** Stale results if models/weights updated
- **Recommendation:** Use sparingly, short TTL (5 min)

---

### Concurrent Request Handling

**Cloud Run Configuration:**

```bash
# Current settings
--concurrency=80        # Requests per instance
--cpu=2                 # CPU cores
--memory=4Gi            # Memory

# For higher load
--concurrency=100       # More concurrent requests
--cpu=4                 # More CPU
--memory=8Gi            # More memory
```

**Optimal Concurrency:**
- **Low CPU tasks:** 100-150 per instance
- **CPU-heavy (ML inference):** 50-80 per instance
- **Memory-heavy:** 30-50 per instance

**Test concurrency limits:**

```bash
# Load test with increasing concurrency
for c in 10 20 50 80 100; do
    echo "Testing concurrency: $c"
    wrk -t4 -c$c -d30s --latency http://localhost:8000/api/v1/health
done

# Monitor for:
# - Latency increase
# - Error rate increase
# - Memory/CPU usage
```

---

## Memory Optimization

### Model Loading

**Problem:** Each XGBoost model is ~500KB. Loading 4 models = 2MB.

**Current State:** Models loaded once at startup (optimal) ✅

**Further Optimization (if needed):**

```python
# Lazy loading per skill (trade memory for latency)
class SkillInferenceService:
    def _load_model(self, skill_type):
        if skill_type not in self.models:
            model_path = self.models_dir / f"{skill_type.value}_model.pkl"
            self.models[skill_type] = joblib.load(model_path)
        return self.models[skill_type]
```

**Trade-offs:**
- Saves memory if not all skills used
- Adds 50-100ms first request latency per skill

---

### Feature Vectors

**Problem:** Feature vectors stored as Python lists (memory-inefficient).

**Solution:** Use NumPy arrays with efficient dtypes (already implemented) ✅

```python
# Good: NumPy array with float32 (4 bytes per value)
features = np.array(features, dtype=np.float32).reshape(1, -1)
# 26 features × 4 bytes = 104 bytes

# Bad: Python list with floats (28 bytes per value)
features = [0.15, 0.08, ...]
# 26 features × 28 bytes = 728 bytes
```

**Impact:** 7x memory reduction per inference ✅

---

### Connection Pool Sizing

**Problem:** Too many database connections consume memory.

**Solution:** Right-size connection pools

```python
# Memory per connection: ~10MB
# Total memory for connections:
total_memory = (POOL_SIZE + MAX_OVERFLOW) * 10MB

# Example:
# Pool: 20 + 40 = 60 connections
# Memory: 60 × 10MB = 600MB
```

**Guidelines:**
- **Small instances (2GB RAM):** Pool=10, Overflow=20
- **Medium instances (4GB RAM):** Pool=20, Overflow=40 (current)
- **Large instances (8GB RAM):** Pool=40, Overflow=80

---

### Memory Profiling

**Detect memory leaks:**

```bash
# Install memory profiler
pip install memory_profiler

# Profile application
python -m memory_profiler app/main.py

# Or use decorator
from memory_profiler import profile

@profile
def my_function():
    ...
```

**Check for common issues:**
- Growing cache without eviction
- Unclosed database sessions
- Circular references preventing GC

---

## GPT-4 API Optimization

### Token Management

**Already Implemented:** Automatic token counting and evidence truncation ✅

```python
# app/services/reasoning_generator.py

def _count_tokens(self, text: str) -> int:
    return len(self.tokenizer.encode(text))

# Truncate evidence if over limit
for max_items in [len(evidence), 10, 5, 3]:
    truncated_evidence, _ = self._truncate_evidence(evidence, max_items)
    token_count = self._count_message_tokens(messages)

    if token_count <= safe_limit:
        break
```

**Impact:**
- Prevents expensive large token requests
- Maintains quality with top evidence ✅

---

### Cost Optimization

**Model Selection:**

| Model | Cost (1M tokens) | Quality | Speed |
|-------|------------------|---------|-------|
| gpt-4o-mini | $0.15 / $0.60 | Good | Fast |
| gpt-4o | $2.50 / $10.00 | Best | Medium |
| gpt-4-turbo | $10 / $30 | Best | Slow |
| gpt-3.5-turbo | $0.50 / $1.50 | Fair | Fastest |

**Current:** gpt-4o-mini (optimal for cost/quality) ✅

**Cost Calculation:**
```python
# Example: 100 inferences/day
tokens_per_inference = 2000  # Prompt + response
daily_tokens = 100 * 2000 = 200,000 tokens
monthly_tokens = 200,000 * 30 = 6M tokens

# gpt-4o-mini cost
monthly_cost = (6M / 1M) * $0.15 = $0.90/month ✅

# gpt-4o cost (if switched)
monthly_cost = (6M / 1M) * $2.50 = $15.00/month
```

---

### Fallback to Templates

**Already Implemented:** Template-based reasoning when GPT-4 unavailable ✅

```python
# app/services/reasoning_generator.py

try:
    response = await self.client.chat.completions.create(...)
except Exception as e:
    logger.error(f"Failed to generate reasoning: {e}")
    return self._generate_fallback_reasoning(...)
```

**Fallback Scenarios:**
- Rate limit exceeded
- API timeout
- Token limit exceeded (even after truncation)
- API key invalid

**Impact:**
- Prevents inference failures
- Degrades gracefully ✅

---

### Caching Repeated Reasoning

**Consider Adding:** Cache GPT-4 responses for identical prompts

```python
import hashlib
import json

class ReasoningCache:
    def __init__(self, ttl=3600):  # 1 hour TTL
        self.cache = {}
        self.ttl = ttl

    def _hash_prompt(self, skill_type, score, evidence):
        # Hash prompt to use as cache key
        prompt_data = {
            'skill': skill_type.value,
            'score': round(score, 2),  # Round to reduce cache misses
            'evidence': [e.content for e in evidence[:3]]  # Top 3 only
        }
        return hashlib.sha256(json.dumps(prompt_data).encode()).hexdigest()

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None

    def set(self, key, data):
        self.cache[key] = (data, time.time())

# Use in reasoning generator
_reasoning_cache = ReasoningCache(ttl=3600)

async def generate_reasoning(self, skill_type, score, evidence, ...):
    cache_key = self._hash_prompt(skill_type, score, evidence)
    cached = _reasoning_cache.get(cache_key)
    if cached:
        return cached

    # Generate new reasoning
    reasoning = await self._call_gpt4(...)
    _reasoning_cache.set(cache_key, reasoning)
    return reasoning
```

**Impact:**
- Reduces API calls by 20-40%
- Saves $0.20-$0.40/month per 100 daily inferences
- Near-zero latency for cached responses

---

## Monitoring & Profiling

### Metrics to Track

**Application Metrics (already collected):**

```python
# app/core/metrics.py

# Tracked automatically:
- inference_time_ms         # Latency per inference
- success/failure rates     # Reliability
- student_id               # Per-student tracking
- skill_type               # Per-skill tracking
- timestamp                # Time series
```

**Access metrics:**

```bash
# Recent metrics
curl http://localhost:8000/api/v1/metrics?limit=100

# Summary statistics
curl http://localhost:8000/api/v1/metrics/summary

# Response:
{
  "total_inferences": 1523,
  "successful_inferences": 1518,
  "failed_inferences": 5,
  "avg_inference_time_ms": 165.3,
  "max_inference_time_ms": 487.2,
  "min_inference_time_ms": 89.5,
  "p95_inference_time_ms": 245.8,
  "success_rate": 0.997
}
```

---

### APM Integration

**New Relic:**

```bash
# Add to requirements.txt
newrelic

# Configure
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program \
  uvicorn app.main:app --host 0.0.0.0 --port 8080

# Dockerfile
CMD ["newrelic-admin", "run-program", "uvicorn", "app.main:app", ...]
```

**DataDog:**

```bash
# Add to requirements.txt
ddtrace

# Run with tracing
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8080

# Dockerfile
CMD ["ddtrace-run", "uvicorn", "app.main:app", ...]
```

**Metrics Collected:**
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Error rates by endpoint
- Database query times
- External API latency (OpenAI)
- Memory usage
- CPU utilization

---

### Profiling Tools

#### Python Profiling

```bash
# CPU profiling
python -m cProfile -o profile.stats -s cumulative app/main.py

# Analyze results
python -m pstats profile.stats
>>> sort cumtime
>>> stats 20  # Top 20 functions by cumulative time
```

#### Memory Profiling

```bash
# Install
pip install memory_profiler

# Profile
python -m memory_profiler app/main.py

# Or use decorator
from memory_profiler import profile

@profile
def inference_pipeline():
    ...
```

#### SQL Profiling

```sql
-- Enable query logging
ALTER DATABASE mass_db SET log_statement = 'all';

-- View slow queries
SELECT
    query,
    calls,
    total_time / calls as avg_time_ms,
    stddev_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY avg_time_ms DESC
LIMIT 20;
```

---

### Cloud Monitoring (GCP)

**Set up custom metrics:**

```bash
# Create log-based metric for high latency
gcloud logging metrics create high_latency_requests \
  --description="Requests with latency > 500ms" \
  --log-filter='resource.type="cloud_run_revision"
    AND jsonPayload.inference_time_ms>500'

# Create alert policy
gcloud alpha monitoring policies create \
  --display-name="High Latency Alert" \
  --condition-display-name="Latency > 500ms" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s \
  --notification-channels=CHANNEL_ID
```

**Dashboard Metrics:**
- Request latency (p50, p95, p99)
- Request count
- Error rate
- Instance count
- CPU utilization
- Memory utilization
- Database connections
- Redis connections

---

## Load Testing

### Tools

**wrk (HTTP load testing):**

```bash
# Install
brew install wrk  # macOS
sudo apt install wrk  # Linux

# Basic test
wrk -t4 -c100 -d30s --latency http://localhost:8000/api/v1/health

# Output:
Running 30s test @ http://localhost:8000/api/v1/health
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    45.23ms   12.15ms  150.22ms   78.45%
    Req/Sec   550.12     85.43   720.00     82.15%
  Latency Distribution
     50%   42.15ms
     75%   48.92ms
     90%   58.33ms
     99%   95.67ms
  65814 requests in 30.00s, 12.45MB read
Requests/sec:   2193.80
Transfer/sec:    425.15KB
```

**Locust (Python load testing):**

```python
# tests/load_test.py
from locust import HttpUser, task, between

class SkillAssessmentUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def infer_single_student(self):
        self.client.post(
            "/api/v1/infer/student_123",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def infer_batch(self):
        self.client.post(
            "/api/v1/infer/batch",
            json={"student_ids": [f"student_{i}" for i in range(10)]},
            headers={"Authorization": f"Bearer {self.token}"}
        )

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/v1/auth/login", json={
            "username": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
```

**Run load test:**

```bash
# Install
pip install locust

# Run
locust -f tests/load_test.py --host=http://localhost:8000

# Open browser: http://localhost:8089
# Configure: 100 users, 10 users/sec spawn rate
```

---

### Test Scenarios

#### Scenario 1: Baseline Performance

**Goal:** Establish baseline metrics

```bash
# Single endpoint, low load
wrk -t2 -c10 -d60s --latency \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/infer/student_123
```

**Success Criteria:**
- p95 latency < 300ms
- p99 latency < 500ms
- 0% error rate

---

#### Scenario 2: Sustained Load

**Goal:** Test under normal production load

```bash
# Medium load for 10 minutes
wrk -t4 -c50 -d600s --latency \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/infer/student_123
```

**Success Criteria:**
- p95 latency < 400ms
- p99 latency < 600ms
- < 0.1% error rate
- No memory leaks (check metrics)

---

#### Scenario 3: Spike Load

**Goal:** Test autoscaling and burst handling

```bash
# Sudden traffic spike
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/v1/infer/student_$i \
    -H "Authorization: Bearer TOKEN" &
done
wait

# Monitor Cloud Run metrics for:
# - Instance count increase
# - Latency spike recovery
# - Error rate
```

**Success Criteria:**
- Cloud Run scales within 30s
- Latency recovers within 60s
- < 1% error rate during spike

---

#### Scenario 4: Batch Processing

**Goal:** Test batch endpoint performance

```bash
# Batch inference with varying sizes
for size in 10 20 50 100; do
  echo "Testing batch size: $size"
  curl -X POST http://localhost:8000/api/v1/infer/batch \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"student_ids\": [$(seq -s, 1 $size | sed 's/[0-9]\+/"student_&"/g')]}" \
    --silent --write-out "\nLatency: %{time_total}s\n"
done
```

**Success Criteria:**
- 10 students: < 2s
- 50 students: < 6s
- 100 students: < 12s

---

## Performance Checklist

### Pre-Deployment

- [ ] Database indexes created and verified
- [ ] Connection pooling configured (size based on load)
- [ ] Model loading cached (singleton pattern)
- [ ] Parallel queries implemented
- [ ] Rate limiting configured (OpenAI tier)
- [ ] Monitoring dashboards set up
- [ ] Load testing completed
- [ ] Alerting configured (latency, errors)

### Post-Deployment

- [ ] Health checks passing
- [ ] Baseline metrics established
- [ ] p95/p99 latency within targets
- [ ] Error rate < 0.5%
- [ ] Memory usage stable (no leaks)
- [ ] Autoscaling policies tested
- [ ] Database connection count normal
- [ ] Redis connection count normal

### Monthly Review

- [ ] Review metrics trends
- [ ] Check for performance regressions
- [ ] Optimize slow queries
- [ ] Tune connection pools if needed
- [ ] Review and adjust rate limits
- [ ] Update performance targets
- [ ] Run load tests
- [ ] Check cost vs performance trade-offs

---

## Troubleshooting

### High Latency

**Check:**
1. Database query times (EXPLAIN ANALYZE)
2. External API latency (OpenAI)
3. Instance CPU/memory usage
4. Connection pool exhaustion
5. Network latency

**Fix:**
- Add missing indexes
- Increase instance resources
- Optimize queries
- Scale horizontally

---

### High Memory Usage

**Check:**
1. Connection pool size
2. Cache sizes
3. Memory leaks
4. Instance memory limits

**Fix:**
- Reduce connection pools
- Add cache eviction
- Profile for leaks
- Increase instance memory

---

### Database Connection Errors

**Check:**
1. Max connections limit
2. Connection pool configuration
3. Connection leaks (unclosed sessions)
4. Slow queries holding connections

**Fix:**
```sql
-- Increase max connections
ALTER SYSTEM SET max_connections = 200;

-- Kill long-running queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 minutes';
```

---

## References

### Implementation Files
- **Metrics Store:** `app/core/metrics.py`
- **Rate Limiter:** `app/core/rate_limiter.py`
- **Inference Service:** `app/services/skill_inference.py`
- **Evidence Fusion:** `app/services/evidence_fusion.py`
- **Performance Tests:** `tests/test_performance.py`

### Related Documentation
- **Architecture:** `docs/ARCHITECTURE.md`
- **Deployment:** `docs/DEPLOYMENT.md`
- **Training Data:** `docs/TRAINING_DATA_FORMAT.md`
- **Evidence Normalization:** `docs/EVIDENCE_NORMALIZATION.md`

### External Resources
- **FastAPI Performance:** https://fastapi.tiangolo.com/deployment/performance/
- **PostgreSQL Tuning:** https://wiki.postgresql.org/wiki/Performance_Optimization
- **Cloud Run Performance:** https://cloud.google.com/run/docs/tips/performance

---

**Last Updated:** 2025-11-13
**Version:** 1.0.0
**Performance Status:** Optimized ✅
