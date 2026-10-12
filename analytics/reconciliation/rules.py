from __future__ import annotations

import pandas as pd


DEFAULT_AMOUNT_TOLERANCE = 0.01
DEFAULT_TIMING_TOLERANCE_DAYS = 7


def apply_reconciliation_rules(
    df: pd.DataFrame,
    amount_tolerance: float = DEFAULT_AMOUNT_TOLERANCE,
    timing_tolerance_days: int = DEFAULT_TIMING_TOLERANCE_DAYS,
) -> pd.DataFrame:

    result = df.copy()

    # ---------------------------------------------------------
    # 1. Missing settlement
    # ---------------------------------------------------------

    result["missing_settlement"] = (
        ~result["settlement_found"]
    )

    # ---------------------------------------------------------
    # 2. Duplicate settlement
    # ---------------------------------------------------------

    result["duplicate_settlement"] = (
        result["settlement_record_count"] > 1
    )

    # ---------------------------------------------------------
    # 3. Amount difference
    # ---------------------------------------------------------

    result["amount_difference"] = (
        result["transaction_amount"]
        - result["settlement_amount"]
    )

    result["absolute_amount_difference"] = (
        result["amount_difference"].abs()
    )

    result["amount_mismatch"] = (
        result["settlement_found"]
        & (
            result["absolute_amount_difference"]
            > amount_tolerance
        )
    )

    # ---------------------------------------------------------
    # 4. Timing difference
    # ---------------------------------------------------------

    result["settlement_delay_days"] = (
        result["settlement_date"]
        - result["created_at"].dt.normalize()
    ).dt.days

    result["timing_mismatch"] = (
        result["settlement_found"]
        & result["settlement_delay_days"].notna()
        & (
            result["settlement_delay_days"]
            > timing_tolerance_days
        )
    )

    # ---------------------------------------------------------
    # 5. Overall exception
    # ---------------------------------------------------------

    result["reconciliation_exception"] = (
        result["missing_settlement"]
        | result["duplicate_settlement"]
        | result["amount_mismatch"]
        | result["timing_mismatch"]
    )

    return result