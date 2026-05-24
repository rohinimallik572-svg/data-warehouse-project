"""
sales_aggregator.py — PySpark Aggregation Job
Demonstrates distributed processing of the sales fact table.
Runs locally using PySpark; swap master("local[*]") for a cluster in production.

Usage:
    python spark/sales_aggregator.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_spark_job():
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
        from pyspark.sql.window import Window
        SPARK_AVAILABLE = True
    except ImportError:
        SPARK_AVAILABLE = False

    if not SPARK_AVAILABLE:
        print("PySpark not installed — running pandas fallback (same logic, local only)")
        run_pandas_fallback()
        return

    spark = (
        SparkSession.builder
        .appName("RetailCo_SalesAggregator")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.memory", "1g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    print("\n🔥 Spark Session started")
    print(f"   Spark version: {spark.version}")

    fact_path = "data/processed/fact_sales.csv"
    print(f"\nReading fact_sales from {fact_path}...")
    df = spark.read.csv(fact_path, header=True, inferSchema=True)
    df.cache()
    print(f"Partitions: {df.rdd.getNumPartitions()} | Rows: {df.count():,}")

    # ── Aggregation 1: Revenue by Region & Quarter ───────────
    print("\n── Revenue by Region & Quarter ──")
    region_quarter = (
        df.groupBy("region", "year", "quarter")
        .agg(
            F.round(F.sum("net_revenue"), 0).alias("total_revenue"),
            F.round(F.avg("gross_margin_pct"), 1).alias("avg_margin_pct"),
            F.count("sale_id").alias("transactions"),
        )
        .orderBy("year", "quarter", F.desc("total_revenue"))
    )
    region_quarter.show(20, truncate=False)

    # ── Aggregation 2: Top 10 Products by Revenue ────────────
    print("\n── Top 10 Products by Revenue ──")
    dim_product_path = "data/processed/dim_product.csv"
    dim_product = spark.read.csv(dim_product_path, header=True, inferSchema=True)

    top_products = (
        df.join(dim_product.select("product_id", "product_name", "category"), "product_id")
        .groupBy("product_name", "category")
        .agg(
            F.round(F.sum("net_revenue"), 0).alias("total_revenue"),
            F.sum("quantity").alias("units_sold"),
            F.round(F.avg("gross_margin_pct"), 1).alias("avg_margin_pct"),
        )
        .orderBy(F.desc("total_revenue"))
        .limit(10)
    )
    top_products.show(truncate=False)

    # ── Aggregation 3: MoM Revenue with Window Function ──────
    print("\n── Month-over-Month Revenue Growth ──")
    monthly = (
        df.groupBy("year", "month", "month_name")
        .agg(F.round(F.sum("net_revenue"), 0).alias("monthly_revenue"))
        .orderBy("year", "month")
    )

    window_spec = Window.orderBy("year", "month")
    monthly_growth = (
        monthly
        .withColumn("prev_month_revenue", F.lag("monthly_revenue").over(window_spec))
        .withColumn(
            "mom_growth_pct",
            F.round(
                (F.col("monthly_revenue") - F.col("prev_month_revenue")) /
                F.col("prev_month_revenue") * 100, 1
            )
        )
        .select("year", "month_name", "monthly_revenue", "mom_growth_pct")
    )
    monthly_growth.show(15, truncate=False)

    # ── Aggregation 4: Customer Segment Performance ──────────
    print("\n── Revenue by Customer Segment ──")
    dim_customer_path = "data/processed/dim_customer.csv"
    dim_customer = spark.read.csv(dim_customer_path, header=True, inferSchema=True)

    segment_perf = (
        df.join(dim_customer.select("customer_id", "segment", "full_name"), "customer_id")
        .groupBy("segment")
        .agg(
            F.round(F.sum("net_revenue"), 0).alias("total_revenue"),
            F.round(F.avg("gross_margin_pct"), 1).alias("avg_margin"),
            F.countDistinct("customer_id").alias("unique_customers"),
            F.count("sale_id").alias("transactions"),
        )
        .orderBy(F.desc("total_revenue"))
    )
    segment_perf.show(truncate=False)

    # ── Write output ─────────────────────────────────────────
    output_path = "data/processed/spark_aggregations"
    region_quarter.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/region_quarter", header=True
    )
    top_products.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/top_products", header=True
    )
    print(f"\nAggregations saved → {output_path}/")

    spark.stop()
    print("Spark session closed.")


def run_pandas_fallback():
    """Same aggregations using pandas — runs without Spark installed."""
    import pandas as pd

    print("\nRunning aggregations with pandas (Spark fallback)...")
    fact = pd.read_csv("data/processed/fact_sales.csv")
    dim_product = pd.read_csv("data/processed/dim_product.csv")
    dim_customer = pd.read_csv("data/processed/dim_customer.csv")

    # Revenue by Region & Quarter
    print("\n── Revenue by Region & Quarter ──")
    rq = (
        fact.groupby(["region", "year", "quarter"])
        .agg(total_revenue=("net_revenue", "sum"),
             avg_margin=("gross_margin_pct", "mean"),
             transactions=("sale_id", "count"))
        .round(1).reset_index()
        .sort_values(["year", "quarter", "total_revenue"], ascending=[True, True, False])
    )
    print(rq.head(15).to_string(index=False))

    # Top 10 products
    print("\n── Top 10 Products by Revenue ──")
    merged = fact.merge(dim_product[["product_id", "product_name", "category"]], on="product_id")
    top = (
        merged.groupby(["product_name", "category"])
        .agg(total_revenue=("net_revenue", "sum"),
             units_sold=("quantity", "sum"),
             avg_margin=("gross_margin_pct", "mean"))
        .round(1).reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )
    print(top.to_string(index=False))

    # MoM growth
    print("\n── Month-over-Month Revenue Growth ──")
    monthly = (
        fact.groupby(["year", "month", "month_name"])
        .agg(monthly_revenue=("net_revenue", "sum"))
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["prev"] = monthly["monthly_revenue"].shift(1)
    monthly["mom_growth_pct"] = ((monthly["monthly_revenue"] - monthly["prev"]) / monthly["prev"] * 100).round(1)
    print(monthly[["year", "month_name", "monthly_revenue", "mom_growth_pct"]].to_string(index=False))

    print("\nPandas fallback complete.")


if __name__ == "__main__":
    run_spark_job()
