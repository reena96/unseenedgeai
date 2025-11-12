#!/bin/bash
# Cloud SQL PostgreSQL + TimescaleDB Setup Script

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-unseenedgeai}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
INSTANCE_NAME="mass-postgres-instance"
DATABASE_NAME="mass_db"
DB_USER="mass_app_user"

echo "=== Cloud SQL PostgreSQL + TimescaleDB Setup ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Instance: $INSTANCE_NAME"
echo ""

# Check if instance already exists
if gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT_ID" &> /dev/null; then
    echo "Instance $INSTANCE_NAME already exists"
else
    echo "Creating Cloud SQL instance..."
    gcloud sql instances create "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --database-version=POSTGRES_15 \
        --tier=db-n1-standard-2 \
        --region="$REGION" \
        --availability-type=REGIONAL \
        --storage-type=SSD \
        --storage-size=100GB \
        --storage-auto-increase \
        --backup \
        --backup-start-time=03:00 \
        --retained-backups-count=30 \
        --database-flags=max_connections=1000,shared_preload_libraries=timescaledb \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=3

    echo "✓ Instance created"
fi

# Create database
echo "Creating database..."
gcloud sql databases create "$DATABASE_NAME" \
    --instance="$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    || echo "Database might already exist"

# Create user
echo "Creating database user..."
DB_PASSWORD=$(openssl rand -base64 32)

gcloud sql users create "$DB_USER" \
    --instance="$INSTANCE_NAME" \
    --password="$DB_PASSWORD" \
    --project="$PROJECT_ID" \
    || echo "User might already exist"

# Store password in Secret Manager
echo "$DB_PASSWORD" | gcloud secrets versions add database-password \
    --data-file=- \
    --project="$PROJECT_ID"

echo "✓ Database user created and password stored in Secret Manager"

# Get connection info
CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(connectionName)")

PRIVATE_IP=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(ipAddresses[0].ipAddress)")

echo ""
echo "=== Cloud SQL Setup Complete ==="
echo ""
echo "Connection Name: $CONNECTION_NAME"
echo "Private IP: $PRIVATE_IP"
echo "Database: $DATABASE_NAME"
echo "User: $DB_USER"
echo "Password: Stored in Secret Manager (database-password)"
echo ""
echo "Connection string for Cloud Run:"
echo "postgresql+asyncpg://$DB_USER:<password>@$PRIVATE_IP:5432/$DATABASE_NAME"
echo ""
echo "Next steps:"
echo "1. Connect to the database:"
echo "   gcloud sql connect $INSTANCE_NAME --user=postgres --project=$PROJECT_ID"
echo ""
echo "2. Enable TimescaleDB extension:"
echo "   CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
echo ""
echo "3. Run database initialization:"
echo "   python backend/scripts/init_db.py"
