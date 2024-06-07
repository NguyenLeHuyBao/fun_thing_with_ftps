from datetime import datetime, timedelta
from airflow import DAG
from process.transfer_ftp import transfer_files
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 6),
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'sftp_transfer_dag',
    default_args=default_args,
    description='Hello world',
    schedule_interval=None,
)

ftp_data_replicate = PythonOperator(
    python_callable=transfer_files,
    task_id='ftp_data_replicate',
    dag=dag
)

ftp_data_replicate
