import json
from datetime import datetime, timezone

import pandas as pd

from scripts.bootstrap import PROJECT_ROOT
from app.data_config import (
    SYNTHETIC_DATA_DIR,
    PROCESSED_DATA_DIR,
)


TRANSACTIONS_FILE = SYNTHETIC_DATA_DIR / "transactions.csv"
OUTPUT_FILE = PROCESSED_DATA_DIR / "analytical_summary.json"


def calculate_percentile(
    series: pd.Series,
    percentile: float,
) -> float:
    """
    Calculate a percentile and round the result
    for stable machine-readable KPI output.
    """

    return round(
        float(series.quantile(percentile)),
        2,
    )


def build_analytical_summary() -> dict:
    """
    Build the NEXUS-M machine-readable analytical KPI summary.
    """

    if not TRANSACTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Transaction dataset not found: "
            f"{TRANSACTIONS_FILE}"
        )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.read_csv(TRANSACTIONS_FILE)

    if df.empty:
        raise ValueError(
            "Transaction dataset is empty."
        )

    required_columns = {
        "transaction_id",
        "transaction_amount",
        "processing_time_ms",
        "status",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required transaction columns: "
            f"{sorted(missing_columns)}"
        )

    total_transactions = int(len(df))

    successful_transactions = int(
        (df["status"] == "SUCCESS").sum()
    )

    failed_transactions = int(
        (df["status"] == "FAILED").sum()
    )

    authorization_rate = (
        successful_transactions
        / total_transactions
        if total_transactions
        else 0.0
    )

    decline_rate = (
        failed_transactions
        / total_transactions
        if total_transactions
        else 0.0
    )

    total_transaction_value = float(
        df["transaction_amount"].sum()
    )

    average_transaction_value = float(
        df["transaction_amount"].mean()
    )

    average_processing_time = float(
        df["processing_time_ms"].mean()
    )

    p95_processing_time = calculate_percentile(
        df["processing_time_ms"],
        0.95,
    )

    p99_processing_time = calculate_percentile(
        df["processing_time_ms"],
        0.99,
    )

    incident_count = 0

    if "incident_flag" in df.columns:
        incident_count = int(
            df["incident_flag"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    weekend_transaction_count = 0

    if "weekend_flag" in df.columns:
        weekend_transaction_count = int(
            df["weekend_flag"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    summary = {
        "metadata": {
            "project": "NEXUS-M",
            "dataset": "synthetic_transactions",
            "generated_at": (
                datetime.now(timezone.utc).isoformat()
            ),
            "source_file": str(
                TRANSACTIONS_FILE
            ),
            "record_count": total_transactions,
        },

        "transaction_kpis": {
            "total_transactions": (
                total_transactions
            ),
            "successful_transactions": (
                successful_transactions
            ),
            "failed_transactions": (
                failed_transactions
            ),
            "authorization_rate": round(
                authorization_rate,
                4,
            ),
            "decline_rate": round(
                decline_rate,
                4,
            ),
            "total_transaction_value": round(
                total_transaction_value,
                2,
            ),
            "average_transaction_value": round(
                average_transaction_value,
                2,
            ),
        },

        "performance_kpis": {
            "average_processing_time_ms": round(
                average_processing_time,
                2,
            ),
            "p95_processing_time_ms": (
                p95_processing_time
            ),
            "p99_processing_time_ms": (
                p99_processing_time
            ),
        },

        "risk_kpis": {
            "incident_count": incident_count,
        },

        "behavioral_kpis": {
            "weekend_transaction_count": (
                weekend_transaction_count
            ),
            "weekend_transaction_share": round(
                (
                    weekend_transaction_count
                    / total_transactions
                )
                if total_transactions
                else 0.0,
                4,
            ),
        },
    }

    return summary


def main():
    print(
        "Building NEXUS-M analytical summary..."
    )

    summary = build_analytical_summary()

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    print(
        "\nAnalytical summary created successfully:"
    )

    print(OUTPUT_FILE)

    print("\nKPI Summary")
    print("-" * 50)

    transaction_kpis = (
        summary["transaction_kpis"]
    )

    performance_kpis = (
        summary["performance_kpis"]
    )

    risk_kpis = (
        summary["risk_kpis"]
    )

    behavioral_kpis = (
        summary["behavioral_kpis"]
    )

    print(
        f"Transactions       : "
        f"{transaction_kpis['total_transactions']:,}"
    )

    print(
        f"Successful         : "
        f"{transaction_kpis['successful_transactions']:,}"
    )

    print(
        f"Failed             : "
        f"{transaction_kpis['failed_transactions']:,}"
    )

    print(
        f"Authorization rate : "
        f"{transaction_kpis['authorization_rate']:.2%}"
    )

    print(
        f"Decline rate       : "
        f"{transaction_kpis['decline_rate']:.2%}"
    )

    print(
        f"Total value        : "
        f"{transaction_kpis['total_transaction_value']:,.2f}"
    )

    print(
        f"Average value      : "
        f"{transaction_kpis['average_transaction_value']:,.2f}"
    )

    print(
        f"Average processing : "
        f"{performance_kpis['average_processing_time_ms']:.2f} ms"
    )

    print(
        f"P95 processing     : "
        f"{performance_kpis['p95_processing_time_ms']:.2f} ms"
    )

    print(
        f"P99 processing     : "
        f"{performance_kpis['p99_processing_time_ms']:.2f} ms"
    )

    print(
        f"Incidents          : "
        f"{risk_kpis['incident_count']:,}"
    )

    print(
        f"Weekend txns       : "
        f"{behavioral_kpis['weekend_transaction_count']:,}"
    )

    print(
        f"Weekend share      : "
        f"{behavioral_kpis['weekend_transaction_share']:.2%}"
    )


if __name__ == "__main__":
    main()