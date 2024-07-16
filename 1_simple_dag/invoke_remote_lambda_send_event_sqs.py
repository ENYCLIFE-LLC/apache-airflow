"""
To achieve a workflow where Apache Airflow invokes a remote Lambda function that sends an event to SNS or SQS, and another service listens to SNS or SQS to execute a job:

1. Invoke the Lambda Function from Airflow: Use the AwsLambdaInvokeFunctionOperator to invoke your Lambda function.
2. Lambda Function Sends Event to SNS or SQS: The Lambda function sends an event to an SNS topic or SQS queue.
3. Service Listens to SNS or SQS: Another service (e.g., AWS Batch, Fargate) is set up to listen to the SNS topic or SQS queue and execute a job.
4. Monitor and Retrieve Job Status: Use additional Airflow operators or sensors to monitor the status of the jobs triggered by the SNS or SQS messages and retrieve the response data.
"""

from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import AwsLambdaInvokeFunctionOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.lambda_function import AwsLambdaHook
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from airflow.utils.dates import days_ago
from datetime import timedelta
import boto3
import json

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'invoke_lambda_and_handle_events',
    default_args=default_args,
    description='A DAG to invoke a Lambda function and handle subsequent events',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

# Lambda function details
LAMBDA_FUNCTION_NAME = 'your-lambda-function-name'
REGION_NAME = 'your-region'
SQS_QUEUE_URL = 'your-sqs-queue-url'

# Task to invoke the Lambda function
invoke_lambda = AwsLambdaInvokeFunctionOperator(
    task_id='invoke_lambda',
    function_name=LAMBDA_FUNCTION_NAME,
    invocation_type='Event',  # Use 'Event' for asynchronous invocation
    aws_conn_id='aws_default',
    region_name=REGION_NAME,
    log_type='None',
    dag=dag,
)

# Task to wait for a message on the SQS queue
wait_for_sqs_message = SqsSensor(
    task_id='wait_for_sqs_message',
    sqs_queue=SQS_QUEUE_URL,
    aws_conn_id='aws_default',
    region_name=REGION_NAME,
    max_messages=1,
    wait_time_seconds=20,
    dag=dag,
)

def process_sqs_message(**kwargs):
    ti = kwargs['ti']
    messages = ti.xcom_pull(task_ids='wait_for_sqs_message')
    for message in messages:
        body = json.loads(message.body)
        # Process the message body as needed
        print(f'SQS message body: {body}')
        # Delete the message from the queue after processing
        sqs_client = boto3.client('sqs', region_name=REGION_NAME)
        sqs_client.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=message.receipt_handle
        )
    return body

process_sqs_message_task = PythonOperator(
    task_id='process_sqs_message',
    python_callable=process_sqs_message,
    provide_context=True,
    dag=dag,
)

# Task dependencies
invoke_lambda >> wait_for_sqs_message >> process_sqs_message_task
