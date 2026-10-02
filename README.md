# Budget vs. Actual Variance Dashboard

Enterprise Financial Analytics, Data Warehouse, and Reporting Solution using MySQL Star Schema, DAX, Power BI, Python ETL, and Interactive Web BI.

---

## Architecture Overview

```
        +-------------------------+
        |     dim_department      |
        +-------------------------+
        | PK  department_key      |
        |     department_id       |
        |     department_name     |
        |     division            |
        |     cost_center_code    |
        |     head_of_department  |
        +------------+------------+
                     | 1
                     |
                     | *
+--------------------+----+    * +-------------------------+
|     fact_financials     |------+       dim_account       |
+-------------------------+      +-------------------------+
| PK  transaction_key     |      | PK  account_key         |
| FK  date_key            |      |     account_number      |
| FK  department_key      |      |     account_name        |
| FK  account_key         |      |     account_category    |
|     scenario            |      |     sub_category        |
|     amount              |      |     statement_section   |
+------------+------------+      |     normal_balance      |
             | *                 +-------------------------+
             |
             | 1
+------------+------------+
|        dim_date         |
+-------------------------+
| PK  date_key            |
|     full_date           |
|     year                |
|     quarter             |
|     month_num           |
|     month_name          |
|     month_short         |
|     year_month          |
|     fiscal_year         |
|     fiscal_quarter      |
+-------------------------+
```

---

## Project Structure

```
Budget-Variance-Dashboard/
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   ├── views.sql
│   ├── stored_procedures.sql
│   └── data_validation.sql
├── data/
│   ├── dim_account.csv
│   ├── dim_date.csv
│   ├── dim_department.csv
│   ├── fact_financials.csv
│   └── Budget_vs_Actual_Variance_Model.xlsx
├── dax/
│   └── dax_measures.dax
├── web/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data.js
├── scripts/
│   ├── generate_data.py
│   ├── etl_pipeline.py
│   ├── verify_reconciliation.py
│   ├── generate_excel_model.py
│   └── export_web_data.py
├── tests/
│   └── test_data_integrity.py
├── powerbi/
│   └── dashboard_specification.md
├── docs/
│   ├── data_dictionary.md
│   └── learning_guide_48h.md
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
└── README.md
```

---

## Quick Start Guide

### 1. Launch Live Interactive Web Dashboard
Open `web/index.html` in any browser to explore the interactive dashboard with charts, drill-down hierarchy, slicers, and 10% threshold alerting.

### 2. Run ETL Pipeline & Data Integrity Tests
```bash
python scripts/etl_pipeline.py
python -m unittest tests/test_data_integrity.py
```

### 3. Generate Formatted Excel Financial Model
```bash
python scripts/generate_excel_model.py
```

### 4. Verify SQL Reconciliation & Totals
```bash
python scripts/verify_reconciliation.py
```

### 5. Dockerized MySQL Warehouse Setup
```bash
docker-compose up -d
```

---

## 48-Hour Learning & Interview Roadmap
Refer to `docs/learning_guide_48h.md` for a structured breakdown of the star schema design, DAX measures hierarchy, SQL reconciliation queries, and key interview talking points.
