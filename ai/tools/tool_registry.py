
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MAX_FILES = 100
MAX_CSV_ROWS = 500
MAX_RETURN_ROWS = 10

# This is an explicit allowlist. User questions cannot add tools.
TOOL_SCHEMAS = {
    "get_kpis": {
        "description": "Retrieve available KPI and overall summary artifacts.",
        "parameters": {},
    },
    "list_opportunities": {
        "description": "Retrieve available opportunity-priority records.",
        "parameters": {"limit": "integer from 1 to 10"},
    },
    "list_anomalies": {
        "description": "Retrieve available anomaly records.",
        "parameters": {"limit": "integer from 1 to 10"},
    },
    "get_reconciliation": {
        "description": "Retrieve reconciliation summaries and exceptions.",
        "parameters": {"limit": "integer from 1 to 10"},
    },
    "list_partners": {
        "description": "Retrieve available partner-performance records.",
        "parameters": {"limit": "integer from 1 to 10"},
    },
    "list_regions": {
        "description": "Retrieve available regional-performance records.",
        "parameters": {"limit": "integer from 1 to 10"},
    },
}


def _processed_files() -> list[Path]:
    """Return a bounded list of supported processed data files."""
    if not PROCESSED_DIR.exists():
        return []

    supported = {".json", ".csv"}

    files = [
        path
        for path in PROCESSED_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in supported
        and "phase21" not in {
            part.lower() for part in path.parts
        }
    ]

    return sorted(files)[:MAX_FILES]


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _read_csv(path: Path) -> list[dict[str, Any]]:
    try:
        frame = pd.read_csv(path, nrows=MAX_CSV_ROWS)
        frame = frame.astype(object).where(pd.notna(frame), None)
        return frame.to_dict(orient="records")
    except (
        OSError,
        UnicodeDecodeError,
        pd.errors.ParserError,
        ValueError,
    ):
        return []


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _matches_filename(path: Path, keywords: set[str]) -> bool:
    name = path.stem.lower().replace("-", "_")
    tokens = set(name.split("_"))
    return bool(tokens & keywords)


def _json_artifact(path: Path) -> dict[str, Any] | None:
    value = _read_json(path)
    if value is None:
        return None

    return {
        "source": _relative_path(path),
        "type": "json",
        "data": value,
    }


def _csv_artifact(path: Path, limit: int) -> dict[str, Any]:
    rows = _read_csv(path)
    return {
        "source": _relative_path(path),
        "type": "csv",
        "row_count_returned": min(len(rows), limit),
        "data": rows[:limit],
    }


def _collect_artifacts(
    filename_keywords: set[str],
    extensions: set[str],
    limit: int = MAX_RETURN_ROWS,
) -> dict[str, Any]:
    """
    Find artifacts using their filenames and return bounded records.

    File paths and results are included so the caller can verify evidence.
    """
    files = _processed_files()
    matched = [
        path
        for path in files
        if path.suffix.lower() in extensions
        and _matches_filename(path, filename_keywords)
    ]

    artifacts: list[dict[str, Any]] = []

    for path in matched[:10]:
        if path.suffix.lower() == ".json":
            artifact = _json_artifact(path)
            if artifact is not None:
                artifacts.append(artifact)
        else:
            artifacts.append(_csv_artifact(path, limit))

    return {
        "status": "ok" if artifacts else "no_data",
        "artifacts": artifacts,
        "message": (
            f"Found {len(artifacts)} matching artifact(s)."
            if artifacts
            else "No matching processed artifacts were found."
        ),
    }


# ---------------------------------------------------------
# APPROVED ANALYTICS TOOLS
# ---------------------------------------------------------

def get_kpis() -> dict[str, Any]:
    """Read available KPI summary files."""
    return _collect_artifacts(
        {"kpi", "kpis", "metrics", "core"},
        {".json", ".csv"},
    )


def list_opportunities(limit: int = 5) -> dict[str, Any]:
    """Read available opportunity-priority files."""
    _validate_limit(limit)
    return _collect_artifacts(
        {"opportunity", "opportunities", "priorities", "priority"},
        {".csv", ".json"},
        limit,
    )


def list_anomalies(limit: int = 5) -> dict[str, Any]:
    """Read available anomaly outputs."""
    _validate_limit(limit)
    return _collect_artifacts(
        {"anomaly", "anomalies", "outlier", "outliers"},
        {".csv", ".json"},
        limit,
    )


def get_reconciliation(limit: int = 5) -> dict[str, Any]:
    """Read reconciliation summaries and exception records."""
    _validate_limit(limit)
    return _collect_artifacts(
        {"reconciliation", "reconcile", "exception", "exceptions"},
        {".json", ".csv"},
        limit,
    )


def list_partners(limit: int = 5) -> dict[str, Any]:
    """Read available partner performance data."""
    _validate_limit(limit)
    return _collect_artifacts(
        {"partner", "partners", "processor", "processors"},
        {".csv", ".json"},
        limit,
    )


def list_regions(limit: int = 5) -> dict[str, Any]:
    """Read available regional performance data."""
    _validate_limit(limit)
    return _collect_artifacts(
        {"region", "regions", "regional", "geography"},
        {".csv", ".json"},
        limit,
    )


