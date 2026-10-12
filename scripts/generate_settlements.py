from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
from scripts.bootstrap import PROJECT_ROOT
from app.data_config import (
    RANDOM_SEED,
    SYNTHETIC_DATA_DIR,
)


random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def generate_settlements():

    print("=" * 70)
    print("NEXUS-M SETTLEMENT GENERATOR")
    print("=" * 70)

    transactions = pd.read_csv(
        SYNTHETIC_DATA_DIR / "transactions.csv"
    )

    successful = transactions[
        transactions["status"] == "SUCCESS"
    ].copy()

    print(
        f"Successful transactions available: "
        f"{len(successful):,}"
    )

    records = []

    for index, row in successful.iterrows():

        settlement_date = (
            pd.to_datetime(row["created_at"])
            + timedelta(
                days=random.choice([1, 2, 3])
            )
        ).date()

        settlement_amount = float(
            row["transaction_amount"]
        )

        settlement_status = "SETTLED"

        # ----------------------------------------------------
        # CONTROLLED SETTLEMENT MISMATCH
        # ----------------------------------------------------

        mismatch_probability = 0.008

        if random.random() < mismatch_probability:

            settlement_amount *= random.choice(
                [
                    0.97,
                    0.98,
                    1.02,
                    1.03,
                ]
            )

            settlement_status = "MISMATCH"

        settlement_id = (
            f"SETTLEMENT_{index + 1:09d}"
        )

        records.append(
            {
                "settlement_id": settlement_id,
                "transaction_id": row[
                    "transaction_id"
                ],
                "partner_key": int(
                    row["partner_key"]
                ),
                "merchant_key": int(
                    row["merchant_key"]
                )
                if pd.notna(
                    row["merchant_key"]
                )
                else None,
                "settlement_amount": round(
                    settlement_amount,
                    2,
                ),
                "settlement_status": settlement_status,
                "settlement_date": settlement_date,
                "created_at": datetime.now(),
            }
        )

    df = pd.DataFrame(records)

    output = (
        SYNTHETIC_DATA_DIR
        / "settlements.csv"
    )

    df.to_csv(
        output,
        index=False,
    )

    print(
        f"Generated settlements: "
        f"{len(df):,}"
    )

    print(
        f"Mismatched settlements: "
        f"{(df['settlement_status'] == 'MISMATCH').sum():,}"
    )

    print(f"Saved: {output}")

    print("=" * 70)
    print("SETTLEMENT GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    generate_settlements()