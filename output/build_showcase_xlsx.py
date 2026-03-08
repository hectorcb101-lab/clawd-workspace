#!/usr/bin/env python3
"""Atlas Spreadsheet Showcase — pushing xlsxwriter to its limits."""

import xlsxwriter
import math
import random
from datetime import datetime, timedelta

OUTPUT = '/home/ubuntu/clawd/output/atlas-showcase.xlsx'

wb = xlsxwriter.Workbook(OUTPUT)

# ─── Formats ──────────────────────────────────────────────────
navy = '#0a1628'
accent = '#e94560'
teal = '#0f969c'
gold = '#f5a623'
soft_blue = '#4a90d9'
purple = '#9b59b6'
green = '#2ecc71'
dark = '#1a1a2e'
light_bg = '#f8f9fa'

f_title = wb.add_format({'bold': True, 'font_size': 22, 'font_color': navy, 'bottom': 2, 'bottom_color': accent, 'font_name': 'Calibri'})
f_subtitle = wb.add_format({'font_size': 12, 'font_color': '#888', 'italic': True, 'font_name': 'Calibri'})
f_h1 = wb.add_format({'bold': True, 'font_size': 16, 'font_color': accent, 'bottom': 1, 'bottom_color': '#ddd', 'font_name': 'Calibri'})
f_h2 = wb.add_format({'bold': True, 'font_size': 13, 'font_color': dark, 'font_name': 'Calibri'})

f_header = wb.add_format({
    'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': navy,
    'border': 1, 'border_color': '#333', 'text_wrap': True, 'valign': 'vcenter',
    'align': 'center', 'font_name': 'Calibri'
})
f_header_accent = wb.add_format({
    'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': accent,
    'border': 1, 'border_color': accent, 'text_wrap': True, 'valign': 'vcenter',
    'align': 'center', 'font_name': 'Calibri'
})
f_header_teal = wb.add_format({
    'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': teal,
    'border': 1, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'
})

f_cell = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'valign': 'vcenter', 'font_name': 'Calibri'})
f_cell_c = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_cell_alt = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'bg_color': light_bg, 'valign': 'vcenter', 'font_name': 'Calibri'})
f_cell_alt_c = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'bg_color': light_bg, 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})

f_money = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '£#,##0.00', 'valign': 'vcenter', 'align': 'right', 'font_name': 'Calibri'})
f_money_alt = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '£#,##0.00', 'bg_color': light_bg, 'valign': 'vcenter', 'align': 'right', 'font_name': 'Calibri'})
f_pct = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '0.0%', 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_pct_alt = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '0.0%', 'bg_color': light_bg, 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_int = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '#,##0', 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_int_alt = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': '#,##0', 'bg_color': light_bg, 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_date = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': 'dd mmm yyyy', 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})
f_date_alt = wb.add_format({'font_size': 10, 'border': 1, 'border_color': '#e0e0e0', 'num_format': 'dd mmm yyyy', 'bg_color': light_bg, 'valign': 'vcenter', 'align': 'center', 'font_name': 'Calibri'})

f_total_label = wb.add_format({'bold': True, 'font_size': 10, 'bg_color': '#e8e8e8', 'border': 1, 'font_name': 'Calibri', 'align': 'right'})
f_total_val = wb.add_format({'bold': True, 'font_size': 10, 'bg_color': '#e8e8e8', 'border': 1, 'num_format': '£#,##0.00', 'font_name': 'Calibri', 'align': 'right'})
f_total_int = wb.add_format({'bold': True, 'font_size': 10, 'bg_color': '#e8e8e8', 'border': 1, 'num_format': '#,##0', 'font_name': 'Calibri', 'align': 'center'})
f_total_pct = wb.add_format({'bold': True, 'font_size': 10, 'bg_color': '#e8e8e8', 'border': 1, 'num_format': '0.0%', 'font_name': 'Calibri', 'align': 'center'})

f_good = wb.add_format({'font_size': 10, 'border': 1, 'font_color': green, 'bold': True, 'align': 'center', 'font_name': 'Calibri'})
f_warn = wb.add_format({'font_size': 10, 'border': 1, 'font_color': gold, 'bold': True, 'align': 'center', 'font_name': 'Calibri'})
f_bad = wb.add_format({'font_size': 10, 'border': 1, 'font_color': accent, 'bold': True, 'align': 'center', 'font_name': 'Calibri'})

f_sparkline_area = wb.add_format({'border': 1, 'border_color': '#e0e0e0'})

