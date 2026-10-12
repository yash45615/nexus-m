import pandas as pd


def calculate_contribution(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    total_change = (
        result["failure_change"]
        .sum()
    )

    if total_change == 0:

        result["contribution_pct"] = 0.0

        return result

    result["contribution_pct"] = (
        result["failure_change"]
        / total_change
        * 100
    )

    result["contribution_pct"] = (
        result["contribution_pct"]
        .clip(lower=0)
    )

    return result.sort_values(
        "contribution_pct",
        ascending=False,
    )


def top_contributors(
    df: pd.DataFrame,
    n: int = 10,
) -> pd.DataFrame:

    return (
        df
        .sort_values(
            "contribution_pct",
            ascending=False,
        )
        .head(n)
    )