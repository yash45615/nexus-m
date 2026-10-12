from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    category: str
    description: str
    numerator: str | None
    denominator: str | None
    grain: str
    dimensions: List[str]
    unit: str
    higher_is_better: bool
    owner: str


METRIC_DEFINITIONS = [

    MetricDefinition(
        name="transaction_count",
        category="volume",
        description="Total number of transactions.",
        numerator="transaction_count",
        denominator=None,
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
            "category",
        ],
        unit="count",
        higher_is_better=True,
        owner="Payments Analytics",
    ),

    MetricDefinition(
        name="success_rate",
        category="reliability",
        description="Percentage of transactions successfully processed.",
        numerator="successful_transactions",
        denominator="transaction_count",
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
            "category",
        ],
        unit="percentage",
        higher_is_better=True,
        owner="Payments Analytics",
    ),

    MetricDefinition(
        name="failure_rate",
        category="reliability",
        description="Percentage of transactions that failed.",
        numerator="failed_transactions",
        denominator="transaction_count",
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
            "category",
        ],
        unit="percentage",
        higher_is_better=False,
        owner="Payments Analytics",
    ),

    MetricDefinition(
        name="total_transaction_value",
        category="financial",
        description="Total monetary value of transactions.",
        numerator="transaction_amount",
        denominator=None,
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
            "category",
        ],
        unit="currency",
        higher_is_better=True,
        owner="Finance Analytics",
    ),

    MetricDefinition(
        name="average_transaction_value",
        category="financial",
        description="Average monetary value per transaction.",
        numerator="total_transaction_value",
        denominator="transaction_count",
        grain="transaction",
        dimensions=[
            "merchant",
            "partner",
            "region",
            "category",
        ],
        unit="currency",
        higher_is_better=True,
        owner="Finance Analytics",
    ),

    MetricDefinition(
        name="p95_processing_latency",
        category="performance",
        description="95th percentile transaction processing latency.",
        numerator=None,
        denominator=None,
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
        ],
        unit="milliseconds",
        higher_is_better=False,
        owner="Platform Analytics",
    ),

    MetricDefinition(
        name="p99_processing_latency",
        category="performance",
        description="99th percentile transaction processing latency.",
        numerator=None,
        denominator=None,
        grain="transaction",
        dimensions=[
            "date",
            "merchant",
            "partner",
            "region",
        ],
        unit="milliseconds",
        higher_is_better=False,
        owner="Platform Analytics",
    ),
]