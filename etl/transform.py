"""
transform.py — Data Transformation Layer
Cleans, enriches, and models raw sales data into warehouse-ready tables.
Applies business rules, handles data quality issues, builds star schema entities.
"""

import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRANSFORM] %(message)s")
logger = logging.getLogger(__name__)

UNIT_COSTS = {
    "Laptop": 800, "Monitor": 220, "Keyboard": 40, "Webcam": 60, "Headset": 100,
    "CRM License": 200, "Analytics Suite": 350, "Security Bundle": 280, "ERP Module": 700,
    "Desk Chair": 200, "Standing Desk": 350, "Whiteboard": 80, "Printer": 140,
    "Storage Plan": 80, "Compute Instance": 250, "Data Pipeline": 400, "ML Platform": 550,
}


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise mixed date formats to YYYY-MM-DD."""
    def parse_date(val):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return pd.to_datetime(val, format=fmt)
            except Exception:
                continue
        return pd.NaT

    original_nulls = df["sale_date"].isna().sum()
    df["sale_date"] = df["sale_date"].apply(parse_date)
    new_nulls = df["sale_date"].isna().sum()
    logger.info(f"Date parsing: {new_nulls - original_nulls} records could not be parsed → dropped")
    df = df.dropna(subset=["sale_date"])
    return df


def handle_missing_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Assign UNKNOWN customer segment for records with missing customer IDs."""
    missing = df["customer_id"].isna().sum()
    df["customer_id"] = df["customer_id"].fillna(0).astype(int)
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
    df["segment"] = df["segment"].fillna("Unassigned")
    logger.info(f"Missing customer IDs resolved: {missing} rows assigned to 'Unknown Customer'")
    return df


def calculate_financials(df: pd.DataFrame) -> pd.DataFrame:
    """Apply business rules to derive revenue, cost, margin."""
    df["unit_cost"] = df["product_name"].map(UNIT_COSTS).fillna(0)
    df["gross_revenue"] = df["quantity"] * df["unit_price"]
    df["discount_amount"] = df["gross_revenue"] * df["discount_pct"]
    df["net_revenue"] = (df["gross_revenue"] - df["discount_amount"]).round(2)
    df["total_cost"] = (df["quantity"] * df["unit_cost"]).round(2)
    df["gross_profit"] = (df["net_revenue"] - df["total_cost"]).round(2)
    df["gross_margin_pct"] = np.where(
        df["net_revenue"] > 0,
        (df["gross_profit"] / df["net_revenue"] * 100).round(2),
        0.0
    )
    return df


def add_date_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    """Extract date dimension attributes."""
    df["year"] = df["sale_date"].dt.year
    df["quarter"] = df["sale_date"].dt.quarter
    df["month"] = df["sale_date"].dt.month
    df["month_name"] = df["sale_date"].dt.strftime("%B")
    df["week_of_year"] = df["sale_date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["sale_date"].dt.day_name()
    df["is_weekend"] = df["sale_date"].dt.dayofweek >= 5
    return df


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Build customer dimension table."""
    dim = (
        df[["customer_id", "customer_name", "segment", "region", "country"]]
        .drop_duplicates(subset=["customer_id"])
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    dim.columns = ["customer_id", "full_name", "segment", "region", "country"]
    logger.info(f"dim_customer built: {len(dim):,} unique customers")
    return dim


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """Build product dimension table."""
    dim = (
        df[["product_name", "category", "unit_cost"]]
        .drop_duplicates(subset=["product_name"])
        .reset_index(drop=True)
    )
    dim.insert(0, "product_id", range(1, len(dim) + 1))
    dim["subcategory"] = dim["category"]  # extend with subcategory logic as needed
    logger.info(f"dim_product built: {len(dim):,} unique products")
    return dim


def build_fact_sales(df: pd.DataFrame, dim_product: pd.DataFrame) -> pd.DataFrame:
    """Build fact_sales table with foreign keys."""
    product_map = dim_product.set_index("product_name")["product_id"].to_dict()

    fact = df.copy()
    fact["product_id"] = fact["product_name"].map(product_map)
    fact["date_key"] = fact["sale_date"].dt.strftime("%Y%m%d").astype(int)

    fact = fact[[
        "sale_id", "sale_date", "date_key", "customer_id", "product_id",
        "region", "country", "quantity", "unit_price", "discount_pct",
        "gross_revenue", "net_revenue", "total_cost", "gross_profit", "gross_margin_pct",
        "year", "quarter", "month", "month_name", "week_of_year", "day_of_week", "is_weekend",
        "sales_rep", "source_system",
    ]]
    logger.info(f"fact_sales built: {len(fact):,} transactions")
    logger.info(f"Total net revenue: £{fact['net_revenue'].sum():,.0f}")
    logger.info(f"Avg gross margin: {fact['gross_margin_pct'].mean():.1f}%")
    return fact


def transform(raw_path: str = "data/raw/sales_raw.csv",
              output_dir: str = "data/processed") -> dict:
    """
    Master transform function. Reads raw CSV, applies all transformations,
    returns dict of warehouse-ready DataFrames.
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)
    logger.info(f"Loaded {len(df):,} raw rows")

    logger.info("Step 1/5: Cleaning dates...")
    df = clean_dates(df)

    logger.info("Step 2/5: Handling missing customers...")
    df = handle_missing_customers(df)

    logger.info("Step 3/5: Calculating financials...")
    df = calculate_financials(df)

    logger.info("Step 4/5: Adding date dimensions...")
    df = add_date_dimensions(df)

    logger.info("Step 5/5: Building star schema tables...")
    dim_customer = build_dim_customer(df)
    dim_product = build_dim_product(df)
    fact_sales = build_fact_sales(df, dim_product)

    tables = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "fact_sales": fact_sales,
    }

    for name, table in tables.items():
        path = os.path.join(output_dir, f"{name}.csv")
        table.to_csv(path, index=False)
        logger.info(f"Saved {name} → {path}")

    logger.info("Transformation complete.")
    return tables


if __name__ == "__main__":
    tables = transform()
    for name, df in tables.items():
        print(f"\n{name} ({len(df):,} rows):")
        print(df.head(3).to_string())
