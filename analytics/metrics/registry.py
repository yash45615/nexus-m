from analytics.metrics.definitions import (
    METRIC_DEFINITIONS,
    MetricDefinition,
)


class MetricRegistry:

    def __init__(self):
        self._metrics = {
            metric.name: metric
            for metric in METRIC_DEFINITIONS
        }

    def get(self, name: str) -> MetricDefinition:
        if name not in self._metrics:
            raise KeyError(f"Unknown metric: {name}")

        return self._metrics[name]

    def list_metrics(self) -> list[MetricDefinition]:
        return list(self._metrics.values())

    def names(self) -> list[str]:
        return list(self._metrics.keys())