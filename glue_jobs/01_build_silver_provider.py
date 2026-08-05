#!/usr/bin/env python3
"""
AWS Glue PySpark job: build curated silver_provider.

Reads the provider information CSV from S3 raw, standardizes provider/facility
fields, and writes Parquet to curated/silver/silver_provider/.
"""

from __future__ import annotations

import sys
import re

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    normalized = {normalize_name(c): c for c in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def normalize_name(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower().strip())).strip("_")


def col_or_default(df, column_name: str | None, default: str = ""):
    if column_name and column_name in df.columns:
        return F.trim(F.col(column_name).cast("string"))
    return F.lit(default)


def number_or_null(df, column_name: str | None):
    if column_name and column_name in df.columns:
        return F.col(column_name).cast("double")
    return F.lit(None).cast("double")


def main() -> None:
    args = getResolvedOptions(
        sys.argv,
        ["JOB_NAME", "raw_bucket", "provider_raw_prefix", "curated_bucket", "curated_prefix"],
    )

    sc = SparkContext()
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    input_path = f"s3://{args['raw_bucket']}/{args['provider_raw_prefix'].strip('/')}/"
    output_path = f"s3://{args['curated_bucket']}/{args['curated_prefix'].strip('/')}/silver/silver_provider/"

    raw = spark.read.option("header", True).option("multiLine", True).csv(input_path)
    columns = raw.columns

    id_col = first_existing(
        columns,
        ["cms_certification_number_ccn", "federal_provider_number", "provider_id", "provnum", "ccn"],
    )
    name_col = first_existing(columns, ["provider_name", "name"])
    state_col = first_existing(columns, ["state"])
    city_col = first_existing(columns, ["city", "provider_city"])
    county_col = first_existing(columns, ["county_name", "county"])
    ownership_col = first_existing(columns, ["ownership_type"])
    provider_type_col = first_existing(columns, ["provider_type"])
    beds_col = first_existing(columns, ["number_of_certified_beds", "certified_beds"])
    overall_col = first_existing(columns, ["overall_rating"])
    staffing_col = first_existing(columns, ["staffing_rating"])
    qm_col = first_existing(columns, ["qm_rating", "quality_measure_rating"])

    if not id_col:
        raise ValueError("Provider source file does not include a recognizable provider ID column.")

    silver = (
        raw.select(
            F.trim(F.col(id_col).cast("string")).alias("provider_id"),
            col_or_default(raw, name_col).alias("provider_name"),
            col_or_default(raw, state_col).alias("state"),
            col_or_default(raw, city_col).alias("city"),
            col_or_default(raw, county_col).alias("county"),
            col_or_default(raw, ownership_col).alias("ownership_type"),
            col_or_default(raw, provider_type_col).alias("provider_type"),
            number_or_null(raw, beds_col).alias("certified_bed_count"),
            number_or_null(raw, overall_col).alias("overall_rating"),
            number_or_null(raw, staffing_col).alias("staffing_rating"),
            number_or_null(raw, qm_col).alias("quality_measure_rating"),
        )
        .where(F.col("provider_id").isNotNull() & (F.col("provider_id") != ""))
        .dropDuplicates(["provider_id"])
    )

    silver.write.mode("overwrite").parquet(output_path)
    job.commit()


if __name__ == "__main__":
    main()
