
from __future__ import annotations

import json

import pytest

from ai.guardrails import responsible_ai as guardrails


@pytest.fixture
def audit_file(tmp_path, monkeypatch):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(guardrails, "AUDIT_LOG", path)
    return path


def test_empty_question_is_rejected(audit_file):
    result = guardrails.safe_investigate("   ")

    assert result["status"] == "rejected"
    assert result["plan"] == []
    assert result["tool_results"] == {}


def test_non_string_question_is_rejected(audit_file):
    result = guardrails.safe_investigate({"question": "show KPIs"})

    assert result["status"] == "rejected"


def test_oversized_question_is_rejected(audit_file):
    result = guardrails.safe_investigate(
        "a" * (guardrails.MAX_QUESTION_LENGTH + 1)
    )

    assert result["status"] == "rejected"
    assert "character limit" in result["limitations"][0]


def test_invalid_limit_is_rejected(audit_file):
    result = guardrails.safe_investigate(
        "Show payment KPIs",
        limit=500,
    )

    assert result["status"] == "rejected"


def test_unapproved_tool_is_rejected():
    with pytest.raises(guardrails.GuardrailError):
        guardrails.validate_tool_plan(
            ["get_kpis", "execute_arbitrary_code"]
        )


def test_duplicate_tools_are_rejected():
    with pytest.raises(guardrails.GuardrailError):
        guardrails.validate_tool_plan(["get_kpis", "get_kpis"])


def test_approved_tools_are_accepted():
    result = guardrails.validate_tool_plan(
        ["get_kpis", "list_anomalies"]
    )

    assert result == ["get_kpis", "list_anomalies"]


def test_common_secrets_are_redacted():
    text = (
        "api_key=abcDEF123456789 "
        "Bearer abcdef123456789 "
        "password=hunter2 "
        "sk-abcdefghijklmnop"
    )

    cleaned = guardrails.redact_text(text)

    assert "abcDEF123456789" not in cleaned
    assert "Bearer abcdef123456789" not in cleaned
    assert "password=hunter2" not in cleaned
    assert "sk-abcdefghijklmnop" not in cleaned
    assert "[REDACTED]" in cleaned


def test_output_sanitization_bounds_large_lists():
    result = guardrails.sanitize_output(list(range(100)))

    assert len(result) == guardrails.MAX_EVIDENCE_ITEMS + 1
    assert "TRUNCATED" in result[-1]


def test_output_sanitization_handles_unknown_objects():
    result = guardrails.sanitize_output(object())

    assert result == "[UNSUPPORTED VALUE: object]"


def test_safe_investigation_sanitizes_and_logs(audit_file, monkeypatch):
    def fake_plan(question):
        return ["get_kpis"]

    def fake_investigate(question, limit=5):
        return {
            "status": "ok",
            "question": question,
            "plan": ["get_kpis"],
            "tool_results": {},
            "evidence": [
                {
                    "source": "data\\processed\\kpi_summary.json",
                    "records": [
                        {
                            "api_key": "api_key=abcDEF123456789",
                            "approval_rate_pct": 95.0,
                        }
                    ],
                }
            ],
            "findings": ["KPI data returned."],
            "limitations": [],
        }

    monkeypatch.setattr(
        guardrails.investigator,
        "plan_investigation",
        fake_plan,
    )
    monkeypatch.setattr(
        guardrails.investigator,
        "investigate",
        fake_investigate,
    )

    question = "Show payment KPIs"
    result = guardrails.safe_investigate(question)

    assert result["status"] == "ok"
    assert result["guardrails"]["input_validation"] == "passed"
    assert result["guardrails"]["audit_log"] == "written"

    serialized = json.dumps(result)
    assert "abcDEF123456789" not in serialized

    audit_text = audit_file.read_text(encoding="utf-8")
    assert question not in audit_text
    assert "question_sha256" in audit_text


def test_unknown_planner_tool_is_rejected(audit_file, monkeypatch):
    def fake_plan(question):
        return ["execute_arbitrary_code"]

    monkeypatch.setattr(
        guardrails.investigator,
        "plan_investigation",
        fake_plan,
    )

    def unexpected_investigation(*args, **kwargs):
        raise AssertionError("Investigation must not execute")

    monkeypatch.setattr(
        guardrails.investigator,
        "investigate",
        unexpected_investigation,
    )

    result = guardrails.safe_investigate("Show payment KPIs")

    assert result["status"] == "rejected"
    assert result["tool_results"] == {}


def test_audit_log_does_not_store_question_or_result(audit_file):
    question = "Show payment KPIs for customer@example.com"

    guardrails._write_audit(
        question,
        status="ok",
        tools=["get_kpis"],
    )

    audit_text = audit_file.read_text(encoding="utf-8")

    assert question not in audit_text
    assert "customer@example.com" not in audit_text
    assert "get_kpis" in audit_text
