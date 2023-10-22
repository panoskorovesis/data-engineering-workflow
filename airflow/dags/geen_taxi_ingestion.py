import os

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingest_script import ingest_callable


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

local_workflow = DAG(
"Geen_Taxi_Ingestion_FINAL",
    # schedule_interval="@monthly",
    # start_date=datetime(2022, 1, 1),
    # end_date=datetime(2022, 11, 1),
    # catchup=False,
    max_active_runs=1
)

URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data' 
URL_TEMPLATE = URL_PREFIX + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
TABLE_NAME_TEMPLATE = 'green_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'

with local_workflow:
    wget_task = BashOperator(
        task_id='wget',
        bash_command=f'curl -sSL {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}'
    )

    check_tast = BashOperator(
        task_id='check',
        bash_command=f'ls -a {AIRFLOW_HOME}'
    )
    
    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=ingest_callable,
        op_kwargs=dict(
            table_name=TABLE_NAME_TEMPLATE,
            csv_file=OUTPUT_FILE_TEMPLATE,
            color='green'
        ),
    )

    wget_task >> check_tast >> ingest_task