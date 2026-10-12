from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analytics.data_quality.checks import (
    check_row_count,
    check_nulls,
    check_duplicates,
    check_numeric_range,
    check_allowed_values,
    check_negative_values,
    check_timestamp_validity,
)

from analytics.data_quality.schema_checks import (
    check_required_columns,
    check_no_unexpected_columns,
    infer_column_types,
)

from analytics.data_quality.quality_score import (
    calculate_quality_score,
    results_to_dataframe,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "governance"
    / "quality_reports"
)


def run_quality_checks():

    print("=" * 70)
    print("NEXUS-M DATA QUALITY ENGINE")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    transactions_path = (
        DATA_DIR
        / "transactions.csv"
    )

    print("\nLoading transactions...")

    df = pd.read_csv(
        transactions_path,
    )

    print(
        f"Rows loaded: {len(df):,}"
    )

    print(
        f"Columns loaded: {len(df.columns)}"
    )

    results = []

    # ---------------------------------------------------------
    # SCHEMA
    # ---------------------------------------------------------

    required_columns = [
        "transaction_id",
        "transaction_amount",
        "processing_time_ms",
        "status",
        "created_at",
    ]

    results.append(
        check_required_columns(
            df,
            required_columns,
        )
    )

    results.append(
        check_no_unexpected_columns(
            df,
            list(df.columns),
        )
    )

    # ---------------------------------------------------------
    # COMPLETENESS
    # ---------------------------------------------------------

    results.append(
        check_row_count(
            df,
            minimum_rows=1,
        )
    )

    results.extend(
        check_nulls(
            df,
            max_null_percentage=5.0,
        )
    )

    # ---------------------------------------------------------
    # UNIQUENESS
    # ---------------------------------------------------------

    results.append(
        check_duplicates(
            df,
            "transaction_id",
        )
    )

    # ---------------------------------------------------------
    # VALIDITY
    # ---------------------------------------------------------

    results.append(
        check_numeric_range(
            df,
            "transaction_amount",
            minimum=0,
        )
    )

    results.append(
        check_numeric_range(
            df,
            "processing_time_ms",
            minimum=0,
            maximum=60000,
        )
    )

    results.append(
        check_allowed_values(
            df,
            "status",
            [
                "SUCCESS",
                "FAILED",
            ],
        )
    )

    results.append(
        check_negative_values(
            df,
            "transaction_amount",
        )
    )

    results.append(
        check_timestamp_validity(
            df,
            "created_at",
        )
    )

    # ---------------------------------------------------------
    # QUALITY SCORE
    # ---------------------------------------------------------

    score = calculate_quality_score(
        results
    )

    print("\nDATA QUALITY SCORE")
    print("-" * 40)

    print(
        f"Score: {score['quality_score']:.2f}%"
    )

    print(
        f"Status: {score['status']}"
    )

    print(
        f"Total checks: {score['total_checks']}"
    )

    print(
        f"Passed: {score['passed_checks']}"
    )

    print(
        f"Failed: {score['failed_checks']}"
    )

    print(
        f"Warnings: {score['warning_checks']}"
    )

    # ---------------------------------------------------------
    # SAVE CHECK RESULTS
    # ---------------------------------------------------------

    results_df = results_to_dataframe(
        results
    )

    results_df.to_csv(
        OUTPUT_DIR
        / "transactions_quality_results.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # SAVE JSON REPORT
    # ---------------------------------------------------------

    report = {
        "dataset": "transactions",
        "source": str(
            transactions_path
        ),
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_types": infer_column_types(df),
        "quality_summary": score,
        "checks": results,
    }

    with open(
        OUTPUT_DIR
        / "transactions_quality_report.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str,
        )

    print(
        "\nQuality report saved to:"
    )

    print(
        OUTPUT_DIR
        / "transactions_quality_report.json"
    )

    return report


if __name__ == "__main__":

    run_quality_checks()