output "raw_bucket" {
  description = "GCS landing/bronze bucket."
  value       = google_storage_bucket.raw.name
}

output "artifacts_bucket" {
  description = "GCS bucket for build/docs artifacts."
  value       = google_storage_bucket.artifacts.name
}

output "bigquery_datasets" {
  description = "BigQuery medallion datasets."
  value       = [for d in google_bigquery_dataset.datasets : d.dataset_id]
}

output "service_account_emails" {
  description = "Service account emails by role."
  value = {
    ingestion = google_service_account.ingestion.email
    agent     = google_service_account.agent.email
    ci        = google_service_account.ci.email
  }
}

output "artifact_registry" {
  description = "Artifact Registry Docker repository path."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
}
