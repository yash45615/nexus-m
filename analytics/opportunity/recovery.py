from __future__ import annotations

import pandas as pd


def calculate_recovery_probability(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Estimate recovery probability using transparent business rules.

    This is scenario modeling rather than a predictive forecast.
    """

    result = df.copy()

    probabilities = []

    for _, row in result.iterrows():

        failure_rate = float(row.get("failure_rate", 0))

        if failure_rate <= 0.03:
            probability = 0.85

        elif failure_rate <= 0.05:
            probability = 0.70

        elif failure_rate <= 0.10:
            probability = 0.55

        elif failure_rate <= 0.20:
            probability = 0.40

        else:
            probability = 0.25

        probabilities.append(probability)

    result["recovery_probability"] = probabilities

    return result


def calculate_recoverable_value(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = calculate_recovery_probability(df)

    result["recoverable_value"] = (
        result["value_at_risk"]
        * result["recovery_probability"]
    )

    result["estimated_recovered_transactions"] = (
        result["failed_transactions"]
        * result["recovery_probability"]
    )

    return result


def calculate_confidence_scenarios(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    base_probability = result["recovery_probability"]

    low_probability = (base_probability - 0.15).clip(0, 1)
    high_probability = (base_probability + 0.15).clip(0, 1)

    result["low_case_recoverable_value"] = (
        result["value_at_risk"]
        * low_probability
    )

    result["base_case_recoverable_value"] = (
        result["value_at_risk"]
        * base_probability
    )

    result["high_case_recoverable_value"] = (
        result["value_at_risk"]
        * high_probability
    )

    return result