
from __future__ import annotations

from ai.evaluation import phase23_evaluator as evaluator


def test_tool_metrics_perfect_match():
    result = evaluator._tool_metrics(
        ["get_kpis", "list_anomalies"],
        ["get_kpis", "list_anomalies"],
    )

    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0
    assert result["exact_match"] is True


def test_tool_metrics_detects_false_positive():
    result = evaluator._tool_metrics(
        ["get_kpis"],
        ["get_kpis", "list_anomalies"],
    )

    assert result["precision"] == 0.5
    assert result["recall"] == 1.0
    assert result["exact_match"] is False


def test_tool_metrics_detects_missing_tool():
    result = evaluator._tool_metrics(
        ["get_kpis", "list_anomalies"],
        ["get_kpis"],
    )

    assert result["precision"] == 1.0
    assert result["recall"] == 0.5
    assert result["exact_match"] is False


def test_empty_expected_and_predicted_tools_are_perfect():
    result = evaluator._tool_metrics([], [])

    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0
    assert result["exact_match"] is True


def test_benchmark_has_unique_ids():
    ids = [case["id"] for case in evaluator.BENCHMARK_CASES]

    assert len(ids) == len(set(ids))
    assert len(ids) >= 8


def test_benchmark_tool_selection():
    report = evaluator.evaluate_suite()

    assert report["summary"]["case_count"] == len(
        evaluator.BENCHMARK_CASES
    )
    assert report["summary"]["passed_cases"] == len(
        evaluator.BENCHMARK_CASES
    )
    assert report["summary"]["failed_cases"] == 0
    assert report["summary"]["exact_match_accuracy"] == 1.0


def test_case_evaluation_includes_expected_and_predicted_tools():
    case = {
        "id": "CUSTOM-001",
        "question": "Show the overall payment KPI summary",
        "expected_tools": ["get_kpis"],
    }

    result = evaluator.evaluate_case(case)

    assert result["expected_tools"] == ["get_kpis"]
    assert result["predicted_tools"] == ["get_kpis"]
    assert result["exact_match"] is True


def test_runtime_evaluation_checks_evidence(monkeypatch):
    def fake_investigate(question):
        return {
            "status": "ok",
            "evidence": [
                {
                    "source": "data\\processed\\kpi_summary.json",
                    "records": [{"approval_rate_pct": 95.0}],
                },
                {
                    "source": "",
                    "records": [],
                },
            ],
            "limitations": [],
        }

    monkeypatch.setattr(
        evaluator.investigator,
        "investigate",
        fake_investigate,
    )

    case = {
        "id": "CUSTOM-002",
        "question": "Show the overall payment KPI summary",
        "expected_tools": ["get_kpis"],
    }

    result = evaluator.evaluate_case(
        case,
        execute_investigation=True,
    )

    assert result["runtime"]["evidence_item_count"] == 2
    assert result["runtime"]["grounded_evidence_item_count"] == 1
    assert result["runtime"]["evidence_grounding_rate"] == 0.5


def test_report_can_be_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluator, "REPORT_DIR", tmp_path)

    report = evaluator.evaluate_suite()
    output_path = evaluator.save_report(report)

    assert output_path.exists()
    assert output_path.name == "phase23_evaluation.json"
    assert '"summary"' in output_path.read_text(encoding="utf-8")
