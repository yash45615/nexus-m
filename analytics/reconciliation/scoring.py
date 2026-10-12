from __future__ import annotations

import pandas as pd


def calculate_reconciliation_score(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    total_transactions = len(result)

    if total_transactions == 0:
        result["reconciliation_score"] = 100.0
        result["reconciliation_status"] = "HEALTHY"
        return result

    exception_count = (
        result["reconciliation_exception"]
        .sum()
    )

    exception_rate = (
        exception_count
        / total_transactions
    )

    score = max(
        0,
        100 * (1 - exception_rate),
    )

    result["exception_rate"] = exception_rate

    result["reconciliation_score"] = score

    if score >= 99:
        status = "HEALTHY"

    elif score >= 95:
        status = "WARNING"

    elif score >= 90:
        status = "DEGRADED"

    else:
        status = "CRITICAL"

    result["reconciliation_status"] = status

    return result


def calculate_financial_exposure(
    df: pd.DataFrame,
) -> dict:

    exceptions = df[
        df["reconciliation_exception"]
    ]

    return {
        "total_transactions": int(
            len(df)
        ),
        "exception_transactions": int(
            len(exceptions)
        ),
        "total_transaction_value": float(
            df["transaction_amount"].sum()
        ),
        "exception_transaction_value": float(
            exceptions[
                "transaction_amount"
            ].sum()
        ),
        "absolute_amount_difference": float(
            exceptions[
                "absolute_amount_difference"
            ].sum()
        ),
    }