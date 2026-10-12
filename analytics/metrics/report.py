import json
from pathlib import Path

from analytics.kpi_engine.data_loader import AnalyticsDataLoader
from analytics.metrics.calculator import KPICalculator
from analytics.metrics.dimensions import DimensionKPIEngine
from analytics.metrics.thresholds import evaluate_threshold


OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "phase7"
)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    loader = AnalyticsDataLoader()

    transactions = loader.load_transactions()

    calculator = KPICalculator(transactions)

    kpis = calculator.calculate_all()

    result = {}

    for metric, value in kpis.items():

        numeric_value = float(value)

        result[metric] = {
            "value": numeric_value,
            "status": evaluate_threshold(
                metric,
                numeric_value,
            ),
        }

    output_file = (
        OUTPUT_DIR
        / "kpi_summary.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )

    dimension_engine = DimensionKPIEngine(
        transactions
    )

    dimensions = [
        "partner_key",
        "merchant_key",
        "region_key",
        "category_key",
    ]

    for dimension in dimensions:

        result_df = dimension_engine.calculate(
            dimension
        )

        result_df.to_csv(
            OUTPUT_DIR
            / f"{dimension}_kpis.csv",
            index=False,
        )

    print("Phase 7 KPI engine completed.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()