def _validate_limit(limit: int) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit must be an integer.")

    if not 1 <= limit <= MAX_RETURN_ROWS:
        raise ValueError(
            f"limit must be between 1 and {MAX_RETURN_ROWS}."
        )


# The registry is the only place where executable tools are registered.
TOOL_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "get_kpis": get_kpis,
    "list_opportunities": list_opportunities,
    "list_anomalies": list_anomalies,
    "get_reconciliation": get_reconciliation,
    "list_partners": list_partners,
    "list_regions": list_regions,
}


def call_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute one allowlisted tool with validated arguments.

    Unknown tools and unsupported arguments are rejected.
    """
    if tool_name not in TOOL_REGISTRY:
        return {
            "status": "error",
            "error": f"Tool '{tool_name}' is not allowlisted.",
        }

    if arguments is None:
        arguments = {}

    if not isinstance(arguments, dict):
        return {
            "status": "error",
            "error": "Tool arguments must be a dictionary.",
        }

    allowed_arguments = set(
        TOOL_SCHEMAS[tool_name]["parameters"].keys()
    )
    unexpected = set(arguments) - allowed_arguments

    if unexpected:
        return {
            "status": "error",
            "error": (
                "Unsupported argument(s): "
                + ", ".join(sorted(unexpected))
            ),
        }

    try:
        return TOOL_REGISTRY[tool_name](**arguments)
    except (ValueError, TypeError) as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


# ---------------------------------------------------------
# QUESTION ROUTER
# ---------------------------------------------------------

def route_question(question: str) -> dict[str, Any]:
    """
    Map a question to an approved tool.

    This initial router is deterministic, not an LLM-based planner.
    """
    question = question.strip().lower()

    if not question:
        return {
            "tool": None,
            "arguments": {},
            "reason": "The question is empty.",
        }

    if any(
        word in question
        for word in ("reconciliation", "reconcile", "exceptions")
    ):
        tool = "get_reconciliation"
        reason = "The question mentions reconciliation or exceptions."

    elif any(
        word in question
        for word in ("opportunity", "opportunities", "recoverable", "recovery")
    ):
        tool = "list_opportunities"
        reason = "The question mentions business opportunities or recovery."

    elif any(
        word in question
        for word in ("anomaly", "anomalies", "outlier", "unusual activity")
    ):
        tool = "list_anomalies"
        reason = "The question mentions anomalies or unusual activity."

    elif any(
        word in question
        for word in ("partner", "partners", "processor", "processors")
    ):
        tool = "list_partners"
        reason = "The question mentions partner performance."

    elif any(
        word in question
        for word in ("region", "regions", "regional", "geography")
    ):
        tool = "list_regions"
        reason = "The question mentions regional performance."

    elif any(
        word in question
        for word in ("kpi", "kpis", "metrics", "overall", "summary")
    ):
        tool = "get_kpis"
        reason = "The question asks for summary metrics."

    else:
        return {
            "tool": None,
            "arguments": {},
            "reason": (
                "No approved tool matched this question. "
                "Try asking about KPIs, partners, regions, anomalies, "
                "opportunities, or reconciliation."
            ),
        }

    return {
        "tool": tool,
        "arguments": {"limit": 5}
        if tool in {
            "list_opportunities",
            "list_anomalies",
            "get_reconciliation",
            "list_partners",
            "list_regions",
        }
        else {},
        "reason": reason,
    }


def ask_with_tools(question: str) -> dict[str, Any]:
    """Route a question, execute the approved tool, and return evidence."""
    if not question or not question.strip():
        return {
            "question": question,
            "status": "validation_error",
            "answer": "Please enter a question.",
            "tool_call": None,
            "result": None,
        }

    routing = route_question(question)

    if routing["tool"] is None:
        return {
            "question": question,
            "status": "no_tool_match",
            "answer": routing["reason"],
            "tool_call": None,
            "result": None,
        }

    result = call_tool(
        routing["tool"],
        routing["arguments"],
    )

    if result["status"] == "error":
        status = "tool_error"
        answer = result["error"]
    elif result["status"] == "no_data":
        status = "no_data"
        answer = (
            "The selected tool ran, but no matching processed artifacts "
            "were found. Check that the relevant analytics phase has run "
            "and review the expected output filenames."
        )
    else:
        status = "ok"
        answer = (
            f"Executed {routing['tool']}. "
            f"{result.get('message', 'Results retrieved.')}"
        )

    return {
        "question": question,
        "status": status,
        "answer": answer,
        "tool_call": {
            "name": routing["tool"],
            "arguments": routing["arguments"],
            "reason": routing["reason"],
        },
        "result": result,
    }


def main() -> None:
    """Run the local tool-calling analyst from the terminal."""
    print("NEXUS-M Tool Calling Analyst")
    print("Approved tools:", ", ".join(TOOL_REGISTRY))
    print("Type 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        response = ask_with_tools(question)
        print(json.dumps(response, indent=2, default=str))


if __name__ == "__main__":
    main()
