# IAM Policy Documents for the CSV Validation Pipeline

This folder contains example IAM policy documents that match the AWS services used by the repository:

- `lambda-execution-policy.json` — least-privilege permissions for the CSV cleaner and invalid-row Lambda functions.
- `s3-access-policy.json` — bucket read/write permissions for source CSVs and rejected-row output.
- `dynamodb-access-policy.json` — permissions for writing accepted records to DynamoDB.
- `sns-publish-policy.json` — permissions to publish Step Functions or Lambda notifications.
- `step-functions-execution-role.json` — execution role for the orchestration workflow.

Notes:
- Replace placeholder values such as account IDs, bucket names, table names, and topic ARNs before deployment.
- The examples are intentionally scoped to the services described in the architecture: S3, Lambda, DynamoDB, SNS, and Step Functions.
- For production use, add tighter conditions (for example, prefixes, KMS keys, or resource tags) to reduce exposure.
