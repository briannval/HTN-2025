import json

import boto3


def generate_embedding(text):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}),
    )
    embedding = json.loads(response["body"].read())["embedding"]
    return embedding
