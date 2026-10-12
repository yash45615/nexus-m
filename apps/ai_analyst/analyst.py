
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


# ---------------------------------------------------------
# PROJECT CONFIGURATION
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_FILES = 35
MAX_ROWS_PER_CSV = 5
MAX_COLUMNS_PER_CSV = 18
MAX_CONTEXT_CHARS = 18000


# ---------------------------------------------------------
# FILE READERS
# ---------------------------------------------------------

def _read_json(path: Path) -> Any:
    """Read JSON safely. Return None if the file is invalid."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _read_csv_preview(path: Path) -> dict[str, Any]:
    """Read a limited CSV preview to keep evidence small."""
    try:
        frame = pd.read_csv(path, nrows=MAX_ROWS_PER_CSV)
        frame = frame.iloc[:, :MAX_COLUMNS_PER_CSV]
        frame = frame.astype(object).where(pd.notna(frame), None)

        return {
            "columns": [str(column) for column in frame.columns],
            "rows": frame.to_dict(orient="records"),
        }
    except (
        OSError,
        UnicodeDecodeError,
        pd.errors.ParserError,
        ValueError,
    ):
        return {"error": "CSV could not be read."}


def _flatten(value: Any, prefix: str = "") -> list[str]:
    """Convert nested JSON data into readable key-value evidence."""
    output: list[str] = []

    if isinstance(value, dict):
        for key, item in value.items():
            new_prefix = f"{prefix}.{key}" if prefix else str(key)
            output.extend(_flatten(item, new_prefix))

    elif isinstance(value, list):
        for index, item in enumerate(value[:10]):
            output.extend(_flatten(item, f"{prefix}[{index}]"))

    else:
        output.append(f"{prefix}: {value}")

    return output


# ---------------------------------------------------------
# EVIDENCE COLLECTION
# ---------------------------------------------------------

def collect_evidence() -> dict[str, Any]:
    """
    Collect existing processed JSON and CSV files.

    The function does not create or fabricate business metrics.
    """
    try:
        source_directory = str(
            PROCESSED_DIR.relative_to(PROJECT_ROOT)
        )
    except ValueError:
        # Handles temporary test paths on a different Windows drive.
        source_directory = str(PROCESSED_DIR)

    evidence: dict[str, Any] = {
        "project": "NEXUS-M",
        "source_directory": source_directory,
        "sources": [],
        "warnings": [],
    }

    if not PROCESSED_DIR.exists():
        evidence["warnings"].append(
            "The processed-data directory does not exist yet."
        )
        return evidence

    files = sorted(
        path
        for path in PROCESSED_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".json", ".csv"}
    )[:MAX_FILES]

    if not files:
        evidence["warnings"].append(
            "No processed JSON or CSV artifacts were found. "
            "Run the relevant NEXUS-M analytics phases first."
        )
        return evidence

    for path in files:
        try:
            relative_path = str(path.relative_to(PROJECT_ROOT))
        except ValueError:
            relative_path = str(path)

        if path.suffix.lower() == ".json":
            content = _read_json(path)

            if content is None:
                evidence["warnings"].append(
                    f"Could not read JSON artifact: {relative_path}"
                )
                continue

            evidence["sources"].append(
                {
                    "path": relative_path,
                    "type": "json",
                    "content": content,
                    "text": _flatten(content)[:100],
                }
            )

        elif path.suffix.lower() == ".csv":
            preview = _read_csv_preview(path)

            evidence["sources"].append(
                {
                    "path": relative_path,
                    "type": "csv",
                    "content": preview,
                }
            )

    return evidence


# ---------------------------------------------------------
# QUESTION-TO-SOURCE MATCHING
# ---------------------------------------------------------

def _relevant_sources(
    question: str,
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rank available files by relevance to the user's question."""
    text = question.lower()

    topic_terms = {
        "kpi": {
            "kpi", "metric", "metrics", "overall",
            "summary", "transaction",
        },
        "partner": {"partner", "processor", "acquirer"},
        "region": {
            "region", "regional", "geography", "geographic",
        },
        "merchant": {"merchant", "segment", "segmentation"},
        "anomaly": {
            "anomaly", "anomalies", "unusual", "outlier",
        },
        "root": {
            "root", "cause", "driver", "failure", "why",
        },
        "opportunity": {
            "opportunity", "recover", "recovery", "value",
            "revenue", "recoverable",
        },
        "reconciliation": {
            "reconciliation", "reconcile", "matched", "exception",
        },
        "quality": {
            "quality", "missing", "duplicate", "validation",
            "governance",
        },
    }

    relevant_terms: set[str] = set()

    for terms in topic_terms.values():
        if any(term in text for term in terms):
            relevant_terms.update(terms)

    question_words = {
        word.strip("?!.,:;()[]{}\"'")
        for word in text.split()
        if len(word.strip("?!.,:;()[]{}\"'")) >= 4
    }

    ranked: list[tuple[int, dict[str, Any]]] = []

    for source in sources:
        path = str(source.get("path", "")).lower()

        try:
            source_text = json.dumps(
                source.get("content", {}),
                default=str,
                ensure_ascii=False,
            ).lower()
        except (TypeError, ValueError):
            source_text = ""

        searchable = f"{path} {source_text}"

        score = sum(
            2 for term in relevant_terms if term in path
        )
        score += sum(
            1 for term in relevant_terms if term in searchable
        )
        score += sum(
            1 for word in question_words if word in path
        )

        if score > 0:
            ranked.append((score, source))

    ranked.sort(key=lambda item: item[0], reverse=True)

    # If no strong keyword matches exist, show a small overview.
    if not ranked:
        return sources[:5]

    return [source for _, source in ranked[:8]]


