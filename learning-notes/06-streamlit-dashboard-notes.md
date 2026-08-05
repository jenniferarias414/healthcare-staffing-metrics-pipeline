# Streamlit Dashboard Notes

## Purpose

Streamlit is used to create the dashboard for the Healthcare Staffing Metrics Pipeline.

The dashboard gives a quick way to review the final gold metrics table without manually opening CSV or Parquet files.

## How the Dashboard Works

The dashboard reads this local gold Parquet output:

```text
data/curated/gold/gold_provider_monthly_staffing_metrics/part-00000.parquet
```

That file is created by:

```text
scripts/build_curated_healthcare_outputs.py
```

The dashboard does not query Athena directly in this version.

Athena was validated separately by uploading the curated Parquet output to S3 and querying the gold table from Athena.

## What the Dashboard Shows

The dashboard includes:

- provider count
- average total nurse hours per resident day
- average RN hours per resident day
- average bed utilization
- state filter
- provider name search
- staffing trend by month
- average staffing by state
- facilities with low staffing coverage
- contract staff ratio view
- gold table preview

## Why Streamlit Was Used

Streamlit is simple for a project dashboard because it can read a dataframe and quickly turn it into filters, charts, tables, and KPI cards.

It is useful here because the project focus is the data pipeline and metrics, not building a custom frontend.

## How to Run

From the repo root:

```bash
streamlit run streamlit_app/app.py
```

The app opens locally in the browser.

## How It Connects to the Pipeline

The pipeline creates the final gold metrics table.

Streamlit reads that table and displays the selected staffing and facility metrics.

The flow is:

```text
source files
→ local pipeline script
→ gold Parquet output
→ Streamlit dashboard
```

For the AWS validation path, the same gold-style output was also uploaded to S3 and queried with Athena.

## What the Screenshot Proves

The dashboard screenshot proves that:

- the gold output was created
- Streamlit can read the output
- the selected metrics can be displayed
- filters, charts, and tables are working

## Future Improvement

A future version could connect Streamlit directly to Athena.

That would make the dashboard read from the AWS query layer instead of the local Parquet file.
