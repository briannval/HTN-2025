import os

from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv()  # Load .env file

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
region = os.getenv("AWS_REGION")
host = os.getenv("OPENSEARCH_HOST")

if __name__ == "__main__":
    awsauth = AWS4Auth(
        aws_access_key, aws_secret_key, region, "es", session_token=aws_session_token
    )

    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    index_name = "my-index"

    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "embedding": {"type": "knn_vector", "dimension": 4},
                "dynamodb_pk": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        },
    }

    client.indices.create(index=index_name, body=index_body, ignore=400)
