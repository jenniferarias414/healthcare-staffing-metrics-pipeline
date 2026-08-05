# Tech Stack Rationale

This document explains why each technology was selected for the Healthcare Staffing Metrics Pipeline.

The approved design uses AWS services for ingestion, storage, transformation, cataloging, querying, and dashboard support. The submitted build also includes a local validation script to prove the data logic before mapping the work into AWS Glue job scripts.

## Google Drive

Google Drive was used because the project source files were provided there.

The project treats Google Drive as the source system. The AWS-ready design includes a Glue Python Shell ingestion job that would connect to Google Drive, check file metadata, and load new or changed files into S3.

For the submitted build, the Google Drive files were downloaded locally first so the source data, metric logic, and outputs could be validated quickly.

## AWS Glue Workflow

AWS Glue Workflow was selected for the approved pipeline design because the project needed a scheduled AWS pipeline.

The workflow gives one place to coordinate everything: the ingestion job, the silver table jobs, and the gold metrics job.

This also matches the SME feedback to keep the pipeline under eGlue and split table creation into separate jobs for better control.

## AWS Glue Python Shell

Glue Python Shell was selected for the ingestion job because the ingestion step is mostly Python API and file movement logic.

The job needs to check Google Drive file metadata, compare it against an S3 manifest, download new or changed files, and write the original files to S3 raw.

This step does not need Spark because it is not joining or transforming a large dataset. It is checking files and moving them.

Lambda could also support this type of ingestion in a different design. For this project, Glue Python Shell keeps ingestion inside the same Glue Workflow as the downstream Glue/PySpark transformation jobs. That matches the SME feedback to keep orchestration under Glue.

## AWS Glue / PySpark Jobs

Glue/PySpark jobs were selected for the transformation layer.

The project data includes a large PBJ staffing file and supporting provider files. PySpark is a good fit for cleaning, joining, casting, and calculating metrics when the same logic needs to run in AWS.

The approved design splits the work into separate jobs:

- build silver provider table
- build silver daily staffing table
- build silver date table
- build gold provider monthly metrics table

This makes the pipeline easier to troubleshoot. If one table fails, that job can be fixed and rerun without rerunning everything.

## Amazon S3

S3 was selected as the data lake storage layer.

The raw zone stores the original source files. The curated zone stores cleaned silver and gold outputs.

This separation makes the project easier to explain and easier to recover. If transformation logic changes, the raw files are still available for reprocessing.

## Raw, Silver, and Gold Layers

The project uses a simple medallion-style layout.

Raw stores original files.

Silver stores cleaned and standardized tables.

Gold stores the final dashboard-ready metrics table.

This structure keeps the pipeline organized and makes it clear which tables are source-like, cleaned, or ready for reporting.

## Parquet

Parquet was selected for curated outputs.

The final silver and gold tables are analytics outputs, not raw source files. Parquet was selected because it is column-based and supports efficient queries in Athena.

## S3 Ingestion Manifest

The S3 manifest was selected for incremental file tracking.

The manifest is a JSON file created and updated by the ingestion job.

The manifest acts as the pipeline's memory. It stores details like source file ID, file name, modified time, file size, checksum, S3 raw path, batch ID, processing status, loaded time, and error message.

On each run, the ingestion job reads Google Drive metadata and compares it to the manifest. New, changed, or previously failed files are loaded to S3 raw. Unchanged files are skipped.

This keeps incremental loading simple for the first version.

## AWS Glue Data Catalog

The Glue Data Catalog was selected as the table metadata layer.

The data stays in S3. The catalog stores table names, column names, data types, file format, and S3 locations.

Athena uses that metadata to query the curated Parquet files in S3.

In the submitted build, the Athena `CREATE EXTERNAL TABLE` SQL created those table definitions for the curated outputs.

## Amazon Athena

Athena was selected as the SQL query layer.

Athena can query files stored in S3 without loading the data into a traditional database first.

This fits the project because the curated output is stored as Parquet in S3 and needs to be queried for validation and reporting.

## Streamlit

Streamlit was selected for the dashboard.

The project required an interactive dashboard. Streamlit made it possible to build a simple dashboard with filters, KPI cards, charts, and tables using Python.

In the submitted build, Streamlit reads the generated local gold Parquet output. Athena was validated separately by querying the gold table from S3.

## CloudWatch Logs

CloudWatch Logs is included in the approved design for job logging.

In a full Glue deployment, CloudWatch would capture logs from the ingestion and transformation jobs. That would help troubleshoot failed jobs, missing files, bad data, or transformation errors.

CloudWatch was planned as the logging layer. It was not fully validated in the submitted build.

## SNS Alerts

SNS is included in the approved design for failure notification.

In a full Glue deployment, SNS could send an alert if an ingestion or transformation job fails.

SNS was planned as the notification layer. It was not fully validated in the submitted build.

## Local Python Validation Script

The local validation script was used to prove the pipeline logic quickly.

Script:

- `scripts/build_curated_healthcare_outputs.py`

This script reads the downloaded source files, creates silver and gold outputs, calculates the selected metrics, and writes small sample reports.

The local script helped confirm that the data and metric logic worked before mapping the same logic into separate AWS Glue job scripts.

## SQL Files

The SQL files support the Athena layer.

- `sql/athena_create_tables.sql` defines Athena external tables over the curated S3 folders.
- `sql/metric_validation_queries.sql` provides SQL queries for reviewing the selected metrics.

The Python script calculates the metrics. The SQL files define and validate the query layer.

## Python Libraries

The project uses Python libraries for local validation and dashboarding.

- `pandas` is used to read source files, clean columns, calculate metrics, and write sample outputs.
- `pathlib` is used to handle local file paths.
- `plotly` is used for dashboard charts.
- `streamlit` is used to build and run the dashboard.
- `boto3` is used in AWS-ready scripts for S3 and Secrets Manager access.
- `googleapiclient` is used in the AWS-ready ingestion script design to connect to Google Drive and download files.

These libraries support the project code, but the main architecture decisions are still the AWS services and data lake layout.

## Final Position

The submitted build validates the data, metric logic, S3 layout, Athena query layer, and Streamlit dashboard.

The repo also includes AWS-ready Glue job scripts that show how the local validation logic maps to the approved Glue Workflow design.
