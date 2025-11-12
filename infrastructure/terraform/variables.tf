# Terraform Variables for MASS Infrastructure

# ============================================
# CORE PROJECT SETTINGS
# ============================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "unseenedgeai"
}

variable "region" {
  description = "GCP Region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

# ============================================
# DATABASE SETTINGS
# ============================================

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "mass_db"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-7680" # 2 vCPU, 7.5GB RAM
}

variable "db_backup_time" {
  description = "Time for automated backups (UTC, HH:MM format)"
  type        = string
  default     = "03:00"
}

variable "db_maintenance_window" {
  description = "Day and hour for database maintenance (UTC)"
  type = object({
    day  = number # 1-7 (1=Monday, 7=Sunday)
    hour = number # 0-23
  })
  default = {
    day  = 7 # Sunday
    hour = 4 # 4 AM UTC
  }
}

# ============================================
# CLOUD RUN SETTINGS
# ============================================

variable "api_service_name" {
  description = "Cloud Run service name for API"
  type        = string
  default     = "mass-api"
}

variable "api_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0 # Scale to zero for cost savings
}

variable "api_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10 # Phase 1 limit
}

variable "api_memory" {
  description = "Memory allocation for Cloud Run instances"
  type        = string
  default     = "2Gi"
}

variable "api_cpu" {
  description = "CPU allocation for Cloud Run instances"
  type        = string
  default     = "2"
}

variable "api_timeout" {
  description = "Request timeout for Cloud Run (seconds)"
  type        = number
  default     = 300 # 5 minutes
}

# ============================================
# STORAGE SETTINGS
# ============================================

variable "audio_retention_days" {
  description = "Days to retain audio files before deletion"
  type        = number
  default     = 30
}

variable "enable_storage_versioning" {
  description = "Enable object versioning for buckets"
  type        = bool
  default     = true
}

# ============================================
# TASK QUEUE SETTINGS
# ============================================

variable "transcription_queue_concurrency" {
  description = "Max concurrent transcription jobs"
  type        = number
  default     = 10
}

variable "inference_queue_concurrency" {
  description = "Max concurrent ML inference jobs"
  type        = number
  default     = 20
}

# ============================================
# MONITORING & ALERTING
# ============================================

variable "alert_email" {
  description = "Email for GCP monitoring alerts"
  type        = string
  default     = "" # Will prompt user to fill
}

variable "budget_amount" {
  description = "Monthly budget in USD for cost alerts"
  type        = number
  default     = 1000
}

# ============================================
# SECURITY SETTINGS
# ============================================

variable "allowed_cors_origins" {
  description = "CORS allowed origins for API"
  type        = list(string)
  default     = ["http://localhost:3000"] # Add production URLs later
}

variable "enable_audit_logging" {
  description = "Enable audit logging for all resources"
  type        = bool
  default     = true
}

# ============================================
# FEATURE FLAGS
# ============================================

variable "enable_high_availability" {
  description = "Enable HA mode for Cloud SQL"
  type        = bool
  default     = true # Recommended for production
}

variable "enable_point_in_time_recovery" {
  description = "Enable PITR for Cloud SQL"
  type        = bool
  default     = true
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = true # Prevent accidental deletion
}
