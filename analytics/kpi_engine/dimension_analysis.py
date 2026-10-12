from __future__ import annotations

import pandas as pd


def partner_performance(
    transactions: pd.DataFrame,
    partners: pd.DataFrame,
) -> pd.DataFrame:

    grouped = (
        transactions
        .groupby("partner_key")
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

    grouped["authorization_rate_pct"] = (
        grouped["successful_transactions"]
        / grouped["transactions"]
        * 100
    )

    grouped["failure_rate_pct"] = (
        grouped["failed_transactions"]
        / grouped["transactions"]
        * 100
    )

    result = grouped.merge(
        partners[
            [
                "partner_key",
                "partner_id",
                "partner_name",
                "partner_type",
                "sla_timeout_seconds",
            ]
        ],
        on="partner_key",
        how="left",
    )

    return result.sort_values(
        "authorization_rate_pct"
    )


def regional_performance(
    transactions: pd.DataFrame,
    regions: pd.DataFrame,
) -> pd.DataFrame:

    grouped = (
        transactions
        .groupby("region_key")
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

    grouped["authorization_rate_pct"] = (
        grouped["successful_transactions"]
        / grouped["transactions"]
        * 100
    )

    grouped["failure_rate_pct"] = (
        grouped["failed_transactions"]
        / grouped["transactions"]
        * 100
    )

    result = grouped.merge(
        regions[
            [
                "region_key",
                "region_name",
                "country",
                "timezone",
            ]
        ],
        on="region_key",
        how="left",
    )

    return result.sort_values(
        "authorization_rate_pct"
    )


def merchant_performance(
    transactions: pd.DataFrame,
    merchants: pd.DataFrame,
) -> pd.DataFrame:

    grouped = (
        transactions
        .groupby("merchant_key")
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
            average_transaction_value=(
                "transaction_amount",
                "mean",
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
        )
        .reset_index()
    )

    grouped["authorization_rate_pct"] = (
        grouped["successful_transactions"]
        / grouped["transactions"]
        * 100
    )

    result = grouped.merge(
        merchants[
            [
                "merchant_key",
                "merchant_id",
                "merchant_name",
                "merchant_category",
                "region",
                "risk_segment",
            ]
        ],
        on="merchant_key",
        how="left",
    )

    return result.sort_values(
        "transaction_value",
        ascending=False,
    )


def category_performance(
    transactions: pd.DataFrame,
    categories: pd.DataFrame,
) -> pd.DataFrame:

    grouped = (
        transactions
        .groupby("category_key")
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
            average_transaction_value=(
                "transaction_amount",
                "mean",
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
        )
        .reset_index()
    )

    grouped["authorization_rate_pct"] = (
        grouped["successful_transactions"]
        / grouped["transactions"]
        * 100
    )

    grouped["failure_rate_pct"] = (
        grouped["failed_transactions"]
        / grouped["transactions"]
        * 100
    )

    result = grouped.merge(
        categories[
            [
                "category_key",
                "category_code",
                "category_name",
            ]
        ],
        on="category_key",
        how="left",
    )

    return result.sort_values(
        "transaction_value",
        ascending=False,
    )


def payment_method_performance(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    result = (
        transactions
        .groupby("payment_method")
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
        "authorization_rate_pct"
    )


def error_code_analysis(
    transactions: pd.DataFrame,
    error_codes: pd.DataFrame,
) -> pd.DataFrame:

    failed = transactions[
        transactions["status"] == "FAILED"
    ].copy()

    result = (
        failed
        .groupby("error_code")
        .agg(
            failures=(
                "transaction_id",
                "count",
            ),
            failed_transaction_value=(
                "transaction_amount",
                "sum",
            ),
            average_latency_ms=(
                "processing_time_ms",
                "mean",
            ),
        )
        .reset_index()
    )

    result = result.merge(
        error_codes[
            [
                "error_code",
                "error_name",
                "error_category",
                "description",
            ]
        ],
        on="error_code",
        how="left",
    )

    result["failure_share_pct"] = (
        result["failures"]
        / result["failures"].sum()
        * 100
    )

    return result.sort_values(
        "failures",
        ascending=False,
    )