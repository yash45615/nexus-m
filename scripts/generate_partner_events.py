from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
from scripts.bootstrap import PROJECT_ROOT
from app.data_config import (
    INCIDENT_PARTNER_ID,
    INCIDENT_REGION,
    INCIDENT_START_DAY,
    INCIDENT_END_DAY,
    RANDOM_SEED,
    SYNTHETIC_DATA_DIR,
)


random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def generate_partner_events():

    print("=" * 70)
    print("NEXUS-M PARTNER EVENT GENERATOR")
    print("=" * 70)

    partners = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_partner.csv"
    )

    regions = pd.read_csv(
        SYNTHETIC_DATA_DIR / "dim_region.csv"
    )

    records = []

    start_date = datetime(
        2026,
        1,
        1,
    )

    event_types = [
        "HEALTH_CHECK",
        "LATENCY_WARNING",
        "SERVICE_DEGRADATION",
        "SERVICE_RECOVERY",
        "OUTAGE",
    ]

    for day in range(180):

        current_date = (
            start_date
            + timedelta(days=day)
        )

        for _, partner in partners.iterrows():

            for _, region in regions.iterrows():

                incident = (
                    partner["partner_id"]
                    == INCIDENT_PARTNER_ID
                    and region["region_name"]
                    == INCIDENT_REGION
                    and INCIDENT_START_DAY
                    <= day
                    <= INCIDENT_END_DAY
                )

                if incident:

                    event_type = random.choice(
                        [
                            "LATENCY_WARNING",
                            "SERVICE_DEGRADATION",
                            "OUTAGE",
                        ]
                    )

                    latency = np.random.normal(
                        1500,
                        300,
                    )

                    severity = random.choice(
                        [
                            "HIGH",
                            "CRITICAL",
                        ]
                    )

                    description = (
                        f"Elevated latency and "
                        f"failure rate detected for "
                        f"{partner['partner_id']} "
                        f"in {region['region_name']}."
                    )

                else:

                    event_type = random.choice(
                        [
                            "HEALTH_CHECK",
                            "HEALTH_CHECK",
                            "HEALTH_CHECK",
                            "LATENCY_WARNING",
                        ]
                    )

                    latency = np.random.normal(
                        180,
                        40,
                    )

                    severity = random.choice(
                        [
                            "LOW",
                            "INFO",
                        ]
                    )

                    description = (
                        f"Routine monitoring event for "
                        f"{partner['partner_id']} "
                        f"in {region['region_name']}."
                    )

                timestamp = current_date.replace(
                    hour=random.randint(
                        0,
                        23,
                    ),
                    minute=random.randint(
                        0,
                        59,
                    ),
                    second=random.randint(
                        0,
                        59,
                    ),
                )

                records.append(
                    {
                        "event_id": (
                            f"EVENT_"
                            f"{len(records) + 1:09d}"
                        ),
                        "partner_key": int(
                            partner["partner_key"]
                        ),
                        "region_key": int(
                            region["region_key"]
                        ),
                        "event_type": event_type,
                        "event_timestamp": timestamp,
                        "latency_ms": round(
                            max(
                                20,
                                latency,
                            ),
                            2,
                        ),
                        "severity": severity,
                        "description": description,
                    }
                )

    df = pd.DataFrame(records)

    output = (
        SYNTHETIC_DATA_DIR
        / "partner_events.csv"
    )

    df.to_csv(
        output,
        index=False,
    )

    print(
        f"Generated events: "
        f"{len(df):,}"
    )

    print(
        "Incident events: "
        f"{df['severity'].isin(['HIGH', 'CRITICAL']).sum():,}"
    )

    print(f"Saved: {output}")

    print("=" * 70)
    print("PARTNER EVENT GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    generate_partner_events()