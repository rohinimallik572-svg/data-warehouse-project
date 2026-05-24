"""
load.py — Data Loading Layer
Loads transformed DataFrames into the warehouse (SQLite locally, PostgreSQL/BigQuery in prod).
Handles upserts, schema creation, and load validation.
"""

import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LOAD] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "data/warehouse.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create warehouse schema if not exists."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_id   INTEGER PRIMARY KEY,
            full_name     TEXT,
            segment       TEXT,
            region        TEXT,
            country       TEXT,
            loaded_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS dim_product (
            product_id    INTEGER PRIMARY KEY,
            product_name  TEXT NOT NULL,
            category      TEXT,
            subcategory   TEXT,
            unit_cost     REAL,
            loaded_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS fact_sales (
            sale_id           TEXT PRIMARY KEY,
            sale_date         TEXT,
            date_key          INTEGER,
            customer_id       INTEGER,
            product_id        INTEGER,
            region            TEXT,
            country           TEXT,
            quantity          INTEGER,
            unit_price        REAL,
            discount_pct      REAL,
            gross_revenue     REAL,
            net_revenue       REAL,
            total_cost        REAL,
            gross_profit      REAL,
            gross_margin_pct  REAL,
            year              INTEGER,
            quarter           INTEGER,
            month             INTEGER,
            month_name        TEXT,
            week_of_year      INTEGER,
            day_of_week       TEXT,
            is_weekend        INTEGER,
            sales_rep         TEXT,
            source_system     TEXT,
            loaded_at         TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS load_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name    TEXT,
            rows_loaded   INTEGER,
            loaded_at     TEXT DEFAULT (datetime('now')),
            status        TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_fact_customer  ON fact_sales(customer_id);
        CREATE INDEX IF NOT EXISTS idx_fact_product   ON fact_sales(product_id);
        CREATE INDEX IF NOT EXISTS idx_fact_date_key  ON fact_sales(date_key);
        CREATE INDEX IF NOT EXISTS idx_fact_region    ON fact_sales(region);
        CREATE INDEX IF NOT EXISTS idx_fact_year_mo   ON fact_sales(year, month);
    """)
    conn.commit()
    logger.info("Warehouse schema ready.")


def load_table(conn: sqlite3.Connection, df: pd.DataFrame,
               table_name: str, if_exists: str = "replace") -> int:
    """Load a DataFrame into the warehouse table."""
    df["loaded_at"] = datetime.utcnow().isoformat()
    df.to_sql(table_name, conn, if_exists=if_exists, index=False, method="multi", chunksize=500)
    rows = len(df)

    conn.execute(
        "INSERT INTO load_log (table_name, rows_loaded, status) VALUES (?, ?, ?)",
        (table_name, rows, "SUCCESS")
    )
    conn.commit()
    logger.info(f"Loaded {rows:,} rows → {table_name}")
    return rows


def validate_load(conn: sqlite3.Connection) -> None:
    """Run post-load validation checks."""
    checks = {
        "fact_sales row count":     "SELECT COUNT(*) FROM fact_sales",
        "dim_customer row count":   "SELECT COUNT(*) FROM dim_customer",
        "dim_product row count":    "SELECT COUNT(*) FROM fact_sales",
        "null customer_id in fact": "SELECT COUNT(*) FROM fact_sales WHERE customer_id IS NULL",
        "null product_id in fact":  "SELECT COUNT(*) FROM fact_sales WHERE product_id IS NULL",
        "total net revenue":        "SELECT ROUND(SUM(net_revenue), 0) FROM fact_sales",
        "avg gross margin %":       "SELECT ROUND(AVG(gross_margin_pct), 2) FROM fact_sales",
    }
    logger.info("--- Load Validation ---")
    for label, query in checks.items():
        result = conn.execute(query).fetchone()[0]
        logger.info(f"  {label}: {result:,}" if isinstance(result, (int, float)) else f"  {label}: {result}")


def load(tables: dict, db_path: str = DB_PATH) -> None:
    """
    Master load function. Takes dict of DataFrames and loads into warehouse.
    Load order respects FK constraints: dims first, facts last.
    """
    conn = get_connection(db_path)
    create_schema(conn)

    load_order = ["dim_customer", "dim_product", "fact_sales"]
    for table_name in load_order:
        if table_name in tables:
            load_table(conn, tables[table_name], table_name)

    validate_load(conn)
    conn.close()
    logger.info(f"All tables loaded into warehouse: {db_path}")


if __name__ == "__main__":
    from transform import transform
    tables = transform()
    load(tables)
