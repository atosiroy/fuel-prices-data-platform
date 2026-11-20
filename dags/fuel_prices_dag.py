from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

CD = 'cd /opt/airflow/project && '
DBT = '/opt/dbt-venv/bin/dbt'
DBT_ARGS = '--project-dir dbt_project --profiles-dir dbt_project'

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='fuel_prices_daily',
    start_date=datetime(2026, 11, 1),
    schedule='@daily',
    catchup=False,
    default_args=default_args,
    tags=['portfolio'],
) as dag:
    ingest_bronze = BashOperator(
        task_id='ingest_bronze',
        bash_command=CD + 'python -m ingestion.ingest --date {{ ds }}',
    )
    build_silver = BashOperator(
        task_id='build_silver',
        bash_command=CD + 'python -m transform.silver --date {{ ds }}',
    )
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=CD + DBT + ' run ' + DBT_ARGS,
    )
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=CD + DBT + ' test ' + DBT_ARGS,
    )

    ingest_bronze >> build_silver >> dbt_run >> dbt_test