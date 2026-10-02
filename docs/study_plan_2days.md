# 2-Day Mastery Plan: Budget vs. Actual Variance Dashboard

This guide translates every financial term, DAX formula, and Power BI concept into Python and MySQL concepts.

---

## Day 1: Financial Concepts, Star Schema & DAX in SQL Terms

### Morning: Core Financial Terms Demystified

| Financial Term | Plain English Definition | Python / SQL Mental Model |
|---|---|---|
| P&L (Profit & Loss) | A summary statement showing money in vs. money out over a period. | A dataset table storing inflows and outflows. |
| Revenue | Total money earned from selling products or services. | `SELECT SUM(amount) WHERE statement_section = 'Revenue'` |
| COGS (Cost of Goods Sold) | Direct costs needed to produce/deliver goods (e.g., cloud hosting, payment fees). | Direct production expenses. |
| OPEX (Operating Expenses) | Day-to-day operational overhead (e.g., salaries, rent, marketing, software). | Operational overhead expenses. |
| Net Profit | Final remaining earnings after deducting all costs. | `Revenue - (COGS + OPEX)` |
| Variance ($ & %) | The difference between actual results and planned budget. | `Variance = Actual - Budget`<br>`Variance % = (Actual - Budget) / Budget` |
| Favorable vs Unfavorable | **Revenue**: Higher than budget is Good (Favorable).<br>**Expenses**: Higher than budget is Bad (Unfavorable). | `IF section == 'Revenue': Favorable if Actual >= Budget`<br>`ELSE: Favorable if Actual <= Budget` |

---

### Midday: Star Schema Architecture

Review `sql/schema.sql` and `docs/data_dictionary.md`.

```
         +---------------------------------------------+
         |                dim_department               |
         | (Who spent it: Executive, Sales, Eng, etc.) |
         +----------------------+----------------------+
                                | 1
                                |
                                | *
+-------------------------------+-----------------------+      * +------------------------------------------+
|                    fact_financials                    |--------+               dim_account                |
| (Transactions: date_key, dept_key, acct_key, scenario,|        | (What it was for: Salaries, Hosting, etc)|
|  amount: $120,000)                                    |        +------------------------------------------+
+-------------------------------+-----------------------+
                                | *
                                |
                                | 1
         +----------------------+----------------------+
         |                   dim_date                  |
         | (When it happened: FY2025, Q1, Month, Day)  |
         +---------------------------------------------+
```

1. **Fact Table (`fact_financials`)**: Contains transaction records, numerical measure (`amount`), foreign keys, and scenario tag (`'Actual'` or `'Budget'`).
2. **Dimension Tables (`dim_*`)**: Contain filtering and descriptive metadata (Department Names, GL Account Names, Calendar Dates).

---

### Afternoon: DAX Measures Translated to SQL

Review `dax/dax_measures.dax`.

#### 1. Base Actuals & Budget
- **DAX**:
  ```dax
  Total Actuals = CALCULATE(SUM(fact_financials[amount]), fact_financials[scenario] = "Actual")
  ```
- **SQL Equivalent**:
  ```sql
  SELECT SUM(amount) FROM fact_financials WHERE scenario = 'Actual';
  ```

#### 2. Percentage Variance with Safe Division
- **DAX**:
  ```dax
  Variance (%) = DIVIDE([Variance ($)], [Total Budget], 0)
  ```
- **SQL Equivalent**:
  ```sql
  SELECT (SUM(actual) - SUM(budget)) / NULLIF(SUM(budget), 0);
  ```

#### 3. Time Intelligence (Year-to-Date / YTD)
- **DAX**:
  ```dax
  Actuals YTD = TOTALYTD([Total Actuals], dim_date[full_date])
  ```
- **SQL Equivalent**:
  ```sql
  SUM(amount) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
  ```

#### 4. The 10% Review Alert Flag
- **DAX**:
  ```dax
  Flag Review Variance 10% = IF(ABS([Variance (%)]) >= 0.10, 1, 0)
  ```
- **Python Equivalent**:
  ```python
  flag = 1 if abs(variance_pct) >= 0.10 else 0
  ```

---

### Evening: Run the Data Pipeline & Verification Scripts

Run the following commands in PowerShell:

```powershell
python scripts/etl_pipeline.py
python scripts/verify_reconciliation.py
python -m unittest tests/test_data_integrity.py
```

---

## Day 2: Dashboard Mechanics, Data Verification & Interview Defense

### Morning: Power BI Concepts via the Live Web App

Open `web/index.html` in your browser:
- **Slicers**: Top dropdown filters (Fiscal Year, Month, Department) filtering all visuals dynamically.
- **KPI Summary Cards**: Top tiles showing Revenue, Expenses, Net Profit, and Alert Count.
- **Matrix Visual**: Interactive table hierarchy allowing drill-down from Department down to General Ledger accounts.
- **Waterfall Chart**: Visual bridge explaining how Revenue, COGS, and OPEX variances combine into net profit variance.

---

### Midday: Review SQL Verification & Audit Queries

Inspect `sql/data_validation.sql`:
1. Execute SQL aggregations across `fact_financials`.
2. Compare SQL totals directly against dashboard metrics ($40,389,477.23 Actual vs $40,228,944.00 Budget).
3. Confirm zero discrepancy between raw database and dashboard KPIs.

---

### Afternoon: Top Technical Interview Questions & Answers

#### Q1: Can you explain the architecture of your Budget Variance Dashboard?
**Answer**:
I designed an end-to-end financial reporting model based on a MySQL Star Schema. A centralized `fact_financials` table stores granular transaction amounts tagged as Actual or Budget, connected to three conformed dimensions: `dim_department`, `dim_account`, and `dim_date`. On top of this schema, DAX measures compute variance metrics, YTD cumulative figures, and MoM trends, with drill-down from executive summaries to GL line items.

#### Q2: How do you calculate variance and handle favorable vs unfavorable outcomes?
**Answer**:
Variance is calculated as `Actual - Budget`. For Revenue accounts, a positive variance is Favorable (higher earnings). For Expense and COGS accounts, a positive variance is Unfavorable (cost overruns). I implemented DAX logic to format favorable variances in green and unfavorable variances in red.

#### Q3: How does the 10% threshold alerting work?
**Answer**:
The DAX measure `Flag Review Variance 10%` evaluates `ABS([Variance (%)]) >= 0.10`. Whenever an account deviates by 10% or more over or under budget, the record is flagged, highlighted, and routed into an Executive Exception Review table.

#### Q4: Why use a Star Schema instead of a single flat table?
**Answer**:
Star Schema eliminates redundant descriptive data, optimizes storage, enforces referential integrity, and allows analytical engines to execute dimensional slicing and time intelligence calculations efficiently.

#### Q5: How did you verify data accuracy before publishing?
**Answer**:
I built automated SQL validation scripts (`data_validation.sql` and `verify_reconciliation.py`) that cross-reconciled fact table totals by scenario, department, and account against dashboard KPIs to ensure 100% data integrity with zero discrepancies.

---

### Evening: Practice the 2-Minute Project Summary

1. **Problem**: Monitoring enterprise P&L variance across departments against allocated budgets.
2. **Model**: 4-table Star Schema in MySQL.
3. **Analytics**: DAX formulas for variance ($, %), YTD, MoM, and 10% review flags.
4. **Validation**: Automated SQL scripts verifying source totals against dashboard outputs.
