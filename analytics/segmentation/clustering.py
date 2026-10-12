import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


CLUSTER_FEATURES = [
    "transaction_count",
    "transaction_value",
    "average_transaction_value",
    "success_rate",
    "failure_rate",
    "average_latency_ms",
    "p95_latency_ms",
    "incident_rate",
    "value_at_risk",
]


class MerchantClusterEngine:

    def __init__(
        self,
        n_clusters: int = 4,
        random_state: int = 42,
    ):
        self.n_clusters = n_clusters
        self.random_state = random_state

        self.scaler = StandardScaler()

        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        )

    def fit_predict(
        self,
        features: pd.DataFrame,
    ) -> pd.DataFrame:

        result = features.copy()

        model_data = (
            result[CLUSTER_FEATURES]
            .replace(
                [float("inf"), float("-inf")],
                0,
            )
            .fillna(0)
        )

        scaled = self.scaler.fit_transform(
            model_data
        )

        result["cluster_id"] = (
            self.model.fit_predict(
                scaled
            )
        )

        return result

    def get_cluster_profiles(
        self,
        clustered: pd.DataFrame,
    ) -> pd.DataFrame:

        profiles = (
            clustered
            .groupby("cluster_id")
            [CLUSTER_FEATURES]
            .mean()
            .reset_index()
        )

        return profiles