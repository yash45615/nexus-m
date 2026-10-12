import pandas as pd

from analytics.anomaly_detection.features import (
    AnomalyFeatureEngine,
)

from analytics.anomaly_detection.statistical import (
    rolling_z_score,
)

from analytics.anomaly_detection.severity import (
    calculate_severity,
)


def test_daily_features():

    data = pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "created_at": "2026-10-01 10:00:00",
                "transaction_amount": 100,
                "processing_time_ms": 100,
                "status": "success",
                "incident_flag": False,
            },
            {
                "transaction_id": "T2",
                "created_at": "2026-10-01 11:00:00",
                "transaction_amount": 200,
                "processing_time_ms": 200,
                "status": "failed",
                "incident_flag": True,
            },
            {
                "transaction_id": "T3",
                "created_at": "2026-10-02 10:00:00",
                "transaction_amount": 300,
                "processing_time_ms": 300,
                "status": "success",
                "incident_flag": False,
            },
        ]
    )

    engine = AnomalyFeatureEngine(data)

    result = engine.build_daily_features()

    assert len(result) == 2

    assert "success_rate" in result.columns
    assert "failure_rate" in result.columns
    assert "p95_latency_ms" in result.columns


def test_rolling_z_score():

    series = pd.Series(
        [10, 10, 10, 10, 100]
    )

    result = rolling_z_score(
        series,
        window=3,
    )

    assert len(result) == 5

    assert result.iloc[-1] > 0


def test_severity_normal():

    row = pd.Series(
        {
            "statistical_anomaly": False,
            "ml_anomaly": False,
            "anomaly_count": 0,
            "anomaly_score": 0,
        }
    )

    assert (
        calculate_severity(row)
        == "NORMAL"
    )


def test_severity_critical():

    row = pd.Series(
        {
            "statistical_anomaly": True,
            "ml_anomaly": True,
            "anomaly_count": 3,
            "anomaly_score": 0.5,
        }
    )

    assert (
        calculate_severity(row)
        == "CRITICAL"
    )