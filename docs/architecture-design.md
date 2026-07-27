# Architecture Design

## Proposed AWS-Only Architecture

Google Drive source files  
→ Python incremental ingestion  
→ Amazon S3 raw zone  
→ AWS Glue Data Catalog  
→ AWS Glue PySpark transformation job  
→ Amazon S3 curated zone using Parquet  
→ AWS Glue Data Catalog curated tables  
→ Amazon Athena  
→ Streamlit dashboard

## Why This Design

This design keeps the project AWS-only, simple, and explainable. S3 stores raw and curated data, Glue/PySpark handles transformation, Athena provides a SQL query layer, and Streamlit provides the dashboard.

## Scheduling

Amazon EventBridge can trigger ingestion and transformation jobs on a schedule.

## Monitoring

Amazon CloudWatch can capture job logs and failures.

## Failure Recovery

Raw files remain in S3 and can be reprocessed. Manifest files can track which files and batches were processed.

## Security

Credentials should not be committed to GitHub. S3 encryption and least-privilege IAM should be used in an AWS implementation.
