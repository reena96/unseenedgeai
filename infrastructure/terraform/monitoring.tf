# Monitoring and Alerting Configuration

# ============================================
# NOTIFICATION CHANNEL
# ============================================

# Email notification channel (if email provided)
resource "google_monitoring_notification_channel" "email" {
  count = var.alert_email != "" ? 1 : 0

  display_name = "Email Alerts"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }

  depends_on = [google_project_service.required_apis]
}

# ============================================
# ALERT POLICIES
# ============================================

# Database connection failures
resource "google_monitoring_alert_policy" "db_connection_failures" {
  display_name = "Cloud SQL Connection Failures"
  combiner     = "OR"

  conditions {
    display_name = "High connection count"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND metric.type = \"cloudsql.googleapis.com/database/network/connections\""
      duration        = "300s" # 5 minutes
      comparison      = "COMPARISON_GT"
      threshold_value = 80

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud SQL is experiencing high connection count. Check database health and connectivity."
    mime_type = "text/markdown"
  }
}

# High CPU usage on Cloud SQL
resource "google_monitoring_alert_policy" "db_high_cpu" {
  display_name = "Cloud SQL High CPU Usage"
  combiner     = "OR"

  conditions {
    display_name = "CPU usage above 80%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND metric.type = \"cloudsql.googleapis.com/database/cpu/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8 # 80%

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud SQL CPU usage is above 80%. Consider scaling up the instance tier."
    mime_type = "text/markdown"
  }
}

# High memory usage on Cloud SQL
resource "google_monitoring_alert_policy" "db_high_memory" {
  display_name = "Cloud SQL High Memory Usage"
  combiner     = "OR"

  conditions {
    display_name = "Memory usage above 90%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND metric.type = \"cloudsql.googleapis.com/database/memory/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.9 # 90%

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud SQL memory usage is above 90%. Consider scaling up the instance tier."
    mime_type = "text/markdown"
  }
}

# Cloud Run error rate
resource "google_monitoring_alert_policy" "cloud_run_errors" {
  display_name = "Cloud Run High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate above 5%"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.label.response_code_class != \"2xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05 # 5%

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.service_name"]
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud Run service is experiencing high error rates (>5%). Check application logs."
    mime_type = "text/markdown"
  }
}

# Cloud Tasks queue depth
resource "google_monitoring_alert_policy" "tasks_queue_depth" {
  display_name = "Cloud Tasks High Queue Depth"
  combiner     = "OR"

  conditions {
    display_name = "Queue depth above 100 tasks"

    condition_threshold {
      filter          = "resource.type = \"cloud_tasks_queue\" AND metric.type = \"cloudtasks.googleapis.com/queue/depth\""
      duration        = "600s" # 10 minutes
      comparison      = "COMPARISON_GT"
      threshold_value = 100

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud Tasks queue has more than 100 pending tasks. Workers may be overwhelmed or failing."
    mime_type = "text/markdown"
  }
}

# Storage quota warning
resource "google_monitoring_alert_policy" "storage_quota" {
  display_name = "Cloud Storage High Usage"
  combiner     = "OR"

  conditions {
    display_name = "Bucket size above 80% of expected"

    condition_threshold {
      filter          = "resource.type = \"gcs_bucket\" AND metric.type = \"storage.googleapis.com/storage/total_bytes\""
      duration        = "3600s" # 1 hour
      comparison      = "COMPARISON_GT"
      threshold_value = 107374182400 # 100 GB

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].id] : []

  documentation {
    content   = "Cloud Storage bucket is approaching quota limits. Review lifecycle policies and data retention."
    mime_type = "text/markdown"
  }
}

# ============================================
# BUDGET ALERTS
# ============================================

# Monthly budget alert
resource "google_billing_budget" "monthly_budget" {
  billing_account = data.google_project.current.billing_account
  display_name    = "MASS Monthly Budget"

  budget_filter {
    projects = ["projects/${data.google_project.current.number}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_amount)
    }
  }

  threshold_rules {
    threshold_percent = 0.5 # Alert at 50%
  }

  threshold_rules {
    threshold_percent = 0.75 # Alert at 75%
  }

  threshold_rules {
    threshold_percent = 0.9 # Alert at 90%
  }

  threshold_rules {
    threshold_percent = 1.0 # Alert at 100%
  }

  threshold_rules {
    threshold_percent = 1.2 # Alert at 120%
    spend_basis       = "FORECASTED_SPEND"
  }

  depends_on = [google_project_service.required_apis]
}

# ============================================
# OUTPUTS
# ============================================

output "monitoring_configured" {
  description = "Monitoring and alerting configuration status"
  value       = var.alert_email != "" ? "Alerts will be sent to ${var.alert_email}" : "No alert email configured. Set var.alert_email to enable email notifications."
}

output "budget_amount" {
  description = "Monthly budget amount"
  value       = "$${var.budget_amount} USD"
}
