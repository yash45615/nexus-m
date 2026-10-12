from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from datetime import datetime

from pipelines.airflow.config import (
    PROCESSED_DATA_DIR,
    ensure_pipeline_directories,
)
from pipelines.airflow.tasks import run_full_analytics_pipeline


def main():
    print("=" * 70)
    print("NEXUS-M")
    print("AUTOMATED ANALYTICAL PIPELINE")
    print("=" * 70)

    ensure_pipeline_directories()

    started_at = datetime.now()

    try:
        result = run_full_analytics_pipeline()
        result["pipeline_status"] = "SUCCESS"

    except Exception as exc:
        result = {
            "pipeline": "NEXUS-M",
            "pipeline_status": "FAILED",
            "error": str(exc),
            "finished_at": datetime.now().isoformat(),
        }

        status_path = PROCESSED_DATA_DIR / "pipeline_status.json"

        status_path.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8",
        )

        raise

    result["started_at"] = started_at.isoformat()
    result["finished_at"] = datetime.now().isoformat()

    status_path = PROCESSED_DATA_DIR / "pipeline_status.json"

    status_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print()
    print(f"Status file: {status_path}")


if __name__ == "__main__":
    main()