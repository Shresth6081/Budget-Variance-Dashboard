# Power BI Dashboard Specification

## Data Model Relationships
- `dim_department[department_key]` 1 -> * `fact_financials[department_key]` (Single Direction)
- `dim_account[account_key]` 1 -> * `fact_financials[account_key]` (Single Direction)
- `dim_date[date_key]` 1 -> * `fact_financials[date_key]` (Single Direction)

## Dashboard Layout & Structure

### Page 1: Executive P&L Variance Overview
- Top KPI Ribbon:
  - Card 1: `Total Actual Revenue` vs `Total Budget Revenue` with `Revenue Variance (%)`
  - Card 2: `Total Actual Expenses` vs `Total Budget Expenses` with `Expense Variance (%)`
  - Card 3: `Actual Net Profit` vs `Budget Net Profit` with `Net Profit Variance (%)`
  - Card 4: `Flagged Review Count` (KPI indicator for accounts exceeding +/- 10% threshold)
- Filter Pane:
  - Slicer: `dim_date[year]` (Single / Multi Select)
  - Slicer: `dim_date[month_name]` (Ordered by `month_num`)
  - Slicer: `dim_department[division]`
  - Slicer: `dim_department[department_name]`
- Main Visuals:
  - Visual 1 (Top Left): Monthly Actual vs Budget Revenue Trend (Clustered Column & Line Chart)
    - X-Axis: `dim_date[month_short]`
    - Column: `Budget Revenue`
    - Line: `Actual Revenue`
  - Visual 2 (Top Right): Monthly Actual vs Budget Expense Trend (Clustered Column & Line Chart)
    - X-Axis: `dim_date[month_short]`
    - Column: `Budget Expenses`
    - Line: `Actual Expenses`
  - Visual 3 (Bottom Left): Waterfall Variance Chart
    - Category: `dim_account[statement_section]`
    - Breakdown: `dim_account[sub_category]`
    - Y-Axis: `Variance ($)`
  - Visual 4 (Bottom Right): Department Variance Breakdown (Bar Chart)
    - Y-Axis: `dim_department[department_name]`
    - X-Axis: `Variance ($)`
    - Color Conditional Formatting: `Variance Status Color`

### Page 2: Department & Account Drill-Down Matrix
- Drill-Down Matrix:
  - Row Hierarchy: `dim_department[department_name]` -> `dim_account[statement_section]` -> `dim_account[account_category]` -> `dim_account[account_name]`
  - Columns: `dim_date[year_month]`
  - Values:
    - `Total Actuals`
    - `Total Budget`
    - `Variance ($)`
    - `Variance (%)`
    - `Flag Review Variance 10% Text`
- Conditional Formatting:
  - Background color on `Variance (%)` linked to measure `KPI Variance Badge Color`
  - Soft Red highlighting when `ABS([Variance (%)]) >= 0.10`

### Page 3: YTD & MoM Financial Performance
- Performance Analysis Table:
  - Rows: `dim_date[month_name]`
  - Values:
    - `Total Actuals`
    - `Actuals YTD`
    - `Budget YTD`
    - `Variance YTD ($)`
    - `Variance YTD (%)`
    - `Actuals Prior Month`
    - `Actuals MoM ($)`
    - `Actuals MoM (%)`
- Visual 1: Cumulative YTD Budget vs Actual (Line Chart)
  - X-Axis: `dim_date[month_short]`
  - Lines: `Actuals YTD`, `Budget YTD`
- Visual 2: Month-over-Month Growth Velocity (Clustered Bar Chart)
  - X-Axis: `Actuals MoM (%)`
  - Y-Axis: `dim_department[department_name]`

### Page 4: Variance Exception & Audit Review
- Review Table (Filtered to `Flag Review Variance 10% = 1`):
  - Columns:
    - `dim_date[full_date]`
    - `dim_department[department_name]`
    - `dim_account[account_number]`
    - `dim_account[account_name]`
    - `dim_account[statement_section]`
    - `Total Budget`
    - `Total Actuals`
    - `Variance ($)`
    - `Variance (%)`
    - `Review Required Summary`
