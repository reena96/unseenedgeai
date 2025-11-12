# MASS Infrastructure - Terraform Configuration
# This defines the complete GCP infrastructure for the Middle School Non-Academic Skills Measurement System

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Store state in GCS bucket (create manually first)
  backend "gcs" {
    bucket = "unseenedgeai-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudrun.googleapis.com",
    "sqladmin.googleapis.com",
    "storage-api.googleapis.com",
    "speech.googleapis.com",
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudscheduler.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# Service Account for the application
resource "google_service_account" "app_service_account" {
  account_id   = "mass-app-service-account"
  display_name = "MASS Application Service Account"
  description  = "Service account for the MASS application backend"
}

# IAM roles for service account
resource "google_project_iam_member" "app_service_account_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/speech.client",
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/secretmanager.secretAccessor",
    "roles/redis.editor",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Cloud Storage bucket for audio files
resource "google_storage_bucket" "audio_files" {
  name          = "${var.project_id}-audio-files"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90  # Delete files older than 90 days
    }
    action {
      type = "Delete"
    }
  }

  encryption {
    default_kms_key_name = null  # Use Google-managed encryption
  }
}

# Cloud Storage bucket for artifacts and backups
resource "google_storage_bucket" "artifacts" {
  name          = "${var.project_id}-artifacts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = null
  }
}

# Secret Manager secrets
resource "google_secret_manager_secret" "secrets" {
  for_each = toset([
    "anthropic-api-key",
    "openai-api-key",
    "perplexity-api-key",
    "jwt-secret-key",
    "database-password",
    "database-url",
    "redis-connection-string",
  ])

  secret_id = each.value

  replication {
    auto {}
  }
}

# VPC for private service networking (for Cloud SQL)
resource "google_compute_network" "private_network" {
  name                    = "mass-private-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "private_subnet" {
  name          = "mass-private-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.private_network.id

  private_ip_google_access = true
}

# Reserve IP range for Cloud SQL private connection
resource "google_compute_global_address" "private_ip_address" {
  name          = "mass-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.private_network.id
}

# Private VPC connection for Cloud SQL
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.private_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL PostgreSQL instance (TimescaleDB extension will be added manually)
resource "google_sql_database_instance" "postgres_instance" {
  name             = "mass-postgres-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-n1-standard-2"  # 2 vCPU, 7.5 GB RAM
    disk_size         = 100                  # GB
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    availability_type = "REGIONAL"           # High availability

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"  # 3 AM UTC
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.private_network.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "1000"
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "timescaledb"  # Enable TimescaleDB
    }

    maintenance_window {
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }
  }

  deletion_protection = true

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Database
resource "google_sql_database" "mass_database" {
  name     = "mass_db"
  instance = google_sql_database_instance.postgres_instance.name
}

# Database user
resource "google_sql_user" "mass_user" {
  name     = "mass_app_user"
  instance = google_sql_database_instance.postgres_instance.name
  password = random_password.db_password.result
}

# Generate secure database password
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret_version" "database_password" {
  secret      = google_secret_manager_secret.secrets["database-password"].id
  secret_data = random_password.db_password.result
}

# Redis instance for task queue
resource "google_redis_instance" "redis_instance" {
  name           = "mass-redis-instance"
  tier           = "STANDARD_HA"  # High availability
  memory_size_gb = 5
  region         = var.region

  redis_version     = "REDIS_7_0"
  display_name      = "MASS Redis Instance"
  authorized_network = google_compute_network.private_network.id

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  depends_on = [google_project_service.required_apis]
}

# VPC Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "connector" {
  name          = "mass-vpc-connector"
  region        = var.region
  network       = google_compute_network.private_network.name
  ip_cidr_range = "10.8.0.0/28"

  depends_on = [google_project_service.required_apis]
}

# Outputs
output "service_account_email" {
  description = "Email of the application service account"
  value       = google_service_account.app_service_account.email
}

output "audio_bucket_name" {
  description = "Name of the Cloud Storage bucket for audio files"
  value       = google_storage_bucket.audio_files.name
}

output "artifacts_bucket_name" {
  description = "Name of the Cloud Storage bucket for artifacts"
  value       = google_storage_bucket.artifacts.name
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres_instance.connection_name
}

output "database_private_ip" {
  description = "Private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres_instance.private_ip_address
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.redis_instance.host
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.redis_instance.port
}

output "vpc_connector_name" {
  description = "VPC connector name for Cloud Run"
  value       = google_vpc_access_connector.connector.name
}
