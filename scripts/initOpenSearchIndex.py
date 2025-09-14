import os

from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv()  # Load .env file

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = "us-east-2"
host = os.getenv("OPENSEARCH_HOST")

if __name__ == "__main__":
    awsauth = AWS4Auth(aws_access_key, aws_secret_key, region, "es")

    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    index_name = "hack-the-north"

    # Delete index if it exists
    if client.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}")
        client.indices.delete(index=index_name)

    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "embedding": {"type": "knn_vector", "dimension": 1024},
                "dynamodb_pk": {"type": "keyword"},
                "created_at": {"type": "date"},
                "description": {"type": "text"},
                "location": {"type": "text"},
                "time": {"type": "date"},
            }
        },
    }

    print(f"Creating index: {index_name}")
    client.indices.create(index=index_name, body=index_body)
    print("Index created successfully")
