# AWS CSV Validation Pipeline

At a growing technology company, data arrives from many places in many different formats. Vendor exports, customer uploads, partner submissions, and internal spreadsheets often come in as messy CSV files with missing values, inconsistent casing, malformed phone numbers, and invalid email addresses. When that data is processed without validation, it creates downstream errors, delays operations, and causes avoidable reporting problems.

This project was created to solve that problem with a simple, scalable, and cost-effective serverless architecture in AWS. The pipeline automatically receives uploaded CSV files, validates and cleans the content, routes records through a decision flow, and stores the good data while flagging bad records for follow-up.

The goal is to provide a practical reference implementation for teams that want a clean event-driven pipeline without building a large, complex system from scratch.

## Architecture Overview

<img width="543" height="972" alt="stepfunctions_graph" src="https://github.com/user-attachments/assets/fd5e58a0-1372-459e-97c5-93738f1ad471" />

## The business problem

Data quality issues are common in real-world business operations:
- missing fields
- inconsistent formatting
- incorrect or malformed values
- data arriving from multiple sources with different conventions

Without a validation layer, companies risk:
- broken reporting
- failed downstream processing
- poor customer experiences
- operational delays
- costly manual cleanup

The AWS CSV Validation Pipeline is designed to address those issues early, before bad records reach the rest of the system.

## The solution

The pipeline is built around a lightweight event-driven design:

1. A CSV file is uploaded to Amazon S3.
2. EventBridge detects the S3 object-created event.
3. A Lambda function reads the file and validates or cleans the content.
4. AWS Step Functions decides whether each record should pass or fail.
5. Valid records move to a downstream datastore such as DynamoDB.
6. Invalid records are routed to a second Lambda for reporting or handling.
7. Amazon SNS can be used to send summary notifications or alerts.

This creates a clean and maintainable pattern for processing incoming data reliably and automatically.

## AWS services used

| Service | Purpose | Location |
| --- | --- | --- |
| S3 | Input file storage for uploaded CSVs | `sample-data/` and deployment bucket |
| EventBridge | Event-driven trigger on file upload | `eventbridge/` |
| Lambda | CSV validation and invalid-row processing | `lambda/` |
| Step Functions | Workflow orchestration and routing | `step-functions/csv-cleaner-workflow.json` |
| DynamoDB | Storage for valid records | Planned infrastructure component |
| SNS | Notifications and summary alerts | Planned infrastructure component |
| IAM | Permissions for Lambdas, S3, Step Functions, and downstream services | `iam/README.md` |

## Repository structure

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
│   ├── s3-event-pattern.json
│   └── input-transformer.json
├── iam/
│   ├── README.md
│   ├── lambda-execution-policy.json
│   ├── s3-access-policy.json
│   ├── dynamodb-access-policy.json
│   ├── sns-publish-policy.json
│   └── step-functions-execution-role.json
├── sample-data/
│   ├── customers_messy.csv
│   ├── customers_clean.csv
│   └── customers_mixed.csv
└── screenshots/
    ├── s3-event-trigger-placeholder.svg
    ├── step-functions-executions.png
    ├── dynamodb-valid-records.png
    └── sns-summary.png
```

## File descriptions

### `step-functions/csv-cleaner-workflow.json`
Defines the orchestration flow for the CSV processing pipeline. The workflow starts with the CSV cleaner Lambda, then branches based on whether the output is valid or invalid.

### `lambda/csvfilecleaner/lambda_function.py`
This Lambda is the main processing entry point. It is intended to read uploaded CSV content, normalize fields, perform validation checks, and return results that the workflow can act on.

### `lambda/write-invalid-rows/lambda_function.py`
Handles rows rejected by validation. This function can be extended to write invalid records to a separate S3 bucket, update a reporting table, or publish an alert.

### `eventbridge/s3-event-pattern.json`
Contains the EventBridge rule pattern for S3 object creation events. This is the trigger used to start the serverless workflow whenever a CSV is uploaded.

### `eventbridge/input-transformer.json`
Contains a sample EventBridge input transformer configuration used to normalize or rewrite the incoming S3 event payload before it reaches downstream processing.

### `iam/README.md`
Documents the IAM permissions expected for Lambda execution, S3 access, Step Functions, and downstream services.

### `sample-data/customers_messy.csv`
Source data with formatting issues used to demonstrate validation and cleanup logic.

### `sample-data/customers_clean.csv`
A cleaned version of the sample data for validation comparisons and success-path testing.

### `sample-data/customers_mixed.csv`
A mixed-quality dataset containing a blend of valid and invalid records to test branching behavior in the pipeline.

### `screenshots/s3-event-trigger-placeholder.svg`
A visual placeholder showing the S3 upload, EventBridge object-created trigger, and Lambda invocation path.

## Why this matters

This project reflects a practical approach to handling messy data in a real-world environment. Instead of relying on manual cleanup, teams can automate the validation process and reduce the risk of poor-quality data entering operational systems.

The design is intentionally simple and understandable. It gives organizations a solid base for building a reliable data-processing workflow without needing a full enterprise-grade platform from day one.

## Sample data

The repository includes sample CSV files with different quality levels:
- `customers_messy.csv` — messy data with common format errors
- `customers_clean.csv` — cleaned version for comparison
- `customers_mixed.csv` — a mixed dataset to simulate real-world quality variation

These files make it easy to test the validation pipeline and demonstrate how the architecture behaves under realistic conditions.

## Deployment notes

This repository is intended as a starter template for a serverless AWS implementation. To move it into production, you should add:
- an S3 bucket with appropriate event notifications
- IAM execution roles and policies
- DynamoDB tables for valid records
- SNS topics for invalid-row notifications or summaries
- deployment automation with AWS SAM, CloudFormation, or Terraform

## Security considerations

When deploying this architecture in AWS, ensure the following:
- least-privilege IAM policies are used
- S3 buckets restrict public access
- secrets and credentials are not hardcoded
- CloudWatch logs are monitored for pipeline failures
- data validation rules are enforced before records are stored

## Summary

The AWS CSV Validation Pipeline provides a simple, scalable, and practical way to handle messy CSV data in the cloud. It is built to help teams automate validation, reduce manual effort, and improve the quality of the data flowing into their systems.

This project is designed to be expanded into a production-grade solution with real infrastructure, validator logic, and observability.
