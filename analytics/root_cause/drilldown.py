import pandas as pd


class RootCauseDrilldown:

    def __init__(
        self,
        baseline: pd.DataFrame,
        incident: pd.DataFrame,
    ):

        self.baseline = baseline.copy()
        self.incident = incident.copy()

    def analyze_dimension(
        self,
        dimension: str,
    ) -> pd.DataFrame:

        baseline = (
            self.baseline
            .groupby(dimension)
            .agg(
                baseline_transactions=(
                    "transaction_id",
                    "count",
                ),

                baseline_failures=(
                    "is_failure",
                    "sum",
                ),

                baseline_value=(
                    "transaction_amount",
                    "sum",
                ),
            )
            .reset_index()
        )

        incident = (
            self.incident
            .groupby(dimension)
            .agg(
                incident_transactions=(
                    "transaction_id",
                    "count",
                ),

                incident_failures=(
                    "is_failure",
                    "sum",
                ),

                incident_value=(
                    "transaction_amount",
                    "sum",
                ),
            )
            .reset_index()
        )

        result = baseline.merge(
            incident,
            on=dimension,
            how="outer",
        ).fillna(0)

        result["baseline_failure_rate"] = (
            result["baseline_failures"]
            / result["baseline_transactions"]
            .replace(0, 1)
            * 100
        )

        result["incident_failure_rate"] = (
            result["incident_failures"]
            / result["incident_transactions"]
            .replace(0, 1)
            * 100
        )

        result["failure_rate_change"] = (
            result["incident_failure_rate"]
            - result["baseline_failure_rate"]
        )

        result["failure_change"] = (
            result["incident_failures"]
            - result["baseline_failures"]
        )

        result["value_change"] = (
            result["incident_value"]
            - result["baseline_value"]
        )

        return result.sort_values(
            "failure_change",
            ascending=False,
        )