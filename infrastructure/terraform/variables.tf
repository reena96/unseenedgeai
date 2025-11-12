# Variables for MASS Infrastructure

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "unseenedgeai"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}
