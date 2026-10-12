import pandas as pd


def classify_merchant(row: pd.Series) -> str:

    volume = row["transaction_count"]
    success_rate = row["success_rate"]
    latency = row["p95_latency_ms"]
    value = row["transaction_value"]
    incident_rate = row["incident_rate"]

    if (
        volume >= 1000
        and success_rate >= 98
        and latency < 500
    ):
        return "High-Value Healthy"

    if (
        value >= 500000
        and success_rate < 95
    ):
        return "High-Value At-Risk"

    if (
        success_rate < 90
        or incident_rate >= 5
    ):
        return "Operationally At-Risk"

    if (
        latency >= 1000
    ):
        return "High-Latency"

    if volume < 100:
        return "Low-Volume"

    return "Stable"


def apply_business_segments(
    features: pd.DataFrame,
) -> pd.DataFrame:

    result = features.copy()

    result["business_segment"] = (
        result.apply(
            classify_merchant,
            axis=1,
        )
    )

    return result