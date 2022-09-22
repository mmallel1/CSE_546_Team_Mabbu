import os

import boto3
import time
import base64
import json
from image_classification import classifier

# Create SQS client
sqs = boto3.client('sqs', aws_access_key_id='AKIAUBFTG5VSPSDZDG6I',
                   aws_secret_access_key='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', region_name='us-east-1')
request_queue_url = "https://sqs.us-east-1.amazonaws.com/277401234788/Request_Queue"
response_queue_url = "https://sqs.us-east-1.amazonaws.com/277401234788/Response_Queue"
session = boto3.Session(aws_access_key_id="AKIAUBFTG5VSPSDZDG6I",
                        aws_secret_access_key="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")
s3 = session.resource('s3')
s3_input_bucket = "ccgroup2inputbucket"
s3_output_bucket = "ccgroup2outputbucket"


def get_num_messages_available():
    """Returns the number of messages in the queue """
    response = sqs.get_queue_attributes(QueueUrl=request_queue_url, AttributeNames=['ApproximateNumberOfMessages'])
    messages_available = int(response['Attributes']['ApproximateNumberOfMessages'])
    print(messages_available)
    return messages_available


def recieve_message():
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=request_queue_url,
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

    print(response)

    if 'Messages' in response:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=request_queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message["Body"])
        print("____________________________________________________")
        try:
            json_image = json.loads(message["Body"])
        except Exception as e:
            print(e.args)
        print("****************************************")

        return json_image["image_string"], json_image["image_name"]


def store_data_to_s3(image_string, image_name, image_description):
    print("Storing image and description to output S3 bucket")
    output_file = image_name.split(".")[0] + ".txt"
    output = os.getcwd() + '/' + output_file
    print(output)
    message = image_name.split(".")[0] + ' , ' + image_description
    print(message)
    with open(output_file, 'w') as f1:
        f1.write(str(message))
    f1.close()
    s3.meta.client.upload_file(Filename=output, Bucket=s3_output_bucket, Key=output_file)

    print("Storing image and description to input S3 bucket")
    path = os.getcwd() + '/' + image_name
    print(path)
    with open(image_name, 'wb') as f:
        f.write(base64.b64decode(image_string))
    f.close()

    s3.meta.client.upload_file(Filename=path, Bucket=s3_input_bucket, Key=image_name)
    print("Stored data in S3")


def send_data_to_sqs(image_description):
    # Send message to SQS queue
    print("Sending Message to Response SQS")
    sqs.send_message(
        QueueUrl=response_queue_url,
        MessageBody=(
            image_description
        )
    )
    print("Sent message to Response SQS")


def run_job():
    if (get_num_messages_available()>0):
        image_string, image_name = recieve_message()
        image_description = classifier(image_string)
        store_data_to_s3(image_string, image_name, image_description)
        send_data_to_sqs(image_description)
        time.sleep(5)
    else:
        time.sleep(10)


while (True):
    run_job()
