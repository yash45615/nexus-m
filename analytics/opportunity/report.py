from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analytics.kpi_engine.data_loader import AnalyticsDataLoader
from analytics.opportunity.features import (
    prepare_opportunity_data,
    calculate_dimension_features,
)
from analytics.opportunity.sizing import (
    build_opportunity_table,
)
from analytics.opportunity.recovery import (
    calculate_recoverable_value,
    calculate_confidence_scenarios,
)
from analytics.opportunity.scoring import (
    calculate_opportunity_score,
)


OUTPUT_DIR = Path("data/processed/phase11")

DIMENSIONS = {
    "merchant": "merchant_key",
    "partner": "partner_key",
    "region": "region_key",
}


def process_dimension(
    df: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:

    features = calculate_dimension_features(
        df,
        dimension,
    )

    result = build_opportunity_table(
        features,
        target_failure_rate=0.02,
    )

    result = calculate_recoverable_value(result)

    result = calculate_confidence_scenarios(result)

    result = calculate_opportunity_score(result)

    return result.sort_values(
        "opportunity_score",
        ascending=False,
    )


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    loader = AnalyticsDataLoader()

    transactions = loader.load_transactions()

    print("=" * 70)
    print("NEXUS-M PHASE 11")
    print("OPPORTUNITY SIZING ENGINE")
    print("=" * 70)

    print()
    print("Transactions loaded:", len(transactions))

    data = prepare_opportunity_data(
        transactions
    )

    outputs = {}

    for name, dimension in DIMENSIONS.items():

        print()
        print(f"Calculating {name} opportunities...")

        result = process_dimension(
            data,
            dimension,
        )

        outputs[name] = result

        path = OUTPUT_DIR / f"{name}_opportunities.csv"

        result.to_csv(
            path,
            index=False,
        )

        print(
            f"Saved: {path}"
        )

    # Create a unified opportunity table

    opportunity_tables = []

    for name, table in outputs.items():

        temp = table.copy()

        temp["dimension_type"] = name

        temp["dimension_value"] = (
            temp[DIMENSIONS[name]].astype(str)
        )

        opportunity_tables.append(
            temp
        )

    opportunities = pd.concat(
        opportunity_tables,
        ignore_index=True,
    )

    opportunities = opportunities.sort_values(
        "opportunity_score",
        ascending=False,
    )

    opportunities["global_rank"] = range(
        1,
        len(opportunities) + 1,
    )

    opportunity_path = (
        OUTPUT_DIR
        / "opportunity_priorities.csv"
    )

    opportunities.to_csv(
        opportunity_path,
        index=False,
    )

    # Summary

    summary = {
        "total_value_at_risk": float(
            opportunities["value_at_risk"].sum()
        ),
        "total_recoverable_value": float(
            opportunities["recoverable_value"].sum()
        ),
        "total_low_case_value": float(
            opportunities["low_case_recoverable_value"].sum()
        ),
        "total_high_case_value": float(
            opportunities["high_case_recoverable_value"].sum()
        ),
        "total_failed_transactions": int(
            opportunities["failed_transactions"].sum()
        ),
        "critical_opportunities": int(
            (opportunities["priority"] == "CRITICAL").sum()
        ),
        "high_opportunities": int(
            (opportunities["priority"] == "HIGH").sum()
        ),
        "medium_opportunities": int(
            (opportunities["priority"] == "MEDIUM").sum()
        ),
        "low_opportunities": int(
            (opportunities["priority"] == "LOW").sum()
        ),
    }

    with open(
        OUTPUT_DIR / "opportunity_summary.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    print()
    print("=" * 70)
    print("PHASE 11 COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Value at risk: "
        f"{summary['total_value_at_risk']:,.2f}"
    )

    print(
        f"Recoverable value: "
        f"{summary['total_recoverable_value']:,.2f}"
    )

    print(
        f"Critical opportunities: "
        f"{summary['critical_opportunities']}"
    )

    print()
    print(
        f"Output directory: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()