from __future__ import annotations

import pandas as pd


def min_max_normalize(series: pd.Series) -> pd.Series:
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(0.0, index=series.index)

    if maximum == minimum:
        return pd.Series(1.0, index=series.index)

    return (series - minimum) / (maximum - minimum)


def calculate_opportunity_score(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    value_score = min_max_normalize(
        result["recoverable_value"]
    )

    failure_score = min_max_normalize(
        result["failure_rate"]
    )

    volume_score = min_max_normalize(
        result["failed_transactions"]
    )

    excess_value_score = min_max_normalize(
        result["estimated_excess_failure_value"]
    )

    result["opportunity_score"] = (
        value_score * 0.40
        + failure_score * 0.20
        + volume_score * 0.15
        + excess_value_score * 0.25
    )

    result["opportunity_score"] = (
        result["opportunity_score"] * 100
    )

    result["priority"] = pd.cut(
        result["opportunity_score"],
        bins=[
            -float("inf"),
            25,
            50,
            75,
            float("inf"),
        ],
        labels=[
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ],
    )

    result["opportunity_rank"] = (
        result["opportunity_score"]
        .rank(
            ascending=False,
            method="dense",
        )
        .astype(int)
    )

    return result