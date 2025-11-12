# What YOU Need to Do (Minimal Action List)

I've built all the infrastructure code. Here's the **minimal list** of things only you can do.

---

## ✅ Step 1: Enable Billing (5 minutes)

**Why you need to do this:** I cannot access your GCP billing account.

**What to do:**

1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=unseenedgeai

2. Click "Link a Billing Account"

3. Select your billing account (or create one if needed)

4. Confirm billing is linked

**Verification:**
```bash
gcloud beta billing projects describe unseenedgeai --format="value(billingEnabled)"
```
Should return: `True`

---

## ✅ Step 2: Run the Setup Script (10 minutes)

**Why you need to do this:** The script needs your authorization to create GCP resources.

**What to do:**

```bash
cd /Users/reena/gauntletai/unseenedgeai-infrastructure/infrastructure/scripts
./setup-gcp.sh
```

**What the script does automatically:**
- ✅ Enables all required Google Cloud APIs
- ✅ Creates Terraform state bucket
- ✅ Initializes Terraform
- ✅ Shows you the infrastructure plan
- ✅ Asks for your confirmation before creating resources

**What you'll be asked:**
1. Confirm you've updated `terraform.tfvars` with your email (for alerts)
2. Review the Terraform plan
3. Type "yes" to create the infrastructure

---

## ✅ Step 3: Add OpenAI API Key (2 minutes)

**Why you need to do this:** Needed for GPT-4 reasoning generation (Wave 7).

**What to do:**

1. Get your OpenAI API key from: https://platform.openai.com/api-keys

2. Add it to Secret Manager:
```bash
echo -n 'sk-your-actual-openai-key-here' | gcloud secrets versions add openai-api-key --data-file=-
```

**Note:** You can skip this for now and add it later when implementing Wave 7 (GPT-4 Reasoning).

---

## ✅ Step 4 (Optional): Update Alert Email

**Why you might want to do this:** To receive alerts about infrastructure issues.

**What to do:**

1. Edit the file:
```bash
cd /Users/reena/gauntletai/unseenedgeai-infrastructure/infrastructure/terraform
nano terraform.tfvars
```

2. Update the line:
```
alert_email = "your-actual-email@example.com"
```

3. Re-apply Terraform:
```bash
terraform apply
```

---

## ❌ What You DON'T Need to Do

I've already done these for you:

- ✅ Installed and verified gcloud CLI
- ✅ Created all Terraform configuration files (7 files)
- ✅ Configured Cloud SQL with PostgreSQL 15 + TimescaleDB
- ✅ Set up Cloud Storage buckets with lifecycle policies
- ✅ Configured Cloud Tasks and Pub/Sub
- ✅ Created IAM service accounts with minimal permissions
- ✅ Set up Secret Manager with auto-generated secure passwords
- ✅ Configured monitoring and alerting
- ✅ Created setup and deployment scripts
- ✅ Generated all documentation

---

## 📊 What Gets Created (Summary)

When you run the setup script and approve the Terraform plan, you'll get:

### Databases & Storage
- Cloud SQL PostgreSQL 15 instance (with TimescaleDB)
- Database: `mass_db`
- 2 Cloud Storage buckets (audio files, ML models)

### Async Processing
- 2 Cloud Tasks queues (transcription, inference)
- 4 Pub/Sub topics + subscriptions

### Security
- Service account `mass-api@unseenedgeai.iam.gserviceaccount.com`
- 4 secrets in Secret Manager (DB password, JWT key, OpenAI key, Sentry DSN)

### Monitoring
- 6 alert policies (CPU, memory, errors, queue depth, storage)
- Budget alerts at 50%, 75%, 90%, 100%, 120%

### Estimated Costs
- Cloud SQL: ~$180/month
- Cloud Storage: ~$5-20/month
- Cloud Run: ~$20-50/month (when deployed)
- **Total: ~$250/month** (not including STT/GPT-4 API costs)

---

## 🚀 Quick Start (TL;DR)

If you just want to get started NOW:

```bash
# 1. Enable billing (web UI)
open https://console.cloud.google.com/billing/linkedaccount?project=unseenedgeai

# 2. Run setup script
cd /Users/reena/gauntletai/unseenedgeai-infrastructure/infrastructure/scripts
./setup-gcp.sh

# 3. Wait for completion
# Answer "yes" when prompted

# 4. Done! Infrastructure is ready.
```

---

## ❓ Troubleshooting

### "Permission denied" on setup script
```bash
chmod +x /Users/reena/gauntletai/unseenedgeai-infrastructure/infrastructure/scripts/setup-gcp.sh
```

### "Billing not enabled" error
- Go to https://console.cloud.google.com/billing
- Ensure a billing account is linked to project `unseenedgeai`

### "Terraform not found"
- Install Terraform: `brew install terraform` (Mac)
- Or download from: https://developer.hashicorp.com/terraform/install

### "API not enabled" errors
- The script should enable all APIs automatically
- If it fails, run: `gcloud services enable [api-name].googleapis.com`

---

## 📝 What Happens Next

After you complete these steps:

1. ✅ **Wave 1 Complete** - Infrastructure is provisioned
2. 📋 **Ready for Wave 2** - Authentication System
3. 📋 **Ready for Wave 3** - STT Pipeline + Game Telemetry

You can verify everything works by running:
```bash
cd /Users/reena/gauntletai/unseenedgeai-infrastructure/infrastructure/terraform
terraform show
```

---

## 🔒 Security Notes

- Database passwords are auto-generated (32 characters, secure)
- JWT secrets are auto-generated (32 characters, base64)
- All secrets stored in Google Secret Manager (encrypted)
- Service account has minimal required permissions only
- Audit logging is enabled by default
- Deletion protection is enabled (prevents accidental deletion)

---

## 💰 Cost Control

- **Budget alerts** are configured at 50%, 75%, 90%, 100%, 120%
- **Cloud SQL** scales to your usage (starts at db-custom-2-7680)
- **Cloud Run** scales to zero when not in use (saves money)
- **Audio files** auto-delete after 30 days (lifecycle policy)

You'll receive email alerts before overspending!

---

## ✅ Ready?

**Estimated time:** 15-20 minutes total

**Your action items:**
1. [ ] Enable billing (5 min)
2. [ ] Run `./setup-gcp.sh` (10 min)
3. [ ] (Optional) Add OpenAI API key (2 min)

Let me know when you're done and I'll help you with Wave 2!
