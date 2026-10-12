import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


MODEL_FEATURES = [
    "transaction_count",
    "transaction_value",
    "success_rate",
    "failure_rate",
    "average_latency_ms",
    "p95_latency_ms",
    "p99_latency_ms",
    "incident_count",
]


class IsolationForestDetector:

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ):

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200,
        )

        self.scaler = StandardScaler()

    def detect(
        self,
        daily: pd.DataFrame,
    ) -> pd.DataFrame:

        result = daily.copy()

        model_data = (
            result[MODEL_FEATURES]
            .replace(
                [float("inf"), float("-inf")],
                0,
            )
            .fillna(0)
        )

        scaled = self.scaler.fit_transform(
            model_data
        )

        predictions = (
            self.model.fit_predict(
                scaled
            )
        )

        scores = (
            self.model
            .decision_function(
                scaled
            )
        )

        result["ml_anomaly"] = (
            predictions == -1
        )

        result["anomaly_score"] = (
            -scores
        )

        return result