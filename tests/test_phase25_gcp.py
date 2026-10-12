
from __future__ import annotations

from pathlib import Path

import pytest

from pipelines.gcp import bigquery_loader, config, gcs_uploader


@pytest.fixture
def cloud_env(monkeypatch):
    monkeypatch.setenv("NEXUS_GCP_PROJECT_ID", "nexus-test-project")
    monkeypatch.setenv("NEXUS_GCP_BUCKET", "nexus-test-bucket")
    monkeypatch.setenv("NEXUS_BQ_DATASET", "nexus_m_analytics")
    monkeypatch.setenv("NEXUS_GCP_LOCATION", "US")
    monkeypatch.setenv("NEXUS_GCS_PREFIX", "nexus-m/processed")


def test_config_loads_environment_variables(cloud_env):
    result = config.GCPConfig.from_env()

    result.validate()

    assert result.project_id == "nexus-test-project"
    assert result.bucket_name == "nexus-test-bucket"
    assert result.bigquery_dataset == "nexus_m_analytics"


def test_config_rejects_missing_project(monkeypatch):
    monkeypatch.delenv("NEXUS_GCP_PROJECT_ID", raising=False)
    monkeypatch.setenv("NEXUS_GCP_BUCKET", "nexus-test-bucket")

    with pytest.raises(ValueError, match="NEXUS_GCP_PROJECT_ID"):
        config.GCPConfig.from_env().validate()


def test_discover_processed_files_filters_extensions(tmp_path):
    (tmp_path / "summary.csv").write_text("a,b\n1,2\n")
    (tmp_path / "summary.json").write_text('{"count": 1}')
    (tmp_path / "summary.txt").write_text("not supported")

    files = gcs_uploader.discover_processed_files(tmp_path)

    assert [path.name for path in files] == [
        "summary.csv",
        "summary.json",
    ]


def test_missing_processed_directory_returns_no_data(
    tmp_path,
    cloud_env,
):
    result = gcs_uploader.upload_processed_files(
        root=tmp_path / "missing",
    )

    assert result["status"] == "no_data"
    assert result["uploaded"] == []


def test_gcs_object_name_preserves_relative_path(tmp_path):
    root = tmp_path / "processed"
    file_path = root / "phase4" / "summary.csv"

    result = gcs_uploader._relative_object_name(
        file_path,
        root,
        "nexus-m/processed",
    )

    assert result == "nexus-m/processed/phase4/summary.csv"


def test_upload_uses_fake_storage_client(
    tmp_path,
    cloud_env,
):
    root = tmp_path / "processed"
    root.mkdir()
    source = root / "summary.csv"
    source.write_text("metric,value\ncount,10\n", encoding="utf-8")

    class FakeBlob:
        def __init__(self, name):
            self.name = name
            self.uploaded_path = None

        def upload_from_filename(self, filename):
            self.uploaded_path = filename

    class FakeBucket:
        def __init__(self):
            self.blobs = []

        def blob(self, name):
            blob = FakeBlob(name)
            self.blobs.append(blob)
            return blob

    class FakeStorageClient:
        def __init__(self):
            self.fake_bucket = FakeBucket()

        def bucket(self, name):
            assert name == "nexus-test-bucket"
            return self.fake_bucket

    client = FakeStorageClient()
    result = gcs_uploader.upload_processed_files(
        root=root,
        client=client,
    )

    assert result["status"] == "ok"
    assert result["uploaded_count"] == 1
    assert result["uploaded"][0]["gcs_uri"].endswith(
        "/nexus-m/processed/summary.csv"
    )
    assert client.fake_bucket.blobs[0].uploaded_path == str(source)


def test_table_id_is_stable_and_sanitized():
    first = bigquery_loader.table_id_for_gcs_uri(
        "gs://nexus-test-bucket/phase4/partner-performance.csv"
    )
    second = bigquery_loader.table_id_for_gcs_uri(
        "gs://nexus-test-bucket/phase4/partner-performance.csv"
    )

    assert first == second
    assert first == "phase4_partner_performance"


def test_table_id_rejects_invalid_uri():
    with pytest.raises(ValueError):
        bigquery_loader.table_id_for_gcs_uri(
            "https://example.com/data.csv"
        )


def test_regular_json_is_skipped(
    cloud_env,
):
    result = bigquery_loader.load_gcs_uri(
        "gs://nexus-test-bucket/phase4/kpi_summary.json",
        client=object(),
    )

    assert result["status"] == "skipped"
    assert "NDJSON" in result["reason"]


def test_bigquery_loader_uses_fake_client(
    cloud_env,
):
    from google.cloud import bigquery

    class FakeJob:
        output_rows = 12

        def result(self):
            return None

    class FakeTable:
        num_rows = 12

    class FakeBigQueryClient:
        def __init__(self):
            self.loaded_uri = None
            self.destination = None
            self.job_config = None

        def get_dataset(self, dataset_ref):
            return dataset_ref

        def load_table_from_uri(
            self,
            uri,
            destination,
            job_config,
            location,
        ):
            self.loaded_uri = uri
            self.destination = destination
            self.job_config = job_config
            return FakeJob()

        def get_table(self, destination):
            return FakeTable()

    client = FakeBigQueryClient()

    result = bigquery_loader.load_gcs_uri(
        "gs://nexus-test-bucket/phase4/partner_performance.csv",
        client=client,
    )

    assert result["status"] == "ok"
    assert result["rows_loaded"] == 12
    assert result["table_num_rows"] == 12
    assert client.job_config.source_format == bigquery.SourceFormat.CSV
    assert client.job_config.skip_leading_rows == 1
    assert (
        client.destination
        == "nexus-test-project.nexus_m_analytics.phase4_partner_performance"
    )
