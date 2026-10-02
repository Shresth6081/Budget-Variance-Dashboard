import sqlite3
import pandas as pd

conn = sqlite3.connect(':memory:')

df_dept = pd.read_csv('data/dim_department.csv')
df_acct = pd.read_csv('data/dim_account.csv')
df_date = pd.read_csv('data/dim_date.csv')
df_fact = pd.read_csv('data/fact_financials.csv')

df_dept.to_sql('dim_department', conn, index=False, if_exists='replace')
df_acct.to_sql('dim_account', conn, index=False, if_exists='replace')
df_date.to_sql('dim_date', conn, index=False, if_exists='replace')
df_fact.to_sql('fact_financials', conn, index=False, if_exists='replace')

query_summary = """
SELECT 
    scenario,
    COUNT(*) AS records,
    ROUND(SUM(amount), 2) AS total_amount
FROM fact_financials
GROUP BY scenario
"""
print("=== SCENARIO TOTALS ===")
print(pd.read_sql_query(query_summary, conn).to_string(index=False))

query_statement = """
SELECT 
    a.statement_section,
    ROUND(SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END), 2) AS actual,
    ROUND(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 2) AS budget,
    ROUND(SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 2) AS variance_dollars,
    ROUND(((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
            SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
            SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) * 100, 2) AS variance_pct
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY a.statement_section
"""
print("\n=== P&L SECTION RECONCILIATION ===")
print(pd.read_sql_query(query_statement, conn).to_string(index=False))

query_flags = """
SELECT 
    d.year,
    d.month_num,
    dept.department_name,
    a.account_name,
    ROUND(SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END), 2) AS actual,
    ROUND(SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 2) AS budget,
    ROUND(SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
          SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END), 2) AS variance_dollars,
    ROUND(((SUM(CASE WHEN f.scenario = 'Actual' THEN f.amount ELSE 0 END) - 
            SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) / 
            SUM(CASE WHEN f.scenario = 'Budget' THEN f.amount ELSE 0 END)) * 100, 2) AS variance_pct
FROM fact_financials f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_department dept ON f.department_key = dept.department_key
JOIN dim_account a ON f.account_key = a.account_key
GROUP BY d.year, d.month_num, dept.department_name, a.account_name
HAVING ABS(variance_pct) >= 10.0
ORDER BY d.year, d.month_num
"""
print("\n=== FLAGGED VARIANCES (>= 10% THRESHOLD) ===")
print(pd.read_sql_query(query_flags, conn).to_string(index=False))
conn.close()
