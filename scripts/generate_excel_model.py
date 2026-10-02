import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

df_dept = pd.read_csv('data/dim_department.csv')
df_acct = pd.read_csv('data/dim_account.csv')
df_date = pd.read_csv('data/dim_date.csv')
df_fact = pd.read_csv('data/fact_financials.csv')

df_merged = df_fact.merge(df_dept, on='department_key').merge(df_acct, on='account_key').merge(df_date, on='date_key')

wb = openpyxl.Workbook()
ws_summary = wb.active
ws_summary.title = "Executive P&L Summary"

ws_dept = wb.create_sheet(title="Department Breakdown")
ws_exceptions = wb.create_sheet(title="Variance Audit (>10%)")
ws_data = wb.create_sheet(title="Financial Model Data")

header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
accent_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
alert_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
alert_font = Font(name="Calibri", size=11, bold=True, color="C00000")
total_font = Font(name="Calibri", size=11, bold=True)
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

ws_summary.views.sheetView[0].showGridLines = True
ws_dept.views.sheetView[0].showGridLines = True
ws_exceptions.views.sheetView[0].showGridLines = True
ws_data.views.sheetView[0].showGridLines = True

ws_summary["A1"] = "EXECUTIVE P&L BUDGET VS ACTUAL VARIANCE MODEL"
ws_summary["A1"].font = Font(name="Calibri", size=16, bold=True, color="1F4E78")
ws_summary["A2"] = "Fiscal Years 2025 - 2026 Consolidated Overview"
ws_summary["A2"].font = Font(name="Calibri", size=11, italic=True, color="595959")

summary_headers = ["P&L Line Item", "Statement Section", "Actuals ($)", "Budget ($)", "Variance ($)", "Variance (%)", "Threshold Flag"]
for col_num, header in enumerate(summary_headers, 1):
    cell = ws_summary.cell(row=4, column=col_num)
    cell.value = header
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

acct_pivot = df_merged.pivot_table(
    index=['statement_section', 'account_name', 'account_number'],
    columns='scenario',
    values='amount',
    aggfunc='sum'
).reset_index()

current_row = 5
for _, row in acct_pivot.iterrows():
    ws_summary.cell(row=current_row, column=1, value=f"{row['account_number']} - {row['account_name']}")
    ws_summary.cell(row=current_row, column=2, value=row['statement_section'])
    
    cell_act = ws_summary.cell(row=current_row, column=3, value=row['Actual'])
    cell_act.number_format = "$#,##0"
    
    cell_bud = ws_summary.cell(row=current_row, column=4, value=row['Budget'])
    cell_bud.number_format = "$#,##0"
    
    cell_var = ws_summary.cell(row=current_row, column=5, value=f"=C{current_row}-D{current_row}")
    cell_var.number_format = "$#,##0;($#,##0);\"-\""
    
    cell_pct = ws_summary.cell(row=current_row, column=6, value=f"=IF(D{current_row}=0, 0, E{current_row}/D{current_row})")
    cell_pct.number_format = "+0.0%;-0.0%;0.0%"
    
    cell_flag = ws_summary.cell(row=current_row, column=7, value=f"=IF(ABS(F{current_row})>=0.10, \"FLAGGED (>10%)\", \"ON TRACK\")")
    
    for c in range(1, 8):
        ws_summary.cell(row=current_row, column=c).border = thin_border
    current_row += 1

total_row = current_row
ws_summary.cell(row=total_row, column=1, value="TOTAL P&L SUMMARY").font = total_font
ws_summary.cell(row=total_row, column=2, value="All Sections").font = total_font
cell_tot_act = ws_summary.cell(row=total_row, column=3, value=f"=SUM(C5:C{total_row-1})")
cell_tot_act.font = total_font
cell_tot_act.number_format = "$#,##0"
cell_tot_bud = ws_summary.cell(row=total_row, column=4, value=f"=SUM(D5:D{total_row-1})")
cell_tot_bud.font = total_font
cell_tot_bud.number_format = "$#,##0"
cell_tot_var = ws_summary.cell(row=total_row, column=5, value=f"=C{total_row}-D{total_row}")
cell_tot_var.font = total_font
cell_tot_var.number_format = "$#,##0;($#,##0);\"-\""
cell_tot_pct = ws_summary.cell(row=total_row, column=6, value=f"=E{total_row}/D{total_row}")
cell_tot_pct.font = total_font
cell_tot_pct.number_format = "+0.0%;-0.0%;0.0%"
ws_summary.cell(row=total_row, column=7, value=f"=IF(ABS(F{total_row})>=0.10, \"FLAGGED (>10%)\", \"ON TRACK\")").font = total_font

for c in range(1, 8):
    ws_summary.cell(row=total_row, column=c).fill = accent_fill
    ws_summary.cell(row=total_row, column=c).border = thin_border

ws_dept["A1"] = "DEPARTMENTAL VARIANCE PERFORMANCE"
ws_dept["A1"].font = Font(name="Calibri", size=16, bold=True, color="1F4E78")

