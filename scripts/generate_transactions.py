from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from scripts.bootstrap import PROJECT_ROOT
from app.data_config import (
    NUMBER_OF_TRANSACTIONS,
    RANDOM_SEED,
    SYNTHETIC_DATA_DIR,
    INCIDENT_START_DAY,
    INCIDENT_END_DAY,
    INCIDENT_PARTNER_ID,
    INCIDENT_REGION,
    MIN_TRANSACTION_AMOUNT,
    MAX_TRANSACTION_AMOUNT,
    DUPLICATE_RATE,
    MISSING_MERCHANT_RATE,
    INVALID_AMOUNT_RATE,
)


random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Wallet",
    "Net Banking",
]


ERROR_WEIGHTS_NORMAL = {
    "E001": 0.35,
    "E002": 0.20,
    "E006": 0.15,
    "E007": 0.08,
    "E008": 0.05,
    "E003": 0.04,
    "E004": 0.03,
    "E005": 0.04,
    "E010": 0.06,
}


ERROR_WEIGHTS_INCIDENT = {
    "E001": 0.10,
    "E002": 0.05,
    "E006": 0.05,
    "E007": 0.03,
    "E008": 0.02,
    "E003": 0.35,
    "E004": 0.20,
    "E005": 0.15,
    "E010": 0.05,
}


def load_dimensions():

    merchants = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_merchant.csv"
    )

    partners = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_partner.csv"
    )

    regions = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_region.csv"
    )

    categories = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_category.csv"
    )

    return (
        merchants,
        partners,
        regions,
        categories,
    )


def weighted_error_code(incident=False):

    weights = (
        ERROR_WEIGHTS_INCIDENT
        if incident
        else ERROR_WEIGHTS_NORMAL
    )

    codes = list(weights.keys())
    probabilities = list(weights.values())

    return random.choices(
        codes,
        weights=probabilities,
        k=1,
    )[0]


def generate_transaction_amount(category):

    category_multipliers = {
        "Grocery": 0.7,
        "Restaurants": 0.5,
        "Fashion": 1.0,
        "Electronics": 2.5,
        "Travel": 3.0,
        "Healthcare": 1.5,
        "Education": 1.2,
        "Automotive": 3.5,
        "Fuel": 0.8,
        "Financial Services": 2.0,
        "E-Commerce": 1.5,
    }

    multiplier = category_multipliers.get(
        category,
        1.0,
    )

    base = np.random.lognormal(
        mean=7.0,
        sigma=1.0,
    )

    amount = base * multiplier

    return float(
        np.clip(
            amount,
            MIN_TRANSACTION_AMOUNT,
            MAX_TRANSACTION_AMOUNT,
        )
    )


