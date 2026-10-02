import csv
import datetime
import os
import random

os.makedirs('data', exist_ok=True)
os.makedirs('sql', exist_ok=True)

random.seed(42)

departments = [
    {"department_key": 1, "department_id": "DEP-100", "department_name": "Executive & General", "division": "Corporate", "cost_center_code": "CC-1000", "head_of_department": "Sarah Jenkins"},
    {"department_key": 2, "department_id": "DEP-200", "department_name": "Sales & Distribution", "division": "Commercial", "cost_center_code": "CC-2000", "head_of_department": "Michael Chang"},
    {"department_key": 3, "department_id": "DEP-300", "department_name": "Marketing & Growth", "division": "Commercial", "cost_center_code": "CC-3000", "head_of_department": "Elena Rostova"},
    {"department_key": 4, "department_id": "DEP-400", "department_name": "Engineering & Technology", "division": "R&D", "cost_center_code": "CC-4000", "head_of_department": "David Kim"},
    {"department_key": 5, "department_id": "DEP-500", "department_name": "Customer Support & Success", "division": "Operations", "cost_center_code": "CC-5000", "head_of_department": "Amina Patel"},
    {"department_key": 6, "department_id": "DEP-600", "department_name": "Operations & Logistics", "division": "Operations", "cost_center_code": "CC-6000", "head_of_department": "Robert Garcia"}
]

accounts = [
    {"account_key": 1, "account_number": "4010", "account_name": "Product Subscription Revenue", "account_category": "Revenue", "sub_category": "Recurring Revenue", "statement_section": "Revenue", "normal_balance": "Credit"},
    {"account_key": 2, "account_number": "4020", "account_name": "Professional Services Revenue", "account_category": "Revenue", "sub_category": "Services Revenue", "statement_section": "Revenue", "normal_balance": "Credit"},
    {"account_key": 3, "account_number": "4030", "account_name": "Enterprise License Revenue", "account_category": "Revenue", "sub_category": "License Revenue", "statement_section": "Revenue", "normal_balance": "Credit"},
    {"account_key": 4, "account_number": "5010", "account_name": "Hosting & Cloud Infrastructure", "account_category": "Cost of Goods Sold", "sub_category": "Direct Tech Costs", "statement_section": "COGS", "normal_balance": "Debit"},
    {"account_key": 5, "account_number": "5020", "account_name": "Direct Labor - Customer Support", "account_category": "Cost of Goods Sold", "sub_category": "Direct Labor", "statement_section": "COGS", "normal_balance": "Debit"},
    {"account_key": 6, "account_number": "5030", "account_name": "Third-Party Merchant Fees", "account_category": "Cost of Goods Sold", "sub_category": "Payment Processing", "statement_section": "COGS", "normal_balance": "Debit"},
    {"account_key": 7, "account_number": "6010", "account_name": "Salaries & Wages", "account_category": "Operating Expenses", "sub_category": "Compensation", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 8, "account_number": "6020", "account_name": "Employee Benefits & Health", "account_category": "Operating Expenses", "sub_category": "Compensation", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 9, "account_number": "6030", "account_name": "Digital Advertising & Paid Media", "account_category": "Operating Expenses", "sub_category": "Marketing", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 10, "account_number": "6040", "account_name": "Events & Trade Shows", "account_category": "Operating Expenses", "sub_category": "Marketing", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 11, "account_number": "6050", "account_name": "SaaS & Software Subscriptions", "account_category": "Operating Expenses", "sub_category": "Technology", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 12, "account_number": "6060", "account_name": "Office Rent & Utilities", "account_category": "Operating Expenses", "sub_category": "Facilities", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 13, "account_number": "6070", "account_name": "Travel & Entertainment", "account_category": "Operating Expenses", "sub_category": "General Travel", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 14, "account_number": "6080", "account_name": "Legal & Professional Advisory", "account_category": "Operating Expenses", "sub_category": "Advisory", "statement_section": "OPEX", "normal_balance": "Debit"},
    {"account_key": 15, "account_number": "6090", "account_name": "Recruiting & Talent Acquisition", "account_category": "Operating Expenses", "sub_category": "Human Resources", "statement_section": "OPEX", "normal_balance": "Debit"}
]

start_date = datetime.date(2025, 1, 1)
end_date = datetime.date(2026, 12, 31)

