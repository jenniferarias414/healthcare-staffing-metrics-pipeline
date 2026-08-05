# Data Dictionary

This data dictionary describes the curated outputs created for the Healthcare Staffing Metrics Pipeline.

The tables are created by the local validation script:

```text
scripts/build_curated_healthcare_outputs.py
```

The same table structure is also represented in the AWS-ready Glue job scripts under:

```text
glue_jobs/
```

## Table: silver_provider

### Purpose

`silver_provider` stores cleaned facility/provider details.

This table gives context for staffing metrics, such as facility name, state, bed count, ratings, ownership, and provider type.

### Grain

One row per provider.

### Source

Supporting nursing home provider information file.

### Columns

| Column | Definition |
|---|---|
| `provider_id` | Unique provider or facility identifier. Used to join provider details to staffing records. |
| `provider_name` | Facility/provider name. |
| `state` | State where the provider is located. |
| `city` | City where the provider is located. |
| `county` | County where the provider is located. |
| `ownership_type` | Ownership category for the provider, if available. |
| `provider_type` | Provider type, if available in the source file. |
| `certified_bed_count` | Certified bed capacity for the provider. Used to estimate bed utilization. |
| `overall_rating` | Overall provider rating, if available. |
| `staffing_rating` | Staffing rating, if available. |
| `quality_measure_rating` | Quality measure rating, if available. |

## Table: silver_daily_staffing

### Purpose

`silver_daily_staffing` stores cleaned daily staffing and census records.

This table is the main staffing fact table for the project.

### Grain

One row per provider and work date.

### Source

`PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

### Columns

| Column | Definition |
|---|---|
| `provider_id` | Provider/facility identifier from the PBJ staffing file. |
| `work_date` | Date for the staffing record. |
| `year` | Calendar year from `work_date`. |
| `month` | Calendar month from `work_date`. |
| `year_month` | Month label used for monthly grouping. |
| `mds_census` | Resident census for the provider on the work date. |
| `rn_hours` | Registered Nurse hours for the provider on the work date. |
| `lpn_hours` | Licensed Practical Nurse hours for the provider on the work date. |
| `cna_hours` | Certified Nursing Assistant hours for the provider on the work date. |
| `rn_contract_hours` | Contract Registered Nurse hours for the provider on the work date. |
| `lpn_contract_hours` | Contract Licensed Practical Nurse hours for the provider on the work date. |
| `cna_contract_hours` | Contract Certified Nursing Assistant hours for the provider on the work date. |
| `total_nurse_hours` | RN + LPN + CNA hours for the provider on the work date. |
| `contract_nurse_hours` | Contract RN + contract LPN + contract CNA hours for the provider on the work date. |
| `total_nurse_hours_per_resident_day` | Total nurse hours divided by resident census for the same provider and work date. |
| `rn_hours_per_resident_day` | RN hours divided by resident census for the same provider and work date. |
| `contract_staff_ratio` | Contract nurse hours divided by total nurse hours. |

## Table: silver_date

### Purpose

`silver_date` stores date reference fields used for trend analysis.

This table supports monthly, quarterly, yearly, and day-of-week analysis.

### Grain

One row per date found in the daily staffing data.

### Source

Created from `work_date` in `silver_daily_staffing`.

### Columns

| Column | Definition |
|---|---|
| `date` | Calendar date. |
| `year` | Calendar year. |
| `month` | Calendar month. |
| `year_month` | Month label used for grouping. |
| `quarter` | Calendar quarter. |
| `day_of_week` | Name of the day of week. |

## Table: gold_provider_monthly_staffing_metrics

### Purpose

`gold_provider_monthly_staffing_metrics` is the final dashboard-ready table.

This table combines staffing metrics with provider details and rolls daily records into monthly provider-level metrics.

### Grain

One row per provider and month.

### Source

Built from:

- `silver_daily_staffing`
- `silver_provider`
- `silver_date`

### Columns

| Column | Definition |
|---|---|
| `provider_id` | Provider/facility identifier. |
| `year_month` | Month for the metric row. |
| `days_reported` | Number of staffing dates reported for the provider/month. |
| `avg_daily_census` | Average resident census for the provider/month. |
| `total_nurse_hours` | Total RN + LPN + CNA hours for the provider/month. |
| `total_contract_nurse_hours` | Total contract RN + LPN + CNA hours for the provider/month. |
| `avg_total_nurse_hours_per_resident_day` | Average total nurse hours per resident day for the provider/month. |
| `avg_rn_hours_per_resident_day` | Average RN hours per resident day for the provider/month. |
| `avg_contract_staff_ratio` | Average contract staff ratio for the provider/month. |
| `provider_name` | Facility/provider name. |
| `state` | State where the provider is located. |
| `city` | City where the provider is located. |
| `county` | County where the provider is located. |
| `ownership_type` | Ownership category for the provider, if available. |
| `provider_type` | Provider type, if available. |
| `certified_bed_count` | Certified bed capacity for the provider. |
| `overall_rating` | Overall provider rating, if available. |
| `staffing_rating` | Staffing rating, if available. |
| `quality_measure_rating` | Quality measure rating, if available. |
| `bed_utilization_rate` | Average daily census divided by certified bed count. Estimates how full the facility is using the available fields. |

## Selected Metrics

The final build uses five metrics that can be traced to available fields.

| Metric | Formula / Source |
|---|---|
| Total nurse hours | `Hrs_RN + Hrs_LPN + Hrs_CNA` |
| Total nurse hours per resident day | `total_nurse_hours / MDScensus` |
| RN hours per resident day | `Hrs_RN / MDScensus` |
| Contract staff ratio | contract nurse hours divided by total nurse hours |
| Bed utilization rate | average daily census divided by certified bed count |

## Metrics Not Included

Some suggested metrics were not included in the first build because the needed fields were not available or were not validated.

| Metric | Reason not included |
|---|---|
| Overtime | The data has worked-hour fields, but not scheduled-hour or overtime-specific fields. |
| Shifts per nurse | The data does not include nurse IDs or shift-level records. |
| Length of stay | The PBJ staffing file does not include admission and discharge dates. |
| Readmission | Readmission is not directly available from the PBJ staffing file and was not validated from supporting files for this build. |
| Payroll cost | The data does not include wage, salary, or labor cost fields. |
| Patient satisfaction | No validated patient satisfaction field was used in the first build. |
