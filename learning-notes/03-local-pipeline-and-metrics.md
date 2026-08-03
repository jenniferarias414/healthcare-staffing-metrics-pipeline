# Local Pipeline and Metrics Build

## Purpose

This section builds the first working version of the healthcare staffing pipeline locally before deploying the same pattern to AWS.

The local script represents the transformation logic that will later map to Glue jobs.

## What the Script Builds

The script creates four curated outputs:

1. `silver_provider`
2. `silver_daily_staffing`
3. `silver_date`
4. `gold_provider_monthly_staffing_metrics`

## Why These Outputs

`silver_provider` gives facility context such as provider name, state, bed count, ratings, ownership, and provider type.

`silver_daily_staffing` gives daily staffing and census facts from the PBJ master file.

`silver_date` supports month, quarter, year, and trend analysis.

`gold_provider_monthly_staffing_metrics` is the dashboard-ready table that joins the useful silver tables and calculates metrics.

## Metrics Created

Initial metrics:

- total nurse hours
- RN hours per resident day
- total nurse hours per resident day
- contract staff ratio
- bed utilization / occupancy proxy

## Important Note

The project instructions list many possible metrics, but the available source data does not support all of them.

The first build focuses on metrics that can be calculated from the available staffing, census, and provider/facility data.
