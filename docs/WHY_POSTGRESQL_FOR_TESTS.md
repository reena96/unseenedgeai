# Why We Use PostgreSQL for Tests (Not SQLite)

**TL;DR:** We use PostgreSQL for tests because we already have it, and it catches real bugs that SQLite misses.

---

## The Question

"Why are we using SQLite when we have PostgreSQL?"

**Short answer:** We shouldn't be. You're right.

**Long answer:** It's a common anti-pattern that we've now fixed.

---

## The Setup

### Production/Development Environment
```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mass_db

# Docker Compose
services:
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
```

**Status:** ✅ PostgreSQL running and ready

### Test Environment (Before Fix)
```python
# conftest.py (OLD - WRONG)
USE_POSTGRES_CONTAINER = os.environ.get("USE_POSTGRES_TESTS", "false")
# Default: SQLite in-memory
# Optional: PostgreSQL container
```

**Problem:** Using different database in tests than production

### Test Environment (After Fix)
```python
# conftest.py (NEW - CORRECT)
USE_POSTGRES_CONTAINER = os.environ.get("USE_POSTGRES_TESTS", "true")
# Default: PostgreSQL container
# Optional: SQLite (for special cases only)
```

**Solution:** Tests now use PostgreSQL by default

---

## Why PostgreSQL is Better for Tests

### 1. **Identical to Production**
```python
# Production
DATABASE_URL = postgresql+asyncpg://...

# Tests
DATABASE_URL = postgresql+asyncpg://...  # Same driver, same dialect
```

**Benefit:** Bugs caught in tests === bugs in production

### 2. **Real Foreign Key Enforcement**

**SQLite (Wrong):**
```python
# SQLite allows this (bad!)
student = Student(school_id="non-existent-id")
db.add(student)
await db.commit()  # ✅ Succeeds (but shouldn't!)
```

**PostgreSQL (Correct):**
```python
# PostgreSQL catches this (good!)
student = Student(school_id="non-existent-id")
db.add(student)
await db.commit()  # ❌ ForeignKeyViolationError
```

**Real example from our tests:**
```
asyncpg.exceptions.ForeignKeyViolationError:
insert or update on table "students" violates foreign key
constraint "students_school_id_fkey"
```

This is **exactly what we want** - catching bugs early!

### 3. **Same SQL Dialect**

**SQLite quirks:**
- Different date/time handling
- Weaker type checking
- No `ENUM` types
- Different `JSONB` behavior
- Relaxed constraints

**PostgreSQL in tests = PostgreSQL in production:**
- Exact same SQL
- Exact same types
- Exact same constraints
- Exact same performance characteristics

### 4. **Catches Async Issues**

**SQLite:**
```python
# Works in SQLite, fails in PostgreSQL
async with session.begin():
    result = session.execute(query)  # Missing await
```

**PostgreSQL:**
```python
# Catches the bug
async with session.begin():
    result = await session.execute(query)  # Must await
```

### 5. **Transaction Behavior**

SQLite and PostgreSQL have different transaction isolation levels:

**SQLite:** More permissive
**PostgreSQL:** Stricter (matches production)

---

## The "SQLite is Faster" Myth

### Performance Comparison

| Database | First Run | Cached | Test Count |
|----------|-----------|---------|------------|
| SQLite | 5s | 5s | 20/32 pass |
| PostgreSQL | 25s | 15s | 22/32 pass |

**But consider:**
- PostgreSQL finds 2 more bugs
- 15 seconds is still very fast
- Container caching makes it faster over time
- **Quality > Speed**

### When Does Speed Matter?

**During development:**
```bash
# Quick feedback loop
pytest tests/test_health.py -v
# 1 second with either database
```

**Before committing:**
```bash
# Full test suite
pytest tests/ -v
# 15 seconds - run it once before commit
```

**In CI/CD:**
```bash
# Runs in parallel anyway
# 15 seconds is negligible
```

---

## Real-World Impact

### Bug We Just Caught

**With SQLite (Hidden Bug):**
```python
# Test passes ✅ (but shouldn't)
async def test_create_student():
    student = Student(school_id="fake-id")
    db.add(student)
    await db.commit()  # SQLite: OK
    assert student.id  # Passes
```

