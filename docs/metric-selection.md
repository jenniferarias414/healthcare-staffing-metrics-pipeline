# Healthcare Metrics Selection

## Purpose

This document explains which healthcare metrics are calculable from the available data and which metrics are not directly supported.

The project instructions list many possible staffing, facility, quality, cost, and operational metrics. Not all of them are available in the source files, so this project focuses on 3-5 metrics that can be supported by the data.

## Selected Metrics

### 1. Total Nurse Hours per Resident Day

Business question:

How much nursing staff coverage is available relative to resident census?

Formula:

total_nurse_hours_per_resident_day = total_nurse_hours / MDScensus

Where:

total_nurse_hours = Hrs_RN + Hrs_LPN + Hrs_CNA

Why this metric is supported:

The PBJ master file contains RN, LPN, CNA hours and MDS census.

### 2. RN Hours per Resident Day

Business question:

How much Registered Nurse coverage is available relative to resident census?

Formula:

rn_hours_per_resident_day = Hrs_RN / MDScensus

Why this metric is supported:

The PBJ master file contains RN hours and MDS census.

### 3. Contract Staff Ratio

Business question:

How much of the nursing workload is covered by contracted staff?

Formula:

contract_staff_ratio = contract_nurse_hours / total_nurse_hours

Where:

contract_nurse_hours = Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr

total_nurse_hours = Hrs_RN + Hrs_LPN + Hrs_CNA

Why this metric is supported:

The PBJ master file separates employed and contracted staffing hours.

### 4. Bed Utilization / Occupancy Proxy

Business question:

How full is each facility compared to its certified bed capacity?

Formula:

bed_utilization_rate = MDScensus / number_of_certified_beds

Why this metric is supported:

The PBJ master file contains resident census. The provider information file is expected to contain certified bed count.

### 5. Staffing Comparison by State or Provider Rating

Business question:

How do staffing levels compare across states, facilities, or provider ratings?

Example calculations:

- average total nurse hours per resident day by state
- average RN hours per resident day by state
- average staffing metrics by overall rating
- average staffing metrics by staffing rating

Why this metric is supported:

The PBJ file contains staffing and state fields. Provider information can provide rating fields.

## Metrics Not Directly Supported

### Overtime Percentage

Not directly supported because the dataset provides total hours worked by staff type, but not scheduled hours or overtime-specific hours.

### Number of Shifts per Nurse

Not directly supported because the dataset is aggregated by provider and date. It does not contain individual nurse IDs or shift-level records.

### Payroll Cost

Not directly supported because the dataset contains staffing hours but not wage rates, payroll records, or cost per hour.

### Patient Satisfaction

Not directly supported unless a supporting file contains patient satisfaction fields.

### Average Length of Stay

Not directly supported from the PBJ staffing file. Supporting quality or claims files may contain related measures, but this must be validated before including it.

### Readmission Rates

Possibly supported through SNF VBP or quality measure supporting files, but it should not be promised until the relevant fields are confirmed.

## Final Metric Strategy

The project will focus on metrics that are clearly supported by the available data instead of forcing unsupported metrics.

Initial selected metric set:

1. Total nurse hours per resident day
2. RN hours per resident day
3. Contract staff ratio
4. Bed utilization / occupancy proxy
5. Staffing comparison by state or rating
