# Cloud SQL (PostgreSQL + TimescaleDB) Configuration

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Cloud SQL Instance
resource "google_sql_database_instance" "mass_db" {
  name             = local.db_instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  # Prevent accidental deletion
  deletion_protection = var.enable_deletion_protection

  settings {
    tier              = var.db_tier
    availability_type = var.enable_high_availability ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100 # GB, will auto-resize
    disk_autoresize   = true

    # Backup configuration
    backup_configuration {
      enabled                        = true
      start_time                     = var.db_backup_time
      point_in_time_recovery_enabled = var.enable_point_in_time_recovery
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30 # Keep 30 days of backups
        retention_unit   = "COUNT"
      }
    }

    # Maintenance window
    maintenance_window {
      day  = var.db_maintenance_window.day
      hour = var.db_maintenance_window.hour
    }

    # IP configuration
    ip_configuration {
      ipv4_enabled    = true
      private_network = null # Use public IP for Phase 1, VPC in Phase 2
      ssl_mode        = "ENCRYPTED_ONLY"

      # Authorized networks (empty for now, will use Cloud Run connector)
      dynamic "authorized_networks" {
        for_each = []
        content {
          name  = authorized_networks.value.name
          value = authorized_networks.value.value
        }
      }
    }

    # Database flags
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    # Note: TimescaleDB extension will be installed via SQL after instance creation
    # shared_preload_libraries flag is not supported in Cloud SQL managed PostgreSQL

    # Insights and monitoring
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }

    # Labels
    user_labels = local.common_labels
  }

  depends_on = [google_project_service.required_apis]
}

# Create database
resource "google_sql_database" "mass_database" {
  name     = var.db_name
  instance = google_sql_database_instance.mass_db.name
}

# Create database user
resource "google_sql_user" "mass_user" {
  name     = "mass_api"
  instance = google_sql_database_instance.mass_db.name
  password = random_password.db_password.result
}

# Outputs
output "db_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.mass_db.name
}

output "db_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.mass_db.connection_name
}

output "db_public_ip" {
  description = "Cloud SQL public IP address"
  value       = google_sql_database_instance.mass_db.public_ip_address
}

output "db_name" {
  description = "Database name"
  value       = google_sql_database.mass_database.name
}

output "db_user" {
  description = "Database user"
  value       = google_sql_user.mass_user.name
  sensitive   = true
}
