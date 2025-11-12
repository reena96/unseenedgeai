# MASS System Infrastructure - Main Terraform Configuration
# This file sets up the core GCP infrastructure for the MASS system

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Store Terraform state in GCS bucket (created manually first)
  # Uncomment after creating the bucket
  # backend "gcs" {
  #   bucket = "unseenedgeai-terraform-state"
  #   prefix = "terraform/state"
  # }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required Google Cloud APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",              # Cloud Run
    "sqladmin.googleapis.com",         # Cloud SQL
    "storage.googleapis.com",          # Cloud Storage
    "cloudtasks.googleapis.com",       # Cloud Tasks
    "pubsub.googleapis.com",           # Pub/Sub
    "speech.googleapis.com",           # Speech-to-Text
    "secretmanager.googleapis.com",    # Secret Manager
    "logging.googleapis.com",          # Cloud Logging
    "monitoring.googleapis.com",       # Cloud Monitoring
    "cloudbuild.googleapis.com",       # Cloud Build
    "artifactregistry.googleapis.com", # Artifact Registry
  ])

  service            = each.key
  disable_on_destroy = false

  # Prevent accidental API disabling
  lifecycle {
    prevent_destroy = false
  }
}

# Local variables for resource naming
locals {
  environment = var.environment

  # Resource naming convention: [project]-[resource]-[environment]
  db_instance_name = "${var.project_id}-db-${local.environment}"
  audio_bucket     = "${var.project_id}-audio-files"
  models_bucket    = "${var.project_id}-ml-models"
  service_account  = "${var.project_id}-api@${var.project_id}.iam.gserviceaccount.com"

  # Common labels for all resources
  common_labels = {
    project     = "mass"
    environment = local.environment
    managed_by  = "terraform"
  }
}

# Data source for current project
data "google_project" "current" {
  project_id = var.project_id
}

# Outputs for use by other modules or scripts
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = local.environment
}
