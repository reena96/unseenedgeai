# MASS Implementation Tasks
## Comprehensive Task Breakdown (Complexity < 7)

**Generated from:** MASS Implementation PRD v3.0, Technical Architecture v1.0, Implementation Roadmap
**Target:** 38-week implementation (Phase 0: 14 weeks, Phase 1: 24 weeks)
**Constraint:** All task complexity scores must be < 7

---

## Phase 0: Ground Truth Collection (Weeks 1-14)

### Task 1: Rubric Development and Coder Training
**Duration:** Weeks 1-2
**Priority:** High
**Complexity:** 5

**Deliverables:**
- 7 validated skill rubrics (empathy, adaptability, problem-solving, self-regulation, resilience, communication, collaboration)
- 4 expert coders recruited, hired, and trained
- Annotation platform setup (Label Studio or equivalent)
- 50 practice transcripts annotated
- Initial IRR baseline calculated

**Subtasks:**
1. Review academic literature on each of the 7 non-academic skills
2. Draft rubric frameworks with 1-4 scale and behavioral anchors
3. Review rubrics with educational psychologist consultant
4. Finalize rubrics with annotation guidelines and examples
5. Post coder recruitment on teacher job boards
6. Conduct interviews and hire 4 expert coders
7. Set up annotation platform (Label Studio on Cloud Run)
8. Conduct 2-hour training session with all coders
9. Complete practice annotation of 50 transcripts
10. Calculate baseline IRR (expect ~0.50-0.60)

**Test Strategy:** Baseline IRR ≥ 0.50, rubrics reviewed by external consultant, platform functional

---

### Task 2: First Annotation Sprint and IRR Achievement
**Duration:** Weeks 3-6
**Priority:** High
**Complexity:** 6

