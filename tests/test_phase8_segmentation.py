import pandas as pd
import pytest

from analytics.segmentation.features import (
    MerchantFeatureEngine,
)

from analytics.segmentation.rules import (
    apply_business_segments,
)

from analytics.segmentation.clustering import (
    MerchantClusterEngine,
)


@pytest.fixture
def transactions():

    return pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "merchant_key": 1,
                "transaction_amount": 1000,
                "processing_time_ms": 100,
                "status": "success",
                "incident_flag": False,
            },
            {
                "transaction_id": "T2",
                "merchant_key": 1,
                "transaction_amount": 1500,
                "processing_time_ms": 120,
                "status": "success",
                "incident_flag": False,
            },
            {
                "transaction_id": "T3",
                "merchant_key": 1,
                "transaction_amount": 500,
                "processing_time_ms": 150,
                "status": "failed",
                "incident_flag": True,
            },
            {
                "transaction_id": "T4",
                "merchant_key": 2,
                "transaction_amount": 200,
                "processing_time_ms": 300,
                "status": "success",
                "incident_flag": False,
            },
            {
                "transaction_id": "T5",
                "merchant_key": 2,
                "transaction_amount": 300,
                "processing_time_ms": 400,
                "status": "success",
                "incident_flag": False,
            },
            {
                "transaction_id": "T6",
                "merchant_key": 2,
                "transaction_amount": 200,
                "processing_time_ms": 350,
                "status": "failed",
                "incident_flag": False,
            },
        ]
    )


def test_feature_engine(transactions):

    engine = MerchantFeatureEngine(
        transactions
    )

    features = engine.build_features()

    assert len(features) == 2

    assert (
        features[
            "transaction_count"
        ].sum()
        == 6
    )

    assert "success_rate" in features.columns
    assert "failure_rate" in features.columns
    assert "value_at_risk" in features.columns


def test_business_segments(transactions):

    engine = MerchantFeatureEngine(
        transactions
    )

    features = engine.build_features()

    segmented = apply_business_segments(
        features
    )

    assert "business_segment" in segmented.columns

    assert (
        segmented["business_segment"]
        .notna()
        .all()
    )


def test_kmeans(transactions):

    engine = MerchantFeatureEngine(
        transactions
    )

    features = engine.build_features()

    model = MerchantClusterEngine(
        n_clusters=2
    )

    result = model.fit_predict(
        features
    )

    assert "cluster_id" in result.columns

    assert result["cluster_id"].notna().all()

    assert (
        result["cluster_id"]
        .nunique()
        <= 2
    )