dept_headers = ["Department ID", "Department Name", "Division", "Cost Center", "Actual ($)", "Budget ($)", "Variance ($)", "Variance (%)", "Review Status"]
for col_num, header in enumerate(dept_headers, 1):
    cell = ws_dept.cell(row=4, column=col_num)
    cell.value = header
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

dept_pivot = df_merged.pivot_table(
    index=['department_id', 'department_name', 'division', 'cost_center_code'],
    columns='scenario',
    values='amount',
    aggfunc='sum'
).reset_index()

dept_row = 5
for _, row in dept_pivot.iterrows():
    ws_dept.cell(row=dept_row, column=1, value=row['department_id'])
    ws_dept.cell(row=dept_row, column=2, value=row['department_name'])
    ws_dept.cell(row=dept_row, column=3, value=row['division'])
    ws_dept.cell(row=dept_row, column=4, value=row['cost_center_code'])
    
    cell_a = ws_dept.cell(row=dept_row, column=5, value=row['Actual'])
    cell_a.number_format = "$#,##0"
    
    cell_b = ws_dept.cell(row=dept_row, column=6, value=row['Budget'])
    cell_b.number_format = "$#,##0"
    
    cell_v = ws_dept.cell(row=dept_row, column=7, value=f"=E{dept_row}-F{dept_row}")
    cell_v.number_format = "$#,##0;($#,##0);\"-\""
    
    cell_p = ws_dept.cell(row=dept_row, column=8, value=f"=G{dept_row}/F{dept_row}")
    cell_p.number_format = "+0.0%;-0.0%;0.0%"
    
    ws_dept.cell(row=dept_row, column=9, value=f"=IF(ABS(H{dept_row})>=0.10, \"NEEDS REVIEW\", \"ACCEPTABLE\")")
    
    for c in range(1, 10):
        ws_dept.cell(row=dept_row, column=c).border = thin_border
    dept_row += 1

ws_exceptions["A1"] = "TRANSACTIONS FLAGGED FOR VARIANCE AUDIT (>= 10% THRESHOLD)"
ws_exceptions["A1"].font = Font(name="Calibri", size=16, bold=True, color="C00000")

audit_headers = ["Year", "Month", "Department", "Account Number", "Account Name", "Actual ($)", "Budget ($)", "Variance ($)", "Variance (%)", "Audit Alert"]
for col_num, header in enumerate(audit_headers, 1):
    cell = ws_exceptions.cell(row=4, column=col_num)
    cell.value = header
    cell.font = header_font
    cell.fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")

monthly_acct = df_merged.pivot_table(
    index=['year', 'month_num', 'month_name', 'department_name', 'account_number', 'account_name'],
    columns='scenario',
    values='amount',
    aggfunc='sum'
).reset_index()

monthly_acct['var_dollars'] = monthly_acct['Actual'] - monthly_acct['Budget']
monthly_acct['var_pct'] = monthly_acct['var_dollars'] / monthly_acct['Budget']

flagged_df = monthly_acct[monthly_acct['var_pct'].abs() >= 0.10].sort_values(by=['year', 'month_num'])

audit_row = 5
for _, row in flagged_df.iterrows():
    ws_exceptions.cell(row=audit_row, column=1, value=int(row['year']))
    ws_exceptions.cell(row=audit_row, column=2, value=f"{int(row['month_num'])} ({row['month_name']})")
    ws_exceptions.cell(row=audit_row, column=3, value=row['department_name'])
    ws_exceptions.cell(row=audit_row, column=4, value=row['account_number'])
    ws_exceptions.cell(row=audit_row, column=5, value=row['account_name'])
    
    c_a = ws_exceptions.cell(row=audit_row, column=6, value=row['Actual'])
    c_a.number_format = "$#,##0"
    
    c_b = ws_exceptions.cell(row=audit_row, column=7, value=row['Budget'])
    c_b.number_format = "$#,##0"
    
    c_v = ws_exceptions.cell(row=audit_row, column=8, value=row['var_dollars'])
    c_v.number_format = "$#,##0;($#,##0);\"-\""
    
    c_p = ws_exceptions.cell(row=audit_row, column=9, value=row['var_pct'])
    c_p.number_format = "+0.0%;-0.0%;0.0%"
    
    ws_exceptions.cell(row=audit_row, column=10, value="VARIANCE >= 10%").font = alert_font
    
    for c in range(1, 11):
        ws_exceptions.cell(row=audit_row, column=c).border = thin_border
        ws_exceptions.cell(row=audit_row, column=c).fill = alert_fill
    audit_row += 1

raw_cols = list(df_merged.columns)
for col_num, header in enumerate(raw_cols, 1):
    cell = ws_data.cell(row=1, column=col_num)
    cell.value = header
    cell.font = header_font
    cell.fill = header_fill

for row_idx, record in enumerate(df_merged.to_dict(orient='records'), 2):
    for col_idx, col_name in enumerate(raw_cols, 1):
        ws_data.cell(row=row_idx, column=col_idx, value=record[col_name])

for sheet in [ws_summary, ws_dept, ws_exceptions, ws_data]:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save("data/Budget_vs_Actual_Variance_Model.xlsx")
print("Saved data/Budget_vs_Actual_Variance_Model.xlsx")
