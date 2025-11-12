# MASS Project Context

## Purpose

**MASS (Middle School Non-Academic Skills Measurement System)** provides continuous, objective assessment of non-academic (socio-emotional) skills in middle school students through AI-driven analysis of multiple evidence sources.

### Core Goals
- Provide scalable, objective measurement of 7 non-academic skills
- Enable educators to track student skill development over time
- Deliver actionable, evidence-based insights with transparent reasoning
- Support early intervention through continuous monitoring

### Target Skills
1. **Empathy** - Understanding and sharing others' feelings
2. **Adaptability** - Adjusting to change and new circumstances
3. **Problem-Solving** - Analyzing challenges and finding solutions
4. **Self-Regulation** - Managing emotions and behaviors
5. **Resilience** - Recovering from setbacks and persisting
6. **Communication** - Expressing ideas clearly and effectively
7. **Collaboration** - Working effectively with others

## Tech Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI 0.109+
- **Database:** PostgreSQL 15 + TimescaleDB extension
- **Cache:** Redis 7.x
- **Task Queue:** Google Cloud Tasks + Cloud Pub/Sub

### AI/ML Stack
- **Speech-to-Text:** Google Cloud STT (Phase 1) → Whisper (Phase 2)
- **NLP Framework:** spaCy 3.7+ (en_core_web_sm)
- **Sentiment Analysis:** VADER 3.3+
- **Text Analysis:** LIWC-22
- **ML Framework:** Scikit-learn 1.4+, XGBoost 2.0+
- **LLM Reasoning:** OpenAI GPT-4
- **Embeddings:** sentence-transformers

### Game (Assessment Component)
- **Engine:** Unity 2022.3 LTS
- **Language:** C# 11+
- **Build Targets:** Windows, Mac, Linux

### Frontend
- **Framework:** React 18.x
- **Language:** TypeScript 5.x
- **UI Library:** Material-UI or Chakra UI
- **State Management:** React Context + hooks
- **API Client:** Axios

### Cloud Infrastructure
- **Platform:** Google Cloud Platform (GCP)
- **Compute:** Cloud Run (serverless containers)
- **Storage:** Cloud Storage (audio files, ML models)
- **Database:** Cloud SQL (managed PostgreSQL)
- **Monitoring:** Cloud Logging + Cloud Monitoring
- **Secrets:** Secret Manager
- **CI/CD:** GitHub Actions

### Development Tools
- **Version Control:** Git + GitHub
- **Testing:** Pytest (backend), Jest + React Testing Library (frontend), Unity Test Framework (game)
- **API Docs:** Swagger/OpenAPI 3.0
- **Error Tracking:** Sentry
- **Infrastructure-as-Code:** Terraform

## Project Conventions

### Code Style

**Python (Backend):**
- PEP 8 style guide
- Black formatter (line length: 100)
- isort for import sorting
- Type hints required for all functions
- Docstrings: Google style

**TypeScript (Frontend):**
- ESLint + Prettier
- Functional components with hooks (no class components)
- Named exports preferred over default exports
- Strict TypeScript mode enabled

**C# (Game):**
- Unity C# conventions
- PascalCase for public members
- camelCase for private members
- XMLDoc comments for public APIs

### Naming Conventions

**Database:**
- Tables: snake_case, plural (e.g., `skill_assessments`)
- Columns: snake_case (e.g., `student_id`)
- Primary keys: `id` (UUID)
- Foreign keys: `[table]_id` (e.g., `student_id`)
- Timestamps: `created_at`, `updated_at`

**API Endpoints:**
- RESTful: `/api/v1/[resource]/[id]`
- Plural nouns for collections (e.g., `/api/v1/skills`)
- Verb usage only for non-CRUD actions (e.g., `/api/v1/audio/transcribe`)

**Python:**
- Modules/packages: snake_case
- Classes: PascalCase
- Functions/variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private: prefix with `_`

