import pandas as pd


class AnomalyFeatureEngine:

    def __init__(self, transactions: pd.DataFrame):
        self.df = transactions.copy()

    def build_daily_features(self):

        df = self.df.copy()

        df["created_at"] = pd.to_datetime(
            df["created_at"]
        )

        df["date"] = (
            df["created_at"]
            .dt.date
        )

        df["is_success"] = (
            df["status"]
            .astype(str)
            .str.lower()
            .eq("success")
        )

        daily = (
            df.groupby("date")
            .agg(
                transaction_count=(
                    "transaction_id",
                    "count",
                ),

                transaction_value=(
                    "transaction_amount",
                    "sum",
                ),

                successful_transactions=(
                    "is_success",
                    "sum",
                ),

                average_latency_ms=(
                    "processing_time_ms",
                    "mean",
                ),

                p95_latency_ms=(
                    "processing_time_ms",
                    lambda x: x.quantile(0.95),
                ),

                p99_latency_ms=(
                    "processing_time_ms",
                    lambda x: x.quantile(0.99),
                ),

                incident_count=(
                    "incident_flag",
                    "sum",
                ),
            )
            .reset_index()
        )

        daily["success_rate"] = (
            daily["successful_transactions"]
            / daily["transaction_count"]
            * 100
        )

        daily["failure_rate"] = (
            100
            - daily["success_rate"]
        )

        daily = daily.sort_values(
            "date"
        )

        return daily