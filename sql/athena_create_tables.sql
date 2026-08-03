-- Athena external table templates for the Healthcare Staffing Metrics Pipeline.
-- Replace YOUR_BUCKET with the project S3 bucket before running.

CREATE DATABASE IF NOT EXISTS healthcare_staffing;

CREATE EXTERNAL TABLE IF NOT EXISTS healthcare_staffing.gold_provider_monthly_staffing_metrics (
  provider_id string,
  year_month string,
  days_reported bigint,
  avg_daily_census double,
  total_nurse_hours double,
  total_contract_nurse_hours double,
  avg_total_nurse_hours_per_resident_day double,
  avg_rn_hours_per_resident_day double,
  avg_contract_staff_ratio double,
  provider_name string,
  state string,
  city string,
  county string,
  ownership_type string,
  provider_type string,
  certified_bed_count double,
  overall_rating double,
  staffing_rating double,
  quality_measure_rating double,
  bed_utilization_rate double
)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/curated/gold/gold_provider_monthly_staffing_metrics/';
