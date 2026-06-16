# Infrastructure (Terraform)

Provisions the GCP data plane. Remote state lives in `gs://governed-agentic-analytics-tfstate`.

## Resources
- **GCS** — `*-raw` (bronze landing zone, 90-day lifecycle) and `*-artifacts` (dbt docs/build).
- **BigQuery** — medallion datasets `raw` / `staging` / `marts`.
- **Service accounts** — `ingestion` (write), `agent` (read-only), `ci` (dbt/CD), least-privilege IAM.
- **Artifact Registry** — Docker repo `containers` for Cloud Run images.

## Usage
```bash
gcloud auth application-default login   # one-time: ADC for the Terraform provider
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```
