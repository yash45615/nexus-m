from pathlib import Path

from analytics.kpi_engine.data_loader import (
    AnalyticsDataLoader,
)

from analytics.anomaly_detection.features import (
    AnomalyFeatureEngine,
)

from analytics.anomaly_detection.statistical import (
    detect_statistical_anomalies,
)

from analytics.anomaly_detection.isolation_forest import (
    IsolationForestDetector,
)

from analytics.anomaly_detection.severity import (
    add_severity,
)

from analytics.anomaly_detection.explanations import (
    generate_explanation,
)


OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "phase9"
)


STATISTICAL_FEATURES = [
    "transaction_count",
    "transaction_value",
    "success_rate",
    "failure_rate",
    "average_latency_ms",
    "p95_latency_ms",
    "p99_latency_ms",
    "incident_count",
]


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    loader = AnalyticsDataLoader()

    transactions = (
        loader.load_transactions()
    )

    # ------------------------------
    # 1. Build daily metrics
    # ------------------------------

    feature_engine = (
        AnomalyFeatureEngine(
            transactions
        )
    )

    daily = (
        feature_engine
        .build_daily_features()
    )

    daily.to_csv(
        OUTPUT_DIR
        / "daily_anomaly_features.csv",
        index=False,
    )

    # ------------------------------
    # 2. Statistical detection
    # ------------------------------

    statistical = (
        detect_statistical_anomalies(
            daily,
            STATISTICAL_FEATURES,
            threshold=3.0,
        )
    )

    # ------------------------------
    # 3. ML detection
    # ------------------------------

    detector = (
        IsolationForestDetector(
            contamination=0.05
        )
    )

    anomalies = detector.detect(
        statistical
    )

    # ------------------------------
    # 4. Severity
    # ------------------------------

    anomalies = add_severity(
        anomalies
    )

    # ------------------------------
    # 5. Explanation
    # ------------------------------

    anomalies["explanation"] = (
        anomalies.apply(
            generate_explanation,
            axis=1,
        )
    )

    # ------------------------------
    # 6. Save
    # ------------------------------

    anomalies.to_csv(
        OUTPUT_DIR
        / "anomaly_results.csv",
        index=False,
    )

    anomaly_only = anomalies[
        anomalies["severity"] != "NORMAL"
    ]

    anomaly_only.to_csv(
        OUTPUT_DIR
        / "detected_anomalies.csv",
        index=False,
    )

    print(
        "Phase 9 Anomaly Detection completed."
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()

    print(
        "Severity distribution:"
    )

    print(
        anomalies[
            "severity"
        ].value_counts()
    )

    print()

    print(
        "Detected anomalies:"
    )

    print(
        anomaly_only[
            [
                "date",
                "severity",
                "anomaly_count",
                "anomaly_score",
                "explanation",
            ]
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()