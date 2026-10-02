USE budget_variance_db;

DROP PROCEDURE IF EXISTS sp_get_department_monthly_variance;
DROP PROCEDURE IF EXISTS sp_get_executive_pl_summary;
DROP PROCEDURE IF EXISTS sp_flag_variance_exceptions;

DELIMITER $$

CREATE PROCEDURE sp_get_department_monthly_variance(
    IN p_year INT,
    IN p_department_id VARCHAR(20)
)
BEGIN
    SELECT 
        d.year,
        d.month_num,
        d.month_name,
        dept.department_id,
        dept.department_name,
        a.statement_section,
        a.account_name,
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
    JOIN dim_department dept ON f.department_key = dept.department_key
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE d.year = p_year
      AND (p_department_id IS NULL OR dept.department_id = p_department_id)
    GROUP BY d.year, d.month_num, d.month_name, dept.department_id, dept.department_name, a.statement_section, a.account_name
    ORDER BY d.month_num, dept.department_name, a.statement_section;
END$$

CREATE PROCEDURE sp_get_executive_pl_summary(
    IN p_year INT
)
BEGIN
    SELECT 
        d.year,
        d.month_num,
        d.month_short,
        SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) AS actual_revenue,
        SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) AS budget_revenue,
        SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section = 'COGS' THEN f.amount ELSE 0 END) AS actual_cogs,
        SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section = 'COGS' THEN f.amount ELSE 0 END) AS budget_cogs,
        SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section = 'OPEX' THEN f.amount ELSE 0 END) AS actual_opex,
        SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section = 'OPEX' THEN f.amount ELSE 0 END) AS budget_opex,
        (SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) -
         SUM(CASE WHEN f.scenario = 'Actual' AND a.statement_section IN ('COGS', 'OPEX') THEN f.amount ELSE 0 END)) AS actual_net_profit,
        (SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section = 'Revenue' THEN f.amount ELSE 0 END) -
         SUM(CASE WHEN f.scenario = 'Budget' AND a.statement_section IN ('COGS', 'OPEX') THEN f.amount ELSE 0 END)) AS budget_net_profit
    FROM fact_financials f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE d.year = p_year
    GROUP BY d.year, d.month_num, d.month_short
    ORDER BY d.month_num;
END$$

CREATE PROCEDURE sp_flag_variance_exceptions(
    IN p_year INT,
    IN p_threshold_pct DECIMAL(5,2)
)
BEGIN
    SELECT 
        d.year,
        d.month_num,
        d.month_name,
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
        ) AS variance_pct
    FROM fact_financials f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_department dept ON f.department_key = dept.department_key
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE d.year = p_year
    GROUP BY d.year, d.month_num, d.month_name, dept.department_name, dept.cost_center_code, a.account_number, a.account_name, a.statement_section
    HAVING ABS(variance_pct) >= p_threshold_pct
    ORDER BY ABS(variance_pct) DESC;
END$$

DELIMITER ;
