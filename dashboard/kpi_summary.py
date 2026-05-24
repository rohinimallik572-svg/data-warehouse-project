"""
kpi_summary.py — Console KPI Dashboard
Reads from the warehouse and prints a formatted KPI report.
Outputs are structured to match Power BI / Tableau data source shapes.

Usage:
    python dashboard/kpi_summary.py
"""

import sqlite3
import pandas as pd
import os
import sys

DB_PATH = "data/warehouse.db"
DIVIDER = "═" * 62


def get_conn():
    if not os.path.exists(DB_PATH):
        print("Warehouse not found. Run:  python etl/pipeline.py  first.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def apply_views(conn):
    """Apply KPI views if not already present."""
    views_sql = open("sql/kpi_views.sql").read()
    for stmt in views_sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                conn.execute(stmt)
            except Exception:
                pass
    conn.commit()


def print_header(title: str):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def exec_summary(conn):
    print_header("EXECUTIVE SUMMARY")
    df = pd.read_sql("SELECT * FROM vw_exec_summary", conn)
    row = df.iloc[0]
    print(f"  Total Transactions     : {int(row.total_transactions):,}")
    print(f"  Unique Customers       : {int(row.unique_customers):,}")
    print(f"  Unique Products        : {int(row.unique_products):,}")
    print(f"  Total Net Revenue      : £{int(row.total_net_revenue):,}")
    print(f"  Total Gross Profit     : £{int(row.total_gross_profit):,}")
    print(f"  Avg Gross Margin       : {row.avg_gross_margin_pct:.1f}%")
    print(f"  Revenue / Customer     : £{int(row.avg_revenue_per_customer):,}")
    print(f"  Period                 : {row.first_sale_date} → {row.last_sale_date}")


def revenue_by_region(conn):
    print_header("REVENUE BY REGION (Full Year)")
    df = pd.read_sql("""
        SELECT region,
               ROUND(SUM(total_revenue), 0) AS total_revenue,
               ROUND(AVG(avg_margin_pct), 1) AS avg_margin,
               SUM(transactions) AS transactions
        FROM vw_revenue_by_region
        GROUP BY region
        ORDER BY total_revenue DESC
    """, conn)

    total = df["total_revenue"].sum()
    for _, row in df.iterrows():
        share = row.total_revenue / total * 100
        bar = "█" * int(share / 3)
        print(f"  {row.region:<20} £{int(row.total_revenue):>10,}  {share:5.1f}%  {bar}")


def top_products(conn):
    print_header("TOP 10 PRODUCTS BY REVENUE")
    df = pd.read_sql("""
        SELECT product_name, category, total_revenue, avg_margin_pct, units_sold
        FROM vw_product_performance
        ORDER BY total_revenue DESC
        LIMIT 10
    """, conn)
    for i, row in enumerate(df.itertuples(), 1):
        print(f"  {i:>2}. {row.product_name:<22} £{int(row.total_revenue):>9,}  "
              f"margin {row.avg_margin_pct:.1f}%  ({int(row.units_sold):,} units)")


def segment_analysis(conn):
    print_header("CUSTOMER SEGMENT PERFORMANCE")
    df = pd.read_sql("SELECT * FROM vw_segment_performance ORDER BY total_revenue DESC", conn)
    print(f"  {'Segment':<15} {'Revenue':>12} {'Margin':>8} {'Customers':>10} {'Rev/Cust':>10}")
    print(f"  {'-'*15} {'-'*12} {'-'*8} {'-'*10} {'-'*10}")
    for row in df.itertuples():
        print(f"  {row.segment:<15} £{int(row.total_revenue):>10,} {row.avg_margin_pct:>7.1f}% "
              f"{int(row.unique_customers):>10,} £{int(row.revenue_per_customer):>9,}")


def monthly_trend(conn):
    print_header("MONTHLY REVENUE TREND (last 12 months)")
    df = pd.read_sql("""
        SELECT month_name, year, monthly_revenue, avg_margin_pct, transactions
        FROM vw_monthly_trend
        ORDER BY year, month
        LIMIT 12
    """, conn)
    max_rev = df["monthly_revenue"].max()
    for row in df.itertuples():
        bar_len = int(row.monthly_revenue / max_rev * 30)
        bar = "▓" * bar_len
        print(f"  {row.month_name[:3]} {row.year}  £{int(row.monthly_revenue):>9,}  "
              f"{bar:<30}  {row.avg_margin_pct:.1f}%")


def sales_rep_leaderboard(conn):
    print_header("SALES REP LEADERBOARD (Top 10)")
    df = pd.read_sql("""
        SELECT sales_rep, region, total_revenue, avg_margin_pct, transactions
        FROM vw_sales_rep_performance
        LIMIT 10
    """, conn)
    print(f"  {'Rep':<10} {'Region':<20} {'Revenue':>12} {'Margin':>8} {'Txns':>6}")
    print(f"  {'-'*10} {'-'*20} {'-'*12} {'-'*8} {'-'*6}")
    for row in df.itertuples():
        print(f"  {row.sales_rep:<10} {row.region:<20} £{int(row.total_revenue):>10,} "
              f"{row.avg_margin_pct:>7.1f}% {int(row.transactions):>6,}")


def main():
    print("\n" + "=" * 62)
    print("   RetailCo Sales Analytics — KPI Dashboard")
    print("   Data Transformation & Warehousing Project")
    print("=" * 62)

    conn = get_conn()
    apply_views(conn)

    exec_summary(conn)
    revenue_by_region(conn)
    top_products(conn)
    segment_analysis(conn)
    monthly_trend(conn)
    sales_rep_leaderboard(conn)

    print(f"\n{DIVIDER}")
    print("  ✅  Dashboard complete. Warehouse: data/warehouse.db")
    print(f"{DIVIDER}\n")

    conn.close()


if __name__ == "__main__":
    main()
