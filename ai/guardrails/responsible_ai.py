
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai.agents import investigator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = PROJECT_ROOT / "reports" / "guardrails" / "audit.jsonl"

MAX_QUESTION_LENGTH = 2000
MAX_EVIDENCE_ITEMS = 50
MAX_RECORDS_PER_EVIDENCE_ITEM = 10
MAX_STRING_LENGTH = 4000

# This layer may authorize only tools that already exist in the registry.
ALLOWED_TOOLS = frozenset(
    {
        "get_kpis",
        "list_opportunities",
        "list_anomalies",
        "get_reconciliation",
        "list_partners",
        "list_regions",
    }
)

# Common secret formats. This is best-effort redaction, not a full DLP system.
SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret)"
            r"(\s*[:=]\s*|\s+)[\"']?([A-Za-z0-9_\-./+=]{8,})"
        ),
        r"\1\2[REDACTED]",
    ),
    (
        re.compile(
            r"(?i)\bBearer\s+[A-Za-z0-9\-._~+/]+=*"
        ),
        "Bearer [REDACTED]",
    ),
    (
        re.compile(
            r"\b(?:sk|rk)-[A-Za-z0-9_-]{12,}\b"
        ),
        "[REDACTED_API_KEY]",
    ),
    (
        re.compile(
            r"(?i)\bpassword(\s*[:=]\s*|\s+)[\"']?[^,\s\"']{4,}"
        ),
        r"password\1[REDACTED]",
    ),
)


class GuardrailError(ValueError):
    """Raised when a request violates a guardrail."""


def validate_question(question: Any) -> str:
    """Validate a user question before passing it to the investigator."""
    if not isinstance(question, str):
        raise GuardrailError("Question must be a string.")

    cleaned = question.strip()

    if not cleaned:
        raise GuardrailError("Question cannot be empty.")

    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise GuardrailError(
            f"Question exceeds the {MAX_QUESTION_LENGTH}-character limit."
        )

    # Permit ordinary tabs/newlines, but reject other control characters.
    if any(
        ord(character) < 32 and character not in "\t\n\r"
        for character in cleaned
    ):
        raise GuardrailError(
            "Question contains unsupported control characters."
        )

    return cleaned


def validate_tool_plan(plan: Any) -> list[str]:
    """Reject malformed plans and any tool not on the allowlist."""
    if not isinstance(plan, list):
        raise GuardrailError("Investigation plan must be a list.")

    if len(plan) > len(ALLOWED_TOOLS):
        raise GuardrailError("Investigation plan contains too many tools.")

    if any(not isinstance(tool, str) for tool in plan):
        raise GuardrailError("Every planned tool must be a string.")

    if len(plan) != len(set(plan)):
        raise GuardrailError("Investigation plan contains duplicate tools.")

    unexpected = set(plan) - ALLOWED_TOOLS
    if unexpected:
        raise GuardrailError(
            "Investigation plan contains unapproved tool(s): "
            + ", ".join(sorted(unexpected))
        )

    return plan


def redact_text(value: str) -> str:
    """Redact common credential patterns from text."""
    result = value[:MAX_STRING_LENGTH]

    for pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(replacement, result)

    return result


def sanitize_output(value: Any, depth: int = 0) -> Any:
    """
    Recursively sanitize a JSON-compatible result.

    Bounds nesting, collection sizes, and string lengths so an unexpected
    tool response cannot produce an unbounded user-facing report.
    """
    if depth > 8:
        return "[TRUNCATED: maximum nesting depth exceeded]"

    if value is None or isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        return redact_text(value)

    if isinstance(value, dict):
        output: dict[str, Any] = {}
        items = list(value.items())[:100]

        for key, item in items:
            safe_key = redact_text(str(key))[:200]
            output[safe_key] = sanitize_output(item, depth + 1)

        if len(value) > 100:
            output["_truncated_keys"] = len(value) - 100

        return output

    if isinstance(value, (list, tuple)):
        output = [
            sanitize_output(item, depth + 1)
            for item in value[:MAX_EVIDENCE_ITEMS]
        ]

        if len(value) > MAX_EVIDENCE_ITEMS:
            output.append(
                f"[TRUNCATED: {len(value) - MAX_EVIDENCE_ITEMS} items omitted]"
            )

        return output

    # Do not serialize arbitrary custom objects.
    return f"[UNSUPPORTED VALUE: {type(value).__name__}]"


