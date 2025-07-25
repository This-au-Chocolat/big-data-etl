# dags/pipeline_dag.py
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from pipeline import (
    extract_worldbank_data,
    transform_worldbank_data,
    extract_restcountries_data,
    transform_restcountries_data,
    extract_frankfurter_data,
    transform_frankfurter_data,
    unified_data_pipeline  # Reemplazo de load_all
)

with DAG(
    dag_id="unified_data_pipeline",
    schedule_interval="@daily",  # Updated to schedule daily
    start_date=pendulum.datetime(2025, 7, 20, tz="UTC"),
    catchup=False,
    tags=["unified", "api", "pipeline"],
) as dag:

    # === World Bank Tasks ===
    extract_worldbank = PythonOperator(
        task_id="extract_worldbank",
        python_callable=extract_worldbank_data
    )
    transform_worldbank = PythonOperator(
        task_id="transform_worldbank",
        python_callable=transform_worldbank_data
    )

    # === Restcountries Tasks ===
    extract_restcountries = PythonOperator(
        task_id="extract_restcountries",
        python_callable=extract_restcountries_data
    )
    transform_restcountries = PythonOperator(
        task_id="transform_restcountries",
        python_callable=transform_restcountries_data
    )

    # === Frankfurter Tasks ===
    extract_frankfurter = PythonOperator(
        task_id="extract_frankfurter",
        python_callable=extract_frankfurter_data
    )
    transform_frankfurter = PythonOperator(
        task_id="transform_frankfurter",
        python_callable=transform_frankfurter_data
    )

    # === Load Once ===
    load_all_task = PythonOperator(
        task_id="load_all",
        python_callable=unified_data_pipeline 
    )

    # === Dependencies ===
    extract_worldbank >> transform_worldbank >> load_all_task
    extract_restcountries >> transform_restcountries >> load_all_task
    extract_frankfurter >> transform_frankfurter >> load_all_task
