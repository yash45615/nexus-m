from pathlib import Path

from analytics.kpi_engine.data_loader import (
    AnalyticsDataLoader,
)

from analytics.segmentation.features import (
    MerchantFeatureEngine,
)

from analytics.segmentation.rules import (
    apply_business_segments,
)

from analytics.segmentation.clustering import (
    MerchantClusterEngine,
)

from analytics.segmentation.explanations import (
    add_cluster_explanations,
)


OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "phase8"
)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    loader = AnalyticsDataLoader()

    transactions = (
        loader.load_transactions()
    )

    # ---------------------------------
    # 1. Build merchant features
    # ---------------------------------

    feature_engine = (
        MerchantFeatureEngine(
            transactions
        )
    )

    features = (
        feature_engine
        .build_features()
    )

    features.to_csv(
        OUTPUT_DIR
        / "merchant_features.csv",
        index=False,
    )

    # ---------------------------------
    # 2. Business-rule segmentation
    # ---------------------------------

    business_segments = (
        apply_business_segments(
            features
        )
    )

    business_segments.to_csv(
        OUTPUT_DIR
        / "merchant_business_segments.csv",
        index=False,
    )

    # ---------------------------------
    # 3. ML clustering
    # ---------------------------------

    cluster_engine = (
        MerchantClusterEngine(
            n_clusters=4
        )
    )

    clustered = (
        cluster_engine
        .fit_predict(
            business_segments
        )
    )

    # ---------------------------------
    # 4. Cluster profiles
    # ---------------------------------

    profiles = (
        cluster_engine
        .get_cluster_profiles(
            clustered
        )
    )

    profiles.to_csv(
        OUTPUT_DIR
        / "cluster_profiles.csv",
        index=False,
    )

    # ---------------------------------
    # 5. Explain clusters
    # ---------------------------------

    final = (
        add_cluster_explanations(
            clustered,
            profiles,
        )
    )

    final.to_csv(
        OUTPUT_DIR
        / "merchant_segments.csv",
        index=False,
    )

    print(
        "Phase 8 Merchant Segmentation completed."
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()
    print("Merchant segments:")
    print(
        final[
            [
                "merchant_key",
                "business_segment",
                "cluster_id",
                "cluster_description",
            ]
        ].head(20)
    )


if __name__ == "__main__":
    main()