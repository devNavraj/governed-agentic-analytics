"""GCS landing (bronze) + BigQuery loading for the raw zone."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime

import google.cloud.bigquery as bigquery
import google.cloud.storage as storage


def _to_ndjson(records: list[dict]) -> bytes:
    buf = io.StringIO()
    for record in records:
        buf.write(json.dumps(record, default=str))
        buf.write("\n")
    return buf.getvalue().encode("utf-8")


def write_ndjson_to_gcs(
    records: list[dict], bucket: str, source: str, table: str, batch_id: str
) -> str:
    """Write records as newline-delimited JSON to the bronze landing zone."""
    client = storage.Client()
    dt = datetime.now(UTC).strftime("%Y-%m-%d")
    blob_path = f"{source}/{table}/dt={dt}/{batch_id}.jsonl"
    blob = client.bucket(bucket).blob(blob_path)
    blob.upload_from_string(_to_ndjson(records), content_type="application/x-ndjson")
    return f"gs://{bucket}/{blob_path}"


def load_gcs_to_bigquery(gcs_uri: str, project: str, dataset: str, table: str) -> int:
    """Append a GCS NDJSON file into a raw BigQuery table (schema autodetected)."""
    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
    )
    load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()
    return int(client.get_table(table_id).num_rows)
