# Healthcare Staffing Metrics Pipeline

## Project Overview

This project builds an AWS-based healthcare staffing analytics pipeline for nursing home staffing and facility performance data.

The goal is to ingest healthcare staffing files, validate the source data, transform the data into analytics-ready tables, calculate staffing and facility metrics, and present the results in a Streamlit dashboard.

## Planned Architecture

Google Drive source files  
→ Python incremental ingestion  
→ Amazon S3 raw zone  
→ AWS Glue / PySpark transformations  
→ Amazon S3 curated zone  
→ AWS Glue Data Catalog  
→ Amazon Athena query layer  
→ Streamlit dashboard

## Initial Metrics

Planned calculable metrics based on available data:

1. Total nurse hours per resident day
2. RN hours per resident day
3. Contract staff ratio
4. Bed utilization / occupancy proxy
5. Staffing level comparison against provider ratings or quality indicators

## Project Status

Current phase: Source discovery, profiling, and architecture design for SME approval.

## Repository Structure

- `analysis/` - source profiling scripts and outputs
- `scripts/` - ingestion, transformation, and metric scripts
- `docs/` - architecture, solution design, data model, and metric documentation
- `streamlit_app/` - dashboard application
- `sql/` - Athena SQL or table creation scripts
- `learning-notes/` - public project learning notes
- `screenshots/` - walkthrough screenshots
- `reports/final-samples/` - selected final report/dashboard samples
