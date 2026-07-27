# Metric Selection

The project instructions list many possible metrics, but not all are calculable from the available data. This project will focus on 3-5 metrics that can be supported by the files.

## Planned Metrics

### 1. Total Nurse Hours per Resident Day

Formula:

total_nurse_hours / MDScensus

Where:

total_nurse_hours = Hrs_RN + Hrs_LPN + Hrs_CNA

### 2. RN Hours per Resident Day

Formula:

Hrs_RN / MDScensus

### 3. Contract Staff Ratio

Formula:

contract_nurse_hours / total_nurse_hours

Where:

contract_nurse_hours = Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr

### 4. Bed Utilization / Occupancy Proxy

Formula:

MDScensus / Number of Certified Beds

This requires joining the PBJ staffing file to provider information.

### 5. Staffing Compared to Provider Ratings

Compare staffing metrics against available provider rating or quality fields.

## Metrics Not Directly Available

The following may not be calculable unless supporting files contain the needed fields:

- Overtime percentage
- Number of shifts per nurse
- Payroll cost
- Patient satisfaction
- Length of stay
- Readmission rates
