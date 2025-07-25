# dags/restcountries_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from restcountries_functions import (
    extract_restcountries_data,
    transform_restcountries_data,
    load_restcountries_data
)

with DAG(
    dag_id="restcountries_pipeline",
    start_date=datetime(2025, 7, 22),
    schedule=None,
    catchup=False,
    tags=["restcountries", "countries"]
) as dag:

    extract_restcountries = PythonOperator(
        task_id="extract_restcountries",
        python_callable=extract_restcountries_data,
    )

    transform_restcountries = PythonOperator(
        task_id="transform_restcountries",
        python_callable=transform_restcountries_data,
    )

    load_restcountries = PythonOperator(
        task_id="load_restcountries",
        python_callable=load_restcountries_data,
    )

    extract_restcountries >> transform_restcountries >> load_restcountries
