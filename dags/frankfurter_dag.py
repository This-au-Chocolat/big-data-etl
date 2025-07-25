from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from frankfurter_functions import (
    extract_currency_data,
    transform_currency_data,
    load_currency_data
)

with DAG(
    dag_id="frankfurter_currency_pipeline",
    start_date=datetime(2025, 7, 22),
    schedule=None,
    catchup=False,
    tags=["currency", "frankfurter"]
) as dag:

    extract_currency = PythonOperator(
        task_id="extract_currency",
        python_callable=extract_currency_data,
    )

    transform_currency = PythonOperator(
        task_id="transform_currency",
        python_callable=transform_currency_data,
    )

    load_currency = PythonOperator(
        task_id="load_currency",
        python_callable=load_currency_data,
    )

    extract_currency >> transform_currency >> load_currency
