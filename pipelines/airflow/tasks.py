from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from pipelines.airflow.config import (
    PROJECT_ROOT,
    LOG_DIR,
)


def run_module(
    module_name: str,
) -> dict:

    started_at = datetime.now()

    command = [
        sys.executable,
        "-m",
        module_name,
    ]

    print()
    print("=" * 70)
    print(f"RUNNING: {module_name}")
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    finished_at = datetime.now()

    log_file = (
        LOG_DIR
        / f"{module_name.replace('.', '_')}.log"
    )

    log_file.write_text(
        (
            f"STARTED: {started_at}\n"
            f"FINISHED: {finished_at}\n"
            f"RETURN CODE: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}\n"
        ),
        encoding="utf-8",
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:

        raise RuntimeError(
            f"Pipeline module failed: "
            f"{module_name}"
        )

    return {
        "module": module_name,
        "status": "SUCCESS",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "log_file": str(log_file),
    }


def run_phase4():

    return run_module(
        "analytics.kpi_engine.report"
    )


def run_phase7():

    return run_module(
        "analytics.metrics.report"
    )


def run_phase8():

    return run_module(
        "analytics.segmentation.report"
    )


def run_phase9():

    return run_module(
        "analytics.anomaly_detection.report"
    )


def run_phase10():

    return run_module(
        "analytics.root_cause.report"
    )


def run_phase11():

    return run_module(
        "analytics.opportunity.report"
    )


def run_phase12():

    return run_module(
        "analytics.reconciliation.report"
    )


def run_full_analytics_pipeline():

    pipeline_start = datetime.now()

    results = []

    tasks = [
        (
            "phase4_kpi_engine",
            run_phase4,
        ),
        (
            "phase7_metrics",
            run_phase7,
        ),
        (
            "phase8_segmentation",
            run_phase8,
        ),
        (
            "phase9_anomaly_detection",
            run_phase9,
        ),
        (
            "phase10_root_cause",
            run_phase10,
        ),
        (
            "phase11_opportunity",
            run_phase11,
        ),
        (
            "phase12_reconciliation",
            run_phase12,
        ),
    ]

    for name, task in tasks:

        started = datetime.now()

        print()
        print(
            f">>> Starting pipeline task: {name}"
        )

        task_result = task()

        finished = datetime.now()

        results.append(
            {
                "name": name,
                "status": task_result["status"],
                "started_at": started.isoformat(),
                "finished_at": finished.isoformat(),
            }
        )

    pipeline_end = datetime.now()

    return {
        "pipeline": "NEXUS-M",
        "status": "SUCCESS",
        "started_at": pipeline_start.isoformat(),
        "finished_at": pipeline_end.isoformat(),
        "tasks": results,
    }