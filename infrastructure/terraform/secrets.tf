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

resource "google_secret_manager_secret_version" "openai_api_key" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = "PLACEHOLDER_UPDATE_WITH_REAL_KEY" # User must update this

  lifecycle {
    ignore_changes = [secret_data] # Don't overwrite user updates
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
