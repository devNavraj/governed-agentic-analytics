"""Connector registry: maps CLI names to connector classes."""

from ingestion.connectors.aemo import AemoNemSummaryConnector
from ingestion.connectors.base import Connector

REGISTRY: dict[str, type[Connector]] = {
    "aemo-nem-summary": AemoNemSummaryConnector,
}
