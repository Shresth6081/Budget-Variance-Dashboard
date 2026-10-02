USE budget_variance_db;

SELECT 
    scenario,
    COUNT(*) AS total_records,
    SUM(amount) AS total_amount,
    AVG(amount) AS average_amount,
    MIN(amount) AS min_amount,
    MAX(amount) AS max_amount
FROM fact_financials
GROUP BY scenario;

SELECT 
    d.year,
    d.month_num,
    d.month_name,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_amount,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_num, d.month_name
ORDER BY d.year, d.month_num;

SELECT 
    dept.department_name,
    dept.division,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_amount,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct
FROM fact_financials f
JOIN dim_department dept ON f.department_key = dept.department_key
GROUP BY dept.department_name, dept.division
ORDER BY variance_pct DESC;

SELECT 
    a.statement_section,
    a.account_category,
    a.account_number,
    a.account_name,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_amount,
    ROUND(
        ((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0)) * 100, 
        2
    ) AS variance_pct,
    CASE 
        WHEN ABS(((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
                   SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
                   NULLIF(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 0))) >= 0.10 
        THEN 'FLAGGED FOR REVIEW' 
        ELSE 'NORMAL' 
    END AS review_status
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY a.statement_section, a.account_category, a.account_number, a.account_name
ORDER BY a.statement_section, ABS(variance_pct) DESC;

SELECT 
    d.year,
    d.month_num,
    dept.department_name,
    a.account_number,
    a.account_name,
    a.statement_section,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amount,
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amount,
    SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
    SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS variance_amount,
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
GROUP BY d.year, d.month_num, dept.department_name, a.account_number, a.account_name, a.statement_section
HAVING ABS(variance_pct) >= 10.00
ORDER BY d.year, d.month_num, ABS(variance_pct) DESC;

WITH monthly_totals AS (
    SELECT 
        d.year,
        d.month_num,
        SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amt,
        SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END) AS budget_amt
    FROM fact_financials f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month_num
)
SELECT 
    year,
    month_num,
    actual_amt,
    SUM(actual_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_ytd,
    budget_amt,
    SUM(budget_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_ytd,
    (SUM(actual_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) - 
     SUM(budget_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)) AS variance_ytd,
    ROUND(
        ((SUM(actual_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) - 
          SUM(budget_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)) / 
          NULLIF(SUM(budget_amt) OVER (PARTITION BY year ORDER BY month_num ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0)) * 100, 
        2
    ) AS variance_ytd_pct
FROM monthly_totals
ORDER BY year, month_num;

WITH monthly_totals AS (
    SELECT 
        d.year,
        d.month_num,
        SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) AS actual_amt
    FROM fact_financials f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month_num
)
SELECT 
    year,
    month_num,
    actual_amt,
    LAG(actual_amt, 1) OVER (ORDER BY year, month_num) AS prior_month_actual,
    (actual_amt - LAG(actual_amt, 1) OVER (ORDER BY year, month_num)) AS mom_variance_amount,
    ROUND(
        ((actual_amt - LAG(actual_amt, 1) OVER (ORDER BY year, month_num)) / 
          NULLIF(LAG(actual_amt, 1) OVER (ORDER BY year, month_num), 0)) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_totals
ORDER BY year, month_num;
