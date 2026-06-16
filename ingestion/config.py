"""Runtime configuration loaded from environment (.env)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gcp_project_id: str = "governed-agentic-analytics"
    gcp_location: str = "australia-southeast1"
    bq_dataset_raw: str = "raw"
    gcs_raw_bucket: str = "governed-agentic-analytics-raw"

    @property
    def resolved_raw_bucket(self) -> str:
        return self.gcs_raw_bucket or f"{self.gcp_project_id}-raw"


settings = Settings()
