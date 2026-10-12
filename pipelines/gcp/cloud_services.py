
from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import quote


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Required environment variable is missing: {name}")
    return value


def _safe_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,62}", value):
        raise ValueError(f"{label} must be a valid lowercase identifier.")
    return value


def _cloud_project() -> str:
    return _required_env("NEXUS_GCP_PROJECT_ID")


def _region() -> str:
    return _required_env("NEXUS_GCP_REGION")


def _authorized_session() -> Any:
    """Create an authenticated HTTP session using Application Default Credentials."""
    import google.auth
    from google.auth.transport.requests import AuthorizedSession

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return AuthorizedSession(credentials)


def submit_dataproc_pyspark(
    main_python_file_uri: str,
    args: list[str] | None = None,
    batch_id: str = "nexus-m-pyspark",
    service_account: str | None = None,
) -> dict[str, Any]:
    """
    Submit a PySpark batch to Dataproc Serverless.

    The Python entry point must already be accessible from GCS.
    This function submits a job; it does not upload the source file.
    """
    if not main_python_file_uri.startswith("gs://"):
        raise ValueError("main_python_file_uri must start with gs://")

    project = _cloud_project()
    region = _region()
    _safe_identifier(batch_id, "batch_id")

    from google.cloud import dataproc_v1

    client = dataproc_v1.BatchControllerClient()
    parent = f"projects/{project}/locations/{region}"

    batch: dict[str, Any] = {
        "pyspark_batch": {
            "main_python_file_uri": main_python_file_uri,
            "args": args or [],
        }
    }

    if service_account:
        batch["environment_config"] = {
            "execution_config": {"service_account": service_account}
        }

    operation = client.create_batch(
        request={
            "parent": parent,
            "batch_id": batch_id,
            "batch": batch,
        }
    )

    return {
        "status": "submitted",
        "service": "dataproc",
        "project_id": project,
        "region": region,
        "batch_id": batch_id,
        "operation_name": getattr(operation, "operation", None),
        "message": "Dataproc batch submission was accepted.",
    }


def launch_dataflow_template(
    template_gcs_path: str,
    job_name: str = "nexus-m-dataflow",
    parameters: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Launch an existing Dataflow classic template stored in GCS.

    The template must already exist and its parameters must match the
    template's definition.
    """
    if not template_gcs_path.startswith("gs://"):
        raise ValueError("template_gcs_path must start with gs://")

    project = _cloud_project()
    region = _region()
    _safe_identifier(job_name, "job_name")

    url = (
        "https://dataflow.googleapis.com/v1b3/projects/"
        f"{quote(project, safe='')}/locations/{quote(region, safe='')}"
        "/templates:launch"
    )

    response = _authorized_session().post(
        url,
        params={"gcsPath": template_gcs_path},
        json={
            "launchParameter": {
                "jobName": job_name,
                "parameters": parameters or {},
                "environment": {},
            }
        },
        timeout=60,
    )
    response.raise_for_status()
    result = response.json()

    return {
        "status": "submitted",
        "service": "dataflow",
        "project_id": project,
        "region": region,
        "job_name": job_name,
        "response": result,
    }


def invoke_cloud_run(
    service_url: str,
    payload: dict[str, Any],
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    """
    Invoke a Cloud Run service with Google-authenticated HTTP.

    The caller's identity must have permission to invoke the target service.
    """
    if not service_url.startswith("https://"):
        raise ValueError("service_url must start with https://")

    if not isinstance(payload, dict):
        raise ValueError("payload must be a dictionary")

    if isinstance(timeout_seconds, bool) or not isinstance(
        timeout_seconds, int
    ):
        raise ValueError("timeout_seconds must be an integer.")

    if not 1 <= timeout_seconds <= 300:
        raise ValueError("timeout_seconds must be from 1 to 300.")

    response = _authorized_session().post(
        service_url,
        json=payload,
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    try:
        body = response.json()
    except ValueError:
        body = {"text": response.text[:4000]}

    return {
        "status": "ok",
        "service": "cloud_run",
        "http_status": response.status_code,
        "response": body,
    }


def call_vertex_ai(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 1024,
) -> dict[str, Any]:
    """
    Call a Gemini model through the Vertex AI generateContent REST endpoint.

    Requires project, region, credentials, model access, and Vertex AI API.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    if len(prompt) > 30000:
        raise ValueError("prompt exceeds the 30000-character limit")

    if isinstance(temperature, bool) or not isinstance(
        temperature, (int, float)
    ):
        raise ValueError("temperature must be numeric")

    if not 0 <= temperature <= 1:
        raise ValueError("temperature must be between 0 and 1")

    if isinstance(max_output_tokens, bool) or not isinstance(
        max_output_tokens, int
    ):
        raise ValueError("max_output_tokens must be an integer")

    if not 1 <= max_output_tokens <= 8192:
        raise ValueError("max_output_tokens must be from 1 to 8192")

    project = _cloud_project()
    region = _region()
    selected_model = model or os.getenv(
        "NEXUS_VERTEX_MODEL", "gemini-2.5-flash"
    )
    _safe_identifier(selected_model, "model")

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/projects/"
        f"{quote(project, safe='')}/locations/{quote(region, safe='')}"
        f"/publishers/google/models/{quote(selected_model, safe='')}:generateContent"
    )

    response = _authorized_session().post(
        url,
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": float(temperature),
                "maxOutputTokens": max_output_tokens,
            },
        },
        timeout=90,
    )
    response.raise_for_status()
    result = response.json()

    candidates = result.get("candidates", [])
    text_parts: list[str] = []

    for candidate in candidates:
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            if isinstance(part.get("text"), str):
                text_parts.append(part["text"])

    return {
        "status": "ok",
        "service": "vertex_ai",
        "model": selected_model,
        "text": "\n".join(text_parts),
        "usage_metadata": result.get("usageMetadata", {}),
        "finish_reason": (
            candidates[0].get("finishReason") if candidates else None
        ),
    }
