-- models/staging/stg_sales.sql
-- dbt staging model: clean and standardise raw sales data
-- Runs on: PostgreSQL / BigQuery / Snowflake (adjust date functions as needed)

{{
    config(
        materialized = 'view',
        tags = ['staging', 'sales']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('raw', 'sales_raw') }}
),

cleaned AS (
    SELECT
        -- IDs
        sale_id,
        CAST(customer_id AS INTEGER)                    AS customer_id,
        NULLIF(TRIM(customer_name), '')                 AS customer_name,

        -- Dates (handle mixed formats via CASE in real DBT — shown as standard here)
        CAST(sale_date AS DATE)                         AS sale_date,

        -- Dimensions
        UPPER(TRIM(segment))                            AS segment,
        TRIM(region)                                    AS region,
        TRIM(country)                                   AS country,
        TRIM(product_name)                              AS product_name,
        TRIM(category)                                  AS category,

        -- Measures
        CAST(quantity AS INTEGER)                       AS quantity,
        ROUND(CAST(unit_price AS NUMERIC), 2)          AS unit_price,
        COALESCE(CAST(discount_pct AS NUMERIC), 0)     AS discount_pct,

        -- Metadata
        TRIM(sales_rep)                                 AS sales_rep,
        COALESCE(TRIM(source_system), 'UNKNOWN')       AS source_system,
        CURRENT_TIMESTAMP                               AS _loaded_at

    FROM source
    WHERE sale_id IS NOT NULL          -- drop completely empty rows
      AND sale_date IS NOT NULL        -- drop unparseable dates
      AND quantity > 0                 -- drop zero-quantity records
      AND unit_price > 0               -- drop zero-price records
)

SELECT * FROM cleaned
