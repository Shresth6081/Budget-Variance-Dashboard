# Data Dictionary

## Schema Architecture: Star Schema

### dim_department
| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| department_key | INT | Primary Key | Unique surrogate key for department |
| department_id | VARCHAR(20) | Business Key | Operational department identifier |
| department_name | VARCHAR(100) | Attribute | Full functional department name |
| division | VARCHAR(50) | Attribute | Higher-level organizational division |
| cost_center_code | VARCHAR(20) | Attribute | Cost center accounting code |
| head_of_department | VARCHAR(100) | Attribute | Executive leader name |

### dim_account
| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| account_key | INT | Primary Key | Unique surrogate key for general ledger account |
| account_number | VARCHAR(20) | Business Key | Standard chart of accounts number |
| account_name | VARCHAR(100) | Attribute | Account descriptive name |
| account_category | VARCHAR(50) | Attribute | Category grouping |
| sub_category | VARCHAR(50) | Attribute | Specific operational category |
| statement_section | VARCHAR(50) | Attribute | P&L classification |
| normal_balance | VARCHAR(10) | Attribute | Accounting normal balance |

### dim_date
| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| date_key | INT | Primary Key | Date key in YYYYMMDD integer format |
| full_date | DATE | Attribute | Calendar date |
| year | INT | Attribute | Calendar year |
| quarter | INT | Attribute | Calendar quarter |
| month_num | INT | Attribute | Month integer |
| month_name | VARCHAR(20) | Attribute | Full month name |
| month_short | VARCHAR(10) | Attribute | Abbreviated month name |
| year_month | VARCHAR(10) | Attribute | Year-Month string identifier |
| day | INT | Attribute | Day of month |
| fiscal_year | VARCHAR(10) | Attribute | Fiscal year identifier |
| fiscal_quarter | VARCHAR(10) | Attribute | Fiscal quarter identifier |
| is_month_end | TINYINT(1) | Attribute | Flag indicating month end date |

### fact_financials
| Column Name | Data Type | Key Type | Description |
|---|---|---|---|
| transaction_key | BIGINT | Primary Key | Unique transaction record key |
| date_key | INT | Foreign Key | References dim_date.date_key |
| department_key | INT | Foreign Key | References dim_department.department_key |
| account_key | INT | Foreign Key | References dim_account.account_key |
| scenario | VARCHAR(20) | Attribute | Indicator for Actual vs Budget data |
| amount | DECIMAL(15,2) | Measure | Financial monetary amount |
