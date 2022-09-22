from app import app
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import boto3
import base64

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        flash('Image successfully uploaded.')
        send_message_to_sqs(file, filename)
        return redirect(request.url)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


def send_message_to_sqs(image_url, filename):
    sqs = boto3.client('sqs', aws_access_key_id='AKIAUBFTG5VSL4BIHY4H',
                       aws_secret_access_key='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', region_name='us-east-1')
    queue_url = "https://sqs.us-east-1.amazonaws.com/277401234788/Request_Queue"

    # Send message to SQS queue
    string_image = base64.b64encode(image_url.read())
    print(str(filename))
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=(
                '{"image_string" : "' + string_image.decode("utf-8") + '", "image_name": "' + str(filename) + '"}'
        )
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