date_records = []
cur_date = start_date
while cur_date <= end_date:
    date_key = int(cur_date.strftime("%Y%m%d"))
    year = cur_date.year
    month_num = cur_date.month
    day = cur_date.day
    quarter = int((month_num - 1) / 3) + 1
    month_name = cur_date.strftime("%B")
    month_short = cur_date.strftime("%b")
    year_month = cur_date.strftime("%Y-%m")
    fiscal_year = f"FY{year}"
    fiscal_quarter = f"FQ{quarter}"
    is_month_end = 1 if (cur_date + datetime.timedelta(days=1)).month != month_num else 0
    date_records.append({
        "date_key": date_key,
        "full_date": cur_date.strftime("%Y-%m-%d"),
        "year": year,
        "quarter": quarter,
        "month_num": month_num,
        "month_name": month_name,
        "month_short": month_short,
        "year_month": year_month,
        "day": day,
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "is_month_end": is_month_end
    })
    cur_date += datetime.timedelta(days=1)

with open('data/dim_department.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(departments[0].keys()))
    writer.writeheader()
    writer.writerows(departments)

with open('data/dim_account.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(accounts[0].keys()))
    writer.writeheader()
    writer.writerows(accounts)

with open('data/dim_date.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(date_records[0].keys()))
    writer.writeheader()
    writer.writerows(date_records)

base_budget_matrix = {
    (1, 7): 45000,
    (1, 8): 9000,
    (1, 11): 8000,
    (1, 12): 22000,
    (1, 14): 18000,
    (2, 1): 280000,
    (2, 2): 60000,
    (2, 3): 120000,
    (2, 7): 110000,
    (2, 8): 22000,
    (2, 13): 25000,
    (2, 15): 8000,
    (3, 7): 65000,
    (3, 8): 13000,
    (3, 9): 85000,
    (3, 10): 30000,
    (3, 11): 12000,
    (4, 4): 40000,
    (4, 7): 160000,
    (4, 8): 32000,
    (4, 11): 28000,
    (4, 15): 15000,
    (5, 2): 30000,
    (5, 5): 25000,
    (5, 6): 12000,
    (5, 7): 55000,
    (5, 8): 11000,
    (5, 11): 6000,
    (6, 7): 48000,
    (6, 8): 9600,
    (6, 12): 15000,
    (6, 13): 6000,
    (6, 14): 5000
}

months_list = []
cur = datetime.date(2025, 1, 1)
while cur <= datetime.date(2026, 12, 1):
    last_day_of_month = (datetime.date(cur.year + (1 if cur.month == 12 else 0), 1 if cur.month == 12 else cur.month + 1, 1) - datetime.timedelta(days=1))
    date_key = int(last_day_of_month.strftime("%Y%m%d"))
    months_list.append((cur.year, cur.month, date_key))
    cur = datetime.date(cur.year + (1 if cur.month == 12 else 0), 1 if cur.month == 12 else cur.month + 1, 1)

fact_rows = []
tx_id = 1

variance_injectors = {
    (2025, 3, 3, 9): 1.18,
    (2025, 5, 2, 1): 1.14,
    (2025, 7, 4, 4): 1.25,
    (2025, 8, 1, 14): 1.35,
    (2025, 11, 3, 10): 0.82,
    (2025, 12, 2, 3): 1.22,
    (2026, 2, 4, 11): 1.16,
    (2026, 4, 2, 13): 1.28,
    (2026, 6, 3, 9): 0.84,
    (2026, 8, 4, 4): 1.22,
    (2026, 9, 2, 2): 0.85,
    (2026, 10, 1, 14): 1.40,
    (2026, 11, 5, 5): 1.19,
    (2026, 12, 2, 1): 1.15
}

for year, month, date_key in months_list:
    growth_multiplier = 1.0 + ((year - 2025) * 12 + (month - 1)) * 0.015
    for (dept_key, acct_key), base_amt in base_budget_matrix.items():
        budget_amt = round(base_amt * growth_multiplier, 2)
        fact_rows.append({
            "transaction_key": tx_id,
            "date_key": date_key,
            "department_key": dept_key,
            "account_key": acct_key,
            "scenario": "Budget",
            "amount": budget_amt
        })
        tx_id += 1

        variance_factor = variance_injectors.get((year, month, dept_key, acct_key), None)
        if variance_factor is None:
            noise = random.uniform(-0.06, 0.06)
            variance_factor = 1.0 + noise

        actual_amt = round(budget_amt * variance_factor, 2)
        fact_rows.append({
            "transaction_key": tx_id,
            "date_key": date_key,
            "department_key": dept_key,
            "account_key": acct_key,
            "scenario": "Actual",
            "amount": actual_amt
        })
        tx_id += 1

with open('data/fact_financials.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(fact_rows[0].keys()))
    writer.writeheader()
    writer.writerows(fact_rows)

schema_sql = """CREATE DATABASE IF NOT EXISTS budget_variance_db;
USE budget_variance_db;

DROP TABLE IF EXISTS fact_financials;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_account;
DROP TABLE IF EXISTS dim_department;

CREATE TABLE dim_department (
    department_key INT NOT NULL,
    department_id VARCHAR(20) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    division VARCHAR(50) NOT NULL,
    cost_center_code VARCHAR(20) NOT NULL,
    head_of_department VARCHAR(100) NOT NULL,
    PRIMARY KEY (department_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_account (
    account_key INT NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    statement_section VARCHAR(50) NOT NULL,
    normal_balance VARCHAR(10) NOT NULL,
    PRIMARY KEY (account_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE dim_date (
    date_key INT NOT NULL,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month_num INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    month_short VARCHAR(10) NOT NULL,
    year_month VARCHAR(10) NOT NULL,
    day INT NOT NULL,
    fiscal_year VARCHAR(10) NOT NULL,
    fiscal_quarter VARCHAR(10) NOT NULL,
    is_month_end TINYINT(1) NOT NULL,
    PRIMARY KEY (date_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_financials (
    transaction_key BIGINT NOT NULL AUTO_INCREMENT,
    date_key INT NOT NULL,
    department_key INT NOT NULL,
    account_key INT NOT NULL,
    scenario VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    PRIMARY KEY (transaction_key),
    CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES dim_date (date_key),
    CONSTRAINT fk_fact_dept FOREIGN KEY (department_key) REFERENCES dim_department (department_key),
    CONSTRAINT fk_fact_acct FOREIGN KEY (account_key) REFERENCES dim_account (account_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_fact_scenario_date ON fact_financials (scenario, date_key);
CREATE INDEX idx_fact_dept_acct ON fact_financials (department_key, account_key);
"""

with open('sql/schema.sql', 'w', encoding='utf-8') as f:
    f.write(schema_sql)

with open('sql/seed_data.sql', 'w', encoding='utf-8') as f:
    f.write("USE budget_variance_db;\n\n")
    
    f.write("INSERT INTO dim_department (department_key, department_id, department_name, division, cost_center_code, head_of_department) VALUES\n")
    dept_lines = []
    for d in departments:
        dept_lines.append(f"({d['department_key']}, '{d['department_id']}', '{d['department_name']}', '{d['division']}', '{d['cost_center_code']}', '{d['head_of_department']}')")
    f.write(",\n".join(dept_lines) + ";\n\n")

    f.write("INSERT INTO dim_account (account_key, account_number, account_name, account_category, sub_category, statement_section, normal_balance) VALUES\n")
    acct_lines = []
    for a in accounts:
        acct_lines.append(f"({a['account_key']}, '{a['account_number']}', '{a['account_name']}', '{a['account_category']}', '{a['sub_category']}', '{a['statement_section']}', '{a['normal_balance']}')")
    f.write(",\n".join(acct_lines) + ";\n\n")

    f.write("INSERT INTO dim_date (date_key, full_date, year, quarter, month_num, month_name, month_short, year_month, day, fiscal_year, fiscal_quarter, is_month_end) VALUES\n")
    date_lines = []
    for d in date_records:
        date_lines.append(f"({d['date_key']}, '{d['full_date']}', {d['year']}, {d['quarter']}, {d['month_num']}, '{d['month_name']}', '{d['month_short']}', '{d['year_month']}', {d['day']}, '{d['fiscal_year']}', '{d['fiscal_quarter']}', {d['is_month_end']})")
    f.write(",\n".join(date_lines) + ";\n\n")

    chunk_size = 500
    for i in range(0, len(fact_rows), chunk_size):
        chunk = fact_rows[i:i + chunk_size]
        f.write("INSERT INTO fact_financials (transaction_key, date_key, department_key, account_key, scenario, amount) VALUES\n")
        fact_lines = []
        for r in chunk:
            fact_lines.append(f"({r['transaction_key']}, {r['date_key']}, {r['department_key']}, {r['account_key']}, '{r['scenario']}', {r['amount']})")
        f.write(",\n".join(fact_lines) + ";\n\n")
