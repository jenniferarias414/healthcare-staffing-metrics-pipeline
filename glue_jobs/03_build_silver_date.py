#!/usr/bin/env python3
"""
AWS Glue PySpark job: build curated silver_date.

Reads silver_daily_staffing, derives one row per work date, and writes Parquet
to curated/silver/silver_date/.
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
    input_path = f"{curated_root}/silver/silver_daily_staffing/"
    output_path = f"{curated_root}/silver/silver_date/"

    silver_daily = spark.read.parquet(input_path)
    silver_date = (
        silver_daily.select(F.to_date("work_date").alias("date"))
        .where(F.col("date").isNotNull())
        .dropDuplicates(["date"])
        .withColumn("year", F.year("date"))
        .withColumn("month", F.month("date"))
        .withColumn("year_month", F.date_format("date", "yyyy-MM"))
        .withColumn("quarter", F.quarter("date"))
        .withColumn("day_of_week", F.date_format("date", "EEEE"))
        .orderBy("date")
    )

    silver_date.write.mode("overwrite").parquet(output_path)
    job.commit()


if __name__ == "__main__":
    main()
