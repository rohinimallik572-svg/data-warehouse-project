-- schema.sql
-- Warehouse DDL — Star Schema for RetailCo Sales Analytics
-- Compatible with: SQLite · PostgreSQL · BigQuery (with minor type adjustments)

-- ═══════════════════════════════════════
-- DIMENSION TABLES
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id   INTEGER      PRIMARY KEY,
    full_name     VARCHAR(200),
    segment       VARCHAR(50),   -- Enterprise / SMB / Consumer / Unassigned
    region        VARCHAR(100),
    country       VARCHAR(100),
    loaded_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id    INTEGER      PRIMARY KEY,
    product_name  VARCHAR(200) NOT NULL,
    category      VARCHAR(100),
    subcategory   VARCHAR(100),
    unit_cost     DECIMAL(10,2),
    loaded_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key      INTEGER      PRIMARY KEY,  -- YYYYMMDD
    full_date     DATE,
    year          INTEGER,
    quarter       INTEGER,
    month         INTEGER,
    month_name    VARCHAR(20),
    week_of_year  INTEGER,
    day_of_week   VARCHAR(20),
    is_weekend    BOOLEAN
);

-- ═══════════════════════════════════════
-- FACT TABLE
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id           VARCHAR(20)  PRIMARY KEY,
    sale_date         DATE,
    date_key          INTEGER      REFERENCES dim_date(date_key),
    customer_id       INTEGER      REFERENCES dim_customer(customer_id),
    product_id        INTEGER      REFERENCES dim_product(product_id),
    region            VARCHAR(100),
    country           VARCHAR(100),
    quantity          INTEGER,
    unit_price        DECIMAL(10,2),
    discount_pct      DECIMAL(5,4),
    gross_revenue     DECIMAL(12,2),
    net_revenue       DECIMAL(12,2),
    total_cost        DECIMAL(12,2),
    gross_profit      DECIMAL(12,2),
    gross_margin_pct  DECIMAL(6,2),
    year              INTEGER,
    quarter           INTEGER,
    month             INTEGER,
    month_name        VARCHAR(20),
    week_of_year      INTEGER,
    day_of_week       VARCHAR(20),
    is_weekend        BOOLEAN,
    sales_rep         VARCHAR(20),
    source_system     VARCHAR(50),
    loaded_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_fact_customer  ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_product   ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_date      ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_region    ON fact_sales(region);
CREATE INDEX IF NOT EXISTS idx_fact_ym        ON fact_sales(year, month);
CREATE INDEX IF NOT EXISTS idx_fact_segment   ON fact_sales(region, year, quarter);
