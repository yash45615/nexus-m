KPI_THRESHOLDS = {

    "success_rate": {
        "warning": 95.0,
        "critical": 90.0,
        "direction": "higher_is_better",
    },

    "failure_rate": {
        "warning": 5.0,
        "critical": 10.0,
        "direction": "lower_is_better",
    },

    "p95_processing_latency": {
        "warning": 500.0,
        "critical": 1000.0,
        "direction": "lower_is_better",
    },

    "p99_processing_latency": {
        "warning": 1000.0,
        "critical": 2000.0,
        "direction": "lower_is_better",
    },
}


def evaluate_threshold(metric: str, value: float):

    if metric not in KPI_THRESHOLDS:
        return "NO_THRESHOLD"

    threshold = KPI_THRESHOLDS[metric]

    direction = threshold["direction"]

    if direction == "higher_is_better":

        if value < threshold["critical"]:
            return "CRITICAL"

        if value < threshold["warning"]:
            return "WARNING"

        return "HEALTHY"

    if direction == "lower_is_better":

        if value >= threshold["critical"]:
            return "CRITICAL"

        if value >= threshold["warning"]:
            return "WARNING"

        return "HEALTHY"

    return "UNKNOWN"