#!/bin/bash
set -e

# MASS System - GCP Infrastructure Setup Script
# This script sets up the complete GCP infrastructure for the MASS system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="unseenedgeai"
REGION="us-central1"

echo "==============================================="
echo "MASS System - GCP Infrastructure Setup"
echo "==============================================="
echo ""

# ============================================
# 1. VERIFY PREREQUISITES
# ============================================

echo -e "${YELLOW}Step 1: Verifying prerequisites...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}✓ gcloud CLI installed${NC}"

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${YELLOW}WARNING: Terraform is not installed${NC}"
    echo "Install from: https://developer.hashicorp.com/terraform/install"
    echo "Or continue without Terraform for manual setup"
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
fi
echo -e "${GREEN}✓ Authenticated${NC}"

# Set project
echo "Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Check if billing is enabled
echo -e "\n${YELLOW}Checking if billing is enabled...${NC}"
BILLING_ENABLED=$(gcloud beta billing projects describe $PROJECT_ID --format="value(billingEnabled)" 2>/dev/null || echo "false")

if [ "$BILLING_ENABLED" != "True" ]; then
    echo -e "${RED}ERROR: Billing is not enabled for project $PROJECT_ID${NC}"
    echo ""
    echo "Please enable billing:"
    echo "1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
    echo "2. Link a billing account"
    echo "3. Re-run this script"
    exit 1
fi
echo -e "${GREEN}✓ Billing enabled${NC}"

echo ""

# ============================================
# 2. ENABLE REQUIRED APIs
# ============================================

echo -e "${YELLOW}Step 2: Enabling required Google Cloud APIs...${NC}"
echo "This may take 2-3 minutes..."

APIS=(
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "storage.googleapis.com"
    "cloudtasks.googleapis.com"
    "pubsub.googleapis.com"
    "speech.googleapis.com"
    "secretmanager.googleapis.com"
    "logging.googleapis.com"
    "monitoring.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api --project=$PROJECT_ID
done

echo -e "${GREEN}✓ All APIs enabled${NC}"
echo ""

# ============================================
# 3. CREATE TERRAFORM STATE BUCKET (optional)
# ============================================

echo -e "${YELLOW}Step 3: Creating Terraform state bucket (optional)...${NC}"

STATE_BUCKET="${PROJECT_ID}-terraform-state"

if gsutil ls -b gs://$STATE_BUCKET 2>/dev/null; then
    echo -e "${GREEN}✓ Terraform state bucket already exists${NC}"
else
    echo "Creating bucket: $STATE_BUCKET"
    gsutil mb -p $PROJECT_ID -l $REGION gs://$STATE_BUCKET/
    gsutil versioning set on gs://$STATE_BUCKET/
    echo -e "${GREEN}✓ Terraform state bucket created${NC}"
fi

echo ""

# ============================================
# 4. TERRAFORM INITIALIZATION
# ============================================

if command -v terraform &> /dev/null; then
    echo -e "${YELLOW}Step 4: Initializing Terraform...${NC}"

    cd ../terraform

    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${YELLOW}terraform.tfvars not found. Copying from example...${NC}"
        cp terraform.tfvars.example terraform.tfvars
        echo -e "${RED}IMPORTANT: Edit terraform.tfvars and update the alert_email and other values!${NC}"
        echo "File location: $(pwd)/terraform.tfvars"
        read -p "Press Enter after you've updated terraform.tfvars..."
    fi

    # Initialize Terraform
    terraform init

    echo -e "${GREEN}✓ Terraform initialized${NC}"
    echo ""

    # ============================================
    # 5. TERRAFORM PLAN
    # ============================================

    echo -e "${YELLOW}Step 5: Running Terraform plan...${NC}"
    terraform plan -out=tfplan

    echo ""
    echo -e "${YELLOW}Terraform plan complete. Review the changes above.${NC}"
    read -p "Do you want to apply these changes? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Applying Terraform configuration...${NC}"
        terraform apply tfplan
        echo -e "${GREEN}✓ Infrastructure created!${NC}"
    else
        echo -e "${YELLOW}Skipping Terraform apply. Run manually when ready:${NC}"
        echo "cd infrastructure/terraform && terraform apply"
    fi
else
    echo -e "${YELLOW}Terraform not installed. Skipping automatic infrastructure creation.${NC}"
    echo "Install Terraform or run the gcloud commands manually."
fi

echo ""

# ============================================
# FINAL STEPS
# ============================================

echo "==============================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Update OpenAI API key:"
echo "   echo -n 'your-openai-key' | gcloud secrets versions add openai-api-key --data-file=-"
echo ""
echo "2. (Optional) Update Sentry DSN if using error tracking:"
echo "   echo -n 'your-sentry-dsn' | gcloud secrets versions add sentry-dsn --data-file=-"
echo ""
echo "3. View created resources:"
echo "   cd infrastructure/terraform && terraform show"
echo ""
echo "4. Get database connection info:"
echo "   gcloud sql instances describe $PROJECT_ID-db-production --format='value(connectionName)'"
echo ""
echo "5. Proceed to Wave 2: Authentication System"
echo ""
