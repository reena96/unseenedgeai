# Railway Deployment Guide

This guide walks through deploying the UnseenEdge AI platform on Railway.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Railway Project                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  PostgreSQL  │  │    Redis     │                         │
│  │   Database   │  │    Cache     │                         │
│  └──────┬───────┘  └──────┬───────┘                         │
│         │                 │                                  │
│         └────────┬────────┘                                  │
│                  │                                           │
│         ┌───────▼────────┐                                  │
│         │  Backend API   │ ◄── FastAPI (port 8080)          │
│         │   /backend     │                                  │
│         └───────┬────────┘                                  │
│                 │                                            │
│    ┌────────────┼────────────┐                              │
│    │            │            │                              │
│ ┌──▼───┐   ┌───▼───┐   ┌───▼────┐                          │
│ │Teacher│   │ Admin │   │Student │  ◄── Streamlit apps     │
│ │ Dash  │   │ Dash  │   │ Portal │                          │
│ └───────┘   └───────┘   └────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway
- API keys ready:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY` (optional)
  - `PERPLEXITY_API_KEY` (optional)

---

## Step 1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select the `unseenedgeai` repository
6. **Important:** Click "Add Service" instead of deploying immediately

---

## Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Wait for it to provision (~30 seconds)
4. Click on the PostgreSQL service to see connection details
5. Note: Railway auto-creates `DATABASE_URL` variable

---

## Step 3: Add Redis Database

1. Click **"+ New"** again
2. Select **"Database"** → **"Redis"**
3. Wait for it to provision
4. Note: Railway auto-creates `REDIS_URL` variable

---

## Step 4: Deploy Backend API

1. Click **"+ New"** → **"GitHub Repo"**
2. Select `unseenedgeai` repository
3. **Configure the service:**

   | Setting | Value |
   |---------|-------|
   | **Service Name** | `backend-api` |
   | **Root Directory** | `backend` |
   | **Build Command** | `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('vader_lexicon')"` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Add Environment Variables** (click "Variables" tab):

   ```
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<generate-32-char-random-string>
   JWT_SECRET_KEY=<generate-32-char-random-string>
   ANTHROPIC_API_KEY=<your-key>
   OPENAI_API_KEY=<your-key>
   PERPLEXITY_API_KEY=<your-key>
   ```

5. **Link Database Variables:**
   - Click "Add Variable" → "Add Reference"
   - Select PostgreSQL → `DATABASE_URL`
   - Select Redis → `REDIS_URL`

6. **Generate Domain:**
   - Go to "Settings" tab
   - Under "Networking", click "Generate Domain"
   - Note the URL (e.g., `backend-api-production.up.railway.app`)

---

## Step 5: Deploy Teacher Dashboard

1. Click **"+ New"** → **"GitHub Repo"**
2. Select `unseenedgeai` repository
3. **Configure:**

   | Setting | Value |
   |---------|-------|
   | **Service Name** | `teacher-dashboard` |
   | **Root Directory** | `backend/dashboard` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `streamlit run app_template.py --server.port=$PORT --server.headless=true --server.address=0.0.0.0` |

4. **Add Environment Variables:**

   ```
   API_URL=https://<your-backend-api-url>
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

5. **Generate Domain** in Settings

---

## Step 6: Deploy Admin Dashboard

1. Click **"+ New"** → **"GitHub Repo"**
2. Select `unseenedgeai` repository
3. **Configure:**

   | Setting | Value |
   |---------|-------|
   | **Service Name** | `admin-dashboard` |
   | **Root Directory** | `backend/dashboard` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `streamlit run admin_dashboard.py --server.port=$PORT --server.headless=true --server.address=0.0.0.0` |

4. **Add Environment Variables:**

   ```
   API_URL=https://<your-backend-api-url>
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

5. **Generate Domain** in Settings

---

## Step 7: Deploy Student Portal

