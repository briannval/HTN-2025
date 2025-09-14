import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

logger = logging.getLogger(__name__)


class DynamoDBInterface:

    def __init__(self):
        self.table_name = "hack_the_north"
        self.region_name = "us-east-2"

        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=self.region_name,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        self.table = self.dynamodb.Table(self.table_name)

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


if __name__ == "__main__":
    db = DynamoDBInterface()
    locations_descriptions = [
        {
            "location": "Toronto, ON",
            "description": "In front of you is a large transit station platform with buses pulling in and out. To your left is a row of metal benches, and to your right you can hear a coffee kiosk with the sound of milk steaming.",
        },
        {
            "location": "Vancouver, BC",
            "description": "In front of you is the ocean, with gentle waves hitting the rocks. To your left is the seawall path where cyclists are passing quickly, and to your right you can feel the breeze blowing in from the water.",
        },
        {
            "location": "Montreal, QC",
            "description": "In front of you are rows of market stalls with voices calling out prices. To your left is a bakery stand with the smell of fresh bread, and to your right are baskets of ripe fruit being arranged.",
        },
        {
            "location": "Calgary, AB",
            "description": "In front of you is a wide intersection with cars rushing past. To your left is a pedestrian crossing signal making a clicking sound, and to your right you can hear people chatting while waiting to cross.",
        },
        {
            "location": "Ottawa, ON",
            "description": "In front of you is a tall exhibit wall with paintings. To your left is a quiet group listening to an audio guide, and to your right you can hear footsteps echoing across the polished floor.",
        },
        {
            "location": "Halifax, NS",
            "description": "In front of you is the harbor with a ferry preparing to leave. To your left are wooden planks underfoot that creak slightly, and to your right you can hear gulls circling above the water.",
        },
        {
            "location": "Winnipeg, MB",
            "description": "In front of you is the café counter where drinks are being made. To your left is a row of small tables where people are talking, and to your right the smell of roasted beans drifts strongly.",
        },
        {
            "location": "Edmonton, AB",
            "description": "In front of you are several store entrances with soft music playing. To your left is the sound of children laughing in the distance, and to your right is a perfume shop releasing a strong floral scent.",
        },
        {
            "location": "Quebec City, QC",
            "description": "In front of you is a narrow cobblestone street with people walking closely together. To your left is a bakery giving off the smell of pastries, and to your right a violinist is playing lively music.",
        },
        {
            "location": "Victoria, BC",
            "description": "In front of you is an open grassy field inside a park. To your left you hear birds chirping in the trees, and to your right children are laughing and running across the playground.",
        },
    ]

    for i, obj in enumerate(locations_descriptions):
        time = datetime.now().isoformat()
        location = obj["location"]
        description = obj["description"]
        db.add_entry(time, location, description)
        logger.info(f"Added entry {i + 1} of {len(locations_descriptions)}")
