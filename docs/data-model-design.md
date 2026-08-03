# Healthcare Staffing Metrics - Data Model Design

## Purpose

This document describes the planned analytics data model for the Healthcare Staffing Metrics project.

The model is intentionally simple and dashboard-focused.

## Source Grain

The master PBJ staffing file appears to have one row per provider and work date.

Expected source grain:

PROVNUM + WorkDate

## Curated Model Overview

The curated model will include:

1. `silver_provider`
2. `silver_date`
3. `silver_daily_staffing`
4. `gold_provider_monthly_staffing_metrics`

## silver_provider

### Grain

One row per provider/facility.

### Purpose

Stores provider-level descriptive attributes.

### Example Columns

- `provider_id`
- `provider_name`
- `city`
- `state`
- `county_name`
- `ownership_type`
- `provider_type`
- `number_of_certified_beds`
- `overall_rating`
- `staffing_rating`
- `qm_rating`

### Source

Main source:

- Provider Information supporting file

Possible join key:

- PBJ `PROVNUM`
- Provider Information CCN / CMS Certification Number

## silver_date

### Grain

One row per calendar date.

### Purpose

Supports time-based reporting.

### Example Columns

- `date_id`
- `work_date`
- `year`
- `quarter`
- `month`
- `month_name`
- `week`
- `day_of_week`

### Source

Derived from distinct `WorkDate` values in the PBJ staffing file.

## silver_daily_staffing

### Grain

One row per provider and work date.

### Purpose

Stores daily staffing and census metrics.

### Example Columns

- `provider_id`
- `date_id`
- `mds_census`
- `rn_hours`
- `rn_employee_hours`
- `rn_contract_hours`
- `lpn_hours`
- `lpn_employee_hours`
- `lpn_contract_hours`
- `cna_hours`
- `cna_employee_hours`
- `cna_contract_hours`
- `total_nurse_hours`
- `employed_nurse_hours`
- `contract_nurse_hours`
- `rn_hours_per_resident_day`
- `total_nurse_hours_per_resident_day`
- `contract_staff_ratio`

### Source

Main source:

- `PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

## gold_provider_monthly_staffing_metrics

### Grain

One row per provider and month.

### Purpose

Supports dashboard reporting at a less detailed level than daily data.

### Example Columns

- `provider_id`
- `year_month`
- `state`
- `provider_name`
- `avg_mds_census`
- `total_nurse_hours`
- `avg_total_nurse_hours_per_resident_day`
- `avg_rn_hours_per_resident_day`
- `avg_contract_staff_ratio`
- `bed_utilization_rate`

## Why Include a Monthly Mart

The raw staffing file is daily and large. A monthly mart makes the Streamlit dashboard faster and easier to explain.

The dashboard can still use daily data if needed, but most business users will understand monthly trends more easily.

## Join Strategy

Primary provider join:

silver_daily_staffing.provider_id  
→ silver_provider.provider_id

Date join:

silver_daily_staffing.date_id  
→ silver_date.date_id

## Modeling Notes

This model does not try to solve every healthcare metric from the assignment list. It focuses on metrics that the available data can support.

The model can be extended later if quality, readmission, or length-of-stay fields are confirmed in supporting files.
