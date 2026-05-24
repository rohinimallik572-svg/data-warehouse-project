-- kpi_views.sql
-- Business KPI Views for RetailCo Sales Analytics
-- These power the Power BI / Tableau dashboards

-- ═══════════════════════════════════════
-- KPI 1: Total Revenue by Region & Period
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_revenue_by_region AS
SELECT
    region,
    year,
    quarter,
    month_name,
    ROUND(SUM(net_revenue), 0)      AS total_revenue,
    ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
    COUNT(sale_id)                  AS transactions,
    SUM(quantity)                   AS units_sold
FROM fact_sales
GROUP BY region, year, quarter, month_name;


-- ═══════════════════════════════════════
-- KPI 2: Product Performance
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_product_performance AS
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(f.net_revenue), 0)      AS total_revenue,
    ROUND(AVG(f.gross_margin_pct), 1) AS avg_margin_pct,
    SUM(f.quantity)                   AS units_sold,
    COUNT(f.sale_id)                  AS transactions,
    ROUND(
        SUM(f.net_revenue) * 100.0 /
        SUM(SUM(f.net_revenue)) OVER (), 2
    )                                 AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name, p.category;


-- ═══════════════════════════════════════
-- KPI 3: Customer Segment Analysis
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_segment_performance AS
SELECT
    c.segment,
    ROUND(SUM(f.net_revenue), 0)      AS total_revenue,
    ROUND(AVG(f.gross_margin_pct), 1) AS avg_margin_pct,
    COUNT(DISTINCT f.customer_id)     AS unique_customers,
    COUNT(f.sale_id)                  AS transactions,
    ROUND(SUM(f.net_revenue) / COUNT(DISTINCT f.customer_id), 0) AS revenue_per_customer
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
WHERE c.segment != 'Unassigned'
GROUP BY c.segment;


-- ═══════════════════════════════════════
-- KPI 4: Monthly Revenue Trend
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_monthly_trend AS
SELECT
    year,
    month,
    month_name,
    ROUND(SUM(net_revenue), 0)      AS monthly_revenue,
    ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
    COUNT(sale_id)                  AS transactions
FROM fact_sales
GROUP BY year, month, month_name
ORDER BY year, month;


-- ═══════════════════════════════════════
-- KPI 5: Sales Rep Leaderboard
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_sales_rep_performance AS
SELECT
    sales_rep,
    region,
    ROUND(SUM(net_revenue), 0)      AS total_revenue,
    ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
    COUNT(sale_id)                  AS transactions,
    SUM(quantity)                   AS units_sold
FROM fact_sales
GROUP BY sales_rep, region
ORDER BY total_revenue DESC;


-- ═══════════════════════════════════════
-- KPI 6: Executive Summary (single row)
-- ═══════════════════════════════════════
CREATE VIEW IF NOT EXISTS vw_exec_summary AS
SELECT
    COUNT(sale_id)                  AS total_transactions,
    COUNT(DISTINCT customer_id)     AS unique_customers,
    COUNT(DISTINCT product_id)      AS unique_products,
    ROUND(SUM(net_revenue), 0)      AS total_net_revenue,
    ROUND(SUM(gross_profit), 0)     AS total_gross_profit,
    ROUND(AVG(gross_margin_pct), 1) AS avg_gross_margin_pct,
    ROUND(SUM(net_revenue) / COUNT(DISTINCT customer_id), 0) AS avg_revenue_per_customer,
    MIN(sale_date)                  AS first_sale_date,
    MAX(sale_date)                  AS last_sale_date
FROM fact_sales;