**TypeScript:**
- Components: PascalCase (e.g., `StudentProfile.tsx`)
- Hooks: camelCase with `use` prefix (e.g., `useStudentSkills`)
- Types/Interfaces: PascalCase (e.g., `StudentSkill`)
- Functions/variables: camelCase

### Architecture Patterns

**Backend:**
- **Layered Architecture:**
  - API Layer (FastAPI routers)
  - Service Layer (business logic)
  - Data Layer (SQLAlchemy models, database operations)
- **Async Processing:** Use Cloud Tasks for long-running operations (STT, ML inference)
- **Event-Driven:** Pub/Sub for event streaming (audio uploaded → transcription → features → inference)
- **Dependency Injection:** FastAPI's `Depends` for shared resources

**Frontend:**
- **Component Structure:**
  - Page components (routes)
  - Container components (data fetching)
  - Presentation components (pure UI)
- **State Management:** React Context for global state, local state for component-specific
- **Data Fetching:** React Query for server state, loading states, caching

**ML Pipeline:**
- **Feature Store Pattern:** Separate feature extraction from model inference
- **Model Versioning:** Track model versions in database (enables A/B testing)
- **Evidence Fusion:** Multi-source weighted averaging with confidence scoring

**Database:**
- **Time-Series Optimization:** Use TimescaleDB hypertables for high-frequency data (game telemetry, skill assessments)
- **Soft Deletes:** Preserve audit trail (add `deleted_at` column)
- **JSONB for Flexibility:** Use JSONB for nested/variable data (telemetry events, feature vectors)

### Testing Strategy

**Unit Tests:**
- Backend: 80%+ coverage for services and models
- Frontend: Test components with user interactions
- Game: Test core mechanics and telemetry logic

**Integration Tests:**
- API endpoints with database interactions
- End-to-end pipeline: audio → transcript → features → inference
- Multi-source evidence fusion

**Validation Tests:**
- ML model accuracy (correlation with teacher ratings)
- STT accuracy (sample validation)
- Evidence quality (manual review)

**Performance Tests:**
- Load testing: 100 concurrent users
- Processing speed: 6hr audio in <2hr
- API latency: p95 <500ms

### Git Workflow

