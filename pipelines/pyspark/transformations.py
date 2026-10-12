from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def clean_transactions(df: DataFrame) -> DataFrame:
    """
    Clean and standardize transaction data.
    """

    cleaned = (
        df
        .withColumn(
            "status",
            F.upper(F.trim(F.col("status")))
        )
        .withColumn(
            "payment_method",
            F.upper(F.trim(F.col("payment_method")))
        )
        .withColumn(
            "transaction_amount",
            F.round(F.col("transaction_amount"), 2)
        )
        .withColumn(
            "processing_time_ms",
            F.round(F.col("processing_time_ms"), 2)
        )
        .dropDuplicates(["transaction_id"])
    )

    return cleaned


def add_derived_columns(df: DataFrame) -> DataFrame:
    """
    Add analytical columns used throughout NEXUS-M.
    """

    return (
        df
        .withColumn(
            "transaction_date",
            F.to_date(F.col("created_at"))
        )
        .withColumn(
            "is_success",
            F.when(F.col("status") == "SUCCESS", 1).otherwise(0)
        )
        .withColumn(
            "is_failure",
            F.when(F.col("status") == "FAILED", 1).otherwise(0)
        )
        .withColumn(
            "is_high_value",
            F.when(F.col("transaction_amount") >= 10000, 1)
             .otherwise(0)
        )
        .withColumn(
            "latency_bucket",
            F.when(F.col("processing_time_ms") < 200, "FAST")
             .when(F.col("processing_time_ms") < 500, "NORMAL")
             .when(F.col("processing_time_ms") < 1000, "SLOW")
             .otherwise("CRITICAL")
        )
    )


def enrich_transactions(
    transactions: DataFrame,
    merchants: DataFrame,
    partners: DataFrame,
    regions: DataFrame,
    categories: DataFrame,
) -> DataFrame:

    enriched = (
        transactions.alias("t")
        .join(
            merchants.alias("m"),
            F.col("t.merchant_key") == F.col("m.merchant_key"),
            "left"
        )
        .join(
            partners.alias("p"),
            F.col("t.partner_key") == F.col("p.partner_key"),
            "left"
        )
        .join(
            regions.alias("r"),
            F.col("t.region_key") == F.col("r.region_key"),
            "left"
        )
        .join(
            categories.alias("c"),
            F.col("t.category_key") == F.col("c.category_key"),
            "left"
        )
        .select(
            "t.*",

            F.col("m.merchant_id"),
            F.col("m.merchant_name"),
            F.col("m.merchant_category"),
            F.col("m.risk_segment"),

            F.col("p.partner_id"),
            F.col("p.partner_name"),
            F.col("p.partner_type"),
            F.col("p.sla_timeout_seconds"),

            F.col("r.region_name"),
            F.col("r.country"),
            F.col("r.timezone"),

            F.col("c.category_code"),
            F.col("c.category_name"),
        )
    )

    return enriched


def calculate_daily_kpis(df: DataFrame) -> DataFrame:

    return (
        df.groupBy("transaction_date")
        .agg(
            F.count("*").alias("transactions"),

            F.sum("transaction_amount")
            .alias("transaction_value"),

            F.sum("is_success")
            .alias("successful_transactions"),

            F.sum("is_failure")
            .alias("failed_transactions"),

            F.avg("processing_time_ms")
            .alias("average_latency_ms"),

            F.expr(
                "percentile_approx(processing_time_ms, 0.95)"
            ).alias("p95_latency_ms"),
        )
        .withColumn(
            "authorization_rate_pct",
            F.round(
                F.col("successful_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
        .withColumn(
            "failure_rate_pct",
            F.round(
                F.col("failed_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
    )


def calculate_partner_kpis(df: DataFrame) -> DataFrame:

    return (
        df.groupBy(
            "partner_key",
            "partner_id",
            "partner_name",
            "partner_type"
        )
        .agg(
            F.count("*").alias("transactions"),

            F.sum("transaction_amount")
            .alias("transaction_value"),

            F.sum("is_success")
            .alias("successful_transactions"),

            F.sum("is_failure")
            .alias("failed_transactions"),

            F.avg("processing_time_ms")
            .alias("average_latency_ms"),

            F.expr(
                "percentile_approx(processing_time_ms, 0.95)"
            ).alias("p95_latency_ms"),
        )
        .withColumn(
            "authorization_rate_pct",
            F.round(
                F.col("successful_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
        .withColumn(
            "failure_rate_pct",
            F.round(
                F.col("failed_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
    )


def calculate_region_kpis(df: DataFrame) -> DataFrame:

    return (
        df.groupBy(
            "region_key",
            "region_name",
            "country"
        )
        .agg(
            F.count("*").alias("transactions"),

            F.sum("transaction_amount")
            .alias("transaction_value"),

            F.sum("is_success")
            .alias("successful_transactions"),

            F.sum("is_failure")
            .alias("failed_transactions"),

            F.avg("processing_time_ms")
            .alias("average_latency_ms"),

            F.expr(
                "percentile_approx(processing_time_ms, 0.95)"
            ).alias("p95_latency_ms"),
        )
        .withColumn(
            "authorization_rate_pct",
            F.round(
                F.col("successful_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
        .withColumn(
            "failure_rate_pct",
            F.round(
                F.col("failed_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
    )


def calculate_category_kpis(df: DataFrame) -> DataFrame:

    return (
        df.groupBy(
            "category_key",
            "category_code",
            "category_name"
        )
        .agg(
            F.count("*").alias("transactions"),

            F.sum("transaction_amount")
            .alias("transaction_value"),

            F.sum("is_success")
            .alias("successful_transactions"),

            F.sum("is_failure")
            .alias("failed_transactions"),

            F.avg("processing_time_ms")
            .alias("average_latency_ms"),

            F.expr(
                "percentile_approx(processing_time_ms, 0.95)"
            ).alias("p95_latency_ms"),
        )
        .withColumn(
            "authorization_rate_pct",
            F.round(
                F.col("successful_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
        .withColumn(
            "failure_rate_pct",
            F.round(
                F.col("failed_transactions")
                / F.col("transactions")
                * 100,
                2
            )
        )
    )