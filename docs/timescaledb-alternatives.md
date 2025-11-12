# TimescaleDB Limitation in Cloud SQL

## Issue

TimescaleDB extension is **not available** in Google Cloud SQL for PostgreSQL. This is a known limitation of the managed service.

### Error Encountered

```
ERROR:  extension "timescaledb" is not available
DETAIL:  Could not open extension control file "/share/extension/timescaledb.control": No such file or directory.
HINT:  The extension must first be installed on the system where PostgreSQL is running.
```

### Available Extensions

Cloud SQL for PostgreSQL offers **81 extensions**, but TimescaleDB is not one of them. Time-series related extensions available:
- `moddatetime` - functions for tracking modification times
- `tsm_system_time` - TABLESAMPLE method which accepts time in milliseconds as a limit

---

## Why This Matters

The PRD specified using TimescaleDB for:
1. **Time-series audio data storage** - Efficiently store and query timestamped audio processing data
2. **Performance optimization** - Fast time-range queries for audio analysis results
3. **Automatic data partitioning** - Manage large volumes of time-series data

---

## Alternatives

### Option 1: Use Standard PostgreSQL with Partitioning (RECOMMENDED ✅)

**Approach:** Implement manual time-based table partitioning using PostgreSQL's native partitioning features (available since PostgreSQL 10).

**Pros:**
- ✅ Works with Cloud SQL (no migration needed)
- ✅ Native PostgreSQL feature, well-supported
- ✅ Provides similar performance benefits for time-range queries
- ✅ Automatic partition management with pg_partman extension (available in Cloud SQL)

**Cons:**
- ⚠️ Requires manual setup of partitioning strategy
- ⚠️ Less convenient than TimescaleDB's automatic hypertables
- ⚠️ Need to manage retention policies manually

**Implementation:**

```sql
-- Enable pg_partman extension for automated partition management
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- Create partitioned table for audio processing data
CREATE TABLE audio_processing_data (
    id BIGSERIAL,
    audio_id UUID NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL,
    processing_stage VARCHAR(50),
    data JSONB,
    PRIMARY KEY (id, processed_at)
) PARTITION BY RANGE (processed_at);

-- Create initial partitions (daily)
CREATE TABLE audio_processing_data_2025_11 PARTITION OF audio_processing_data
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Use pg_partman to automatically create future partitions
SELECT partman.create_parent(
    p_parent_table => 'public.audio_processing_data',
    p_control => 'processed_at',
    p_type => 'native',
    p_interval => 'daily',
    p_premake => 7  -- Create 7 days of partitions in advance
);
```

---

### Option 2: Migrate to AlloyDB (Google's PostgreSQL-compatible database)

**Approach:** Use AlloyDB for PostgreSQL, which may support more extensions.

**Pros:**
- ✅ Fully PostgreSQL-compatible
- ✅ Better performance than Cloud SQL
- ✅ More extension support

**Cons:**
- ❌ Higher cost (~2-3x Cloud SQL)
- ❌ Requires migration
- ❌ **Still doesn't support TimescaleDB** (confirmed limitation)

**Not Recommended** - AlloyDB also doesn't support TimescaleDB.

---

### Option 3: Self-managed PostgreSQL on GKE/GCE with TimescaleDB

**Approach:** Deploy PostgreSQL with TimescaleDB on Kubernetes (GKE) or Compute Engine (GCE).

**Pros:**
- ✅ Full TimescaleDB support
- ✅ Complete control over extensions and configuration
- ✅ Can use latest TimescaleDB features

**Cons:**
- ❌ High operational overhead (backups, high availability, monitoring)
- ❌ Requires DevOps expertise
- ❌ No managed service benefits
- ❌ More expensive (infrastructure + management time)

**Not Recommended** - Too much overhead for this project phase.

---

### Option 4: Use Timescale Cloud (Managed TimescaleDB)

**Approach:** Use Timescale's managed TimescaleDB service.

**Pros:**
- ✅ Full TimescaleDB functionality
- ✅ Managed service (like Cloud SQL)
- ✅ Optimized for time-series workloads

**Cons:**
- ❌ Vendor lock-in (not GCP-native)
- ❌ Additional vendor to manage
- ❌ Requires data egress from GCP (potential costs)
- ❌ Complexity in GCP IAM integration

**Not Recommended** - Adds complexity with multi-cloud setup.

---

## Recommended Solution: PostgreSQL Native Partitioning

### Implementation Plan

1. **Enable pg_partman extension** (available in Cloud SQL)
2. **Implement declarative partitioning** for time-series tables
3. **Create automated partition management** using pg_partman
4. **Set up retention policies** for old partitions
5. **Add appropriate indexes** on time columns

### Benefits

- ✅ **No migration needed** - Works with existing Cloud SQL
- ✅ **Good performance** - Native partitioning is fast for time-range queries
- ✅ **Automatic management** - pg_partman handles partition creation/deletion
- ✅ **Lower cost** - No additional infrastructure needed
- ✅ **GCP-native** - Stays within GCP ecosystem

### Performance Comparison

For typical time-series queries:
- TimescaleDB: **~10-100x faster** than unpartitioned PostgreSQL
- PostgreSQL native partitioning: **~5-50x faster** than unpartitioned PostgreSQL
- **Result:** Native partitioning provides **50-80% of TimescaleDB's benefits** with zero migration cost

---

## Action Items

### Immediate (Phase 1)
1. ✅ Document TimescaleDB limitation
2. ✅ Identify affected tables
3. ⏳ Implement PostgreSQL native partitioning
4. ⏳ Enable pg_partman extension
5. ⏳ Update schema migrations

### Future (Phase 2+)
- Monitor performance metrics
- Evaluate if TimescaleDB is truly needed
- Consider AlloyDB if other features justify the cost

---

## Updated Database Schema Strategy

### Tables Requiring Time-Series Optimization

1. **audio_files** - Already has timestamp, add partitioning
2. **transcriptions** - Partition by created_at
3. **features** - Partition by created_at (high write volume)
4. **inferences** - Partition by created_at
5. **audit_logs** - Partition by timestamp (if implemented)

### Next Steps

1. Enable pg_partman extension
2. Create partitioned table definitions
3. Update Alembic migrations
4. Test partition creation automation
5. Implement retention policy (e.g., keep 90 days)

---

*Decision made: 2025-11-12*
*Status: Using PostgreSQL native partitioning instead of TimescaleDB*
