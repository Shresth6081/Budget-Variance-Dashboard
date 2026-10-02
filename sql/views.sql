USE budget_variance_db;

DROP VIEW IF EXISTS vw_financial_star_schema;
DROP VIEW IF EXISTS vw_monthly_pl_summary;
DROP VIEW IF EXISTS vw_department_variance_summary;
DROP VIEW IF EXISTS vw_variance_audit_alerts;

CREATE VIEW vw_financial_star_schema AS
SELECT 
    f.transaction_key,
    d.date_key,
    d.full_date,
    d.year,
    d.quarter,
    d.month_num,
    d.month_name,
    d.month_short,
    d.year_month,
    d.fiscal_year,
    d.fiscal_quarter,
    dept.department_key,
    dept.department_id,
    dept.department_name,
    dept.division,
    dept.cost_center_code,
    dept.head_of_department,
    a.account_key,
    a.account_number,
    a.account_name,
    a.account_category,
    a.sub_category,
    a.statement_section,
    a.normal_balance,
    f.scenario,
    f.amount
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_department dept ON f.department_key = dept.department_key
JOIN dim_account a ON f.account_key = a.account_key;

CREATE VIEW vw_monthly_pl_summary AS
SELECT 
    d.year,
    d.month_num,
    d.year_month,
    a.statement_section,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_dollars,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY d.year, d.month_num, d.year_month, a.statement_section;

CREATE VIEW vw_department_variance_summary AS
SELECT 
    d.year,
    dept.department_id,
    dept.department_name,
    dept.division,
    SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) AS actual_revenue,
    SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) AS budget_revenue,
    SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section IN ('COGS', 'OPEX') THEN f.amount ELSE 0 END) AS actual_expenses,
    SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section IN ('COGS', 'OPEX') THEN f.amount ELSE 0 END) AS budget_expenses,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS total_actual,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS total_budget,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS total_variance,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_department dept ON f.department_key = dept.department_key
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY d.year, dept.department_id, dept.department_name, dept.division;

CREATE VIEW vw_variance_audit_alerts AS
SELECT 
    d.year,
    d.month_num,
    d.year_month,
    dept.department_name,
    dept.cost_center_code,
    a.account_number,
    a.account_name,
    a.statement_section,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_dollars,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct,
    CASE 
        WHEN ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
               SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
               NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) >= 0.10 
        THEN 'UNFAVORABLE_OVER_SPEND'
        WHEN ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
               SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
               NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) <= -0.10 
        THEN 'UNDER_BUDGET_SAVING'
        ELSE 'WITHIN_TOLERANCE'
    END AS alert_category
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_department dept ON f.department_key = dept.department_key
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY d.year, d.month_num, d.year_month, dept.department_name, dept.cost_center_code, a.account_number, a.account_name, a.statement_section
HAVING ABS(variance_pct) >= 10.00;
