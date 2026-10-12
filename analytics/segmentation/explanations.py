import pandas as pd


def describe_cluster(row: pd.Series) -> str:

    success_rate = row["success_rate"]
    value = row["transaction_value"]
    latency = row["p95_latency_ms"]
    failure_rate = row["failure_rate"]

    if (
        success_rate >= 98
        and latency < 500
    ):
        return "Healthy high-performing merchants"

    if (
        failure_rate >= 10
        and value >= 500000
    ):
        return "High-value merchants with elevated failure risk"

    if latency >= 1000:
        return "Merchants experiencing elevated processing latency"

    if value >= 500000:
        return "High-value merchants requiring close monitoring"

    return "Moderate behavioral profile"


def add_cluster_explanations(
    clustered: pd.DataFrame,
    profiles: pd.DataFrame,
) -> pd.DataFrame:

    profiles = profiles.copy()

    profiles["cluster_description"] = (
        profiles.apply(
            describe_cluster,
            axis=1,
        )
    )

    result = clustered.merge(
        profiles[
            [
                "cluster_id",
                "cluster_description",
            ]
        ],
        on="cluster_id",
        how="left",
    )

    return result