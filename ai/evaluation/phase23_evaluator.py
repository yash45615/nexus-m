
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.agents import investigator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "ai_evaluation"

# Fixed, repeatable benchmark. Expected tools are based on the question's intent.
BENCHMARK_CASES: list[dict[str, Any]] = [
    {
        "id": "EVAL-001",
        "question": "Show the overall payment KPI summary",
        "expected_tools": ["get_kpis"],
    },
    {
        "id": "EVAL-002",
        "question": "Why are payment approval rates declining?",
        "expected_tools": ["get_kpis", "list_anomalies"],
    },
    {
    "id": "EVAL-003",
    "question": "Investigate settlement mismatches and reconciliation exceptions",
    "expected_tools": [
        "list_anomalies",
        "get_reconciliation",
    ],
    },
    {
        "id": "EVAL-004",
        "question": "Which opportunities should we prioritize for recovery?",
        "expected_tools": ["list_opportunities"],
    },
    {
    "id": "EVAL-005",
    "question": "Compare partner performance",
    "expected_tools": ["get_kpis", "list_partners"],
    },
    {
    "id": "EVAL-006",
    "question": "Compare performance across regions",
    "expected_tools": ["get_kpis", "list_regions"],
    },
    {
        "id": "EVAL-007",
        "question": "Tell me a joke about penguins",
        "expected_tools": [],
    },
    {
        "id": "EVAL-008",
        "question": "Run a comprehensive investigation and tell me what to prioritize",
        "expected_tools": [
            "get_kpis",
            "list_anomalies",
            "get_reconciliation",
            "list_opportunities",
        ],
    },
]


def _tool_metrics(
    expected: list[str],
    predicted: list[str],
) -> dict[str, Any]:
    """Calculate precision, recall, F1, and exact-match for one case."""
    expected_set = set(expected)
    predicted_set = set(predicted)
    true_positive = len(expected_set & predicted_set)
    false_positive = len(predicted_set - expected_set)
    false_negative = len(expected_set - predicted_set)

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else (1.0 if not expected_set else 0.0)
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 1.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "exact_match": expected_set == predicted_set,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def evaluate_case(
    case: dict[str, Any],
    execute_investigation: bool = False,
) -> dict[str, Any]:
    """Evaluate tool planning, with optional runtime evidence checks."""
    question = case["question"]
    expected = case["expected_tools"]
    predicted = investigator.plan_investigation(question)
    metrics = _tool_metrics(expected, predicted)

    result: dict[str, Any] = {
        "id": case["id"],
        "question": question,
        "expected_tools": expected,
        "predicted_tools": predicted,
        **metrics,
    }

    if execute_investigation:
        report = investigator.investigate(question)
        evidence = report.get("evidence", [])
        valid_evidence = [
            item
            for item in evidence
            if isinstance(item, dict)
            and isinstance(item.get("source"), str)
            and item["source"].strip()
            and isinstance(item.get("records"), list)
            and len(item["records"]) > 0
        ]

        result["runtime"] = {
            "status": report.get("status", "unknown"),
            "evidence_item_count": len(evidence),
            "grounded_evidence_item_count": len(valid_evidence),
            "evidence_grounding_rate": round(
                len(valid_evidence) / len(evidence), 4
            ) if evidence else 0.0,
            "limitations": report.get("limitations", []),
        }

    return result


def _average(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def evaluate_suite(
    cases: list[dict[str, Any]] | None = None,
    execute_investigation: bool = False,
) -> dict[str, Any]:
    """Run all cases and summarize tool-selection performance."""
    selected_cases = BENCHMARK_CASES if cases is None else cases
    results = [
        evaluate_case(case, execute_investigation=execute_investigation)
        for case in selected_cases
    ]

    summary = {
        "case_count": len(results),
        "exact_match_accuracy": _average(
            [float(row["exact_match"]) for row in results]
        ),
        "macro_precision": _average(
            [row["precision"] for row in results]
        ),
        "macro_recall": _average(
            [row["recall"] for row in results]
        ),
        "macro_f1": _average([row["f1"] for row in results]),
        "passed_cases": sum(
            1 for row in results if row["exact_match"]
        ),
        "failed_cases": sum(
            1 for row in results if not row["exact_match"]
        ),
    }

    return {
        "evaluation": "NEXUS-M Phase 23",
        "summary": summary,
        "results": results,
        "notes": [
            "Expected tools are manually defined benchmark labels.",
            "High tool-selection scores do not prove business-answer correctness.",
            "Evidence grounding checks source and record presence, not factual truth.",
            "Runtime evaluation can return no data if processed artifacts are absent.",
        ],
    }


def save_report(report: dict[str, Any]) -> Path:
    """Save the latest benchmark report as JSON."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "phase23_evaluation.json"
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    print("NEXUS-M Evaluation & Quality Benchmark")
    print("Running tool-selection and runtime evidence checks...")

    report = evaluate_suite(execute_investigation=True)
    output_path = save_report(report)

    print(json.dumps(report["summary"], indent=2))
    print(f"\nDetailed report saved to: {output_path}")

    print("\nPer-case results:")
    for item in report["results"]:
        status = "PASS" if item["exact_match"] else "FAIL"
        print(
            f'{status} {item["id"]}: '
            f'precision={item["precision"]:.2f}, '
            f'recall={item["recall"]:.2f}, '
            f'F1={item["f1"]:.2f}'
        )
        if "runtime" in item:
            runtime = item["runtime"]
            print(
                f'  Runtime status={runtime["status"]}, '
                f'evidence={runtime["grounded_evidence_item_count"]}/'
                f'{runtime["evidence_item_count"]} grounded evidence items'
            )


if __name__ == "__main__":
    main()
