import json
from pathlib import Path

import pandas as pd

from analytics.kpi_engine.data_loader import (
    AnalyticsDataLoader,
)

from analytics.root_cause.baseline import (
    prepare_transaction_data,
    compare_periods,
)

from analytics.root_cause.drilldown import (
    RootCauseDrilldown,
)

from analytics.root_cause.contribution import (
    calculate_contribution,
    top_contributors,
)

from analytics.root_cause.scoring import (
    calculate_root_cause_score,
)

from analytics.root_cause.narrative import (
    generate_narrative,
)


OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "phase10"
)


DIMENSIONS = [
    "partner_key",
    "region_key",
    "category_key",
    "error_code",
    "merchant_key",
]


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    loader = AnalyticsDataLoader()

    transactions = (
        loader.load_transactions()
    )

    df = prepare_transaction_data(
        transactions
    )

    dates = sorted(
        df["date"].unique()
    )

    if len(dates) < 4:

        raise ValueError(
            "At least four dates are required "
            "for root-cause analysis."
        )

    # Use the final period as the incident
    # and previous periods as baseline.

    incident_date = dates[-1]

    baseline_dates = dates[:-1]

    baseline = df[
        df["date"].isin(
            baseline_dates
        )
    ].copy()

    incident = df[
        df["date"] == incident_date
    ].copy()

    # --------------------------------
    # Overall comparison
    # --------------------------------

    comparison = compare_periods(
        baseline,
        incident,
    )

    with open(
        OUTPUT_DIR / "period_comparison.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            comparison,
            file,
            indent=4,
            default=str,
        )

    # --------------------------------
    # Dimension investigation
    # --------------------------------

    drilldown = RootCauseDrilldown(
        baseline,
        incident,
    )

    narratives = {}

    for dimension in DIMENSIONS:

        # Some synthetic datasets may have
        # null error codes.
        if dimension not in df.columns:
            continue

        result = drilldown.analyze_dimension(
            dimension
        )

        result = calculate_contribution(
            result
        )

        result = calculate_root_cause_score(
            result
        )

        result.to_csv(
            OUTPUT_DIR
            / f"{dimension}_root_causes.csv",
            index=False,
        )

        top = top_contributors(
            result,
            n=10,
        )

        narratives[dimension] = (
            generate_narrative(
                dimension,
                top,
            )
        )

    with open(
        OUTPUT_DIR
        / "investigation_narratives.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            narratives,
            file,
            indent=4,
        )

    print(
        "Phase 10 Root-Cause Investigation completed."
    )

    print(
        f"Incident date: {incident_date}"
    )

    print()

    print(
        "Overall comparison:"
    )

    print(
        json.dumps(
            comparison,
            indent=4,
        )
    )

    print()

    print(
        "Investigation narratives:"
    )

    for dimension, narrative in narratives.items():

        print()
        print(
            f"[{dimension}]"
        )
        print(narrative)


if __name__ == "__main__":
    main()