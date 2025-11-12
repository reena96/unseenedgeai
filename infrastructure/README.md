# MASS Infrastructure - Wave 1

This directory contains all infrastructure-as-code for the MASS system.

## 📁 Directory Structure

```
infrastructure/
├── terraform/              # Terraform configuration files
│   ├── main.tf            # Main Terraform config, provider setup
│   ├── variables.tf       # Variable definitions
│   ├── cloud-sql.tf       # PostgreSQL database
│   ├── storage.tf         # Cloud Storage buckets
│   ├── tasks-pubsub.tf    # Cloud Tasks + Pub/Sub
│   ├── iam.tf             # Service accounts + permissions
│   ├── secrets.tf         # Secret Manager
│   ├── monitoring.tf      # Alerts + monitoring
│   └── terraform.tfvars.example  # Example variables file
├── scripts/               # Setup and deployment scripts
│   └── setup-gcp.sh      # Main GCP setup script
└── README.md             # This file
```

## 🚀 Quick Start

See `../WHAT_YOU_NEED_TO_DO.md` for step-by-step instructions.

**TL;DR:**
```bash
# 1. Enable billing in GCP Console
# 2. Run setup script
cd scripts
./setup-gcp.sh
```

## 📋 What Gets Created

### Compute & Databases
- Cloud SQL PostgreSQL 15 instance (db-custom-2-7680)
- TimescaleDB extension enabled
- High availability mode
- Automated daily backups

### Storage
- `unseenedgeai-audio-files` bucket (30-day lifecycle)
- `unseenedgeai-ml-models` bucket (versioned)

### Async Processing
- `transcription-jobs` queue (10 concurrent)
- `inference-jobs` queue (20 concurrent)
- 4 Pub/Sub topics with subscriptions

### Security
- Service account: `mass-api@unseenedgeai.iam.gserviceaccount.com`
- 4 secrets in Secret Manager:
  - `db-password` (auto-generated)
  - `jwt-secret-key` (auto-generated)
  - `openai-api-key` (user must add)
  - `sentry-dsn` (optional)

### Monitoring
- 6 alert policies (CPU, memory, errors, queues, storage)
- Budget alerts at multiple thresholds
- Email notifications (if configured)

## 🔧 Terraform Commands

### Initialize Terraform
```bash
cd terraform
terraform init
```

### Plan changes
```bash
terraform plan
```

### Apply changes
```bash
terraform apply
```

### Show current state
```bash
terraform show
```

### Destroy all resources (DANGER!)
```bash
terraform destroy
```

## 📝 Configuration

### Required Variables
Edit `terraform/terraform.tfvars`:

```hcl
project_id = "unseenedgeai"
region     = "us-central1"

# IMPORTANT: Set this for alerts
alert_email = "your-email@example.com"

# Optional: Customize budget
budget_amount = 1000
```

### Optional Variables
See `terraform/variables.tf` for all available options:
- Database tier, backup times
- Cloud Run scaling limits
- Queue concurrency
- Storage retention
- Feature flags

## 🔒 Security

### Service Account Permissions
The `mass-api` service account has minimal required permissions:
- `roles/cloudsql.client` - Connect to database
- `roles/storage.objectAdmin` - Read/write storage
- `roles/cloudtasks.enqueuer` - Create tasks
- `roles/pubsub.publisher` - Publish messages
- `roles/pubsub.subscriber` - Subscribe to topics
- `roles/secretmanager.secretAccessor` - Read secrets
- `roles/speech.client` - Use Speech-to-Text
- `roles/logging.logWriter` - Write logs
- `roles/monitoring.metricWriter` - Write metrics

### Secrets Management
- All secrets stored in Google Secret Manager
- Encrypted at rest and in transit
- Automatic secret rotation (configure manually)
- IAM-based access control

### Network Security
- Cloud SQL uses SSL/TLS connections
- Public IP with authorized networks (empty for Phase 1)
- Will migrate to VPC in Phase 2

## 💰 Cost Estimates

| Service | Monthly Cost |
|---------|-------------|
| Cloud SQL (db-custom-2-7680) | ~$180 |
| Cloud Storage (100 GB) | ~$10 |
| Cloud Run (minimal usage) | ~$20-50 |
| Cloud Tasks + Pub/Sub | ~$5 |
| Cloud Logging | ~$5 |
| **Total** | **~$250/month** |

**Not included:**
- Google Cloud Speech-to-Text: ~$10k for Phase 1 pilot
- OpenAI GPT-4 API: ~$28/month for 100 students

## 📊 Monitoring

### Alert Policies
1. **Database Connection Failures** - Alerts if >10 failures in 5 minutes
2. **High CPU Usage** - Alerts if CPU >80% for 5 minutes
3. **High Memory Usage** - Alerts if memory >90% for 5 minutes
4. **Cloud Run Errors** - Alerts if error rate >5%
5. **High Queue Depth** - Alerts if >100 tasks pending for 10 minutes
6. **Storage Quota** - Alerts if bucket >100 GB

### Budget Alerts
- 50% of budget
- 75% of budget
- 90% of budget
- 100% of budget
- 120% of forecasted spend

## 🧪 Testing

### Verify Infrastructure
```bash
# Check Cloud SQL instance
gcloud sql instances describe unseenedgeai-db-production

# List buckets
gsutil ls

# List secrets
gcloud secrets list

# Check service account
gcloud iam service-accounts describe mass-api@unseenedgeai.iam.gserviceaccount.com
```

### Connect to Database
```bash
# Get connection name
gcloud sql instances describe unseenedgeai-db-production --format='value(connectionName)'

# Connect via cloud_sql_proxy
cloud_sql_proxy -instances=CONNECTION_NAME=tcp:5432
```

## 🐛 Troubleshooting

### Terraform state lock
```bash
terraform force-unlock LOCK_ID
```

### API not enabled
```bash
gcloud services enable [api-name].googleapis.com --project=unseenedgeai
```

### Permission denied
```bash
# Ensure you have Owner or Editor role
gcloud projects get-iam-policy unseenedgeai --flatten="bindings[].members" --filter="bindings.members:user:YOUR_EMAIL"
```

### Budget not appearing
- Budgets can take up to 24 hours to show in console
- Check: https://console.cloud.google.com/billing/budgets

## 📚 Documentation

- [Google Cloud SQL](https://cloud.google.com/sql/docs)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Tasks](https://cloud.google.com/tasks/docs)
- [Pub/Sub](https://cloud.google.com/pubsub/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

## ✅ Next Steps

After Wave 1 is complete:
1. ✅ Infrastructure provisioned
2. 📋 Wave 2: Authentication System
3. 📋 Wave 3: STT Pipeline + Game Telemetry
4. 📋 Wave 4: ML Inference + Evidence Fusion
5. 📋 Wave 5: GPT-4 Reasoning
6. 📋 Wave 6: Teacher Dashboard

See `../openspec/changes/` for detailed implementation tasks for each wave.