def generate_transactions():

    print("=" * 70)
    print("NEXUS-M TRANSACTION GENERATOR")
    print("=" * 70)

    merchants, partners, regions, categories = load_dimensions()

    merchant_records = merchants.to_dict("records")
    partner_records = partners.to_dict("records")
    region_records = regions.to_dict("records")
    category_records = categories.to_dict("records")

    start_date = datetime(2026, 1, 1)

    rows = []

    for i in range(NUMBER_OF_TRANSACTIONS):

        merchant = random.choice(
            merchant_records
        )

        partner = random.choice(
            partner_records
        )

        region = random.choice(
            region_records
        )

        category = random.choice(
            category_records
        )

        day_offset = random.randint(
            0,
            179,
        )

        current_date = start_date + timedelta(
            days=day_offset
        )

        # ----------------------------------------------------
        # BUSINESS SEASONALITY
        # ----------------------------------------------------

        hour = random.choices(
            range(24),
            weights=[
                0.5, 0.3, 0.2, 0.2, 0.2, 0.3,
                0.5, 0.8, 1.0, 1.2, 1.3, 1.4,
                1.5, 1.5, 1.4, 1.3, 1.4, 1.6,
                1.8, 2.0, 2.2, 1.8, 1.2, 0.8
            ],
            k=1,
        )[0]

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        timestamp = current_date.replace(
            hour=hour,
            minute=minute,
            second=second,
        )

        # ----------------------------------------------------
        # WEEKEND EFFECT
        # ----------------------------------------------------

        weekend = timestamp.weekday() >= 5

        if weekend:
            transaction_probability = 1.15
        else:
            transaction_probability = 1.0

        # ----------------------------------------------------
        # INCIDENT DETECTION
        # ----------------------------------------------------

        incident = (
            partner["partner_id"] == INCIDENT_PARTNER_ID
            and region["region_name"] == INCIDENT_REGION
            and INCIDENT_START_DAY
            <= day_offset
            <= INCIDENT_END_DAY
        )

        # ----------------------------------------------------
        # BASE SUCCESS RATE
        # ----------------------------------------------------

        success_rate = 0.96

        # Merchant risk effect
        if merchant["risk_segment"] == "Medium":
            success_rate -= 0.015

        elif merchant["risk_segment"] == "High":
            success_rate -= 0.04

        # Weekend effect
        success_rate += (
            0.002
            if weekend
            else 0
        )

        # Incident effect
        if incident:
            success_rate = 0.78

        success_rate = np.clip(
            success_rate,
            0.50,
            0.99,
        )

        successful = (
            random.random()
            < success_rate
        )

        status = (
            "SUCCESS"
            if successful
            else "FAILED"
        )

        # ----------------------------------------------------
        # ERROR CODE
        # ----------------------------------------------------

        error_code = None

        if not successful:
            error_code = weighted_error_code(
                incident=incident
            )

        # ----------------------------------------------------
        # LATENCY
        # ----------------------------------------------------

        base_latency = np.random.normal(
            loc=180,
            scale=45,
        )

        if partner["partner_type"] == "Bank":
            base_latency += 40

        if partner["partner_type"] == "Wallet":
            base_latency -= 20

        if incident:
            base_latency += np.random.normal(
                1100,
                250,
            )

        processing_time = max(
            30,
            base_latency,
        )

        # ----------------------------------------------------
        # TRANSACTION VALUE
        # ----------------------------------------------------

        amount = generate_transaction_amount(
            category["category_name"]
        )

        # ----------------------------------------------------
        # PAYMENT METHOD
        # ----------------------------------------------------

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=[
                0.45,
                0.20,
                0.18,
                0.10,
                0.07,
            ],
            k=1,
        )[0]

        transaction_id = (
            f"TXN_{i + 1:09d}"
        )

        rows.append(
            {
                "transaction_id": transaction_id,
                "date_key": int(
                    timestamp.strftime("%Y%m%d")
                ),
                "merchant_key": int(
                    merchant["merchant_key"]
                ),
                "partner_key": int(
                    partner["partner_key"]
                ),
                "region_key": int(
                    region["region_key"]
                ),
                "category_key": int(
                    category["category_key"]
                ),
                "error_code": error_code,
                "transaction_amount": round(
                    amount,
                    2,
                ),
                "processing_time_ms": round(
                    processing_time,
                    2,
                ),
                "status": status,
                "payment_method": payment_method,
                "created_at": timestamp,
                "incident_flag": incident,
                "weekend_flag": weekend,
            }
        )

        if (i + 1) % 25_000 == 0:
            print(
                f"Generated "
                f"{i + 1:,} / "
                f"{NUMBER_OF_TRANSACTIONS:,} transactions"
            )

    df = pd.DataFrame(rows)

    # ========================================================
    # DATA QUALITY DEFECTS
    # ========================================================

    print("Injecting controlled data-quality defects...")

    # Duplicate transactions
    duplicate_count = int(
        len(df) * DUPLICATE_RATE
    )

    if duplicate_count > 0:

        duplicates = df.sample(
            n=duplicate_count,
            random_state=RANDOM_SEED,
        )

        df = pd.concat(
            [df, duplicates],
            ignore_index=True,
        )

    # Missing merchant references
    missing_count = int(
        len(df) * MISSING_MERCHANT_RATE
    )

    if missing_count > 0:

        indexes = np.random.choice(
            df.index,
            size=missing_count,
            replace=False,
        )

        df.loc[
            indexes,
            "merchant_key"
        ] = np.nan

    # Invalid amounts
    invalid_count = int(
        len(df) * INVALID_AMOUNT_RATE
    )

    if invalid_count > 0:

        indexes = np.random.choice(
            df.index,
            size=invalid_count,
            replace=False,
        )

        df.loc[
            indexes,
            "transaction_amount"
        ] = -100

    # ========================================================
    # SAVE
    # ========================================================

    output = (
        SYNTHETIC_DATA_DIR
        / "transactions.csv"
    )

    df.to_csv(
        output,
        index=False,
    )

    print("=" * 70)
    print("TRANSACTION GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Rows generated: {len(df):,}"
    )

    print(
        f"Successful transactions: "
        f"{(df['status'] == 'SUCCESS').sum():,}"
    )

    print(
        f"Failed transactions: "
        f"{(df['status'] == 'FAILED').sum():,}"
    )

    print(
        f"Incident transactions: "
        f"{df['incident_flag'].sum():,}"
    )

    print(
        f"Duplicate rows injected: "
        f"{duplicate_count:,}"
    )

    print(
        f"Missing merchants injected: "
        f"{missing_count:,}"
    )

    print(
        f"Invalid amounts injected: "
        f"{invalid_count:,}"
    )

    print(f"Saved: {output}")

    return df


if __name__ == "__main__":
    generate_transactions()