import pandas as pd
import pytest
from analytics.kpi_engine.transaction_metrics import (
    transaction_count,
    successful_transaction_count,
    failed_transaction_count,
    authorization_rate,
    decline_rate,
    total_transaction_value,
    average_transaction_value,
    average_processing_latency,
    p95_latency,
    p99_latency,
)


def sample_transactions():

    return pd.DataFrame(
        {
            "transaction_id": [
                "TXN_1",
                "TXN_2",
                "TXN_3",
                "TXN_4",
            ],
            "transaction_amount": [
                100.0,
                200.0,
                300.0,
                400.0,
            ],
            "processing_time_ms": [
                100.0,
                200.0,
                300.0,
                400.0,
            ],
            "status": [
                "SUCCESS",
                "SUCCESS",
                "FAILED",
                "FAILED",
            ],
            "incident_flag": [
                False,
                False,
                False,
                True,
            ],
        }
    )


def test_transaction_count():

    df = sample_transactions()

    assert transaction_count(df) == 4


def test_successful_transaction_count():

    df = sample_transactions()

    assert successful_transaction_count(df) == 2


def test_failed_transaction_count():

    df = sample_transactions()

    assert failed_transaction_count(df) == 2


def test_authorization_rate():

    df = sample_transactions()

    assert authorization_rate(df) == 50.0


def test_decline_rate():

    df = sample_transactions()

    assert decline_rate(df) == 50.0


def test_total_transaction_value():

    df = sample_transactions()

    assert total_transaction_value(df) == 1000.0


def test_average_transaction_value():

    df = sample_transactions()

    assert average_transaction_value(df) == 250.0


def test_average_latency():

    df = sample_transactions()

    assert average_processing_latency(df) == 250.0


def test_p95_latency():

    df = sample_transactions()

    assert p95_latency(df) == pytest.approx(385.0)


def test_p99_latency():

    df = sample_transactions()

    assert p99_latency(df) == pytest.approx(397.0)