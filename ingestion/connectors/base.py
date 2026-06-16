"""Connector framework: the source-agnostic contract every connector implements.

REST APIs (incremental via ``cursor_field``), batch files, and—later—streaming
sources all implement the same small interface, which keeps the platform extensible.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from pydantic import BaseModel


class ConnectorResult(BaseModel):
    """Outcome of a single connector run."""

    source: str
    table: str
    row_count: int
    batch_id: str
    gcs_uri: str | None = None
    cursor: str | None = None


class Connector(ABC):
    """A source connector. Subclasses implement :meth:`fetch`."""

    #: stable source-system name, e.g. ``"aemo"``
    source: str
    #: logical table name, e.g. ``"nem_summary"``
    table: str
    #: record field used as the incremental high-water mark; ``None`` = full snapshot
    cursor_field: str | None = None

    @property
    def dataset_table(self) -> str:
        """Fully-qualified raw table name, e.g. ``aemo__nem_summary``."""
        return f"{self.source}__{self.table}"

    @abstractmethod
    def fetch(self, since: str | None) -> Iterable[dict]:
        """Yield raw source records (ideally only those newer than ``since``)."""

    def select_new(self, records: list[dict], since: str | None) -> list[dict]:
        """Keep only records strictly after ``since`` so re-runs never duplicate."""
        if not self.cursor_field or since is None:
            return records
        return [r for r in records if str(r.get(self.cursor_field)) > since]

    def extract_cursor(self, records: list[dict]) -> str | None:
        """Return the new high-water mark from a batch of records."""
        if not self.cursor_field:
            return None
        values = [
            str(r[self.cursor_field]) for r in records if r.get(self.cursor_field) is not None
        ]
        return max(values) if values else None
