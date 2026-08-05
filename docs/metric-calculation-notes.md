# Metric Calculation Notes

## Purpose

This project focuses on staffing metrics that can be calculated from the available PBJ daily staffing file and provider information file.

The goal is to choose metrics that are supported by source columns and useful in the Streamlit dashboard.

## Selected Metrics

### 1. Total Nurse Hours

Formula:

```text
total_nurse_hours = Hrs_RN + Hrs_LPN + Hrs_CNA
```

Source columns:

- `Hrs_RN`
- `Hrs_LPN`
- `Hrs_CNA`

Why it is useful:

Each PBJ row includes a provider and work date. This metric adds RN, LPN, and CNA hours for that facility/date row.

The gold table later groups the daily rows by provider and month.

### 2. Total Nurse Hours per Resident Day

Formula:

```text
total_nurse_hours_per_resident_day = total_nurse_hours / MDScensus
```

Source columns:

- `Hrs_RN`
- `Hrs_LPN`
- `Hrs_CNA`
- `MDScensus`

Why it is useful:

A resident day means one resident present for one day. `WorkDate` gives the day. `MDScensus` gives the resident count for that facility/date row.

This metric divides total nurse hours by `MDScensus`. It shows staffing coverage compared with the number of residents present that day.

### 3. RN Hours per Resident Day

Formula:

```text
rn_hours_per_resident_day = Hrs_RN / MDScensus
```

Source columns:

- `Hrs_RN`
- `MDScensus`

Why it is useful:

A resident day means one resident present for one day. This metric divides RN hours by `MDScensus` for the same facility/date row.

### 4. Contract Staff Ratio

Formula:

```text
contract_nurse_hours = Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr
contract_staff_ratio = contract_nurse_hours / total_nurse_hours
```

Source columns:

- `Hrs_RN_ctr`
- `Hrs_LPN_ctr`
- `Hrs_CNA_ctr`
- `Hrs_RN`
- `Hrs_LPN`
- `Hrs_CNA`

Why it is useful:

This shows what share of reported nurse hours came from contracted staff.

### 5. Bed Utilization / Occupancy Proxy

Formula:

```text
bed_utilization_rate = avg_daily_census / certified_bed_count
```

Source columns:

- `MDScensus` from the PBJ daily staffing file
- certified bed count from the provider information file

Why it is useful:

This estimates how full a facility is using the available fields. It divides average daily census by certified bed count.

## Where Metrics Are Calculated

`silver_daily_staffing` calculates:

- `total_nurse_hours`
- `contract_nurse_hours`
- `total_nurse_hours_per_resident_day`
- `rn_hours_per_resident_day`
- `contract_staff_ratio`

`gold_provider_monthly_staffing_metrics` calculates provider/month aggregations:

- `total_nurse_hours`
- `total_contract_nurse_hours`
- `avg_total_nurse_hours_per_resident_day`
- `avg_rn_hours_per_resident_day`
- `avg_contract_staff_ratio`
- `bed_utilization_rate`

## Metrics Not Included

### Overtime

Overtime is not included because there are worked-hour fields but no scheduled-hour or overtime-specific fields.

### Shifts per Nurse

Shifts per nurse is not included because there are no nurse IDs or shift-level records.

### Length of Stay

Length of stay is not included because there are no admission/discharge dates or validated ALOS field in the first build.

### Readmission

Readmission is not included because it is not directly available from the PBJ staffing file and was not validated from supporting files for the first build.

### Payroll Cost

Payroll cost is not included because there are no wage, salary, or cost fields.

### Patient Satisfaction

Patient satisfaction is not included because no validated satisfaction field was used in the first build.

## Final Metric Strategy

The final metric set uses calculations that can be traced to available source columns. I did not force metrics that the current data does not support.
