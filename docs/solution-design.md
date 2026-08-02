# Healthcare Staffing Metrics Pipeline - Solution Design

## Business Objective

The goal is to create a unified view of nursing home staffing and operational performance across facilities.

The system should help explain how nurse availability, staffing workload, and resident census relate to facility performance and utilization.

## Technical Objective

Build a simple AWS-based data lake pipeline that:

1. Uses AWS Glue Workflow to schedule and coordinate the pipeline.
2. Runs Google Drive ingestion in a Glue Python Shell job.
3. Tracks incremental file loading with an S3 ingestion manifest.
4. Stores raw source files unchanged in Amazon S3.
5. Registers raw table metadata in the AWS Glue Data Catalog.
6. Transforms source data using separate Glue/PySpark jobs.
7. Writes curated silver and gold analytics tables to S3 as Parquet.
8. Registers curated table metadata in the AWS Glue Data Catalog.
9. Supports querying through Athena.
10. Presents selected metrics in a Streamlit dashboard.
11. Uses CloudWatch Logs and optional SNS alerts for monitoring and failure notification.

## Source Data

### Master File

`PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

This file contains daily provider-level staffing and census data.

Expected grain:

```text
one row per provider and work date
```

Expected key columns:

- `PROVNUM`
- `WorkDate`

Important metric columns:

- `MDScensus`
- `Hrs_RN`
- `Hrs_RN_emp`
- `Hrs_RN_ctr`
- `Hrs_LPN`
- `Hrs_LPN_emp`
- `Hrs_LPN_ctr`
- `Hrs_CNA`
- `Hrs_CNA_emp`
- `Hrs_CNA_ctr`

### Supporting Files

Supporting nursing home files provide provider details, ratings, quality measures, ownership, penalties, survey information, and other facility context.

Initial useful supporting file:

- `NH_ProviderInfo_Oct2024.csv`

Likely useful fields include:

- provider identifier
- provider name
- state
- certified bed count
- overall rating
- staffing rating
- quality measure rating
- ownership type
- provider type

## Ingestion Plan

The ingestion step runs as an AWS Glue Python Shell job inside an AWS Glue Workflow.

The ingestion job will:

1. Check the Google Drive source file list and metadata.
2. Compare source file metadata against an S3 ingestion manifest.
3. Load files that are new, changed, or previously failed.
4. Skip files that already loaded successfully and have not changed.
5. Write original source files to the S3 raw zone.
6. Update the S3 manifest with file status, batch ID, S3 path, and errors.

## Raw Layer

Raw files are stored unchanged in Amazon S3.

The raw layer acts as the recovery point for the pipeline. If transformation logic changes or a later job fails, the pipeline can reprocess data from the raw files instead of downloading the files again from Google Drive.

## Curated Layer

The curated layer is split into silver and gold outputs.

Silver tables are cleaned and standardized.

Gold tables are dashboard-ready and metric-focused.

## Transformation Job Plan

The transformation layer will be split into individual Glue jobs for better control and troubleshooting.

Planned jobs:

1. `job_build_silver_provider`
   - Reads provider source files from S3 raw.
   - Cleans provider identifiers, provider names, state, bed count, ratings, ownership, and facility fields.
   - Writes `silver_provider` to S3 curated/silver.

2. `job_build_silver_daily_staffing`
   - Reads PBJ daily staffing data from S3 raw.
   - Parses work dates and casts census/staffing hour fields.
   - Calculates row-level staffing measures.
   - Writes `silver_daily_staffing` to S3 curated/silver.

3. `job_build_silver_date`
   - Builds a simple date reference table from staffing work dates.
   - Writes `silver_date` to S3 curated/silver.

4. `job_build_gold_provider_monthly_metrics`
   - Reads silver provider, silver daily staffing, and silver date tables.
   - Joins datasets and calculates dashboard-ready monthly metrics.
   - Writes `gold_provider_monthly_staffing_metrics` to S3 curated/gold.

Splitting table creation into separate jobs provides better control. If one table fails, the failed job can be reviewed and rerun without rerunning the entire transformation layer.

## Planned Data Model

The curated model will be simple and dashboard-focused:

1. `silver_provider`
2. `silver_daily_staffing`
3. `silver_date`
4. `gold_provider_monthly_staffing_metrics`

## Planned Metric Logic

Initial calculated fields:

- total nurse hours
- RN hours per resident day
- total nurse hours per resident day
- contract staff ratio
- bed utilization / occupancy proxy

Initial formulas:

```text
total_nurse_hours = Hrs_RN + Hrs_LPN + Hrs_CNA
contract_nurse_hours = Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr
total_nurse_hours_per_resident_day = total_nurse_hours / MDScensus
rn_hours_per_resident_day = Hrs_RN / MDScensus
contract_staff_ratio = contract_nurse_hours / total_nurse_hours
bed_utilization_rate = MDScensus / certified_bed_count
```

## Dashboard Plan

The Streamlit dashboard will include:

- summary KPI cards
- state filter
- provider filter
- staffing coverage trends
- facilities with low staffing coverage
- contract staff ratio analysis
- bed utilization / occupancy proxy
- staffing comparison by state or rating

## Error Handling and Monitoring

CloudWatch Logs will capture Glue job logs.

SNS can be added for failure alerts if needed.

The S3 ingestion manifest will track file-level status so failed ingestion attempts can be reviewed and retried.

## Out of Scope for Initial Build

These metrics are not planned for the first build unless supporting fields are found:

- overtime percentage
- individual nurse shifts
- payroll cost
- patient satisfaction
- true length of stay

## Why This Design

This design keeps the project simple, explainable, and aligned with the AWS project requirement.

The project demonstrates:

- source discovery
- file validation
- AWS Glue Workflow orchestration
- data lake architecture
- raw, silver, and gold outputs
- incremental file tracking with an S3 manifest
- PySpark transformations
- Data Catalog metadata
- Athena querying
- data modeling
- metric calculation
- dashboarding
- documentation
