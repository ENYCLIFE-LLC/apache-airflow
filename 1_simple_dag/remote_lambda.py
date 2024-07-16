import json
import boto3

def lambda_handler(event, context):
    batch_client = boto3.client('batch')

    # Define job details
    job_queue = 'your-job-queue'
    job_definition = 'your-job-definition'

    # Submit the AWS Batch job
    response = batch_client.submit_job(
        jobName='example-job',
        jobQueue=job_queue,
        jobDefinition=job_definition
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Job submitted successfully',
            'jobId': response['jobId']
        })
    }
