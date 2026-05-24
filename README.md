# 🏗️ Data Transformation & Warehousing Pipeline

> **End-to-end ETL pipeline** — raw sales data → cloud warehouse → business-ready KPI dashboards  
> Built with Python · SQL/dbt · Apache Spark · Kafka (simulated) · AWS/GCP-ready

---

## 📌 Project Overview

This project demonstrates a production-style data pipeline for a fictional retail company **RetailCo**, processing daily sales transactions across 5 regions. The pipeline ingests raw data, applies business transformations, loads into a star-schema warehouse, and surfaces KPIs via SQL views.

| Layer | Tool | Purpose |
|-------|------|---------|
| Ingestion | Python + Kafka (simulated) | Stream raw sales events |
| Transformation | Python (pandas) + dbt | Clean, model, enrich |
| Processing | PySpark | Aggregate large volumes |
| Warehouse | PostgreSQL / BigQuery-ready | Star schema storage |
| Reporting | SQL views + Power BI ready | KPI dashboards |

---

## 📁 Project Structure

```
data-warehouse-project/
│
├── data/
│   ├── raw/                    # Raw source CSV files (simulated source system)
│   └── processed/              # Output after transformation
│
├── etl/
│   ├── extract.py              # Data extraction from source
│   ├── transform.py            # Pandas-based transformation logic
│   ├── load.py                 # Load into warehouse (SQLite / PostgreSQL)
│   └── pipeline.py             # Orchestrates full ETL run
│
├── dbt_models/
│   ├── models/
│   │   ├── staging/            # stg_sales, stg_customers, stg_products
│   │   └── marts/              # dim_customer, dim_product, fact_sales
│   └── macros/                 # Reusable dbt macros
│
├── spark/
│   └── sales_aggregator.py     # PySpark job for large-scale aggregation
│
├── sql/
│   ├── schema.sql              # Warehouse schema DDL
│   └── kpi_views.sql           # Business KPI SQL views
│
├── dashboard/
│   └── kpi_summary.py          # Console KPI report (Power BI-ready output)
│
├── docs/
│   ├── architecture.md         # System design & data flow
│   └── data_dictionary.md      # Field definitions
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/data-warehouse-project.git
cd data-warehouse-project
pip install -r requirements.txt
```

### 2. Generate sample data & run the full pipeline
```bash
python etl/pipeline.py
```

This will:
- Generate realistic raw sales data (10,000 rows)
- Extract, clean, and transform it
- Load into a local SQLite warehouse (zero config needed)
- Print a KPI summary report

### 3. Run the Spark aggregation job
```bash
python spark/sales_aggregator.py
```

### 4. View KPI dashboards
```bash
python dashboard/kpi_summary.py
```

---

## 📊 Data Model (Star Schema)

```
                    ┌─────────────────┐
                    │   fact_sales    │
                    │─────────────────│
              ┌────▶│ sale_id (PK)    │◀────┐
              │     │ customer_id(FK) │     │
              │     │ product_id (FK) │     │
              │     │ date_id    (FK) │     │
              │     │ region          │     │
              │     │ quantity        │     │
              │     │ unit_price      │     │
              │     │ total_revenue   │     │
              │     │ discount_pct    │     │
              │     └─────────────────┘     │
              │                             │
   ┌──────────┴──────┐         ┌────────────┴────┐
   │  dim_customer   │         │  dim_product    │
   │─────────────────│         │─────────────────│
   │ customer_id(PK) │         │ product_id (PK) │
   │ full_name       │         │ product_name    │
   │ segment         │         │ category        │
   │ region          │         │ subcategory     │
   │ country         │         │ unit_cost       │
   └─────────────────┘         └─────────────────┘
```

---

## 📈 Key KPIs Produced

| KPI | Description |
|-----|-------------|
| Total Revenue | Sum of all sales by region / period |
| Gross Margin % | `(revenue - cost) / revenue` |
| Top 10 Products | By revenue contribution |
| Customer Segments | Revenue split by segment (Enterprise / SMB / Consumer) |
| Monthly Trend | MoM revenue growth rate |
| Regional Performance | Revenue by region with % share |

---

## 🛠️ Skills Demonstrated

- ✅ **Requirements Analysis** — modelled KPIs from business requirements
- ✅ **Data Modelling** — star schema with fact + dimension tables
- ✅ **Python / pandas** — transformation, cleaning, enrichment
- ✅ **SQL** — DDL schema, KPI views, window functions
- ✅ **dbt** — staging models, marts, documentation-ready
- ✅ **Apache Spark** — distributed aggregation with PySpark
- ✅ **Process Improvement** — pipeline reduced manual reporting by design
- ✅ **Cross-functional KPIs** — finance, sales, ops metrics in one model
- ✅ **Cloud-ready** — PostgreSQL / BigQuery / Snowflake compatible

---

## 🔧 Configuration

Copy `.env.example` to `.env` and set your database connection if using PostgreSQL:

```bash
cp .env.example .env
```

By default the pipeline uses **SQLite** — zero setup needed.

---

## 📚 Documentation

- [Architecture & Data Flow](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)

---

## 🏷️ Tags
`#DataEngineering` `#ETL` `#Python` `#SQL` `#dbt` `#ApacheSpark` `#DataWarehousing` `#BusinessIntelligence` `#PowerBI` `#CloudData`
