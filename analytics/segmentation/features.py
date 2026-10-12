import numpy as np
import pandas as pd


class MerchantFeatureEngine:

    def __init__(self, transactions: pd.DataFrame):
        self.df = transactions.copy()

    def build_features(self) -> pd.DataFrame:

        df = self.df.copy()

        df["is_success"] = (
            df["status"]
            .astype(str)
            .str.lower()
            .eq("success")
        )

        df["is_failure"] = ~df["is_success"]

        features = (
            df.groupby("merchant_key")
            .agg(
                transaction_count=(
                    "transaction_id",
                    "count",
                ),

                transaction_value=(
                    "transaction_amount",
                    "sum",
                ),

                average_transaction_value=(
                    "transaction_amount",
                    "mean",
                ),

                average_latency_ms=(
                    "processing_time_ms",
                    "mean",
                ),

                p95_latency_ms=(
                    "processing_time_ms",
                    lambda x: np.percentile(x, 95),
                ),

                successful_transactions=(
                    "is_success",
                    "sum",
                ),

                failed_transactions=(
                    "is_failure",
                    "sum",
                ),

                incident_count=(
                    "incident_flag",
                    "sum",
                ),
            )
            .reset_index()
        )

        features["success_rate"] = (
            features["successful_transactions"]
            / features["transaction_count"]
            * 100
        )

        features["failure_rate"] = (
            features["failed_transactions"]
            / features["transaction_count"]
            * 100
        )

        features["incident_rate"] = (
            features["incident_count"]
            / features["transaction_count"]
            * 100
        )

        features["value_at_risk"] = (
            features["transaction_value"]
            * features["failure_rate"]
            / 100
        )

        return features