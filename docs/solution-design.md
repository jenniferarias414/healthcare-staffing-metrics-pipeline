# Solution Design

## Business Goal

Create a unified view of healthcare staffing and operational performance across facilities.

## Technical Goal

Build a simple AWS-based data pipeline that ingests source files, transforms them into curated analytics tables, calculates selected metrics, and supports a Streamlit dashboard.

## Source

The project instructions treat Google Drive as the source system. For the local project build, files are downloaded and profiled locally first, then the AWS design treats the files as incrementally ingested from Google Drive into S3.

## Storage

- Raw zone: S3 CSV files
- Curated zone: S3 Parquet files
- Query layer: Athena tables over curated data

## Transformation

PySpark will clean, type cast, join, and calculate metrics.

## Dashboard

Streamlit will be used to present staffing and facility performance insights.
