import boto3
import base64

sqs = boto3.client('sqs',aws_access_key_id='AKIAUBFTG5VSPSDZDG6I', aws_secret_access_key='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',region_name='us-east-1')
queue_url = "https://sqs.us-east-1.amazonaws.com/277401234788/Request_Queue"

with open("test_53.JPEG", "rb") as image:
    string_image = base64.b64encode(image.read())
    print(type(string_image))
# Send message to SQS queue
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=(
        '{"image_string" : "'+string_image.decode("utf-8") +'", "image_name":"TEST_NAME_4.JPEG"}'

    )
)

print(response['MessageId'])