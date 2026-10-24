import json


def lambda_handler(event, context):
    """Placeholder Lambda for CSV cleaning and validation."""
    print("Event received:", json.dumps(event))

    records = []
    for record in event.get("Records", []):
        bucket = record.get("s3", {}).get("bucket", {}).get("name")
        key = record.get("s3", {}).get("object", {}).get("key")
        records.append({"bucket": bucket, "key": key})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "CSV cleaner invoked",
            "records": records
        })
    }
