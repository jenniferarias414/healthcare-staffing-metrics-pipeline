# Data Lake Fundamentals Notes

## Data Lake Definition

A data lake stores data in files instead of loading everything into a traditional database first.

The data can be raw, cleaned, or ready for reporting.

In this project:

```text
S3 raw = original source files
S3 curated silver = cleaned tables
S3 curated gold = dashboard-ready metric table
```

## Data Lake Architecture and Components

This project uses a basic data lake layout:

```text
source files
→ ingestion
→ raw storage
→ cleaned silver tables
→ gold metrics table
→ SQL query layer
→ dashboard
```

Project mapping:

| Data lake part | Project service or folder |
|---|---|
| Source | Google Drive project files |
| Ingestion | Glue Python Shell job design / local downloaded files for validation |
| Raw storage | Amazon S3 raw zone |
| Transformation | Local Python script and AWS-ready Glue/PySpark job scripts |
| Curated storage | Amazon S3 curated silver/gold Parquet |
| Table metadata | Glue Data Catalog / Athena external table SQL |
| Query layer | Athena |
| Dashboard | Streamlit |

## Data Lake Principles

The main ideas I used for this project:

1. Keep raw files unchanged.
2. Separate raw data from cleaned data.
3. Create tables that match the business question.
4. Track what files were loaded.
5. Keep credentials and raw data out of GitHub.
6. Use formats and tools that support analytics.

## How a Data Lake Differs From Other Architectures

A data lake stores files first.

A traditional warehouse usually stores highly structured tables first.

For this project, S3 stores the files and Athena reads them as tables using external table definitions.

That means the data can stay in S3, while Athena provides SQL access.

## Use Cases

This project uses a data lake pattern because the source files are CSV/ZIP files and the final use case is analytics.

The same pattern works well when a team needs to:

- keep raw source files
- clean and join files later
- create reporting tables
- query data with SQL
- support dashboards

## Architecture Roadmap

The approved architecture is:

```text
AWS Glue Workflow scheduled trigger
→ AWS Glue Python Shell job for Google Drive ingestion
→ S3 raw zone
→ Glue Data Catalog raw tables
→ separate Glue/PySpark jobs for silver tables
→ Glue/PySpark job for gold metrics table
→ S3 curated Parquet
→ Glue Data Catalog curated tables
→ Athena
→ Streamlit
```

For the submitted build, I validated the flow with:

```text
local downloaded source files
→ local Python pipeline
→ S3 raw/curated uploads
→ Athena query
→ Streamlit dashboard
```

The repo also includes AWS-ready Glue job scripts that map the local logic to the approved Glue design.

## Security

Security choices for this project:

- raw source files are not committed to GitHub
- project PDFs and ZIPs stay in ignored local folders
- secrets and `.env` files are ignored
- the AWS-ready design uses IAM roles instead of hardcoded credentials
- Google Drive credentials should be stored in AWS Secrets Manager in the Glue version

## Benefits of a Data Lake

The data lake approach helped this project because:

- raw files can be preserved
- cleaned outputs can be stored separately
- Parquet files work well for analytics
- Athena can query the curated data in S3
- the dashboard can use the final gold output

## Challenges of a Data Lake

The main challenges are:

- file organization matters
- table definitions must match the files
- bad source data can flow downstream if checks are weak
- permissions and credentials must be handled carefully
- naming must stay consistent across S3, Glue, Athena, and the dashboard

## Best Practices Used

Best practices used in this repo:

- kept raw and curated zones separate
- kept local source files out of GitHub
- created a data dictionary
- documented metric logic
- kept a small final sample instead of the full dataset
- used screenshots to prove each major step
- added AWS-ready Glue job scripts to match the approved design

## Data Lake Technologies

Common data lake tools include:

- object storage such as Amazon S3
- processing tools such as AWS Glue, Spark, or PySpark
- table catalogs such as Glue Data Catalog
- query engines such as Athena
- dashboard tools such as Streamlit, QuickSight, or Power BI

This project stayed with AWS services for the architecture because the project instructions required AWS services.

## Open-Source Options

Open-source tools often used with data lakes include:

- Apache Spark
- PySpark
- Apache Iceberg
- Delta Lake
- Apache Airflow
- Trino

This project used PySpark-style Glue job scripts and Parquet outputs, but did not add Iceberg, Delta Lake, Airflow, or Trino.

## Trends and Future Direction

A stronger future version of this project could add:

- fully deployed Glue Workflow
- Google Drive API ingestion running inside Glue
- Glue job bookmarks or a stronger manifest process
- automated data quality checks
- Athena views for dashboard queries
- Streamlit reading from Athena instead of local Parquet
- CI/CD for job deployment
