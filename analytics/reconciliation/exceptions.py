from __future__ import annotations

import pandas as pd


def classify_exception(row: pd.Series) -> str:

    if row["missing_settlement"]:
        return "MISSING_SETTLEMENT"

    if row["duplicate_settlement"]:
        return "DUPLICATE_SETTLEMENT"

    if row["amount_mismatch"]:
        return "AMOUNT_MISMATCH"

    if row["timing_mismatch"]:
        return "TIMING_MISMATCH"

    return "MATCHED"


def classify_exceptions(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result["exception_type"] = result.apply(
        classify_exception,
        axis=1,
    )

    return result


def summarize_exceptions(
    df: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        df.groupby("exception_type")
        .agg(
            transaction_count=(
                "transaction_id",
                "count",
            ),
            transaction_value=(
                "transaction_amount",
                "sum",
            ),
            amount_difference=(
                "absolute_amount_difference",
                "sum",
            ),
        )
        .reset_index()
    )

    return summary.sort_values(
        "transaction_value",
        ascending=False,
    )