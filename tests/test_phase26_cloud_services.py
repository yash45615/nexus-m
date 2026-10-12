
from __future__ import annotations

import pytest

from pipelines.gcp import cloud_services as cloud


@pytest.fixture
def cloud_env(monkeypatch):
    monkeypatch.setenv("NEXUS_GCP_PROJECT_ID", "nexus-test-project")
    monkeypatch.setenv("NEXUS_GCP_REGION", "us-central1")
    monkeypatch.setenv("NEXUS_VERTEX_MODEL", "gemini-2.5-flash")


def test_required_environment_variable_is_checked(monkeypatch):
    monkeypatch.delenv("NEXUS_GCP_PROJECT_ID", raising=False)

    with pytest.raises(ValueError, match="NEXUS_GCP_PROJECT_ID"):
        cloud._cloud_project()


def test_dataproc_rejects_non_gcs_entry_point(cloud_env):
    with pytest.raises(ValueError, match="gs://"):
        cloud.submit_dataproc_pyspark(
            "https://example.com/job.py"
        )


def test_dataproc_rejects_invalid_batch_id(cloud_env):
    with pytest.raises(ValueError, match="batch_id"):
        cloud.submit_dataproc_pyspark(
            "gs://nexus-bucket/jobs/job.py",
            batch_id="INVALID BATCH",
        )


def test_dataflow_rejects_non_gcs_template(cloud_env):
    with pytest.raises(ValueError, match="gs://"):
        cloud.launch_dataflow_template(
            "https://example.com/template"
        )


def test_cloud_run_rejects_http_url():
    with pytest.raises(ValueError, match="https://"):
        cloud.invoke_cloud_run(
            "http://localhost:8080",
            {"question": "Show KPIs"},
        )


def test_cloud_run_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="1 to 300"):
        cloud.invoke_cloud_run(
            "https://example.run.app",
            {},
            timeout_seconds=500,
        )


def test_vertex_ai_rejects_empty_prompt(cloud_env):
    with pytest.raises(ValueError, match="non-empty"):
        cloud.call_vertex_ai("   ")


def test_vertex_ai_rejects_invalid_temperature(cloud_env):
    with pytest.raises(ValueError, match="temperature"):
        cloud.call_vertex_ai(
            "Summarize payment performance",
            temperature=2.0,
        )


def test_vertex_ai_rejects_oversized_prompt(cloud_env):
    with pytest.raises(ValueError, match="30000"):
        cloud.call_vertex_ai("x" * 30001)


def test_vertex_ai_rejects_invalid_token_limit(cloud_env):
    with pytest.raises(ValueError, match="max_output_tokens"):
        cloud.call_vertex_ai(
            "Summarize payment performance",
            max_output_tokens=0,
        )


def test_vertex_ai_rejects_invalid_model_id(cloud_env):
    with pytest.raises(ValueError, match="model"):
        cloud.call_vertex_ai(
            "Summarize payment performance",
            model="INVALID MODEL NAME",
        )


def test_cloud_run_rejects_non_dictionary_payload():
    with pytest.raises(ValueError, match="dictionary"):
        cloud.invoke_cloud_run(
            "https://example.run.app",
            ["not", "a", "dictionary"],
        )
