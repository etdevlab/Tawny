#!/usr/bin/python3

"""
Library to use the amazon SQS for stuff
"""

import boto3
from botocore.exceptions import ClientError
import json

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.secrets as secrets

sqs_client = boto3.client(
        "sqs", 
        region_name=secrets.AWS_Region,
        aws_access_key_id=secrets.aws_access_key_id,
        aws_secret_access_key=secrets.aws_secret_access_key
)

def send_message(message):
    global sqs_client

    response = sqs_client.send_message(
        QueueUrl=secrets.SQS_URL,
        MessageBody=json.dumps(message)
    )
    return response

def receive_message(amount=1):
    global sqs_client

    response = sqs_client.receive_message(
        QueueUrl=secrets.SQS_URL,
        MaxNumberOfMessages=amount,
        WaitTimeSeconds=20
    )
    return response

def delete_message(receipt_handle):
    global sqs_client

    response = sqs_client.delete_message(
        QueueUrl=secrets.SQS_URL,
        ReceiptHandle=receipt_handle
    )
    return response

def release_message(receipt_handle):
    global sqs_client

    response = sqs_client.change_message_visibility(
        QueueUrl=secrets.SQS_URL,
        ReceiptHandle=receipt_handle,
        VisibilityTimeout=0
    )
    return response

def get_attributes():
    global sqs_client
    return sqs_client.get_queue_attributes(
            QueueUrl=secrets.SQS_URL, 
            AttributeNames=['All']
    )
