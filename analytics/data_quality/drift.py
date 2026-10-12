from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_distribution(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:

    return (
        df[column]
        .value_counts(
            normalize=True,
            dropna=False,
        )
    )


def detect_categorical_drift(
    baseline: pd.DataFrame,
    current: pd.DataFrame,
    column: str,
    threshold: float = 0.10,
) -> dict[str, Any]:

    baseline_distribution = calculate_distribution(
        baseline,
        column,
    )

    current_distribution = calculate_distribution(
        current,
        column,
    )

    categories = set(
        baseline_distribution.index
    ).union(
        current_distribution.index
    )

    changes = []

    for category in categories:

        baseline_value = float(
            baseline_distribution.get(
                category,
                0,
            )
        )

        current_value = float(
            current_distribution.get(
                category,
                0,
            )
        )

        absolute_change = abs(
            current_value - baseline_value
        )

        changes.append({
            "category": str(category),
            "baseline_percentage": round(
                baseline_value * 100,
                4,
            ),
            "current_percentage": round(
                current_value * 100,
                4,
            ),
            "absolute_change_percentage": round(
                absolute_change * 100,
                4,
            ),
        })

    maximum_change = max(
        (
            row["absolute_change_percentage"]
            for row in changes
        ),
        default=0,
    )

    drift_detected = (
        maximum_change > threshold * 100
    )

    return {
        "column": column,
        "drift_detected": drift_detected,
        "threshold_percentage": threshold * 100,
        "maximum_change_percentage": maximum_change,
        "details": changes,
    }