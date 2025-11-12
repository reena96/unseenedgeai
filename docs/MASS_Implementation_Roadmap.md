# MASS Implementation Roadmap
## Week-by-Week Execution Guide

**Project:** Middle School Non-Academic Skills Measurement System
**Date:** January 2025
**Total Duration:** 38 weeks (9 months)
**Total Budget:** $485,000

---

## Table of Contents

1. [Phase Overview](#phase-overview)
2. [Phase 0: Ground Truth Collection (Weeks 1-14)](#phase-0-ground-truth-collection-weeks-1-14)
3. [Phase 1: System Development (Weeks 15-38)](#phase-1-system-development-weeks-15-38)
4. [Team Structure & Roles](#team-structure--roles)
5. [Risk Management & Contingencies](#risk-management--contingencies)
6. [Success Criteria & Decision Gates](#success-criteria--decision-gates)
7. [Weekly Status Reporting](#weekly-status-reporting)

---

## Phase Overview

### Phase 0: Ground Truth Collection
**Duration:** 14 weeks
**Budget:** $40,000
**Goal:** Validate that AI can predict non-academic skills from transcripts + game data
**Decision Gate:** Week 14 - GO/NO-GO based on correlation ≥0.45

### Phase 1: System Development
**Duration:** 24 weeks
**Budget:** $445,000
**Goal:** Full system delivering assessments for all 7 skills
**Deliverable:** Production-ready pilot system

---

## Phase 0: Ground Truth Collection (Weeks 1-14)

### Week 1: Project Kickoff & Rubric Design

**Team:**
- Data Scientist (40 hrs)
- Educational Psychologist Consultant (8 hrs)

**Deliverables:**
- [ ] Project workspace setup (GitHub, GCP project, Slack)
- [ ] Initial rubric drafts for all 7 skills
- [ ] Annotation platform selected (Label Studio, Prodigy, or custom)
- [ ] Expert coder recruitment postings live

**Activities:**
1. **Monday-Tuesday:** Infrastructure setup
   - Create GitHub repository
   - Set up GCP project (free tier)
   - Configure Label Studio on Cloud Run
   - Create data collection templates

2. **Wednesday-Thursday:** Rubric development
   - Review academic literature on each skill
   - Draft 7 skill rubrics (1-4 scale with behavioral anchors)
   - Review with educational psychologist

3. **Friday:** Recruitment launch
   - Post on teacher job boards (Indeed, EdSurge)
   - Reach out to teacher networks
   - Schedule interviews for Week 2

**Budget:** $3,800
**Key Risk:** Finding qualified expert coders quickly

---

### Week 2: Rubric Refinement & Coder Onboarding

**Team:**
- Data Scientist (40 hrs)
- Educational Psychologist Consultant (4 hrs)
- Expert Coders (4 coders × 4 hrs each = 16 hrs)

**Deliverables:**
- [ ] Finalized rubrics for all 7 skills
- [ ] 4 expert coders hired and trained
- [ ] 50 practice transcripts annotated
- [ ] Initial inter-rater reliability (IRR) baseline

**Activities:**
1. **Monday:** Rubric finalization
   - Incorporate consultant feedback
   - Create detailed annotation guidelines
   - Build example annotations for each skill level

2. **Tuesday-Wednesday:** Coder training
   - 2-hour training session (all coders + consultant)
   - Practice on 10 sample transcripts
   - Q&A and clarification

3. **Thursday-Friday:** Pilot annotations
   - Each coder annotates 50 transcripts independently
   - Calculate baseline IRR (expect ~0.50-0.60)
   - Identify disagreement patterns

**Budget:** $3,500
**Key Milestone:** Baseline IRR calculated

---

### Week 3-4: First Annotation Sprint (300 segments)

**Team:**
- Data Scientist (40 hrs/week)
- Expert Coders (4 × 10 hrs/week = 40 hrs)

**Deliverables:**
- [ ] 300 transcript segments dual-coded
- [ ] IRR report (target: α ≥0.65)
- [ ] Rubric adjustments documented
- [ ] Data collection pipeline tested

**Activities:**
- **Daily:** Each coder annotates 15-20 segments
- **Data Scientist:**
  - Monitor annotation quality
  - Calculate weekly IRR
  - Provide feedback to coders
  - Adjust rubrics based on disagreements
- **Friday:** Weekly sync meeting
  - Review IRR progress
  - Discuss edge cases
  - Refine rubrics

**Budget (2 weeks):** $7,800
**Key Risk:** IRR below 0.65 → may need additional training

---

### Week 5-6: Second Annotation Sprint (600 segments)

**Team:**
- Data Scientist (40 hrs/week)
- Expert Coders (4 × 12 hrs/week = 48 hrs)

**Deliverables:**
- [ ] 600 transcript segments dual-coded (900 total)
- [ ] IRR report (target: α ≥0.75)
- [ ] Feature extraction pipeline built
- [ ] Preliminary correlation analysis

**Activities:**
- **Data Scientist:**
  - Build feature extraction pipeline (spaCy, VADER, LIWC)
  - Extract linguistic features from annotated segments
  - Run preliminary correlation: features → ground truth scores
  - Target: r ≥ 0.30 at this stage
- **Coders:** Continue dual-coding (20-25 segments/week each)

**Budget (2 weeks):** $8,200
**Key Milestone:** IRR ≥ 0.75 achieved

---

### Week 7-10: Full Annotation (1,200 more segments)

**Team:**
- Data Scientist (40 hrs/week)
- Expert Coders (4 × 12 hrs/week = 48 hrs)

**Deliverables:**
- [ ] 2,100 total segments annotated (300 per skill)
- [ ] IRR maintained at α ≥0.75
- [ ] Feature engineering complete
- [ ] Baseline ML models trained

**Activities (Week 7-8):**
- Continue annotation at steady pace
- Data Scientist: Advanced feature engineering
  - N-gram patterns for each skill
  - Contextual embeddings (sentence-transformers)
  - Behavioral proxies from linguistic patterns

**Activities (Week 9-10):**
- Complete final annotations
- Data Scientist: Train baseline models
  - Logistic regression (interpretable baseline)
  - XGBoost models (one per skill)
  - 70/30 train/test split
  - Target: r ≥ 0.40 on held-out test set

**Budget (4 weeks):** $16,400
**Key Milestone:** All annotations complete, models trained

---

### Week 11-12: Game Telemetry Design & Synthetic Data

**Team:**
- Data Scientist (40 hrs/week)
- Game Designer Consultant (8 hrs)

**Deliverables:**
- [ ] Game telemetry specification document
- [ ] Synthetic game data generator
- [ ] Multi-modal fusion model designed
- [ ] Phase 0 analysis report drafted

**Activities:**
- **Week 11:**
  - Design telemetry events for 3 game missions
  - Map game choices → skill indicators
  - Create synthetic game data (300 fake players)
  - Extract behavioral features from game data

- **Week 12:**
  - Train multi-source fusion models
  - Combine transcript + game features
  - Test different weighting schemes
  - Document optimal fusion approach

**Budget (2 weeks):** $7,200
**Key Output:** Fusion model architecture validated

---

### Week 13-14: Phase 0 Analysis & GO/NO-GO Decision

**Team:**
- Data Scientist (40 hrs/week)
- External Statistician (8 hrs)

**Deliverables:**
- [ ] **Phase 0 Final Report**
- [ ] Statistical validation (external review)
- [ ] Recommendation: GO or NO-GO
- [ ] Phase 1 detailed plan (if GO)

**Report Contents:**
1. **Inter-Rater Reliability:**
   - Krippendorff's Alpha for each skill
   - Confusion matrices
   - Edge case analysis

2. **Predictive Validity:**
   - Correlation: features → ground truth (per skill)
   - Model performance metrics (MAE, RMSE)
   - Feature importance rankings

3. **Multi-Source Fusion:**
   - Optimal weights: transcript vs game vs teacher
   - Confidence scoring approach
   - Evidence extraction strategy

4. **Recommendation:**
   - GO if: IRR ≥0.75 AND avg correlation ≥0.45
   - NO-GO if: Critical failures in detectability

**Budget (2 weeks):** $7,200
**CRITICAL MILESTONE:** Decision Gate

---

## Phase 1: System Development (Weeks 15-38)

### Week 15-16: Infrastructure & Team Ramp-Up

**Team Onboarding:**
- Backend Engineer (full-time start)
- Game Developer (full-time start)
- Frontend Engineer (half-time start)
- ML Engineer (full-time start)

**Deliverables:**
- [ ] GCP infrastructure deployed
- [ ] Database schema implemented
- [ ] CI/CD pipeline configured
- [ ] Game Unity project initialized
- [ ] Team knowledge transfer complete

**Activities:**

**Backend Engineer:**
- Set up GCP project (production)
- Deploy Cloud SQL (PostgreSQL + TimescaleDB)
- Create Cloud Storage buckets
- Set up Cloud Tasks & Pub/Sub
- Implement database migrations (Alembic)

**Game Developer:**
- Initialize Unity 2022 LTS project
- Set up version control (Git LFS for assets)
- Install core packages (Cinemachine, TextMeshPro)
- Create project structure
- Design Mission 1 flowchart

**Frontend Engineer:**
- Initialize React + TypeScript project
- Set up component library (Material-UI or Chakra)
- Configure API client (Axios)
- Build authentication flow UI

**ML Engineer:**
- Port Phase 0 models to production format
- Create model serving infrastructure
- Set up MLflow for experiment tracking
- Build feature extraction service

**Budget:** $28,000
**Key Risk:** Team coordination and knowledge transfer

---

### Week 17-18: Core API Development + Mission 1 Start

**Deliverables:**
- [ ] Authentication API complete
- [ ] Audio upload API complete
- [ ] Database CRUD operations
- [ ] Mission 1: Environment and NPCs designed
- [ ] Feature extraction service deployed

**Backend Engineer (40 hrs/week):**
- Implement FastAPI endpoints:
  - `/api/v1/auth/*` (login, refresh, logout)
  - `/api/v1/audio/upload` (with GCS integration)
  - `/api/v1/students/*` (CRUD)
  - `/api/v1/teachers/*` (CRUD)
- Write unit tests (Pytest)

**Game Developer (40 hrs/week):**
- Mission 1: "Understanding Perspectives"
  - Design academy courtyard environment
  - Purchase & integrate environment assets ($600)
  - Create Mentor Maya 3D model (low-poly)
  - Create Alex 2D sprite with emotional states
  - Implement basic dialogue system

**ML Engineer (40 hrs/week):**
- Deploy feature extraction service
- Integrate spaCy + VADER + LIWC
- Build async processing worker
- Test on sample transcripts

**Frontend Engineer (20 hrs/week):**
- Build login page
- Build teacher dashboard shell
- Set up routing (React Router)

**Budget:** $29,000

---

### Week 19-20: STT Integration + Mission 1 Completion

**Deliverables:**
- [ ] Google Cloud STT integrated
- [ ] Transcription pipeline working end-to-end
- [ ] Mission 1 fully playable (10-12 min)
- [ ] Telemetry events firing correctly

**Backend Engineer:**
- Integrate Google Cloud Speech-to-Text
- Implement async transcription worker
- Build speaker diarization mapping
- Create Cloud Tasks queue for STT jobs
- Test with sample classroom audio

**Game Developer:**
- Complete Mission 1 implementation:
  - 5 choice points with branching dialogue
  - Empathy-testing scenarios
  - Telemetry integration (choice tracking)
  - Time-on-dialogue tracking
  - Help-seeking behavior tracking
- Polish: lighting, sound effects, UI

**ML Engineer:**
- Build linguistic feature extraction pipeline
- Create transcript segmentation logic
- Implement student-speaker mapping algorithm
- Test feature extraction on transcribed audio

**Frontend Engineer:**
- Build audio upload interface
- Build transcription status viewer
- Create loading states and error handling

**Budget:** $29,000
**Key Milestone:** First end-to-end flow (audio → transcript → features)

---

### Week 21-22: ML Inference Service + Mission 2 Start

**Deliverables:**
- [ ] All 7 skill models deployed
- [ ] Inference API working
- [ ] Mission 2 environment and NPCs created
- [ ] Dashboard: Class overview page

**ML Engineer:**
- Package all 7 XGBoost models for production
- Build inference service (`/api/v1/skills/infer`)
- Implement batch inference for full classroom
- Add model versioning and A/B testing infrastructure
- Create inference worker (Cloud Tasks)

**Backend Engineer:**
- Build skills API endpoints:
  - `GET /api/v1/skills/{student_id}`
  - `GET /api/v1/skills/{student_id}/history`
  - `GET /api/v1/evidence/{assessment_id}`
- Implement caching (Redis)
- Write integration tests

**Game Developer:**
- Mission 2: "The Group Project Challenge"
  - Create classroom environment (Asset Store: $800)
  - Create Jordan and Sam 2D sprites
  - Design 7 choice points
  - Implement resource allocation mini-game
  - Add task delegation mechanics

**Frontend Engineer:**
- Build class overview heatmap
- Show all students × 7 skills in grid
- Color-coding: red/yellow/green by score
- Sorting and filtering controls

**Budget:** $29,000

---

### Week 23-24: Evidence Fusion + Mission 2 Completion

**Deliverables:**
- [ ] Evidence fusion service deployed
- [ ] Multi-source weighting implemented
- [ ] Mission 2 fully playable (12-15 min)
- [ ] Dashboard: Student detail page

**ML Engineer:**
- Build evidence fusion service
- Implement skill-specific weighting
  - Empathy: transcript 0.35, game 0.40, teacher 0.25
  - Adaptability: transcript 0.20, game 0.50, teacher 0.30
  - (etc. for all 7 skills)
- Calculate confidence scores (agreement-based)
- Build evidence extraction logic (top 3-5 snippets per skill)

**Game Developer:**
- Complete Mission 2:
  - Collaboration telemetry (turn-taking, delegation)
  - Problem-solving telemetry (planning patterns)
  - Conflict resolution scenarios
  - Polish and playtesting
- Integrate with backend API (POST telemetry events)

**Backend Engineer:**
- Build evidence retrieval API
- Implement teacher rubric CRUD endpoints
- Create fusion worker (combines all sources)
- Add database indexes for performance

**Frontend Engineer:**
- Build student detail page:
  - Skill scores with confidence bands
  - Evidence snippets viewer
  - Historical trend chart (line graph)
  - Teacher notes section

**Budget:** $29,000
**Key Milestone:** Week 24 = 50% through Phase 1

---

### Week 25-26: GPT-4 Reasoning + Mission 3 Start

**Deliverables:**
- [ ] GPT-4 reasoning generation working
- [ ] All assessments have explanations
- [ ] Mission 3 designed and environment created
- [ ] Dashboard: Evidence viewer page

**ML Engineer:**
- Integrate OpenAI GPT-4 API
- Build reasoning generation service
- Create prompts for all 7 skills
- Implement caching (avoid re-generating)
- Test reasoning quality (manual review)
- Cost monitoring (OpenAI usage)

**Backend Engineer:**
- Build reasoning API endpoint
- Store reasoning_explanations in database
- Add reasoning to skill assessment response
- Implement rate limiting for GPT-4 calls
- Create async reasoning worker

**Game Developer:**
- Mission 3: "The Unexpected Change"
  - Use Mission 2 classroom (reuse assets)
  - Design 6 choice points (adaptability focus)
  - Create setback scenarios (group project changed)
  - Implement failure/retry mechanics
  - Add emotional regulation timing tracking

**Frontend Engineer:**
- Build evidence viewer component
  - Timeline view of evidence items
  - Source highlighting (transcript vs game)
  - Relevance scores displayed
  - Context expansion (before/after text)

**Budget:** $29,000

---

### Week 27-28: Full Game Integration + Testing Infrastructure

**Deliverables:**
- [ ] Mission 3 complete - Full game playable (30-45 min)
- [ ] All 3 missions integrated and polished
- [ ] Game telemetry fully connected to backend
- [ ] Comprehensive testing suite

**Game Developer:**
- Complete Mission 3:
  - Adaptability telemetry (strategy switching)
  - Resilience telemetry (retry patterns, persistence)
  - Self-regulation telemetry (time to recover)
  - Polish: transitions between missions
  - Add progress save/load system
  - Accessibility features (text size, colorblind mode)

- Full game integration:
  - Opening tutorial
  - Mission select screen
  - Ending summary with encouragement
  - Test full 30-45 min playthrough

**Backend Engineer:**
- Build integration test suite
- Test full pipeline: audio → transcript → features → inference → reasoning
- Performance testing (load test with 100 concurrent users)
- Database query optimization
- API documentation (Swagger/OpenAPI)

**ML Engineer:**
- End-to-end ML pipeline testing
- Validate all 7 skill models on synthetic data
- Behavioral feature extraction from game telemetry
- Test fusion weights with synthetic multi-source data
- Create model evaluation dashboard (MLflow)

**Frontend Engineer:**
- Testing: Jest + React Testing Library
- E2E tests: Playwright or Cypress
- Accessibility audit (WCAG 2.1)
- Responsive design testing

**Budget:** $29,000
**Key Milestone:** Week 28 = Full system functional

---

### Week 29-30: Dashboard Polish + System Integration Testing

**Deliverables:**
- [ ] All dashboard features complete
- [ ] Admin view functional
- [ ] Student view functional
- [ ] Full system integration validated

**Frontend Engineer (now full-time):**
- Administrator Dashboard:
  - Cohort-wide skill heatmaps
  - School-level trend analysis
  - Intervention alerts (students below threshold)
  - Export functionality (CSV, PDF reports)

- Student Dashboard:
  - Skill growth over time
  - Strengths and growth areas
  - Reflection prompts
  - Gamification (badges for growth)

- UI/UX Polish:
  - Loading states and skeletons
  - Error handling and user feedback
  - Help tooltips and onboarding
  - Mobile responsive design

**Backend Engineer:**
- Dashboard API endpoints
- Aggregation queries for cohort views
- Data export functionality
- Performance optimization (caching aggregates)

**ML Engineer:**
- Final model tuning
- A/B test setup (compare model versions)
- Drift detection monitoring
- Feature store implementation

**Game Developer:**
- Game launcher and packaging
  - Windows build
  - Mac build
  - Linux build (optional)
- Installer creation
- Game telemetry validation
- Final playtesting and bug fixes

**Budget:** $29,000

---

### Week 31-32: Security Audit + Compliance Review

**Deliverables:**
- [ ] Security audit complete
- [ ] FERPA compliance validated
- [ ] COPPA compliance validated
- [ ] Data privacy documentation

**All Team Members (focused effort):**

**Backend Engineer:**
- Security hardening:
  - Input validation on all endpoints
  - SQL injection prevention (parameterized queries)
  - XSS prevention
  - CSRF tokens
  - Rate limiting
- Penetration testing (use external tool: OWASP ZAP)
- Secret rotation procedures
- Backup and disaster recovery testing

**Frontend Engineer:**
- Security review:
  - Content Security Policy (CSP)
  - Secure cookie handling
  - XSS prevention in React
  - Sensitive data handling
- Privacy-focused UX:
  - Clear consent flows
  - Data deletion requests
  - Privacy policy display

**ML Engineer:**
- Model security:
  - Input sanitization for feature extraction
  - Prevent prompt injection in GPT-4 calls
  - Model access controls
  - PII detection in transcripts

**Compliance Documentation:**
- FERPA compliance checklist
- COPPA parental consent flow
- Data retention policy (delete after graduation + 1 year)
- Audit logging review
- Terms of Service and Privacy Policy

**Budget:** $29,000
**Key Deliverable:** Security & Compliance Report

---

### Week 33: School Partnership Setup + Pilot Planning

**Deliverables:**
- [ ] 2-3 pilot schools confirmed
- [ ] Teacher training materials created
- [ ] Pilot timeline and logistics finalized
- [ ] Recording equipment procured

**Activities:**

**Project Manager / Lead:**
- Outreach to partner schools
- Negotiate pilot agreements
- Schedule teacher training sessions
- Plan student consent process

**Backend Engineer:**
- Multi-tenant setup (separate data per school)
- School onboarding flow
- Bulk student import (CSV)
- Teacher account creation

**Frontend Engineer:**
- Teacher onboarding wizard
- Training video embeds
- Help documentation
- Support chat widget

**Logistics:**
- Purchase recording equipment:
  - 3 classroom microphones ($1,000 each)
  - Audio interface and cables
  - Backup equipment
- Ship to pilot schools

**Budget:** $24,000 (includes partnerships & equipment)

---

### Week 34-35: Teacher Training + Pilot Kickoff

**Deliverables:**
- [ ] Teachers trained on MASS system
- [ ] Students complete baseline game sessions
- [ ] First week of classroom audio collected
- [ ] Pilot monitoring dashboard active

**Activities:**

**Week 34: Training Week**
- **Monday-Tuesday:** Teacher training (virtual + in-person)
  - System overview and goals
  - How to upload audio
  - How to read skill assessments
  - How to use rubric scoring interface
  - Privacy and consent procedures

- **Wednesday:** Student orientation
  - Students play Flourish Academy (30-45 min)
  - Baseline game telemetry collected
  - Troubleshoot any technical issues

- **Thursday-Friday:** First classroom recordings
  - Teachers record 2-hour class sessions
  - Upload via dashboard
  - Monitor transcription quality

**Week 35: Pilot Operations**
- Daily: Classroom audio collection continues
- Monitor STT accuracy and diarization quality
- Provide technical support to teachers
- Collect teacher feedback (daily quick surveys)

**All Engineers:**
- On-call support rotation
- Bug fixes and quick improvements
- Monitor system performance and logs
- Address issues within 24 hours

**Budget:** $29,000 (includes teacher stipends: $5,000)

---

### Week 36-37: Pilot Execution + Data Collection

**Deliverables:**
- [ ] 4 weeks of classroom audio collected
- [ ] Game sessions: 80%+ completion rate
- [ ] Teacher rubric assessments: 100% complete
- [ ] First skill assessments generated

**Ongoing Activities:**

**Daily Operations:**
- Classroom audio uploaded and transcribed
- Students complete game sessions (makeup sessions for absences)
- Teachers complete weekly rubric assessments
- Technical support provided as needed

**Data Quality Monitoring:**
- STT accuracy checks (sample validation)
- Speaker diarization review
- Game telemetry completeness
- Feature extraction error rates

**Weekly:**
- Generate skill assessments for all students
- Share with teachers for feedback
- Collect qualitative feedback (interviews)
- Iterate on dashboard based on feedback

**Engineering Team:**
- Bug fixes and patches deployed continuously
- Performance optimization (if slow queries found)
- Data validation and error handling improvements
- Prepare final reporting queries

**Budget:** $29,000
**Key Milestone:** Week 37 = Pilot data collection complete

---

### Week 38: Pilot Analysis + Final Validation

**Deliverables:**
- [ ] **Final Validation Report**
- [ ] Success metrics calculated
- [ ] Teacher satisfaction survey results
- [ ] Recommendations for Phase 2

**Analysis Activities:**

**Quantitative Validation:**
1. **Skill Inference Accuracy:**
   - Correlation: MASS scores vs teacher rubric scores (per skill)
   - Target: r ≥ 0.50 (optimal: r ≥ 0.55)
   - Statistical significance testing

2. **System Performance:**
   - STT accuracy (>75% target)
   - Processing time (6hr audio in <2hr)
   - System uptime (95%+)
   - Dashboard load time (<2s)

3. **Student Engagement:**
   - Game completion rate (80%+ target)
   - Average playtime
   - Mission completion breakdown

**Qualitative Validation:**
1. **Teacher Feedback:**
   - Survey: 70%+ rate assessments as helpful (target)
   - Interviews: Evidence quality, usefulness, trust
   - Suggestions for improvement

2. **Student Feedback:**
   - Survey: 75%+ rate game as fun (target)
   - Engagement observations
   - Accessibility feedback

**Final Report Contents:**
1. Executive Summary
2. Success Metrics (achieved vs target)
3. Correlation Analysis (all 7 skills)
4. Evidence Quality Review
5. Teacher Testimonials
6. Lessons Learned
7. Recommendations for Phase 2
8. Cost Analysis (actual vs budget)

**Budget:** $14,500
**FINAL MILESTONE:** Phase 1 Complete

---

## Team Structure & Roles

### Phase 0 (Weeks 1-14)

| Role | Time Commitment | Rate | Total Cost |
|------|----------------|------|------------|
| Data Scientist | 40 hrs/week × 14 weeks | $80/hr | $44,800 |
| Expert Coders (4) | Variable (avg 10 hr/week/person) | $30/hr | $16,800 |
| Educational Psychologist | 20 hrs total | $150/hr | $3,000 |
| Game Designer Consultant | 8 hrs | $100/hr | $800 |
| External Statistician | 8 hrs | $150/hr | $1,200 |

**Subtotal Phase 0 Labor:** $66,600
*(Note: This exceeds $40K budget quoted in PRD - needs reconciliation or Phase 0 is $67K)*

### Phase 1 (Weeks 15-38)

| Role | Time Commitment | Rate | Total Cost |
|------|----------------|------|------------|
| Backend Engineer | 40 hrs/week × 24 weeks | $90/hr | $86,400 |
| Game Developer | 40 hrs/week × 24 weeks | $85/hr | $81,600 |
| ML Engineer | 40 hrs/week × 24 weeks | $90/hr | $86,400 |
| Frontend Engineer | 30 hrs/week × 24 weeks | $85/hr | $61,200 |
| Project Manager | 10 hrs/week × 24 weeks | $75/hr | $18,000 |

**Subtotal Phase 1 Labor:** $333,600

### Phase 1 Non-Labor Costs

| Category | Items | Cost |
|----------|-------|------|
| **Infrastructure** | GCP (6 months), Cloud SQL, Cloud Run, Storage | $8,000 |
| **Game Assets** | Unity Asset Store, audio, sprites | $5,500 |
| **API Costs** | Google STT (pilot), OpenAI GPT-4 | $10,400 |
| **Tools** | GitHub, Sentry, monitoring tools | $3,000 |
| **Pilot Costs** | School partnerships, incentives, equipment | $10,000 |
| **Equipment** | Recording hardware (3 schools) | $3,000 |
| **Misc** | Licenses, domains, contingency | $3,100 |

**Subtotal Phase 1 Non-Labor:** $43,000

**Phase 1 Total:** $376,600
*(Note: This is less than $445K quoted - reconcile or adjust team rates/hours)*

---

## Risk Management & Contingencies

### Critical Risks & Mitigations

| Risk | Probability | Impact | Mitigation Strategy | Contingency Budget |
|------|------------|--------|---------------------|-------------------|
| **Phase 0: IRR < 0.75** | Medium | High | Extra training week, rubric refinement | +$2,000 |
| **Phase 0: Correlation < 0.45** | Medium | Critical | Pivot model approach, add features | +$5,000 |
| **Game development delays** | High | High | 3-mission MVP (not 5), use Asset Store | Already budgeted |
| **STT accuracy < 75%** | Medium | High | Accept 75-80%, confidence scoring | No extra cost |
| **Pilot school dropout** | Low | High | Recruit 3 schools (need only 2) | +$3,000 |
| **Cloud costs exceed budget** | Low | Medium | Monitoring + alerts, optimize queries | +$2,000 |
| **Team attrition** | Low | High | Overlapping knowledge transfer, documentation | +$5,000 |
| **Security vulnerability** | Low | Critical | External security audit (Week 31-32) | Already budgeted |

**Total Contingency Reserve:** $17,000 (3.5% of total budget)

---

## Success Criteria & Decision Gates

### Phase 0 Decision Gate (Week 14)

**GO Criteria (all must be met):**
- ✅ IRR: Krippendorff's Alpha ≥ 0.75 on all 7 skills
- ✅ Correlation: Average r ≥ 0.45 (features → ground truth)
- ✅ Sample Quality: <5% unusable transcript segments
- ✅ Coverage: ≥280 usable annotations per skill

**NO-GO Indicators:**
- ❌ IRR < 0.70 (rubrics unreliable)
- ❌ Correlation < 0.40 (models won't work)
- ❌ Any skill completely undetectable (r < 0.20)

**If NO-GO:**
- Option A: Pivot to 2-4 high-detectability skills only
- Option B: Extend Phase 0 by 4 weeks, refine approach (+$10K)
- Option C: Cancel project (sunk cost: $40K)

### Phase 1 Success Criteria (Week 38)

**Primary Metrics:**
| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| Skill inference accuracy (avg r) | ≥0.55 | ≥0.50 |
| Teacher acceptance | 70%+ helpful | 60%+ helpful |
| Evidence quality | 75%+ relevant | 65%+ relevant |
| Student game completion | 80%+ | 70%+ |
| System uptime | 95%+ | 90%+ |
| Processing speed | 6hr → <2hr | 6hr → <3hr |

**If Primary Metrics Met:**
- ✅ Proceed to Phase 2: District Rollout
- Plan for 10 schools, 500+ students
- Migrate to Whisper for cost optimization
- Add baseline cognitive assessment layer

**If Metrics Partially Met:**
- 🟡 Limited rollout (2-3 schools only)
- Focus on model improvement for 6 months
- Re-validate before broader expansion

---

## Weekly Status Reporting

### Status Report Template

**Week X Status Report**

**Completed This Week:**
- [ ] Deliverable 1
- [ ] Deliverable 2

**In Progress:**
- [ ] Task A (75% complete)
- [ ] Task B (40% complete)

**Blocked:**
- Issue description + blocker details

**Metrics:**
- Team hours: X/Y budgeted
- Spend: $X/$Y budgeted
- Key performance indicators

**Risks:**
- New risks identified
- Existing risk updates

**Next Week Plan:**
- Priority 1
- Priority 2
- Priority 3

### Key Communication Cadences

**Daily (Phase 1 only):**
- 15-min standup (async via Slack during Phase 0)
- Blockers surfaced immediately

**Weekly:**
- Friday: Status report submitted
- Monday: Week planning meeting (1 hour)

**Bi-Weekly:**
- Sprint demo (show working features)
- Retrospective (process improvements)

**Monthly:**
- Stakeholder update (executive summary)
- Budget review
- Risk assessment update

---

## Appendix: Quick Reference

### Phase 0 Key Dates
- **Week 2:** Rubrics finalized, coders trained
- **Week 6:** IRR ≥ 0.75 target achieved
- **Week 10:** All annotations complete
- **Week 14:** GO/NO-GO DECISION

### Phase 1 Key Dates
- **Week 18 (Week 4 of Phase 1):** Infrastructure deployed
- **Week 22 (Week 8):** STT pipeline working
- **Week 26 (Week 12):** Mission 1 complete, ML models deployed
- **Week 30 (Week 16):** All 3 missions complete, full integration
- **Week 34 (Week 20):** Pilot begins
- **Week 38 (Week 24):** PILOT COMPLETE, validation results

### Budget Checkpoints
- **Week 7:** 25% of Phase 0 budget consumed ($10K)
- **Week 14:** Phase 0 complete ($40K)
- **Week 22:** 25% of Phase 1 budget consumed ($111K)
- **Week 30:** 66% of Phase 1 budget consumed ($294K)
- **Week 38:** Phase 1 complete ($445K)

### Emergency Contacts
- Project Lead: [Name, email, phone]
- Technical Lead: [Name, email, phone]
- School Liaison: [Name, email, phone]
- GCP Support: support.google.com/cloud

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** End of Week 14 (Phase 0 completion)

---

*This roadmap provides week-by-week execution guidance for the MASS implementation. All dates, budgets, and deliverables are subject to adjustment based on Phase 0 decision gate results.*
