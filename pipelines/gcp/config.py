
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GCPConfig:
    project_id: str
    bucket_name: str
    bigquery_dataset: str
    gcs_prefix: str = "nexus-m/processed"
    location: str = "US"

    @classmethod
    def from_env(cls) -> "GCPConfig":
        return cls(
            project_id=os.getenv("NEXUS_GCP_PROJECT_ID", "").strip(),
            bucket_name=os.getenv("NEXUS_GCP_BUCKET", "").strip(),
            bigquery_dataset=os.getenv(
                "NEXUS_BQ_DATASET", "nexus_m_analytics"
            ).strip(),
            gcs_prefix=os.getenv(
                "NEXUS_GCS_PREFIX", "nexus-m/processed"
            ).strip().strip("/"),
            location=os.getenv("NEXUS_GCP_LOCATION", "US").strip(),
        )

    def validate(self) -> None:
        if not self.project_id:
            raise ValueError(
                "Set NEXUS_GCP_PROJECT_ID before running the cloud pipeline."
            )

        if not self.bucket_name:
            raise ValueError(
                "Set NEXUS_GCP_BUCKET to an existing GCS bucket."
            )

        if not re.fullmatch(r"[a-z][a-z0-9_]{0,1023}", self.bigquery_dataset):
            raise ValueError(
                "NEXUS_BQ_DATASET must be a valid BigQuery dataset ID."
            )

        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,220}", self.bucket_name):
            raise ValueError("NEXUS_GCP_BUCKET has an invalid bucket name.")

        if not self.location:
            raise ValueError("NEXUS_GCP_LOCATION cannot be empty.")


def processed_dir() -> Path:
    """Return the local processed-data directory."""
    return PROJECT_ROOT / "data" / "processed"


def require_cloud_config() -> GCPConfig:
    config = GCPConfig.from_env()
    config.validate()
    return config
