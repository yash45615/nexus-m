import pandas as pd
import pytest

from analytics.metrics.calculator import KPICalculator
from analytics.metrics.registry import MetricRegistry
from analytics.metrics.thresholds import evaluate_threshold


@pytest.fixture
def sample_transactions():

    return pd.DataFrame(
        [
            {
                "transaction_id": "TX001",
                "transaction_amount": 100,
                "processing_time_ms": 100,
                "status": "success",
            },
            {
                "transaction_id": "TX002",
                "transaction_amount": 200,
                "processing_time_ms": 200,
                "status": "success",
            },
            {
                "transaction_id": "TX003",
                "transaction_amount": 300,
                "processing_time_ms": 300,
                "status": "failed",
            },
            {
                "transaction_id": "TX004",
                "transaction_amount": 400,
                "processing_time_ms": 400,
                "status": "failed",
            },
        ]
    )


def test_transaction_count(sample_transactions):

    calculator = KPICalculator(
        sample_transactions
    )

    assert calculator.transaction_count() == 4


def test_success_rate(sample_transactions):

    calculator = KPICalculator(
        sample_transactions
    )

    assert calculator.success_rate() == pytest.approx(50.0)


def test_failure_rate(sample_transactions):

    calculator = KPICalculator(
        sample_transactions
    )

    assert calculator.failure_rate() == pytest.approx(50.0)


def test_transaction_value(sample_transactions):

    calculator = KPICalculator(
        sample_transactions
    )

    assert (
        calculator.total_transaction_value()
        == 1000
    )


def test_average_transaction_value(
    sample_transactions,
):

    calculator = KPICalculator(
        sample_transactions
    )

    assert (
        calculator.average_transaction_value()
        == pytest.approx(250.0)
    )


def test_registry():

    registry = MetricRegistry()

    assert "success_rate" in registry.names()

    metric = registry.get("success_rate")

    assert metric.category == "reliability"


def test_threshold():

    assert (
        evaluate_threshold(
            "success_rate",
            98.0,
        )
        == "HEALTHY"
    )

    assert (
        evaluate_threshold(
            "success_rate",
            92.0,
        )
        == "WARNING"
    )

    assert (
        evaluate_threshold(
            "success_rate",
            85.0,
        )
        == "CRITICAL"
    )