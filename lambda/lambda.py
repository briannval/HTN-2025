import json
import os
from datetime import datetime

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

bedrock = boto3.client("bedrock-runtime")

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = "us-east-2"
host = os.getenv("OPENSEARCH_HOST")
index_name = "hack-the-north"

awsauth = AWS4Auth(aws_access_key, aws_secret_key, region, "es")

os_client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)


def generate_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}),
    )
    embedding = json.loads(response["body"].read())["embedding"]
    return embedding


def lambda_handler(event, context):
    for record in event["Records"]:
        dynamodb_record = record["dynamodb"]["NewImage"]
        pk = dynamodb_record["PK"]["S"]
        description = dynamodb_record["description"]["S"]
        time = dynamodb_record["time"]["S"]
        location = dynamodb_record["location"]["S"]
        embedding = generate_embedding(description)

        doc_body = {
            "dynamodb_pk": pk,
            "embedding": embedding,
            "created_at": datetime.utcnow().isoformat(),
            "description": description,
            "time": time,
            "location": location,
        }

        os_client.index(index=index_name, id=pk, body=doc_body)
