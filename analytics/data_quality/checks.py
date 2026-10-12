from __future__ import annotations

from typing import Any

import pandas as pd


def check_row_count(
    df: pd.DataFrame,
    minimum_rows: int = 1,
) -> dict[str, Any]:

    row_count = len(df)

    passed = row_count >= minimum_rows

    return {
        "check_name": "row_count",
        "check_type": "completeness",
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": row_count,
        "expected_value": f">= {minimum_rows}",
        "message": (
            "Dataset contains an acceptable number of rows."
            if passed
            else "Dataset contains fewer rows than expected."
        ),
    }


def check_nulls(
    df: pd.DataFrame,
    max_null_percentage: float = 5.0,
) -> list[dict[str, Any]]:

    results = []

    for column in df.columns:

        null_count = int(df[column].isna().sum())

        null_percentage = (
            null_count / len(df) * 100
            if len(df) > 0
            else 0
        )

        passed = null_percentage <= max_null_percentage

        results.append({
            "check_name": f"null_check_{column}",
            "check_type": "completeness",
            "column": column,
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "actual_value": round(null_percentage, 4),
            "expected_value": f"<= {max_null_percentage}%",
            "message": (
                f"{column} has acceptable null percentage."
                if passed
                else f"{column} exceeds the allowed null percentage."
            ),
        })

    return results


def check_duplicates(
    df: pd.DataFrame,
    key_column: str,
) -> dict[str, Any]:

    if key_column not in df.columns:

        return {
            "check_name": f"duplicate_check_{key_column}",
            "check_type": "uniqueness",
            "column": key_column,
            "status": "FAIL",
            "passed": False,
            "actual_value": None,
            "expected_value": "Column must exist",
            "message": f"Column {key_column} does not exist.",
        }

    duplicate_count = int(
        df[key_column].duplicated().sum()
    )

    passed = duplicate_count == 0

    return {
        "check_name": f"duplicate_check_{key_column}",
        "check_type": "uniqueness",
        "column": key_column,
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": duplicate_count,
        "expected_value": 0,
        "message": (
            "No duplicate keys detected."
            if passed
            else f"{duplicate_count} duplicate keys detected."
        ),
    }


def check_numeric_range(
    df: pd.DataFrame,
    column: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> dict[str, Any]:

    if column not in df.columns:

        return {
            "check_name": f"range_check_{column}",
            "check_type": "validity",
            "column": column,
            "status": "FAIL",
            "passed": False,
            "actual_value": None,
            "expected_value": "Column must exist",
            "message": f"Column {column} does not exist.",
        }

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    invalid = pd.Series(False, index=df.index)

    if minimum is not None:
        invalid |= series < minimum

    if maximum is not None:
        invalid |= series > maximum

    invalid_count = int(invalid.sum())

    passed = invalid_count == 0

    return {
        "check_name": f"range_check_{column}",
        "check_type": "validity",
        "column": column,
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": invalid_count,
        "expected_value": {
            "minimum": minimum,
            "maximum": maximum,
        },
        "message": (
            f"All {column} values are within the expected range."
            if passed
            else f"{invalid_count} {column} values are outside the expected range."
        ),
    }


def check_allowed_values(
    df: pd.DataFrame,
    column: str,
    allowed_values: list[str],
) -> dict[str, Any]:

    if column not in df.columns:

        return {
            "check_name": f"allowed_values_{column}",
            "check_type": "validity",
            "column": column,
            "status": "FAIL",
            "passed": False,
            "actual_value": None,
            "expected_value": allowed_values,
            "message": f"Column {column} does not exist.",
        }

    invalid_mask = ~df[column].isin(allowed_values)

    invalid_count = int(invalid_mask.sum())

    passed = invalid_count == 0

    return {
        "check_name": f"allowed_values_{column}",
        "check_type": "validity",
        "column": column,
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": invalid_count,
        "expected_value": allowed_values,
        "message": (
            f"All {column} values are valid."
            if passed
            else f"{invalid_count} invalid {column} values detected."
        ),
    }


def check_negative_values(
    df: pd.DataFrame,
    column: str,
) -> dict[str, Any]:

    if column not in df.columns:

        return {
            "check_name": f"negative_check_{column}",
            "check_type": "validity",
            "column": column,
            "status": "FAIL",
            "passed": False,
            "actual_value": None,
            "expected_value": "Column must exist",
            "message": f"Column {column} does not exist.",
        }

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    negative_count = int(
        (series < 0).sum()
    )

    passed = negative_count == 0

    return {
        "check_name": f"negative_check_{column}",
        "check_type": "validity",
        "column": column,
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": negative_count,
        "expected_value": 0,
        "message": (
            f"No negative values found in {column}."
            if passed
            else f"{negative_count} negative values found in {column}."
        ),
    }


def check_timestamp_validity(
    df: pd.DataFrame,
    column: str,
) -> dict[str, Any]:

    if column not in df.columns:

        return {
            "check_name": f"timestamp_check_{column}",
            "check_type": "validity",
            "column": column,
            "status": "FAIL",
            "passed": False,
            "actual_value": None,
            "expected_value": "Column must exist",
            "message": f"Column {column} does not exist.",
        }

    parsed = pd.to_datetime(
        df[column],
        errors="coerce",
    )

    invalid_count = int(parsed.isna().sum())

    passed = invalid_count == 0

    return {
        "check_name": f"timestamp_check_{column}",
        "check_type": "validity",
        "column": column,
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "actual_value": invalid_count,
        "expected_value": 0,
        "message": (
            f"All {column} timestamps are valid."
            if passed
            else f"{invalid_count} invalid timestamps detected."
        ),
    }