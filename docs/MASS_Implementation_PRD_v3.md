# MASS: Middle School Non-Academic Skills Measurement System
## Implementation-Ready Product Requirements Document (Version 3.0)

**Organization:** Flourish Schools
**Project ID:** JnGyV0Xlx2AEiL31nu7J_1761530509243
**Date:** January 2025
**Status:** Implementation Ready
**Total Budget:** $485,000
**Timeline:** 38 weeks (9 months)

---

## Executive Summary

The Middle School Non-Academic Skills Measurement System (MASS) is an AI-driven platform that provides continuous, objective assessment of all 7 non-academic skills in middle school students through a multi-evidence approach:

**Four Evidence Layers:**
1. **Baseline Cognitive Assessment** - Initial learner profile (Phase 2)
2. **Game-Based Behavioral Assessment** - Flourish Academy MVP (Phase 1)
3. **AI-Driven Classroom Analysis** - Transcript + project analysis (Phase 1)
4. **Teacher Rubric Evaluation** - Structured human judgment (Phase 1)

**Phase 1 Delivers:**
- All 7 skills assessed: Empathy, Adaptability, Problem-Solving, Self-Regulation, Resilience, Communication, Collaboration
- Professional Unity game (3 missions, 30-45 minutes gameplay)
- Evidence fusion combining transcripts + game telemetry
- Teacher dashboard with evidence-based insights
- GPT-4 generated reasoning for all assessments

---

## Key Decisions & Rationale

### Decision 1: Speech-to-Text Strategy
**Choice:** Google Cloud Speech-to-Text for Phase 1, migrate to Whisper in Phase 2

**Rationale:**
- Fastest implementation (2-3 days vs 2 weeks)
- Zero DevOps overhead in Phase 1
- Focus team on core ML/game development
- Cost: $10,000 for Phase 1 pilot (acceptable for speed)
- Migration to Whisper in Phase 2 saves $32/student/month at scale

### Decision 2: Skills Coverage
**Choice:** All 7 skills in Phase 1

**Skills:**
1. Empathy (medium detectability from transcripts, high from game)
2. Adaptability (low from transcripts, high from game)
3. Problem-Solving (medium from transcripts, high from game)
4. Self-Regulation (low from transcripts, medium from game)
5. Resilience (low from transcripts, high from game)
6. Communication (high from transcripts, medium from game)
7. Collaboration (high from transcripts, high from game)

**Rationale:**
- Comprehensive validation of approach
- Demonstrates full PRD vision
- Game component essential for skills 2, 4, 5 (low transcript detectability)
- Meets stakeholder expectations for complete system

### Decision 3: Reasoning Generation
**Choice:** GPT-4 LLM-based reasoning

**Rationale:**
- 7 skills × 3 score levels = 21 templates (significant effort)
- GPT-4 provides nuanced, context-aware explanations
- Cost modest: $28/month for 100 students
- Can migrate to templates in Phase 2 if needed
- Quality impression critical for Phase 1 validation

### Decision 4: Game Component
**Choice:** Flourish Academy MVP (Unity-based, 3 missions)

**Rationale:**
- Professional quality, not prototype
- 95% reusable to full game in Phase 2
- Validates game-based assessment works
- Essential for detecting Adaptability, Self-Regulation, Resilience
- Impressive stakeholder demonstration
- 3 missions cover 5 of 7 skills adequately

### Decision 5: Phase 0 Budget
**Choice:** $40,000 (Recommended tier)

**Rationale:**
- 2,100 coded segments (300 per skill)
- Strong IRR (α ≥ 0.80 target)
- 70% real classroom audio, 30% synthetic
- Quality ground truth essential for 7-skill system
- Only 8% of total budget, high-leverage investment

---

## Functional Requirements

### P0 Requirements (Must-Have) - ALL MET

#### P0.1: Quantitative Skill Inference ✓
**Requirement:** Quantitatively infer student non-academic skill levels from classroom transcripts and project deliverables.

**Implementation:**
- Google Cloud Speech-to-Text: Classroom audio → transcripts (>75% accuracy expected)
- Linguistic feature extraction: LIWC + spaCy + custom patterns
- Behavioral feature extraction: Game telemetry → behavioral patterns
- XGBoost/Logistic Regression models: Features → skill scores (0-1 scale)
- Evidence fusion: Combine transcript + game signals with learned weights

**Acceptance Criteria:**
- All 7 skills have quantitative scores (0-1 scale)
- Correlation with teacher ratings: r ≥ 0.50 (target: r ≥ 0.55)
- Handles 6+ hours of classroom audio per day
- Inference latency: <30 seconds per student

#### P0.2: Evidence and Reasoning ✓
**Requirement:** Provide justifying evidence and reasoning for each inference.

**Implementation:**
- Evidence extraction: 3-5 snippets per skill from transcripts + game choices
- Source attribution: Timestamp, context, relevance score
- GPT-4 reasoning generation: 2-3 sentence growth-oriented explanation
- Confidence scoring: Based on evidence agreement and source reliability

**Acceptance Criteria:**
- Every skill score includes 3-5 evidence items
- Reasoning is clear, actionable, growth-oriented
- Teachers rate evidence as "helpful" (target: 75%+)
- Confidence scores correlate with actual accuracy

#### P0.3: Cloud Deployment ✓
**Requirement:** Support cloud deployment for scalability and accessibility.

**Implementation:**
- **Platform:** Google Cloud Platform (GCP)
- **Services:**
  - Cloud Run: API server (auto-scaling 0-100 instances)
  - Cloud SQL: PostgreSQL + TimescaleDB
  - Cloud Storage: Audio files and artifacts
  - Cloud Tasks: Async job queue
  - Cloud Pub/Sub: Event streaming
- **Infrastructure-as-Code:** Terraform scripts
- **CI/CD:** GitHub Actions

**Acceptance Criteria:**
- Supports 1,000+ concurrent users
- 95%+ uptime (Phase 1 target, 99.5% production)
- Auto-scaling responds within 30 seconds
- Multi-tenant architecture (isolated school data)

#### P0.4: High-Performance Parallel Processing ✓
**Requirement:** Handle parallel processing of full-day classroom transcripts.

**Implementation:**
- Cloud Tasks async queue: Transcription jobs
- Cloud Pub/Sub: Event-driven processing
- Parallel workers: Multiple Cloud Run instances process concurrently
- Batch processing: Full-day transcripts processed overnight
- TimescaleDB: Efficient time-series queries

**Acceptance Criteria:**
- Process 6 hours of classroom audio in <2 hours (for 30 students)
- Support 10 concurrent classrooms (300 students)
- Handle 100 GB/day of data
- Zero data loss under high load

---

## Phase 1 System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MASS System Architecture                 │
└─────────────────────────────────────────────────────────────┘

Student Interactions:
├─ Flourish Academy Game (Unity) ────┐
│                                     │
├─ Classroom Conversations ──────────┤
│   (Audio Recording)                 │
│                                     ▼
└─ Project Submissions ─────────► Backend API (FastAPI)
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
           Google Cloud STT   Game Telemetry    Project Text
               (Async)          Processing       Processing
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                          Feature Extraction Engine
                          (Linguistic + Behavioral)
                                      │
                                      ▼
                          ML Inference Models (7 skills)
                          ├─ XGBoost classifiers
                          └─ Logistic regression baseline
                                      │
                                      ▼
                          Evidence Fusion Engine
                          ├─ Multi-source weighting
                          ├─ Confidence calculation
                          └─ GPT-4 reasoning generation
                                      │
                                      ▼
                          PostgreSQL + TimescaleDB
                          (Skill assessments + evidence)
                                      │
                                      ▼
                          Teacher Dashboard (React)
                          ├─ Class overview
                          ├─ Student profiles
                          ├─ Evidence viewer
                          └─ Alerts & recommendations
```

---

## Technical Specifications

### Technology Stack

| Layer | Component | Technology | Rationale |
|-------|-----------|------------|-----------|
| **Game** | Flourish Academy | Unity 2022 LTS (C#) | Industry standard, 95% reusable to full game |
| **Frontend** | Teacher Dashboard | React + TypeScript | Type safety, fast development |
| **Backend** | API Server | FastAPI (Python 3.11) | Modern, excellent for ML/data science |
| **Task Queue** | Async Processing | Cloud Tasks + Pub/Sub | GCP-native, fully managed |
| **STT** | Speech-to-Text | Google Cloud STT | Fast Phase 1, migrate Whisper Phase 2 |
| **NLP** | Linguistic Analysis | spaCy + VADER + LIWC | Proven NLP tools |
| **ML** | Skill Inference | Scikit-learn + XGBoost | Interpretable, efficient |
| **Reasoning** | Explanations | OpenAI GPT-4 API | Best-in-class natural language |
| **Database** | Primary | PostgreSQL 15 | Mature, reliable |
| **Database** | Time-Series | TimescaleDB | Optimized for temporal queries |
| **Cache** | In-Memory | Redis | Fast, proven |
| **Cloud** | Infrastructure | Google Cloud Platform | Excellent AI/ML support |
| **Monitoring** | Observability | Cloud Logging + Monitoring | Integrated GCP |

### Data Model (Key Tables)

```sql
-- Core Entities
Students (id, name, school_id, grade_level, demographics)
Teachers (id, name, school_id, classes)
Schools (id, name, district_id, settings)
Classrooms (id, school_id, teacher_id, grade)

