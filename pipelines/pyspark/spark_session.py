from __future__ import annotations

import os
import sys

from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    python_executable = sys.executable

    # Force Spark Python workers to use this virtual environment.
    os.environ["PYSPARK_PYTHON"] = python_executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable

    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("NEXUS-M-PySpark-Pipeline")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.python.worker.reuse", "true")
        .config("spark.pyspark.python", python_executable)
        .config("spark.pyspark.driver.python", python_executable)
        .config("spark.executorEnv.PYSPARK_PYTHON", python_executable)
        .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", python_executable)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark