# MASS Terraform Infrastructure

This directory contains Terraform configurations for deploying the MASS infrastructure on Google Cloud Platform.

## Prerequisites

1. **Terraform**: Install from https://www.terraform.io/downloads
2. **GCP Account**: Active GCP account with billing enabled
3. **GCP Project**: Create a project in GCP Console
4. **gcloud CLI**: Authenticated and configured

## Initial Setup

### 1. Authenticate with GCP

```bash
gcloud auth application-default login
```

### 2. Create Terraform State Bucket

```bash
gsutil mb -l us-central1 gs://unseenedgeai-terraform-state
gsutil versioning set on gs://unseenedgeai-terraform-state
```

### 3. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

## Deployment

### Initialize Terraform

```bash
terraform init
```

### Plan Infrastructure Changes

```bash
terraform plan
```

### Apply Infrastructure

```bash
terraform apply
```

Review the plan carefully and type `yes` to proceed.

## Post-Deployment

After Terraform completes, you need to:

1. **Enable TimescaleDB extension** on Cloud SQL:
   ```bash
   gcloud sql connect mass-postgres-instance --user=postgres
   # In psql:
   CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
   ```

2. **Update API keys in Secret Manager**:
   ```bash
   echo -n "your-key" | gcloud secrets versions add anthropic-api-key --data-file=-
   echo -n "your-key" | gcloud secrets versions add openai-api-key --data-file=-
   echo -n "your-key" | gcloud secrets versions add perplexity-api-key --data-file=-
   ```

3. **Generate JWT secret**:
   ```bash
   openssl rand -base64 32 | gcloud secrets versions add jwt-secret-key --data-file=-
   ```

## Updating Infrastructure

To update infrastructure:

```bash
# Review changes
terraform plan

# Apply updates
terraform apply
```

## Destroying Infrastructure

⚠️ **WARNING**: This will delete all resources!

```bash
terraform destroy
```

## Outputs

After applying, Terraform will output:

- `service_account_email` - Email for the application service account
- `audio_bucket_name` - Cloud Storage bucket for audio files
- `artifacts_bucket_name` - Cloud Storage bucket for artifacts
- `database_connection_name` - Cloud SQL connection string
- `redis_host` - Redis instance host
- `redis_port` - Redis instance port
- `vpc_connector_name` - VPC connector for Cloud Run

View outputs anytime:

```bash
terraform output
```

## State Management

Terraform state is stored in GCS bucket `unseenedgeai-terraform-state`.

**Important**:
- Never edit state files manually
- Use `terraform state` commands for state manipulation
- Enable state locking to prevent concurrent modifications

## Cost Estimation

Estimate monthly costs:

```bash
terraform plan -out=tfplan
terraform show -json tfplan | infracost breakdown --path=-
```

## Troubleshooting

### API Not Enabled Errors

Wait a few minutes after APIs are enabled, then retry:
```bash
terraform apply
```

### Permission Denied Errors

Ensure your GCP user has necessary permissions:
- Project Editor or Owner
- Service Account Admin
- Compute Network Admin

### State Lock Errors

If state is locked after a failed operation:
```bash
terraform force-unlock <lock-id>
```
