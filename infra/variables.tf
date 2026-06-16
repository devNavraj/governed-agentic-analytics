variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  description = "Default GCP region for regional resources (Cloud Run, Artifact Registry)."
  default     = "australia-southeast1"
}

variable "location" {
  type        = string
  description = "Location for BigQuery datasets and GCS buckets."
  default     = "australia-southeast1"
}
