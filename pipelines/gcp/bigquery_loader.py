
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from pipelines.gcp.config import require_cloud_config


def table_id_for_gcs_uri(gcs_uri: str) -> str:
    """Build a stable BigQuery table ID from a GCS object URI."""
    parsed = urlparse(gcs_uri)

    if parsed.scheme != "gs" or not parsed.netloc or not parsed.path:
        raise ValueError("Expected a valid gs://bucket/object URI.")

    object_path = parsed.path.lstrip("/")
    if not object_path:
        raise ValueError("GCS URI must include an object path.")

    # Include parent folder names to reduce same-filename collisions.
    table_base = re.sub(r"\.(csv|jsonl|ndjson)$", "", object_path, flags=re.I)
    table_id = re.sub(r"[^A-Za-z0-9_]", "_", table_base)

    if not table_id or not table_id[0].isalpha() and table_id[0] != "_":
        table_id = f"t_{table_id}"

    # BigQuery table IDs are limited to 1024 characters.
    return table_id[:1024]


def load_gcs_uri(
    gcs_uri: str,
    client: Any = None,
    project_id: str | None = None,
    dataset_id: str | None = None,
    location: str | None = None,
) -> dict[str, Any]:
    """
    Load a GCS CSV or newline-delimited JSON file into BigQuery.

    The destination table is replaced on each successful load, making
    reruns deterministic. Do not use this write mode for tables that
    must preserve historical append-only records.
    """
    config = require_cloud_config()
    project = project_id or config.project_id
    dataset = dataset_id or config.bigquery_dataset
    region = location or config.location

    suffix = gcs_uri.rsplit("/", 1)[-1].lower()

    if suffix.endswith(".csv"):
        source_format_name = "CSV"
    elif suffix.endswith((".jsonl", ".ndjson")):
        source_format_name = "NEWLINE_DELIMITED_JSON"
    else:
        return {
            "status": "skipped",
            "gcs_uri": gcs_uri,
            "reason": (
                "Only CSV and newline-delimited JSON (.jsonl/.ndjson) "
                "are loaded automatically. Convert regular JSON to NDJSON "
                "before loading."
            ),
        }

    if client is None:
        from google.cloud import bigquery

        client = bigquery.Client(project=project)

    table_id = table_id_for_gcs_uri(gcs_uri)
    destination = f"{project}.{dataset}.{table_id}"

    # Create the dataset if it does not exist.
    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    dataset_ref = bigquery.Dataset(f"{project}.{dataset}")
    dataset_ref.location = region

    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        client.create_dataset(dataset_ref, exists_ok=True)

    job_config = bigquery.LoadJobConfig(
        source_format=(
            bigquery.SourceFormat.CSV
            if source_format_name == "CSV"
            else bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        ),
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    if source_format_name == "CSV":
        job_config.skip_leading_rows = 1

    job = client.load_table_from_uri(
        gcs_uri,
        destination,
        job_config=job_config,
        location=region,
    )
    job.result()

    table = client.get_table(destination)

    return {
        "status": "ok",
        "gcs_uri": gcs_uri,
        "destination_table": destination,
        "source_format": source_format_name,
        "rows_loaded": getattr(job, "output_rows", None),
        "table_num_rows": getattr(table, "num_rows", None),
    }


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Load a GCS CSV or NDJSON object into BigQuery."
    )
    parser.add_argument("gcs_uri", help="Source URI, e.g. gs://bucket/file.csv")
    args = parser.parse_args()

    result = load_gcs_uri(args.gcs_uri)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
