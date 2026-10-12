from __future__ import annotations

import json
from pathlib import Path

from analytics.kpi_engine.data_loader import (
    AnalyticsDataLoader,
)

from analytics.reconciliation.matching import (
    match_transactions_to_settlements,
)

from analytics.reconciliation.rules import (
    apply_reconciliation_rules,
)

from analytics.reconciliation.exceptions import (
    classify_exceptions,
    summarize_exceptions,
)

from analytics.reconciliation.scoring import (
    calculate_reconciliation_score,
    calculate_financial_exposure,
)


OUTPUT_DIR = Path(
    "data/processed/phase12"
)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("NEXUS-M PHASE 12")
    print("RECONCILIATION ENGINE")
    print("=" * 70)

    loader = AnalyticsDataLoader()

    transactions = (
        loader.load_transactions()
    )

    settlements = (
        loader.load_settlements()
    )

    print()
    print(
        f"Transactions: {len(transactions):,}"
    )

    print(
        f"Settlements:  {len(settlements):,}"
    )

    # ---------------------------------------------------------
    # MATCH
    # ---------------------------------------------------------

    print()
    print("Matching transactions to settlements...")

    matched = match_transactions_to_settlements(
        transactions,
        settlements,
    )

    # ---------------------------------------------------------
    # RULES
    # ---------------------------------------------------------

    print(
        "Applying reconciliation rules..."
    )

    reconciled = apply_reconciliation_rules(
        matched
    )

    # ---------------------------------------------------------
    # CLASSIFICATION
    # ---------------------------------------------------------

    print(
        "Classifying exceptions..."
    )

    classified = classify_exceptions(
        reconciled
    )

    # ---------------------------------------------------------
    # SCORING
    # ---------------------------------------------------------

    print(
        "Calculating reconciliation score..."
    )

    scored = calculate_reconciliation_score(
        classified
    )

    # ---------------------------------------------------------
    # OUTPUT 1
    # ---------------------------------------------------------

    detail_path = (
        OUTPUT_DIR
        / "reconciliation_details.csv"
    )

    scored.to_csv(
        detail_path,
        index=False,
    )

    # ---------------------------------------------------------
    # OUTPUT 2
    # ---------------------------------------------------------

    exception_summary = (
        summarize_exceptions(
            scored
        )
    )

    summary_path = (
        OUTPUT_DIR
        / "exception_summary.csv"
    )

    exception_summary.to_csv(
        summary_path,
        index=False,
    )

    # ---------------------------------------------------------
    # FINANCIAL SUMMARY
    # ---------------------------------------------------------

    financial_exposure = (
        calculate_financial_exposure(
            scored
        )
    )

    # ---------------------------------------------------------
    # GLOBAL SUMMARY
    # ---------------------------------------------------------

    matched_count = int(
        (~scored["reconciliation_exception"])
        .sum()
    )

    exception_count = int(
        scored["reconciliation_exception"]
        .sum()
    )

    total_count = len(scored)

    match_rate = (
        matched_count / total_count
        if total_count
        else 1
    )

    summary = {
        **financial_exposure,
        "matched_transactions": matched_count,
        "match_rate": match_rate,
        "reconciliation_score": float(
            scored[
                "reconciliation_score"
            ].iloc[0]
            if len(scored)
            else 100
        ),
        "reconciliation_status": (
            str(
                scored[
                    "reconciliation_status"
                ].iloc[0]
            )
            if len(scored)
            else "HEALTHY"
        ),
        "exception_breakdown": {
            row["exception_type"]:
                int(row["transaction_count"])
            for _, row
            in exception_summary.iterrows()
        },
    }

    with open(
        OUTPUT_DIR
        / "reconciliation_summary.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    # ---------------------------------------------------------
    # PRINT RESULTS
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("RECONCILIATION RESULTS")
    print("=" * 70)

    print()
    print(
        f"Matched transactions: "
        f"{matched_count:,}"
    )

    print(
        f"Exception transactions: "
        f"{exception_count:,}"
    )

    print(
        f"Match rate: "
        f"{match_rate:.2%}"
    )

    print(
        f"Reconciliation score: "
        f"{summary['reconciliation_score']:.2f}"
    )

    print(
        f"Status: "
        f"{summary['reconciliation_status']}"
    )

    print()
    print(
        "Absolute amount discrepancy: "
        f"{financial_exposure['absolute_amount_difference']:,.2f}"
    )

    print()
    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()
    print(
        "PHASE 12 COMPLETE"
    )


if __name__ == "__main__":
    main()