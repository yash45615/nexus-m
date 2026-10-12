import pandas as pd


def generate_explanation(
    row: pd.Series,
) -> str:

    reasons = []

    if row.get(
        "transaction_count_anomaly",
        False,
    ):
        reasons.append(
            "transaction volume deviated significantly from its recent baseline"
        )

    if row.get(
        "transaction_value_anomaly",
        False,
    ):
        reasons.append(
            "transaction value deviated significantly from its recent baseline"
        )

    if row.get(
        "success_rate_anomaly",
        False,
    ):
        reasons.append(
            "success rate deviated significantly from its recent baseline"
        )

    if row.get(
        "failure_rate_anomaly",
        False,
    ):
        reasons.append(
            "failure rate deviated significantly from its recent baseline"
        )

    if row.get(
        "average_latency_ms_anomaly",
        False,
    ):
        reasons.append(
            "average processing latency increased unexpectedly"
        )

    if row.get(
        "p95_latency_ms_anomaly",
        False,
    ):
        reasons.append(
            "P95 latency increased unexpectedly"
        )

    if row.get(
        "p99_latency_ms_anomaly",
        False,
    ):
        reasons.append(
            "P99 latency increased unexpectedly"
        )

    if row.get(
        "incident_count_anomaly",
        False,
    ):
        reasons.append(
            "incident activity increased unexpectedly"
        )

    if not reasons:

        if row.get(
            "ml_anomaly",
            False,
        ):
            return (
                "Machine-learning detector identified "
                "an unusual combination of operational metrics."
            )

        return "No significant anomaly detected."

    return "; ".join(reasons) + "."