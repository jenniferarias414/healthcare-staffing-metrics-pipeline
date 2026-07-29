# Healthcare Source Profile Report

Generated at UTC: `2026-07-29T19:52:43.641036+00:00`

## Master PBJ Staffing File

- Row count: `1325324`
- Column count: `33`
- Duplicate full rows: `0`
- Duplicate provider/date keys: `0`
- Distinct providers: `14564`
- Distinct states: `52`
- WorkDate min: `2024-04-01`
- WorkDate max: `2024-06-30`
- WorkDate parse success count: `1325324`
- WorkDate parse failure count: `0`

### Metric Readiness

- rows_with_positive_census: `1325004`
- rows_with_zero_or_missing_census: `320`
- rows_with_positive_total_nurse_hours: `1322216`
- rows_with_zero_total_nurse_hours: `3108`

### Numeric Summary

#### `MDScensus`

- min: `0.0`
- max: `742.0`
- mean: `83.4167003691173`
- zero_count: `320`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_RNDON`

- min: `0.0`
- max: `103.96`
- mean: `5.195886892563629`
- zero_count: `495886`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_RNadmin`

- min: `0.0`
- max: `275.5`
- mean: `10.262754164264738`
- zero_count: `579234`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_RN`

- min: `0.0`
- max: `915.98`
- mean: `34.80191902508368`
- zero_count: `89326`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_LPNadmin`

- min: `0.0`
- max: `281.5`
- mean: `6.712468679356896`
- zero_count: `753768`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_LPN`

- min: `0.0`
- max: `13946.25`
- mean: `66.17242316595791`
- zero_count: `32697`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_CNA`

- min: `0.0`
- max: `1758.1`
- mean: `173.79076031974068`
- zero_count: `5785`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_NAtrn`

- min: `0.0`
- max: `443.75`
- mean: `4.314155036806095`
- zero_count: `1075892`
- negative_count: `0`
- missing_count: `0`

#### `Hrs_MedAide`

- min: `0.0`
- max: `429.8`
- mean: `8.578326575237451`
- zero_count: `916991`
- negative_count: `0`
- missing_count: `0`

### Master Missing Values

| Column | Missing Count | Missing % |
|---|---:|---:|

## Supporting Files

| File | Rows | Columns | Possible Provider Key | Notes |
|---|---:|---:|---|---|
| FY_2024_SNF_VBP_Aggregate_Performance.csv | 1 | 9 | Not obvious |  |
| FY_2024_SNF_VBP_Facility_Performance.csv | 10858 | 20 | CMS Certification Number (CCN) |  |
| NH_CitationDescriptions_Oct2024.csv | 641 | 5 | Not obvious |  |
| NH_CovidVaxAverages_20241027.csv | 54 | 4 | Not obvious |  |
| NH_CovidVaxProvider_20241027.csv | 14814 | 5 | CMS Certification Number (CCN) |  |
| NH_DataCollectionIntervals_Oct2024.csv | 45 | 6 | Not obvious |  |
| NH_FireSafetyCitations_Oct2024.csv | 200003 | 24 | CMS Certification Number (CCN) |  |
| NH_HealthCitations_Oct2024.csv | 402424 | 23 | CMS Certification Number (CCN) |  |
| NH_HlthInspecCutpointsState_Oct2024.csv | 53 | 6 | Not obvious |  |
| NH_Ownership_Oct2024.csv | 145354 | 13 | CMS Certification Number (CCN) |  |
| NH_Penalties_Oct2024.csv | 28505 | 13 | CMS Certification Number (CCN) |  |
| NH_ProviderInfo_Oct2024.csv | 14814 | 103 | CMS Certification Number (CCN) |  |
| NH_QualityMsr_Claims_Oct2024.csv | 59256 | 17 | CMS Certification Number (CCN) |  |
| NH_QualityMsr_MDS_Oct2024.csv | 266652 | 23 | CMS Certification Number (CCN) |  |
| NH_StateUSAverages_Oct2024.csv | 54 | 48 | Not obvious |  |
| NH_SurveyDates_Oct2024.csv | 159723 | 5 | CMS Certification Number (CCN) |  |
| NH_SurveySummary_Oct2024.csv | 44243 | 41 | CMS Certification Number (CCN) |  |
| Skilled_Nursing_Facility_Quality_Reporting_Program_National_Data_Oct2024.csv | 24 | 7 | CMS Certification Number (CCN) |  |
| Skilled_Nursing_Facility_Quality_Reporting_Program_Provider_Data_Oct2024.csv | 711072 | 16 | CMS Certification Number (CCN) |  |
| Swing_Bed_SNF_data_Oct2024.csv | 38064 | 16 | CMS Certification Number (CCN) |  |

## Initial Modeling Notes

- The PBJ staffing file appears to be the driving source for daily staffing metrics.
- `PROVNUM` is expected to be the main provider/facility join key.
- `WorkDate` supports daily and monthly trend analysis.
- `MDScensus` can be used as the resident/patient census denominator.
- RN, LPN, and CNA hour fields can be used to calculate staffing coverage metrics.
- Supporting provider files need to be narrowed to the files that help calculate bed utilization, ratings, quality indicators, or facility context.

