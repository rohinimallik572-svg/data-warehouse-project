-- models/marts/fact_sales.sql
-- dbt mart: final fact_sales table with all financials

{{
    config(
        materialized = 'table',
        tags = ['marts', 'finance', 'sales'],
        indexes = [
            {'columns': ['customer_id']},
            {'columns': ['product_id']},
            {'columns': ['year', 'month']},
        ]
    )
}}

WITH stg AS (
    SELECT * FROM {{ ref('stg_sales') }}
),

product_costs AS (
    SELECT * FROM {{ ref('dim_product') }}
),

financials AS (
    SELECT
        s.sale_id,
        s.sale_date,
        TO_CHAR(s.sale_date, 'YYYYMMDD')::INT          AS date_key,
        COALESCE(s.customer_id, 0)                      AS customer_id,
        p.product_id,
        s.region,
        s.country,
        s.quantity,
        s.unit_price,
        s.discount_pct,
        s.sales_rep,
        s.source_system,

        -- Financial calculations
        ROUND(s.quantity * s.unit_price, 2)             AS gross_revenue,
        ROUND(s.quantity * s.unit_price * (1 - s.discount_pct), 2)  AS net_revenue,
        ROUND(s.quantity * p.unit_cost, 2)              AS total_cost,
        ROUND(
            s.quantity * s.unit_price * (1 - s.discount_pct) -
            s.quantity * p.unit_cost, 2
        )                                               AS gross_profit,

        -- Date parts
        EXTRACT(YEAR  FROM s.sale_date)::INT            AS year,
        EXTRACT(QUARTER FROM s.sale_date)::INT          AS quarter,
        EXTRACT(MONTH FROM s.sale_date)::INT            AS month,
        TO_CHAR(s.sale_date, 'Month')                   AS month_name,
        EXTRACT(WEEK  FROM s.sale_date)::INT            AS week_of_year,
        TO_CHAR(s.sale_date, 'Day')                     AS day_of_week,
        EXTRACT(DOW FROM s.sale_date) IN (0, 6)        AS is_weekend

    FROM stg s
    LEFT JOIN product_costs p ON s.product_name = p.product_name
)

SELECT
    *,
    CASE
        WHEN net_revenue > 0
        THEN ROUND(gross_profit / net_revenue * 100, 2)
        ELSE 0
    END AS gross_margin_pct
FROM financials
