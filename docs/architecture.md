# Architecture & Data Flow

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOURCE LAYER                             │
│  CSV Files · CRM exports · ERP extracts · Web events           │
└───────────────────────────┬─────────────────────────────────────┘
                            │  (Kafka stream in production)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                             │
│  etl/extract.py — pulls raw data, saves to data/raw/           │
│  In prod: Kafka consumer / Airflow DAG trigger                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TRANSFORMATION LAYER                          │
│  etl/transform.py (pandas)                                      │
│    • Date standardisation                                       │
│    • Null handling & imputation                                  │
│    • Financial metric derivation                                 │
│    • Star schema construction                                    │
│                                                                 │
│  dbt_models/ (production-grade SQL transforms)                  │
│    • stg_sales → fact_sales                                     │
│    • dim_customer, dim_product                                   │
│                                                                 │
│  spark/sales_aggregator.py (PySpark)                            │
│    • Distributed aggregations at scale                          │
│    • MoM window functions                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WAREHOUSE LAYER                            │
│  SQLite (local dev) · PostgreSQL · BigQuery · Snowflake         │
│                                                                 │
│  Star Schema:                                                   │
│    fact_sales ──▶ dim_customer                                  │
│               ──▶ dim_product                                   │
│               ──▶ dim_date                                      │
│                                                                 │
│  KPI Views:                                                     │
│    vw_revenue_by_region · vw_product_performance               │
│    vw_segment_performance · vw_monthly_trend                    │
│    vw_sales_rep_performance · vw_exec_summary                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORTING LAYER                               │
│  dashboard/kpi_summary.py — console KPI report                  │
│  Power BI / Tableau — connect to warehouse views                 │
│  SQL queries — ad-hoc analysis                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema design | Star schema | Simple joins, optimised for aggregation |
| Local warehouse | SQLite | Zero-config, portable, BigQuery-compatible SQL |
| Transform tool | pandas + dbt | pandas for ETL logic, dbt for warehouse models |
| Scale layer | PySpark | Demonstrates distributed processing capability |
| Date handling | Multi-format parser | Realistic — source systems use mixed formats |
| Missing data | Imputation + flag | Business rule: retain records, flag unknowns |

## Cloud Deployment (Production Path)

```
AWS / GCP variant:
  Source data     → S3 / GCS bucket
  Streaming       → MSK (Kafka) / Pub/Sub
  Processing      → EMR / Dataproc (Spark)
  Warehouse       → Redshift / BigQuery
  Orchestration   → Airflow / Cloud Composer
  BI layer        → Power BI / Looker
```
