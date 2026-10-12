from pipelines.pyspark.spark_session import create_spark_session
from pipelines.pyspark.transformations import (
    clean_transactions,
    add_derived_columns,
)


def test_spark_session():

    spark = create_spark_session()

    assert spark.version is not None

    spark.stop()


def test_transaction_transformations():

    spark = create_spark_session()

    data = [
        (
            "TX001",
            1001,
            1,
            1,
            1,
            1,
            None,
            500.0,
            120.0,
            "success",
            "card",
            "2026-10-01 10:00:00",
            False,
        ),
        (
            "TX002",
            1001,
            1,
            1,
            1,
            1,
            "E001",
            750.0,
            800.0,
            "failed",
            "card",
            "2026-10-01 10:01:00",
            True,
        ),
    ]

    columns = [
        "transaction_id",
        "date_key",
        "merchant_key",
        "partner_key",
        "region_key",
        "category_key",
        "error_code",
        "transaction_amount",
        "processing_time_ms",
        "status",
        "payment_method",
        "created_at",
        "incident_flag",
    ]

    df = spark.createDataFrame(data, columns)

    cleaned = clean_transactions(df)

    transformed = add_derived_columns(cleaned)

    rows = transformed.collect()

    assert rows[0]["status"] == "SUCCESS"
    assert rows[1]["status"] == "FAILED"

    assert rows[0]["is_success"] == 1
    assert rows[1]["is_failure"] == 1

    assert rows[0]["latency_bucket"] == "FAST"
    assert rows[1]["latency_bucket"] == "SLOW"

    spark.stop()