from __future__ import annotations

import pandas as pd


def prepare_transactions(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    df = transactions.copy()

    df["transaction_id"] = (
        df["transaction_id"]
        .astype(str)
        .str.strip()
    )

    df["transaction_amount"] = pd.to_numeric(
        df["transaction_amount"],
        errors="coerce",
    ).fillna(0)

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    return df


def prepare_settlements(
    settlements: pd.DataFrame,
) -> pd.DataFrame:

    df = settlements.copy()

    df["transaction_id"] = (
        df["transaction_id"]
        .astype(str)
        .str.strip()
    )

    df["settlement_amount"] = pd.to_numeric(
        df["settlement_amount"],
        errors="coerce",
    ).fillna(0)

    df["settlement_date"] = pd.to_datetime(
        df["settlement_date"],
        errors="coerce",
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    return df


def aggregate_duplicate_settlements(
    settlements: pd.DataFrame,
) -> pd.DataFrame:

    duplicate_counts = (
        settlements.groupby("transaction_id")
        .size()
        .reset_index(name="settlement_record_count")
    )

    result = (
        settlements.groupby("transaction_id")
        .agg(
            settlement_amount=(
                "settlement_amount",
                "sum",
            ),
            settlement_date=(
                "settlement_date",
                "min",
            ),
        )
        .reset_index()
    )

    result = result.merge(
        duplicate_counts,
        on="transaction_id",
        how="left",
    )

    return result


def match_transactions_to_settlements(
    transactions: pd.DataFrame,
    settlements: pd.DataFrame,
) -> pd.DataFrame:

    tx = prepare_transactions(transactions)

    st = prepare_settlements(settlements)

    settlement_agg = aggregate_duplicate_settlements(
        st
    )

    result = tx.merge(
        settlement_agg,
        on="transaction_id",
        how="left",
        indicator=True,
    )

    result["settlement_found"] = (
        result["_merge"] == "both"
    )

    result["settlement_record_count"] = (
        result["settlement_record_count"]
        .fillna(0)
        .astype(int)
    )

    result["settlement_amount"] = (
        result["settlement_amount"]
        .fillna(0)
    )

    result.drop(
        columns=["_merge"],
        inplace=True,
    )

    return result