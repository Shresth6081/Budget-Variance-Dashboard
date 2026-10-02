import json
import pandas as pd
import os

os.makedirs('web', exist_ok=True)

df_dept = pd.read_csv('data/dim_department.csv')
df_acct = pd.read_csv('data/dim_account.csv')
df_date = pd.read_csv('data/dim_date.csv')
df_fact = pd.read_csv('data/fact_financials.csv')

df_merged = df_fact.merge(df_dept, on='department_key').merge(df_acct, on='account_key').merge(df_date, on='date_key')

records = df_merged.to_dict(orient='records')
depts = df_dept.to_dict(orient='records')
accts = df_acct.to_dict(orient='records')
dates = df_date.to_dict(orient='records')

payload = {
    "departments": depts,
    "accounts": accts,
    "dates": dates,
    "records": records
}

with open('web/data.js', 'w', encoding='utf-8') as f:
    f.write("const FINANCIAL_DATA = " + json.dumps(payload, indent=2) + ";")

print("Generated web/data.js")
