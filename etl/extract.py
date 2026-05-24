"""
extract.py — Data Extraction Layer
Simulates pulling raw sales data from a source system (CSV / API / Kafka stream).
In production: replace generate_raw_data() with your real source connector.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EXTRACT] %(message)s")
logger = logging.getLogger(__name__)

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
SEGMENTS = ["Enterprise", "SMB", "Consumer"]
CATEGORIES = {
    "Electronics":    ["Laptop", "Monitor", "Keyboard", "Webcam", "Headset"],
    "Software":       ["CRM License", "Analytics Suite", "Security Bundle", "ERP Module"],
    "Office":         ["Desk Chair", "Standing Desk", "Whiteboard", "Printer"],
    "Cloud Services": ["Storage Plan", "Compute Instance", "Data Pipeline", "ML Platform"],
}
CUSTOMER_NAMES = [
    "Acme Corp", "TechNova Ltd", "BlueSky Inc", "Meridian Group", "Apex Solutions",
    "Horizon Ventures", "Pinnacle Co", "Vertex Systems", "Summit Enterprises", "Crest Global",
    "Atlas Holdings", "Nexus Partners", "Zenith Industries", "Orbit Technologies", "Nova Dynamics",
]


def generate_raw_data(n_rows: int = 10_000, seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic raw sales transaction data.
    Simulates what you'd receive from a Kafka stream or source DB extract.
    """
    np.random.seed(seed)
    random.seed(seed)

    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=int(d)) for d in np.random.randint(0, 365, n_rows)]

    categories = list(CATEGORIES.keys())
    cat_choices = np.random.choice(categories, n_rows)
    product_choices = [random.choice(CATEGORIES[c]) for c in cat_choices]

    unit_prices = {
        "Laptop": 1200, "Monitor": 350, "Keyboard": 80, "Webcam": 120, "Headset": 200,
        "CRM License": 500, "Analytics Suite": 800, "Security Bundle": 650, "ERP Module": 1500,
        "Desk Chair": 450, "Standing Desk": 700, "Whiteboard": 180, "Printer": 300,
        "Storage Plan": 200, "Compute Instance": 600, "Data Pipeline": 900, "ML Platform": 1200,
    }

    prices = [unit_prices[p] * np.random.uniform(0.85, 1.15) for p in product_choices]
    quantities = np.random.choice([1, 1, 1, 2, 2, 3, 5, 10], n_rows)
    discounts = np.random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20], n_rows)

    # Inject some data quality issues (realistic!)
    customer_ids = np.random.randint(1, len(CUSTOMER_NAMES) + 1, n_rows).astype(float)
    customer_ids[np.random.choice(n_rows, 50, replace=False)] = np.nan  # missing customer IDs

    raw_dates = [d.strftime("%Y-%m-%d") if random.random() > 0.02 else d.strftime("%d/%m/%Y") for d in dates]

    df = pd.DataFrame({
        "sale_id":        [f"TXN-{i:06d}" for i in range(1, n_rows + 1)],
        "sale_date":      raw_dates,
        "customer_id":    customer_ids,
        "customer_name":  [CUSTOMER_NAMES[int(cid) - 1] if not np.isnan(cid) else None
                           for cid in customer_ids],
        "segment":        np.random.choice(SEGMENTS, n_rows),
        "region":         np.random.choice(REGIONS, n_rows),
        "country":        np.random.choice(["USA", "UK", "Germany", "Japan", "Brazil", "UAE", "Canada", "France"], n_rows),
        "product_name":   product_choices,
        "category":       cat_choices,
        "quantity":       quantities,
        "unit_price":     [round(p, 2) for p in prices],
        "discount_pct":   discounts,
        "sales_rep":      [f"REP-{np.random.randint(1, 20):02d}" for _ in range(n_rows)],
        "source_system":  np.random.choice(["CRM", "ERP", "Web", "Manual"], n_rows, p=[0.5, 0.3, 0.15, 0.05]),
    })

    return df


def extract(output_path: str = "data/raw/sales_raw.csv", n_rows: int = 10_000) -> pd.DataFrame:
    """
    Main extract function. Generates (or loads) raw data and saves to CSV.
    Replace the body with a real DB/API connector in production.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Extracting {n_rows:,} sales records from source system...")
    df = generate_raw_data(n_rows=n_rows)

    df.to_csv(output_path, index=False)
    logger.info(f"Raw data saved → {output_path} ({len(df):,} rows, {df.shape[1]} columns)")
    logger.info(f"Date range: {df['sale_date'].min()} to {df['sale_date'].max()}")
    logger.info(f"Null customer IDs: {df['customer_id'].isna().sum()} (will be handled in transform)")

    return df


if __name__ == "__main__":
    df = extract()
    print(df.head())
