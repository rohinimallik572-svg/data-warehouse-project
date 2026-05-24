# Data Dictionary

## fact_sales

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| sale_id | VARCHAR | Unique transaction ID | TXN-000001 |
| sale_date | DATE | Transaction date | 2024-03-15 |
| date_key | INTEGER | YYYYMMDD surrogate key | 20240315 |
| customer_id | INTEGER | FK → dim_customer | 7 |
| product_id | INTEGER | FK → dim_product | 3 |
| region | VARCHAR | Sales region | Europe |
| country | VARCHAR | Country of sale | Germany |
| quantity | INTEGER | Units sold | 2 |
| unit_price | DECIMAL | Sale price per unit (£) | 1150.00 |
| discount_pct | DECIMAL | Discount applied (0–1) | 0.10 |
| gross_revenue | DECIMAL | qty × unit_price | 2300.00 |
| net_revenue | DECIMAL | gross_revenue × (1 - discount) | 2070.00 |
| total_cost | DECIMAL | qty × unit_cost | 1600.00 |
| gross_profit | DECIMAL | net_revenue - total_cost | 470.00 |
| gross_margin_pct | DECIMAL | gross_profit / net_revenue × 100 | 22.7 |
| year | INTEGER | Sale year | 2024 |
| quarter | INTEGER | Sale quarter (1–4) | 1 |
| month | INTEGER | Sale month (1–12) | 3 |
| month_name | VARCHAR | Month name | March |
| week_of_year | INTEGER | ISO week number | 11 |
| day_of_week | VARCHAR | Day name | Friday |
| is_weekend | BOOLEAN | True if Sat/Sun | False |
| sales_rep | VARCHAR | Sales rep code | REP-04 |
| source_system | VARCHAR | Data origin | CRM |

## dim_customer

| Field | Type | Description |
|-------|------|-------------|
| customer_id | INTEGER | PK — unique customer |
| full_name | VARCHAR | Company name |
| segment | VARCHAR | Enterprise / SMB / Consumer |
| region | VARCHAR | Customer region |
| country | VARCHAR | Customer country |

## dim_product

| Field | Type | Description |
|-------|------|-------------|
| product_id | INTEGER | PK — unique product |
| product_name | VARCHAR | Product display name |
| category | VARCHAR | Top-level category |
| subcategory | VARCHAR | Sub-level category |
| unit_cost | DECIMAL | Cost to company per unit (£) |

## Business Rules

1. **Revenue** = `quantity × unit_price × (1 − discount_pct)`
2. **Gross Margin** = `(net_revenue − total_cost) / net_revenue × 100`
3. Transactions with `quantity ≤ 0` or `unit_price ≤ 0` are excluded
4. Missing `customer_id` records are assigned `customer_id = 0` (Unknown Customer)
5. Dates must resolve to ISO format; unparseable dates are dropped
