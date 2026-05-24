"""
pipeline.py — ETL Orchestrator
Runs the full Extract → Transform → Load pipeline end-to-end.
Entry point for the project.

Usage:
    python etl/pipeline.py
    python etl/pipeline.py --rows 50000
"""

import sys
import os
import time
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import extract
from etl.transform import transform
from etl.load import load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════════╗
║       Data Transformation & Warehousing Pipeline         ║
║       RetailCo Sales Analytics — ETL v1.0                ║
╚══════════════════════════════════════════════════════════╝
"""


def run_pipeline(n_rows: int = 10_000) -> None:
    print(BANNER)
    total_start = time.time()

    # ── Stage 1: Extract ────────────────────────────────────
    logger.info("=" * 50)
    logger.info("STAGE 1 OF 3 — EXTRACT")
    logger.info("=" * 50)
    t0 = time.time()
    extract(output_path="data/raw/sales_raw.csv", n_rows=n_rows)
    logger.info(f"Extract complete in {time.time() - t0:.1f}s\n")

    # ── Stage 2: Transform ──────────────────────────────────
    logger.info("=" * 50)
    logger.info("STAGE 2 OF 3 — TRANSFORM")
    logger.info("=" * 50)
    t0 = time.time()
    tables = transform(
        raw_path="data/raw/sales_raw.csv",
        output_dir="data/processed",
    )
    logger.info(f"Transform complete in {time.time() - t0:.1f}s\n")

    # ── Stage 3: Load ───────────────────────────────────────
    logger.info("=" * 50)
    logger.info("STAGE 3 OF 3 — LOAD")
    logger.info("=" * 50)
    t0 = time.time()
    load(tables, db_path="data/warehouse.db")
    logger.info(f"Load complete in {time.time() - t0:.1f}s\n")

    # ── Summary ─────────────────────────────────────────────
    elapsed = time.time() - total_start
    fact = tables["fact_sales"]
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"  Total rows processed : {len(fact):,}")
    logger.info(f"  Total net revenue    : £{fact['net_revenue'].sum():,.0f}")
    logger.info(f"  Avg gross margin     : {fact['gross_margin_pct'].mean():.1f}%")
    logger.info(f"  Date range           : {fact['sale_date'].min()} → {fact['sale_date'].max()}")
    logger.info(f"  Regions covered      : {fact['region'].nunique()}")
    logger.info(f"  Unique products      : {fact['product_id'].nunique()}")
    logger.info(f"  Unique customers     : {fact['customer_id'].nunique()}")
    logger.info(f"  Pipeline runtime     : {elapsed:.1f}s")
    logger.info("=" * 50)
    logger.info("Pipeline finished. Warehouse ready at: data/warehouse.db")
    logger.info("Next: run  python dashboard/kpi_summary.py  to view KPIs")
    logger.info("      run  python spark/sales_aggregator.py  for Spark job")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetailCo ETL Pipeline")
    parser.add_argument("--rows", type=int, default=10_000,
                        help="Number of sales records to generate (default: 10000)")
    args = parser.parse_args()
    run_pipeline(n_rows=args.rows)
