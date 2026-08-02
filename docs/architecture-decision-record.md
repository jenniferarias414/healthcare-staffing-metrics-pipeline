# Architecture Decision Record

## Decision

Use an AWS Glue-centered pipeline design for the Healthcare Staffing Metrics project.

Final proposed flow:

```text
AWS Glue Workflow scheduled trigger
→ AWS Glue Python Shell job for Google Drive ingestion
→ Amazon S3 raw zone
→ AWS Glue Data Catalog raw tables
→ Individual AWS Glue PySpark jobs for silver tables
→ AWS Glue PySpark job for gold/dashboard metrics
→ Amazon S3 curated Parquet tables
→ AWS Glue Data Catalog curated tables
→ Amazon Athena query layer
→ Streamlit dashboard
```

Supporting services:

- S3 ingestion manifest for lightweight file tracking
- CloudWatch Logs for Glue job logs
- SNS alerts if failure notifications are needed

## Context

The project requirements are broad:

- Google Drive is treated as the source.
- The pipeline should support incremental loads.
- The pipeline should use AWS resources.
- The design should follow data lake concepts.
- The output should support a Streamlit dashboard.

## Options Considered

### Option 1: EventBridge, Lambda, DynamoDB, and Glue

Initial idea:

```text
EventBridge scheduled trigger
→ Lambda Python ingestion
→ Google Drive source files
→ S3 raw zone
→ DynamoDB ingestion manifest
→ Glue PySpark transformations
→ S3 curated Parquet
→ Glue Data Catalog
→ Athena
→ Streamlit
```

This option made the ingestion runtime explicit and used a tracking table for file state.

Tradeoffs:

- More AWS services to configure and explain.
- More handoffs between services.
- More complex orchestration for a project-sized pipeline.
- Lambda may be cost-effective for small checks, but it adds another runtime outside Glue.

### Option 2: Glue Workflow with Separate Glue Jobs

Selected idea:

```text
Glue Workflow scheduled trigger
→ Glue Python Shell ingestion job
→ S3 raw zone
→ separate Glue PySpark silver table jobs
→ Glue PySpark gold metrics job
→ S3 curated Parquet
→ Glue Data Catalog
→ Athena
→ Streamlit
```

This option keeps orchestration and job runtime consolidated in AWS Glue.

## Rationale

The selected design is simpler for this project because:

- AWS Glue Workflow can coordinate the ingestion and transformation jobs.
- Glue Python Shell can run the Python ingestion logic.
- Separate Glue PySpark jobs give better control over individual silver/gold tables.
- S3 raw preserves the original files unchanged.
- S3 curated Parquet provides analytics-ready outputs.
- Glue Data Catalog and Athena support SQL querying over S3.
- CloudWatch Logs and SNS support basic monitoring and failure notification.
- An S3 manifest keeps incremental tracking lightweight.

## Notes

This project is designed as a first working version.

A Lambda and DynamoDB approach could still be reasonable in a different context, especially if a team already standardizes on that pattern or needs more explicit event-driven ingestion and state tracking.

For this project, the Glue-centered design keeps the architecture easier to explain, operate, and build.