def _bound_report(report: dict[str, Any]) -> dict[str, Any]:
    """Apply output limits to investigation evidence and records."""
    bounded = dict(report)
    evidence = bounded.get("evidence", [])

    if isinstance(evidence, list):
        limited_evidence = []

        for item in evidence[:MAX_EVIDENCE_ITEMS]:
            if not isinstance(item, dict):
                continue

            safe_item = dict(item)
            records = safe_item.get("records", [])

            if isinstance(records, list):
                safe_item["records"] = records[
                    :MAX_RECORDS_PER_EVIDENCE_ITEM
                ]

            limited_evidence.append(safe_item)

        bounded["evidence"] = limited_evidence

    return bounded


def _write_audit(
    question: str,
    status: str,
    tools: list[str],
    rejection_code: str | None = None,
) -> None:
    """
    Append minimal audit metadata.

    The question, evidence, and tool outputs are deliberately not written.
    The question digest is a correlation identifier, not anonymization.
    """
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "question_sha256": hashlib.sha256(
            question.encode("utf-8")
        ).hexdigest(),
        "status": status,
        "tools": tools,
        "rejection_code": rejection_code,
    }

    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Avoid crashing a valid investigation because audit storage failed.
        # The response reports the logging issue to the caller.
        raise


def safe_investigate(question: Any, limit: int = 5) -> dict[str, Any]:
    """
    Run an investigation behind validation, tool-plan allowlisting,
    bounded output sanitization, and minimal audit logging.
    """
    safe_question = question if isinstance(question, str) else ""

    try:
        safe_question = validate_question(question)

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise GuardrailError("limit must be an integer from 1 to 10.")

        if not 1 <= limit <= 10:
            raise GuardrailError("limit must be an integer from 1 to 10.")

        plan = validate_tool_plan(
            investigator.plan_investigation(safe_question)
        )

        # The investigator creates its own plan, so verify it again before
        # allowing execution. Unexpected plans fail closed.
        report = investigator.investigate(safe_question, limit=limit)

        if not isinstance(report, dict):
            raise GuardrailError("Investigator returned an invalid report.")

        returned_plan = report.get("plan", [])
        validate_tool_plan(returned_plan)

        bounded = _bound_report(report)
        sanitized = sanitize_output(bounded)

        if not isinstance(sanitized, dict):
            raise GuardrailError("Sanitized report is not a dictionary.")

        try:
            _write_audit(
                safe_question,
                str(sanitized.get("status", "unknown")),
                plan,
            )
            audit_status = "written"
        except OSError:
            audit_status = "write_failed"

        sanitized["guardrails"] = {
            "input_validation": "passed",
            "tool_allowlist": "passed",
            "output_sanitization": "applied",
            "audit_log": audit_status,
            "disclaimer": (
                "Redaction covers common credential patterns only. "
                "Review evidence and source access controls separately."
            ),
        }

        return sanitized

    except GuardrailError as exc:
        message = str(exc)
        try:
            _write_audit(
                safe_question,
                "rejected",
                [],
                rejection_code=type(exc).__name__,
            )
            audit_status = "written"
        except OSError:
            audit_status = "write_failed"

        return {
            "status": "rejected",
            "question": None,
            "plan": [],
            "tool_results": {},
            "evidence": [],
            "findings": [],
            "limitations": [message],
            "guardrails": {
                "input_validation": "rejected",
                "audit_log": audit_status,
            },
        }


def main() -> None:
    print("NEXUS-M Responsible AI Guardrails")
    print("Type 'exit' to quit.")

    while True:
        try:
            question = input("\nBusiness question: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.strip().casefold() in {"exit", "quit"}:
            print("Exiting.")
            break

        result = safe_investigate(question)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
