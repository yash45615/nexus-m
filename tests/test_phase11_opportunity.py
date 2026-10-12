import pandas as pd
import pytest

from analytics.opportunity.features import (
    prepare_opportunity_data,
    calculate_dimension_features,
)
from analytics.opportunity.sizing import (
    build_opportunity_table,
)
from analytics.opportunity.recovery import (
    calculate_recoverable_value,
    calculate_confidence_scenarios,
)
from analytics.opportunity.scoring import (
    calculate_opportunity_score,
)


@pytest.fixture
def sample_transactions():

    return pd.DataFrame(
        {
            "created_at": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-01",
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-02",
                ]
            ),
            "transaction_amount": [
                1000,
                2000,
                3000,
                1500,
                2500,
                4000,
            ],
            "status": [
                "success",
                "failed",
                "success",
                "failed",
                "success",
                "failed",
            ],
            "merchant_key": [
                1,
                1,
                2,
                2,
                3,
                3,
            ],
            "partner_key": [
                1,
                1,
                1,
                2,
                2,
                2,
            ],
            "region_key": [
                1,
                1,
                1,
                2,
                2,
                2,
            ],
        }
    )


def test_prepare_opportunity_data(
    sample_transactions,
):

    result = prepare_opportunity_data(
        sample_transactions
    )

    assert "is_success" in result.columns
    assert "is_failure" in result.columns
    assert "failed_value" in result.columns

    assert result["is_failure"].sum() == 3


def test_dimension_features(
    sample_transactions,
):

    data = prepare_opportunity_data(
        sample_transactions
    )

    result = calculate_dimension_features(
        data,
        "merchant_key",
    )

    assert len(result) == 3

    assert "value_at_risk" in result.columns
    assert "failure_rate" in result.columns


def test_opportunity_sizing(
    sample_transactions,
):

    data = prepare_opportunity_data(
        sample_transactions
    )

    features = calculate_dimension_features(
        data,
        "merchant_key",
    )

    result = build_opportunity_table(
        features
    )

    assert "value_at_risk" in result.columns
    assert "estimated_excess_failure_value" in result.columns

    assert (
        result["value_at_risk"] >= 0
    ).all()


def test_recovery_value(
    sample_transactions,
):

    data = prepare_opportunity_data(
        sample_transactions
    )

    features = calculate_dimension_features(
        data,
        "merchant_key",
    )

    sized = build_opportunity_table(
        features
    )

    result = calculate_recoverable_value(
        sized
    )

    assert "recovery_probability" in result.columns
    assert "recoverable_value" in result.columns

    assert (
        result["recovery_probability"]
        .between(0, 1)
        .all()
    )

    assert (
        result["recoverable_value"]
        <= result["value_at_risk"]
    ).all()


def test_confidence_scenarios(
    sample_transactions,
):

    data = prepare_opportunity_data(
        sample_transactions
    )

    features = calculate_dimension_features(
        data,
        "merchant_key",
    )

    sized = build_opportunity_table(
        features
    )

    recovered = calculate_recoverable_value(
        sized
    )

    result = calculate_confidence_scenarios(
        recovered
    )

    assert (
        result["low_case_recoverable_value"]
        <= result["base_case_recoverable_value"]
    ).all()

    assert (
        result["base_case_recoverable_value"]
        <= result["high_case_recoverable_value"]
    ).all()


def test_opportunity_score(
    sample_transactions,
):

    data = prepare_opportunity_data(
        sample_transactions
    )

    features = calculate_dimension_features(
        data,
        "merchant_key",
    )

    sized = build_opportunity_table(
        features
    )

    recovered = calculate_recoverable_value(
        sized
    )

    scenarios = calculate_confidence_scenarios(
        recovered
    )

    result = calculate_opportunity_score(
        scenarios
    )

    assert "opportunity_score" in result.columns
    assert "priority" in result.columns
    assert "opportunity_rank" in result.columns

    assert (
        result["opportunity_score"]
        .between(0, 100)
        .all()
    )