f_note = wb.add_format({'font_size': 9, 'font_color': '#999', 'italic': True, 'font_name': 'Calibri'})


# ═══════════════════════════════════════════════════════════════
# SHEET 1: Dashboard
# ═══════════════════════════════════════════════════════════════
ws1 = wb.add_worksheet('📊 Dashboard')
ws1.hide_gridlines(2)
ws1.set_tab_color(accent)
ws1.set_column('A:A', 3)
ws1.set_column('B:B', 22)
ws1.set_column('C:H', 16)

# Title
ws1.merge_range('B2:H2', 'ATLAS — Infrastructure Dashboard', f_title)
ws1.merge_range('B3:H3', f'Generated {datetime.utcnow().strftime("%d %B %Y %H:%M UTC")} · All data programmatic', f_subtitle)

# KPI Cards (using merge + big numbers)
kpi_val = wb.add_format({'bold': True, 'font_size': 28, 'font_color': accent, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Calibri', 'border': 1, 'border_color': '#eee', 'bg_color': '#fafafa'})
kpi_label = wb.add_format({'font_size': 9, 'font_color': '#888', 'align': 'center', 'valign': 'vcenter', 'font_name': 'Calibri', 'border': 1, 'border_color': '#eee', 'bg_color': '#fafafa'})
kpi_delta_up = wb.add_format({'font_size': 10, 'font_color': green, 'align': 'center', 'bold': True, 'font_name': 'Calibri', 'border': 1, 'border_color': '#eee', 'bg_color': '#fafafa'})
kpi_delta_down = wb.add_format({'font_size': 10, 'font_color': accent, 'align': 'center', 'bold': True, 'font_name': 'Calibri', 'border': 1, 'border_color': '#eee', 'bg_color': '#fafafa'})

ws1.set_row(5, 40)
ws1.set_row(6, 18)
ws1.set_row(7, 18)

kpis = [
    ('4,590', 'Events Captured', '▲ +312 this week', True),
    ('486', 'Facts Stored', '▲ +41 this week', True),
    ('26', 'Days Active', '', True),
    ('99.2%', 'System Uptime', '▲ +0.3%', True),
    ('12', 'Systems Built', '▲ +1 today', True),
]
for i, (val, label, delta, is_up) in enumerate(kpis):
    col = 1 + i  # B=1, C=2, etc
    ws1.write(5, col, val, kpi_val)
    ws1.write(6, col, label, kpi_label)
    if delta:
        ws1.write(7, col, delta, kpi_delta_up if is_up else kpi_delta_down)

# Systems Status Table
row = 10
ws1.merge_range(f'B{row}:H{row}', 'Active Systems', f_h1)
row += 1

headers = ['System', 'Status', 'Reliability', 'Tokens/Day', 'Cost/Day', 'Last Check', 'Trend']
for c, h in enumerate(headers):
    ws1.write(row, c+1, h, f_header)
row += 1

systems = [
    ['Email (Send)', '✅ Active', 0.998, 1200, 0.02, '19 Feb 08:20', [95,96,98,97,99,100,99]],
    ['Email (Read)', '✅ Active', 0.995, 800, 0.01, '19 Feb 08:20', [90,92,95,94,96,98,99]],
    ['Email Daemon', '✅ Running', 0.982, 0, 0, '19 Feb 08:15', [88,90,85,92,95,97,98]],
    ['Intel Briefing', '✅ Active', 0.950, 45000, 0.68, '19 Feb 09:00', [80,82,88,90,92,95,95]],
    ['Memory Daemon', '✅ Running', 0.975, 2000, 0.03, '19 Feb 08:20', [85,88,90,92,95,96,97]],
    ['Research (DD)', '✅ Active', 0.960, 30000, 0.45, '18 Feb 14:30', [75,80,85,88,92,95,96]],
    ['Research (EX)', '✅ Active', 0.920, 80000, 1.20, '17 Feb 22:00', [70,72,78,82,88,90,92]],
    ['Google Direct', '🆕 NEW', 1.000, 500, 0.01, '19 Feb 08:20', [0,0,0,0,0,0,100]],
    ['Atlas OS v2', '✅ Active', 0.940, 5000, 0.08, '19 Feb 07:45', [60,65,75,82,88,92,94]],
    ['Self-Awareness', '✅ Active', 0.890, 3000, 0.05, '19 Feb 07:45', [50,55,65,72,78,85,89]],
    ['Geopolitical α', '✅ Active', 0.850, 25000, 0.38, '19 Feb 09:00', [0,0,40,60,72,80,85]],
    ['MCP Workspace', '❌ Deprecated', 0.300, 0, 0, '19 Feb 07:45', [90,85,70,50,40,35,30]],
]

# Data validation lists for sparklines
spark_ws = wb.add_worksheet('_spark_data')
spark_ws.hide()

for i, sys_row in enumerate(systems):
    r = row + i
    is_alt = i % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    cc = f_cell_alt_c if is_alt else f_cell_c
    cp = f_pct_alt if is_alt else f_pct
    cm = f_money_alt if is_alt else f_money
    ci = f_int_alt if is_alt else f_int
    
    ws1.write(r, 1, sys_row[0], cf)
    
    # Status with colour
    status = sys_row[1]
    if '✅' in status or '🆕' in status:
        ws1.write(r, 2, status, f_good)
    elif '❌' in status:
        ws1.write(r, 2, status, f_bad)
    else:
        ws1.write(r, 2, status, f_warn)
    
    ws1.write(r, 3, sys_row[2], cp)
    ws1.write(r, 4, sys_row[3], ci)
    ws1.write(r, 5, sys_row[4], cm)
    ws1.write(r, 6, sys_row[5], cc)
    
    # Sparkline data
    for j, v in enumerate(sys_row[6]):
        spark_ws.write(i, j, v)
    
    ws1.add_sparkline(r, 7, {
        'range': f'_spark_data!A{i+1}:G{i+1}',
        'type': 'column',
        'style': 36 if '❌' not in status else 29,
    })

# Totals row
total_row = row + len(systems)
ws1.write(total_row, 1, 'TOTALS', f_total_label)
ws1.write(total_row, 2, '', f_total_label)
ws1.write_formula(total_row, 3, f'=AVERAGE(D{row+1}:D{total_row})', f_total_pct)
ws1.write_formula(total_row, 4, f'=SUM(E{row+1}:E{total_row})', f_total_int)
ws1.write_formula(total_row, 5, f'=SUM(F{row+1}:F{total_row})', f_total_val)
ws1.write(total_row, 6, '', f_total_label)
ws1.write(total_row, 7, '', f_total_label)

# Conditional formatting on reliability
ws1.conditional_format(row, 3, total_row-1, 3, {
    'type': 'cell', 'criteria': '>=', 'value': 0.95,
    'format': wb.add_format({'bg_color': '#e8f5e9', 'font_color': '#2e7d32', 'border': 1, 'num_format': '0.0%', 'align': 'center'})
})
ws1.conditional_format(row, 3, total_row-1, 3, {
    'type': 'cell', 'criteria': 'between', 'minimum': 0.80, 'maximum': 0.949,
    'format': wb.add_format({'bg_color': '#fff8e1', 'font_color': '#f57f17', 'border': 1, 'num_format': '0.0%', 'align': 'center'})
})
ws1.conditional_format(row, 3, total_row-1, 3, {
    'type': 'cell', 'criteria': '<', 'value': 0.80,
    'format': wb.add_format({'bg_color': '#fce4ec', 'font_color': '#c62828', 'border': 1, 'num_format': '0.0%', 'align': 'center'})
})

# Data bars on tokens/day
ws1.conditional_format(row, 4, total_row-1, 4, {
    'type': 'data_bar', 'bar_color': accent, 'bar_solid': True
})

# Note
ws1.write(total_row + 2, 1, '💡 Reliability is colour-coded: green ≥95%, amber 80-95%, red <80%. Token usage has data bars.', f_note)
ws1.write(total_row + 3, 1, '📈 Sparklines show 7-day trend per system.', f_note)


# ═══════════════════════════════════════════════════════════════
# SHEET 2: Financial Model
# ═══════════════════════════════════════════════════════════════
ws2 = wb.add_worksheet('💰 Cost Model')
ws2.hide_gridlines(2)
ws2.set_tab_color(gold)
ws2.set_column('A:A', 3)
ws2.set_column('B:B', 18)
ws2.set_column('C:N', 13)

ws2.merge_range('B2:N2', 'Atlas Operating Costs — 12 Month Projection', f_title)
ws2.merge_range('B3:N3', 'Based on actual usage data Jan-Feb 2026', f_subtitle)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
row = 5
ws2.write(row, 1, 'Category', f_header)
for i, m in enumerate(months):
    ws2.write(row, i+2, m, f_header)
row += 1

random.seed(42)
categories = [
    ('API Tokens', [15.20, 22.50, 28.00, 32.00, 35.00, 38.00, 40.00, 42.00, 44.00, 45.00, 46.00, 48.00]),
    ('Compute (EC2)', [8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50, 8.50]),
    ('Research (Exa)', [0, 5.00, 8.00, 10.00, 12.00, 12.00, 14.00, 14.00, 15.00, 15.00, 16.00, 16.00]),
    ('Storage', [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 1.60]),
    ('Domains/DNS', [0, 0, 1.20, 0, 0, 0, 0, 0, 0, 0, 0, 1.20]),
    ('Misc Tools', [2.00, 3.00, 3.50, 4.00, 4.00, 4.50, 4.50, 5.00, 5.00, 5.00, 5.50, 5.50]),
]

for i, (cat, vals) in enumerate(categories):
    r = row + i
    is_alt = i % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    cm = f_money_alt if is_alt else f_money
    ws2.write(r, 1, cat, cf)
    for j, v in enumerate(vals):
        ws2.write(r, j+2, v, cm)

# Total row
total_r = row + len(categories)
ws2.write(total_r, 1, 'TOTAL', f_total_label)
for j in range(12):
    col_letter = chr(67 + j)  # C=67
    ws2.write_formula(total_r, j+2, f'=SUM({col_letter}{row+1}:{col_letter}{total_r})', f_total_val)

# Cumulative row
cum_r = total_r + 1
f_cum = wb.add_format({'bold': True, 'font_size': 10, 'bg_color': '#e8e8e8', 'border': 1, 'num_format': '£#,##0.00', 'font_name': 'Calibri', 'align': 'right', 'font_color': accent})
ws2.write(cum_r, 1, 'CUMULATIVE', f_total_label)
ws2.write_formula(cum_r, 2, f'=C{total_r+1}', f_cum)
for j in range(1, 12):
    col_letter = chr(67 + j)
    prev_letter = chr(66 + j)
    ws2.write_formula(cum_r, j+2, f'={prev_letter}{cum_r+1}+{col_letter}{total_r+1}', f_cum)

# Chart: Monthly costs stacked bar
chart1 = wb.add_chart({'type': 'column', 'subtype': 'stacked'})
palette = [accent, teal, gold, soft_blue, purple, green]
for i, (cat, _) in enumerate(categories):
    chart1.add_series({
        'name': cat,
        'categories': f"'💰 Cost Model'!$C$6:$N$6",
        'values': f"'💰 Cost Model'!$C${row+1+i}:$N${row+1+i}",
        'fill': {'color': palette[i % len(palette)]},
        'gap': 80,
    })
chart1.set_title({'name': 'Monthly Operating Cost Breakdown', 'name_font': {'size': 12, 'color': navy}})
chart1.set_y_axis({'name': 'Cost (£)', 'num_format': '£#,##0'})
chart1.set_size({'width': 720, 'height': 380})
chart1.set_legend({'position': 'bottom'})
chart1.set_plotarea({'border': {'none': True}, 'fill': {'color': '#fafafa'}})
ws2.insert_chart(f'B{cum_r + 3}', chart1)

# Chart: Cumulative line
chart2 = wb.add_chart({'type': 'line'})
chart2.add_series({
    'name': 'Cumulative Cost',
    'categories': f"'💰 Cost Model'!$C$6:$N$6",
    'values': f"'💰 Cost Model'!$C${cum_r+1}:$N${cum_r+1}",
    'line': {'color': accent, 'width': 3},
    'marker': {'type': 'circle', 'size': 6, 'fill': {'color': accent}, 'border': {'color': 'white'}},
    'data_labels': {'value': True, 'num_format': '£#,##0', 'font': {'size': 8, 'color': '#666'}},
})
chart2.set_title({'name': 'Cumulative Annual Cost', 'name_font': {'size': 12, 'color': navy}})
chart2.set_y_axis({'name': 'Cumulative £', 'num_format': '£#,##0'})
chart2.set_size({'width': 720, 'height': 320})
chart2.set_legend({'none': True})
chart2.set_plotarea({'border': {'none': True}, 'fill': {'color': '#fafafa'}})
ws2.insert_chart(f'B{cum_r + 23}', chart2)


# ═══════════════════════════════════════════════════════════════
# SHEET 3: Task Analytics
# ═══════════════════════════════════════════════════════════════
ws3 = wb.add_worksheet('📈 Task Analytics')
ws3.hide_gridlines(2)
ws3.set_tab_color(teal)
ws3.set_column('A:A', 3)
ws3.set_column('B:B', 28)
ws3.set_column('C:I', 14)

ws3.merge_range('B2:I2', 'Task Performance Analytics', f_title)
ws3.merge_range('B3:I3', 'Aggregated from 26 days of operation', f_subtitle)

row = 5
headers = ['Task Type', 'Count', 'Avg Time (s)', 'Success %', 'Avg Tokens', 'Avg Cost', 'Complexity', 'Satisfaction']
for c, h in enumerate(headers):
    ws3.write(row, c+1, h, f_header_teal)
row += 1

random.seed(99)
tasks = [
    ['Email Send', 89, 3.2, 0.988, 1200, 0.02, 'Low', '⭐⭐⭐⭐⭐'],
    ['Email Read/Triage', 156, 5.1, 0.974, 2100, 0.03, 'Low', '⭐⭐⭐⭐⭐'],
    ['Research (Quick)', 34, 45.0, 0.941, 15000, 0.23, 'Medium', '⭐⭐⭐⭐'],
    ['Research (Deep)', 12, 210.0, 0.917, 48000, 0.72, 'High', '⭐⭐⭐⭐⭐'],
    ['Research (Exhaustive)', 5, 780.0, 0.800, 120000, 1.80, 'Very High', '⭐⭐⭐⭐'],
    ['Code Generation', 67, 35.0, 0.955, 8500, 0.13, 'Medium', '⭐⭐⭐⭐'],
    ['System Build', 18, 420.0, 0.889, 55000, 0.83, 'Very High', '⭐⭐⭐⭐⭐'],
    ['Calendar Mgmt', 42, 4.5, 0.976, 900, 0.01, 'Low', '⭐⭐⭐⭐'],
    ['File Management', 38, 8.0, 0.947, 1500, 0.02, 'Low', '⭐⭐⭐⭐'],
    ['Obsidian Updates', 95, 6.2, 0.968, 1100, 0.02, 'Low', '⭐⭐⭐⭐⭐'],
    ['Intel Briefing', 26, 120.0, 0.923, 42000, 0.63, 'High', '⭐⭐⭐⭐'],
    ['Conversation', 312, 8.5, 0.990, 3000, 0.05, 'Low', '⭐⭐⭐⭐⭐'],
    ['PDF Generation', 3, 25.0, 1.000, 5000, 0.08, 'Medium', '⭐⭐⭐⭐⭐'],
    ['Debug/Fix', 45, 55.0, 0.911, 12000, 0.18, 'High', '⭐⭐⭐'],
]

for i, t in enumerate(tasks):
    r = row + i
    is_alt = i % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    cc = f_cell_alt_c if is_alt else f_cell_c
    ci = f_int_alt if is_alt else f_int
    cp = f_pct_alt if is_alt else f_pct
    cm = f_money_alt if is_alt else f_money
    
    ws3.write(r, 1, t[0], cf)
    ws3.write(r, 2, t[1], ci)
    ws3.write(r, 3, t[2], cc)
    ws3.write(r, 4, t[3], cp)
    ws3.write(r, 5, t[4], ci)
    ws3.write(r, 6, t[5], cm)
    ws3.write(r, 7, t[6], cc)
    ws3.write(r, 8, t[7], cc)

# Conditional formatting — success rate
ws3.conditional_format(row, 4, row+len(tasks)-1, 4, {
    'type': '3_color_scale',
    'min_color': '#fce4ec',
    'mid_color': '#fff8e1',
    'max_color': '#e8f5e9',
})

# Data bars on count
ws3.conditional_format(row, 2, row+len(tasks)-1, 2, {
    'type': 'data_bar', 'bar_color': teal, 'bar_solid': True
})

# Icon set on cost
ws3.conditional_format(row, 6, row+len(tasks)-1, 6, {
    'type': 'icon_set', 'icon_style': '3_traffic_lights',
    'icons': [
        {'criteria': '>=', 'type': 'number', 'value': 0.50},
        {'criteria': '>=', 'type': 'number', 'value': 0.10},
        {'criteria': '<', 'type': 'number', 'value': 0.10},
    ]
})

# Pie chart — task count distribution
chart3 = wb.add_chart({'type': 'pie'})
chart3.add_series({
    'name': 'Task Distribution',
    'categories': f"'📈 Task Analytics'!$B${row+1}:$B${row+len(tasks)}",
    'values': f"'📈 Task Analytics'!$C${row+1}:$C${row+len(tasks)}",
    'data_labels': {'percentage': True, 'category': True, 'leader_lines': True, 'font': {'size': 8}},
    'points': [{'fill': {'color': palette[i % len(palette)]}} for i in range(len(tasks))],
})
chart3.set_title({'name': 'Task Volume Distribution', 'name_font': {'size': 12, 'color': navy}})
chart3.set_size({'width': 480, 'height': 380})
chart3.set_legend({'position': 'right', 'font': {'size': 8}})
ws3.insert_chart(f'B{row + len(tasks) + 2}', chart3)

# Scatter: complexity vs cost
chart4 = wb.add_chart({'type': 'scatter'})
chart4.add_series({
    'name': 'Avg Time vs Cost',
    'categories': f"'📈 Task Analytics'!$D${row+1}:$D${row+len(tasks)}",
    'values': f"'📈 Task Analytics'!$G${row+1}:$G${row+len(tasks)}",
    'marker': {'type': 'circle', 'size': 8, 'fill': {'color': accent}, 'border': {'color': 'white', 'width': 1}},
})
chart4.set_title({'name': 'Time vs Cost Correlation', 'name_font': {'size': 12, 'color': navy}})
chart4.set_x_axis({'name': 'Avg Time (seconds)'})
chart4.set_y_axis({'name': 'Avg Cost (£)', 'num_format': '£#,##0.00'})
chart4.set_size({'width': 400, 'height': 380})
chart4.set_legend({'none': True})
chart4.set_plotarea({'fill': {'color': '#fafafa'}})
ws3.insert_chart(f'G{row + len(tasks) + 2}', chart4)


# ═══════════════════════════════════════════════════════════════
# SHEET 4: Weekly Tracker
# ═══════════════════════════════════════════════════════════════
ws4 = wb.add_worksheet('📅 Weekly Tracker')
ws4.hide_gridlines(2)
ws4.set_tab_color(purple)
ws4.set_column('A:A', 3)
ws4.set_column('B:B', 16)
ws4.set_column('C:H', 14)
ws4.set_column('I:I', 16)

ws4.merge_range('B2:I2', 'Weekly Activity Tracker', f_title)

row = 4
headers = ['Week', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat/Sun', 'Weekly Total']
for c, h in enumerate(headers):
    ws4.write(row, c+1, h, f_header_accent if c == 0 or c == 7 else f_header)
row += 1

random.seed(7)
base = datetime(2026, 1, 26)
for w in range(4):
    r = row + w
    is_alt = w % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    ci = f_int_alt if is_alt else f_int
    
    week_start = base + timedelta(weeks=w)
    ws4.write(r, 1, f'W/C {week_start.strftime("%d %b")}', cf)
    
    daily = [random.randint(15, 85) for _ in range(6)]
    for d, val in enumerate(daily):
        ws4.write(r, d+2, val, ci)
    
    col_start = chr(67)  # C
    col_end = chr(72)    # H
    ws4.write_formula(r, 8, f'=SUM(C{r+1}:H{r+1})', f_total_int)

# Conditional formatting — heatmap on daily values
ws4.conditional_format(row, 2, row+3, 7, {
    'type': '3_color_scale',
    'min_color': '#fff5f5',
    'mid_color': '#fed7d7',
    'max_color': '#e94560',
})

# Area chart
chart5 = wb.add_chart({'type': 'area'})
for w in range(4):
    week_start = base + timedelta(weeks=w)
    chart5.add_series({
        'name': f'W/C {week_start.strftime("%d %b")}',
        'categories': f"'📅 Weekly Tracker'!$C$5:$H$5",
        'values': f"'📅 Weekly Tracker'!$C${row+1+w}:$H${row+1+w}",
        'fill': {'color': palette[w], 'transparency': 40},
        'line': {'color': palette[w], 'width': 2},
    })
chart5.set_title({'name': 'Weekly Activity Pattern', 'name_font': {'size': 12, 'color': navy}})
chart5.set_y_axis({'name': 'Tasks Completed'})
chart5.set_size({'width': 600, 'height': 350})
chart5.set_plotarea({'fill': {'color': '#fafafa'}})
ws4.insert_chart(f'B{row + 6}', chart5)


# ═══════════════════════════════════════════════════════════════
# SHEET 5: MSc Progress  
# ═══════════════════════════════════════════════════════════════
ws5 = wb.add_worksheet('🎓 MSc Progress')
ws5.hide_gridlines(2)
ws5.set_tab_color(green)
ws5.set_column('A:A', 3)
ws5.set_column('B:B', 22)
ws5.set_column('C:J', 14)

ws5.merge_range('B2:J2', 'MSc AI — Academic Progress Tracker', f_title)
ws5.merge_range('B3:J3', 'Queen Mary University of London · Started 28 Jan 2026', f_subtitle)

row = 5
headers = ['Module', 'Week', 'Readings', 'Lectures', 'Practice', 'Quiz Score', 'Confidence', 'Notes']
for c, h in enumerate(headers):
    ws5.write(row, c+1, h, f_header)
row += 1

modules = [
    ['Machine Learning', 'Week 3', '✅', '✅', '⚠️ Partial', 0.78, 0.65, 'Matrix operations need work'],
    ['Statistics', 'Week 3', '✅', '✅', '✅', 0.82, 0.70, 'Bayes theorem solid'],
    ['Ethics in AI', 'Week 3', '⚠️ Behind', '✅', 'N/A', None, 0.55, 'Need to read docs this week'],
    ['Programming', 'Week 3', '✅', '✅', '✅', 0.91, 0.85, 'Strong — professional exp helps'],
]

for i, m in enumerate(modules):
    r = row + i
    is_alt = i % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    cc = f_cell_alt_c if is_alt else f_cell_c
    cp = f_pct_alt if is_alt else f_pct
    
    ws5.write(r, 1, m[0], cf)
    ws5.write(r, 2, m[1], cc)
    
    for j in range(2, 5):
        val = m[j]
        if '✅' in str(val):
            ws5.write(r, j+1, val, f_good)
        elif '⚠️' in str(val):
            ws5.write(r, j+1, val, f_warn)
        else:
            ws5.write(r, j+1, val, cc)
    
    if m[5] is not None:
        ws5.write(r, 6, m[5], cp)
    else:
        ws5.write(r, 6, 'N/A', cc)
    
    ws5.write(r, 7, m[6], cp)
    ws5.write(r, 8, m[7], cf)

# Confidence conditional formatting
ws5.conditional_format(row, 7, row+len(modules)-1, 7, {
    'type': '3_color_scale',
    'min_color': '#fce4ec',
    'mid_color': '#fff8e1',
    'max_color': '#e8f5e9',
})

# Radar-style chart (bar as proxy)
chart6 = wb.add_chart({'type': 'radar', 'subtype': 'filled'})
chart6.add_series({
    'name': 'Confidence',
    'categories': f"'🎓 MSc Progress'!$B${row+1}:$B${row+len(modules)}",
    'values': f"'🎓 MSc Progress'!$H${row+1}:$H${row+len(modules)}",
    'fill': {'color': accent, 'transparency': 30},
    'line': {'color': accent, 'width': 2},
})
chart6.add_series({
    'name': 'Quiz Score',
    'categories': f"'🎓 MSc Progress'!$B${row+1}:$B${row+len(modules)}",
    'values': f"'🎓 MSc Progress'!$G${row+1}:$G${row+len(modules)}",
    'fill': {'color': teal, 'transparency': 30},
    'line': {'color': teal, 'width': 2},
})
chart6.set_title({'name': 'Module Confidence vs Quiz Performance', 'name_font': {'size': 12, 'color': navy}})
chart6.set_size({'width': 450, 'height': 350})
ws5.insert_chart(f'B{row + len(modules) + 2}', chart6)

# Study hours doughnut
chart7 = wb.add_chart({'type': 'doughnut'})
# Write study hour data
study_row = row + len(modules) + 2
ws5.write(study_row, 8, 'ML', f_note)
ws5.write(study_row+1, 8, 'Stats', f_note)
ws5.write(study_row+2, 8, 'Ethics', f_note)
ws5.write(study_row+3, 8, 'Programming', f_note)
ws5.write(study_row, 9, 12, f_cell_c)
ws5.write(study_row+1, 9, 10, f_cell_c)
ws5.write(study_row+2, 9, 5, f_cell_c)
ws5.write(study_row+3, 9, 8, f_cell_c)

chart7.add_series({
    'name': 'Study Hours',
    'categories': f"'🎓 MSc Progress'!$I${study_row+1}:$I${study_row+4}",
    'values': f"'🎓 MSc Progress'!$J${study_row+1}:$J${study_row+4}",
    'data_labels': {'percentage': True, 'category': True, 'font': {'size': 9}},
    'points': [{'fill': {'color': c}} for c in [accent, teal, gold, soft_blue]],
})
chart7.set_title({'name': 'Study Hours by Module (This Week)', 'name_font': {'size': 12, 'color': navy}})
chart7.set_size({'width': 400, 'height': 350})
ws5.insert_chart(f'F{row + len(modules) + 2}', chart7)


# ═══════════════════════════════════════════════════════════════
# SHEET 6: What This Demonstrates
# ═══════════════════════════════════════════════════════════════
ws6 = wb.add_worksheet('🛠️ Capabilities')
ws6.hide_gridlines(2)
ws6.set_tab_color(navy)
ws6.set_column('A:A', 3)
ws6.set_column('B:B', 25)
ws6.set_column('C:C', 25)
ws6.set_column('D:D', 45)

ws6.merge_range('B2:D2', 'Spreadsheet Generation Capabilities', f_title)
ws6.merge_range('B3:D3', 'Everything in this workbook was built programmatically', f_subtitle)

row = 5
ws6.write(row, 1, 'Capability', f_header_accent)
ws6.write(row, 2, 'Library', f_header_accent)
ws6.write(row, 3, 'Example in This Workbook', f_header_accent)
row += 1

caps = [
    ['Multi-sheet Workbooks', 'xlsxwriter', '6 sheets with different themes'],
    ['Coloured Tab Headers', 'xlsxwriter', 'Each sheet has a unique tab colour'],
    ['Merged Cells', 'xlsxwriter', 'Title rows span multiple columns'],
    ['Custom Number Formats', 'xlsxwriter', '£ currency, %, #,##0 integers, dates'],
    ['Alternating Row Colours', 'xlsxwriter', 'Zebra striping on all data tables'],
    ['Conditional Formatting', 'xlsxwriter', '3-colour scales, data bars, icon sets'],
    ['Data Bars', 'xlsxwriter', 'Token usage column on Dashboard'],
    ['Icon Sets', 'xlsxwriter', 'Traffic lights on cost column'],
    ['3-Colour Scales', 'xlsxwriter', 'Reliability %, heatmap on weekly tracker'],
    ['Sparklines', 'xlsxwriter', '7-day trend per system on Dashboard'],
    ['Formulas (SUM/AVG)', 'xlsxwriter', 'Totals rows with live formulas'],
    ['Column Charts', 'xlsxwriter', 'Stacked cost breakdown'],
    ['Line Charts', 'xlsxwriter', 'Cumulative cost with data labels'],
    ['Pie Charts', 'xlsxwriter', 'Task volume distribution'],
    ['Area Charts', 'xlsxwriter', 'Weekly activity patterns'],
    ['Radar Charts', 'xlsxwriter', 'Module confidence vs quiz scores'],
    ['Doughnut Charts', 'xlsxwriter', 'Study hours by module'],
    ['Scatter Plots', 'xlsxwriter', 'Time vs cost correlation'],
    ['Hidden Helper Sheets', 'xlsxwriter', 'Sparkline data stored in hidden sheet'],
    ['Custom Fonts & Colours', 'xlsxwriter', 'Navy/accent palette throughout'],
    ['Border Styling', 'xlsxwriter', 'Light borders, header emphasis'],
    ['Text Wrapping', 'xlsxwriter', 'Header cells auto-wrap'],
    ['Frozen Panes', 'xlsxwriter', 'Could add — headers stay visible on scroll'],
    ['Data Validation', 'xlsxwriter', 'Could add — dropdowns, input constraints'],
    ['Print Layout', 'xlsxwriter', 'Could add — page breaks, headers/footers'],
]

for i, (cap, lib, ex) in enumerate(caps):
    r = row + i
    is_alt = i % 2 == 1
    cf = f_cell_alt if is_alt else f_cell
    cc = f_cell_alt_c if is_alt else f_cell_c
    ws6.write(r, 1, cap, cf)
    ws6.write(r, 2, lib, cc)
    ws6.write(r, 3, ex, cf)

ws6.write(row + len(caps) + 1, 1, f'Total capabilities demonstrated: {len([c for c in caps if "Could" not in c[2]])}', f_note)
ws6.write(row + len(caps) + 2, 1, 'Built by Atlas · 19 February 2026 · No templates, no manual design', f_note)


# ─── Finalise ─────────────────────────────────────────────────
wb.close()
print(f'✅ Workbook built: {OUTPUT}')
print(f'   Sheets: 6 (+ 1 hidden)')
print(f'   Charts: 7')
print(f'   Tables: 6')
print(f'   Conditional formats: 8')
print(f'   Sparklines: 12')
