# Complete Data Population Plan for UnseenEdge AI Dashboards

## Dashboard Analysis - Data Requirements

Based on the provided screenshots, the dashboards require:

### Screenshot 1: Export Reports Page
- Student assessment data
- Skill scores for all 7 skills
- CSV/PDF export capabilities
- Summary reports

### Screenshot 2: Class Overview
- Total Students count
- Total Classes count
- Avg Score percentage
- Skill Distribution visualization
- Skill comparison metrics (0-44 scale shown)

### Screenshot 3: Supporting Evidence
- Evidence items for each assessment
- Evidence source information
- Evidence text/content
- Relevance scores

### Screenshot 4: Student Skill Assessment
- Individual student skill scores
- Gauge visualizations for each skill (Empathy, Problem Solving, Self-Regulation, Resilience)
- Score percentages (0-100 scale)
- Assessment timestamps

## Current Database Status

```bash
✅ students: 50 records
✅ skill_assessments: 200 records (4 skills × 50 students)
✅ evidence: 600 records
❌ game_sessions: 0 records (EMPTY)
❌ game_telemetry: 0 records (EMPTY)
❌ transcripts: 0 records (EMPTY)
❌ linguistic_features: 0 records (EMPTY)
❌ behavioral_features: 0 records (EMPTY)
```

## Missing Data for Full Dashboard Functionality

### 1. Additional Skill Assessments
**Current:** 4 skills (empathy, problem_solving, self_regulation, resilience)
**Needed:** All 7 skills (+ adaptability, communication, collaboration)

**Impact on Dashboards:**
- Skill distribution chart incomplete
- Class overview metrics incorrect
- Export reports missing 3 skills

### 2. Historical Assessments (Time Series)
**Current:** Single point-in-time assessments
**Needed:** Multiple assessments over time per student/skill

**Impact on Dashboards:**
- Cannot show trends over time (4-week, 12-week, semester)
- Progress tracking unavailable
- Longitudinal analysis impossible

### 3. Game Sessions
**Current:** 0 sessions
**Needed:** Multiple game sessions per student

**Impact on Dashboards:**
- Session-based evidence tracking broken
- Cannot correlate assessments with gameplay
- Behavioral features cannot be extracted

### 4. Game Telemetry
**Current:** 0 events
**Needed:** Telemetry events for each session

**Impact on Dashboards:**
- No behavioral data for ML inference
- Cannot extract behavioral features
- Real-time inference endpoints unusable

### 5. Transcripts
**Current:** 0 transcripts
**Needed:** Conversation transcripts for students

**Impact on Dashboards:**
- No linguistic data for ML inference
- Cannot extract linguistic features
- Evidence sources incomplete

### 6. Linguistic Features (Extracted)
**Current:** 0 records
**Needed:** Extracted features from transcripts

**Impact on Dashboards:**
- ML inference endpoint `/infer/*` cannot work
- Feature importance analysis unavailable
- Model-based predictions impossible

### 7. Behavioral Features (Extracted)
**Current:** 0 records
**Needed:** Extracted features from telemetry

**Impact on Dashboards:**
- ML inference endpoint `/infer/*` cannot work
- Behavioral pattern analysis unavailable
- Model-based predictions impossible

### 8. Classes/Schools
**Current:** Students lack proper class assignments
**Needed:** Proper class and school associations

**Impact on Dashboards:**
- Class overview page incomplete
- Cannot filter by class
- Heatmaps by class unavailable

## Data Population Plan - Execution Order

### Phase 1: Core Entity Enhancement (Immediate)
**Goal:** Complete the 7-skill assessments and add temporal data

#### Step 1.1: Add Missing Skills to Existing Assessments
**Script:** Create `scripts/add_missing_skills.py`

**What it does:**
- Add assessments for adaptability, communication, collaboration
- For all 50 existing students
- With reasoning and evidence
- Brings total from 200 to 350 assessments (7 skills × 50 students)

**Creates:**
- 150 new skill_assessments records
- 450 new evidence records

**Runtime:** ~5-10 minutes (AI-generated reasoning)

