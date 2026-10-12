from datetime import date, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd
from faker import Faker
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from scripts.bootstrap import PROJECT_ROOT
from app.data_config import (
    NUMBER_OF_MERCHANTS,
    NUMBER_OF_PARTNERS,
    NUMBER_OF_REGIONS,
    NUMBER_OF_CATEGORIES,
    NUMBER_OF_DAYS,
    RANDOM_SEED,
    SYNTHETIC_DATA_DIR,
)


random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)


# ============================================================
# STATIC BUSINESS DEFINITIONS
# ============================================================

REGIONS = [
    {
        "region_name": "North",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "South",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "East",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "West",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "Central",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "Northeast",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "Metro",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
    {
        "region_name": "Tier2",
        "country": "India",
        "timezone": "Asia/Kolkata",
    },
]


CATEGORIES = [
    "Grocery",
    "Fashion",
    "Electronics",
    "Travel",
    "Restaurants",
    "Healthcare",
    "Education",
    "Entertainment",
    "Automotive",
    "Fuel",
    "Utilities",
    "Insurance",
    "Financial Services",
    "Home & Furniture",
    "Beauty",
    "Sports",
    "Pharmacy",
    "Hospitality",
    "Telecom",
    "E-Commerce",
]


ERROR_CODES = [
    {
        "error_code": "E001",
        "error_name": "Insufficient Funds",
        "error_category": "Customer",
        "description": "Customer account does not have sufficient funds.",
    },
    {
        "error_code": "E002",
        "error_name": "Invalid Card",
        "error_category": "Customer",
        "description": "Payment instrument is invalid or expired.",
    },
    {
        "error_code": "E003",
        "error_name": "Partner Timeout",
        "error_category": "Infrastructure",
        "description": "Partner response exceeded the configured timeout.",
    },
    {
        "error_code": "E004",
        "error_name": "Partner Unavailable",
        "error_category": "Infrastructure",
        "description": "Payment partner was unavailable.",
    },
    {
        "error_code": "E005",
        "error_name": "Network Error",
        "error_category": "Infrastructure",
        "description": "Network communication failed.",
    },
    {
        "error_code": "E006",
        "error_name": "Risk Decline",
        "error_category": "Risk",
        "description": "Transaction was rejected by risk controls.",
    },
    {
        "error_code": "E007",
        "error_name": "Fraud Suspected",
        "error_category": "Risk",
        "description": "Transaction triggered fraud detection rules.",
    },
    {
        "error_code": "E008",
        "error_name": "Invalid Request",
        "error_category": "Technical",
        "description": "Transaction request contained invalid data.",
    },
    {
        "error_code": "E009",
        "error_name": "Duplicate Transaction",
        "error_category": "Technical",
        "description": "Duplicate transaction detected.",
    },
    {
        "error_code": "E010",
        "error_name": "System Error",
        "error_category": "Infrastructure",
        "description": "Unexpected internal system error.",
    },
]


PARTNER_TYPES = [
    "Payment Gateway",
    "Bank",
    "Wallet",
    "UPI Network",
]


PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Wallet",
    "Net Banking",
]


RISK_SEGMENTS = [
    "Low",
    "Medium",
    "High",
]


# ============================================================
# DATE DIMENSION
# ============================================================

def generate_dates():
    print("Generating date dimension...")

    start_date = date(2026, 1, 1)

    records = []

    for index in range(NUMBER_OF_DAYS):
        current_date = start_date + timedelta(days=index)

        records.append(
            {
                "date_key": int(current_date.strftime("%Y%m%d")),
                "full_date": current_date,
                "year": current_date.year,
                "quarter": ((current_date.month - 1) // 3) + 1,
                "month": current_date.month,
                "month_name": current_date.strftime("%B"),
                "week": current_date.isocalendar().week,
                "day_of_week": current_date.weekday(),
                "day_name": current_date.strftime("%A"),
                "is_weekend": current_date.weekday() >= 5,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_date.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} dates")
    print(f"Saved: {output}")

    return df


# ============================================================
# REGION DIMENSION
# ============================================================

def generate_regions():
    print("Generating region dimension...")

    records = []

    for index, region in enumerate(REGIONS, start=1):
        records.append(
            {
                "region_key": index,
                **region,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_region.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} regions")
    print(f"Saved: {output}")

    return df


# ============================================================
# CATEGORY DIMENSION
# ============================================================

def generate_categories():
    print("Generating category dimension...")

    records = []

    for index, category in enumerate(CATEGORIES, start=1):
        records.append(
            {
                "category_key": index,
                "category_code": f"CAT_{index:03d}",
                "category_name": category,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_category.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} categories")
    print(f"Saved: {output}")

    return df


# ============================================================
# ERROR CODE DIMENSION
# ============================================================

def generate_error_codes():
    print("Generating error-code dimension...")

    records = []

    for index, error in enumerate(ERROR_CODES, start=1):
        records.append(
            {
                "error_key": index,
                **error,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_error_code.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} error codes")
    print(f"Saved: {output}")

    return df


# ============================================================
# PARTNER DIMENSION
# ============================================================

def generate_partners():
    print("Generating partner dimension...")

    records = []

    for index in range(1, NUMBER_OF_PARTNERS + 1):

        partner_id = f"PARTNER_{index:02d}"

        partner_type = random.choice(PARTNER_TYPES)

        sla_timeout = random.choice(
            [2.0, 3.0, 5.0, 8.0]
        )

        records.append(
            {
                "partner_key": index,
                "partner_id": partner_id,
                "partner_name": f"Nexus {partner_type} {index:02d}",
                "partner_type": partner_type,
                "sla_timeout_seconds": sla_timeout,
                "active": True,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_partner.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} partners")
    print(f"Saved: {output}")

    return df


# ============================================================
# MERCHANT DIMENSION
# ============================================================

def generate_merchants():
    print("Generating merchant dimension...")

    records = []

    region_names = [region["region_name"] for region in REGIONS]

    for index in range(1, NUMBER_OF_MERCHANTS + 1):

        category = random.choice(CATEGORIES)

        region = random.choice(region_names)

        city = fake.city()

        risk = random.choices(
            RISK_SEGMENTS,
            weights=[0.60, 0.30, 0.10],
            k=1,
        )[0]

        records.append(
            {
                "merchant_key": index,
                "merchant_id": f"MERCHANT_{index:06d}",
                "merchant_name": fake.company(),
                "merchant_category": category,
                "region": region,
                "city": city,
                "risk_segment": risk,
                "active": True,
            }
        )

    df = pd.DataFrame(records)

    output = SYNTHETIC_DATA_DIR / "dim_merchant.csv"

    df.to_csv(output, index=False)

    print(f"Generated {len(df):,} merchants")
    print(f"Saved: {output}")

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    SYNTHETIC_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("NEXUS-M DIMENSION DATA GENERATOR")
    print("=" * 70)

    generate_dates()
    generate_regions()
    generate_categories()
    generate_error_codes()
    generate_partners()
    generate_merchants()

    print("=" * 70)
    print("DIMENSION GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()