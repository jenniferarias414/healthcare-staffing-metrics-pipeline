# Implementation Status

## Build Summary

This project was designed as an AWS Glue-based healthcare staffing pipeline.

The approved design uses Google Drive as the source, AWS Glue Workflow for orchestration, S3 for raw and curated storage, Glue/PySpark for table builds, Athena for SQL validation, and Streamlit for the dashboard.

For the submitted build, I validated the pipeline locally first because of the project timeline. The local build confirms the source files, transformation logic, selected metrics, silver/gold outputs, S3 layout, Athena query layer, and dashboard.

The repo also includes AWS-ready Glue job scripts that show how the local logic maps to the approved Glue Workflow design.

## What Was Built and Validated

The working local validation pipeline is in:

- `scripts/build_curated_healthcare_outputs.py`

That script reads the downloaded Google Drive source files, creates curated silver and gold outputs, writes local Parquet files, and generates sample report files in:

- `reports/final-samples/`

Validated outputs:

| Output | Purpose |
|---|---|
| `silver_provider` | Provider/facility context such as name, state, beds, ratings, ownership, and type |
| `silver_daily_staffing` | Daily PBJ staffing and census records with metric fields |
| `silver_date` | Date reference table for month, quarter, year, and trend analysis |
| `gold_provider_monthly_staffing_metrics` | Provider/month metric table used for dashboarding and Athena validation |

The curated outputs were uploaded to S3 for Athena validation.

The Streamlit dashboard was validated locally using the generated gold Parquet output.

## Approved AWS Design

The SME-approved design is:

| Step | Component | Purpose |
|---|---|---|
| 1 | AWS Glue Workflow scheduled trigger | Starts the pipeline on a schedule |
| 2 | AWS Glue Python Shell ingestion job | Checks Google Drive metadata and loads new or changed files |
| 3 | Amazon S3 raw zone | Stores original source files unchanged |
| 4 | AWS Glue Data Catalog raw tables | Registers raw table metadata |
| 5 | Separate Glue/PySpark silver jobs | Builds cleaned provider, staffing, and date tables |
| 6 | Glue/PySpark gold job | Builds the final provider/month metrics table |
| 7 | Amazon S3 curated Parquet | Stores silver and gold analytics outputs |
| 8 | AWS Glue Data Catalog curated tables | Registers curated table metadata |
| 9 | Amazon Athena | Queries the curated S3 Parquet outputs |
| 10 | Streamlit | Displays the final dashboard |

## Current Build vs Full AWS Build

The submitted build validates the core data flow and metric outputs.

Current build:

- Source files were downloaded locally from Google Drive.
- The local Python script created silver and gold outputs.
- Raw and curated outputs were uploaded to S3.
- Athena external tables were created over the S3 curated outputs.
- Athena validation queries were run against the gold table.
- Streamlit displayed the generated local gold Parquet output.
- AWS-ready Glue job scripts were added to match the approved job structure.

Full AWS build path:

- Package Google Drive client libraries for Glue.
- Store Google Drive credentials in AWS Secrets Manager.
- Configure the Glue Python Shell ingestion job with the source folder, raw S3 bucket, manifest path, and secret name.
- Configure separate Glue/PySpark jobs for each silver and gold table.
- Create the Glue Workflow and scheduled trigger.
- Add CloudWatch logs and SNS failure alerts.
- Optionally update Streamlit to query Athena instead of reading local Parquet.

## Incremental Ingestion Design

Incremental loading is handled by the ingestion job.

The Glue Workflow scheduled trigger controls when the pipeline runs.

The Glue Python Shell ingestion job controls what files are loaded.

The ingestion job design uses an S3 manifest file as the pipeline's memory. The manifest is created and updated by the pipeline.

On each run, the ingestion job:

1. Reads the current Google Drive file list and metadata.
2. Reads the existing S3 manifest.
3. Compares file ID, file name, modified time, file size, and checksum when available.
4. Loads files that are new, changed, or previously failed.
5. Skips files that have already loaded successfully and have not changed.
6. Writes new or changed files to S3 raw.
7. Updates the manifest with status, S3 path, batch ID, load time, and errors.

## How the Local Script Maps to Glue Jobs

| Local function or script area | Glue job mapping |
|---|---|
| Local source file discovery | `glue_jobs/00_ingest_google_drive_to_s3.py` |
| `build_silver_provider` | `glue_jobs/01_build_silver_provider.py` |
| `build_silver_daily_staffing` | `glue_jobs/02_build_silver_daily_staffing.py` |
| `build_silver_date` | `glue_jobs/03_build_silver_date.py` |
| `build_gold_monthly` | `glue_jobs/04_build_gold_provider_monthly_metrics.py` |
| Local Parquet/report writes | S3 curated Parquet and Athena external tables |

## Metric Calculation

The project calculates five metrics supported by the PBJ staffing file and provider information file.

| Metric | Calculation |
|---|---|
| Total nurse hours | `Hrs_RN + Hrs_LPN + Hrs_CNA` |
| Total nurse hours per resident day | `total_nurse_hours / MDScensus` |
| RN hours per resident day | `Hrs_RN / MDScensus` |
| Contract staff ratio | `(Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr) / total_nurse_hours` |
| Bed utilization rate | `avg_daily_census / certified_bed_count` |

Daily staffing metrics are created in `silver_daily_staffing`.

Provider/month totals and averages are created in `gold_provider_monthly_staffing_metrics`.

## Athena and Dashboard Connection

`sql/athena_create_tables.sql` defines Athena external tables over the curated S3 Parquet folders.

`sql/metric_validation_queries.sql` includes SQL queries for reviewing the five selected metrics.

Athena validates that the curated gold output can be queried from S3.

`streamlit_app/app.py` displays the dashboard using the generated local gold Parquet output.

## Project Requirements Met

The project required pipeline documentation, code files, SQL queries, a data dictionary, a dashboard, and an explanation of the tech stack.

This repo includes:

- source validation and profiling scripts
- local pipeline script
- AWS-ready Glue job scripts
- S3/Athena validation
- Streamlit dashboard
- metric calculation notes
- data dictionary
- tech stack rationale
- walkthrough screenshots

The main remaining work for a full AWS deployment would be configuring and running the Glue Workflow end to end.
