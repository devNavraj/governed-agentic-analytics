"""CLI: run a connector end-to-end (fetch -> land in GCS -> load to BigQuery -> save cursor)."""

from __future__ import annotations

import argparse
import logging
import uuid
from datetime import UTC, datetime

from ingestion.config import settings
from ingestion.connectors import REGISTRY
from ingestion.connectors.base import Connector, ConnectorResult
from ingestion.state import ConnectorState, load_state, save_state
from ingestion.storage import load_gcs_to_bigquery, write_ndjson_to_gcs

logger = logging.getLogger("ingestion")


def _add_metadata(records: list[dict], source: str, batch_id: str) -> list[dict]:
    ingested_at = datetime.now(UTC).isoformat()
    return [
        {**record, "_source": source, "_batch_id": batch_id, "_ingested_at": ingested_at}
        for record in records
    ]


def run_connector(connector: Connector) -> ConnectorResult:
    bucket = settings.resolved_raw_bucket
    state_key = connector.dataset_table
    state = load_state(bucket, state_key)
    logger.info("starting %s (cursor=%s)", state_key, state.cursor)

    fetched = list(connector.fetch(state.cursor))
    new_records = connector.select_new(fetched, state.cursor)
    batch_id = uuid.uuid4().hex

    if not new_records:
        logger.info("no new records for %s", state_key)
        return ConnectorResult(
            source=connector.source,
            table=connector.table,
            row_count=0,
            batch_id=batch_id,
            cursor=state.cursor,
        )

    enriched = _add_metadata(new_records, connector.source, batch_id)
    gcs_uri = write_ndjson_to_gcs(enriched, bucket, connector.source, connector.table, batch_id)
    load_gcs_to_bigquery(
        gcs_uri, settings.gcp_project_id, settings.bq_dataset_raw, connector.dataset_table
    )

    new_cursor = connector.extract_cursor(new_records) or state.cursor
    save_state(
        bucket,
        state_key,
        ConnectorState(cursor=new_cursor, last_batch_id=batch_id, last_row_count=len(new_records)),
    )
    logger.info("loaded %d rows for %s (cursor=%s)", len(new_records), state_key, new_cursor)
    return ConnectorResult(
        source=connector.source,
        table=connector.table,
        row_count=len(new_records),
        batch_id=batch_id,
        gcs_uri=gcs_uri,
        cursor=new_cursor,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Run an ingestion connector.")
    parser.add_argument("connector", choices=sorted(REGISTRY), help="connector name")
    args = parser.parse_args()
    connector = REGISTRY[args.connector]()
    result = run_connector(connector)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
