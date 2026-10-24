import boto3
import csv
import io
import json
import os

s3 = boto3.client("s3")

DEFAULT_BUCKET = "csvfilebucketname"
DEFAULT_ERROR_PREFIX = "errors/"
CSV_FIELDS = [
    "customerId",
    "fullName",
    "email",
    "age",
    "country",
    "errors",
    "row_number",
]


def lambda_handler(event, context):
    # Step Functions normally passes a dictionary. Also support a
    # Lambda Invoke response containing a dictionary Payload.
    payload = event.get("Payload", event) if isinstance(event, dict) else event
    if not isinstance(payload, dict):
        raise ValueError("Expected the Lambda event to be a JSON object.")

    source_bucket = (
        payload.get("source_bucket")
        or payload.get("bucket")
        or DEFAULT_BUCKET
    )
    source_key = (
        payload.get("source_key")
        or payload.get("key")
        or "incoming/customers_messy.csv"
    )
    target_bucket = payload.get("target_bucket") or DEFAULT_BUCKET
    target_prefix = payload.get("target_prefix") or DEFAULT_ERROR_PREFIX

    # Locate the Map ResultWriter manifest or accept a direct result payload.
    map_result = (
        payload.get("map_result")
        or payload.get("result_manifest")
        or payload
    )

    manifest_bucket = source_bucket
    manifest_key = None

    if isinstance(map_result, dict):
        details = map_result.get("ResultWriterDetails")
        if isinstance(details, dict):
            manifest_bucket = details.get("Bucket") or manifest_bucket
            manifest_key = details.get("Key")

        # Support the alternate ResultFiles.S3 shape.
        if not manifest_key:
            result_files = map_result.get("ResultFiles")
            if isinstance(result_files, dict):
                s3_info = result_files.get("S3", {})
                if isinstance(s3_info, dict):
                    manifest_bucket = s3_info.get("Bucket") or manifest_bucket
                    manifest_key = s3_info.get("Key")

        # Support a direct S3 location.
        if not manifest_key and map_result.get("Bucket") and map_result.get("Key"):
            manifest_bucket = map_result["Bucket"]
            manifest_key = map_result["Key"]

    valid_rows = []
    invalid_rows = []

    def process_records(records):
        for record in records:
            if not isinstance(record, dict):
                continue

            output = record.get("Output")

            # Distributed Map output may store each child's Output as JSON text.
            if isinstance(output, str):
                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    continue

            # Also support records that are already the validator's output.
            if not isinstance(output, dict):
                output = record if "status" in record else None

            if not isinstance(output, dict):
                continue

            status = output.get("status")

            if status == "VALID":
                valid_rows.append(output)
            elif status == "INVALID":
                customer = output.get("customer") or {}
                customer = dict(customer) if isinstance(customer, dict) else {}

                errors = output.get("errors", "")
                if isinstance(errors, list):
                    errors = "; ".join(str(error) for error in errors)

                customer["errors"] = errors
                customer["row_number"] = output.get("row_index")
                invalid_rows.append(customer)

    if manifest_key:
        if manifest_key.startswith("$"):
            raise ValueError(f"Invalid unresolved manifest key: {manifest_key}")

        print(f"Reading manifest: s3://{manifest_bucket}/{manifest_key}")
        manifest = read_json(manifest_bucket, manifest_key)

        if isinstance(manifest, list):
            # The manifest file itself contains child execution records.
            process_records(manifest)

        elif isinstance(manifest, dict):
            result_files = manifest.get("ResultFiles", {})

            if isinstance(result_files, list):
                file_entries = result_files
            elif isinstance(result_files, dict):
                file_entries = []
                for status_group in ("SUCCEEDED", "FAILED", "PENDING"):
                    entries = result_files.get(status_group, [])
                    if isinstance(entries, dict):
                        entries = [entries]
                    if isinstance(entries, list):
                        file_entries.extend(entries)
            else:
                file_entries = []

            for file_info in file_entries:
                if not isinstance(file_info, dict):
                    continue

                file_key = file_info.get("Key")
                if not file_key:
                    continue

                file_bucket = file_info.get("Bucket") or manifest_bucket
                print(f"Reading result file: s3://{file_bucket}/{file_key}")
                records = read_json(file_bucket, file_key)

                if isinstance(records, dict):
                    records = [records]
                if isinstance(records, list):
                    process_records(records)
        else:
            raise ValueError(
                f"Unexpected manifest format: {type(manifest).__name__}"
            )

    else:
        # If the state machine passes result records directly, process them.
        direct_records = map_result
        if isinstance(direct_records, dict):
            direct_records = direct_records.get("records", [direct_records])
        if isinstance(direct_records, list):
            process_records(direct_records)
        else:
            raise ValueError(
                "Could not locate a ResultWriter manifest or direct result records. "
                f"Received: {json.dumps(map_result, default=str)[:1000]}"
            )

    clean_count = len(valid_rows)
    dirty_count = len(invalid_rows)
    total_rows = clean_count + dirty_count

    print(f"Processed rows: {total_rows}")
    print(f"Valid rows: {clean_count}")
    print(f"Invalid rows: {dirty_count}")

    error_key = None

    if invalid_rows:
        filename = os.path.splitext(os.path.basename(source_key))[0]
        error_key = f"{target_prefix.rstrip('/')}/{filename}_errors.csv"

        csv_buffer = io.StringIO()
        writer = csv.DictWriter(
            csv_buffer,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(invalid_rows)

        s3.put_object(
            Bucket=target_bucket,
            Key=error_key,
            Body=csv_buffer.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )
        print(
            f"Wrote {dirty_count} invalid rows to "
            f"s3://{target_bucket}/{error_key}"
        )

    if dirty_count:
        message = (
            f"Processed {total_rows} total rows. "
            f"{clean_count} clean rows written to DynamoDB. "
            f"{dirty_count} invalid rows exported to "
            f"s3://{target_bucket}/{error_key}."
        )
    else:
        message = (
            f"Processed {total_rows} total rows. "
            f"All {clean_count} rows were valid and written to DynamoDB."
        )

    return {
        "source_bucket": source_bucket,
        "source_key": source_key,
        "error_key": error_key,
        "processed_rows": total_rows,
        "clean_rows": clean_count,
        "dirty_rows": dirty_count,
        "summary_details": message,
        "message": message,
    }


def read_json(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8").strip()

    if not content:
        return []

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback for newline-delimited JSON.
        records = []
        for line in content.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records