-- Audio & Transcription (P0.1)
AudioFiles (id, classroom_id, file_path, duration, status)
Transcripts (id, audio_file_id, full_text, confidence, diarization_data)
TranscriptSegments (id, transcript_id, student_id, text, start_time, end_time)

-- Game Telemetry (P0.1)
GameSessions (id, student_id, started_at, ended_at, mission_progress)
GameTelemetryEvents (id, session_id, event_type, event_data, timestamp)

-- Projects (P0.1)
Projects (id, classroom_id, title, due_date, project_type)
ProjectSubmissions (id, student_id, project_id, text, submitted_at)

-- Feature Extraction
LinguisticFeatures (id, student_id, source_id, empathy_markers, adapt_markers, ...)
BehavioralFeatures (id, student_id, session_id, task_completion, persistence, ...)

-- Skill Assessments (P0.1 - Quantitative Output)
SkillAssessments (
  id, student_id, skill,
  score FLOAT,           -- 0-1 scale (P0.1)
  confidence FLOAT,      -- 0-1 scale
  period_start, period_end,
  model_version, feature_importance JSONB
)

-- Evidence & Reasoning (P0.2)
EvidenceItems (
  id, assessment_id,
  evidence_type,         -- linguistic, behavioral, contextual
  source_type,           -- transcript, game, project
  evidence_text TEXT,    -- The actual evidence (P0.2)
  relevance_score
)

ReasoningExplanations (
  id, assessment_id,
  reasoning_text TEXT,   -- GPT-4 generated (P0.2)
  generated_at
)

-- Teacher Rubrics
TeacherRubricAssessments (
  id, student_id, teacher_id, skill,
  score INTEGER,         -- 1-4 scale
  feedback TEXT,
  assessment_date
)
```

---

## Flourish Academy MVP - Game Design

### Game Overview
**Title:** Flourish Academy
**Genre:** Narrative adventure with educational assessment
**Platform:** Windows/Mac/Linux (Unity standalone)
**Duration:** 30-45 minutes (3 missions)
**Assessment:** Stealth (students unaware of assessment)

### Missions

**Mission 1: "Understanding Perspectives" (Empathy)**
- **Setting:** Academy courtyard
- **NPCs:** Alex (new student feeling isolated)
- **Duration:** 10-12 minutes
- **Decisions:** 5 choice points
- **Skills Measured:** Empathy (primary)
- **Telemetry:**
  - Choice selection (empathetic vs self-focused)
  - Time spent reading dialogue (perspective-taking indicator)
  - Re-reading character dialogue (understanding effort)
  - Help-seeking behaviors

**Mission 2: "The Group Project Challenge" (Collaboration + Problem-Solving)**
- **Setting:** Academy classroom
- **NPCs:** Alex, Jordan (bossy), Sam (shy)
- **Duration:** 12-15 minutes
- **Decisions:** 7 choice points
- **Skills Measured:** Collaboration (primary), Problem-Solving (primary)
- **Telemetry:**
  - Task delegation patterns (fair vs autocratic)
  - Conflict resolution strategies
  - Resource allocation decisions
  - Planning approach (systematic vs random)
  - Turn-taking behaviors

**Mission 3: "The Unexpected Change" (Adaptability + Resilience)**
- **Setting:** Academy classroom (continuation)
- **NPCs:** All from Mission 2 + Mentor Maya
- **Duration:** 10-15 minutes
- **Decisions:** 6 choice points
- **Skills Measured:** Adaptability (primary), Resilience (primary), Self-Regulation (secondary)
- **Telemetry:**
  - Initial reaction to setback (frustration vs adaptive)
  - Strategy switching frequency (rigid vs flexible)
  - Persistence after failure (quit vs retry)
  - Emotional regulation indicators (time to recover)
  - Help-seeking patterns

### NPCs

1. **Mentor Maya** (3D model)
   - Wise guide character
   - Provides hints and encouragement
   - Represents authority and support

2. **Alex** (2D sprite)
   - Quiet, feels left out initially
   - Player builds relationship across all missions
   - Tests empathy and social inclusion

3. **Jordan** (2D sprite)
   - Confident, sometimes bossy
   - Creates natural conflict for collaboration testing
   - Tests conflict resolution skills

4. **Sam** (2D sprite)
   - Shy but helpful
   - Supports player when they make good choices
   - Reinforces positive collaborative behaviors

### Art & Audio

**Environments:**
- Academy Classroom (Unity Asset Store base + customization: $800)
- Academy Courtyard (Unity Asset Store: $600)

**Characters:**
- Mentor Maya: Custom 3D model (low-poly, stylized)
- Alex, Jordan, Sam: High-quality 2D sprites with emotional states

**Audio:**
- Licensed background music: $500
- Sound effects library: $300
- Text-to-speech for accessibility: Google Cloud TTS API

**UI/UX:**
- Clean, accessible interface
- Keyboard navigation support
- Adjustable text size
- Color-blind friendly palette

---

## Evidence Fusion Model

### Fusion Algorithm

```python
def calculate_fused_skill_score(student_id, skill, period_start, period_end):
    """
    Fuse evidence from multiple sources with learned weights
    """
    # Get scores from each source
    transcript_score = get_transcript_based_score(student_id, skill, period)
    game_score = get_game_based_score(student_id, skill, period)
    teacher_score = get_teacher_rubric_score(student_id, skill, period)

    # Skill-specific weights (learned from Phase 0 validation)
    weights = SKILL_WEIGHTS[skill]
    # Example for Empathy:
    # weights = {'transcript': 0.35, 'game': 0.40, 'teacher': 0.25}

    # Calculate weighted average
    fused_score = (
        transcript_score * weights['transcript'] +
        game_score * weights['game'] +
        teacher_score * weights['teacher']
    )

    # Calculate confidence based on agreement
    scores = [transcript_score, game_score, teacher_score]
    agreement = 1.0 - np.std(scores)  # Low std = high agreement
    confidence = min(agreement * 1.2, 1.0)

    return {
        'score': fused_score,
        'confidence': confidence,
        'sources': {
            'transcript': transcript_score,
            'game': game_score,
            'teacher': teacher_score
        }
    }
```

### Evidence Weights by Skill

| Skill | Transcript | Game | Teacher | Rationale |
|-------|-----------|------|---------|-----------|
| **Empathy** | 0.35 | 0.40 | 0.25 | Game scenarios best test empathy |
| **Adaptability** | 0.20 | 0.50 | 0.30 | Hard to detect in transcripts |
| **Problem-Solving** | 0.30 | 0.45 | 0.25 | Game shows process clearly |
| **Self-Regulation** | 0.25 | 0.40 | 0.35 | Teacher observation critical |
| **Resilience** | 0.25 | 0.50 | 0.25 | Game failure scenarios key |
| **Communication** | 0.50 | 0.25 | 0.25 | Transcripts are primary source |
| **Collaboration** | 0.40 | 0.35 | 0.25 | Both transcripts + game valuable |

---

## Success Metrics

### Phase 1 Validation Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Skill Inference Accuracy** | r ≥ 0.50 vs teacher ratings | Correlation analysis |
| **Optimal Target** | r ≥ 0.55 | Statistical validation |
| **Teacher Acceptance** | 70%+ rate assessments helpful | Post-pilot survey |
| **Evidence Quality** | 75%+ teachers find evidence relevant | Survey + interviews |
| **Student Engagement** | 80%+ complete all 3 missions | Game telemetry |
| **Student Enjoyment** | 75%+ rate game as fun | Student survey |
| **System Uptime** | 95%+ | Cloud monitoring |
| **Processing Speed** | 6hr audio processed in <2hr | Performance metrics |
| **STT Accuracy** | >75% in classroom settings | Manual validation sample |

### Phase 0 Success Criteria (Decision Gate)

**Proceed to Phase 1 IF:**
- ✓ IRR: Krippendorff's Alpha ≥ 0.75 on all 7 skills
- ✓ Correlation: Average r ≥ 0.45 (features → ground truth scores)
- ✓ Sample Quality: <5% unusable transcript segments
- ✓ Coverage: ≥280 usable annotations per skill

---

## Budget Summary

### Phase 0: Ground Truth Collection
**Duration:** 14 weeks
**Budget:** $40,000

- Data Scientist: $32,000
- Expert Coders (4): $6,440
- External Consultant: $3,000
- Data Collection: $2,000
- Tools & Platform: $500

**Deliverables:**
- 2,100 dual-coded transcript segments
- 7 validated skill rubrics
- IRR report (α ≥ 0.75)
- Feasibility analysis

---

### Phase 1: System Development
**Duration:** 24 weeks
**Budget:** $445,000

**Backend Development:** $180,000
- STT integration & pipeline
- Feature extraction (linguistic + behavioral)
- ML model training (7 skills)
- Evidence fusion engine
- GPT-4 reasoning integration
- API development
- Database implementation

**Game Development:** $220,000
- 3 Unity missions (30-45 min gameplay)
- 4 NPC characters (1 3D, 3 2D)
- 2 environments (classroom + courtyard)
- Telemetry integration
- UI/UX design
- Text-to-speech accessibility

**Infrastructure & Tools:** $30,000
- GCP costs (6 months): $8,000
- Unity assets: $5,500
- Google Cloud STT: $10,000
- OpenAI GPT-4 API: $400
- SaaS tools: $3,000
- Misc: $3,100

**Pilot & Validation:** $15,000
- School partnerships: $5,000
- Recording equipment: $3,000
- Student incentives: $2,000
- Teacher training: $5,000

---

### Total Project Investment
**Phase 0 + Phase 1:** $485,000
**Timeline:** 38 weeks (9 months)

---

## Implementation Phases

### Phase 0: Weeks 1-14
**Ground Truth Collection & Validation**

Key Milestones:
- Week 2: Rubrics developed
- Week 6: IRR ≥ 0.75 achieved
- Week 12: Annotation complete (2,100 segments)
- Week 14: Feasibility study, GO/NO-GO decision

### Phase 1: Weeks 15-38 (24 weeks)
**Full System Development**

Key Milestones:
- Week 4 (18): Infrastructure deployed
- Week 8 (22): STT + feature extraction working
- Week 12 (26): ML models trained, Mission 1 complete
- Week 16 (30): Full system integrated, all 3 missions done
- Week 20 (34): Testing complete, pilot ready
- Week 24 (38): Pilot complete, validation results

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| STT accuracy <75% | Medium | High | Accept 75-80% as sufficient; confidence scoring for low-quality segments |
| Game development delays | Medium | High | 3-mission MVP (not 5); use Asset Store for environments |
| Model performance r <0.50 | Medium | Critical | Phase 0 validation catches this early; pivot if needed |
| Cloud costs exceed budget | Low | Medium | Monitoring + alerts; use free tiers where possible |

### Organizational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Teacher skepticism | High | Medium | Transparency in evidence; growth-oriented language; training |
| Low pilot participation | Medium | High | Multiple school partnerships; student incentives |
| Privacy concerns | Medium | High | Clear consent process; FERPA compliance; opt-out option |

---

## Out of Scope (Phase 1)

**Deferred to Phase 2:**
- Baseline cognitive assessment (PRD Layer 1)
- Whisper STT migration (cost optimization)
- Full Flourish Academy (5 missions, voice acting)
- Advanced analytics & predictive models
- Parent portal
- Mobile app

**Deferred to Phase 3:**
- Multi-language support
- District-level dashboards
- Advanced customization & reporting
- Integration with non-educational platforms

---

## Appendix: API Endpoints

### Core Endpoints

```
Authentication:
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

