import os
from datetime import datetime

from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv()

TEXT_QUERY_SIZE = 3


class OpenSearchClient:
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = "us-east-2"
        self.host = os.getenv("OPENSEARCH_HOST")
        self.index_name = "hack-the-north"

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
        print(len(query_embedding))
        search_body = {
            "size": size,
            "query": {"knn": {"embedding": {"vector": query_embedding, "k": size}}},
        }

        response = self.client.search(index=self.index_name, body=search_body)

        return response

    def search_by_text(self, query_text, size=TEXT_QUERY_SIZE):
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

    def get_search_by_text_results_prompt(self, response):
        return "\n".join(
            [
                f'At {el["_source"]["time"]}, in {el["_source"]["location"]}, {el["_source"]["description"]}'
                for el in response["hits"]["hits"]
            ]
        )

    def delete_document(self, doc_id):
        response = self.client.delete(index=self.index_name, id=doc_id)

        return response

    def bulk_index(self, documents):
        bulk_body = []

        for doc in documents:
            bulk_body.append({"index": {"_index": self.index_name}})
            bulk_body.append(doc)

        response = self.client.bulk(body=bulk_body)["hits"]["hits"]
        return [el["_source"]["description"] for el in response]

    def get_all_documents(self, size=100):
        search_body = {"query": {"match_all": {}}, "size": size}
        response = self.client.search(index=self.index_name, body=search_body)
        return response

    def get_document_by_id(self, doc_id):
        try:
            response = self.client.get(index=self.index_name, id=doc_id)
            return response
        except Exception as e:
            return f"Document not found: {str(e)}"

    def get_index_stats(self):
        try:
            stats = self.client.indices.stats(index=self.index_name)
            return stats
        except Exception as e:
            return f"Error getting index stats: {str(e)}"

    def count_documents(self):
        try:
            count = self.client.count(index=self.index_name)
            return count["count"]
        except Exception as e:
            return f"Error counting documents: {str(e)}"

    def list_all_documents_pretty(self, size=100):
        try:
            response = self.get_all_documents(size)
            documents = response["hits"]["hits"]

            print(f"Found {len(documents)} documents:")
            print("=" * 50)

            for i, doc in enumerate(documents, 1):
                source = doc["_source"]
                print(f"Document {i} (ID: {doc['_id']}):")
                print(f"  Description: {source.get('description', 'N/A')}")
                print(f"  Location: {source.get('location', 'N/A')}")
                print(f"  Time: {source.get('time', 'N/A')}")
                print(f"  Created: {source.get('created_at', 'N/A')}")
                print(f"  DynamoDB Key: {source.get('dynamodb_pk', 'N/A')}")
                print("-" * 30)

            return documents
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []


if __name__ == "__main__":
    opensearch_client = OpenSearchClient()
    opensearch_client.list_all_documents_pretty()
    query = input("Enter your query: ")
    res = opensearch_client.search_by_text(query)
    print(opensearch_client.get_search_by_text_results_prompt(res))
