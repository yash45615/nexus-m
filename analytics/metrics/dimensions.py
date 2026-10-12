import pandas as pd


class DimensionKPIEngine:

    def __init__(self, transactions: pd.DataFrame):
        self.df = transactions.copy()

    def calculate(self, dimension: str):

        grouped = (
            self.df
            .groupby(dimension)
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

                average_latency=(
                    "processing_time_ms",
                    "mean",
                ),
            )
            .reset_index()
        )

        success_counts = (
            self.df[
                self.df["status"].str.lower() == "success"
            ]
            .groupby(dimension)
            .size()
            .reset_index(
                name="successful_transactions"
            )
        )

        grouped = grouped.merge(
            success_counts,
            on=dimension,
            how="left",
        )

        grouped["successful_transactions"] = (
            grouped["successful_transactions"]
            .fillna(0)
        )

        grouped["success_rate"] = (
            grouped["successful_transactions"]
            / grouped["transaction_count"]
            * 100
        )

        grouped["failure_rate"] = (
            100 - grouped["success_rate"]
        )

        return grouped