from pathlib import Path
from time import perf_counter

import pandas as pd

from pipelines.pyspark.spark_session import create_spark_session


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRANSACTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "transactions.csv"
)


def pandas_benchmark():

    start = perf_counter()

    df = pd.read_csv(TRANSACTIONS_FILE)

    result = (
        df.groupby("status")
        .agg(
            transactions=("transaction_id", "count"),
            transaction_value=("transaction_amount", "sum"),
            average_latency=("processing_time_ms", "mean"),
        )
        .reset_index()
    )

    elapsed = perf_counter() - start

    return elapsed, result


def spark_benchmark(spark):

    start = perf_counter()

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(TRANSACTIONS_FILE))
    )

    result = (
        df.groupBy("status")
        .agg(
            {"transaction_id": "count",
             "transaction_amount": "sum",
             "processing_time_ms": "avg"}
        )
    )

    result.collect()

    elapsed = perf_counter() - start

    return elapsed, result


def main():

    print("=" * 70)
    print("NEXUS-M PANDAS VS PYSPARK BENCHMARK")
    print("=" * 70)

    pandas_time, pandas_result = pandas_benchmark()

    print("\nPandas result:")
    print(pandas_result)

    print(
        f"\nPandas execution time: "
        f"{pandas_time:.4f} seconds"
    )

    spark = create_spark_session()

    spark_time, spark_result = spark_benchmark(spark)

    print(
        f"\nPySpark execution time: "
        f"{spark_time:.4f} seconds"
    )

    print("\nImportant:")
    print(
        "For small datasets, local PySpark can be slower "
        "because Spark has startup and execution overhead."
    )

    if spark_time > 0:

        print(
            f"\nPandas/Spark time ratio: "
            f"{pandas_time / spark_time:.2f}"
        )

    spark.stop()


if __name__ == "__main__":
    main()