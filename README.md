# 🏥 NHS A&E Healthcare Data Pipeline

> **End-to-end healthcare data pipeline** — raw NHS A&E attendance data → Snowflake warehouse → operational KPI dashboards  
> Built with Python · SQL / dbt · Snowflake · Apache Spark · Power BI

---

## 📌 Project Overview

This project demonstrates a production-style healthcare data pipeline processing **monthly NHS England A&E (Accident & Emergency) attendance and waiting time data** across 200+ hospitals and NHS trusts.

The pipeline ingests publicly available government data, applies clinical operations business rules, models it into a structured Snowflake warehouse using dbt, and surfaces operational KPIs — including 4-hour breach rates, regional patient flow trends, and department-level resource utilisation — via a Power BI dashboard designed for hospital operations managers.

**Dataset:** [NHS England A&E Attendances and Emergency Admissions](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/) — publicly available, updated monthly, free to use.

| Layer | Tool | Purpose |
|---|---|---|
| Ingestion | Python (requests + pandas) | Download & parse NHS monthly CSV releases |
| Transformation | Python (pandas) + dbt | Clean, validate, model into dimensional schema |
| Processing | PySpark | Aggregate multi-year data at scale |
| Warehouse | Snowflake (dbt-managed) | Star schema storage, version-controlled models |
| Reporting | SQL views + Power BI | Operational KPI dashboards for capacity planning |

---

## 📁 Project Structure

```
data-warehouse-project/
│
├── data/
│   ├── raw/                          # Raw NHS A&E monthly CSV files
│   └── processed/                    # Cleaned & transformed output
│
├── etl/
│   ├── extract.py                    # Downloads NHS A&E data from NHS England API / CSV
│   ├── transform.py                  # Cleans, validates, and enriches raw data
│   ├── load.py                       # Loads into Snowflake (or local SQLite for dev)
│   └── pipeline.py                   # Orchestrates full ETL run
│
├── dbt_models/
│   ├── models/
│   │   ├── staging/                  # stg_ae_attendances, stg_hospitals, stg_regions
│   │   └── marts/
│   │       ├── dim_hospital.sql      # Hospital & NHS trust dimension
│   │       ├── dim_region.sql        # Region / ICB dimension
│   │       ├── dim_date.sql          # Date dimension (month, quarter, year)
│   │       ├── dim_department.sql    # A&E department type dimension
│   │       └── fact_ae_activity.sql  # Core fact table: attendances, waits, breaches
│   └── macros/                       # Reusable dbt macros (breach rate calc, etc.)
│
├── spark/
│   └── ae_aggregator.py              # PySpark job for multi-year trend aggregation
│
├── sql/
│   ├── schema.sql                    # Snowflake DDL (warehouses, schemas, roles)
│   └── kpi_views.sql                 # Operational KPI SQL views
│
├── dashboard/
│   └── kpi_summary.py                # Console KPI report (mirrors Power BI output)
│
├── docs/
│   ├── architecture.md               # System design & data flow diagram
│   └── data_dictionary.md            # Field definitions & NHS data glossary
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/rohinimallik572-svg/data-warehouse-project.git
cd data-warehouse-project
pip install -r requirements.txt
```

### 2. Run the full pipeline (local dev mode — no Snowflake needed)

```bash
python etl/pipeline.py
```

This will:
- Download the latest NHS A&E monthly data from NHS England
- Clean and validate the raw CSV (handle nulls, type mismatches, NHS trust name changes)
- Apply business logic: calculate breach rates, flag seasonal periods, classify department types
- Load into a local SQLite warehouse (zero config — works immediately)
- Print a KPI summary to the console

### 3. Run the Spark aggregation (multi-year trend analysis)

```bash
python spark/ae_aggregator.py
```

### 4. View the KPI dashboard output

```bash
python dashboard/kpi_summary.py
```

### 5. Connect to Snowflake (production mode)

Copy `.env.example` to `.env` and add your Snowflake credentials:

```bash
cp .env.example .env
```

Then run dbt models against your Snowflake instance:

```bash
cd dbt_models
dbt run
dbt test
dbt docs generate
```

---

## 📊 Data Model (Star Schema)

