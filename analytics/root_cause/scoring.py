import pandas as pd


def min_max_normalize(
    series: pd.Series,
) -> pd.Series:

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            0.0,
            index=series.index,
        )

    return (
        (series - minimum)
        / (maximum - minimum)
    )


def calculate_root_cause_score(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result["contribution_score"] = (
        min_max_normalize(
            result["contribution_pct"]
        )
    )

    result["failure_score"] = (
        min_max_normalize(
            result["failure_change"]
            .clip(lower=0)
        )
    )

    result["value_score"] = (
        min_max_normalize(
            result["incident_value"]
            .clip(lower=0)
        )
    )

    result["rate_score"] = (
        min_max_normalize(
            result["failure_rate_change"]
            .clip(lower=0)
        )
    )

    result["root_cause_score"] = (
        result["contribution_score"] * 0.40
        + result["failure_score"] * 0.25
        + result["value_score"] * 0.20
        + result["rate_score"] * 0.15
    )

    return result.sort_values(
        "root_cause_score",
        ascending=False,
    )