#### Step 1.2: Add Historical Assessments (Time Series)
**Script:** Create `scripts/seed_historical_assessments.py`

**What it does:**
- Create 4-8 historical assessments per student per skill
- Spread across last 3 months
- Show realistic progression (scores improve/vary over time)
- Each with reasoning and evidence

**Creates:**
- ~2,100 skill_assessments (50 students × 7 skills × 6 historical points)
- ~6,300 evidence records

**Runtime:** ~20-30 minutes (AI-generated reasoning)

### Phase 2: Game Data (Required for ML Inference)
**Goal:** Populate game sessions and telemetry for feature extraction

#### Step 2.1: Create Game Sessions
**Script:** Create `scripts/seed_game_sessions.py`

**What it does:**
- Create 5-10 game sessions per student
- Spread across last 3 months
- Realistic session durations (10-45 minutes)
- Different missions/game versions

**Creates:**
- ~400 game_sessions (50 students × 8 sessions avg)

**Runtime:** ~1 minute

#### Step 2.2: Generate Game Telemetry Events
**Script:** Create `scripts/seed_game_telemetry.py`

**What it does:**
- Generate 100-500 telemetry events per session
- Different event types: mission_start, choice_made, challenge_completed, etc.
- Realistic event sequences
- JSON event_data with mission context

**Creates:**
- ~100,000 game_telemetry events (400 sessions × 250 events avg)

**Runtime:** ~5-10 minutes

**⚠️ Note:** This uses TimescaleDB hypertable for efficiency

### Phase 3: Transcripts and Conversations
**Goal:** Linguistic data for feature extraction

#### Step 3.1: Generate Transcripts
**Script:** Use existing `scripts/generate_synthetic_responses.py` or create new

**What it does:**
- Generate 2-4 conversation transcripts per student
- Realistic dialogue showing empathy, collaboration, etc.
- 10-20 turns per transcript
- Linked to game sessions

**Creates:**
- ~120 transcripts (50 students × 2.4 transcripts avg)

**Runtime:** ~10-15 minutes (AI-generated dialogue)

### Phase 4: Feature Extraction (ML Pipeline)
**Goal:** Extract features for ML inference

#### Step 4.1: Extract Linguistic Features
**Script:** Use existing `scripts/extract_linguistic_features.py`

**What it does:**
- Process transcripts using NLP
- Extract empathy markers, social processes, etc.
- Calculate sentiment scores
- Generate word embeddings

**Creates:**
- ~120 linguistic_features records (one per transcript)

**Runtime:** ~5-10 minutes

#### Step 4.2: Extract Behavioral Features
**Script:** Use existing `scripts/generate_behavioral_features.py`

**What it does:**
- Analyze telemetry events per session
- Calculate task completion rates, time efficiency
- Extract retry counts, recovery rates
- Focus duration, collaboration indicators

**Creates:**
- ~400 behavioral_features records (one per session)

**Runtime:** ~3-5 minutes

### Phase 5: Classes and Schools (Optional but Recommended)
**Goal:** Enable class-based filtering and heatmaps

#### Step 5.1: Seed Schools and Classes
**Script:** Use existing `scripts/seed_data.py` (schools section)

**What it does:**
- Create 2-3 schools
- Create 10-15 classes across grades 6-8
- Associate students with schools and classes

**Updates:**
- 50 students (add school_id, class assignments)
- Creates ~3 schools
- Creates ~15 class records

**Runtime:** ~1 minute

## Comprehensive Seed Script Execution Order

### Option A: Full Production-Ready Data (Recommended)