```
                       ┌──────────────────────┐
                       │   fact_ae_activity   │
                       │──────────────────────│
          ┌───────────▶│ activity_id    (PK)  │◀──────────────┐
          │            │ hospital_id    (FK)  │               │
          │            │ region_id      (FK)  │               │
          │            │ date_id        (FK)  │               │
          │            │ department_id  (FK)  │               │
          │            │ total_attendances    │               │
          │            │ attendances_gt4hr    │               │
          │            │ breach_rate_pct      │               │
          │            │ admitted_patients    │               │
          │            │ avg_wait_mins        │               │
          │            └──────────────────────┘               │
          │                                                    │
┌─────────┴────────┐   ┌──────────────┐   ┌──────────────────┴──┐
│  dim_hospital    │   │  dim_region  │   │   dim_department     │
│──────────────────│   │──────────────│   │─────────────────────-│
│ hospital_id (PK) │   │ region_id(PK)│   │ department_id   (PK) │
│ hospital_name    │   │ region_name  │   │ department_type      │
│ nhs_trust        │   │ icb_name     │   │ ae_type (1/2/other)  │
│ trust_code       │   │ nhs_region   │   └──────────────────────┘
│ hospital_type    │   └──────────────┘
│ lat / lon        │
└──────────────────┘
```

**Key business logic applied in dbt models:**
- `breach_rate_pct` = patients waiting over 4 hours ÷ total attendances × 100
- `ae_type` classification: Type 1 (major A&E), Type 2 (single-specialty), Type 3 (minor injuries unit)
- Seasonal flagging: winter pressure months (Nov–Feb) vs. baseline
- 12-month rolling averages for trend smoothing

---

## 📈 Key KPIs Surfaced

| KPI | Description | NHS Benchmark |
|---|---|---|
| 4-hour breach rate | % patients not seen within 4 hours | < 5% target |
| Total A&E attendances | Monthly volume by hospital / region | — |
| Emergency admissions rate | % attendances resulting in admission | — |
| Average wait time | Mean wait in minutes by department type | — |
| Regional patient flow | Attendance volume by ICB / NHS region | — |
| Winter pressure index | % uplift in attendances vs. summer baseline | — |
| Hospital performance rank | Trust-level breach rate league table | — |
| YoY attendance trend | Year-on-year change in monthly volumes | — |

---

## 🛠️ Skills Demonstrated

- ✅ **Healthcare domain** — NHS A&E operational data, breach rate definitions, ICB/trust structures
- ✅ **Data Modelling** — star schema: fact table + 4 dimension tables, dbt-managed in Snowflake
- ✅ **dbt** — staging models, mart models, schema tests, documentation, macros
- ✅ **Snowflake** — warehouse setup, roles, schemas, dbt integration
- ✅ **Python / pandas** — NHS data ingestion, cleaning, null handling, type enforcement
- ✅ **SQL** — window functions, breach rate aggregations, rolling averages, KPI views
- ✅ **Apache Spark** — PySpark multi-year aggregation for large monthly datasets
- ✅ **KPI Development** — defined 8 operational KPIs from business requirements
- ✅ **Quantitative Analysis** — breach rate trends, seasonal analysis, regional benchmarking
- ✅ **Process Improvement** — pipeline replaces manual monthly Excel-based reporting
- ✅ **Power BI / BI Tools** — dashboard designed for hospital operations managers
- ✅ **Cross-functional output** — serves capacity planning, finance, and clinical ops teams

---

## 📋 Resume One-Liner

> *"Built an end-to-end healthcare data pipeline ingesting NHS A&E attendance data across 200+ hospitals, modelling it in dbt and Snowflake into a star schema, and surfacing operational KPIs — 4-hour breach rates, resource utilisation, and regional patient flow trends — via a Power BI dashboard to support capacity planning decisions."*

---

## 🔧 Configuration

| Variable | Description |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier |
| `SNOWFLAKE_USER` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | Snowflake password |
| `SNOWFLAKE_DATABASE` | Target database (e.g. `NHS_AE_DWH`) |
| `SNOWFLAKE_SCHEMA` | Target schema (e.g. `MARTS`) |
| `SNOWFLAKE_WAREHOUSE` | Compute warehouse name |

Default mode uses **SQLite** — zero setup, runs immediately with `python etl/pipeline.py`.

---

## 📚 Documentation

- [Architecture & Data Flow](docs/architecture.md)
- [Data Dictionary & NHS Glossary](docs/data_dictionary.md)
- [NHS England A&E Data Source](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/)

---

## 🏷️ Tags

`#HealthcareData` `#NHS` `#DataEngineering` `#ETL` `#Python` `#SQL` `#dbt` `#Snowflake` `#ApacheSpark` `#DataWarehousing` `#PowerBI` `#BusinessAnalysis` `#KPIDesign` `#QuantitativeAnalysis`
