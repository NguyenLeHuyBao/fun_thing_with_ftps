from datetime import datetime, timedelta
from airflow import DAG
from process.transfer_ftp import transfer_files
from airflow.operators.python import PythonOperator
from configs.dev import FTPSourceInfo, FTPReplicateInfo

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
    catchup=False,
    schedule_interval="0 18 * * *",
)

ftp_data_replicate = PythonOperator(
    python_callable=transfer_files,
    task_id='ftp_data_replicate',
    dag=dag,
    provide_context=True,
    op_kwargs = {
        'ftp_source': FTPSourceInfo,
        'ftp_replicate': FTPReplicateInfo
    }
)

ftp_data_replicate
