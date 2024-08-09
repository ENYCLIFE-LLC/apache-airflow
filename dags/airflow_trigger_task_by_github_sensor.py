"""
"""

import logging
from datetime import timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.models.variable import Variable
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
from custom_github_sensors import GitHubPRMergedSensor, GitHubFileChangedSensor


# Initialize the logger
logger = logging.getLogger(__name__)


DEFAULT_ARGS = {
    'owner': 'JC COURSE',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='3_airflow_trigger_task_by_github_sensor',
    schedule_interval='@once',
    start_date=days_ago(1),
    catchup=False,
    tags=['JC COURSE', 'Sensors'],
    default_args=DEFAULT_ARGS,
) as dag:
    # pr_merge_sensor_task = GitHubPRMergedSensor(
    #     task_id='check_pr_merged',
    #     github_conn_id='github_default',
    #     owner='ENYCLIFE-LLC',
    #     repo='apache-airflow',
    #     branch='master',
    #     poke_interval=60, # Time invterval between pokes, the sensor will check the condition every 60 seconds
    #     timeout=120, # Timeout for the sensor in seconds(2 mins)
    # )
    
    file_change_sensor_task = GitHubFileChangedSensor(
        task_id='check_file_changed',
        github_conn_id='github_default',
        owner='ENYCLIFE-LLC',
        repo='apache-airflow',
        branch='master',
        poke_interval=300, # Time invterval between pokes, the sensor will check the condition every 60 seconds
        timeout=600, # Timeout for the sensor in seconds(2 mins)
        file_path='ReadMe.md', # the file name is not case sensitive
    )
    
    process_results = EmptyOperator(
        task_id='process_results',
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # [pr_merge_sensor_task, file_change_sensor_task] >> process_results
    file_change_sensor_task >> process_results