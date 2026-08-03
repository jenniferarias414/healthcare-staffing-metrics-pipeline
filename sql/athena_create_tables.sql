-- Athena external table templates for the Healthcare Staffing Metrics Pipeline.
-- Replace YOUR_BUCKET with the final project S3 bucket name before running.

CREATE DATABASE IF NOT EXISTS healthcare_staffing;

CREATE EXTERNAL TABLE IF NOT EXISTS healthcare_staffing.silver_provider (
  provider_id string,
  provider_name string,
  state string,
  city string,
  county string,
  ownership_type string,
  provider_type string,
  certified_bed_count double,
  overall_rating double,
  staffing_rating double,
  quality_measure_rating double
)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/curated/silver/silver_provider/';

CREATE EXTERNAL TABLE IF NOT EXISTS healthcare_staffing.silver_daily_staffing (
  provider_id string,
  work_date timestamp,
  year int,
  month int,
  year_month string,
  mds_census double,
  rn_hours double,
  lpn_hours double,
  cna_hours double,
  rn_contract_hours double,
  lpn_contract_hours double,
  cna_contract_hours double,
  total_nurse_hours double,
  contract_nurse_hours double,
  total_nurse_hours_per_resident_day double,
  rn_hours_per_resident_day double,
  contract_staff_ratio double
)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/curated/silver/silver_daily_staffing/';

CREATE EXTERNAL TABLE IF NOT EXISTS healthcare_staffing.silver_date (
  date timestamp,
  year int,
  month int,
  year_month string,
  quarter int,
  day_of_week string
)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/curated/silver/silver_date/';

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