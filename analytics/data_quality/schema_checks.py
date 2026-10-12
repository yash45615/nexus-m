from __future__ import annotations

from typing import Any

import pandas as pd


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> dict[str, Any]:

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    passed = len(missing_columns) == 0

    return {
        "check_name": "required_columns",
        "check_type": "schema",
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": list(df.columns),
        "expected_value": required_columns,
        "missing_columns": missing_columns,
        "message": (
            "All required columns are present."
            if passed
            else f"Missing columns: {missing_columns}"
        ),
    }


def check_no_unexpected_columns(
    df: pd.DataFrame,
    expected_columns: list[str],
) -> dict[str, Any]:

    unexpected_columns = [
        column
        for column in df.columns
        if column not in expected_columns
    ]

    passed = len(unexpected_columns) == 0

    return {
        "check_name": "unexpected_columns",
        "check_type": "schema",
        "status": "PASS" if passed else "WARNING",
        "passed": passed,
        "actual_value": list(df.columns),
        "expected_value": expected_columns,
        "unexpected_columns": unexpected_columns,
        "message": (
            "No unexpected columns detected."
            if passed
            else f"Unexpected columns: {unexpected_columns}"
        ),
    }


def infer_column_types(
    df: pd.DataFrame,
) -> dict[str, str]:

    return {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }