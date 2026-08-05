# Project Intake and Architecture Plan

## Project Goal

The goal of this project is to create a healthcare staffing analytics pipeline using an AWS-only design.

## Planned Flow

Google Drive source files are treated as the source system. The approved design ingests files into S3 raw, transforms them with PySpark, stores curated Parquet files, queries them with Athena, and supports a Streamlit dashboard.

## Why Start with Source Profiling

Before building the pipeline, the source files need to be inspected for:

- File count
- Row counts
- Column names
- Missing values
- Duplicate keys
- Join keys
- Available metrics

This prevents designing metrics that the data cannot actually support.

## Initial Design Choice

The build will stay simple and explainable. The focus is on a working pipeline, clear documentation, and metrics that can be supported by the available data.
