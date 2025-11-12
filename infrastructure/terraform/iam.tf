# IAM Configuration - Service Accounts and Permissions

# ============================================
# SERVICE ACCOUNT
# ============================================

# Main service account for MASS API
resource "google_service_account" "mass_api" {
  account_id   = "mass-api"
  display_name = "MASS API Service Account"
  description  = "Service account for MASS API server with minimal required permissions"

  depends_on = [google_project_service.required_apis]
}

# ============================================
# IAM ROLE BINDINGS
# ============================================

# Cloud SQL Client (connect to database)
resource "google_project_iam_member" "mass_api_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Storage Object Admin (already defined in storage.tf, but adding project-level)
resource "google_project_iam_member" "mass_api_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Cloud Tasks Enqueuer (create tasks)
resource "google_project_iam_member" "mass_api_tasks_enqueuer" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Pub/Sub Publisher
resource "google_project_iam_member" "mass_api_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Pub/Sub Subscriber
resource "google_project_iam_member" "mass_api_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Secret Manager Secret Accessor (read secrets)
resource "google_project_iam_member" "mass_api_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Speech-to-Text User (use STT API)
resource "google_project_iam_member" "mass_api_speech_user" {
  project = var.project_id
  role    = "roles/speech.client"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Cloud Logging Writer (write logs)
resource "google_project_iam_member" "mass_api_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# Cloud Monitoring Metric Writer (write custom metrics)
resource "google_project_iam_member" "mass_api_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.mass_api.email}"
}

# ============================================
# SERVICE ACCOUNT KEY (for local development)
# ============================================

# Generate service account key (ONLY for development)
# WARNING: This creates a sensitive key file. In production, use Workload Identity
resource "google_service_account_key" "mass_api_key" {
  service_account_id = google_service_account.mass_api.name

  # Only create if explicitly enabled (default: false for security)
  count = 0 # Set to 1 to generate key for local development
}

# ============================================
# OUTPUTS
# ============================================

output "service_account_email" {
  description = "MASS API service account email"
  value       = google_service_account.mass_api.email
}

output "service_account_name" {
  description = "MASS API service account name"
  value       = google_service_account.mass_api.name
}

# Only output if key was created
output "service_account_key" {
  description = "MASS API service account key (base64 encoded) - SENSITIVE"
  value       = length(google_service_account_key.mass_api_key) > 0 ? google_service_account_key.mass_api_key[0].private_key : null
  sensitive   = true
}
