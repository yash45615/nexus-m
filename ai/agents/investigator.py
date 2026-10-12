
from __future__ import annotations

from typing import Any

from ai.tools import tool_registry


# Only these approved tools can be executed by the investigator.
# The order is stable so reports and tests remain deterministic.
TOOL_ORDER = (
    "get_kpis",
    "list_anomalies",
    "get_reconciliation",
    "list_opportunities",
    "list_partners",
    "list_regions",
)


def plan_investigation(question: str) -> list[str]:
    """Select relevant approved tools in a stable execution order."""
    if not isinstance(question, str) or not question.strip():
        return []

    text = question.casefold()

    # Broad investigations deliberately inspect all four core evidence areas.
    broad_terms = (
        "comprehensive",
        "end to end",
        "end-to-end",
        "what should we prioritize",
        "what should we prioritise",
        "run a comprehensive investigation",
    )

    if any(term in text for term in broad_terms):
        selected = {
            "get_kpis",
            "list_anomalies",
            "get_reconciliation",
            "list_opportunities",
        }
        return [name for name in TOOL_ORDER if name in selected]

    # Keep settlement and reconciliation investigations focused.
    reconciliation_terms = (
        "reconciliation",
        "reconcile",
        "settlement",
        "mismatch",
        "mismatches",
        "exception",
        "exceptions",
    )

    if any(term in text for term in reconciliation_terms):
        selected = {"list_anomalies", "get_reconciliation"}
        return [name for name in TOOL_ORDER if name in selected]

    selected: set[str] = set()

    opportunity_terms = (
        "opportunity",
        "opportunities",
        "prioritize",
        "prioritise",
        "recover",
        "recovery",
        "recoverable",
        "growth",
        "improve",
        "improvement",
        "optimize",
        "optimise",
    )

    if any(term in text for term in opportunity_terms):
        selected.add("list_opportunities")

    anomaly_terms = (
        "anomaly",
        "anomalies",
        "outlier",
        "outliers",
        "unusual",
        "spike",
        "decline",
        "declining",
        "drop",
        "dropped",
        "failure",
        "failures",
        "error",
        "errors",
        "risk",
        "why",
        "cause",
        "causes",
        "root cause",
        "investigate",
        "investigation",
        "issue",
        "issues",
    )

    if any(term in text for term in anomaly_terms):
        selected.add("list_anomalies")

    partner_terms = (
        "partner",
        "partners",
        "processor",
        "processors",
        "bank",
        "gateway",
    )

    if any(term in text for term in partner_terms):
        selected.add("list_partners")

    region_terms = (
        "region",
        "regions",
        "regional",
        "geography",
        "geographic",
        "location",
        "locations",
    )

    if any(term in text for term in region_terms):
        selected.add("list_regions")

    kpi_terms = (
        "kpi",
        "kpis",
        "metric",
        "metrics",
        "approval",
        "authorization",
        "authorisation",
        "transaction",
        "transactions",
        "performance",
        "payment",
        "payments",
        "summary",
        "overall",
        "volume",
        "success rate",
    )

    if any(term in text for term in kpi_terms):
        selected.add("get_kpis")

    return [name for name in TOOL_ORDER if name in selected]


def _records_from_artifact(artifact: Any) -> list[Any]:
    """Extract displayable records without assuming a specific file schema."""
    if not isinstance(artifact, dict):
        return [artifact]

    data = artifact.get("data")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    if data is not None:
        return [data]

    return []


def _build_evidence(
    tool_name: str,
    result: dict[str, Any],
    limit: int,
) -> list[dict[str, Any]]:
    """Create a compact evidence list from a tool's returned artifacts."""
    evidence: list[dict[str, Any]] = []
    artifacts = result.get("artifacts", [])

    if not isinstance(artifacts, list):
        return evidence

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue

        source = artifact.get("source", "Unknown source")
        records = _records_from_artifact(artifact)

        evidence.append(
            {
                "tool": tool_name,
                "source": str(source),
                "records_available_in_result": len(records),
                "records": records[:limit],
            }
        )

    return evidence


def investigate(
    question: str,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Run a bounded, multi-tool investigation and return a structured report.

    Planning is deterministic. This function does not use an LLM, execute
    arbitrary code, or claim that correlations prove causation.
    """
    if not isinstance(question, str) or not question.strip():
        return {
            "status": "invalid_question",
            "question": question,
            "plan": [],
            "tool_results": {},
            "evidence": [],
            "findings": [],
            "limitations": ["Provide a non-empty business question."],
        }

    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 1 <= limit <= 10
    ):
        return {
            "status": "invalid_arguments",
            "question": question,
            "plan": [],
            "tool_results": {},
            "evidence": [],
            "findings": [],
            "limitations": ["limit must be an integer from 1 to 10."],
        }

    plan = plan_investigation(question)

    if not plan:
        return {
            "status": "no_matching_tools",
            "question": question,
            "plan": [],
            "tool_results": {},
            "evidence": [],
            "findings": [
                "The question did not match any approved investigation tools."
            ],
            "limitations": [
                "Rephrase the question using terms such as KPI, partner, "
                "region, anomaly, opportunity, or reconciliation."
            ],
        }

    tool_results: dict[str, dict[str, Any]] = {}
    evidence: list[dict[str, Any]] = []
    limitations: list[str] = []

    # Execute tools independently so one failure does not hide other evidence.
    for tool_name in plan:
        try:
            arguments = {"limit": limit} if tool_name != "get_kpis" else {}
            result = tool_registry.call_tool(tool_name, arguments)

            if not isinstance(result, dict):
                result = {
                    "status": "error",
                    "error": "Tool returned an unexpected result type.",
                }

        except Exception as exc:
            result = {
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
            }

        tool_results[tool_name] = result
        evidence.extend(_build_evidence(tool_name, result, limit))

        result_status = result.get("status", "unknown")
        if result_status != "ok":
            detail = result.get("error") or result_status
            limitations.append(f"{tool_name}: {detail}")

    successful_tools = [
        name
        for name, result in tool_results.items()
        if result.get("status") == "ok"
    ]

    findings: list[str] = []

    if successful_tools:
        findings.append(
            "Approved tools completed successfully: "
            + ", ".join(successful_tools)
            + "."
        )

    if evidence:
        findings.append(
            f"Collected {len(evidence)} evidence item(s) from tool artifacts."
        )
    else:
        findings.append(
            "No usable evidence artifacts were returned. "
            "Check that processed analytics files exist and match the "
            "tool registry's filename rules."
        )

    if limitations:
        status = "partial" if successful_tools else "no_data"
    else:
        status = "ok"

    return {
        "status": status,
        "question": question.strip(),
        "plan": plan,
        "tool_results": tool_results,
        "evidence": evidence,
        "findings": findings,
        "limitations": limitations,
        "disclaimer": (
            "This report summarizes tool outputs; it does not establish "
            "causation or independently verify the underlying source data."
        ),
    }


def main() -> None:
    """Interactive command-line interface."""
    import json

    print("NEXUS-M Agentic Investigation Engine")
    print("Type 'exit' to quit.")

    while True:
        try:
            question = input("\nInvestigation question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting investigation engine.")
            break

        if question.casefold() in {"exit", "quit"}:
            print("Exiting investigation engine.")
            break

        report = investigate(question)
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
