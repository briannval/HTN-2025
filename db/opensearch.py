import os
from datetime import datetime

from bedrock import generate_embedding
from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv()


class OpenSearchClient:
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = "us-east-2"
        self.host = os.getenv("OPENSEARCH_HOST")
        self.index_name = "my-index"

        awsauth = AWS4Auth(self.aws_access_key, self.aws_secret_key, self.region, "es")

        self.client = OpenSearch(
            hosts=[{"host": self.host, "port": 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )

    def index_document(self, embedding, dynamodb_pk, description, location, time=None):
        if time is None:
            time = datetime.now().isoformat()

        document = {
            "embedding": embedding,
            "dynamodb_pk": dynamodb_pk,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "location": location,
            "time": time,
        }

        response = self.client.index(index=self.index_name, body=document)

        return response

    def search_by_vector(self, query_embedding, size=10):
        search_body = {
            "size": size,
            "query": {"knn": {"embedding": {"vector": query_embedding, "k": size}}},
        }

        response = self.client.search(index=self.index_name, body=search_body)

        return response

    def search_by_text(self, query_text, size=10):
        search_body = {
            "size": size,
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["description", "location"],
                }
            },
        }

        response = self.client.search(index=self.index_name, body=search_body)

        return response

    def delete_document(self, doc_id):
        response = self.client.delete(index=self.index_name, id=doc_id)

        return response

    def bulk_index(self, documents):
        bulk_body = []

        for doc in documents:
            bulk_body.append({"index": {"_index": self.index_name}})
            bulk_body.append(doc)

        response = self.client.bulk(body=bulk_body)
        return response


if __name__ == "__main__":
    opensearch_client = OpenSearchClient()
    query = input("Enter your query: ")
    res = opensearch_client.search_by_vector(generate_embedding(query))
    print(res)
