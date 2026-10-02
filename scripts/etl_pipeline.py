import csv
import os
import json
import sqlite3
from datetime import datetime

class FinancialETLPipeline:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.stats = {
            "departments_loaded": 0,
            "accounts_loaded": 0,
            "dates_loaded": 0,
            "facts_loaded": 0,
            "errors": []
        }

    def extract_dimensions(self):
        dept_path = os.path.join(self.data_dir, 'dim_department.csv')
        acct_path = os.path.join(self.data_dir, 'dim_account.csv')
        date_path = os.path.join(self.data_dir, 'dim_date.csv')

        departments = []
        with open(dept_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                departments.append(row)

        accounts = []
        with open(acct_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)

        dates = []
        with open(date_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dates.append(row)

        return departments, accounts, dates

    def extract_facts(self):
        fact_path = os.path.join(self.data_dir, 'fact_financials.csv')
        facts = []
        with open(fact_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                facts.append(row)
        return facts

    def validate_and_transform(self, departments, accounts, dates, facts):
        valid_dept_keys = {int(d['department_key']) for d in departments}
        valid_acct_keys = {int(a['account_key']) for a in accounts}
        valid_date_keys = {int(d['date_key']) for d in dates}

        transformed_facts = []
        for idx, row in enumerate(facts):
            try:
                date_key = int(row['date_key'])
                dept_key = int(row['department_key'])
                acct_key = int(row['account_key'])
                amount = float(row['amount'])
                scenario = row['scenario'].strip()

                if date_key not in valid_date_keys:
                    self.stats["errors"].append(f"Invalid date_key {date_key} at row {idx}")
                    continue

                if dept_key not in valid_dept_keys:
                    self.stats["errors"].append(f"Invalid dept_key {dept_key} at row {idx}")
                    continue

                if acct_key not in valid_acct_keys:
                    self.stats["errors"].append(f"Invalid acct_key {acct_key} at row {idx}")
                    continue

                if scenario not in ('Actual', 'Budget'):
                    self.stats["errors"].append(f"Unknown scenario {scenario} at row {idx}")
                    continue

                transformed_facts.append({
                    "transaction_key": int(row.get('transaction_key', idx + 1)),
                    "date_key": date_key,
                    "department_key": dept_key,
                    "account_key": acct_key,
                    "scenario": scenario,
                    "amount": round(amount, 2)
                })
            except Exception as e:
                self.stats["errors"].append(str(e))

        return transformed_facts

    def run_pipeline(self, target_sqlite_db=None):
        departments, accounts, dates = self.extract_dimensions()
        raw_facts = self.extract_facts()

        transformed_facts = self.validate_and_transform(departments, accounts, dates, raw_facts)

        self.stats["departments_loaded"] = len(departments)
        self.stats["accounts_loaded"] = len(accounts)
        self.stats["dates_loaded"] = len(dates)
        self.stats["facts_loaded"] = len(transformed_facts)

        if target_sqlite_db:
            conn = sqlite3.connect(target_sqlite_db)
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS etl_log (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                facts_count INTEGER,
                errors_count INTEGER,
                status TEXT
            )
            """)
            status = "SUCCESS" if len(self.stats["errors"]) == 0 else "PARTIAL_SUCCESS"
            cur.execute(
                "INSERT INTO etl_log (timestamp, facts_count, errors_count, status) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), self.stats["facts_loaded"], len(self.stats["errors"]), status)
            )
            conn.commit()
            conn.close()

        return self.stats

if __name__ == '__main__':
    pipeline = FinancialETLPipeline()
    results = pipeline.run_pipeline(target_sqlite_db='data/etl_staging.db')
    print(json.dumps(results, indent=2))
