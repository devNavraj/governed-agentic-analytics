# Orchestration (Dagster)

One materializable asset per connector in `ingestion.connectors.REGISTRY`, plus a job and
a 15-minute schedule (Australia/Sydney). Assets run the connector end-to-end
(fetch -> GCS bronze -> BigQuery raw) and surface row counts, cursor, and the GCS URI as
run metadata.

## Run locally
```bash
uv sync --group orchestration
uv run dagster dev -m orchestration.definitions          # UI at http://localhost:3000
uv run dagster asset materialize -m orchestration.definitions --select "*"   # one-off run
```

## Deployment (later phase)
Packaged as a Cloud Run job triggered by Cloud Scheduler on the same cadence; the schedule
above documents the intended interval.