```bash
# Navigate to backend directory
cd /Users/reena/gauntletai/unseenedgeai/backend
source venv/bin/activate

# Phase 1: Complete skill assessments
echo "Phase 1: Adding missing skills..."
python scripts/add_missing_skills.py
# Adds adaptability, communication, collaboration for all 50 students
# Total: 350 assessments (7 skills × 50 students)

echo "Phase 1.2: Adding historical assessments..."
python scripts/seed_historical_assessments.py
# Adds 6 historical assessments per student per skill
# Total: 2,450 assessments (350 current + 2,100 historical)

# Phase 2: Game data
echo "Phase 2.1: Creating game sessions..."
python scripts/seed_game_sessions.py
# Creates 8 sessions per student across 3 months
# Total: 400 sessions

echo "Phase 2.2: Generating telemetry..."
python scripts/seed_game_telemetry.py
# Generates 200-300 events per session
# Total: ~100,000 telemetry events

# Phase 3: Transcripts
echo "Phase 3: Generating transcripts..."
python scripts/generate_synthetic_responses.py
# Generates 2-3 transcripts per student
# Total: 120 transcripts

# Phase 4: Feature extraction
echo "Phase 4.1: Extracting linguistic features..."
python scripts/extract_linguistic_features.py
# Processes transcripts
# Total: 120 linguistic_features

echo "Phase 4.2: Extracting behavioral features..."
python scripts/generate_behavioral_features.py
# Processes telemetry per session
# Total: 400 behavioral_features

# Phase 5: Schools and classes
echo "Phase 5: Adding schools and classes..."
python scripts/seed_schools_classes.py
# Creates schools and class associations
# Updates 50 students with class assignments

echo "✅ All data populated!"
```

**Total Runtime:** ~60-90 minutes
**Total Records Created:** ~105,000+

### Option B: Quick Dashboard Testing (Minimal)

```bash
cd /Users/reena/gauntletai/unseenedgeai/backend
source venv/bin/activate

# Just add missing skills for complete dashboard visualization
python scripts/add_missing_skills.py

# Add 2-3 historical assessments for trend visualization
python scripts/seed_minimal_historical.py  # Create this - just 2 points per skill

echo "✅ Minimal data ready for dashboard testing"
```

**Total Runtime:** ~10-15 minutes
**Total Records:** ~700 assessments

### Option C: ML-Ready Data (For Inference Testing)

```bash
cd /Users/reena/gauntletai/unseenedgeai/backend
source venv/bin/activate

# Skip historical assessments, focus on ML pipeline
python scripts/add_missing_skills.py
python scripts/seed_game_sessions.py
python scripts/seed_game_telemetry.py
python scripts/generate_synthetic_responses.py
python scripts/extract_linguistic_features.py
python scripts/generate_behavioral_features.py

echo "✅ ML inference endpoints ready"
```

**Total Runtime:** ~40-50 minutes
**Total Records:** ~100,500

## Scripts That Need to be Created

### 1. `scripts/add_missing_skills.py` ⭐ PRIORITY
```python
"""
Add adaptability, communication, collaboration assessments
to all 50 existing students.
"""
# Uses AI assessment service to generate 3 more skills per student
# Creates 150 new assessments + 450 evidence records
```

### 2. `scripts/seed_historical_assessments.py` ⭐ PRIORITY
```python
"""
Create 4-8 historical assessments per student per skill
over the last 3 months.
"""
# Generates time-series data for trend analysis
# Creates ~2,100 assessments + ~6,300 evidence records
```

### 3. `scripts/seed_game_sessions.py` ⭐ PRIORITY
```python
"""
Create realistic game sessions for all students.
"""
# Creates 5-10 sessions per student
# Spans last 3 months with realistic timing
```

### 4. `scripts/seed_game_telemetry.py` ⭐ PRIORITY
```python
"""
Generate telemetry events for each game session.
"""
# Creates 100-500 events per session
# Different event types, realistic sequences
```

### 5. `scripts/seed_schools_classes.py`
```python
"""
Create schools and class associations.
"""
# 2-3 schools, 10-15 classes
# Updates students with class assignments
```

### 6. `scripts/seed_minimal_historical.py` (for quick testing)
```python
"""
Quick version - just 2-3 historical assessments per skill.
"""
# Minimal time-series for testing trends
```

## Scripts That Already Exist

✅ `scripts/quick_seed_students.py` - Creates students (DONE)
✅ `scripts/seed_sample_assessments.py` - Creates initial assessments (DONE)
✅ `scripts/generate_synthetic_responses.py` - Generates transcripts
✅ `scripts/extract_linguistic_features.py` - Extracts NLP features
✅ `scripts/generate_behavioral_features.py` - Extracts telemetry features
✅ `scripts/seed_data.py` - Comprehensive seeding (has schools section)

