import os
import sys

from pipelines.pyspark.spark_session import create_spark_session


def main():
    print("=" * 60)
    print("DRIVER PYTHON")
    print("=" * 60)

    print("sys.executable:")
    print(sys.executable)

    print()
    print("PYSPARK_PYTHON:")
    print(os.environ.get("PYSPARK_PYTHON"))

    print()
    print("PYSPARK_DRIVER_PYTHON:")
    print(os.environ.get("PYSPARK_DRIVER_PYTHON"))

    spark = create_spark_session()

    print()
    print("=" * 60)
    print("SPARK")
    print("=" * 60)

    print("Spark version:")
    print(spark.version)

    print("Spark Python version:")
    print(spark.sparkContext.pythonVer)

    print()
    print("Configured Spark Python:")
    print(spark.conf.get("spark.pyspark.python"))

    print()
    print("=" * 60)
    print("PYTHON WORKER TEST")
    print("=" * 60)

    result = (
        spark.range(5)
        .selectExpr(
            "id",
            "id * 10 AS value"
        )
        .collect()
    )

    for row in result:
        print(row)

    spark.stop()

    print()
    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()