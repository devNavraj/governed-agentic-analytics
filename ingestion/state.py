"""Incremental cursor state, persisted as small JSON objects in the raw bucket."""

from __future__ import annotations

from datetime import UTC, datetime

import google.cloud.storage as storage
from pydantic import BaseModel


class ConnectorState(BaseModel):
    cursor: str | None = None
    last_batch_id: str | None = None
    last_row_count: int = 0
    updated_at: str | None = None


def _state_blob(bucket: str, key: str) -> storage.Blob:
    client = storage.Client()
    return client.bucket(bucket).blob(f"_state/{key}.json")


def load_state(bucket: str, key: str) -> ConnectorState:
    blob = _state_blob(bucket, key)
    if not blob.exists():
        return ConnectorState()
    return ConnectorState.model_validate_json(blob.download_as_bytes())


def save_state(bucket: str, key: str, state: ConnectorState) -> None:
    state.updated_at = datetime.now(UTC).isoformat()
    blob = _state_blob(bucket, key)
    blob.upload_from_string(state.model_dump_json(indent=2), content_type="application/json")
