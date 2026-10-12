from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from pipelines.airflow.tasks import (
    run_phase4,
    run_phase7,
    run_phase8,
    run_phase9,
    run_phase10,
    run_phase11,
    run_phase12,
)


default_args = {
    "owner": "nexus-m",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="nexus_m_analytical_pipeline",
    description=(
        "NEXUS-M autonomous merchant and "
        "network intelligence pipeline"
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    tags=[
        "nexus-m",
        "analytics",
        "payments",
        "data-quality",
        "root-cause",
        "reconciliation",
    ],
) as dag:

    phase4 = PythonOperator(
        task_id="kpi_engine",
        python_callable=run_phase4,
    )

    phase7 = PythonOperator(
        task_id="metrics_engine",
        python_callable=run_phase7,
    )

    phase8 = PythonOperator(
        task_id="merchant_segmentation",
        python_callable=run_phase8,
    )

    phase9 = PythonOperator(
        task_id="anomaly_detection",
        python_callable=run_phase9,
    )

    phase10 = PythonOperator(
        task_id="root_cause_analysis",
        python_callable=run_phase10,
    )

    phase11 = PythonOperator(
        task_id="opportunity_sizing",
        python_callable=run_phase11,
    )

    phase12 = PythonOperator(
        task_id="reconciliation",
        python_callable=run_phase12,
    )

    (
        phase4
        >> phase7
        >> phase8
        >> phase9
        >> phase10
        >> phase11
        >> phase12
    )