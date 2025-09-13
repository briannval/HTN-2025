import logging
from datetime import datetime
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBInterface:

    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        self.table_name = table_name
        self.region_name = region_name

        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    def add_entry(
        self, time: str, location: str, description: str, entry_id: Optional[str] = None
    ) -> bool:
        try:
            if entry_id is None:
                entry_id = f"entry_{datetime.now().isoformat()}"

            item = {
                "id": entry_id,
                "time": time,
                "location": location,
                "description": description,
                "created_at": datetime.now().isoformat(),
            }

            response = self.table.put_item(Item=item)
            logger.info(f"Successfully added entry with ID: {entry_id}")
            return True

        except ClientError as e:
            logger.error(f"Error adding entry: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding entry: {str(e)}")
            return False

    def get_entry(self, entry_id: str) -> Optional[Dict]:
        try:
            response = self.table.get_item(Key={"id": entry_id})
            return response.get("Item")

        except ClientError as e:
            logger.error(f"Error retrieving entry: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving entry: {str(e)}")
            return None

    def get_entries_by_location(self, location: str) -> List[Dict]:
        try:
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("location").eq(location)
            )
            return response.get("Items", [])

        except ClientError as e:
            logger.error(
                f"Error scanning entries by location: {e.response['Error']['Message']}"
            )
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning entries: {str(e)}")
            return []

    def get_entries_by_time_range(self, start_time: str, end_time: str) -> List[Dict]:
        try:
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("time").between(
                    start_time, end_time
                )
            )
            return response.get("Items", [])

        except ClientError as e:
            logger.error(
                f"Error scanning entries by time range: {e.response['Error']['Message']}"
            )
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning entries: {str(e)}")
            return []

    def update_entry(self, entry_id: str, updates: Dict) -> bool:
        try:
            update_expression = "SET "
            expression_attribute_values = {}

            for key, value in updates.items():
                if key != "id":
                    update_expression += f"{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = value

            update_expression = update_expression.rstrip(", ")

            update_expression += ", updated_at = :updated_at"
            expression_attribute_values[":updated_at"] = datetime.now().isoformat()

            response = self.table.update_item(
                Key={"id": entry_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW",
            )

            logger.info(f"Successfully updated entry with ID: {entry_id}")
            return True

        except ClientError as e:
            logger.error(f"Error updating entry: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating entry: {str(e)}")
            return False

    def delete_entry(self, entry_id: str) -> bool:
        try:
            response = self.table.delete_item(Key={"id": entry_id})
            logger.info(f"Successfully deleted entry with ID: {entry_id}")
            return True

        except ClientError as e:
            logger.error(f"Error deleting entry: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting entry: {str(e)}")
            return False

    def list_all_entries(self, limit: Optional[int] = None) -> List[Dict]:
        try:
            if limit:
                response = self.table.scan(Limit=limit)
            else:
                response = self.table.scan()

            return response.get("Items", [])

        except ClientError as e:
            logger.error(f"Error listing entries: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing entries: {str(e)}")
            return []

    def create_table(self):
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )

            table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully")
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                logger.info(f"Table {self.table_name} already exists")
                return True
            else:
                logger.error(f"Error creating table: {e.response['Error']['Message']}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error creating table: {str(e)}")
            return False
