# Healthcare Staffing Metrics Pipeline - Solution Design

## Business Objective

The goal is to create a unified view of nursing home staffing and operational performance across facilities.

The system should help explain how nurse availability, staffing workload, and resident census relate to facility performance and utilization.

## Technical Objective

Build a simple AWS-based data pipeline that:

1. Ingests healthcare staffing and supporting facility files.
2. Stores raw data in Amazon S3.
3. Transforms source data using PySpark.
4. Writes curated analytics tables to S3.
5. Registers curated tables in the AWS Glue Data Catalog.
6. Supports querying through Athena.
7. Presents selected metrics in a Streamlit dashboard.

## Source Data

### Master File

`PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

This file contains daily provider-level staffing and census data.

Expected grain:

One row per provider and work date.

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

## Planned Data Model

The curated model will be simple and dashboard-focused:

1. `dim_provider`
2. `dim_date`
3. `fact_daily_staffing`
4. `mart_provider_monthly_staffing`

## Dashboard Plan

The Streamlit dashboard will include:

- Summary KPI cards
- State filter
- Provider filter
- Staffing coverage trends
- Facilities with low staffing coverage
- Contract staff ratio analysis
- Bed utilization / occupancy proxy
- Staffing comparison by state or rating

## Why This Design

This design keeps the project simple, explainable, and aligned with the AWS-only project requirement.

The project demonstrates:

- Source discovery
- File validation
- Data lake architecture
- Raw and curated zones
- PySpark transformations
- Data modeling
- Metric calculation
- Dashboarding
- Documentation
