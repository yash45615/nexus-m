from pathlib import Path

from pipelines.airflow.config import (
    PROJECT_ROOT,
    PROCESSED_DATA_DIR,
    SYNTHETIC_DATA_DIR,
    ensure_pipeline_directories,
)


def test_project_root_exists():

    assert PROJECT_ROOT.exists()

    assert (
        PROJECT_ROOT
        / "analytics"
    ).exists()


def test_pipeline_directories():

    ensure_pipeline_directories()

    assert PROCESSED_DATA_DIR.exists()

    assert SYNTHETIC_DATA_DIR.exists()


def test_pipeline_modules_exist():

    expected_modules = [
        "analytics.kpi_engine.report",
        "analytics.metrics.report",
        "analytics.segmentation.report",
        "analytics.anomaly_detection.report",
        "analytics.root_cause.report",
        "analytics.opportunity.report",
        "analytics.reconciliation.report",
    ]

    for module in expected_modules:

        module_path = Path(
            *module.split(".")
        )

        assert module_path.with_suffix(
            ".py"
        ).exists()


def test_airflow_dag_file_exists():

    dag_file = (
        PROJECT_ROOT
        / "pipelines"
        / "airflow"
        / "nexus_m_dag.py"
    )

    assert dag_file.exists()


def test_pipeline_tasks_file_exists():

    tasks_file = (
        PROJECT_ROOT
        / "pipelines"
        / "airflow"
        / "tasks.py"
    )

    assert tasks_file.exists()