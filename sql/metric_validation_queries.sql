-- Metric validation queries for the Healthcare Staffing Metrics Pipeline.
-- These queries use the gold Athena table created from the curated Parquet output.
-- The metrics are calculated in scripts/build_curated_healthcare_outputs.py.

-- 1. Total nurse hours by state and month
SELECT
  state,
  year_month,
  ROUND(SUM(total_nurse_hours), 2) AS total_nurse_hours
FROM healthcare_staffing.gold_provider_monthly_staffing_metrics
WHERE state IS NOT NULL
GROUP BY state, year_month
ORDER BY year_month, total_nurse_hours DESC;


-- 2. Total nurse hours per resident day by state
SELECT
  state,
  COUNT(DISTINCT provider_id) AS provider_count,
  ROUND(AVG(avg_total_nurse_hours_per_resident_day), 2) AS avg_total_nurse_hours_per_resident_day
FROM healthcare_staffing.gold_provider_monthly_staffing_metrics
WHERE state IS NOT NULL
GROUP BY state
ORDER BY avg_total_nurse_hours_per_resident_day DESC;


-- 3. RN hours per resident day by state
SELECT
  state,
  COUNT(DISTINCT provider_id) AS provider_count,
  ROUND(AVG(avg_rn_hours_per_resident_day), 2) AS avg_rn_hours_per_resident_day
FROM healthcare_staffing.gold_provider_monthly_staffing_metrics
WHERE state IS NOT NULL
GROUP BY state
ORDER BY avg_rn_hours_per_resident_day DESC;


-- 4. Contract staff ratio by provider
SELECT
  provider_id,
  provider_name,
  state,
  year_month,
  ROUND(avg_contract_staff_ratio, 3) AS avg_contract_staff_ratio,
  ROUND(total_contract_nurse_hours, 2) AS total_contract_nurse_hours,
  ROUND(total_nurse_hours, 2) AS total_nurse_hours
FROM healthcare_staffing.gold_provider_monthly_staffing_metrics
WHERE avg_contract_staff_ratio IS NOT NULL
ORDER BY avg_contract_staff_ratio DESC
LIMIT 25;


-- 5. Bed utilization rate by provider
SELECT
  provider_id,
  provider_name,
  state,
  year_month,
  ROUND(avg_daily_census, 2) AS avg_daily_census,
  ROUND(certified_bed_count, 2) AS certified_bed_count,
  ROUND(bed_utilization_rate, 3) AS bed_utilization_rate
FROM healthcare_staffing.gold_provider_monthly_staffing_metrics
WHERE bed_utilization_rate IS NOT NULL
ORDER BY bed_utilization_rate DESC
LIMIT 25;
