
import json

import pytest

import ai.tools.tool_registry as registry


@pytest.fixture
def sample_processed_data(tmp_path, monkeypatch):
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)

    (processed / "kpi_summary.json").write_text(
        json.dumps(
            {
                "transaction_count": 12000,
                "success_rate": 96.2,
            }
        ),
        encoding="utf-8",
    )

    (processed / "opportunity_priorities.csv").write_text(
        "opportunity_id,recoverable_value\n"
        "OPP-001,250000\n"
        "OPP-002,180000\n",
        encoding="utf-8",
    )

    (processed / "anomaly_summary.csv").write_text(
        "anomaly_id,severity\n"
        "AN-001,high\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(registry, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(registry, "PROCESSED_DIR", processed)

    return processed


def test_registry_contains_only_approved_tools():
    expected = {
        "get_kpis",
        "list_opportunities",
        "list_anomalies",
        "get_reconciliation",
        "list_partners",
        "list_regions",
    }

    assert set(registry.TOOL_REGISTRY) == expected


def test_kpi_tool_reads_json(sample_processed_data):
    result = registry.call_tool("get_kpis")

    assert result["status"] == "ok"
    assert result["artifacts"]
    assert result["artifacts"][0]["source"].endswith(
        "kpi_summary.json"
    )


def test_opportunity_tool_returns_bounded_records(
    sample_processed_data,
):
    result = registry.call_tool(
        "list_opportunities",
        {"limit": 1},
    )

    assert result["status"] == "ok"
    assert len(result["artifacts"][0]["data"]) == 1
    assert result["artifacts"][0]["data"][0]["opportunity_id"] == "OPP-001"


def test_unknown_tool_is_rejected():
    result = registry.call_tool("execute_arbitrary_code")

    assert result["status"] == "error"
    assert "not allowlisted" in result["error"]


def test_unsupported_arguments_are_rejected():
    result = registry.call_tool(
        "get_kpis",
        {"sql": "SELECT * FROM users"},
    )

    assert result["status"] == "error"
    assert "Unsupported argument" in result["error"]


def test_invalid_limit_is_rejected():
    result = registry.call_tool(
        "list_opportunities",
        {"limit": 500},
    )

    assert result["status"] == "error"


def test_question_routes_to_opportunity_tool(
    sample_processed_data,
):
    result = registry.ask_with_tools(
        "Which opportunities should we prioritize?"
    )

    assert result["status"] == "ok"
    assert result["tool_call"]["name"] == "list_opportunities"
    assert result["result"]["artifacts"]


def test_question_routes_to_reconciliation_tool():
    result = registry.route_question(
        "Show reconciliation exceptions"
    )

    assert result["tool"] == "get_reconciliation"


def test_empty_question_is_handled():
    result = registry.ask_with_tools("  ")

    assert result["status"] == "validation_error"
    assert result["tool_call"] is None


def test_unmatched_question_does_not_execute_a_tool():
    result = registry.ask_with_tools(
        "Tell me a joke about the moon"
    )

    assert result["status"] == "no_tool_match"
    assert result["tool_call"] is None


def test_missing_processed_directory_returns_no_data(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        registry,
        "PROCESSED_DIR",
        tmp_path / "does_not_exist",
    )

    result = registry.call_tool("get_kpis")

    assert result["status"] == "no_data"
    assert result["artifacts"] == []
