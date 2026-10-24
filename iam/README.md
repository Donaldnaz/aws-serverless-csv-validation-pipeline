# IAM Policy Documents for the CSV Validation Pipeline

This folder contains example IAM policy documents for the AWS services used by the repository.

The JSON policies below intentionally use explicit placeholder values so they are easy to customize before deployment.

- `lambda-execution-policy.json` — least-privilege permissions for the CSV cleaner and invalid-row Lambda functions.
- `s3-access-policy.json` — bucket read/write permissions for CSV source and invalid-row destinations.
- `dynamodb-access-policy.json` — permissions for writing accepted records to DynamoDB.
- `sns-publish-policy.json` — permissions to publish pipeline notifications.
- `step-functions-execution-role.json` — execution role for the orchestration workflow.

Required placeholder replacements before deployment:
- `REPLACE_WITH_AWS_ACCOUNT_ID`
- `REPLACE_WITH_CSV_INPUT_BUCKET`
- `REPLACE_WITH_INVALID_CSV_BUCKET`
- `REPLACE_WITH_VALID_RECORDS_TABLE`
- `REPLACE_WITH_VALIDATION_TOPIC`
- `REPLACE_WITH_CSV_CLEANER_FUNCTION`
- `REPLACE_WITH_INVALID_ROWS_FUNCTION`

These examples are meant to be edited directly before creating AWS roles or attaching policies.
