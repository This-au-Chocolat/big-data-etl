from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from worldbank_functions import (
    extract_worldbank_data,
    transform_worldbank_data,
    load_worldbank_data
)

with DAG(
    dag_id="worldbank_gdp_pipeline",
    start_date=datetime(2025, 7, 22),
    schedule=None,
    catchup=False,
    tags=["worldbank", "gdp"]
) as dag:

    extract_worldbank = PythonOperator(
        task_id="extract_worldbank",
        python_callable=extract_worldbank_data,
    )

    transform_worldbank = PythonOperator(
        task_id="transform_worldbank",
        python_callable=transform_worldbank_data,
    )

    load_worldbank = PythonOperator(
        task_id="load_worldbank",
        python_callable=load_worldbank_data,
    )

    extract_worldbank >> transform_worldbank >> load_worldbank