1. Click **"+ New"** → **"GitHub Repo"**
2. Select `unseenedgeai` repository
3. **Configure:**

   | Setting | Value |
   |---------|-------|
   | **Service Name** | `student-portal` |
   | **Root Directory** | `backend/dashboard` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `streamlit run student_portal.py --server.port=$PORT --server.headless=true --server.address=0.0.0.0` |

4. **Add Environment Variables:**

   ```
   API_URL=https://<your-backend-api-url>
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

5. **Generate Domain** in Settings

---

## Step 8: Run Database Migrations

1. Click on the **Backend API** service
2. Go to **"Deployments"** tab
3. Click the three dots menu → **"Open Shell"**
4. Run:

   ```bash
   alembic upgrade head
   ```

5. (Optional) Seed demo data:

   ```bash
   python scripts/seed_demo_data.py
   ```

---

## Step 9: Verify Deployment

### Health Checks

| Service | URL | Expected |
|---------|-----|----------|
| Backend API | `https://<backend-url>/api/v1/health` | `{"status": "healthy"}` |
| Teacher Dashboard | `https://<teacher-url>/` | Login page |
| Admin Dashboard | `https://<admin-url>/` | Login page |
| Student Portal | `https://<student-url>/` | Login page |

### Test Credentials

| Dashboard | Username | Password |
|-----------|----------|----------|
| Teacher | `teacher` | `password123` |
| Admin | `admin` | `admin123` |
| Student | `student123` | `password` |

---

## Environment Variables Reference

### Backend API

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto from Railway) |
| `REDIS_URL` | Yes | Redis connection string (auto from Railway) |
| `SECRET_KEY` | Yes | App secret key (32+ chars) |
| `JWT_SECRET_KEY` | Yes | JWT signing key (32+ chars) |
| `ENVIRONMENT` | Yes | `production` |
| `DEBUG` | No | `false` (default) |
| `ANTHROPIC_API_KEY` | Yes | For AI assessments |
| `OPENAI_API_KEY` | No | Alternative AI provider |
| `PERPLEXITY_API_KEY` | No | For research features |

### Dashboards

| Variable | Required | Description |
|----------|----------|-------------|
| `API_URL` | Yes | Backend API URL |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | No | Set to `false` |

---

## Troubleshooting

### Build Fails

1. Check "Build Logs" in Railway
2. Common issues:
   - Missing `requirements.txt` → Check root directory setting
   - spaCy download fails → It's okay, models will download on first use

### App Crashes on Start

1. Check "Deploy Logs" in Railway
2. Common issues:
   - Missing environment variables → Add them in Variables tab
   - Database not ready → Wait for PostgreSQL to be healthy

### Database Connection Error

1. Ensure `DATABASE_URL` is linked (not manually typed)
2. Check PostgreSQL service is running
3. The URL format should be: `postgresql://user:pass@host:port/db`

### Dashboards Can't Connect to API

1. Verify `API_URL` is correct (include `https://`)
2. Check Backend API has a public domain generated
3. Ensure Backend API is healthy first

---

## Cost Estimate

| Service | Estimated Cost |
|---------|---------------|
| PostgreSQL (1GB) | ~$5-10/month |
| Redis (100MB) | ~$3-5/month |
| Backend API | ~$5-10/month |
| Teacher Dashboard | ~$3-5/month |
| Admin Dashboard | ~$3-5/month |
| Student Portal | ~$3-5/month |
| **Total** | **~$25-40/month** |

*Costs vary based on usage. Railway charges per resource-hour.*

---

## Updating Deployments

Railway auto-deploys when you push to the connected branch (usually `main`).

To manually redeploy:
1. Go to the service
2. Click "Deployments" tab
3. Click "Redeploy" on the latest deployment

---

## Useful Commands (Railway Shell)

```bash
# Run migrations
alembic upgrade head

# Check database
python -c "from app.core.database import engine; print('DB OK')"

# List students
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text
async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text('SELECT COUNT(*) FROM students'))
        print(f'Students: {result.scalar()}')
asyncio.run(check())
"
```
