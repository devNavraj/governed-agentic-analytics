"""Smoke test that the Dagster Definitions construct and validate."""

from __future__ import annotations

import pytest


def test_definitions_load() -> None:
    pytest.importorskip("dagster")
    from orchestration.definitions import defs, ingestion_assets, ingestion_schedule

    assert ingestion_schedule.cron_schedule == "*/15 * * * *"
    assert len(ingestion_assets) >= 1
    assert defs is not None
