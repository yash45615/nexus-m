from __future__ import annotations

import pandas as pd


def calculate_value_at_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate value at risk caused by failed transactions.
    """

    result = df.copy()

    result["value_at_risk"] = result["failed_value"].clip(lower=0)

    return result


def calculate_excess_failure_value(
    df: pd.DataFrame,
    target_failure_rate: float = 0.02,
) -> pd.DataFrame:
    """
    Estimate excess failure value above a target failure rate.

    This is a scenario model, not a financial forecast.
    """

    result = df.copy()

    result["expected_failed_transactions"] = (
        result["transaction_count"] * target_failure_rate
    )

    result["excess_failed_transactions"] = (
        result["failed_transactions"]
        - result["expected_failed_transactions"]
    ).clip(lower=0)

    result["estimated_excess_failure_value"] = (
        result["excess_failed_transactions"]
        * result["average_transaction_value"]
    )

    return result


def build_opportunity_table(
    df: pd.DataFrame,
    target_failure_rate: float = 0.02,
) -> pd.DataFrame:

    result = calculate_value_at_risk(df)

    result = calculate_excess_failure_value(
        result,
        target_failure_rate=target_failure_rate,
    )

    return result