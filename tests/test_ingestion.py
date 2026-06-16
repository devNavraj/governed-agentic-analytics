"""Unit tests for the connector framework (no network / no GCP)."""

from __future__ import annotations

from collections.abc import Iterable

from ingestion.connectors.base import Connector


class FakeIncremental(Connector):
    source = "fake"
    table = "events"
    cursor_field = "ts"

    def fetch(self, since: str | None) -> Iterable[dict]:
        return []


class FakeSnapshot(Connector):
    source = "fake"
    table = "snapshot"
    cursor_field = None

    def fetch(self, since: str | None) -> Iterable[dict]:
        return []


def test_dataset_table_name() -> None:
    assert FakeIncremental().dataset_table == "fake__events"


def test_select_new_is_strictly_after() -> None:
    connector = FakeIncremental()
    records = [{"ts": "2026-01-01"}, {"ts": "2026-01-02"}, {"ts": "2026-01-03"}]
    assert connector.select_new(records, "2026-01-02") == [{"ts": "2026-01-03"}]


def test_select_new_without_cursor_returns_all() -> None:
    connector = FakeIncremental()
    records = [{"ts": "2026-01-01"}, {"ts": "2026-01-02"}]
    assert connector.select_new(records, None) == records


def test_extract_cursor_returns_max() -> None:
    connector = FakeIncremental()
    records = [{"ts": "2026-01-01"}, {"ts": "2026-01-03"}, {"ts": "2026-01-02"}]
    assert connector.extract_cursor(records) == "2026-01-03"


def test_snapshot_connector_has_no_cursor() -> None:
    connector = FakeSnapshot()
    records = [{"a": 1}]
    assert connector.select_new(records, "anything") == records
    assert connector.extract_cursor(records) is None
