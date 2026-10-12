from pathlib import Path

from pipelines.pyspark.spark_session import create_spark_session
from pipelines.pyspark.transformations import (
    clean_transactions,
    add_derived_columns,
    enrich_transactions,
    calculate_daily_kpis,
    calculate_partner_kpis,
    calculate_region_kpis,
    calculate_category_kpis,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "phase5"
)


def run_pipeline():

    print("=" * 70)
    print("NEXUS-M PYSPARK BIG-DATA PIPELINE")
    print("=" * 70)

    spark = create_spark_session()

    print("\nSpark version:")
    print(spark.version)

    print("\nLoading transaction data...")

    transactions = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_DIR / "transactions.csv"))
    )

    print("Transaction rows:", transactions.count())

    print("\nLoading dimensions...")

    merchants = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_DIR / "dim_merchant.csv"))
    )

    partners = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_DIR / "dim_partner.csv"))
    )

    regions = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_DIR / "dim_region.csv"))
    )

    categories = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_DIR / "dim_category.csv"))
    )

    print("Merchants:", merchants.count())
    print("Partners:", partners.count())
    print("Regions:", regions.count())
    print("Categories:", categories.count())

    print("\nCleaning transactions...")

    transactions = clean_transactions(transactions)

    print(
        "Rows after duplicate removal:",
        transactions.count()
    )

    print("\nAdding analytical columns...")

    transactions = add_derived_columns(transactions)

    print("\nEnriching transactions...")

    enriched = enrich_transactions(
        transactions,
        merchants,
        partners,
        regions,
        categories,
    )

    enriched = enriched.cache()

    print("Enriched rows:", enriched.count())

    print("\nCalculating daily KPIs...")

    daily_kpis = calculate_daily_kpis(enriched)

    print("\nCalculating partner KPIs...")

    partner_kpis = calculate_partner_kpis(enriched)

    print("\nCalculating regional KPIs...")

    region_kpis = calculate_region_kpis(enriched)

    print("\nCalculating category KPIs...")

    category_kpis = calculate_category_kpis(enriched)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nWriting Parquet outputs...")

    (
        enriched
        .write
        .mode("overwrite")
        .partitionBy("transaction_date")
        .parquet(
            str(
                OUTPUT_DIR
                / "transactions_enriched"
            )
        )
    )

    (
        daily_kpis
        .write
        .mode("overwrite")
        .parquet(
            str(
                OUTPUT_DIR
                / "daily_kpis"
            )
        )
    )

    (
        partner_kpis
        .write
        .mode("overwrite")
        .parquet(
            str(
                OUTPUT_DIR
                / "partner_kpis"
            )
        )
    )

    (
        region_kpis
        .write
        .mode("overwrite")
        .parquet(
            str(
                OUTPUT_DIR
                / "regional_kpis"
            )
        )
    )

    (
        category_kpis
        .write
        .mode("overwrite")
        .parquet(
            str(
                OUTPUT_DIR
                / "category_kpis"
            )
        )
    )

    print("\nPipeline completed successfully.")

    print("\nOutput directory:")
    print(OUTPUT_DIR)

    enriched.unpersist()

    spark.stop()


if __name__ == "__main__":
    run_pipeline()