from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_quality_score(
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    if not results:

        return {
            "quality_score": 0.0,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warning_checks": 0,
            "status": "FAIL",
        }

    total = len(results)

    passed = sum(
        1
        for result in results
        if result.get("passed") is True
    )

    failed = sum(
        1
        for result in results
        if result.get("status") == "FAIL"
    )

    warnings = sum(
        1
        for result in results
        if result.get("status") == "WARNING"
    )

    score = passed / total * 100

    if failed > 0:

        status = "FAIL"

    elif score < 95:

        status = "WARNING"

    else:

        status = "PASS"

    return {
        "quality_score": round(score, 2),
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": failed,
        "warning_checks": warnings,
        "status": status,
    }


def results_to_dataframe(
    results: list[dict[str, Any]],
) -> pd.DataFrame:

    return pd.DataFrame(results)