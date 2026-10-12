import pandas as pd


def generate_narrative(
    dimension: str,
    result: pd.DataFrame,
) -> str:

    if result.empty:
        return (
            f"No significant {dimension} "
            "root cause was identified."
        )

    top = result.iloc[0]

    entity = top[dimension]

    contribution = float(
        top["contribution_pct"]
    )

    failure_change = float(
        top["failure_change"]
    )

    value = float(
        top["incident_value"]
    )

    rate_change = float(
        top["failure_rate_change"]
    )

    return (
        f"The strongest {dimension} contributor "
        f"was {entity}. It accounted for approximately "
        f"{contribution:.1f}% of the increase in failures, "
        f"with {failure_change:.0f} additional failures "
        f"and approximately {value:,.2f} in transaction "
        f"value during the incident period. Its failure "
        f"rate changed by {rate_change:.2f} percentage "
        f"points versus the baseline."
    )