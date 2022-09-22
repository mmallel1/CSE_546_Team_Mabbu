import boto3
import time

# Create SQS client
sqs = boto3.client('sqs',aws_access_key_id='AKIAUBFTG5VSPSDZDG6I', aws_secret_access_key='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',region_name='us-east-1')
queue_url = "https://sqs.us-east-1.amazonaws.com/277401234788/Response_Queue"

while(True):
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    if 'Messages' in response:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message["Body"])
    time.sleep(1)