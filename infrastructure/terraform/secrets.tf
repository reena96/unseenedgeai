# Secret Manager Configuration

# ============================================
# SECRETS CREATION
# ============================================

# JWT Secret Key (for API authentication)
resource "random_password" "jwt_secret" {
  length  = 32
  special = false # Base64-friendly
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-key"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

# OpenAI API Key (placeholder - user must update manually)
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# Note: openai-api-key secret version already exists from previous setup
# Users should update it manually with: gcloud secrets versions add openai-api-key --data-file=-

# App Secret Key (for session encryption)
resource "random_password" "app_secret" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "app_secret_key" {
  secret_id = "app-secret-key"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "app_secret_key" {
  secret      = google_secret_manager_secret.app_secret_key.id
  secret_data = random_password.app_secret.result
}

# Database URL (constructed from Cloud SQL instance)
resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "postgresql://${google_sql_user.mass_user.name}:${random_password.db_password.result}@/${google_sql_database.mass_database.name}?host=/cloudsql/${google_sql_database_instance.mass_db.connection_name}"
}

# Redis URL (placeholder for future Redis instance)
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url"

  replication {
    auto {}
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "redis_url" {
  secret      = google_secret_manager_secret.redis_url.id
  secret_data = "redis://localhost:6379/0" # Placeholder - update when Redis deployed

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# Sentry DSN (optional - placeholder)
resource "google_secret_manager_secret" "sentry_dsn" {
  secret_id = "sentry-dsn"

  replication {
    auto {}
  }

  labels = merge(local.common_labels, {
    optional = "true"
  })

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "sentry_dsn" {
  secret      = google_secret_manager_secret.sentry_dsn.id
  secret_data = "PLACEHOLDER_OPTIONAL" # User can update if using Sentry

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# ============================================
# IAM PERMISSIONS FOR SECRETS
# ============================================

# Grant service account access to all secrets
resource "google_secret_manager_secret_iam_member" "app_secret_access" {
  secret_id = google_secret_manager_secret.app_secret_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "jwt_secret_access" {
  secret_id = google_secret_manager_secret.jwt_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "db_password_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "database_url_access" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "redis_url_access" {
  secret_id = google_secret_manager_secret.redis_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "openai_key_access" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

resource "google_secret_manager_secret_iam_member" "sentry_dsn_access" {
  secret_id = google_secret_manager_secret.sentry_dsn.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mass_api.email}"
}

# ============================================
# OUTPUTS
# ============================================

output "secret_ids" {
  description = "Secret Manager secret IDs"
  value = {
    jwt_secret     = google_secret_manager_secret.jwt_secret.id
    db_password    = google_secret_manager_secret.db_password.id
    openai_api_key = google_secret_manager_secret.openai_api_key.id
    sentry_dsn     = google_secret_manager_secret.sentry_dsn.id
  }
}

output "secrets_note" {
  description = "Important note about secrets"
  value       = "IMPORTANT: Update the openai-api-key secret with your real OpenAI API key using: gcloud secrets versions add openai-api-key --data-file=- < api_key.txt"
}