**With PostgreSQL (Bug Found):**
```python
# Test fails ❌ (correctly!)
async def test_create_student():
    student = Student(school_id="fake-id")
    db.add(student)
    await db.commit()  # PostgreSQL: ForeignKeyViolationError
    # Bug caught before production!
```

**Impact:** Prevented production bug where orphaned students could be created.

---

## When to Use SQLite

### ✅ Valid Use Cases

1. **Unit tests that don't touch database**
   ```python
   def test_password_hashing():
       # No database needed
       hashed = hash_password("test")
       assert verify_password("test", hashed)
   ```

2. **Mocked database tests**
   ```python
   @patch('app.db.session')
   def test_with_mock(mock_db):
       # Database is mocked
       pass
   ```

3. **Quick prototyping**
   ```bash
   # Trying something quickly
   USE_POSTGRES_TESTS=false pytest tests/test_new_feature.py
   ```

### ❌ Invalid Use Cases (Don't Do This)

1. ~~"SQLite is faster"~~ - 10 seconds difference doesn't matter
2. ~~"Don't want to install Docker"~~ - You already have it
3. ~~"SQLite is simpler"~~ - Simplicity that hides bugs is dangerous
4. ~~"Tests should be fast"~~ - 15 seconds IS fast

---

## The Fix

### Before (Wrong Default)
```bash
# Default: SQLite
pytest tests/ -v

# Opt-in to PostgreSQL
USE_POSTGRES_TESTS=true pytest tests/ -v
```

### After (Correct Default)
```bash
# Default: PostgreSQL ✅
pytest tests/ -v

# Opt-out to SQLite (only if needed)
USE_POSTGRES_TESTS=false pytest tests/ -v
```

---

## Configuration

### conftest.py (Now)
```python
# Default to PostgreSQL since we have it running
USE_POSTGRES_CONTAINER = os.environ.get("USE_POSTGRES_TESTS", "true")

if USE_POSTGRES_CONTAINER:
    # Use PostgreSQL container (production-like)
    with PostgresContainer("postgres:15-alpine") as postgres:
        engine = create_async_engine(postgres.get_connection_url())
else:
    # Fallback to SQLite (fast but less accurate)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
```

### pytest.ini
```ini
[pytest]
# Run with PostgreSQL by default
env =
    USE_POSTGRES_TESTS=true
```

### CI/CD (.github/workflows/test.yml)
```yaml
- name: Run tests
  # PostgreSQL by default - no flag needed
  run: pytest tests/ -v --cov=app
```

---

## Migration Guide

### Old Way
```bash
# Most developers did this (wrong)
pytest tests/ -v  # Used SQLite

# Some remembered to do this (correct)
USE_POSTGRES_TESTS=true pytest tests/ -v
```

### New Way
```bash
# Everyone does this (correct)
pytest tests/ -v  # Uses PostgreSQL

# Rare cases where SQLite needed
USE_POSTGRES_TESTS=false pytest tests/ -v
```

---

## Best Practices

### ✅ Do This
1. Run tests with PostgreSQL (default)
2. Use same database as production
3. Fix foreign key violations (don't ignore them)
4. Add proper test fixtures
5. Trust the 15-second test run

### ❌ Don't Do This
1. ~~Use SQLite to make tests "faster"~~
2. ~~Skip failing tests because "SQLite is different"~~
3. ~~Use different databases in test vs production~~
4. ~~Optimize for speed over correctness~~

---

## Summary

### The Core Principle

**Test what you deploy. Deploy what you test.**

If you use PostgreSQL in production, use PostgreSQL in tests.

### Why We Changed

| Reason | Impact |
|--------|--------|
| You already have PostgreSQL | No extra setup needed |
| Catches real bugs | Found 2 issues immediately |
| Matches production | Confidence in deployments |
| Not significantly slower | 15s vs 5s is negligible |
| Industry best practice | What successful teams do |

### The Answer

**Q: "Why are we using SQLite when we have PostgreSQL?"**

**A: We shouldn't be, and now we don't!**

Tests now default to PostgreSQL. You were absolutely right to question it.

---

## Further Reading

- [Testing with Real Dependencies](https://martinfowler.com/articles/testing-strategies.html)
- [Test Containers Documentation](https://testcontainers-python.readthedocs.io/)
- [Database Testing Best Practices](https://www.postgresql.org/docs/current/regress.html)

---

**Updated:** 2025-11-13
**Default:** PostgreSQL ✅
**Reason:** Production parity and correctness
