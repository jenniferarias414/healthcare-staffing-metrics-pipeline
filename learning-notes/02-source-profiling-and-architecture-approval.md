# Source Profiling and Architecture Approval Notes

## Where This Project Stands

The project completed the early setup and discovery work before moving into build planning.

Completed so far:

1. Repo created and organized.
2. Project files downloaded locally.
3. Download integrity check completed.
4. Source profiling completed.
5. Architecture diagram created and revised.
6. SME feedback incorporated.
7. Final architecture direction approved.
8. Additional SME guidance added: separate silver table jobs for better control.

## Original Project Direction

The project requirements were broad:

- Use Google Drive as the source.
- Support incremental loads.
- Use AWS resources.
- Follow a data lake-style design.
- Build a Streamlit dashboard.
- Submit a pipeline architecture diagram and explanation.
- Create a solution design document.
- Get written SME approval.

## Source Materials

Main source file:

- `PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

Supporting materials:

- Nursing home supporting data ZIP
- Nursing home data dictionary PDF
- Project instruction PDF

## Step 1 - Download Integrity

A script was created to verify local project files:

- `analysis/verify_download_integrity.py`

Outputs:

- `analysis/output/download-integrity-report.md`
- `analysis/output/download-integrity-manifest.json`

Purpose:

- Confirm the master CSV exists.
- Confirm expected columns are present.
- Confirm the supporting ZIP can open.
- Capture file size and checksum information.
- Document local source files without committing raw source data to GitHub.

## Step 2 - Source Profiling

A script was created to profile the healthcare source files:

- `analysis/profile_healthcare_sources.py`

Outputs:

- `analysis/output/source-profile-report.md`
- `analysis/output/source-profile-summary.json`

Purpose:

- Review row counts and column counts.
- Check duplicate rows and duplicate provider/date keys.
- Review missing values.
- Inspect date ranges.
- Identify useful source columns.
- Identify which metrics appear calculable from the available files.

## Why Provider, Staffing, and Date Tables

The proposed silver tables come from the source data shape and dashboard needs.

`silver_daily_staffing` is needed because the PBJ master file contains the core daily staffing and census facts.

`silver_provider` is needed because the dashboard needs provider context such as facility name, state, bed count, ratings, ownership, and provider type.

`silver_date` is useful because the staffing file is daily and date fields support month, quarter, year, and trend analysis.

A gold monthly metrics table is useful because the dashboard should not have to calculate every metric from raw daily rows every time it loads.

## Final Architecture Direction

Approved direction:

```text
AWS Glue Workflow scheduled trigger
→ AWS Glue Python Shell job for Google Drive ingestion
→ Amazon S3 raw zone
→ AWS Glue Data Catalog raw tables
→ Separate AWS Glue/PySpark jobs for silver tables
→ AWS Glue/PySpark job for gold metrics table
→ Amazon S3 curated Parquet tables
→ AWS Glue Data Catalog curated tables
→ Amazon Athena query layer
→ Streamlit dashboard
```

Supporting services:

- S3 ingestion manifest for file tracking
- CloudWatch Logs for Glue job logs
- SNS alerts if failure notification is needed
