
from __future__ import annotations

from ai.agents import investigator


def test_empty_question_is_rejected():
    result = investigator.investigate("   ")

    assert result["status"] == "invalid_question"
    assert result["plan"] == []


def test_invalid_limit_is_rejected():
    result = investigator.investigate(
        "Show payment KPIs",
        limit=100,
    )

    assert result["status"] == "invalid_arguments"


def test_payment_performance_plans_kpis():
    plan = investigator.plan_investigation(
        "Show the overall payment performance"
    )

    assert "get_kpis" in plan


def test_declining_performance_plans_anomaly_investigation():
    plan = investigator.plan_investigation(
        "Why are payment approval rates declining?"
    )

    assert "list_anomalies" in plan
    assert "get_kpis" in plan


def test_broad_investigation_plans_multiple_tools():
    plan = investigator.plan_investigation(
        "Run a comprehensive investigation and tell me "
        "what we should prioritize"
    )

    assert "get_kpis" in plan
    assert "list_anomalies" in plan
    assert "get_reconciliation" in plan
    assert "list_opportunities" in plan


def test_unknown_question_does_not_execute_tools(monkeypatch):
    def unexpected_call(*args, **kwargs):
        raise AssertionError("No tool should execute")

    monkeypatch.setattr(
        investigator.tool_registry,
        "call_tool",
        unexpected_call,
    )

    result = investigator.investigate(
        "Tell me a joke about penguins"
    )

    assert result["status"] == "no_matching_tools"
    assert result["tool_results"] == {}


def test_successful_investigation_collects_evidence(monkeypatch):
    def fake_call_tool(tool_name, arguments=None):
        return {
            "status": "ok",
            "artifacts": [
                {
                    "source": "data\\processed\\kpi_summary.json",
                    "data": {
                        "transactions": 1000,
                        "approval_rate_pct": 95.0,
                    },
                }
            ],
        }

    monkeypatch.setattr(
        investigator.tool_registry,
        "call_tool",
        fake_call_tool,
    )

    result = investigator.investigate("Show payment KPIs")

    assert result["status"] == "ok"
    assert "get_kpis" in result["tool_results"]
    assert result["evidence"]
    assert (
        result["evidence"][0]["source"]
        == "data\\processed\\kpi_summary.json"
    )
    assert result["evidence"][0]["records"][0]["approval_rate_pct"] == 95.0


def test_one_tool_failure_does_not_stop_other_tools(monkeypatch):
    def fake_call_tool(tool_name, arguments=None):
        if tool_name == "list_anomalies":
            raise RuntimeError("Simulated tool failure")

        return {
            "status": "ok",
            "artifacts": [
                {
                    "source": "data\\processed\\kpi_summary.json",
                    "data": {"approval_rate_pct": 95.0},
                }
            ],
        }

    monkeypatch.setattr(
        investigator.tool_registry,
        "call_tool",
        fake_call_tool,
    )

    result = investigator.investigate(
        "Why is payment performance declining?"
    )

    assert result["status"] == "partial"
    assert "get_kpis" in result["tool_results"]
    assert "list_anomalies" in result["tool_results"]
    assert result["evidence"]
    assert result["limitations"]


def test_no_data_is_reported_without_inventing_findings(monkeypatch):
    def fake_call_tool(tool_name, arguments=None):
        return {
            "status": "no_data",
            "artifacts": [],
        }

    monkeypatch.setattr(
        investigator.tool_registry,
        "call_tool",
        fake_call_tool,
    )

    result = investigator.investigate("Show payment KPIs")

    assert result["status"] == "no_data"
    assert result["evidence"] == []
    assert any("No usable evidence" in item for item in result["findings"])


def test_tool_arguments_are_bounded(monkeypatch):
    received = []

    def fake_call_tool(tool_name, arguments=None):
        received.append((tool_name, arguments))
        return {"status": "ok", "artifacts": []}

    monkeypatch.setattr(
        investigator.tool_registry,
        "call_tool",
        fake_call_tool,
    )

    investigator.investigate(
        "Run a comprehensive investigation",
        limit=3,
    )

    assert received
    assert all(
        args.get("limit") == 3
        for name, args in received
        if name != "get_kpis"
    )
    assert all(name in investigator.TOOL_ORDER for name, args in received)
