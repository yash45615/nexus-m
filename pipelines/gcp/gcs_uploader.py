
from __future__ import annotations

from pathlib import Path
from typing import Any

from pipelines.gcp.config import (
    processed_dir,
    require_cloud_config,
)


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson"}


def discover_processed_files(root: Path | None = None) -> list[Path]:
    """Find supported analytics files beneath data/processed."""
    base = root or processed_dir()

    if not base.exists():
        return []

    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _relative_object_name(path: Path, root: Path, prefix: str) -> str:
    relative = path.relative_to(root).as_posix()
    return f"{prefix}/{relative}" if prefix else relative


def upload_processed_files(
    root: Path | None = None,
    client: Any = None,
    bucket_name: str | None = None,
    prefix: str | None = None,
) -> dict[str, Any]:
    """
    Upload processed artifacts to an existing GCS bucket.

    Pass a client explicitly in tests. In real use, Application Default
    Credentials are used by the Google Cloud SDK.
    """
    config = require_cloud_config()
    base = (root or processed_dir()).resolve()
    selected_bucket = bucket_name or config.bucket_name
    selected_prefix = (
        config.gcs_prefix if prefix is None else prefix.strip("/")
    )

    if not base.exists():
        return {
            "status": "no_data",
            "uploaded": [],
            "errors": [],
            "message": f"Processed-data directory not found: {base}",
        }

    files = discover_processed_files(base)

    if not files:
        return {
            "status": "no_data",
            "uploaded": [],
            "errors": [],
            "message": "No supported processed files were found.",
        }

    if client is None:
        from google.cloud import storage

        client = storage.Client(project=config.project_id)

    bucket = client.bucket(selected_bucket)
    uploaded: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for path in files:
        object_name = _relative_object_name(
            path, base, selected_prefix
        )

        try:
            blob = bucket.blob(object_name)
            blob.upload_from_filename(str(path))
            uploaded.append(
                {
                    "local_path": str(path),
                    "gcs_uri": f"gs://{selected_bucket}/{object_name}",
                }
            )
        except Exception as exc:
            errors.append(
                {
                    "local_path": str(path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    status = "ok" if not errors else (
        "partial" if uploaded else "error"
    )

    return {
        "status": status,
        "uploaded": uploaded,
        "errors": errors,
        "uploaded_count": len(uploaded),
        "error_count": len(errors),
    }


def main() -> None:
    import json

    result = upload_processed_files()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
