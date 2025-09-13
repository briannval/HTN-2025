"""
Example usage of the DynamoDB interface class.
This file demonstrates how to use the DynamoDBInterface class to interact with DynamoDB.
"""

import os
from datetime import datetime
import logging

from dynamodb_interface import DynamoDBInterface

logger = logging.getLogger(__name__)


def example_usage():
    """
    Example demonstrating how to use the DynamoDB interface.
    """

    # Initialize the interface
    # Make sure to set your AWS credentials via environment variables or AWS CLI
    table_name = "my_entries_table"
    db_interface = DynamoDBInterface(table_name=table_name, region_name="us-east-1")

    # Optional: Create the table (requires appropriate AWS permissions)
    logger.info("Creating table if it doesn't exist...")
    db_interface.create_table()

    # Add some sample entries
    logger.info("\nAdding sample entries...")

    # Entry 1
    success = db_interface.add_entry(
        time="2025-01-15T10:30:00",
        location="New York, NY",
        description="Meeting with client at downtown office",
    )
    logger.info(f"Entry 1 added: {success}")

    # Entry 2
    success = db_interface.add_entry(
        time="2025-01-15T14:00:00",
        location="San Francisco, CA",
        description="Product demo presentation",
        entry_id="demo_presentation_001",
    )
    logger.info(f"Entry 2 added: {success}")

    # Entry 3
    success = db_interface.add_entry(
        time="2025-01-16T09:00:00",
        location="New York, NY",
        description="Team standup meeting",
    )
    logger.info(f"Entry 3 added: {success}")

    # Retrieve a specific entry
    logger.info("\nRetrieving specific entry...")
    entry = db_interface.get_entry("demo_presentation_001")
    if entry:
        logger.info(f"Found entry: {entry}")
    else:
        logger.warning("Entry not found")

    # Get entries by location
    logger.info("\nGetting entries for New York, NY...")
    ny_entries = db_interface.get_entries_by_location("New York, NY")
    logger.info(f"Found {len(ny_entries)} entries in New York")
    for entry in ny_entries:
        logger.info(f"  - {entry['time']}: {entry['description']}")

    # Get entries by time range
    logger.info("\nGetting entries for January 15, 2025...")
    entries_jan_15 = db_interface.get_entries_by_time_range(
        "2025-01-15T00:00:00", "2025-01-15T23:59:59"
    )
    logger.info(f"Found {len(entries_jan_15)} entries on January 15")
    for entry in entries_jan_15:
        logger.info(f"  - {entry['time']}: {entry['description']} at {entry['location']}")

    # Update an entry
    logger.info("\nUpdating an entry...")
    success = db_interface.update_entry(
        "demo_presentation_001",
        {
            "description": "Updated: Product demo presentation with Q&A session",
            "location": "San Francisco, CA (Remote)",
        },
    )
    logger.info(f"Entry updated: {success}")

    # List all entries
    logger.info("\nListing all entries...")
    all_entries = db_interface.list_all_entries(limit=10)
    logger.info(f"Total entries: {len(all_entries)}")
    for entry in all_entries:
        logger.info(f"  - ID: {entry['id']}")
        logger.info(f"    Time: {entry['time']}")
        logger.info(f"    Location: {entry['location']}")
        logger.info(f"    Description: {entry['description']}")
        logger.info("")


if __name__ == "__main__":
    # Note: Make sure you have AWS credentials configured
    # You can set them via:
    # - AWS CLI: aws configure
    # - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    # - IAM roles (if running on EC2)

    logger.info("DynamoDB Interface Example")
    logger.info("=" * 30)

    # Check if AWS credentials are available
    if not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")):
        logger.warning("Warning: AWS credentials not detected.")
        logger.info("Please configure your AWS credentials before running this example.")
        logger.info("You can use 'aws configure' or set environment variables.")
    else:
        example_usage()
