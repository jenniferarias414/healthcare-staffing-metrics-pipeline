# SME Approval Request

Hi — I’m starting the Healthcare Metrics project and wanted to get SME approval on the proposed AWS-only architecture before I move into the build phase.

## Proposed Architecture

Google Drive source files  
→ Python incremental ingestion  
→ Amazon S3 raw zone  
→ AWS Glue Data Catalog  
→ AWS Glue / PySpark transformations  
→ Amazon S3 curated Parquet tables  
→ AWS Glue Data Catalog curated tables  
→ Amazon Athena query layer  
→ Streamlit dashboard

## Why This Architecture

I’m using an AWS data lake pattern because the project instructions say to treat Google Drive as the source, ingest incrementally, and stick to AWS services only.

This keeps the design simple and explainable:

- S3 stores raw and curated data.
- Python handles ingestion and file validation.
- Glue/PySpark handles transformations and metric calculations.
- Glue Data Catalog registers table metadata.
- Athena provides a SQL query layer.
- Streamlit provides the dashboard.

## Initial Metrics

Based on the available PBJ staffing data and supporting nursing home files, I plan to calculate:

1. Total nurse hours per resident day
2. RN hours per resident day
3. Contract staff ratio
4. Bed utilization / occupancy proxy
5. Staffing comparison by state or provider rating

## Notes on Metric Scope

The project instructions list many possible metrics, but also state that not all may be calculable from the available data.

I am not planning to calculate overtime percentage, individual nurse shifts, payroll cost, or patient satisfaction unless the supporting files contain those fields, because the PBJ staffing file does not directly provide those details.

Please let me know if this architecture and metric selection are approved before I move forward with the build.
