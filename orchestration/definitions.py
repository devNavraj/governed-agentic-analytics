"""Dagster orchestration: one materializable asset per registered connector.

Assets are generated from ``ingestion.connectors.REGISTRY``, so every connector
added in later phases automatically gets an orchestrated, scheduled asset with
lineage and run metadata in the Dagster UI.

Note: this module intentionally does NOT use ``from __future__ import annotations`` --
Dagster inspects the ``context`` parameter annotation at runtime.
"""

from dagster import (
    AssetExecutionContext,
    Definitions,
    MaterializeResult,
    MetadataValue,
    ScheduleDefinition,
    asset,
    define_asset_job,
)
from ingestion.connectors import REGISTRY
from ingestion.connectors.base import Connector
from ingestion.run import run_connector


def _build_ingestion_asset(name: str, connector_cls: type[Connector]):
    asset_name = "raw_" + name.replace("-", "_")
    instance = connector_cls()
    description = f"Incremental ingestion of {instance.source}.{instance.table} into BigQuery raw."

    @asset(
        name=asset_name,
        group_name="ingestion",
        description=description,
        compute_kind="python",
    )
    def _ingest(context: AssetExecutionContext) -> MaterializeResult:
        result = run_connector(connector_cls())
        context.log.info("%s -> %d rows (cursor=%s)", asset_name, result.row_count, result.cursor)
        return MaterializeResult(
            metadata={
                "row_count": result.row_count,
                "cursor": result.cursor or "n/a",
                "batch_id": result.batch_id,
                "gcs_uri": MetadataValue.text(result.gcs_uri or "n/a"),
                "table": f"raw.{result.source}__{result.table}",
            }
        )

    return _ingest


ingestion_assets = [_build_ingestion_asset(name, cls) for name, cls in REGISTRY.items()]

ingestion_job = define_asset_job(name="ingestion_job", selection="*")

ingestion_schedule = ScheduleDefinition(
    name="ingestion_every_15min",
    job=ingestion_job,
    cron_schedule="*/15 * * * *",
    execution_timezone="Australia/Sydney",
)

defs = Definitions(
    assets=ingestion_assets,
    jobs=[ingestion_job],
    schedules=[ingestion_schedule],
)
