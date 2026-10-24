# AWS Serverless CSV Validation Pipeline Architecture

This diagram shows the proposed serverless flow for ingesting, validating, cleaning, and routing CSV records in AWS.

```mermaid
flowchart LR
    U[User / Data Producer] -->|Upload CSV file| S3[(Amazon S3)]
    S3 -->|S3 ObjectCreated event| EB[Amazon EventBridge]
    EB -->|Invoke rule| L1[Lambda<br/>csvfilecleaner]
    L1 -->|Read, clean, validate rows| SF[AWS Step Functions]

    SF -->|Valid records| DDB[(Amazon DynamoDB)]
    SF -->|Invalid records| L2[Lambda<br/>write-invalid-rows]

    L2 -->|Store / alert / report| SNS[(Amazon SNS)]
    L2 -->|Logs and metrics| CW[Amazon CloudWatch]

    DDB -->|Query / dashboards / reporting| APP[Business Apps / Analysts]
    SNS -->|Email / SMS / notifications| NOTIF[Ops Team]

    IAM[IAM Roles and Policies] --> S3
    IAM --> L1
    IAM --> L2
    IAM --> SF
    IAM --> DDB
    IAM --> SNS

    classDef aws fill:#f4f7fb,stroke:#1f2937,stroke-width:1px,color:#111827;
    classDef lambda fill:#fff7da,stroke:#d97706,stroke-width:1px,color:#111827;
    classDef data fill:#ecfdf5,stroke:#10b981,stroke-width:1px,color:#111827;
    classDef notify fill:#fdf2f8,stroke:#db2777,stroke-width:1px,color:#111827;

    class S3,EB,DDB,SNS,CW,APP,NOTIF,IAM aws;
    class L1,L2 lambda;
    class SF data;
    class U notify;

    subgraph AWS["AWS Serverless CSV Validation Pipeline"]
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
4. The Step Functions workflow decides whether each row or file is valid or invalid.
5. Valid records are stored in DynamoDB.
6. Invalid records are handled by the `write-invalid-rows` Lambda.
7. The invalid-row handler can log issues, push alerts, or send notifications using SNS and CloudWatch.

## Security and Operations

- IAM roles grant least-privilege access to S3, Lambda, Step Functions, DynamoDB, and SNS.
- CloudWatch provides monitoring, logging, and alerting for pipeline execution.
- SNS can be used to notify teams about rejected records or operational issues.

## Optional Export to PNG

To render this Mermaid diagram as a PNG image for slides or documentation:

```bash
npx -y @mermaid-js/mermaid-cli -i architecture.mmd -o architecture.png -b transparent -w 2200 -H 1400
```

This keeps the AWS service styling while producing a cleaner presentation-ready image.
