from __future__ import annotations

import pandas as pd


def prepare_opportunity_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare transaction-level data for opportunity sizing.
    """

    data = df.copy()

    data["created_at"] = pd.to_datetime(
        data["created_at"],
        errors="coerce",
    )

    data["transaction_amount"] = pd.to_numeric(
        data["transaction_amount"],
        errors="coerce",
    ).fillna(0)

    data["status"] = (
        data["status"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    data["is_success"] = data["status"].isin(
        ["success", "successful", "approved", "completed"]
    )

    data["is_failure"] = ~data["is_success"]

    data["transaction_date"] = data["created_at"].dt.date

    data["failed_value"] = data["transaction_amount"].where(
        data["is_failure"],
        0,
    )

    data["successful_value"] = data["transaction_amount"].where(
        data["is_success"],
        0,
    )

    return data


def calculate_dimension_features(
    df: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    """
    Calculate opportunity-related metrics for a dimension.
    """

    if dimension not in df.columns:
        raise ValueError(
            f"Dimension '{dimension}' does not exist in the dataset."
        )

    grouped = (
        df.groupby(dimension, dropna=False)
        .agg(
            transaction_count=("transaction_amount", "size"),
            transaction_value=("transaction_amount", "sum"),
            failed_transactions=("is_failure", "sum"),
            failed_value=("failed_value", "sum"),
            successful_transactions=("is_success", "sum"),
            successful_value=("successful_value", "sum"),
        )
        .reset_index()
    )

    grouped["failure_rate"] = (
        grouped["failed_transactions"]
        / grouped["transaction_count"].replace(0, pd.NA)
    )

    grouped["average_transaction_value"] = (
        grouped["transaction_value"]
        / grouped["transaction_count"].replace(0, pd.NA)
    )

    grouped["value_at_risk"] = grouped["failed_value"]

    return grouped