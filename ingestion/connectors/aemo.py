"""AEMO NEM summary connector: 5-minute settlement prices & demand by region."""

from __future__ import annotations

from collections.abc import Iterable

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ingestion.connectors.base import Connector

AEMO_NEM_SUMMARY_URL = "https://visualisations.aemo.com.au/aemo/apps/api/report/ELEC_NEM_SUMMARY"


class AemoNemSummaryConnector(Connector):
    """Current NEM summary (one record per region per 5-minute settlement interval)."""

    source = "aemo"
    table = "nem_summary"
    cursor_field = "SETTLEMENTDATE"

    def __init__(self, url: str = AEMO_NEM_SUMMARY_URL, timeout: float = 30.0) -> None:
        self.url = url
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _get(self) -> dict:
        headers = {
            "User-Agent": "gaa-ingestion/0.1 (+https://github.com/devNavraj)",
            "Accept": "application/json",
        }
        resp = httpx.get(self.url, headers=headers, timeout=self.timeout, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()

    def fetch(self, since: str | None) -> Iterable[dict]:
        payload = self._get()
        yield from payload.get("ELEC_NEM_SUMMARY", [])
