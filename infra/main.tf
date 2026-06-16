locals {
  labels = {
    project     = "gaa"
    environment = "dev"
    managed_by  = "terraform"
  }

  datasets = toset(["raw", "staging", "marts"])
}

# ---------------------------------------------------------------------------
# Storage: data lake landing zone (bronze) + build/docs artifacts
# ---------------------------------------------------------------------------
resource "google_storage_bucket" "raw" {
  name                        = "${var.project_id}-raw"
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = false
  labels                      = local.labels

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "artifacts" {
  name                        = "${var.project_id}-artifacts"
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = false
  labels                      = local.labels
}

# ---------------------------------------------------------------------------
# BigQuery: medallion datasets (raw -> staging -> marts)
# ---------------------------------------------------------------------------
resource "google_bigquery_dataset" "datasets" {
  for_each      = local.datasets
  dataset_id    = each.key
  friendly_name = each.key
  location      = var.location
  labels        = local.labels
}

# ---------------------------------------------------------------------------
# Service accounts (least privilege)
# ---------------------------------------------------------------------------
resource "google_service_account" "ingestion" {
  account_id   = "gaa-ingestion"
  display_name = "Ingestion connectors (writes raw + loads BigQuery)"
}

resource "google_service_account" "agent" {
  account_id   = "gaa-agent"
  display_name = "Agentic analytics service (read-only queries)"
}

resource "google_service_account" "ci" {
  account_id   = "gaa-ci"
  display_name = "CI/CD + dbt transformations"
}

# Ingestion: write to raw bucket, load + manage BigQuery data
resource "google_storage_bucket_iam_member" "ingestion_raw" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ingestion.email}"
}

resource "google_project_iam_member" "ingestion_bq_data" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.ingestion.email}"
}

resource "google_project_iam_member" "ingestion_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.ingestion.email}"
}

# Agent: read-only data access + run query jobs
resource "google_project_iam_member" "agent_bq_data" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

# CI/dbt: transform data + publish docs/artifacts
resource "google_project_iam_member" "ci_bq_data" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.ci.email}"
}

resource "google_project_iam_member" "ci_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.ci.email}"
}

resource "google_storage_bucket_iam_member" "ci_artifacts" {
  bucket = google_storage_bucket.artifacts.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ci.email}"
}

# ---------------------------------------------------------------------------
# Artifact Registry (container images for Cloud Run services)
# ---------------------------------------------------------------------------
resource "google_artifact_registry_repository" "containers" {
  repository_id = "containers"
  location      = var.region
  format        = "DOCKER"
  description   = "Container images for ingestion, agent, and orchestration services."
  labels        = local.labels
}
