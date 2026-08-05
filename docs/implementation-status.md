# Implementation Status

## What Was Built and Validated

The project has a working local validation pipeline in `scripts/build_curated_healthcare_outputs.py`.

That script reads locally downloaded Google Drive source files, creates curated silver and gold outputs, writes Parquet files locally, and generates sample report files in `reports/final-samples/`.

Validated local outputs:

| Output | Purpose |
|---|---|
| `silver_provider` | Provider/facility context such as name, state, beds, ratings, ownership, and type |
| `silver_daily_staffing` | Daily PBJ staffing and census facts with row-level metric fields |
| `silver_date` | Date reference table for reporting periods |
| `gold_provider_monthly_staffing_metrics` | Provider/month dashboard-ready metric table |

The curated outputs were used for sample reporting. They were also uploaded to S3 for Athena validation. The project includes Athena DDL in `sql/athena_create_tables.sql` for the silver and gold curated tables.

## What Was Architecture-Approved

The SME-approved design is:

```text
AWS Glue Workflow scheduled trigger
-> AWS Glue Python Shell job for Google Drive ingestion
-> S3 raw zone
-> Glue Data Catalog raw tables
-> separate Glue/PySpark jobs for silver tables
-> Glue/PySpark job for gold metrics table
-> S3 curated Parquet
-> Glue Data Catalog curated tables
-> Athena
-> Streamlit
```

The `glue_jobs/` folder represents this approved design as separate AWS-ready job scripts.

## What Was Not Run End to End in Glue

The full AWS Glue Workflow was not run end to end for the due-date validation unless separate Glue run screenshots are added later.

The Google Drive ingestion script is an AWS Glue Python Shell implementation template. It includes the manifest and incremental-load design. To run it in AWS, the job still needs packaged Google Drive client libraries, an AWS Secrets Manager secret, IAM permissions, and final S3/Glue job arguments.

The Streamlit app currently reads the local gold Parquet output. It can be adapted to Athena by replacing the local Parquet read with an Athena query client or a staged query result read.

## How the Local Script Maps to Glue Jobs

| Local function/script area | Glue job mapping |
|---|---|
| Local source file discovery | `00_ingest_google_drive_to_s3.py` |
| `build_silver_provider` | `01_build_silver_provider.py` |
| `build_silver_daily_staffing` | `02_build_silver_daily_staffing.py` |
| `build_silver_date` | `03_build_silver_date.py` |
| `build_gold_monthly` | `04_build_gold_provider_monthly_metrics.py` |
| Local Parquet/report writes | S3 curated Parquet plus Athena table definitions |

## Metric Calculation

The project calculates five metrics supported by the PBJ staffing file and provider information file:

| Metric | Calculation |
|---|---|
| Total nurse hours | `Hrs_RN + Hrs_LPN + Hrs_CNA` |
| Total nurse hours per resident day | `total_nurse_hours / MDScensus` |
| RN hours per resident day | `Hrs_RN / MDScensus` |
| Contract staff ratio | `(Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr) / total_nurse_hours` |
| Bed utilization / occupancy proxy | `avg_daily_census / certified_bed_count` |

The row-level staffing metrics are created in `silver_daily_staffing`. Provider/month averages and totals are created in `gold_provider_monthly_staffing_metrics`.

## Athena and Dashboard Connection

`sql/athena_create_tables.sql` defines external Athena tables over the curated S3 Parquet locations. Athena is the query layer for the approved AWS design.

`streamlit_app/app.py` demonstrates the dashboard experience using the generated local gold Parquet output. The submitted dashboard does not query Athena directly.

## Honest Summary

This repo contains a validated local implementation plus AWS-ready Glue job scripts that map the validated logic to the approved architecture. The repo should not claim that the full Glue Workflow was executed unless future evidence, logs, or screenshots are added.