# ---------------------------------------------------------
# EVIDENCE FORMATTING
# ---------------------------------------------------------

def _format_sources(
    sources: list[dict[str, Any]],
) -> str:
    """Format selected evidence for an optional language model."""
    parts: list[str] = []

    for source in sources:
        path = source.get("path", "unknown source")
        content = source.get("content", {})

        try:
            rendered = json.dumps(
                content,
                indent=2,
                default=str,
                ensure_ascii=False,
            )
        except (TypeError, ValueError):
            rendered = str(content)

        parts.append(f"SOURCE: {path}\n{rendered}")

    return "\n\n".join(parts)[:MAX_CONTEXT_CHARS]


# ---------------------------------------------------------
# LOCAL ANALYST — NO API KEY REQUIRED
# ---------------------------------------------------------

def _local_answer(
    question: str,
    sources: list[dict[str, Any]],
    warnings: list[str],
) -> str:
    """
    Produce a transparent evidence inventory without a language model.

    This fallback does not pretend to perform statistical analysis
    or draw conclusions that are not supported by the source data.
    """
    if not sources:
        lines = [
            "I cannot answer this question from the current project outputs.",
            "",
            "No readable evidence artifacts were found.",
            "Run the relevant NEXUS-M analytics phases and try again.",
        ]

        if warnings:
            lines.extend(["", "Warnings:"])
            lines.extend(f"- {warning}" for warning in warnings)

        return "\n".join(lines)

    selected = _relevant_sources(question, sources)

    lines = [
        "NEXUS-M Local Evidence Analyst",
        "Mode: local; no language-model API was used.",
        "",
        f"Question: {question}",
        "",
        "Relevant available evidence:",
    ]

    for source in selected:
        lines.append(f"- Source: {source['path']}")

        if source.get("type") == "json":
            entries = source.get("text", [])

            if entries:
                for entry in entries[:8]:
                    lines.append(f"    {entry}")
            else:
                lines.append("    JSON file is empty.")

        elif source.get("type") == "csv":
            content = source.get("content", {})
            columns = content.get("columns", [])
            rows = content.get("rows", [])

            if content.get("error"):
                lines.append("    CSV preview could not be read.")
                continue

            if columns:
                lines.append(
                    "    Columns: " + ", ".join(columns)
                )

            if rows:
                lines.append(
                    "    Sample rows: "
                    + json.dumps(
                        rows[:2],
                        default=str,
                        ensure_ascii=False,
                    )
                )
            else:
                lines.append("    No preview rows available.")

    lines.extend(
        [
            "",
            "Interpretation:",
            "These are source-file previews, not independently "
            "verified business conclusions. Check the relevant "
            "metrics and records before taking action.",
        ]
    )

    if warnings:
        lines.extend(["", "Data warnings:"])
        lines.extend(f"- {warning}" for warning in warnings)

    return "\n".join(lines)


