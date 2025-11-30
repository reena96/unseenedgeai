# Data Persistence and Backup Guide

## Overview

This guide covers the data persistence architecture for the MASS (Multi-modal Assessment of Social Skills) platform and provides instructions for backup, restore, and verification operations.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow](#data-flow)
3. [Backup Operations](#backup-operations)
4. [Restore Operations](#restore-operations)
5. [Data Integrity Verification](#data-integrity-verification)
6. [Database Statistics](#database-statistics)

---

## Architecture Overview

### Database Configuration

- **Database**: PostgreSQL 15+ with TimescaleDB extension
- **Connection**: Async SQLAlchemy with asyncpg driver
- **Location**: `postgresql+asyncpg://mass_user:mass_password@127.0.0.1:5432/mass_db`
- **Session Management**: Async context manager with auto-commit/rollback

### Key Models

#### SkillAssessment
- **Table**: `skill_assessments`
- **Fields**:
  - `id` (UUID): Primary key
  - `student_id` (UUID): Foreign key to students table
  - `skill_type` (Enum): One of 7 skill types (EMPATHY, PROBLEM_SOLVING, SELF_REGULATION, RESILIENCE, ADAPTABILITY, COMMUNICATION, COLLABORATION)
  - `score` (Float): 0-1 scale
  - `confidence` (Float): 0-1 scale
  - `reasoning` (Text): AI-generated explanation
  - `recommendations` (Text): Improvement suggestions
  - `feature_importance` (JSON): ML model feature weights
  - `created_at`, `updated_at`: Timestamps

#### Evidence
- **Table**: `evidence`
- **Fields**:
  - `id` (UUID): Primary key
  - `assessment_id` (UUID): Foreign key to skill_assessments
  - `evidence_type` (Enum): LINGUISTIC, BEHAVIORAL, CONTEXTUAL
  - `source` (String): transcript, game_telemetry, etc.
  - `content` (Text): Evidence content
  - `relevance_score` (Float): 0-1 scale
  - `created_at`, `updated_at`: Timestamps

---

## Data Flow

### Assessment Creation Flow

1. **API Endpoint** (`/api/v1/assessments/{student_id}`)
   - Receives request for skill assessment
   - Validates student exists
   - Checks for cached recent assessment (7-day window)

2. **AI Assessment Service** (`app/services/ai_assessment.py`)
   - Fetches linguistic features from transcripts
   - Fetches behavioral features from game sessions
   - Builds prompt with student data and skill criteria
   - Calls OpenAI API (gpt-4o-mini) for assessment
   - Validates score and confidence ranges (0-1)

3. **Database Persistence** (`app/services/ai_assessment.py:527`)
   ```python
   assessment = SkillAssessment(...)
   session.add(assessment)

   # Create evidence entries
   for quote in evidence_quotes:
       evidence = Evidence(...)
       session.add(evidence)

   await session.commit()  # ✓ Transaction committed
   await session.refresh(assessment)  # ✓ Reload with relationships
   ```

4. **Response with Evidence** (lines 530-538)
   - Eagerly loads evidence relationships using `selectinload`
   - Returns assessment with all evidence attached

### ML Inference Flow

1. **Inference Endpoint** (`/api/v1/infer/{student_id}`)
   - Runs ML models for all skill predictions
   - Scores on 0-1 scale with confidence

2. **Evidence Service** (`app/services/evidence_service.py`)
   - `create_assessment_with_evidence()` method
   - Generates reasoning from feature importance
   - Extracts linguistic evidence from transcripts
   - Extracts behavioral evidence from game sessions
   - Creates assessment with linked evidence
   - **Commits transaction** at line 71

3. **Persistence Guarantee**
   ```python
   session.add(assessment)
   await session.flush()  # Get ID before evidence

   for evidence_record in evidence_records:
       session.add(evidence_record)

   await session.commit()  # ✓ All data persisted

   # Reload with relationships for API response
   result = await session.execute(
       select(SkillAssessment)
       .options(selectinload(SkillAssessment.evidence))
       .where(SkillAssessment.id == assessment.id)
   )
   ```

### Transaction Management

The database session is managed by `app/core/database.py`:

```python
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # ✓ Auto-commit on success
        except Exception:
            await session.rollback()  # ✓ Auto-rollback on error
            raise
        finally:
            await session.close()
```

**Key Points:**
- ✓ Auto-commit on successful endpoint execution
- ✓ Auto-rollback on exceptions
- ✓ Proper connection cleanup
- ✓ Timezone-aware timestamps
- ✓ Evidence relationships eagerly loaded to prevent lazy-loading issues

---

## Backup Operations

### CLI Export Script

**Location**: `scripts/export_assessments.py`

#### Full Backup
```bash
# Export all assessments with evidence
python scripts/export_assessments.py --output data/exports/backup_$(date +%Y%m%d).json

# Example output:
# ✓ Successfully exported 2194 assessments
# ✓ Saved to: data/exports/backup_20251129.json
```

#### Filtered Backups
```bash
# Export for specific student
python scripts/export_assessments.py \
  --student-id 0d56491b-9c2c-430d-871e-02f960b591a7 \
  --output data/exports/student_backup.json

# Export specific skill type
python scripts/export_assessments.py \
  --skill-type empathy \
  --output data/exports/empathy_assessments.json

# Export date range
python scripts/export_assessments.py \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --output data/exports/2024_assessments.json
```

#### Backup Format
```json
{
  "export_timestamp": "2025-11-29T21:51:32.123456",
  "export_filters": {
    "student_id": null,
    "skill_type": null,
    "start_date": null,
    "end_date": null
  },
  "total_assessments": 2194,
  "assessments": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "skill_type": "empathy",
      "score": 0.77,
      "confidence": 0.85,
      "reasoning": "The student excels at empathy...",
      "recommendations": "Continue fostering...",
      "feature_importance": "{...}",
      "created_at": "2024-11-29T12:34:56.789",
      "updated_at": "2024-11-29T12:34:56.789",
      "evidence": [
        {
          "id": "uuid",
          "assessment_id": "uuid",
          "evidence_type": "linguistic",
          "source": "transcript",
          "content": "Student demonstrated empathy...",
          "relevance_score": 0.9,
          "created_at": "2024-11-29T12:34:56.789",
          "updated_at": "2024-11-29T12:34:56.789"
        }
      ]
    }
  ]
}
```

### API Backup Endpoint

**Endpoint**: `POST /api/v1/assessments/backup`

```bash
# Trigger backup via API
curl -X POST http://localhost:8000/api/v1/assessments/backup

# Response:
{
  "success": true,
  "backup_file": "/path/to/backend/data/exports/assessments_backup_20251129_215130.json",
  "total_assessments": 2194,
  "timestamp": "2025-11-29T21:51:30.123456"
}
```

---

## Restore Operations

### CLI Import Script

**Location**: `scripts/import_assessments.py`

#### Import New Data
```bash
# Import assessments from backup (error on duplicates)
python scripts/import_assessments.py \
  --input data/exports/backup_20251129.json

# Skip duplicate assessments
python scripts/import_assessments.py \
  --input data/exports/backup_20251129.json \
  --skip-duplicates

# Update existing assessments with imported data
python scripts/import_assessments.py \
  --input data/exports/backup_20251129.json \
  --update-duplicates
```

#### Import Process
1. Reads JSON backup file
2. Validates data structure
3. For each assessment:
   - Checks if assessment ID exists
   - Based on flags:
     - **Default**: Error on duplicate
     - **--skip-duplicates**: Skip existing records
     - **--update-duplicates**: Update existing records
   - Creates/updates assessment
   - Imports all linked evidence
4. Commits in batches of 100 for performance

#### Example Output
```
Starting assessment import...
Input file: data/exports/backup_20251129.json
Duplicate handling: skip
Found 2194 assessments in backup file
Backup timestamp: 2025-11-29T21:51:32.123456
Progress: 100/2194 (skipped duplicate)
Progress: 200/2194 (imported)
...
✓ Import complete:
  - Imported: 150
  - Skipped: 2044
  - Updated: 0
```

---

## Data Integrity Verification

### CLI Verification Script

**Location**: `scripts/verify_data_integrity.py`

#### Basic Verification
```bash
# Run all integrity checks
python scripts/verify_data_integrity.py

# Verbose output
python scripts/verify_data_integrity.py --verbose

# Fix orphaned evidence automatically
python scripts/verify_data_integrity.py --fix-orphans
```

#### Checks Performed

1. **Score Range Validation**
   - All scores between 0 and 1
   - All confidence scores between 0 and 1

2. **Student Coverage**
   - All students have assessments
   - All students have 4 primary skills assessed
   - Primary skills: EMPATHY, PROBLEM_SOLVING, SELF_REGULATION, RESILIENCE

3. **Orphaned Evidence**
   - Evidence records with non-existent assessment IDs
   - Auto-fix available with `--fix-orphans`

4. **Evidence Linking**
   - All assessments have evidence records
   - Evidence counts are reasonable (3-20 per assessment)

5. **Timestamp Consistency**
   - No future timestamps
   - `updated_at` >= `created_at`

#### Example Output
```
======================================================================
SKILL ASSESSMENT DATA INTEGRITY VERIFICATION
======================================================================

6. Database statistics:
  Total assessments: 2194
    - empathy: 361
    - problem_solving: 361
    - self_regulation: 361
    - resilience: 361
    - adaptability: 250
    - communication: 250
    - collaboration: 250
  Total evidence records: 10083
  Total students: 50
  Average assessments per student: 43.9

1. Checking score ranges...
✓ All scores are within valid range (0-1)
✓ All confidence scores are within valid range (0-1)

2. Checking student assessment coverage...
✓ All 50 students have assessments
✓ All students have all 4 primary skill assessments

3. Checking for orphaned evidence...
✓ No orphaned evidence records found

4. Checking evidence linking...
✓ All assessments have evidence records
✓ Evidence counts are reasonable for all assessments

5. Checking timestamp consistency...
✓ No future timestamps found
✓ All timestamps are consistent

======================================================================
SUMMARY
======================================================================
Issues found: 0
Warnings: 0

✓ All integrity checks passed! Data is healthy.
```

---

## Database Statistics

### Current State (as of 2025-11-29)

```sql
-- Total assessments
SELECT COUNT(*) FROM skill_assessments;
-- Result: 2194

-- Unique students with assessments
SELECT COUNT(DISTINCT student_id) FROM skill_assessments;
-- Result: 50

-- Assessments by skill type
SELECT skill_type, COUNT(*)
FROM skill_assessments
GROUP BY skill_type
ORDER BY count DESC;
/*
   skill_type    | count
-----------------+-------
 empathy         |   361
 problem_solving |   361
 resilience      |   361
 self_regulation |   361
 adaptability    |   250
 collaboration   |   250
 communication   |   250
*/

-- Total evidence records
SELECT COUNT(*) FROM evidence;
-- Result: 10083

-- Average evidence per assessment
SELECT AVG(evidence_count) FROM (
  SELECT COUNT(e.id) as evidence_count
  FROM skill_assessments a
  LEFT JOIN evidence e ON a.id = e.assessment_id
  GROUP BY a.id
) subquery;
-- Result: ~4.6 evidence records per assessment
```

### Direct Database Access

```bash
# Connect to database
PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db

# Quick stats
PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -c \
  "SELECT COUNT(*) FROM skill_assessments;"

# Export to CSV (for analysis)
PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -c \
  "COPY (SELECT * FROM skill_assessments) TO STDOUT WITH CSV HEADER" \
  > assessments_export.csv
```

---

## Troubleshooting

### Issue: Assessments Not Persisting

**Symptoms**: API returns success but data not in database

**Diagnosis**:
```python
# Check if session is committing
# In app/core/database.py get_db(), verify:
await session.commit()  # Should be called on success
```

**Solution**: All current endpoints properly use `get_db()` dependency which handles commits.

### Issue: Evidence Missing from API Response

**Symptoms**: Assessment has evidence in DB but not in API response

**Diagnosis**:
```python
# Check if using selectinload
result = await session.execute(
    select(SkillAssessment)
    .options(selectinload(SkillAssessment.evidence))  # ← Must include this
    .where(SkillAssessment.id == assessment_id)
)
```

**Solution**: All assessment endpoints now use `selectinload` for evidence relationships.

### Issue: Slow Assessment Queries

**Symptoms**: API response times > 1 second

**Diagnosis**:
```sql
-- Check index usage
EXPLAIN ANALYZE
SELECT * FROM skill_assessments
WHERE student_id = 'uuid'
ORDER BY created_at DESC;
```

**Solution**:
- Indexes exist on `student_id`, `skill_type`, and composite `(student_id, skill_type, created_at)`
- Use caching with `use_cached=True` parameter (7-day cache window)

---

## Best Practices

### For Developers

1. **Always use the database dependency**
   ```python
   async def endpoint(db: AsyncSession = Depends(get_db)):
       # Auto-commit/rollback handled
   ```

2. **Eagerly load relationships**
   ```python
   .options(selectinload(SkillAssessment.evidence))
   ```

3. **Validate before commit**
   ```python
   score = max(0.0, min(1.0, score))  # Clamp to 0-1
   ```

4. **Use timezone-aware timestamps**
   ```python
   from datetime import datetime, timezone
   datetime.now(timezone.utc)  # Not datetime.utcnow()
   ```

### For Operations

1. **Daily backups**
   ```bash
   # Add to cron
   0 2 * * * cd /path/to/backend && source venv/bin/activate && \
     python scripts/export_assessments.py \
     --output data/exports/daily_backup_$(date +\%Y\%m\%d).json
   ```

2. **Weekly integrity checks**
   ```bash
   # Add to cron
   0 3 * * 0 cd /path/to/backend && source venv/bin/activate && \
     python scripts/verify_data_integrity.py --verbose \
     > logs/integrity_check_$(date +\%Y\%m\%d).log
   ```

3. **Retention policy**
   ```bash
   # Keep last 30 days of backups
   find data/exports -name "daily_backup_*.json" -mtime +30 -delete
   ```

---

## Files and Locations

### Scripts
- `/scripts/export_assessments.py` - Export assessments to JSON
- `/scripts/import_assessments.py` - Import assessments from JSON
- `/scripts/verify_data_integrity.py` - Verify data integrity

### Data Directories
- `/data/exports/` - Backup files location
- `/logs/` - Log files (create if needed)

### Core Files
- `/app/core/database.py` - Database session management
- `/app/models/assessment.py` - Assessment and Evidence models
- `/app/services/ai_assessment.py` - AI-powered assessment service
- `/app/services/evidence_service.py` - ML inference evidence service
- `/app/api/endpoints/assessments.py` - Assessment API endpoints

---

## Support

For issues or questions:
1. Check the integrity verification output
2. Review API logs for transaction errors
3. Verify database connection with `psql`
4. Check backup files are valid JSON

---

**Last Updated**: 2025-11-29
**Database Version**: PostgreSQL 15 + TimescaleDB
**Python Version**: 3.12+
**SQLAlchemy Version**: 2.0+ (async)
