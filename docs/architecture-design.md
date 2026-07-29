# Healthcare Staffing Metrics Pipeline - Architecture Design

## Purpose

This document defines the proposed AWS-only architecture for the Healthcare Staffing Metrics project.

The project goal is to create a unified analytics view of nursing home staffing and facility performance. The system should support staffing metrics, facility utilization metrics, selected quality/rating comparisons, and a Streamlit dashboard.

## Architecture Summary

Proposed flow:

Google Drive source files  
→ Python incremental ingestion  
→ Amazon S3 raw zone  
→ AWS Glue Data Catalog raw tables  
→ AWS Glue PySpark transformation job  
→ Amazon S3 curated zone using Parquet  
→ AWS Glue Data Catalog curated tables  
→ Amazon Athena  
→ Streamlit dashboard

## Architecture Diagram - Text Version

Google Drive Source Files  
PBJ master CSV + supporting CMS files  
↓  
Python Ingestion Script  
detect new files, validate file presence, validate schema, write manifest  
↓  
Amazon S3 Raw Zone  
raw healthcare files retained by source and batch date  
↓  
AWS Glue Data Catalog  
raw external table metadata  
↓  
AWS Glue PySpark Job  
clean, cast, join provider files, calculate metrics  
↓  
Amazon S3 Curated Zone  
curated Parquet analytics tables  
↓  
AWS Glue Data Catalog + Amazon Athena  
curated table metadata and SQL query layer  
↓  
Streamlit Dashboard  
staffing and facility performance insights

## Why This Architecture

This design follows a simple AWS data lake pattern.

### Google Drive as Source

The project instructions treat Google Drive as the source system. The ingestion process should be able to identify and process new files over time.

### Python for Ingestion

Python is used for file ingestion because it is simple, flexible, and appropriate for pulling files from Google Drive or processing downloaded files locally during development.

Python can also validate file names, schemas, file sizes, and checksums before writing data to S3.

### Amazon S3 for Raw and Curated Storage

S3 is used as the data lake storage layer.

Raw files are kept unchanged in the raw zone. Curated files are written separately after transformation. This makes the pipeline easier to audit, rerun, and explain.

### AWS Glue Data Catalog

The Glue Data Catalog stores metadata about raw and curated datasets so the files in S3 can be queried as tables.

### AWS Glue / PySpark for Transformations

PySpark is used for transformation because the dataset is large enough to justify distributed-style processing and because the project is intended to follow an AWS data lake pattern.

The Glue job will clean data, cast data types, join provider context, and calculate staffing/facility metrics.

### Parquet for Curated Outputs

Curated data will be stored as Parquet because Parquet is columnar, efficient for analytics, and commonly used in data lake pipelines.

### Athena for SQL Queries

Athena provides a serverless SQL query layer over the curated S3 data. This avoids needing Snowflake, Redshift, or another external warehouse for this project.

### Streamlit for Dashboarding

Streamlit is used to create an interactive dashboard for staffing and facility performance metrics.

## Scheduling

For a production-style AWS implementation, Amazon EventBridge can trigger ingestion and transformation jobs on a schedule.

Example schedule:

- Daily check for new Google Drive files
- Trigger ingestion when new files are available
- Run Glue transformation after successful ingestion
- Refresh curated outputs used by the dashboard

## Monitoring and Logging

CloudWatch can be used for:

- Ingestion logs
- Glue job logs
- Failure messages
- Runtime metrics

A production version could add SNS alerts for failed jobs or data quality failures.

## Failure Recovery

The design supports recovery because raw files are retained in S3.

If a transformation fails:

1. Keep the raw file in S3.
2. Review CloudWatch logs.
3. Fix the issue.
4. Rerun the Glue job for the affected batch.
5. Regenerate curated outputs.

Manifest files can track which files were processed and when.

## Data Quality Checks

Planned checks:

- Expected file presence
- File size and checksum capture
- CSV readability
- Expected column validation
- Row count checks
- Duplicate provider/date checks
- Missing value checks
- Negative or invalid numeric checks
- Join coverage checks between staffing and provider files
- Metric sanity checks

## Security

Planned security practices:

- No credentials committed to GitHub
- S3 encryption
- IAM least privilege
- Environment variables or AWS Secrets Manager for credentials
- Raw data kept out of the public repository

## Why Not Snowflake or dbt

This project is designed as an AWS-only pipeline. Snowflake and dbt were appropriate for the Walmart project because that project focused on warehouse modeling and dbt transformations.

For this Healthcare project, the design uses AWS-native services and PySpark transformations instead. This better matches the project requirement to stick to AWS services and supports a data lake style architecture.

## Simple Speaking Explanation

I chose this architecture because the project asks for an AWS-only data lake design with Google Drive as the source. The raw files land in S3 first so the original data is preserved. Glue/PySpark handles the transformation layer, which is different from the Walmart project where dbt handled transformations. Curated Parquet tables are stored back in S3, registered in the Glue Data Catalog, queried with Athena, and displayed in Streamlit.

The design is intentionally simple: raw storage, transformation, curated storage, query layer, dashboard. It is enough to show an end-to-end pipeline without over-engineering the project.
