from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    LongType,
    DoubleType,
    BooleanType,
    TimestampType,
)


TRANSACTION_SCHEMA = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("date_key", IntegerType(), True),
    StructField("merchant_key", IntegerType(), True),
    StructField("partner_key", IntegerType(), True),
    StructField("region_key", IntegerType(), True),
    StructField("category_key", IntegerType(), True),
    StructField("error_code", StringType(), True),
    StructField("transaction_amount", DoubleType(), True),
    StructField("processing_time_ms", DoubleType(), True),
    StructField("status", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("incident_flag", BooleanType(), True),
])


MERCHANT_SCHEMA = StructType([
    StructField("merchant_key", IntegerType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("merchant_name", StringType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("region", StringType(), True),
    StructField("city", StringType(), True),
    StructField("risk_segment", StringType(), True),
    StructField("active", BooleanType(), True),
])


PARTNER_SCHEMA = StructType([
    StructField("partner_key", IntegerType(), True),
    StructField("partner_id", StringType(), True),
    StructField("partner_name", StringType(), True),
    StructField("partner_type", StringType(), True),
    StructField("sla_timeout_seconds", DoubleType(), True),
    StructField("active", BooleanType(), True),
])


REGION_SCHEMA = StructType([
    StructField("region_key", IntegerType(), True),
    StructField("region_name", StringType(), True),
    StructField("country", StringType(), True),
    StructField("timezone", StringType(), True),
])


CATEGORY_SCHEMA = StructType([
    StructField("category_key", IntegerType(), True),
    StructField("category_code", StringType(), True),
    StructField("category_name", StringType(), True),
])


ERROR_CODE_SCHEMA = StructType([
    StructField("error_code", StringType(), True),
    StructField("error_name", StringType(), True),
    StructField("error_category", StringType(), True),
    StructField("description", StringType(), True),
])