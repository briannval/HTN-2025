"""
Example usage of the DynamoDB interface class.
This file demonstrates how to use the DynamoDBInterface class to interact with DynamoDB.
"""

from dynamodb_interface import DynamoDBInterface
from datetime import datetime
import os

def example_usage():
    """
    Example demonstrating how to use the DynamoDB interface.
    """
    
    # Initialize the interface
    # Make sure to set your AWS credentials via environment variables or AWS CLI
    table_name = "my_entries_table"
    db_interface = DynamoDBInterface(table_name=table_name, region_name='us-east-1')
    
    # Optional: Create the table (requires appropriate AWS permissions)
    print("Creating table if it doesn't exist...")
    db_interface.create_table()
    
    # Add some sample entries
    print("\nAdding sample entries...")
    
    # Entry 1
    success = db_interface.add_entry(
        time="2025-01-15T10:30:00",
        location="New York, NY",
        description="Meeting with client at downtown office"
    )
    print(f"Entry 1 added: {success}")
    
    # Entry 2
    success = db_interface.add_entry(
        time="2025-01-15T14:00:00",
        location="San Francisco, CA",
        description="Product demo presentation",
        entry_id="demo_presentation_001"
    )
    print(f"Entry 2 added: {success}")
    
    # Entry 3
    success = db_interface.add_entry(
        time="2025-01-16T09:00:00",
        location="New York, NY",
        description="Team standup meeting"
    )
    print(f"Entry 3 added: {success}")
    
    # Retrieve a specific entry
    print("\nRetrieving specific entry...")
    entry = db_interface.get_entry("demo_presentation_001")
    if entry:
        print(f"Found entry: {entry}")
    else:
        print("Entry not found")
    
    # Get entries by location
    print("\nGetting entries for New York, NY...")
    ny_entries = db_interface.get_entries_by_location("New York, NY")
    print(f"Found {len(ny_entries)} entries in New York")
    for entry in ny_entries:
        print(f"  - {entry['time']}: {entry['description']}")
    
    # Get entries by time range
    print("\nGetting entries for January 15, 2025...")
    entries_jan_15 = db_interface.get_entries_by_time_range(
        "2025-01-15T00:00:00",
        "2025-01-15T23:59:59"
    )
    print(f"Found {len(entries_jan_15)} entries on January 15")
    for entry in entries_jan_15:
        print(f"  - {entry['time']}: {entry['description']} at {entry['location']}")
    
    # Update an entry
    print("\nUpdating an entry...")
    success = db_interface.update_entry(
        "demo_presentation_001",
        {
            "description": "Updated: Product demo presentation with Q&A session",
            "location": "San Francisco, CA (Remote)"
        }
    )
    print(f"Entry updated: {success}")
    
    # List all entries
    print("\nListing all entries...")
    all_entries = db_interface.list_all_entries(limit=10)
    print(f"Total entries: {len(all_entries)}")
    for entry in all_entries:
        print(f"  - ID: {entry['id']}")
        print(f"    Time: {entry['time']}")
        print(f"    Location: {entry['location']}")
        print(f"    Description: {entry['description']}")
        print()

if __name__ == "__main__":
    # Note: Make sure you have AWS credentials configured
    # You can set them via:
    # - AWS CLI: aws configure
    # - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    # - IAM roles (if running on EC2)
    
    print("DynamoDB Interface Example")
    print("=" * 30)
    
    # Check if AWS credentials are available
    if not (os.getenv('AWS_ACCESS_KEY_ID') or os.getenv('AWS_PROFILE')):
        print("Warning: AWS credentials not detected.")
        print("Please configure your AWS credentials before running this example.")
        print("You can use 'aws configure' or set environment variables.")
    else:
        example_usage()
