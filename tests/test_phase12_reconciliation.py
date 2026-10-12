import pandas as pd

from analytics.reconciliation.matching import (
    match_transactions_to_settlements,
)

from analytics.reconciliation.rules import (
    apply_reconciliation_rules,
)

from analytics.reconciliation.exceptions import (
    classify_exceptions,
)

from analytics.reconciliation.scoring import (
    calculate_reconciliation_score,
)


def create_transactions():

    return pd.DataFrame(
        {
            "transaction_id": [
                "TX001",
                "TX002",
                "TX003",
                "TX004",
            ],
            "transaction_amount": [
                1000,
                2000,
                3000,
                4000,
            ],
            "created_at": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-01",
                    "2026-01-01",
                    "2026-01-01",
                ]
            ),
        }
    )


def create_settlements():

    return pd.DataFrame(
        {
            "transaction_id": [
                "TX001",
                "TX002",
                "TX002",
                "TX004",
            ],
            "settlement_amount": [
                1000,
                1800,
                200,
                4000,
            ],
            "settlement_date": pd.to_datetime(
                [
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-15",
                ]
            ),
            "created_at": pd.to_datetime(
                [
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-15",
                ]
            ),
        }
    )


def test_transaction_settlement_matching():

    transactions = create_transactions()

    settlements = create_settlements()

    result = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    assert len(result) == 4

    assert result[
        "settlement_found"
    ].sum() == 3


def test_missing_settlement():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    result = apply_reconciliation_rules(
        matched
    )

    tx003 = result[
        result["transaction_id"] == "TX003"
    ].iloc[0]

    assert bool(tx003["missing_settlement"]) is True


def test_duplicate_settlement():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    result = apply_reconciliation_rules(
        matched
    )

    tx002 = result[
        result["transaction_id"] == "TX002"
    ].iloc[0]

    assert bool(tx002["duplicate_settlement"]) is True


def test_amount_difference():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    result = apply_reconciliation_rules(
        matched
    )

    tx002 = result[
        result["transaction_id"] == "TX002"
    ].iloc[0]

    assert (
        tx002[
            "amount_difference"
        ]
        == 0
    )


def test_timing_mismatch():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    result = apply_reconciliation_rules(
        matched,
        timing_tolerance_days=7,
    )

    tx004 = result[
        result["transaction_id"] == "TX004"
    ].iloc[0]

    assert bool(tx004["timing_mismatch"]) is True


def test_exception_classification():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    rules = apply_reconciliation_rules(
        matched
    )

    result = classify_exceptions(
        rules
    )

    assert (
        "exception_type"
        in result.columns
    )

    assert (
        "MISSING_SETTLEMENT"
        in result["exception_type"].values
    )


def test_reconciliation_score():

    transactions = create_transactions()

    settlements = create_settlements()

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    rules = apply_reconciliation_rules(
        matched
    )

    classified = classify_exceptions(
        rules
    )

    result = calculate_reconciliation_score(
        classified
    )

    assert (
        "reconciliation_score"
        in result.columns
    )

    assert (
        result["reconciliation_score"]
        .between(0, 100)
        .all()
    )