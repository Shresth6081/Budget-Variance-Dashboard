import unittest
import pandas as pd

class TestDataWarehouseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df_dept = pd.read_csv('data/dim_department.csv')
        cls.df_acct = pd.read_csv('data/dim_account.csv')
        cls.df_date = pd.read_csv('data/dim_date.csv')
        cls.df_fact = pd.read_csv('data/fact_financials.csv')

    def test_dimensions_not_empty(self):
        self.assertGreater(len(self.df_dept), 0)
        self.assertGreater(len(self.df_acct), 0)
        self.assertGreater(len(self.df_date), 0)
        self.assertGreater(len(self.df_fact), 0)

    def test_department_primary_keys_unique(self):
        self.assertEqual(len(self.df_dept), self.df_dept['department_key'].nunique())

    def test_account_primary_keys_unique(self):
        self.assertEqual(len(self.df_acct), self.df_acct['account_key'].nunique())

    def test_date_primary_keys_unique(self):
        self.assertEqual(len(self.df_date), self.df_date['date_key'].nunique())

    def test_foreign_key_referential_integrity(self):
        dept_keys = set(self.df_dept['department_key'])
        acct_keys = set(self.df_acct['account_key'])
        date_keys = set(self.df_date['date_key'])

        fact_dept_keys = set(self.df_fact['department_key'])
        fact_acct_keys = set(self.df_fact['account_key'])
        fact_date_keys = set(self.df_fact['date_key'])

        self.assertTrue(fact_dept_keys.issubset(dept_keys))
        self.assertTrue(fact_acct_keys.issubset(acct_keys))
        self.assertTrue(fact_date_keys.issubset(date_keys))

    def test_scenario_consistency(self):
        scenarios = set(self.df_fact['scenario'].unique())
        self.assertEqual(scenarios, {'Actual', 'Budget'})

        actual_count = len(self.df_fact[self.df_fact['scenario'] == 'Actual'])
        budget_count = len(self.df_fact[self.df_fact['scenario'] == 'Budget'])
        self.assertEqual(actual_count, budget_count)

    def test_no_null_amounts(self):
        self.assertEqual(self.df_fact['amount'].isnull().sum(), 0)
        self.assertTrue((self.df_fact['amount'] >= 0).all())

    def test_statement_sections_valid(self):
        valid_sections = {'Revenue', 'COGS', 'OPEX'}
        acct_sections = set(self.df_acct['statement_section'].unique())
        self.assertTrue(acct_sections.issubset(valid_sections))

if __name__ == '__main__':
    unittest.main()
