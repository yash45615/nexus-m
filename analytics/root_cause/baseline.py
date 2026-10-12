import pandas as pd


def prepare_transaction_data(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    df = transactions.copy()

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    df["date"] = (
        df["created_at"]
        .dt.date
    )

    df["is_success"] = (
        df["status"]
        .astype(str)
        .str.lower()
        .eq("success")
    )

    df["is_failure"] = ~df["is_success"]

    return df


def calculate_period_metrics(
    df: pd.DataFrame,
) -> dict:

    total = len(df)

    if total == 0:
        return {
            "transaction_count": 0,
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "transaction_value": 0.0,
        }

    successful = int(
        df["is_success"].sum()
    )

    return {
        "transaction_count": total,

        "success_rate": (
            successful / total * 100
        ),

        "failure_rate": (
            (total - successful)
            / total
            * 100
        ),

        "transaction_value": float(
            df["transaction_amount"].sum()
        ),
    }


def compare_periods(
    baseline: pd.DataFrame,
    incident: pd.DataFrame,
) -> dict:

    baseline_metrics = (
        calculate_period_metrics(
            baseline
        )
    )

    incident_metrics = (
        calculate_period_metrics(
            incident
        )
    )

    return {
        "baseline": baseline_metrics,
        "incident": incident_metrics,
        "failure_rate_change": (
            incident_metrics["failure_rate"]
            - baseline_metrics["failure_rate"]
        ),
        "success_rate_change": (
            incident_metrics["success_rate"]
            - baseline_metrics["success_rate"]
        ),
        "transaction_value_change": (
            incident_metrics["transaction_value"]
            - baseline_metrics["transaction_value"]
        ),
    }