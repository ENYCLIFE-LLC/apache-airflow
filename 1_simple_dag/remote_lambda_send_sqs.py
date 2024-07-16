import json
import boto3

def lambda_handler(event, context):
    sqs_client = boto3.client('sqs')
    queue_url = 'your-sqs-queue-url'

    # Define the message to send to SQS
    message = {
        'event': 'job_trigger',
        'details': 'Job details or parameters here'
    }

    # Send the message to the SQS queue
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Message sent to SQS',
            'messageId': response['MessageId']
        })
    }
