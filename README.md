# 🏭 End-to-End Data Warehouse Pipeline

> Transforming raw operational data from 6 source systems into analytics-ready dimensional models — with a Power BI dashboard that eliminated analyst bottlenecks for 4 regional business units.

---

## 📌 Impact

| Metric | Result |
|--------|--------|
| Data quality improvement | **+20%** |
| Ad-hoc data prep time reduced | **−35%** across 200+ org units |
| Reporting delivery accelerated | **3 days faster** per cycle for 4 regional BUs |
| Stakeholder independence | Non-technical teams make decisions without analyst intervention |

---

## 🏗️ Architecture

```
Source Systems (6)
       │
       ▼
  [Fivetran]  ──── Raw ingestion & sync
       │
       ▼
  [Snowflake]  ─── Staging + raw layer
       │
       ▼
   [dbt / Python]  ── Transformation, cleaning, dimensional modeling
       │
       ▼
  Dimensional Models (Star Schema)
       │
       ▼
   [Power BI Dashboard]
   ├── KPI Tracking
   ├── Regional Drill-down
   └── Time-Period Filtering
```

---

## 🔧 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)
![Fivetran](https://img.shields.io/badge/Fivetran-0073FF?style=flat&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=postgresql&logoColor=white)

---

## 📁 Project Structure

```
data-warehouse-project/
├── etl/                    # Python ETL scripts and connectors
├── dbt_models/models/      # dbt transformation models
│   ├── staging/            # Raw source cleaning
│   ├── intermediate/       # Business logic transforms
│   └── marts/              # Analytics-ready dimensional models
├── sql/                    # Ad-hoc and validation queries
├── dashboard/              # Power BI report files and documentation
├── docs/                   # Architecture diagrams, data dictionary
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/rohinimallik572-svg/data-warehouse-project.git
cd data-warehouse-project

# Set up environment
cp .env.example .env
# Fill in your Snowflake credentials and Fivetran API keys

pip install -r requirements.txt

# Run dbt transformations
cd dbt_models
dbt deps
dbt run
dbt test
```

---

## 📊 Key Features

- **Star schema dimensional models** — fact and dimension tables optimized for BI querying
- **Incremental dbt models** — efficient re-processing of only new/changed records
- **Data quality tests** — dbt schema tests for nulls, uniqueness, referential integrity
- **Power BI dashboard** — KPI cards, regional drill-down filters, time-period slicers enabling self-serve analytics

---

## 💼 Business Context

Engineered at NatWest Group to unify operational data from 6 disconnected source systems spanning 200+ organisational units. The pipeline reduced analyst dependency for monthly reporting and enabled regional business units to access pre-built, trustworthy dimensional models directly.
