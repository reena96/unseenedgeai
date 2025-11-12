# Wave 1 Setup Checklist: Required Information

This checklist contains all the information and credentials you need to gather before implementing Wave 1 (Infrastructure Setup).

---

## ☑️ Pre-Implementation Checklist

### 1. Google Cloud Platform (GCP) Account Setup

#### 1.1 GCP Project
- [ ] **GCP Project ID** (e.g., `mass-production` or your preferred name)
  - Where to find: [GCP Console](https://console.cloud.google.com) → Select/Create Project
  - Must be globally unique
  - Recommend: `mass-production-[your-org]` or `unseenedgeai-prod`
  - **Your value:** `___________________________`

- [ ] **GCP Billing Account ID**
  - Where to find: [Billing Console](https://console.cloud.google.com/billing)
  - Format: `XXXXXX-XXXXXX-XXXXXX`
  - **Your value:** `___________________________`

- [ ] **Default Region**
  - Recommended: `us-central1` (Iowa - cost-effective)
  - Alternative: `us-east1`, `us-west1`
  - **Your choice:** `___________________________`

#### 1.2 GCP User Permissions
- [ ] You have **Owner** or **Editor** role on the GCP project
- [ ] You can create service accounts
- [ ] You can enable billing

#### 1.3 GCP CLI Installed
- [ ] Install gcloud CLI: https://cloud.google.com/sdk/docs/install
- [ ] Run: `gcloud --version` to verify installation
- [ ] Run: `gcloud auth login` to authenticate

---

### 2. Secrets & API Keys

#### 2.1 Database Credentials
- [ ] **PostgreSQL Admin Password** (create a strong password)
  - Minimum 12 characters, mix of letters, numbers, symbols
  - Store securely (you'll add to Secret Manager)
  - **Your password:** `___________________________ ` (DELETE AFTER STORING IN SECRET MANAGER)

#### 2.2 JWT Authentication
- [ ] **JWT Secret Key** (256-bit random string)
  - Generate with: `openssl rand -base64 32`
  - **Your key:** `___________________________ ` (DELETE AFTER STORING IN SECRET MANAGER)

#### 2.3 OpenAI API Key (for GPT-4 reasoning)
- [ ] **OpenAI API Key**
  - Where to get: [OpenAI Platform](https://platform.openai.com/api-keys)
  - Create account if needed
  - Enable billing (credit card required)
  - Format: `sk-...`
  - **Your key:** `___________________________ ` (DELETE AFTER STORING IN SECRET MANAGER)

---

### 3. GitHub Repository Setup

#### 3.1 GitHub Repository
- [ ] **GitHub Repository URL**
  - Format: `https://github.com/[org]/[repo].git`
  - **Your repo:** `___________________________`

- [ ] **GitHub Personal Access Token** (for GitHub Actions)
  - Where to create: [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
  - Permissions needed: `repo`, `workflow`
  - **Your token:** `___________________________ ` (DELETE AFTER STORING)

#### 3.2 Repository Structure
- [ ] Current directory is a git repository (already initialized ✅)
- [ ] Git remote is configured
  - Run: `git remote add origin [your-repo-url]` if not set

---

### 4. Email & Notifications (Optional but Recommended)

#### 4.1 Alerting Email
- [ ] **Email for GCP alerts** (monitoring, billing, errors)
  - **Your email:** `___________________________`

#### 4.2 Slack Webhook (Optional)
- [ ] **Slack webhook URL** for alerts
  - Where to create: Slack → Apps → Incoming Webhooks
  - **Your webhook:** `___________________________ ` (optional)

---

### 5. Domain & SSL (Optional for Phase 1)

#### 5.1 Custom Domain (Optional)
- [ ] **Domain name** (if you want custom domain instead of Cloud Run URL)
  - Example: `api.unseenedge.ai`
  - **Your domain:** `___________________________` (optional for Phase 1)

- [ ] **DNS provider access** (if using custom domain)

---

### 6. Budget & Cost Controls

#### 6.1 Budget Limits
- [ ] **Monthly budget cap** for GCP
  - Recommended for Phase 1: $500-1,000/month
  - **Your budget:** `$___________________________`

#### 6.2 Cost Awareness
- [ ] Understand approximate costs:
  - Cloud SQL (db-custom-2-7680): ~$180/month
  - Cloud Run (minimal usage): ~$20-50/month
  - Cloud Storage: ~$5-20/month
  - Cloud STT: ~$10,000 for Phase 1 pilot
  - OpenAI GPT-4: ~$28/month for 100 students
  - **Total estimated**: ~$250-300/month + $10k STT pilot

---

### 7. Environment Configuration Values

#### 7.1 Application Settings
- [ ] **Environment name** (e.g., `production`, `staging`, `development`)
  - **Your choice:** `___________________________`

- [ ] **CORS allowed origins** (frontend URLs that can access API)
  - Example: `https://dashboard.unseenedge.ai,http://localhost:3000`
  - **Your origins:** `___________________________`

#### 7.2 Database Settings
- [ ] **Database name** (default: `mass_db`)
  - **Your choice:** `___________________________`

- [ ] **Database instance name** (default: `mass-db`)
  - **Your choice:** `___________________________`

---

### 8. Third-Party Tools (Optional)

#### 8.1 Error Tracking
- [ ] **Sentry DSN** (optional but recommended)
  - Where to get: [Sentry.io](https://sentry.io)
  - Free tier available
  - **Your DSN:** `___________________________` (optional)

#### 8.2 Analytics (Optional)
- [ ] **Google Analytics ID** (if tracking dashboard usage)
  - **Your GA ID:** `___________________________` (optional)

---

## 🚀 Quick Start Values (Recommended Defaults)

If you want to get started quickly with sensible defaults, here's what I recommend:

```bash
# Core GCP Settings
GCP_PROJECT_ID="mass-production-unseenedge"
GCP_REGION="us-central1"
GCP_ZONE="us-central1-a"

# Database
DB_INSTANCE_NAME="mass-db"
DB_NAME="mass_db"
DB_TIER="db-custom-2-7680"

# Storage
AUDIO_BUCKET_NAME="${GCP_PROJECT_ID}-audio-files"
MODELS_BUCKET_NAME="${GCP_PROJECT_ID}-ml-models"

# Application
APP_NAME="mass-api"
ENVIRONMENT="production"
```

---

## 📋 What to Do With These Values

### Option A: Create `.env` File (Recommended)

I'll create a `.env.example` file with all these variables, and you can:
1. Copy to `.env`
2. Fill in your actual values
3. Add `.env` to `.gitignore` (never commit secrets!)

### Option B: Store in Secret Manager Directly

We'll use Terraform and scripts to:
1. Read values from your input
2. Create GCP resources
3. Store secrets in Secret Manager automatically

### Option C: Hybrid (Best for Production)

1. Non-sensitive config → `.env` file
2. Sensitive secrets → Secret Manager only
3. Terraform manages everything

---

## ✅ Verification Steps

Once you've gathered everything, we'll verify:

```bash
# 1. GCP authentication
gcloud auth login
gcloud config set project [YOUR_PROJECT_ID]

# 2. Enable required APIs (I'll help with this)
gcloud services enable run.googleapis.com sqladmin.googleapis.com ...

# 3. Create service account
gcloud iam service-accounts create mass-api

# 4. Store secrets
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-
```

---

## 🎯 Minimum Required to Start

**Absolutely need right now:**
1. ✅ GCP Project ID
2. ✅ GCP Billing Account (linked to project)
3. ✅ gcloud CLI installed and authenticated

**Can generate/create during implementation:**
- Database passwords (we'll generate secure ones)
- JWT secrets (we'll generate)
- Service accounts (we'll create)
- Buckets, queues, topics (we'll provision)

**Can add later:**
- OpenAI API key (needed for reasoning generation in later waves)
- Sentry DSN (optional)
- Custom domain (optional)
- Slack webhooks (optional)

---

## 🔒 Security Reminders

1. **NEVER commit secrets to git**
   - Add `.env` to `.gitignore`
   - Use Secret Manager for all sensitive data
   - Rotate secrets regularly

2. **Use least privilege**
   - Service accounts get minimum required permissions
   - No broad `Owner` roles for apps

3. **Enable audit logging**
   - Track all access to secrets
   - Monitor for unusual activity

4. **Set up billing alerts**
   - Get notified before overspending
   - Daily budget monitoring

---

## 📞 Next Steps

Once you have the **minimum required** items (GCP Project ID, Billing, gcloud CLI), let me know and I'll:

1. Create all Terraform configuration files
2. Generate secure secrets automatically
3. Set up the complete infrastructure
4. Test everything works
5. Create deployment scripts

**Ready to proceed?** Just provide:
- GCP Project ID
- Confirmation that billing is enabled
- Confirmation that gcloud CLI is authenticated

I'll handle the rest! 🚀
