# AWS Serverless CSV Validation Pipeline Architecture

This diagram shows the proposed serverless flow for ingesting, validating, cleaning, and routing CSV records in AWS.

```mermaid
flowchart LR
    U[User / Data Producer] -->|Upload CSV File| S3[(Amazon S3 Bucket)]

    S3 -->|ObjectCreated event| EB[Amazon EventBridge]
    EB -->|Trigger Rule| L1[Lambda: csvfilecleaner]

    L1 -->|Read CSV + Clean + Validate| SF[AWS Step Functions]

    SF -->|Valid Records| DDB[(Amazon DynamoDB)]
    SF -->|Invalid Rows| L2[Lambda: write-invalid-rows]

    L2 -->|Store / Report / Alert| SNS[(Amazon SNS)]
    L2 -->|Log Errors + Metrics| CW[Amazon CloudWatch]

    DDB -->|Query / Dashboard / Reporting| APP[Business Applications / Analysts]
    SNS -->|Email / SMS / Notifications| NOTIF[Notifications / Ops Team]

    IAM[IAM Roles and Policies] --> L1
    IAM --> L2
    IAM --> SF
    IAM --> S3
    IAM --> DDB
    IAM --> SNS

    subgraph "AWS Serverless CSV Validation Pipeline"
        S3
        EB
        L1
        SF
        L2
        DDB
        SNS
        CW
    end
```

## Flow Description

1. A CSV file is uploaded to an Amazon S3 bucket.
2. EventBridge listens for the S3 `ObjectCreated` event.
3. The `csvfilecleaner` Lambda is triggered to inspect the file, parse row data, and perform validation and cleaning.
4. The Step Functions workflow decides whether a row or file is valid or invalid.
5. Valid records are stored in DynamoDB.
6. Invalid records are handled by the `write-invalid-rows` Lambda.
7. The invalid-row handler can log issues, push alerts, or send notifications using SNS and CloudWatch.

## Security and Operations

- IAM roles grant least-privilege access to S3, Lambda, Step Functions, DynamoDB, and SNS.
- CloudWatch provides monitoring, logging, and alerting for pipeline execution.
- SNS can be used to notify teams about rejected records or operational issues.

## Recommended Next Step

Open this diagram in a Lucidchart-compatible editor or Mermaid viewer to refine layout, labels, and styling for your presentation or documentation.
