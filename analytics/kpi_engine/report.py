from pathlib import Path

import pandas as pd

from analytics.kpi_engine.data_loader import (
    AnalyticsDataLoader,
)

from analytics.kpi_engine.transaction_metrics import (
    calculate_core_metrics,
)

from analytics.kpi_engine.dimension_analysis import (
    partner_performance,
    regional_performance,
    merchant_performance,
    category_performance,
    payment_method_performance,
    error_code_analysis,
)

from analytics.kpi_engine.trend_analysis import (
    daily_transaction_trend,
    incident_comparison,
)


OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "phase4"
)


def save_dataframe(
    df: pd.DataFrame,
    filename: str,
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = OUTPUT_DIR / filename

    df.to_csv(
        path,
        index=False,
    )

    print(
        f"Saved: {path}"
    )


def main():

    print("=" * 80)
    print("NEXUS-M PHASE 4 ANALYTICAL ENGINE")
    print("=" * 80)

    loader = AnalyticsDataLoader()

    print("\nLoading datasets...")

    transactions = (
        loader.load_transactions()
    )

    merchants = (
        loader.load_merchants()
    )

    partners = (
        loader.load_partners()
    )

    regions = (
        loader.load_regions()
    )

    categories = (
        loader.load_categories()
    )

    error_codes = (
        loader.load_error_codes()
    )

    print(
        f"Transactions loaded: "
        f"{len(transactions):,}"
    )

    # ========================================================
    # CORE KPIs
    # ========================================================

    print("\n" + "=" * 80)
    print("CORE KPIs")
    print("=" * 80)

    metrics = calculate_core_metrics(
        transactions
    )

    for name, value in metrics.items():
        print(
            f"{name:35s}: {value:,.2f}"
            if isinstance(value, float)
            else f"{name:35s}: {value:,}"
        )

    # ========================================================
    # PARTNER
    # ========================================================

    print("\n" + "=" * 80)
    print("PARTNER PERFORMANCE")
    print("=" * 80)

    partner_result = partner_performance(
        transactions,
        partners,
    )

    print(
        partner_result[
            [
                "partner_id",
                "partner_name",
                "transactions",
                "authorization_rate_pct",
                "failure_rate_pct",
                "average_latency_ms",
                "p95_latency_ms",
            ]
        ]
        .to_string(index=False)
    )

    save_dataframe(
        partner_result,
        "partner_performance.csv",
    )

    # ========================================================
    # REGION
    # ========================================================

    print("\n" + "=" * 80)
    print("REGIONAL PERFORMANCE")
    print("=" * 80)

    region_result = regional_performance(
        transactions,
        regions,
    )

    print(
        region_result[
            [
                "region_name",
                "transactions",
                "authorization_rate_pct",
                "failure_rate_pct",
                "average_latency_ms",
            ]
        ]
        .to_string(index=False)
    )

    save_dataframe(
        region_result,
        "regional_performance.csv",
    )

    # ========================================================
    # MERCHANT
    # ========================================================

    print("\n" + "=" * 80)
    print("TOP MERCHANTS BY TRANSACTION VALUE")
    print("=" * 80)

    merchant_result = merchant_performance(
        transactions,
        merchants,
    )

    print(
        merchant_result[
            [
                "merchant_id",
                "merchant_name",
                "merchant_category",
                "transaction_value",
                "transactions",
                "authorization_rate_pct",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    save_dataframe(
        merchant_result,
        "merchant_performance.csv",
    )

    # ========================================================
    # CATEGORY
    # ========================================================

    print("\n" + "=" * 80)
    print("CATEGORY PERFORMANCE")
    print("=" * 80)

    category_result = category_performance(
        transactions,
        categories,
    )

    print(
        category_result[
            [
                "category_name",
                "transactions",
                "transaction_value",
                "authorization_rate_pct",
                "failure_rate_pct",
            ]
        ]
        .to_string(index=False)
    )

    save_dataframe(
        category_result,
        "category_performance.csv",
    )

    # ========================================================
    # PAYMENT METHOD
    # ========================================================

    print("\n" + "=" * 80)
    print("PAYMENT METHOD PERFORMANCE")
    print("=" * 80)

    payment_result = payment_method_performance(
        transactions
    )

    print(
        payment_result.to_string(
            index=False
        )
    )

    save_dataframe(
        payment_result,
        "payment_method_performance.csv",
    )

    # ========================================================
    # ERROR ANALYSIS
    # ========================================================

    print("\n" + "=" * 80)
    print("ERROR CODE ANALYSIS")
    print("=" * 80)

    error_result = error_code_analysis(
        transactions,
        error_codes,
    )

    print(
        error_result[
            [
                "error_code",
                "error_name",
                "error_category",
                "failures",
                "failure_share_pct",
            ]
        ]
        .to_string(index=False)
    )

    save_dataframe(
        error_result,
        "error_code_analysis.csv",
    )

    # ========================================================
    # DAILY TREND
    # ========================================================

    print("\n" + "=" * 80)
    print("DAILY TREND")
    print("=" * 80)

    daily_result = daily_transaction_trend(
        transactions
    )

    print(
        daily_result.tail(10)
        .to_string(index=False)
    )

    save_dataframe(
        daily_result,
        "daily_transaction_trend.csv",
    )

    # ========================================================
    # INCIDENT COMPARISON
    # ========================================================

    print("\n" + "=" * 80)
    print("INCIDENT VS NORMAL")
    print("=" * 80)

    incident_result = incident_comparison(
        transactions
    )

    print(
        incident_result.to_string(
            index=False
        )
    )

    save_dataframe(
        incident_result,
        "incident_comparison.csv",
    )

    print("\n" + "=" * 80)
    print("PHASE 4 ANALYTICS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()