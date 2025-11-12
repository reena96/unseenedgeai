# GitHub Actions Secrets Configuration

This document lists all the secrets that need to be configured in GitHub Actions for CI/CD pipelines.

## How to Add Secrets to GitHub

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/unseenedgeai`
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each secret below

---

## Required Secrets

### 1. GCP Project Configuration

**Secret Name:** `GCP_PROJECT_ID`
**Value:** `unseenedgeai`
**Description:** Google Cloud Project ID

**Secret Name:** `GCP_REGION`
**Value:** `us-central1`
**Description:** Primary GCP region for deployment

**Secret Name:** `GCP_SERVICE_ACCOUNT`
**Value:** `mass-api@unseenedgeai.iam.gserviceaccount.com`
**Description:** Service account email for deployments

---

### 2. Service Account Key (For GitHub Actions Authentication)

**Secret Name:** `GCP_SA_KEY`
**Value:** See instructions below to generate
**Description:** Base64-encoded service account key JSON

#### To Generate Service Account Key:

```bash
# Create a new key for GitHub Actions
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=mass-api@unseenedgeai.iam.gserviceaccount.com

# Base64 encode the key (for GitHub secret)
base64 github-actions-key.json > github-actions-key-base64.txt

# Copy the base64 content and paste as GCP_SA_KEY secret
cat github-actions-key-base64.txt

# IMPORTANT: Delete the local key files after copying
rm github-actions-key.json github-actions-key-base64.txt
```

**⚠️ Security Note:** Never commit service account keys to git! Use GitHub Secrets only.

---

### 3. Database Configuration

**Secret Name:** `DB_CONNECTION_NAME`
**Value:** `unseenedgeai:us-central1:unseenedgeai-db-production`
**Description:** Cloud SQL connection name

**Secret Name:** `DB_NAME`
**Value:** `mass_db`
**Description:** PostgreSQL database name

**Secret Name:** `DB_USER`
**Value:** `mass_api`
**Description:** Database user

**Secret Name:** `DB_PASSWORD`
**Value:** Get from Secret Manager (see below)
**Description:** Database password

#### To Get Database Password:

```bash
# Retrieve the database password from Secret Manager
gcloud secrets versions access latest --secret=db-password

# Copy the output and paste as DB_PASSWORD secret
```

---

### 4. Application Secrets

**Secret Name:** `JWT_SECRET`
**Value:** Get from Secret Manager (see below)
**Description:** JWT signing secret for authentication

#### To Get JWT Secret:

```bash
# Retrieve the JWT secret from Secret Manager
gcloud secrets versions access latest --secret=jwt-secret-key

# Copy the output and paste as JWT_SECRET secret
```

**Secret Name:** `OPENAI_API_KEY`
**Value:** Get from Secret Manager (see below)
**Description:** OpenAI API key for LLM features

#### To Get OpenAI API Key:

```bash
# Retrieve the OpenAI API key from Secret Manager
gcloud secrets versions access latest --secret=openai-api-key

# Copy the output and paste as OPENAI_API_KEY secret
```

---

### 5. Optional Secrets

**Secret Name:** `SENTRY_DSN` (Optional)
**Value:** Get from Secret Manager or Sentry dashboard
**Description:** Sentry error tracking DSN

```bash
# If using Sentry
gcloud secrets versions access latest --secret=sentry-dsn
```

---

## Summary Checklist

Use this checklist to ensure all secrets are configured:

- [ ] `GCP_PROJECT_ID` = `unseenedgeai`
- [ ] `GCP_REGION` = `us-central1`
- [ ] `GCP_SERVICE_ACCOUNT` = `mass-api@unseenedgeai.iam.gserviceaccount.com`
- [ ] `GCP_SA_KEY` = (Base64-encoded service account key JSON)
- [ ] `DB_CONNECTION_NAME` = `unseenedgeai:us-central1:unseenedgeai-db-production`
- [ ] `DB_NAME` = `mass_db`
- [ ] `DB_USER` = `mass_api`
- [ ] `DB_PASSWORD` = (From Secret Manager: db-password)
- [ ] `JWT_SECRET` = (From Secret Manager: jwt-secret-key)
- [ ] `OPENAI_API_KEY` = (From Secret Manager: openai-api-key)
- [ ] `SENTRY_DSN` = (Optional, from Secret Manager: sentry-dsn)

---

## Security Best Practices

1. **Never commit secrets to git** - Always use GitHub Secrets
2. **Rotate keys regularly** - Service account keys should be rotated every 90 days
3. **Use Workload Identity Federation** - For production, consider migrating to Workload Identity Federation instead of service account keys
4. **Limit key permissions** - The `mass-api` service account has minimal required permissions
5. **Monitor key usage** - Check GCP audit logs for service account key usage

---

## Verification

After adding all secrets, verify they're configured correctly:

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. You should see all 10-11 secrets listed
3. Run a test GitHub Actions workflow to verify authentication works

---

## Next Steps

After configuring these secrets:
1. Create/update `.github/workflows/` CI/CD pipelines
2. Test deployment workflow with a test branch
3. Configure branch protection rules for `main` branch
4. Set up deployment environments (staging, production)

---

*Last updated: 2025-11-12*
