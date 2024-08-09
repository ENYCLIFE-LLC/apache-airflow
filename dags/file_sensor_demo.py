 
import logging
from datetime import datetime, timedelta
from os.path import exists
 
from airflow.utils.dates import days_ago
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.time_sensor import TimeSensor
from airflow.sensors.filesystem import FileSensor
 
# Initialize the logger
logger = logging.getLogger(__name__)


DEFAULT_ARGS = {
    'owner': 'JC COURSE',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id='2_file_and_time_sensors_demo',
    default_args=DEFAULT_ARGS,
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['JC COURSE', 'Sensors'],
) as dag:
    
    # Start the task after 5 seconds
    wait_5_seconds_sensor = TimeSensor(
        task_id='wait_5_seconds_to_start',
        target_time=(datetime.now() + timedelta(seconds=5)).time(),
        timeout=20,
    )
    
    create_tmp_file_task = BashOperator(
        task_id='create_tmp_file',
        bash_command='echo "Hello, World!" > /tmp/hello_world.txt',
    )
    
    wait_for_file_sensor = FileSensor(
        task_id='wait_for_file_to_be_present',
        filepath='/tmp/hello_world.txt',
        fs_conn_id='fs_default',
        poke_interval=20, # 10 seconds interval between pokes
        timeout=180, # 3 mins
        mode='poke',
    )
    
    
    process_file_tasks = PythonOperator(
        task_id='print_log_if_file_exists',
        python_callable=lambda: logger.info('File Exists!') if exists('/tmp/hello_world.txt') else logger.info('File does not exist'),
    )
    
    rm_tmp_file_task = BashOperator(task_id="rm_tmp_file", bash_command="rm /tmp/hello_world.txt")
    
    wait_5_seconds_sensor >> create_tmp_file_task >> rm_tmp_file_task
    wait_for_file_sensor >> process_file_tasks >> rm_tmp_file_task