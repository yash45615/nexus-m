import pandas as pd

from analytics.data_quality.checks import (
    check_duplicates,
    check_numeric_range,
    check_allowed_values,
    check_negative_values,
)

from analytics.data_quality.quality_score import (
    calculate_quality_score,
)


def test_duplicate_detection():

    df = pd.DataFrame({
        "transaction_id": [
            "TX001",
            "TX001",
            "TX002",
        ]
    })

    result = check_duplicates(
        df,
        "transaction_id",
    )

    assert result["passed"] is False
    assert result["actual_value"] == 1


def test_numeric_range():

    df = pd.DataFrame({
        "transaction_amount": [
            100,
            200,
            300,
        ]
    })

    result = check_numeric_range(
        df,
        "transaction_amount",
        minimum=0,
    )

    assert result["passed"] is True


def test_invalid_status():

    df = pd.DataFrame({
        "status": [
            "SUCCESS",
            "FAILED",
            "UNKNOWN",
        ]
    })

    result = check_allowed_values(
        df,
        "status",
        [
            "SUCCESS",
            "FAILED",
        ],
    )

    assert result["passed"] is False
    assert result["actual_value"] == 1


def test_negative_amount():

    df = pd.DataFrame({
        "transaction_amount": [
            100,
            -20,
            300,
        ]
    })

    result = check_negative_values(
        df,
        "transaction_amount",
    )

    assert result["passed"] is False
    assert result["actual_value"] == 1


def test_quality_score():

    results = [
        {
            "passed": True,
            "status": "PASS",
        },
        {
            "passed": True,
            "status": "PASS",
        },
        {
            "passed": False,
            "status": "FAIL",
        },
    ]

    result = calculate_quality_score(
        results
    )

    assert result["total_checks"] == 3
    assert result["passed_checks"] == 2
    assert result["failed_checks"] == 1
    assert result["status"] == "FAIL"