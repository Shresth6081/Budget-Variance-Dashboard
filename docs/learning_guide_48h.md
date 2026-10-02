# 48-Hour Accelerated Master Guide: Budget vs. Actual Variance Dashboard

This guide equips you to understand and speak about every architectural component, data model decision, DAX measure, and SQL query in this project.

---

## High-Level Project Story

### Executive Problem Statement
Enterprise finance teams require visibility into departmental spending versus allocated budget. When variance exceeds acceptable tolerance (&plusmn;10%), leadership needs immediate drill-down capabilities from division-level summaries down to individual General Ledger (GL) line items without data reconciliation delays.

### Core Solution Architecture
1. **Data Layer (MySQL / Data Warehouse)**:
   - Star schema with 1 centralized Fact Table (`fact_financials`) and 3 Conformed Dimensions (`dim_department`, `dim_account`, `dim_date`).
   - Automated Referential Integrity, indexing, analytical views, and stored procedures.
2. **Business Logic & Analytics Layer (DAX & SQL)**:
   - Core measures for Actuals, Budget, Variance ($), and Variance (%).
   - Time Intelligence formulas: Year-to-Date (YTD), Month-over-Month (MoM), Same Period Last Year (SPLY).
   - Automated threshold alerting for items exceeding &plusmn;10% variance.
3. **Presentation Layer (Power BI Desktop & Live Web BI)**:
   - Executive overview cards with dynamic status badges.
   - Interactive multi-level matrix hierarchy: Department &rarr; P&L Statement Section &rarr; Sub-Category &rarr; Account.
   - Waterfall charts and bar charts for net financial impact.
4. **Data Pipeline & Audit (Python ETL & Excel Modeling)**:
   - Extraction, validation, and staging pipeline.
   - Multi-tab automated Excel variance model with dynamic cell formulas and conditional audit logs.
   - Pytest / Unittest validation suite ensuring 100% data integrity.

---

## Hour-by-Hour Learning Plan (2-Day Mastery)

### Day 1: Data Modeling, SQL, and DAX Deep Dive

#### 09:00 - 12:00: Star Schema Architecture
- Review `sql/schema.sql` and `docs/data_dictionary.md`.
- **Key Concept**: Why Star Schema? Star schemas eliminate transitive dependencies, simplify reporting queries, and allow Power BI VertiPaq engine to optimize column compression and relationship traversal.
- **Key Tables**:
  - `dim_department`: Department ID, Division, Cost Center Code, Head of Department.
  - `dim_account`: Chart of Accounts, Statement Section (`Revenue`, `COGS`, `OPEX`), Normal Balance.
  - `dim_date`: Continuous calendar dimension supporting time intelligence (FY2025 - FY2026).
  - `fact_financials`: Granular transactions tagged by `scenario` (`Actual` vs `Budget`).

#### 13:00 - 15:00: SQL Views, Stored Procedures, and Reconciliation
- Review `sql/views.sql`, `sql/stored_procedures.sql`, and `sql/data_validation.sql`.
- Run `python scripts/verify_reconciliation.py`.
- **Key Query**: How to calculate percentage variance in SQL with zero-division safety:
```sql
ROUND(
    ((SUM(CASE WHEN scenario = 'Actual' THEN amount ELSE 0 END) - 
      SUM(CASE WHEN scenario = 'Budget' THEN amount ELSE 0 END)) / 
      NULLIF(SUM(CASE WHEN scenario = 'Budget' THEN amount ELSE 0 END), 0)) * 100, 
    2
) AS variance_pct
```

#### 15:30 - 18:00: DAX Measure Hierarchy
- Review `dax/dax_measures.dax`.
- Understand the 3 layers of DAX:
  1. **Base Aggregations**: `Total Actuals`, `Total Budget`, `Actual Revenue`, `Actual Expenses`.
  2. **Variance Calculations**: `Variance ($)`, `Variance (%)`, `Variance Impact Label`.
  3. **Time Intelligence**: `Actuals YTD` using `TOTALYTD()`, `Actuals Prior Month` using `DATEADD()`, `Actuals MoM (%)`.
  4. **Dynamic Flagging**: `Flag Review Variance 10%` evaluating `ABS([Variance (%)]) >= 0.10`.

---

### Day 2: Interactive Dashboards, ETL Pipeline & Interview Readiness

#### 09:00 - 12:00: Live Interactive Web Dashboard & Power BI Specifications
- Open `web/index.html` in your browser.
- Test the interactive features:
  - Slicers: Fiscal Year, Month, Division, Department.
  - Drill-down matrix: Expand Engineering &rarr; OPEX &rarr; SaaS Subscriptions.
  - SPLY and YTD cumulative chart progression.
  - Variance exception audit table with &plusmn;10% threshold badge.
- Cross-reference with `powerbi/dashboard_specification.md` to explain how to reproduce every visual in Power BI Desktop.

#### 13:00 - 15:00: Production ETL Pipeline and Automated Financial Modeling
- Review `scripts/etl_pipeline.py` and `scripts/generate_excel_model.py`.
- Run `python scripts/generate_excel_model.py` and inspect `data/Budget_vs_Actual_Variance_Model.xlsx`.
- Run unit tests: `python -m unittest tests/test_data_integrity.py`.

#### 15:30 - 18:00: Interview Pitch & Demonstration Talking Points
- Prepare answers for top interview questions:
  1. *How did you handle Favorable vs Unfavorable variance?*
     - Revenue: Actual > Budget is Favorable (positive impact).
     - Expense / COGS: Actual > Budget is Unfavorable (negative impact).
  2. *How did you ensure 100% data reconciliation?*
     - Implemented automated SQL validation scripts comparing fact table sum by scenario with dashboard card outputs. Zero variance discrepancies.
  3. *Why use 10% variance threshold alerting?*
     - Allows management to practice exception-based reporting, focusing executive attention on significant budget deviations.

---

## Quick Reference Command Cheatsheet

1. **Generate Raw Data & Warehouse SQL**:
   `python scripts/generate_data.py`

2. **Run ETL Pipeline Staging**:
   `python scripts/etl_pipeline.py`

3. **Verify Reconciliation Totals**:
   `python scripts/verify_reconciliation.py`

4. **Generate Excel Financial Model**:
   `python scripts/generate_excel_model.py`

5. **Run Data Warehouse Integrity Tests**:
   `python -m unittest tests/test_data_integrity.py`

6. **Launch Dockerized MySQL & ETL**:
   `docker-compose up -d`

7. **Launch Live Web Dashboard**:
   Open `web/index.html` directly in any web browser.
