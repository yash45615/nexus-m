import pandas as pd

from scripts.bootstrap import PROJECT_ROOT

from app.data_config import SYNTHETIC_DATA_DIR

def inspect():

    print("=" * 70)
    print("NEXUS-M SYNTHETIC DATA INSPECTION")
    print("=" * 70)

    # --------------------------------------------------------
    # MERCHANTS
    # --------------------------------------------------------

    merchants = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_merchant.csv"
    )

    print("\nMERCHANTS")
    print("-" * 70)

    print(
        f"Rows: {len(merchants):,}"
    )

    print(
        f"Unique merchants: "
        f"{merchants['merchant_id'].nunique():,}"
    )

    print(
        "\nMerchant risk distribution:"
    )

    print(
        merchants["risk_segment"]
        .value_counts()
    )

    # --------------------------------------------------------
    # TRANSACTIONS
    # --------------------------------------------------------

    transactions = pd.read_csv(
        SYNTHETIC_DATA_DIR / "transactions.csv"
    )

    print("\nTRANSACTIONS")
    print("-" * 70)

    print(
        f"Rows: {len(transactions):,}"
    )

    print(
        "\nStatus:"
    )

    print(
        transactions["status"]
        .value_counts()
    )

    print(
        "\nPayment methods:"
    )

    print(
        transactions["payment_method"]
        .value_counts()
    )

    print(
        "\nAverage transaction amount:"
    )

    print(
        round(
            transactions[
                "transaction_amount"
            ].mean(),
            2,
        )
    )

    print(
        "\nAverage processing latency:"
    )

    print(
        round(
            transactions[
                "processing_time_ms"
            ].mean(),
            2,
        )
    )

    print(
        "\nIncident transactions:"
    )

    print(
        transactions[
            "incident_flag"
        ].sum()
    )

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    duplicate_count = (
        transactions["transaction_id"]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate transaction IDs:"
    )

    print(
        duplicate_count
    )

    # --------------------------------------------------------
    # INVALID AMOUNTS
    # --------------------------------------------------------

    invalid_amounts = (
        transactions[
            "transaction_amount"
        ] <= 0
    ).sum()

    print(
        "\nInvalid transaction amounts:"
    )

    print(
        invalid_amounts
    )

    # --------------------------------------------------------
    # MISSING MERCHANTS
    # --------------------------------------------------------

    missing_merchants = (
        transactions[
            "merchant_key"
        ]
        .isna()
        .sum()
    )

    print(
        "\nMissing merchant keys:"
    )

    print(
        missing_merchants
    )

    # --------------------------------------------------------
    # SETTLEMENTS
    # --------------------------------------------------------

    settlements = pd.read_csv(
        SYNTHETIC_DATA_DIR / "settlements.csv"
    )

    print("\nSETTLEMENTS")
    print("-" * 70)

    print(
        f"Rows: {len(settlements):,}"
    )

    print(
        "\nSettlement status:"
    )

    print(
        settlements[
            "settlement_status"
        ].value_counts()
    )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    events = pd.read_csv(
        SYNTHETIC_DATA_DIR / "partner_events.csv"
    )

    print("\nPARTNER EVENTS")
    print("-" * 70)

    print(
        f"Rows: {len(events):,}"
    )

    print(
        "\nSeverity:"
    )

    print(
        events[
            "severity"
        ].value_counts()
    )

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    inspect()