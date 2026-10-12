import json

from app.data_config import PROCESSED_DATA_DIR


SUMMARY_FILE = (
    PROCESSED_DATA_DIR
    / "analytical_summary.json"
)


def load_summary():
    with open(
        SUMMARY_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_analytical_summary_exists():
    assert SUMMARY_FILE.exists()


def test_analytical_summary_structure():
    summary = load_summary()

    assert "metadata" in summary
    assert "transaction_kpis" in summary
    assert "performance_kpis" in summary
    assert "risk_kpis" in summary
    assert "behavioral_kpis" in summary


def test_transaction_kpis():
    summary = load_summary()

    kpis = summary["transaction_kpis"]

    assert kpis["total_transactions"] >= 0
    assert (
        kpis["successful_transactions"] >= 0
    )
    assert kpis["failed_transactions"] >= 0

    assert (
        0
        <= kpis["authorization_rate"]
        <= 1
    )

    assert (
        0
        <= kpis["decline_rate"]
        <= 1
    )

    assert (
        kpis["total_transaction_value"]
        >= 0
    )

    assert (
        kpis["average_transaction_value"]
        >= 0
    )


def test_performance_kpis():
    summary = load_summary()

    kpis = summary["performance_kpis"]

    assert (
        kpis["average_processing_time_ms"]
        >= 0
    )

    assert (
        kpis["p95_processing_time_ms"]
        >= 0
    )

    assert (
        kpis["p99_processing_time_ms"]
        >= 0
    )

    assert (
        kpis["p95_processing_time_ms"]
        >=
        kpis["average_processing_time_ms"]
    )

    assert (
        kpis["p99_processing_time_ms"]
        >=
        kpis["p95_processing_time_ms"]
    )


def test_risk_kpis():
    summary = load_summary()

    kpis = summary["risk_kpis"]

    assert kpis["incident_count"] >= 0


def test_behavioral_kpis():
    summary = load_summary()

    kpis = summary["behavioral_kpis"]

    assert (
        kpis["weekend_transaction_count"]
        >= 0
    )

    assert (
        0
        <= kpis["weekend_transaction_share"]
        <= 1
    )