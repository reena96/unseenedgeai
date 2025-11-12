# Cloud Tasks and Pub/Sub Configuration

# ============================================
# CLOUD TASKS QUEUES
# ============================================

# Transcription jobs queue
resource "google_cloud_tasks_queue" "transcription_jobs" {
  name     = "transcription-jobs"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = var.transcription_queue_concurrency
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts       = 5
    max_retry_duration = "3600s" # 1 hour
    min_backoff        = "10s"
    max_backoff        = "300s"
    max_doublings      = 3
  }

  depends_on = [google_project_service.required_apis]
}

# ML inference jobs queue
resource "google_cloud_tasks_queue" "inference_jobs" {
  name     = "inference-jobs"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = var.inference_queue_concurrency
    max_dispatches_per_second = 10
  }

  retry_config {
    max_attempts       = 3
    max_retry_duration = "1800s" # 30 minutes
    min_backoff        = "5s"
    max_backoff        = "120s"
    max_doublings      = 3
  }

  depends_on = [google_project_service.required_apis]
}

# ============================================
# PUB/SUB TOPICS
# ============================================

# Audio uploaded topic
resource "google_pubsub_topic" "audio_uploaded" {
  name = "audio-uploaded"

  message_retention_duration = "86400s" # 24 hours

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# Transcription completed topic
resource "google_pubsub_topic" "transcription_completed" {
  name = "transcription-completed"

  message_retention_duration = "86400s"

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# Features extracted topic
resource "google_pubsub_topic" "features_extracted" {
  name = "features-extracted"

  message_retention_duration = "86400s"

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# Skills inferred topic
resource "google_pubsub_topic" "skills_inferred" {
  name = "skills-inferred"

  message_retention_duration = "86400s"

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# ============================================
# PUB/SUB SUBSCRIPTIONS
# ============================================

# Audio uploaded subscription
resource "google_pubsub_subscription" "audio_uploaded_sub" {
  name  = "audio-uploaded-sub"
  topic = google_pubsub_topic.audio_uploaded.name

  ack_deadline_seconds = 60

  message_retention_duration = "86400s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "" # Never expire
  }

  labels = local.common_labels
}

# Transcription completed subscription
resource "google_pubsub_subscription" "transcription_completed_sub" {
  name  = "transcription-completed-sub"
  topic = google_pubsub_topic.transcription_completed.name

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = ""
  }

  labels = local.common_labels
}

# Features extracted subscription
resource "google_pubsub_subscription" "features_extracted_sub" {
  name  = "features-extracted-sub"
  topic = google_pubsub_topic.features_extracted.name

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = ""
  }

  labels = local.common_labels
}

# Skills inferred subscription
resource "google_pubsub_subscription" "skills_inferred_sub" {
  name  = "skills-inferred-sub"
  topic = google_pubsub_topic.skills_inferred.name

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = ""
  }

  labels = local.common_labels
}

# ============================================
# OUTPUTS
# ============================================

output "transcription_queue_name" {
  description = "Transcription jobs queue name"
  value       = google_cloud_tasks_queue.transcription_jobs.name
}

output "inference_queue_name" {
  description = "Inference jobs queue name"
  value       = google_cloud_tasks_queue.inference_jobs.name
}

output "pubsub_topics" {
  description = "Pub/Sub topic names"
  value = {
    audio_uploaded          = google_pubsub_topic.audio_uploaded.name
    transcription_completed = google_pubsub_topic.transcription_completed.name
    features_extracted      = google_pubsub_topic.features_extracted.name
    skills_inferred         = google_pubsub_topic.skills_inferred.name
  }
}
