from __future__ import annotations

import pandas as pd


def calculate_period_metrics(
    df: pd.DataFrame,
) -> dict[str, float]:

    if len(df) == 0:
        return {
            "transactions": 0,
            "transaction_value": 0.0,
            "authorization_rate_pct": 0.0,
            "failure_rate_pct": 0.0,
            "average_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
        }

    transactions = len(df)

    successful = (
        df["status"] == "SUCCESS"
    ).sum()

    failed = (
        df["status"] == "FAILED"
    ).sum()

    return {
        "transactions": int(
            transactions
        ),
        "transaction_value": float(
            df["transaction_amount"].sum()
        ),
        "authorization_rate_pct": float(
            successful
            / transactions
            * 100
        ),
        "failure_rate_pct": float(
            failed
            / transactions
            * 100
        ),
        "average_latency_ms": float(
            df["processing_time_ms"].mean()
        ),
        "p95_latency_ms": float(
            df["processing_time_ms"].quantile(
                0.95
            )
        ),
    }


def percentage_change(
    current: float,
    previous: float,
) -> float:

    if previous == 0:
        return 0.0

    return (
        (current - previous)
        / abs(previous)
    ) * 100


def compare_periods(
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
) -> pd.DataFrame:

    current = calculate_period_metrics(
        current_df
    )

    previous = calculate_period_metrics(
        previous_df
    )

    rows = []

    for metric in current:

        current_value = current[metric]
        previous_value = previous[metric]

        rows.append(
            {
                "metric": metric,
                "current": current_value,
                "previous": previous_value,
                "absolute_change": (
                    current_value
                    - previous_value
                ),
                "percentage_change": (
                    percentage_change(
                        current_value,
                        previous_value,
                    )
                ),
            }
        )

    return pd.DataFrame(rows)