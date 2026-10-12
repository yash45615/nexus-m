import pandas as pd
import pytest

from analytics.root_cause.baseline import (
    prepare_transaction_data,
    compare_periods,
)

from analytics.root_cause.drilldown import (
    RootCauseDrilldown,
)

from analytics.root_cause.contribution import (
    calculate_contribution,
)

from analytics.root_cause.scoring import (
    calculate_root_cause_score,
)


@pytest.fixture
def sample_data():

    return pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "created_at": "2026-10-01 10:00:00",
                "partner_key": 1,
                "region_key": 1,
                "category_key": 1,
                "merchant_key": 1,
                "error_code": None,
                "transaction_amount": 100,
                "status": "success",
            },
            {
                "transaction_id": "T2",
                "created_at": "2026-10-01 11:00:00",
                "partner_key": 1,
                "region_key": 1,
                "category_key": 1,
                "merchant_key": 1,
                "error_code": "E001",
                "transaction_amount": 200,
                "status": "failed",
            },
            {
                "transaction_id": "T3",
                "created_at": "2026-10-02 10:00:00",
                "partner_key": 1,
                "region_key": 1,
                "category_key": 1,
                "merchant_key": 1,
                "error_code": "E001",
                "transaction_amount": 300,
                "status": "failed",
            },
            {
                "transaction_id": "T4",
                "created_at": "2026-10-02 11:00:00",
                "partner_key": 2,
                "region_key": 2,
                "category_key": 2,
                "merchant_key": 2,
                "error_code": "E002",
                "transaction_amount": 400,
                "status": "success",
            },
        ]
    )


def test_prepare_data(sample_data):

    result = prepare_transaction_data(
        sample_data
    )

    assert "date" in result.columns
    assert "is_success" in result.columns
    assert "is_failure" in result.columns


def test_compare_periods(sample_data):

    prepared = prepare_transaction_data(
        sample_data
    )

    baseline = prepared[
        prepared["date"]
        == pd.to_datetime(
            "2026-10-01"
        ).date()
    ]

    incident = prepared[
        prepared["date"]
        == pd.to_datetime(
            "2026-10-02"
        ).date()
    ]

    result = compare_periods(
        baseline,
        incident,
    )

    assert "baseline" in result
    assert "incident" in result
    assert "failure_rate_change" in result


def test_dimension_drilldown(sample_data):

    prepared = prepare_transaction_data(
        sample_data
    )

    baseline = prepared[
        prepared["date"]
        == pd.to_datetime(
            "2026-10-01"
        ).date()
    ]

    incident = prepared[
        prepared["date"]
        == pd.to_datetime(
            "2026-10-02"
        ).date()
    ]

    engine = RootCauseDrilldown(
        baseline,
        incident,
    )

    result = engine.analyze_dimension(
        "partner_key"
    )

    assert "failure_change" in result.columns
    assert "failure_rate_change" in result.columns


def test_contribution():

    data = pd.DataFrame(
        {
            "partner_key": [
                1,
                2,
                3,
            ],
            "failure_change": [
                50,
                30,
                20,
            ],
        }
    )

    result = calculate_contribution(
        data
    )

    assert (
        result["contribution_pct"]
        .sum()
        == pytest.approx(100.0)
    )


def test_root_cause_score():

    data = pd.DataFrame(
        {
            "partner_key": [1, 2, 3],
            "failure_change": [50, 30, 20],
            "contribution_pct": [50, 30, 20],
            "incident_value": [
                1000,
                500,
                250,
            ],
            "failure_rate_change": [
                10,
                5,
                2,
            ],
        }
    )

    result = calculate_root_cause_score(
        data
    )

    assert "root_cause_score" in result.columns

    assert (
        result.iloc[0]["root_cause_score"]
        >= result.iloc[-1]["root_cause_score"]
    )