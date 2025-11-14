# Technology Research: Next Steps Options

**Last Updated:** 2025-11-13
**Purpose:** Research findings and recommendations for each immediate next step option

---

## Table of Contents

1. [Streamlit Dashboard Research](#streamlit-dashboard-research)
2. [GCP Cloud Run Research](#gcp-cloud-run-research)
3. [CI/CD Pipeline Research](#cicd-pipeline-research)
4. [Performance Optimization Research](#performance-optimization-research)
5. [Real Data Collection Research](#real-data-collection-research)
6. [Alternative Technologies Considered](#alternative-technologies-considered)

---

## Streamlit Dashboard Research

### Overview

**Streamlit** is an open-source Python framework for building data science and ML web applications.

**Official Docs:** https://docs.streamlit.io

### Why Streamlit?

✅ **Pros:**
- Pure Python (no HTML/CSS/JavaScript required)
- Fast development (build UI in hours, not days)
- Built-in components for data visualization (charts, tables, metrics)
- Native integration with Plotly, Matplotlib, Altair
- Free hosting on Streamlit Cloud
- Active community and extensive documentation
- Hot reloading during development
- Built-in session state management

❌ **Cons:**
- Limited customization compared to React/Vue
- Not ideal for highly complex UIs
- Reruns entire script on user interaction (can be slow)
- Limited offline capabilities
- Less control over page layout

### Technical Details

**Installation:**
```bash
pip install streamlit plotly pandas requests
```

**Running Locally:**
```bash
streamlit run dashboard/app_template.py
```

**Deployment Options:**
1. **Streamlit Cloud** (Recommended for MVP)
   - Free tier: Public apps, 1GB resources
   - Connect directly to GitHub repo
   - Auto-deploy on push
   - Custom subdomain: `yourapp.streamlit.app`
   - **Cost:** $0/month (free tier)

2. **GCP Cloud Run**
   - Dockerize Streamlit app
   - Deploy alongside backend API
   - More control over resources
   - **Cost:** $5-15/month

3. **Heroku**
   - Simple deployment with buildpacks
   - **Cost:** $7/month (Eco dyno)

### Performance Considerations

**Optimization Tips:**
- Use `@st.cache_data` for expensive computations
- Minimize API calls with caching
- Use `st.spinner()` for long operations
- Lazy load data (don't fetch all students upfront)
- Implement pagination for large datasets

**Typical Response Times:**
- Initial load: 1-2 seconds
- User interactions: <500ms
- API calls: Variable (depends on backend)

### Authentication Options

1. **Streamlit Built-in Auth** (Coming Soon)
   - Native authentication in Streamlit 1.29+
   - OAuth2 support

2. **Custom Auth:**
   ```python
   import streamlit as st

   def check_password():
       """Returns True if password is correct"""
       password = st.text_input("Password:", type="password")
       if password == st.secrets["password"]:
           return True
       return False

   if check_password():
       # Show main app
   ```

3. **OAuth2 (Google, Microsoft):**
   - Use `streamlit-authenticator` library
   - Integrate with Google OAuth

### Best Practices

1. **State Management:**
   - Use `st.session_state` for user data
   - Clear state on logout

2. **Error Handling:**
   - Wrap API calls in try/except
   - Display user-friendly error messages

3. **Performance:**
   - Cache API responses
   - Use loading indicators
   - Implement pagination

4. **UI/UX:**
   - Use columns for layout
   - Add tooltips with `help` parameter
   - Provide export functionality (CSV, PDF)

### Alternative Dashboard Technologies

| Framework | Pros | Cons | Best For |
|-----------|------|------|----------|
| **Streamlit** | Fast, pure Python, easy | Limited customization | Quick MVPs, data apps |
| **Dash (Plotly)** | More control, production-ready | Steeper learning curve | Complex dashboards |
| **Gradio** | Great for ML demos | Less customization | Model demos only |
| **React + D3.js** | Full control, modern | Requires JS expertise | Production apps |
| **Flask + Jinja** | Familiar, flexible | Manual UI coding | Custom needs |

**Recommendation:** Start with **Streamlit** for MVP, migrate to **React** if complex UI needed later.

---

## GCP Cloud Run Research

### Overview

**Cloud Run** is a fully managed platform for running containerized applications on Google Cloud.

**Official Docs:** https://cloud.google.com/run/docs

### Why Cloud Run?

✅ **Pros:**
- Pay-per-use (scales to zero when idle)
- Auto-scaling (0 to N instances)
- Fast deployment (<2 minutes)
- Built-in HTTPS and load balancing
- No infrastructure management
- Easy CI/CD integration
- Supports any language/framework (via Docker)
- Native Cloud SQL and Secret Manager integration

❌ **Cons:**
- Cold start latency (1-3 seconds if scaled to zero)
- Request timeout (max 60 minutes, but not ideal)
- Limited persistent storage (use Cloud Storage)
- Vendor lock-in to GCP
- Learning curve for GCP ecosystem

### Technical Details

**Resource Limits:**
- CPU: 1-8 vCPUs
- Memory: 128MB - 32GB
- Request timeout: 60 minutes max (default 300s)
- Concurrency: 1-1,000 requests per instance

**Pricing (as of Nov 2025):**
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Requests: $0.40 per million
- **Free tier:** 2 million requests/month, 360,000 GB-seconds memory, 180,000 vCPU-seconds

**Typical Monthly Cost:**
- 10,000 requests: $5-10
- 50,000 requests: $10-20
- 200,000 requests: $30-50

### Deployment Best Practices

1. **Optimize Docker Image:**
   - Use multi-stage builds
   - Minimize layer count
   - Use .dockerignore

2. **Cold Start Mitigation:**
   - Keep min instances = 1 for production (costs ~$8-15/month)
   - Optimize container startup time
   - Use smaller base images (python:3.10-slim)

3. **Security:**
   - Use Secret Manager for sensitive data
   - Enable Cloud Armor for DDoS protection
   - Use Cloud IAP for authentication

4. **Monitoring:**
   - Enable Cloud Monitoring
   - Set up log-based metrics
   - Configure alerting policies

### Cloud Run vs Alternatives

| Service | Cold Start | Scaling | Cost | Best For |
|---------|------------|---------|------|----------|
| **Cloud Run** | 1-3s | 0-N auto | Low | Variable traffic |
| **App Engine** | None | 0-N auto | Medium | Consistent traffic |
| **Cloud Functions** | 2-5s | 0-N auto | Very Low | Event-driven |
| **Kubernetes (GKE)** | None | Manual | High | Complex apps |
| **Compute Engine** | None | Manual | Medium | Full control |

**Recommendation:** **Cloud Run** is ideal for this use case (variable traffic, fast deployment, cost-effective).

### Alternative Cloud Providers

| Provider | Service | Pros | Cons |
|----------|---------|------|------|
| **AWS** | ECS Fargate, Lambda | Mature, wide adoption | More complex |
| **Azure** | Container Apps | Good .NET integration | Less mature |
| **Heroku** | Dynos | Simple deployment | Expensive |
| **Railway** | Containers | Dev-friendly | Limited scale |
| **Fly.io** | Machines | Edge deployment | Smaller community |

**Recommendation:** Stick with **GCP Cloud Run** (already using GCP for ML services).

---

## CI/CD Pipeline Research

### Overview

**GitHub Actions** provides CI/CD automation directly integrated with GitHub repositories.

**Official Docs:** https://docs.github.com/en/actions

### Why GitHub Actions?

✅ **Pros:**
- Native GitHub integration
- Free tier (2,000 minutes/month for private repos)
- YAML-based configuration
- Marketplace with 13,000+ actions
- Matrix builds (test multiple Python versions)
- Secrets management
- Easy to set up and maintain

❌ **Cons:**
- Minutes quota can run out (for heavy workloads)
- Less powerful than Jenkins for complex pipelines
- Vendor lock-in to GitHub
- Limited self-hosted runner options

### Technical Details

**Pricing:**
- **Free tier:** 2,000 minutes/month (private repos), unlimited (public repos)
- **Paid:** $0.008/minute (Linux), $0.016/minute (Windows)

**Typical Monthly Usage:**
- 50 PRs × 5 min each = 250 minutes
- 10 main pushes × 10 min each = 100 minutes
- 4 weekly model training × 20 min each = 80 minutes
- **Total:** ~430 minutes/month (within free tier)

### Pipeline Stages

**Recommended Pipeline:**

1. **On PR:** Lint + Test (~5 min)
   - Code formatting (Black, Flake8)
   - Type checking (MyPy)
   - Unit tests (Pytest)
   - Coverage report (Codecov)

2. **On Merge to Main:** Build + Deploy Staging (~10 min)
   - Build Docker image
   - Push to GCR
   - Deploy to Cloud Run (staging)
   - Run smoke tests

3. **On Manual Trigger:** Deploy Production (~5 min)
   - Require approval
   - Deploy to Cloud Run (production)
   - Run smoke tests
   - Notify team (Slack)

4. **On Schedule (Weekly):** Retrain Models (~20 min)
   - Generate synthetic data
   - Train XGBoost models
   - Evaluate performance
   - Upload to GCS

### Best Practices

1. **Caching:**
   - Cache pip dependencies
   - Cache Docker layers
   - Save 2-5 minutes per run

2. **Parallelization:**
   - Run lint and test in parallel
   - Use matrix strategy for multiple Python versions

3. **Secrets Management:**
   - Use GitHub Secrets for API keys
   - Rotate secrets regularly
   - Never log secrets

4. **Monitoring:**
   - Track build times
   - Set up failure notifications
   - Review failed builds weekly

### Alternative CI/CD Tools

| Tool | Pros | Cons | Cost |
|------|------|------|------|
| **GitHub Actions** | Native integration, easy | Limited minutes | Free tier: 2,000 min |
| **CircleCI** | Fast, powerful caching | Complex config | Free tier: 6,000 min |
| **GitLab CI** | Integrated with GitLab | Requires GitLab | Free tier: 400 min |
| **Jenkins** | Open source, highly customizable | Self-hosted, complex | Free (self-host) |
| **Travis CI** | Simple YAML config | Slow builds | Free tier: limited |

**Recommendation:** **GitHub Actions** (already using GitHub, free tier sufficient).

---

## Performance Optimization Research

### Database Optimization

**PostgreSQL Best Practices:**

1. **Indexing:**
   - Add indexes on foreign keys
   - Add composite indexes for common queries
   - Monitor index usage with `pg_stat_user_indexes`

   ```sql
   CREATE INDEX idx_linguistic_student_created
   ON linguistic_features(student_id, created_at DESC);
   ```

2. **Query Optimization:**
   - Use `EXPLAIN ANALYZE` for slow queries
   - Avoid SELECT *
   - Use JOINs instead of multiple queries
   - Implement pagination (LIMIT/OFFSET)

3. **Connection Pooling:**
   - Use pgbouncer or SQLAlchemy pooling
   - Configure pool size (20-50 connections)
   - Set connection timeout (30s)

4. **Vacuuming:**
   - Enable autovacuum (default)
   - Run manual VACUUM ANALYZE weekly
   - Monitor bloat with pg_stat_user_tables

**Expected Improvements:**
- Query time: 30ms → 5ms (6x faster)
- Throughput: 10 req/s → 50 req/s (5x faster)

### API Optimization

**FastAPI Best Practices:**

1. **Async/Await:**
   - Use async database drivers (asyncpg)
   - Parallelize independent operations
   - Use `asyncio.gather()` for concurrent tasks

2. **Caching:**
   - Redis for hot data (student assessments)
   - HTTP caching headers (Cache-Control)
   - Application-level caching (@lru_cache)

3. **Response Optimization:**
   - Use Pydantic models for serialization
   - Enable gzip compression
   - Minimize response payloads

4. **Rate Limiting:**
   - Implement per-user rate limits
   - Use Redis for distributed rate limiting
   - Graceful degradation (return cached results)

**Expected Improvements:**
- API latency: 200ms → 50ms (4x faster)
- Throughput: 20 req/s → 100 req/s (5x faster)

### Model Serving Optimization

1. **Model Loading:**
   - Load models once on startup (not per request)
   - Use model registry for versioning
   - Implement model warm-up

2. **Inference Optimization:**
   - Batch predictions when possible
   - Use NumPy for vectorization
   - Consider model quantization (int8)

3. **Caching:**
   - Cache predictions for identical features
   - Use Redis with TTL (1 hour)

**Expected Improvements:**
- Inference time: 150ms → 50ms (3x faster)
- Memory usage: 500MB → 300MB (40% reduction)

### Tools & Monitoring

**Profiling:**
- `py-spy`: Python profiler (no code changes)
- `memory_profiler`: Track memory usage
- `locust`: Load testing

**Monitoring:**
- Cloud Monitoring (GCP)
- Prometheus + Grafana (self-hosted)
- DataDog or New Relic (APM)

---

## Real Data Collection Research

### Speech-to-Text Options

| Service | Cost | Accuracy | Features | Best For |
|---------|------|----------|----------|----------|
| **Google Cloud STT** | $0.016/min | 90-95% | Speaker diarization | Production |
| **Whisper (OpenAI)** | $0.006/min | 85-90% | Open source, local | Cost-sensitive |
| **AssemblyAI** | $0.015/min | 90-95% | Real-time, entities | Startups |
| **AWS Transcribe** | $0.024/min | 88-93% | Custom vocabulary | AWS users |

**Recommendation:** **Whisper** for pilot (75% cheaper), **Google Cloud STT** for production (better accuracy).

### Audio Recording Equipment

**Budget Option ($200-300 per classroom):**
- Blue Yeti USB Microphone: $130
- Boom arm: $30
- Pop filter: $10
- USB extension cable: $15
- **Total:** ~$185 per classroom

**Professional Option ($400-600 per classroom):**
- Shure MX396 Boundary Mic: $400
- XLR cable: $30
- Audio interface (Focusrite Scarlett): $120
- **Total:** ~$550 per classroom

**Recommendation:** Start with **Blue Yeti** ($130) for pilot, upgrade to professional if needed.

### Privacy & Compliance

**Required:**
- FERPA compliance (student data protection)
- COPPA compliance (parental consent for <13)
- State-specific privacy laws

**Best Practices:**
- Obtain parental consent forms
- Anonymize transcripts (remove names, locations)
- Encrypt audio at rest
- Delete audio after 90 days
- Provide data deletion on request

**Legal Review:** Budget $1,000-2,000 for lawyer to review consent forms.

---

## Alternative Technologies Considered

### Frontend Alternatives to Streamlit

**1. Dash (Plotly)**
- **Pros:** More customizable, production-ready, Plotly integration
- **Cons:** Steeper learning curve, more verbose
- **Use Case:** Complex, multi-page dashboards
- **Verdict:** Good alternative if Streamlit too limiting

**2. Gradio**
- **Pros:** Fast ML model demos, simple API
- **Cons:** Limited to model inference UIs
- **Use Case:** Quick model demos only
- **Verdict:** Too limited for full dashboard

**3. React + FastAPI**
- **Pros:** Full control, modern, scalable
- **Cons:** Requires JavaScript expertise, slower development
- **Use Case:** Production-grade applications
- **Verdict:** Consider for v2.0 if Streamlit insufficient

**4. Flask + Bootstrap**
- **Pros:** Familiar Python, flexible
- **Cons:** Manual UI coding, slower development
- **Use Case:** Custom needs not met by frameworks
- **Verdict:** Too much work for MVP

### Backend Alternatives to Cloud Run

**1. AWS Lambda + API Gateway**
- **Pros:** Mature, serverless, low cost
- **Cons:** Cold starts, vendor lock-in, 15min timeout
- **Use Case:** Event-driven, short-running tasks
- **Verdict:** Good alternative if using AWS

**2. Heroku**
- **Pros:** Simple deployment, Git push to deploy
- **Cons:** Expensive ($7-50/month), less control
- **Use Case:** Quick prototypes, small apps
- **Verdict:** Too expensive for production

**3. DigitalOcean App Platform**
- **Pros:** Affordable, simple, managed
- **Cons:** Limited features, smaller community
- **Use Case:** Simple apps, budget-conscious
- **Verdict:** Good alternative to Cloud Run

**4. Self-hosted (Docker + Nginx)**
- **Pros:** Full control, no vendor lock-in
- **Cons:** Requires DevOps expertise, manual scaling
- **Use Case:** High-volume, cost-sensitive
- **Verdict:** Overkill for current needs

### Model Serving Alternatives

**1. TensorFlow Serving**
- **Pros:** Optimized for TensorFlow models
- **Cons:** Overkill for XGBoost, complex setup
- **Verdict:** Not needed (using XGBoost, not TensorFlow)

**2. MLflow Models**
- **Pros:** Model versioning, registry, deployment
- **Cons:** Additional infrastructure
- **Verdict:** Consider for v2.0 (model management)

**3. BentoML**
- **Pros:** Production-ready, Docker deployment
- **Cons:** Learning curve, additional abstraction
- **Verdict:** Good alternative if scaling model serving

**4. Seldon Core**
- **Pros:** Kubernetes-native, advanced features
- **Cons:** Requires Kubernetes, complex
- **Verdict:** Overkill for current needs

---

## Summary: Technology Recommendations

### Immediate Next Steps (After Model Training)

| Option | Technology | Why | Alternatives Considered |
|--------|-----------|-----|------------------------|
| **Dashboard** | Streamlit | Fast, pure Python, easy | Dash, React |
| **Deployment** | GCP Cloud Run | Serverless, auto-scale, pay-per-use | AWS Lambda, Heroku |
| **CI/CD** | GitHub Actions | Native integration, free tier | CircleCI, Jenkins |
| **Performance** | PostgreSQL indexing, Redis caching | High ROI, low effort | N/A |
| **Real Data** | Whisper (STT), Blue Yeti (mic) | Cost-effective, good quality | Google Cloud STT |

### Technology Stack Summary

**Frontend:**
- Streamlit (MVP) → React (Production)

**Backend:**
- FastAPI + PostgreSQL + Redis
- Deployed on GCP Cloud Run

**ML:**
- XGBoost models
- GPT-4o-mini for reasoning
- Stored in GCS

**CI/CD:**
- GitHub Actions
- Automated testing, building, deployment

**Monitoring:**
- Cloud Monitoring + Cloud Logging
- Optional: DataDog/New Relic

**Data Collection:**
- Whisper for transcription
- Blue Yeti microphones

---

## Key Takeaways

1. **Start simple:** Streamlit + Cloud Run is fastest path to MVP
2. **Optimize iteratively:** Don't over-engineer upfront
3. **Leverage managed services:** Cloud Run, Cloud SQL, Redis (saves DevOps time)
4. **Use free tiers:** GitHub Actions, Cloud Run free tier
5. **Plan for scale:** Architecture supports 100x growth without major changes

---

**Last Updated:** 2025-11-13
**Version:** 1.0
**Next Review:** After technology choices finalized
