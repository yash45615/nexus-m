from __future__ import annotations

import pandas as pd


def transaction_count(df: pd.DataFrame) -> int:
    """
    Total number of transaction rows.
    """
    return int(len(df))


def unique_transaction_count(df: pd.DataFrame) -> int:
    """
    Number of unique transaction IDs.
    """
    return int(
        df["transaction_id"].nunique()
    )


def successful_transaction_count(
    df: pd.DataFrame,
) -> int:
    """
    Number of successful transactions.
    """
    return int(
        (df["status"] == "SUCCESS").sum()
    )


def failed_transaction_count(
    df: pd.DataFrame,
) -> int:
    """
    Number of failed transactions.
    """
    return int(
        (df["status"] == "FAILED").sum()
    )


def authorization_rate(
    df: pd.DataFrame,
) -> float:
    """
    Percentage of transactions that succeeded.
    """

    if len(df) == 0:
        return 0.0

    return (
        successful_transaction_count(df)
        / len(df)
    ) * 100


def decline_rate(
    df: pd.DataFrame,
) -> float:
    """
    Percentage of transactions that failed.
    """

    if len(df) == 0:
        return 0.0

    return (
        failed_transaction_count(df)
        / len(df)
    ) * 100


def total_transaction_value(
    df: pd.DataFrame,
) -> float:
    """
    Total transaction value / GMV.
    """

    return float(
        df["transaction_amount"]
        .fillna(0)
        .sum()
    )


def successful_transaction_value(
    df: pd.DataFrame,
) -> float:
    """
    GMV from successful transactions.
    """

    successful = df[
        df["status"] == "SUCCESS"
    ]

    return float(
        successful["transaction_amount"]
        .fillna(0)
        .sum()
    )


def average_transaction_value(
    df: pd.DataFrame,
) -> float:
    """
    Average transaction amount.
    """

    if len(df) == 0:
        return 0.0

    return float(
        df["transaction_amount"]
        .mean()
    )


def average_processing_latency(
    df: pd.DataFrame,
) -> float:
    """
    Average transaction processing latency.
    """

    if len(df) == 0:
        return 0.0

    return float(
        df["processing_time_ms"]
        .mean()
    )


def percentile_latency(
    df: pd.DataFrame,
    percentile: float,
) -> float:
    """
    Calculate a latency percentile.

    Example:
        percentile=95 -> P95
        percentile=99 -> P99
    """

    if len(df) == 0:
        return 0.0

    return float(
        df["processing_time_ms"]
        .quantile(percentile / 100)
    )


def p95_latency(
    df: pd.DataFrame,
) -> float:
    return percentile_latency(
        df,
        95,
    )


def p99_latency(
    df: pd.DataFrame,
) -> float:
    return percentile_latency(
        df,
        99,
    )


def failure_rate(
    df: pd.DataFrame,
) -> float:
    """
    Failure rate as a percentage.
    """

    if len(df) == 0:
        return 0.0

    return (
        df["status"]
        .eq("FAILED")
        .mean()
        * 100
    )


def incident_rate(
    df: pd.DataFrame,
) -> float:
    """
    Percentage of transactions that occurred
    during a known incident.
    """

    if len(df) == 0:
        return 0.0

    return (
        df["incident_flag"]
        .fillna(False)
        .mean()
        * 100
    )


def calculate_core_metrics(
    df: pd.DataFrame,
) -> dict[str, float | int]:

    return {
        "transaction_count": transaction_count(df),
        "unique_transaction_count": (
            unique_transaction_count(df)
        ),
        "successful_transactions": (
            successful_transaction_count(df)
        ),
        "failed_transactions": (
            failed_transaction_count(df)
        ),
        "authorization_rate_pct": round(
            authorization_rate(df),
            2,
        ),
        "decline_rate_pct": round(
            decline_rate(df),
            2,
        ),
        "failure_rate_pct": round(
            failure_rate(df),
            2,
        ),
        "total_transaction_value": round(
            total_transaction_value(df),
            2,
        ),
        "successful_transaction_value": round(
            successful_transaction_value(df),
            2,
        ),
        "average_transaction_value": round(
            average_transaction_value(df),
            2,
        ),
        "average_latency_ms": round(
            average_processing_latency(df),
            2,
        ),
        "p95_latency_ms": round(
            p95_latency(df),
            2,
        ),
        "p99_latency_ms": round(
            p99_latency(df),
            2,
        ),
        "incident_rate_pct": round(
            incident_rate(df),
            2,
        ),
    }