# Glue Job Scripts

This folder maps the local validation pipeline into AWS-ready Glue job scripts.

The submitted project used `scripts/build_curated_healthcare_outputs.py` for fast local validation, sample generation, and S3/Athena proof. The approved production-style architecture would run the logic as separate jobs inside an AWS Glue Workflow.

These scripts are implementation templates. They are written to show the correct Glue job boundaries and job arguments, but they should be configured with the final S3 bucket names, IAM role, Glue connections/libraries, and Google Drive credentials before a real deployment.

| Job | Glue type | Purpose | Output |
|---|---|---|---|
| `00_ingest_google_drive_to_s3.py` | Python Shell | Reads Google Drive metadata, compares it to an S3 manifest, downloads only new/changed/failed files, and writes original source files to S3 raw. | `s3://.../raw/...` plus manifest JSON |
| `01_build_silver_provider.py` | Glue/PySpark | Cleans provider identifiers and facility context from provider source files. | `curated/silver/silver_provider/` |
| `02_build_silver_daily_staffing.py` | Glue/PySpark | Cleans PBJ daily staffing data and calculates row-level staffing metrics. | `curated/silver/silver_daily_staffing/` |
| `03_build_silver_date.py` | Glue/PySpark | Builds a date reference table from staffing work dates. | `curated/silver/silver_date/` |
| `04_build_gold_provider_monthly_metrics.py` | Glue/PySpark | Aggregates provider/month metrics and joins facility context. | `curated/gold/gold_provider_monthly_staffing_metrics/` |

## Incremental Loading Design

The approved workflow starts from a scheduled Glue Workflow trigger. The ingestion job reads the current Google Drive file list and compares file ID, modified time, size, and checksum against an S3 manifest JSON. Files that are unchanged are marked `SKIPPED`. Files that are new, changed, or previously failed are downloaded again, written to S3 raw, and marked `SUCCESS` or `FAILED`.

The manifest keeps file-level state without adding DynamoDB or another database service. That keeps the first version easier to explain while still supporting incremental source loads.

## Monitoring

In the planned Glue version, CloudWatch Logs would capture job logs for the workflow and each job. SNS can be added for Glue failure notifications if alerts are needed.

## Validation Status

The local validation script was run to prove the transformation logic and output tables. Curated outputs were then available for S3/Athena validation. 
