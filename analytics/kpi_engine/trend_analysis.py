from __future__ import annotations

import pandas as pd


def daily_transaction_trend(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    df = transactions.copy()

    df["date"] = (
        df["created_at"]
        .dt.date
    )

    result = (
        df.groupby("date")
        .agg(
            transactions=(
                "transaction_id",
                "count",
            ),
            transaction_value=(
                "transaction_amount",
                "sum",
            ),
            successful_transactions=(
                "status",
                lambda x: (x == "SUCCESS").sum(),
            ),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum(),
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
            p95_latency_ms=(
                "processing_time_ms",
                lambda x: x.quantile(0.95),
            ),
            p99_latency_ms=(
                "processing_time_ms",
                lambda x: x.quantile(0.99),
            ),
        )
        .reset_index()
    )

    result["authorization_rate_pct"] = (
        result["successful_transactions"]
        / result["transactions"]
        * 100
    )

    result["failure_rate_pct"] = (
        result["failed_transactions"]
        / result["transactions"]
        * 100
    )

    return result.sort_values("date")


def daily_partner_trend(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    df = transactions.copy()

    df["date"] = (
        df["created_at"]
        .dt.date
    )

    result = (
        df.groupby(
            [
                "date",
                "partner_key",
            ]
        )
        .agg(
            transactions=(
                "transaction_id",
                "count",
            ),
            transaction_value=(
                "transaction_amount",
                "sum",
            ),
            successful_transactions=(
                "status",
                lambda x: (x == "SUCCESS").sum(),
            ),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum(),
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
            p95_latency_ms=(
                "processing_time_ms",
                lambda x: x.quantile(0.95),
            ),
        )
        .reset_index()
    )

    result["authorization_rate_pct"] = (
        result["successful_transactions"]
        / result["transactions"]
        * 100
    )

    result["failure_rate_pct"] = (
        result["failed_transactions"]
        / result["transactions"]
        * 100
    )

    return result.sort_values(
        ["date", "partner_key"]
    )


def incident_comparison(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    result = (
        transactions
        .groupby("incident_flag")
        .agg(
            transactions=(
                "transaction_id",
                "count",
            ),
            transaction_value=(
                "transaction_amount",
                "sum",
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
            p95_latency_ms=(
                "processing_time_ms",
                lambda x: x.quantile(0.95),
            ),
            successful_transactions=(
                "status",
                lambda x: (x == "SUCCESS").sum(),
            ),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum(),
            ),
        )
        .reset_index()
    )

    result["authorization_rate_pct"] = (
        result["successful_transactions"]
        / result["transactions"]
        * 100
    )

    result["failure_rate_pct"] = (
        result["failed_transactions"]
        / result["transactions"]
        * 100
    )

    return result