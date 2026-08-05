#!/usr/bin/env python3
"""
AWS Glue PySpark job: build curated silver_daily_staffing.

Reads PBJ daily nurse staffing data from S3 raw, standardizes dates and numeric
staffing fields, calculates row-level staffing metrics, and writes Parquet to
curated/silver/silver_daily_staffing/.
"""

from __future__ import annotations

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


def num(column_name: str):
    return F.coalesce(F.col(column_name).cast("double"), F.lit(0.0))


def ratio(numerator, denominator):
    return F.when(denominator > F.lit(0.0), numerator / denominator).otherwise(F.lit(None).cast("double"))


def parse_work_date():
    raw = F.trim(F.col("WorkDate").cast("string"))
    return F.coalesce(
        F.to_date(raw, "yyyyMMdd"),
        F.to_date(raw, "yyyy-MM-dd"),
        F.to_date(raw, "MM/dd/yyyy"),
    )


def main() -> None:
    args = getResolvedOptions(
        sys.argv,
        ["JOB_NAME", "raw_bucket", "staffing_raw_prefix", "curated_bucket", "curated_prefix"],
    )

    sc = SparkContext()
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    input_path = f"s3://{args['raw_bucket']}/{args['staffing_raw_prefix'].strip('/')}/"
    output_path = f"s3://{args['curated_bucket']}/{args['curated_prefix'].strip('/')}/silver/silver_daily_staffing/"

    raw = spark.read.option("header", True).csv(input_path)
    required = {"PROVNUM", "WorkDate", "MDScensus"}
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError(f"PBJ staffing source missing required columns: {missing}")

    work_date = parse_work_date()
    rn_hours = num("Hrs_RN")
    lpn_hours = num("Hrs_LPN")
    cna_hours = num("Hrs_CNA")
    rn_contract = num("Hrs_RN_ctr")
    lpn_contract = num("Hrs_LPN_ctr")
    cna_contract = num("Hrs_CNA_ctr")
    total_nurse_hours = rn_hours + lpn_hours + cna_hours
    contract_nurse_hours = rn_contract + lpn_contract + cna_contract
    mds_census = F.col("MDScensus").cast("double")

    silver = (
        raw.select(
            F.trim(F.col("PROVNUM").cast("string")).alias("provider_id"),
            work_date.alias("work_date"),
            mds_census.alias("mds_census"),
            rn_hours.alias("rn_hours"),
            lpn_hours.alias("lpn_hours"),
            cna_hours.alias("cna_hours"),
            rn_contract.alias("rn_contract_hours"),
            lpn_contract.alias("lpn_contract_hours"),
            cna_contract.alias("cna_contract_hours"),
            total_nurse_hours.alias("total_nurse_hours"),
            contract_nurse_hours.alias("contract_nurse_hours"),
            ratio(total_nurse_hours, mds_census).alias("total_nurse_hours_per_resident_day"),
            ratio(rn_hours, mds_census).alias("rn_hours_per_resident_day"),
            ratio(contract_nurse_hours, total_nurse_hours).alias("contract_staff_ratio"),
        )
        .withColumn("year", F.year("work_date"))
        .withColumn("month", F.month("work_date"))
        .withColumn("year_month", F.date_format("work_date", "yyyy-MM"))
        .where(F.col("work_date").isNotNull())
        .select(
            "provider_id",
            "work_date",
            "year",
            "month",
            "year_month",
            "mds_census",
            "rn_hours",
            "lpn_hours",
            "cna_hours",
            "rn_contract_hours",
            "lpn_contract_hours",
            "cna_contract_hours",
            "total_nurse_hours",
            "contract_nurse_hours",
            "total_nurse_hours_per_resident_day",
            "rn_hours_per_resident_day",
            "contract_staff_ratio",
        )
    )

    silver.write.mode("overwrite").parquet(output_path)
    job.commit()


if __name__ == "__main__":
    main()
