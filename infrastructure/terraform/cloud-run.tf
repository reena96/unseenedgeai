# Cloud Run Service for MASS API
# This file defines the Cloud Run service that hosts the FastAPI application

# Note: This configuration assumes a Docker image has already been built and pushed
# to Artifact Registry. The initial deployment should be done manually via:
# 1. Build image: docker build -t gcr.io/unseenedgeai/mass-api:latest backend/
# 2. Push image: docker push gcr.io/unseenedgeai/mass-api:latest
# 3. Apply terraform: terraform apply

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "mass_api" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = "mass-api"
  description   = "Docker repository for MASS API images"
  format        = "DOCKER"

  labels = local.common_labels
}

# Cloud Run service for API
resource "google_cloud_run_v2_service" "mass_api" {
  provider = google-beta
  project  = var.project_id
  location = var.region
  name     = var.api_service_name

  template {
    # Scaling configuration
    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    # Service account with appropriate permissions
    service_account = google_service_account.mass_api.email

    # Container configuration
    containers {
      # Image will be updated via CI/CD after initial deployment
      # For initial deployment, use: gcloud run deploy mass-api --image gcr.io/unseenedgeai/mass-api:latest
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.mass_api.repository_id}/mass-api:latest"

      # Resource limits
      resources {
        limits = {
          cpu    = var.api_cpu
          memory = var.api_memory
        }

        cpu_idle = true # Scale to zero when not in use
        startup_cpu_boost = true
      }

      # Environment variables from Secret Manager
      env {
        name = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.app_secret_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "REDIS_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "AUDIO_BUCKET_NAME"
        value = google_storage_bucket.audio_files.name
      }

      env {
        name = "ARTIFACTS_BUCKET_NAME"
        value = google_storage_bucket.ml_models.name
      }

      # Health check configuration
      startup_probe {
        http_get {
          path = "/api/v1/health"
          port = 8080
        }
        initial_delay_seconds = 10
        timeout_seconds = 3
        period_seconds = 5
        failure_threshold = 3
      }

      liveness_probe {
        http_get {
          path = "/api/v1/liveness"
          port = 8080
        }
        initial_delay_seconds = 30
        timeout_seconds = 3
        period_seconds = 30
        failure_threshold = 3
      }

      # Container port
      ports {
        container_port = 8080
        name          = "http1"
      }
    }

    # Request timeout
    timeout = "${var.api_timeout}s"

    # Execution environment
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    # Session affinity for sticky sessions
    session_affinity = false
  }

  # Traffic configuration
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Lifecycle ignore changes for image (updated by CI/CD)
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  labels = local.common_labels

  depends_on = [
    google_project_service.required_apis,
    google_sql_database_instance.mass_db,
    google_artifact_registry_repository.mass_api,
  ]
}

# IAM policy to allow public access (adjust for production)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = google_cloud_run_v2_service.mass_api.project
  location = google_cloud_run_v2_service.mass_api.location
  name     = google_cloud_run_v2_service.mass_api.name
  role     = "roles/run.invoker"

  # Allow unauthenticated access for public endpoints
  # In production, consider using Cloud Armor or restricting to specific users
  member = "allUsers"
}

# Outputs
output "cloud_run_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.mass_api.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository for API images"
  value       = google_artifact_registry_repository.mass_api.name
}
