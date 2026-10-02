CREATE DATABASE IF NOT EXISTS budget_variance_db;
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
