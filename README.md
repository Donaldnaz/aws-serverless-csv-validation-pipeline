# AWS Serverless CSV Validation Pipeline

This repository contains a sample serverless architecture for ingesting, validating, cleaning, and processing CSV files in AWS. The solution is designed to automatically process uploaded CSV data, normalize it, and decide whether records should be accepted or rejected.

The project is structured as a starter/reference implementation and includes placeholder infrastructure definitions, workflow configuration, sample data, and Lambda function scaffolding to help you understand the overall serverless design and extend it into a production-ready pipeline.

## Architecture Overview
<img width="888" height="1056" alt="Screenshot 2026-10-24 000648" src="https://github.com/user-attachments/assets/84448b47-f2ee-46d2-a7a1-4a4c271bf26a" />

## Infrastructure Overview

The pipeline is built around a lightweight event-driven architecture:

- Amazon S3 stores the incoming CSV files.
- Amazon EventBridge watches the S3 bucket for new object uploads.
- A Lambda function processes the uploaded file and validates/cleans the data.
- AWS Step Functions orchestrates the validation decision path.
- Valid rows are sent to a downstream datastore such as DynamoDB.
- Invalid rows are routed to a second Lambda for handling, reporting, or alerting.
- Amazon SNS can be used to send summary notifications for rejected or processed records.

## Architecture Flow

1. A user uploads a CSV file to an S3 bucket.
2. EventBridge detects the S3 ObjectCreated event.
3. The `csvfilecleaner` Lambda is triggered.
4. The Lambda reads the file, validates rows, removes obvious formatting issues, and inspects data quality.
5. The Step Functions workflow decides whether the record is valid or invalid.
6. Valid records continue to storage.
7. Invalid records are processed by the `write-invalid-rows` Lambda and can be stored or reported.

## AWS Services Used

| Service | Purpose | Location |
| --- | --- | --- |
| S3 | Input file storage for uploaded CSVs | `sample-data/` and deployment bucket |
| EventBridge | Event-driven trigger on file upload | `eventbridge/s3-event-pattern.json` |
| Lambda | CSV validation and invalid-row processing | `lambda/` |
| Step Functions | Workflow orchestration and routing | `step-functions/csv-cleaner-workflow.json` |
| DynamoDB | Storage for validated records | Planned infrastructure component |
| SNS | Notifications and summary alerts | Planned infrastructure component |
| IAM | Permissions for Lambdas, S3, Step Functions, and downstream services | `iam/README.md` |

## Repository Structure

```text
aws-serverless-csv-validation-pipeline/
├── README.md
├── architecture/
│   └── architecture.png
├── step-functions/
│   └── csv-cleaner-workflow.json
├── lambda/
│   ├── csvfilecleaner/
│   │   └── lambda_function.py
│   └── write-invalid-rows/
│       └── lambda_function.py
├── eventbridge/
│   └── s3-event-pattern.json
├── iam/
│   ├── README.md
│   ├── lambda-execution-policy.json
│   ├── s3-access-policy.json
│   ├── dynamodb-access-policy.json
│   ├── sns-publish-policy.json
│   └── step-functions-execution-role.json
├── sample-data/
│   └── customers_messy.csv
└── screenshots/
    ├── s3-event-trigger-placeholder.svg
    ├── step-functions-executions.png
    ├── dynamodb-valid-records.png
    └── sns-summary.png
```

## File Descriptions

### `step-functions/csv-cleaner-workflow.json`
Defines the orchestration flow for the CSV processing pipeline. The workflow starts with the CSV cleaner Lambda, then branches based on whether the output is valid or invalid.

### `lambda/csvfilecleaner/lambda_function.py`
This Lambda is the main processing entry point. It is intended to read uploaded CSV content, normalize fields, perform validation checks, and return results that the workflow can act on.

### `lambda/write-invalid-rows/lambda_function.py`
Handles rows rejected by validation. This function can be extended to write invalid records to a separate S3 bucket, update a reporting table, or publish an alert.

### `eventbridge/s3-event-pattern.json`
Contains an EventBridge rule pattern for S3 object creation events. This is the trigger used to start the serverless workflow whenever a CSV is uploaded.

### `iam/README.md`
Documents the IAM permissions expected for Lambda execution, S3 access, Step Functions, and downstream services.

### `iam/*.json`
Example AWS IAM policy documents describing least-privilege access for the Lambda functions, S3 buckets, DynamoDB table, SNS topic, and Step Functions execution role.

### `sample-data/customers_messy.csv`
Sample input data used to test validation logic and demonstrate how messy CSV content is cleaned and processed.

### `screenshots/s3-event-trigger-placeholder.svg`
A visual placeholder showing the S3 upload, EventBridge object-created trigger, and Lambda invocation path.

## Example Data Flow

A sample file such as `customers_messy.csv` may contain formatting issues like:

- missing values
- inconsistent casing
- malformed phone numbers
- blank email fields
- invalid postal codes

The validation pipeline can clean or reject these records according to business rules defined in the Lambda logic and Step Functions workflow.

## Deployment Notes

This repository is intended as a starter template for a serverless AWS implementation. To move it into production, you should add:

- an S3 bucket with appropriate event notifications
- IAM execution roles and policies
- DynamoDB tables for valid records
- SNS topics for invalid-row notifications or summaries
- actual deployment automation using AWS SAM, CloudFormation, or Terraform

## Security Considerations

When deploying this architecture in AWS, ensure the following:

- least-privilege IAM policies are used
- S3 buckets restrict public access
- secrets and credentials are not hardcoded
- CloudWatch logs are monitored for pipeline failures
- data validation rules are enforced before records are stored

## Suggested Next Steps

1. Replace the placeholder Lambda logic with real CSV parsing and validation rules.
2. Define the exact data model for valid and invalid records.
3. Add DynamoDB or S3 destinations for accepted records.
4. Add SNS or email notifications for failed validations.
5. Automate deployment with Infrastructure as Code.

## Summary

This repository is a practical example of a serverless CSV validation pipeline in AWS. It demonstrates a clean event-driven architecture where S3, EventBridge, Lambda, and Step Functions work together to process uploaded CSV data efficiently and predictably.

This project is designed to be expanded into a production-grade solution with real infrastructure, validator logic, and observability.
