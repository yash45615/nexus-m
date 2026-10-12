import pandas as pd


def calculate_severity(row: pd.Series) -> str:

    statistical = bool(
        row.get(
            "statistical_anomaly",
            False,
        )
    )

    ml = bool(
        row.get(
            "ml_anomaly",
            False,
        )
    )

    anomaly_count = int(
        row.get(
            "anomaly_count",
            0,
        )
    )

    score = float(
        row.get(
            "anomaly_score",
            0,
        )
    )

    if (
        statistical
        and ml
        and anomaly_count >= 3
    ):
        return "CRITICAL"

    if (
        statistical
        and ml
    ):
        return "HIGH"

    if (
        statistical
        or ml
        or score >= 0.15
    ):
        return "MEDIUM"

    return "NORMAL"


def add_severity(
    anomalies: pd.DataFrame,
) -> pd.DataFrame:

    result = anomalies.copy()

    result["severity"] = (
        result.apply(
            calculate_severity,
            axis=1,
        )
    )

    return result