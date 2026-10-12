from pathlib import Path

from pipelines.pyspark.spark_session import create_spark_session


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "phase5"
)


def main():

    spark = create_spark_session()

    print("=" * 70)
    print("NEXUS-M PARQUET OUTPUT VALIDATION")
    print("=" * 70)

    datasets = [
        "transactions_enriched",
        "daily_kpis",
        "partner_kpis",
        "regional_kpis",
        "category_kpis",
    ]

    for dataset in datasets:

        path = OUTPUT_DIR / dataset

        print(f"\nDataset: {dataset}")

        df = spark.read.parquet(str(path))

        print("Rows:", df.count())

        print("Columns:")

        print(df.columns)

        print("\nSample:")

        df.show(5, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()