## Dashboard Feature Completeness Matrix

| Dashboard Feature | Current Status | After Phase 1 | After Phase 2-3 | After Phase 4 |
|-------------------|----------------|---------------|-----------------|---------------|
| Skill distribution (7 skills) | ❌ 4/7 skills | ✅ 7/7 | ✅ 7/7 | ✅ 7/7 |
| Individual student scores | ✅ Working | ✅ Complete | ✅ Complete | ✅ Complete |
| Supporting evidence | ✅ Working | ✅ Enhanced | ✅ Enhanced | ✅ Enhanced |
| Trend analysis (time series) | ❌ No history | ✅ Available | ✅ Available | ✅ Available |
| Class overview | ❌ No classes | ❌ No classes | ❌ No classes | ⚠️ Need Phase 5 |
| Export reports | ⚠️ Incomplete | ✅ Complete | ✅ Complete | ✅ Complete |
| AI reasoning display | ✅ Working | ✅ Enhanced | ✅ Enhanced | ✅ Enhanced |
| ML inference endpoints | ❌ No features | ❌ No features | ⚠️ Need Phase 4 | ✅ Working |
| Real-time scoring | ❌ No features | ❌ No features | ⚠️ Need Phase 4 | ✅ Working |
| Heatmaps by class | ❌ No classes | ❌ No classes | ❌ No classes | ⚠️ Need Phase 5 |

## Recommended Approach

### For Immediate Dashboard Demo (TODAY):
```bash
# 1. Add missing 3 skills (~10 min)
python scripts/add_missing_skills.py

# 2. Add minimal historical data (~5 min)
python scripts/seed_minimal_historical.py

# Result: Complete dashboards with 7 skills + basic trends
```

### For Full Production System (THIS WEEK):
Run **Option A** above (all phases)
- Complete historical data
- Full ML pipeline ready
- All dashboard features working

### For ML Inference Testing (NEXT SPRINT):
Run **Option C** above (skip historical, focus on ML)
- Feature extraction working
- Inference endpoints functional
- Can switch from AI assessments to ML predictions

## Cloud Functions Integration

You mentioned cloud functions are set up. Here's how they integrate:

### If Cloud Functions Do Feature Extraction:
```bash
# Instead of running local scripts:
python scripts/extract_linguistic_features.py
python scripts/generate_behavioral_features.py

# Call cloud functions via API:
curl -X POST https://your-cloud-function/extract-linguistic \
  -d '{"transcript_ids": ["id1", "id2", ...]}'

curl -X POST https://your-cloud-function/extract-behavioral \
  -d '{"session_ids": ["id1", "id2", ...]}'
```

Update the seed scripts to call cloud functions instead of local processing.

## Summary - What to Run NOW

**Minimum for Dashboard Completion:**
```bash
cd /Users/reena/gauntletai/unseenedgeai/backend
source venv/bin/activate

# Create and run these 2 scripts:
python scripts/add_missing_skills.py          # 10 min - adds 3 skills
python scripts/seed_historical_assessments.py  # 20 min - adds time series

# Result: All dashboard visualizations complete
```

**Check results:**
```bash
# Should show 2,450 total assessments (7 skills × 50 students × 7 time points)
psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db \
  -c "SELECT COUNT(*) FROM skill_assessments;"

# Should show 7 distinct skills
psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db \
  -c "SELECT DISTINCT skill_type FROM skill_assessments;"
```

---

**Next Steps:**
1. Create `add_missing_skills.py` script
2. Create `seed_historical_assessments.py` script
3. Run both scripts
4. Verify dashboard completeness
5. (Optional) Add game data for ML inference later

**Timeline:**
- Phase 1 scripts creation: 30-45 minutes
- Phase 1 execution: 30 minutes
- Total: ~1-1.5 hours for complete dashboard functionality

Let me know which approach you'd like to take and I'll create the necessary scripts!
