# Cloud Storage Configuration

# Audio files bucket (temporary storage, 30-day lifecycle)
resource "google_storage_bucket" "audio_files" {
  name          = local.audio_bucket
  location      = var.region
  force_destroy = false # Prevent accidental deletion

  uniform_bucket_level_access = true

  # Lifecycle rule: delete files after 30 days
  lifecycle_rule {
    condition {
      age = var.audio_retention_days
    }
    action {
      type = "Delete"
    }
  }

  # Versioning for accidental deletion recovery
  versioning {
    enabled = var.enable_storage_versioning
  }

  # CORS for frontend uploads
  cors {
    origin          = var.allowed_cors_origins
    method          = ["GET", "POST", "PUT", "DELETE"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# ML models bucket (long-term storage)
resource "google_storage_bucket" "ml_models" {
  name          = local.models_bucket
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  # Versioning for model rollback
  versioning {
    enabled = true
  }

  # Storage class for cost optimization
  storage_class = "STANDARD"

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# IAM binding for audio bucket (service account access)
resource "google_storage_bucket_iam_member" "audio_bucket_admin" {
  bucket = google_storage_bucket.audio_files.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.mass_api.email}"
}

# IAM binding for models bucket
resource "google_storage_bucket_iam_member" "models_bucket_admin" {
  bucket = google_storage_bucket.ml_models.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.mass_api.email}"
}

# Outputs
output "audio_bucket_name" {
  description = "Audio files bucket name"
  value       = google_storage_bucket.audio_files.name
}

output "audio_bucket_url" {
  description = "Audio files bucket URL"
  value       = google_storage_bucket.audio_files.url
}

output "models_bucket_name" {
  description = "ML models bucket name"
  value       = google_storage_bucket.ml_models.name
}

output "models_bucket_url" {
  description = "ML models bucket URL"
  value       = google_storage_bucket.ml_models.url
}
