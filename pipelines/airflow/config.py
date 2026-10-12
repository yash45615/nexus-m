from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"

LOG_DIR = PROJECT_ROOT / "logs"

PIPELINE_NAME = "nexus_m_analytical_pipeline"

PIPELINE_VERSION = "1.0.0"


def ensure_pipeline_directories() -> None:
    """
    Create directories required by the orchestration layer.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SYNTHETIC_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )