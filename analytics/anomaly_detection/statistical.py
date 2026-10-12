import numpy as np
import pandas as pd


def rolling_z_score(
    series: pd.Series,
    window: int = 7,
) -> pd.Series:

    rolling_mean = (
        series
        .rolling(
            window=window,
            min_periods=3,
        )
        .mean()
    )

    rolling_std = (
        series
        .rolling(
            window=window,
            min_periods=3,
        )
        .std()
    )

    rolling_std = rolling_std.replace(
        0,
        np.nan,
    )

    z_score = (
        series - rolling_mean
    ) / rolling_std

    return z_score.fillna(0)


def detect_statistical_anomalies(
    daily: pd.DataFrame,
    columns: list[str],
    threshold: float = 3.0,
) -> pd.DataFrame:

    result = daily.copy()

    for column in columns:

        z_column = (
            f"{column}_zscore"
        )

        anomaly_column = (
            f"{column}_anomaly"
        )

        result[z_column] = (
            rolling_z_score(
                result[column]
            )
        )

        result[anomaly_column] = (
            result[z_column].abs()
            >= threshold
        )

    anomaly_columns = [
        f"{column}_anomaly"
        for column in columns
    ]

    result["statistical_anomaly"] = (
        result[anomaly_columns]
        .any(axis=1)
    )

    result["anomaly_count"] = (
        result[anomaly_columns]
        .sum(axis=1)
    )

    return result