# ---------------------------------------------------------
# OPTIONAL OPENAI INTEGRATION
# ---------------------------------------------------------

def _openai_answer(
    question: str,
    evidence_text: str,
) -> str:
    """Generate a grounded answer using the optional OpenAI API."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions=(
            "You are the NEXUS-M analytics assistant for a simulated "
            "payment network. Use only the supplied project evidence. "
            "Do not invent values, causes, sample sizes, or outcomes. "
            "If evidence is insufficient, clearly say what is missing. "
            "Distinguish observed facts from hypotheses and recommendations. "
            "Cite the source file paths used. Never claim synthetic data "
            "is real production payment-network data. "
            "Keep the answer clear, concise, and actionable."
        ),
        input=(
            f"ANALYST QUESTION:\n{question}\n\n"
            f"PROJECT EVIDENCE:\n{evidence_text}"
        ),
    )

    answer = getattr(response, "output_text", None)

    if not answer or not answer.strip():
        raise RuntimeError("The model returned no text answer.")

    return answer.strip()


# ---------------------------------------------------------
# PUBLIC ANALYST FUNCTION
# ---------------------------------------------------------

def ask_analyst(question: str) -> dict[str, Any]:
    """
    Answer a business question using available project evidence.

    Returns:
        answer: The generated or fallback answer.
        mode: The execution mode.
        sources: Evidence file paths.
        warnings: Any data or model warnings.
    """
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "mode": "validation",
            "sources": [],
            "warnings": [],
        }

    evidence = collect_evidence()

    selected = _relevant_sources(
        question,
        evidence["sources"],
    )

    source_paths = [
        source["path"] for source in selected
    ]

    warnings = list(evidence["warnings"])
    api_key_available = bool(
        os.getenv("OPENAI_API_KEY")
    )

    if api_key_available:
        try:
            answer = _openai_answer(
                question,
                _format_sources(selected),
            )
            mode = f"openai:{DEFAULT_MODEL}"

        except Exception as exc:
            # A failed API call should not prevent local analysis.
            warnings.append(
                "The model request failed "
                f"({type(exc).__name__}); using local evidence mode."
            )

            answer = _local_answer(
                question,
                evidence["sources"],
                warnings,
            )
            mode = "local_fallback"

    else:
        answer = _local_answer(
            question,
            evidence["sources"],
            warnings,
        )
        mode = "local"

    return {
        "answer": answer,
        "mode": mode,
        "sources": source_paths,
        "warnings": warnings,
    }


# ---------------------------------------------------------
# COMMAND-LINE ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    print("NEXUS-M GenAI Analyst")
    print("Type a question, or type 'exit' to quit.")

    while True:
        try:
            user_question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting analyst.")
            break

        if user_question.lower() in {"exit", "quit"}:
            print("Exiting analyst.")
            break

        result = ask_analyst(user_question)

        print(f"\nMode: {result['mode']}")
        print("\nAnswer:")
        print(result["answer"])

        if result["sources"]:
            print("\nSources:")
            for source_path in result["sources"]:
                print(f"- {source_path}")

        if result["warnings"]:
            print("\nWarnings:")
            for warning in result["warnings"]:
                print(f"- {warning}")