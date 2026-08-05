#!/usr/bin/env python3
"""
AWS Glue PySpark job: build gold_provider_monthly_staffing_metrics.

Reads curated silver tables, aggregates provider/month staffing metrics, joins
facility context, and writes the dashboard-ready Parquet table to curated/gold.
"""

from __future__ import annotations

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


def main() -> None:
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "curated_bucket", "curated_prefix"])

    sc = SparkContext()
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    curated_root = f"s3://{args['curated_bucket']}/{args['curated_prefix'].strip('/')}"
    provider_path = f"{curated_root}/silver/silver_provider/"
    daily_path = f"{curated_root}/silver/silver_daily_staffing/"
    date_path = f"{curated_root}/silver/silver_date/"
    output_path = f"{curated_root}/gold/gold_provider_monthly_staffing_metrics/"

    silver_provider = spark.read.parquet(provider_path)
    silver_daily = spark.read.parquet(daily_path)
    silver_date = spark.read.parquet(date_path).select("date", "year_month").dropDuplicates(["date"])

    daily_with_month = (
        silver_daily.drop("year_month")
        .join(silver_date, F.to_date(silver_daily["work_date"]) == silver_date["date"], how="left")
        .drop("date")
    )

    grouped = (
        daily_with_month.groupBy("provider_id", "year_month")
        .agg(
            F.countDistinct("work_date").alias("days_reported"),
            F.avg("mds_census").alias("avg_daily_census"),
            F.sum("total_nurse_hours").alias("total_nurse_hours"),
            F.sum("contract_nurse_hours").alias("total_contract_nurse_hours"),
            F.avg("total_nurse_hours_per_resident_day").alias("avg_total_nurse_hours_per_resident_day"),
            F.avg("rn_hours_per_resident_day").alias("avg_rn_hours_per_resident_day"),
            F.avg("contract_staff_ratio").alias("avg_contract_staff_ratio"),
        )
    )

    gold = (
        grouped.join(silver_provider, on="provider_id", how="left")
        .withColumn(
            "bed_utilization_rate",
            F.when(F.col("certified_bed_count") > 0, F.col("avg_daily_census") / F.col("certified_bed_count"))
            .otherwise(F.lit(None).cast("double")),
        )
        .select(
            "provider_id",
            "year_month",
            "days_reported",
            "avg_daily_census",
            "total_nurse_hours",
            "total_contract_nurse_hours",
            "avg_total_nurse_hours_per_resident_day",
            "avg_rn_hours_per_resident_day",
            "avg_contract_staff_ratio",
            "provider_name",
            "state",
            "city",
            "county",
            "ownership_type",
            "provider_type",
            "certified_bed_count",
            "overall_rating",
            "staffing_rating",
            "quality_measure_rating",
            "bed_utilization_rate",
        )
    )

    gold.write.mode("overwrite").parquet(output_path)
    job.commit()


if __name__ == "__main__":
    main()
