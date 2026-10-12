import pandas as pd
import numpy as np


class KPICalculator:

    def __init__(self, transactions: pd.DataFrame):
        self.df = transactions.copy()

    def transaction_count(self):
        return int(len(self.df))

    def successful_transactions(self):
        return int(
            (self.df["status"].str.lower() == "success").sum()
        )

    def failed_transactions(self):
        return int(
            (self.df["status"].str.lower() != "success").sum()
        )

    def success_rate(self):

        total = self.transaction_count()

        if total == 0:
            return 0.0

        return (
            self.successful_transactions()
            / total
            * 100
        )

    def failure_rate(self):

        total = self.transaction_count()

        if total == 0:
            return 0.0

        return (
            self.failed_transactions()
            / total
            * 100
        )

    def total_transaction_value(self):

        return float(
            self.df["transaction_amount"].sum()
        )

    def successful_transaction_value(self):

        successful = self.df[
            self.df["status"].str.lower() == "success"
        ]

        return float(
            successful["transaction_amount"].sum()
        )

    def failed_transaction_value(self):

        failed = self.df[
            self.df["status"].str.lower() != "success"
        ]

        return float(
            failed["transaction_amount"].sum()
        )

    def average_transaction_value(self):

        if len(self.df) == 0:
            return 0.0

        return float(
            self.df["transaction_amount"].mean()
        )

    def average_processing_latency(self):

        if len(self.df) == 0:
            return 0.0

        return float(
            self.df["processing_time_ms"].mean()
        )

    def p95_processing_latency(self):

        if len(self.df) == 0:
            return 0.0

        return float(
            np.percentile(
                self.df["processing_time_ms"],
                95,
            )
        )

    def p99_processing_latency(self):

        if len(self.df) == 0:
            return 0.0

        return float(
            np.percentile(
                self.df["processing_time_ms"],
                99,
            )
        )

    def calculate_all(self):

        return {
            "transaction_count":
                self.transaction_count(),

            "successful_transactions":
                self.successful_transactions(),

            "failed_transactions":
                self.failed_transactions(),

            "success_rate":
                self.success_rate(),

            "failure_rate":
                self.failure_rate(),

            "total_transaction_value":
                self.total_transaction_value(),

            "successful_transaction_value":
                self.successful_transaction_value(),

            "failed_transaction_value":
                self.failed_transaction_value(),

            "average_transaction_value":
                self.average_transaction_value(),

            "average_processing_latency":
                self.average_processing_latency(),

            "p95_processing_latency":
                self.p95_processing_latency(),

            "p99_processing_latency":
                self.p99_processing_latency(),
        }