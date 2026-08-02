# SME Approval Request

Hi — I updated the Healthcare Metrics architecture diagram based on the feedback around ingestion, orchestration, error handling, and separating table jobs for better control.

## Updated Proposed Architecture

```text
AWS Glue Workflow scheduled trigger
→ AWS Glue Python Shell job for Google Drive ingestion
→ Amazon S3 raw zone
→ AWS Glue Data Catalog raw tables
→ Individual AWS Glue/PySpark jobs for silver tables
→ AWS Glue/PySpark job for gold metrics table
→ Amazon S3 curated Parquet tables
→ AWS Glue Data Catalog curated tables
→ Amazon Athena query layer
→ Streamlit dashboard
```

Supporting services:

- S3 ingestion manifest for lightweight file tracking
- CloudWatch Logs for Glue job logs
- SNS alerts if failure notification is needed

## Explanation

The process starts with an AWS Glue Workflow scheduled trigger.

The first Glue job is a Python Shell job for ingestion. It checks the Google Drive source files, compares file metadata against an S3 ingestion manifest, and loads only files that are new, changed, or previously failed into the S3 raw zone.

The S3 raw zone keeps the original source files unchanged so the data can be reprocessed if needed. This gives the pipeline a recovery point if a transformation fails or if the metric logic changes later.

The transformation layer is split into separate Glue/PySpark jobs for better control. Planned jobs include a provider silver table job, a daily staffing silver table job, a date/reference silver table job, and a downstream gold metrics table job for dashboard-ready outputs.

The curated tables are registered in the Glue Data Catalog, queried by Athena, and displayed in Streamlit.

CloudWatch Logs captures Glue job logs, and SNS can be added for failure alerts if needed.

## Why This Architecture

This design keeps the pipeline orchestration and job runtime consolidated in AWS Glue while still separating ingestion and transformation responsibilities.

- Glue Workflow provides the schedule and job coordination.
- Glue Python Shell handles the Google Drive ingestion logic.
- S3 raw stores the original files unchanged.
- The S3 manifest tracks file-level ingestion state.
- Separate Glue/PySpark jobs provide better control over silver/gold table creation.
- S3 curated Parquet stores analytics-ready outputs.
- Glue Data Catalog stores table metadata.
- Athena provides the SQL query layer.
- Streamlit provides the dashboard.
- CloudWatch Logs and SNS provide logging and failure notification.

## Initial Metrics

Based on the available PBJ staffing data and supporting nursing home files, I plan to calculate:

1. Total nurse hours per resident day
2. RN hours per resident day
3. Contract staff ratio
4. Bed utilization / occupancy proxy
5. Staffing comparison by state or provider rating

## Notes on Metric Scope

The project instructions list several possible metric ideas, but not all of them appear directly available from the provided files.

I am not planning to calculate overtime percentage, individual nurse shifts, payroll cost, or patient satisfaction unless the supporting files contain those fields, because the PBJ staffing file does not directly provide those details.

Approval was received to move forward with this Glue-centered design, with an additional note to segregate silver table creation into different individual jobs for better control.