**Branching:**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/[name]` - Feature development
- `fix/[name]` - Bug fixes
- `release/[version]` - Release preparation

**Commits:**
- Conventional Commits format: `type(scope): message`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Examples:
  - `feat(api): add skill assessment endpoint`
  - `fix(stt): handle missing diarization data`
  - `docs(readme): update installation instructions`

**Pull Requests:**
- Require code review (1+ approver)
- All tests must pass
- OpenSpec validation must pass (for spec changes)
- Squash and merge to main

## Domain Context

### Educational Assessment
- **Formative Assessment:** Continuous feedback during learning (MASS approach)
- **Summative Assessment:** Evaluation at end of learning period (traditional)
- **Inter-Rater Reliability (IRR):** Agreement between human coders (target: α ≥ 0.75)
- **Validity:** Correlation between MASS scores and teacher ratings (target: r ≥ 0.50)

### Non-Academic Skills (SEL - Social-Emotional Learning)
- Critical for real-world success but difficult to measure objectively
- Traditional assessment relies on subjective teacher observations
- MASS uses multi-source evidence (transcripts + game + teacher rubrics)

### Evidence Fusion Model
- Different skills have different "detectability" from different sources
- Example weights:
  - **Communication:** transcript 50%, game 25%, teacher 25% (highly detectable in speech)
  - **Adaptability:** transcript 20%, game 50%, teacher 30% (best observed in game scenarios)
- Confidence based on agreement between sources (low std = high confidence)

### Skill Scoring
- **Scale:** 0-1 continuous (normalized)
- **Interpretation:**
  - 0.00-0.49: Emerging
  - 0.50-0.74: Developing
  - 0.75-1.00: Proficient
- **Confidence:** 0-1 (based on source agreement and data quality)

### Classroom Context
- **Middle School:** Grades 6-8 (ages 11-14)
- **Class Size:** 20-35 students
- **Recording:** Full-day classroom audio (6+ hours)
- **Privacy:** FERPA and COPPA compliant (parental consent required)

### Game Assessment ("Flourish Academy")
- **Stealth Assessment:** Students unaware they're being assessed
- **Narrative Adventure:** 30-45 minute gameplay (3 missions)
- **Telemetry:** Tracks choices, timing, persistence, strategy switching
- **Skills Measured:** All 7 skills (primary focus on 5 with low transcript detectability)

## Important Constraints

### Regulatory Compliance
- **FERPA (Family Educational Rights and Privacy Act):**
  - Student data access restricted to authorized educators
  - Audit logging of all data access
  - Data retention limits (delete after graduation + 1 year)
  - Parental rights to review and delete data

- **COPPA (Children's Online Privacy Protection Act):**
  - Parental consent required for students under 13
  - Data minimization (collect only what's necessary)
  - No advertising or marketing to students
  - Right to delete student data

### Performance Requirements
- **STT Processing:** <5 seconds per minute of audio
- **ML Inference:** <30 seconds per student (all 7 skills)
- **API Latency:** p95 <500ms
- **Dashboard Load:** <2 seconds
- **System Uptime:** 95%+ (Phase 1), 99.5%+ (production)

### Cost Constraints
- **Phase 1 Budget:** $485,000 total
- **STT Cost:** ~$34.55/student/month (Google STT Phase 1)
  - *Migrate to Whisper in Phase 2 for cost optimization (~$2/student/month)*
- **GPT-4 Cost:** ~$0.03-0.05 per reasoning generation (~$28/month for 100 students)
- **GCP Infrastructure:** ~$1,500/month for Phase 1 pilot

### Data Quality Requirements
- **STT Accuracy:** >75% (classroom environment is challenging)
- **Speaker Diarization:** Required for attributing speech to students
- **IRR (Ground Truth):** Krippendorff's Alpha ≥ 0.75
- **Model Validity:** Correlation r ≥ 0.50 vs teacher ratings

### Privacy & Security
- **Data Encryption:**
  - At rest: AES-256 (automatic in Cloud SQL)
  - In transit: TLS 1.3 (all API communication)
- **Authentication:** OAuth 2.0 + JWT
- **Authorization:** Role-based access control (teacher, admin, student)
- **Audit Logging:** All data access logged with timestamps, user, action

### Scalability Targets
- **Phase 1:** 2-3 schools, ~100 students
- **Phase 2:** 10 schools, ~500 students
- **Phase 3:** District-wide, 5,000+ students

## External Dependencies

### Google Cloud Platform (GCP)
- **Cloud Speech-to-Text API:** Transcription service
  - Rate limit: 60 requests/minute (long-running)
  - Model: `latest_long` (optimized for classroom audio)
  - Diarization: Up to 10 speakers
- **Cloud Storage:** Audio file storage (30-day lifecycle)
- **Cloud SQL:** Managed PostgreSQL database
- **Cloud Run:** Serverless container hosting
- **Cloud Tasks:** Async job queue
- **Cloud Pub/Sub:** Event streaming

### OpenAI API
- **GPT-4:** Reasoning generation for skill assessments
  - Model: `gpt-4` (not GPT-4 Turbo initially for quality)
  - Rate limit: 10,000 requests/day (Tier 1)
  - Cost: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
  - Max tokens: 150 per reasoning (2-3 sentences)

### Unity Asset Store
- **Environment Assets:** Classroom, courtyard ($1,400 total)
- **Audio:** Background music, sound effects ($800)
- **Plugins:** May use TextMeshPro, Cinemachine (built-in Unity packages)

### NLP Libraries
- **spaCy:** Linguistic analysis (POS tagging, dependency parsing)
  - Model: `en_core_web_sm` (35MB, fast)
- **VADER:** Sentiment analysis (included in vaderSentiment package)
- **LIWC-22:** Psychological language categories (requires license: ~$100)

### ML Libraries
- **Scikit-learn:** Model training, preprocessing, evaluation
- **XGBoost:** Gradient boosting for skill inference models
- **sentence-transformers:** Contextual embeddings (model: `all-MiniLM-L6-v2`)

### School Information Systems (SIS)
- **Integration:** CSV import initially, API integration in Phase 2
- **Data:** Student roster, demographics, class assignments
- **Common SIS:** PowerSchool, Infinite Campus, Skyward

## Decision Logs

### Decision: Google STT → Whisper Migration Path
- **Phase 1:** Google Cloud STT for speed (2-3 days vs 2 weeks implementation)
- **Phase 2:** Migrate to Whisper for cost optimization ($34.55 → $2/student/month)
- **Rationale:** Focus Phase 1 on core ML/game, defer infrastructure complexity

### Decision: GPT-4 for Reasoning (vs Templates)
- **Choice:** GPT-4 LLM-based reasoning
- **Rationale:** 7 skills × 3 levels = 21 templates (significant effort), GPT-4 provides nuanced explanations, cost modest ($28/month for 100 students)
- **Migration Path:** Can switch to templates in Phase 2 if cost becomes issue

### Decision: Unity Game (vs Web-based)
- **Choice:** Unity 2022 LTS (desktop builds)
- **Rationale:** Professional quality, 95% reusable to full game, better performance for complex interactions
- **Trade-off:** Distribution complexity (vs web link), but richer telemetry and engagement

### Decision: XGBoost Models (vs Deep Learning)
- **Choice:** XGBoost for skill inference
- **Rationale:** Interpretable (feature importance), efficient (low latency), works well with small-medium datasets (300 samples/skill)
- **Alternative Considered:** Neural networks rejected due to interpretability requirements and data size

### Decision: Multi-Tenant Database Architecture
- **Choice:** Single database with `school_id` foreign keys
- **Rationale:** Simpler ops (vs separate DB per school), sufficient isolation with RLS (Row Level Security)
- **Scale Limit:** Revisit at 50+ schools

## Phase 0 Decision Gate (Week 14)

**GO Criteria:**
- ✅ IRR: Krippendorff's Alpha ≥ 0.75 on all 7 skills
- ✅ Correlation: Average r ≥ 0.45 (features → ground truth)
- ✅ Sample Quality: <5% unusable transcript segments
- ✅ Coverage: ≥280 usable annotations per skill

**NO-GO → Pivot Options:**
- Reduce to 2-4 high-detectability skills only
- Extend Phase 0 by 4 weeks for additional data collection
- Cancel project (sunk cost: $40K)

## Reference Documents

- **PRD:** `docs/MASS_Implementation_PRD_v3.md`
- **Technical Architecture:** `docs/MASS_Technical_Architecture_v1.md`
- **Implementation Roadmap:** `docs/MASS_Implementation_Roadmap.md`
- **Original Project Brief:** `docs/Project Brief.md`

## Glossary

- **STT:** Speech-to-Text
- **IRR:** Inter-Rater Reliability (Krippendorff's Alpha)
- **SEL:** Social-Emotional Learning
- **FERPA:** Family Educational Rights and Privacy Act
- **COPPA:** Children's Online Privacy Protection Act
- **LIWC:** Linguistic Inquiry and Word Count
- **VADER:** Valence Aware Dictionary and sEntiment Reasoner
- **MAE:** Mean Absolute Error
- **RMSE:** Root Mean Squared Error
- **Diarization:** Speaker identification in audio
- **Fusion:** Combining scores from multiple evidence sources
- **Hypertable:** TimescaleDB's time-series optimized table structure
