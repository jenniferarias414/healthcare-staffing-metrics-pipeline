# S3 and Athena Validation

## Purpose

This phase validated the AWS data lake query layer for the Healthcare Staffing Metrics Pipeline.

The local pipeline created curated silver and gold Parquet outputs. Those outputs were uploaded to Amazon S3 and queried with Athena.

## What Was Uploaded to S3

Raw zone:

- PBJ daily nurse staffing CSV
- Nursing homes supporting ZIP

Curated zone:

- silver_provider
- silver_daily_staffing
- silver_date
- gold_provider_monthly_staffing_metrics

## Why S3 Was Used

S3 is the storage layer for the data lake.

The raw zone keeps source files unchanged. The curated zone stores cleaned and analytics-ready Parquet outputs.

## Why Parquet Was Used

Parquet is a columnar file format that works well for analytics.

It is more efficient for query tools like Athena than reading large CSV files repeatedly.

## Why Athena Was Used

Athena provides a SQL query layer over files stored in S3.

Athena does not move the data into a traditional database. Instead, it uses external table definitions to understand the file structure and query the data in place.

## What the Athena DDL Does

The SQL file defines external tables for:

- silver_provider
- silver_daily_staffing
- silver_date
- gold_provider_monthly_staffing_metrics

Each table points to a specific S3 curated folder.

## Validation Query

A validation query was run against the gold metrics table.

The query summarized staffing metrics by state, including:

- provider count
- average total nurse hours per resident day
- average RN hours per resident day
- average bed utilization

## What This Proves

This proves that the project can:

1. Store raw source files in S3.
2. Store curated analytics outputs in S3.
3. Register table definitions for the curated outputs.
4. Query the final gold metrics table with Athena.
5. Support downstream dashboard/reporting use cases.
