import json


def lambda_handler(event, context):
    """Placeholder Lambda to write invalid rows to a downstream resource."""
    print("Invalid rows event:", json.dumps(event))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Invalid rows processed",
            "items": event.get("invalidRows", [])
        })
    }
