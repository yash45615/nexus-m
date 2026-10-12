from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

BI_DIR = (
    PROJECT_ROOT
    / "dashboards"
    / "powerbi"
    / "data"
)


def ensure_directory() -> None:
    BI_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def copy_csv(
    source: Path,
    destination_name: str,
) -> None:

    if not source.exists():
        print(
            f"WARNING: source not found: {source}"
        )
        return

    destination = (
        BI_DIR
        / destination_name
    )

    df = pd.read_csv(source)

    df.to_csv(
        destination,
        index=False,
    )

    print(
        f"Exported {destination_name}: "
        f"{len(df):,} rows"
    )


def export_transactions() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase4"
        / "daily_transaction_trend.csv",
        "daily_transaction_trend.csv",
    )


def export_partners() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase4"
        / "partner_performance.csv",
        "partner_performance.csv",
    )


def export_regions() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase4"
        / "regional_performance.csv",
        "regional_performance.csv",
    )


def export_merchants() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase8"
        / "merchant_segments.csv",
        "merchant_segments.csv",
    )


def export_anomalies() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase9"
        / "anomaly_results.csv",
        "anomaly_results.csv",
    )


def export_opportunities() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase11"
        / "opportunity_priorities.csv",
        "opportunity_priorities.csv",
    )


def export_reconciliation() -> None:

    copy_csv(
        PROCESSED_DIR
        / "phase12"
        / "reconciliation_details.csv",
        "reconciliation_details.csv",
    )


def export_root_causes() -> None:

    dimensions = [
        "partner_key",
        "region_key",
        "category_key",
        "error_code",
        "merchant_key",
    ]

    for dimension in dimensions:

        copy_csv(
            PROCESSED_DIR
            / "phase10"
            / f"{dimension}_root_causes.csv",
            f"{dimension}_root_causes.csv",
        )


def export_kpis() -> None:

    source = (
        PROCESSED_DIR
        / "phase7"
        / "kpi_summary.json"
    )

    if not source.exists():

        source = (
            PROCESSED_DIR
            / "phase4"
            / "core_kpis.json"
        )

    if not source.exists():

        print(
            "WARNING: KPI summary not found."
        )
        return

    destination = (
        BI_DIR
        / "kpi_summary.json"
    )

    destination.write_text(
        source.read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    print(
        "Exported kpi_summary.json"
    )


def export() -> None:

    ensure_directory()

    export_transactions()
    export_partners()
    export_regions()
    export_merchants()
    export_anomalies()
    export_opportunities()
    export_reconciliation()
    export_root_causes()
    export_kpis()

    print()
    print(
        "NEXUS-M Power BI export completed."
    )


if __name__ == "__main__":
    export()