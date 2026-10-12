
from __future__ import annotations

import json
from typing import Any

from pipelines.gcp.bigquery_loader import load_gcs_uri
from pipelines.gcp.gcs_uploader import upload_processed_files


def run_cloud_pipeline() -> dict[str, Any]:
    """Upload processed files, then load supported formats into BigQuery."""
    upload_result = upload_processed_files()

    if upload_result["status"] in {"no_data", "error"}:
        return {
            "status": upload_result["status"],
            "upload": upload_result,
            "loads": [],
            "message": "No BigQuery loads were attempted.",
        }

    loads: list[dict[str, Any]] = []

    for item in upload_result.get("uploaded", []):
        uri = item["gcs_uri"]
        lower_uri = uri.lower()

        if lower_uri.endswith(".csv") or lower_uri.endswith(
            (".jsonl", ".ndjson")
        ):
            try:
                loads.append(load_gcs_uri(uri))
            except Exception as exc:
                loads.append(
                    {
                        "status": "error",
                        "gcs_uri": uri,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        else:
            loads.append(
                {
                    "status": "skipped",
                    "gcs_uri": uri,
                    "reason": (
                        "Uploaded to GCS; not loaded into BigQuery because "
                        "the file is not CSV or newline-delimited JSON."
                    ),
                }
            )

    load_errors = [
        item for item in loads if item.get("status") == "error"
    ]
    status = (
        "error" if not upload_result.get("uploaded") and upload_result.get("errors")
        else "partial" if upload_result.get("errors") or load_errors
        else "ok"
    )

    return {
        "status": status,
        "upload": upload_result,
        "loads": loads,
        "load_count": sum(item.get("status") == "ok" for item in loads),
        "load_error_count": len(load_errors),
    }


def main() -> None:
    result = run_cloud_pipeline()
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