**Deliverables:**
- 900 transcript segments dual-coded (300 segments in weeks 3-4, 600 segments in weeks 5-6)
- IRR ≥ 0.75 achieved (Krippendorff's Alpha)
- Rubric adjustments documented
- Feature extraction pipeline built and tested

**Subtasks:**
1. Dual-code 300 transcript segments (weeks 3-4)
2. Calculate IRR after first 300 segments (target: α ≥0.65)
3. Hold weekly sync meetings to discuss disagreements and edge cases
4. Refine rubrics based on disagreement patterns
5. Dual-code additional 600 segments (weeks 5-6)
6. Calculate IRR after 900 segments (target: α ≥0.75)
7. Build feature extraction pipeline (spaCy, VADER, LIWC)
8. Extract linguistic features from annotated segments
9. Run preliminary correlation analysis (features → ground truth)
10. Document rubric adjustments and IRR progress

**Test Strategy:** IRR α ≥ 0.75 on all 7 skills, preliminary correlation r ≥ 0.30, <5% unusable segments

---

### Task 3: Full Annotation and Baseline Model Training
**Duration:** Weeks 7-10
**Priority:** High
**Complexity:** 6

**Deliverables:**
- 2,100 total segments annotated (300 per skill)
- IRR maintained at α ≥0.75
- Advanced feature engineering complete
- Baseline ML models trained (Logistic Regression + XGBoost for each skill)
- Correlation r ≥ 0.40 on held-out test set

**Subtasks:**
1. Continue dual-coding at steady pace (weeks 7-8: 600 segments)
2. Complete final 600 segments (weeks 9-10)
3. Maintain IRR through regular calibration meetings
4. Advanced feature engineering: N-gram patterns, contextual embeddings (sentence-transformers)
5. Create behavioral proxies from linguistic patterns
6. Split data: 70% training, 30% test
7. Train Logistic Regression baseline models (one per skill)
8. Train XGBoost models (one per skill)
9. Validate on held-out test set (target: r ≥ 0.40)
10. Document feature importance for each skill

**Test Strategy:** All 2,100 segments coded, IRR α ≥0.75 maintained, model correlation r ≥ 0.40, ≥280 usable annotations per skill

---

### Task 4: Game Telemetry Design and Synthetic Data Validation
**Duration:** Weeks 11-12
**Priority:** High
**Complexity:** 5

**Deliverables:**
- Game telemetry specification document (event types, data schema)
- Synthetic game data generator (300 fake players)
- Behavioral feature extraction from game data
- Multi-modal fusion model designed and tested
- Optimal fusion weights determined

**Subtasks:**
1. Design telemetry events for 3 game missions (empathy, collaboration/problem-solving, adaptability/resilience)
2. Map game choices → skill indicators
3. Create event schema (JSON format)
4. Build synthetic game data generator (Python script)
5. Generate 300 synthetic player profiles with varied skill levels
6. Extract behavioral features from synthetic game data (task completion, retry patterns, delegation, persistence)
7. Design multi-source fusion algorithm (transcript + game + teacher)
8. Test different weighting schemes (skill-specific weights)
9. Validate fusion model on synthetic data
10. Document optimal fusion approach and weights

**Test Strategy:** Synthetic data generator produces valid events, behavioral features extracted correctly, fusion model combines sources appropriately

---

### Task 5: Phase 0 Analysis and GO/NO-GO Decision
**Duration:** Weeks 13-14
**Priority:** Critical
**Complexity:** 5

**Deliverables:**
- Phase 0 Final Report (IRR, predictive validity, fusion model, recommendation)
- External statistical validation
- GO or NO-GO recommendation
- Phase 1 detailed plan (if GO)

**Subtasks:**
1. Calculate Krippendorff's Alpha for each skill (target: α ≥0.75)
2. Create confusion matrices for edge cases
3. Calculate correlation: features → ground truth (target: avg r ≥ 0.45)
4. Compute model performance metrics (MAE, RMSE)
5. Rank feature importance for each skill
6. Document optimal fusion weights (transcript vs game vs teacher)
7. Design confidence scoring approach
8. Design evidence extraction strategy
9. Engage external statistician for validation review
10. Write Phase 0 Final Report with GO/NO-GO recommendation
11. If GO: Create detailed Phase 1 plan

**Test Strategy:** All GO criteria met (IRR ≥0.75, correlation ≥0.45, <5% unusable, ≥280 per skill), external validation confirms findings

**Decision Gate:** PROCEED TO PHASE 1 IF ALL GO CRITERIA MET

---

## Phase 1: System Development (Weeks 15-38, 24 weeks)

### Task 6: Infrastructure Foundation and Team Onboarding
**Duration:** Weeks 15-16 (Phase 1 Weeks 1-2)
**Priority:** Critical
**Complexity:** 6

**Deliverables:**
- GCP infrastructure deployed (Cloud Run, Cloud SQL, Cloud Storage, Cloud Tasks, Pub/Sub)
- Database schema implemented (PostgreSQL + TimescaleDB)
- CI/CD pipeline configured (GitHub Actions)
- Unity game project initialized (2022.3 LTS)
- FastAPI server foundation deployed
- Team knowledge transfer complete

**Subtasks:**
1. Set up GCP project and enable required APIs (Cloud Run, Cloud SQL, Cloud Storage, Cloud Speech-to-Text, Secret Manager)
2. Deploy Cloud SQL instance with PostgreSQL 15 + TimescaleDB extension
3. Create Cloud Storage buckets for audio files and ML models
4. Set up Cloud Tasks queues for transcription and inference jobs
5. Create Cloud Pub/Sub topics for event streaming
6. Implement database schema (all tables from Technical Architecture)
7. Create SQLAlchemy models for all entities
8. Initialize Unity 2022.3 LTS project with proper architecture
9. Set up FastAPI project structure with basic endpoints
10. Configure GitHub Actions CI/CD pipeline (build, test, deploy)
11. Deploy FastAPI server to Cloud Run (auto-scaling 0-10 instances)
12. Conduct team knowledge transfer sessions (backend, game, ML engineers)

**Test Strategy:** GCP services operational, database migrations run successfully, CI/CD deploys to Cloud Run, Unity project builds

---

### Task 7: Authentication, Audio Pipeline, and Mission 1 Development
**Duration:** Weeks 17-20 (Phase 1 Weeks 3-6)
**Priority:** High
**Complexity:** 6

**Deliverables:**
- Authentication API complete (OAuth 2.0 + JWT, RBAC)
- Audio upload API complete (GCS integration)
- Google Cloud STT integrated (>75% accuracy target)
- Transcription pipeline working end-to-end
- Mission 1 fully playable (10-12 min, empathy assessment)
- Telemetry events firing correctly

**Subtasks:**
1. Implement OAuth 2.0 + JWT authentication endpoints (login, refresh, logout)
2. Create role-based access control (teacher, admin, student, counselor roles)
3. Implement audit logging for all data access
4. Build audio upload API with Cloud Storage integration
5. Integrate Google Cloud Speech-to-Text API (config for classroom audio)
6. Implement async transcription worker (Cloud Tasks)
7. Build speaker diarization mapping logic
8. Test STT pipeline with sample classroom audio
9. Design Mission 1: "Understanding Perspectives" (Academy courtyard, Alex character)
10. Purchase and integrate Unity Asset Store environment ($600)
11. Create Alex 2D sprite with emotional states
12. Create Mentor Maya 3D model (low-poly, stylized)
13. Implement dialogue system with 5 choice points
14. Integrate telemetry logging (choice selection, time on dialogue, re-reading, help-seeking)
15. Polish Mission 1 with lighting, sound effects, UI
16. Test Mission 1 end-to-end (10-12 min playtime)

**Test Strategy:** Authentication works with all roles, audio uploads and transcribes correctly (>75% accuracy), Mission 1 playable and telemetry logs events

---

### Task 8: ML Inference, Evidence Fusion, and Mission 2 Development
**Duration:** Weeks 21-24 (Phase 1 Weeks 7-10)
**Priority:** High
**Complexity:** 6

**Deliverables:**
- All 7 XGBoost skill models deployed to production
- Inference API working (GET /api/v1/skills/{student_id})
- Evidence fusion service deployed (skill-specific weights)
- Evidence extraction system functional
- Mission 2 fully playable (12-15 min, collaboration + problem-solving)
- Class overview dashboard page functional

**Subtasks:**
1. Package all 7 XGBoost models for production (joblib format)
2. Build ML inference service (services/ml_inference.py)
3. Implement batch inference for full classroom (30+ students)
4. Create inference worker (Cloud Tasks async processing)
5. Build skill assessment API endpoints (GET /api/v1/skills/{student_id}, /history, /{skill})
6. Implement evidence fusion service with skill-specific weights (empathy: 0.35/0.40/0.25, etc.)
7. Calculate confidence scores based on source agreement
8. Build evidence extraction system (top 3-5 snippets per skill)
9. Implement evidence API endpoints (GET /api/v1/evidence/{assessment_id})
10. Design Mission 2: "The Group Project Challenge" (classroom, Jordan + Sam characters)
11. Purchase and integrate classroom environment ($800)
12. Create Jordan and Sam 2D sprites
13. Implement 7 choice points with resource allocation mini-game
14. Integrate telemetry (delegation patterns, conflict resolution, planning approach)
15. Polish Mission 2 and test end-to-end (12-15 min)
16. Build class overview dashboard page (React) with skill distribution heatmap

**Test Strategy:** All 7 models deployed and returning scores, evidence fusion combines sources correctly, Mission 2 playable with telemetry, dashboard loads <2s

---

### Task 9: GPT-4 Reasoning, Mission 3, and Full Game Integration
**Duration:** Weeks 25-28 (Phase 1 Weeks 11-14)
**Priority:** High
**Complexity:** 6

**Deliverables:**
- GPT-4 reasoning generation working (2-3 sentence growth-oriented explanations)
- All assessments have reasoning
- Mission 3 complete (10-15 min, adaptability + resilience)
- Full game playable (30-45 min, all 3 missions integrated)
- Game telemetry fully connected to backend
- Comprehensive testing suite (unit, integration, end-to-end)
- Student detail dashboard page with evidence viewer

**Subtasks:**
1. Integrate OpenAI GPT-4 API
2. Build reasoning generation service (services/reasoning_service.py)
3. Create prompts for each skill (2-3 sentence, growth-oriented)
4. Implement reasoning caching (avoid re-generating)
5. Create reasoning API endpoint (GET /api/v1/reasoning/{assessment_id})
6. Test reasoning quality with manual review
7. Implement cost monitoring for OpenAI usage
8. Design Mission 3: "The Unexpected Change" (classroom continuation, setback scenarios)
9. Implement 6 choice points (adaptability focus)
10. Create failure/retry mechanics
11. Integrate telemetry (strategy switching, persistence, emotional regulation timing)
12. Integrate all 3 missions with opening tutorial and ending summary
13. Implement progress save/load system
14. Add accessibility features (text size, colorblind mode, keyboard navigation)
15. Test full game playthrough (30-45 min)
16. Build comprehensive test suite (Pytest for backend, Jest for React, Unity Test Framework)
17. Achieve >80% test coverage
18. Build student detail dashboard page with evidence excerpts and trend chart

**Test Strategy:** GPT-4 generates clear reasoning, Mission 3 playable, full game completable in 30-45 min, test coverage >80%, dashboard loads <2s

---

### Task 10: Dashboard Completion, Security Audit, and Pilot Preparation
**Duration:** Weeks 29-32 (Phase 1 Weeks 15-18)
**Priority:** High
**Complexity:** 6

**Deliverables:**
- All dashboard features complete (teacher, admin, student views)
- Security audit complete (FERPA/COPPA compliance validated)
- Penetration testing passed
- 2-3 pilot schools confirmed and onboarded
- Teacher training materials created
- Recording equipment procured and shipped

**Subtasks:**
1. Build administrator dashboard (school-wide skill distributions, trends, equity analysis, heatmaps)
2. Build student portal (skill visualization, growth-oriented feedback, achievement tracking)
3. Implement all dashboard features (sorting, filtering, export to PDF/CSV)
4. Ensure mobile-responsive design
5. Conduct security audit (input validation, SQL injection prevention, XSS prevention, CSRF tokens)
6. Run penetration testing with OWASP ZAP
7. Validate FERPA compliance (data access controls, audit logs, retention policy)
8. Validate COPPA compliance (parental consent flow, data minimization, deletion rights)
9. Implement Content Security Policy (CSP)
10. Test disaster recovery procedures (backup, restore, RTO/RPO)
11. Reach out to 3-5 potential pilot schools
12. Negotiate pilot agreements (2-3 schools confirmed)
13. Create teacher training materials (video tutorials, user guides, FAQ)
14. Purchase recording equipment (3 classroom microphones, audio interface, cables)
15. Ship equipment to pilot schools
16. Schedule teacher training sessions

**Test Strategy:** All dashboards functional and load <2s, security audit passed with no critical vulnerabilities, pilot schools confirmed and equipment received

---

### Task 11: Pilot Execution and Data Collection
**Duration:** Weeks 33-37 (Phase 1 Weeks 19-23)
**Priority:** Critical
**Complexity:** 6

**Deliverables:**
- Teachers trained on MASS system
- Students complete baseline game sessions (target: 80%+ completion)
- 4 weeks of classroom audio collected and processed
- Teacher rubric assessments: 100% complete for pilot students
- First skill assessments generated and shared with teachers
- Technical support provided continuously
- Pilot feedback collected (surveys + interviews)

**Subtasks:**
1. Conduct teacher training sessions (virtual + in-person, 2 hours each)
2. Cover: system overview, audio upload, reading skill assessments, rubric scoring, privacy/consent
3. Conduct student orientation sessions
4. Have students play Flourish Academy game (30-45 min each)
5. Collect baseline game telemetry
6. Troubleshoot any technical issues immediately
7. Begin classroom audio recording (2-hour sessions per day)
8. Upload audio files via dashboard daily
9. Monitor transcription quality and diarization
10. Process audio through STT pipeline
11. Extract linguistic features from transcripts
12. Run skill inference models
13. Generate first skill assessments (all 7 skills per student)
14. Share assessments with teachers for feedback
15. Teachers complete rubric assessments for all pilot students (1-4 scale per skill)
16. Provide on-call technical support (24-hour response time)
17. Collect daily quick feedback surveys from teachers
18. Conduct weekly check-in interviews with teachers
19. Monitor game completion rates (target: 80%+)
20. Monitor system performance (uptime, processing speed, errors)

**Test Strategy:** 80%+ students complete game, 100% teacher rubrics completed, system uptime >95%, audio processing <2hr for 6hr audio

---

### Task 12: Final Validation and Phase 1 Completion
**Duration:** Week 38 (Phase 1 Week 24)
**Priority:** Critical
**Complexity:** 5

**Deliverables:**
- Final Validation Report (correlation analysis, system performance, engagement analysis, teacher satisfaction)
- Success metrics calculated and documented
- Recommendations for Phase 2
- Launch decision (GO/NO-GO for broader rollout)

**Subtasks:**
1. Correlation analysis: MASS skill scores vs teacher rubric scores (per skill)
2. Calculate Pearson correlation coefficient r (target: r ≥ 0.50, optimal: r ≥ 0.55)
3. Statistical significance testing (p-values)
4. System performance validation: uptime (target: 95%+), processing speed (6hr audio in <2hr), STT accuracy (>75%)
5. Dashboard load time validation (<2s)
6. Student engagement analysis: game completion rate (target: 80%+), average playtime, mission completion breakdown
7. Student enjoyment survey (target: 75%+ rate game as fun)
8. Teacher satisfaction survey (target: 70%+ rate assessments helpful)
9. Evidence quality interviews (target: 75%+ find evidence relevant)
10. Analyze qualitative feedback from teachers and students
11. Identify successes and areas for improvement
12. Calculate cost analysis (actual vs budget)
13. Write Final Validation Report with executive summary
14. Develop recommendations for Phase 2 (Whisper migration, full 5-mission game, parent portal)
15. Present findings to stakeholders
16. Make launch decision (GO for broader rollout if success metrics met)

**Test Strategy:** All success metrics met or exceeded, stakeholder approval obtained, Phase 2 plan documented

---

## Summary Statistics

**Total Main Tasks:** 12
- Phase 0: 5 tasks (Weeks 1-14)
- Phase 1: 7 tasks (Weeks 15-38)

**Complexity Distribution:**
- Complexity 5: 4 tasks
- Complexity 6: 8 tasks
- All tasks < 7 (constraint met)

**Estimated Timeline:** 38 weeks (9 months)
**Total Budget:** $485,000
- Phase 0: $40,000
- Phase 1: $445,000

**Team Size:**
- Phase 0: 1 Data Scientist + 4 Expert Coders + Consultants
- Phase 1: 4-6 engineers (backend, game, ML, frontend, DevOps, product)

**Success Criteria (Phase 1):**
- Skill Inference Accuracy: r ≥ 0.50 (optimal: r ≥ 0.55)
- Teacher Acceptance: 70%+ helpful
- Evidence Quality: 75%+ relevant
- Student Engagement: 80%+ complete game
- Student Enjoyment: 75%+ fun
- System Uptime: 95%+
- Processing Speed: 6hr audio in <2hr
- STT Accuracy: >75%

---

## Notes for Implementation

1. **Phase 0 is a Decision Gate:** Do not proceed to Phase 1 unless all GO criteria are met (IRR ≥0.75, correlation ≥0.45, <5% unusable, ≥280 per skill)

2. **Parallel Development:** Game development can proceed in parallel with backend/ML development after Week 16

3. **Complexity Management:** All tasks are designed with complexity <7 by breaking down large features into focused, time-boxed deliverables

4. **Risk Mitigation:** 3-mission MVP (not 5) reduces game development risk; Unity Asset Store usage reduces art/environment risk

5. **API Keys Required:** Ensure ANTHROPIC_API_KEY (or equivalent) is available in MCP environment for Task Master operations

6. **Task Master Integration:** Use `mcp__task-master__parse_prd` with this document to generate tasks.json if API keys are configured

---

This task breakdown provides a clear, implementable roadmap with controlled complexity for the MASS system development.