Audio & Transcription:
POST   /api/v1/audio/upload
GET    /api/v1/transcripts/{student_id}
GET    /api/v1/transcripts/{transcript_id}

Game Telemetry:
POST   /api/v1/game/telemetry/events
POST   /api/v1/game/telemetry/batch
GET    /api/v1/game/sessions/{student_id}

Skill Assessments:
GET    /api/v1/skills/{student_id}
GET    /api/v1/skills/{student_id}/history
GET    /api/v1/skills/{student_id}/{skill}
GET    /api/v1/evidence/{assessment_id}
GET    /api/v1/reasoning/{assessment_id}

Teacher Dashboard:
GET    /api/v1/dashboard/class/{class_id}
GET    /api/v1/dashboard/student/{student_id}
GET    /api/v1/dashboard/alerts

Teacher Rubrics:
POST   /api/v1/rubrics/assessment
GET    /api/v1/rubrics/{student_id}

System:
GET    /api/v1/jobs/{job_id}/status
GET    /api/v1/health
```

---

## Document Control

**Version:** 3.0 (Implementation Ready)
**Date:** January 2025
**Status:** Approved for Implementation
**Next Review:** End of Phase 0 (Week 14)

**Change Log:**
- v1.0: Original Project Brief
- v2.0: Comprehensive PRD (full vision)
- v3.0: Implementation PRD (with decisions & budget)

---

*This PRD represents the implementable plan based on systematic decision-making process. All requirements meet Project Brief P0 criteria while building toward full PRD vision.*
