#!/usr/bin/env python3
"""ML Week 2 — Linear Regression Visual Notation Cheat Sheet"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)

OUTPUT = '/home/ubuntu/clawd/output/ml-linear-regression-cheatsheet.pdf'

NAVY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#e94560')
TEAL = colors.HexColor('#0f969c')
GOLD = colors.HexColor('#f5a623')
PURPLE = colors.HexColor('#9b59b6')
LIGHT = colors.HexColor('#f8f9fa')

C_RED = '#e94560'
C_BLUE = '#4a90d9'
C_GOLD = '#f5a623'
C_TEAL = '#0f969c'
C_PURPLE = '#9b59b6'
C_NAVY = '#1e3a5f'
C_GREY = '#888888'
C_GREEN = '#2ecc71'


def fig_simple_regression():
    """Simple linear regression — line of best fit with errors shown."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    
    np.random.seed(42)
    x = np.linspace(20, 65, 15)
    y_true = 0.8 * x + 10 + np.random.randn(15) * 5
    
    # Best fit line
    w1, w0 = np.polyfit(x, y_true, 1)
    y_pred = w1 * x + w0
    
    ax.scatter(x, y_true, color=C_BLUE, s=60, edgecolors='white', linewidth=1, zorder=3, label='Data points (xᵢ, yᵢ)')
    ax.plot(x, y_pred, color=C_RED, linewidth=2.5, zorder=2, label=f'Model: ŷ = {w0:.1f} + {w1:.2f}x')
    
    # Show errors for a few points
    for i in [2, 5, 9, 12]:
        ax.plot([x[i], x[i]], [y_true[i], y_pred[i]], color=C_GOLD, linewidth=2, linestyle='-', zorder=1)
        mid_y = (y_true[i] + y_pred[i]) / 2
        ax.text(x[i] + 1, mid_y, f'eᵢ', fontsize=8, color=C_GOLD, fontweight='bold')
    
    ax.set_xlabel('x (predictor, e.g. Age)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_ylabel('y (label, e.g. Salary)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_title('Simple Linear Regression: ŷ = w₀ + w₁x', fontsize=12, fontweight='bold', color=C_NAVY, pad=10)
    ax.legend(fontsize=8, loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Annotate w0 and w1
    ax.annotate(f'w₀ = {w0:.1f}\n(intercept)', xy=(20, y_pred[0]),
               textcoords='offset points', xytext=(-10, 30),
               fontsize=8, color=C_NAVY, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbe6', edgecolor=C_GOLD, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_GOLD, linewidth=1.5))
    
    ax.annotate(f'w₁ = {w1:.2f}\n(gradient/slope)', xy=(45, w1*45+w0),
               textcoords='offset points', xytext=(30, -25),
               fontsize=8, color=C_NAVY, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#fde0e5', edgecolor=C_RED, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_RED, linewidth=1.5))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_error_visual():
    """Visual: error, squared error, MSE."""
    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    
    np.random.seed(7)
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2.1, 3.8, 5.2, 7.1, 8.5])
    y_pred = 1.8 * x + 0.2
    errors = y - y_pred
    
    # Plot 1: Errors
    ax = axes[0]
    ax.scatter(x, y, color=C_BLUE, s=60, edgecolors='white', linewidth=1, zorder=3)
    ax.plot(x, y_pred, color=C_RED, linewidth=2, zorder=2)
    for i in range(len(x)):
        ax.plot([x[i], x[i]], [y[i], y_pred[i]], color=C_GOLD, linewidth=2)
    ax.set_title('eᵢ = yᵢ − ŷᵢ\n(prediction errors)', fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=7)
    
    # Plot 2: Squared errors as squares
    ax = axes[1]
    sq_errors = errors ** 2
    bar_colors = ['#dbe9f7' if e >= 0 else '#fde0e5' for e in errors]
    ax.bar(x, sq_errors, color=bar_colors, edgecolor=C_BLUE, linewidth=1.5, width=0.6)
    for i, (xi, se) in enumerate(zip(x, sq_errors)):
        ax.text(xi, se + 0.05, f'{se:.2f}', ha='center', fontsize=7, color=C_NAVY, fontweight='bold')
    ax.set_title('eᵢ² = (yᵢ − ŷᵢ)²\n(squared errors)', fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=7)
    
    # Plot 3: MSE formula
    ax = axes[2]
    ax.axis('off')
    mse = np.mean(sq_errors)
    sse = np.sum(sq_errors)
    
    text_lines = [
        ('SSE = Σ eᵢ²', f'= {sse:.2f}', C_TEAL),
        ('MSE = SSE / N', f'= {sse:.2f} / {len(x)} = {mse:.2f}', C_RED),
        ('RMSE = √MSE', f'= √{mse:.2f} = {math.sqrt(mse):.2f}', C_PURPLE),
    ]
    
    for i, (formula, value, col) in enumerate(text_lines):
        y_pos = 0.75 - i * 0.3
        ax.text(0.5, y_pos, formula, ha='center', va='center', fontsize=11, color=col,
                fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, y_pos - 0.1, value, ha='center', va='center', fontsize=9, color=C_GREY,
                transform=ax.transAxes)
    
    ax.set_title('Quality Metrics\n(how good is the fit?)', fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_polynomial():
    """Polynomial regression — underfitting to overfitting."""
    fig, axes = plt.subplots(1, 4, figsize=(8, 2.8))
    
    np.random.seed(42)
    x = np.linspace(0, 10, 20)
    y = 0.5 * x**2 - 3 * x + 10 + np.random.randn(20) * 3
    x_smooth = np.linspace(0, 10, 100)
    
    degrees = [1, 2, 3, 15]
    titles = ['D=1: Linear\n(underfitting)', 'D=2: Quadratic\n(just right ✓)', 'D=3: Cubic\n(still good)', 'D=15: Overfit\n(memorising noise)']
    title_cols = [C_BLUE, C_GREEN, C_TEAL, C_RED]
    
    for ax, d, title, tc in zip(axes, degrees, titles, title_cols):
        ax.scatter(x, y, color=C_BLUE, s=30, edgecolors='white', linewidth=0.5, zorder=3)
        
        coeffs = np.polyfit(x, y, d)
        y_fit = np.polyval(coeffs, x_smooth)
        
        line_col = tc
        ax.plot(x_smooth, y_fit, color=line_col, linewidth=2.5, zorder=2)
        
        mse = np.mean((y - np.polyval(coeffs, x))**2)
        ax.text(5, max(y) + 3, f'MSE = {mse:.1f}', ha='center', fontsize=7, color=C_NAVY, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#fffbe6', edgecolor=C_GOLD, linewidth=1))
        
        ax.set_title(title, fontsize=8, fontweight='bold', color=tc, pad=8)
        ax.set_ylim(min(y) - 5, max(y) + 8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=6)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_bias_variance():
    """Training vs deployment error — the U-curve."""
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    
    x = np.linspace(0, 10, 100)
    train_err = 12 * np.exp(-0.5 * x) + 0.5
    deploy_err = 12 * np.exp(-0.5 * x) + 0.5 + 0.15 * x**2
    
    ax.plot(x, train_err, color=C_RED, linewidth=2.5, label='Training error')
    ax.plot(x, deploy_err, color=C_BLUE, linewidth=2.5, label='Deployment error')
    
    # Sweet spot
    min_idx = np.argmin(deploy_err)
    ax.scatter([x[min_idx]], [deploy_err[min_idx]], color=C_GREEN, s=100, zorder=5, edgecolors='white', linewidth=2)
    ax.annotate('Sweet spot\n"Just right"', (x[min_idx], deploy_err[min_idx]),
               textcoords='offset points', xytext=(40, 20),
               fontsize=9, color=C_GREEN, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4efdf', edgecolor=C_GREEN, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_GREEN, linewidth=1.5))
    
    # Zones
    ax.axvspan(0, 2.5, color='#dbe9f7', zorder=0)
    ax.axvspan(2.5, 5.5, color='#d4efdf', zorder=0)
    ax.axvspan(5.5, 10, color='#fde0e5', zorder=0)
    
    ax.text(1.2, 12, 'UNDERFITTING\n(too rigid)', ha='center', fontsize=8, color=C_BLUE, fontweight='bold')
    ax.text(4, 12, 'JUST RIGHT', ha='center', fontsize=8, color=C_GREEN, fontweight='bold')
    ax.text(7.5, 12, 'OVERFITTING\n(memorising noise)', ha='center', fontsize=8, color=C_RED, fontweight='bold')
    
    ax.set_xlabel('Model Flexibility (complexity / degree D)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_ylabel('Error (MSE)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_title('The Flexibility Trade-Off: Training vs Deployment Error', fontsize=11, fontweight='bold', color=C_NAVY, pad=10)
    ax.legend(fontsize=9, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, 15)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_least_squares():
    """Visual: the least squares solution."""
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.axis('off')
    
    # Show the formula with breakdown
    ax.text(0.5, 0.85, 'The Least Squares Solution', ha='center', fontsize=13, fontweight='bold', color=C_NAVY, transform=ax.transAxes)
    
    ax.text(0.5, 0.55, 'w_best = (XᵀX)⁻¹ Xᵀy', ha='center', fontsize=16, fontweight='bold', color=C_RED,
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fde0e5', edgecolor=C_RED, linewidth=2))
    
    labels = [
        (0.12, 0.15, 'X = design matrix\n(all predictors + 1s column)', C_BLUE),
        (0.38, 0.15, 'Xᵀ = X transposed\n(rows ↔ columns)', C_TEAL),
        (0.65, 0.15, '(XᵀX)⁻¹ = inverse\n(undo the multiplication)', C_PURPLE),
        (0.88, 0.15, 'y = true labels\n(what we\'re fitting to)', C_GOLD),
    ]
    for x_pos, y_pos, text, col in labels:
        ax.text(x_pos, y_pos, text, ha='center', fontsize=7, color=col, fontweight='bold', transform=ax.transAxes)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_design_matrix():
    """Visual: the design matrix X."""
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.axis('off')
    
    # Show matrix visually
    ax.text(0.02, 0.85, 'The Design Matrix — How Your Data Becomes Maths', fontsize=11, fontweight='bold', color=C_NAVY, transform=ax.transAxes)
    
    # Spreadsheet → Matrix
    # Left side: spreadsheet
    cell_data = [
        ['', 'Age', 'Height', 'Salary'],
        ['S1', '18', '175', '£12k'],
        ['S2', '37', '180', '£68k'],
        ['S3', '66', '158', '£80k'],
    ]
    
    for r, row in enumerate(cell_data):
        for c, val in enumerate(row):
            x_pos = 0.02 + c * 0.09
            y_pos = 0.7 - r * 0.15
            bg = '#dbe9f7' if r == 0 else ('#f8f9fa' if r % 2 == 0 else 'white')
            fc = C_NAVY if r == 0 else '#333'
            fw = 'bold' if r == 0 or c == 0 else 'normal'
            ax.text(x_pos, y_pos, val, fontsize=8, color=fc, fontweight=fw, transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.15', facecolor=bg, edgecolor='#ddd', linewidth=0.5) if r > 0 or c > 0 else {})
    
    # Arrow
    ax.annotate('', xy=(0.42, 0.4), xytext=(0.38, 0.4), 
                arrowprops=dict(arrowstyle='->', color=C_GOLD, linewidth=3), transform=ax.transAxes)
    ax.text(0.4, 0.5, 'becomes', fontsize=7, color=C_GREY, ha='center', transform=ax.transAxes)
    
    # Right side: Matrix
    ax.text(0.45, 0.75, 'X =', fontsize=12, color=C_RED, fontweight='bold', transform=ax.transAxes)
    
    matrix_text = '⎡ 1   18   175 ⎤\n⎢ 1   37   180 ⎥\n⎢ 1   66   158 ⎥\n⎣ 1   25   168 ⎦'
    ax.text(0.52, 0.45, matrix_text, fontsize=9, color=C_NAVY, fontfamily='monospace', transform=ax.transAxes,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#fde0e5', edgecolor=C_RED, linewidth=1.5))
    
    ax.text(0.52, 0.1, '↑ Column of 1s\n(for intercept w₀)', fontsize=7, color=C_GOLD, fontweight='bold', transform=ax.transAxes)
    
    # y vector
    ax.text(0.82, 0.75, 'y =', fontsize=12, color=C_TEAL, fontweight='bold', transform=ax.transAxes)
    y_text = '⎡ 12k ⎤\n⎢ 68k ⎥\n⎢ 80k ⎥\n⎣ 45k ⎦'
    ax.text(0.87, 0.45, y_text, fontsize=9, color=C_NAVY, fontfamily='monospace', transform=ax.transAxes,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#d6f0f0', edgecolor=C_TEAL, linewidth=1.5))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_pipeline():
    """Regression pipeline."""
    fig, ax = plt.subplots(figsize=(7, 1.8))
    
    steps = [
        ('Data\n{(xᵢ, yᵢ)}', C_BLUE, '#dbe9f7'),
        ('Choose Model\nLinear / Poly', C_PURPLE, '#ede0f5'),
        ('Train\n(least squares)', C_GOLD, '#fef3d6'),
        ('Predict\nŷ = f(x)', C_RED, '#fde0e5'),
        ('Evaluate\nMSE, R²', C_TEAL, '#d6f0f0'),
    ]
    
    for i, (text, col, bg) in enumerate(steps):
        x = i * 1.5
        rect = FancyBboxPatch((x, 0.1), 1.2, 0.8, boxstyle='round,pad=0.1',
                               facecolor=bg, edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.6, 0.5, text, ha='center', va='center', fontsize=7.5, color=C_NAVY, fontweight='bold')
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + 1.4, 0.5), xytext=(x + 1.25, 0.5),
                        arrowprops=dict(arrowstyle='->', color=C_NAVY, linewidth=2))
    
    ax.set_xlim(-0.2, 7.5)
    ax.set_ylim(-0.1, 1.1)
    ax.axis('off')
    ax.set_title('The Regression Pipeline', fontsize=12, fontweight='bold', color=C_NAVY, pad=5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_r_squared():
    """R² visual explanation."""
    fig, axes = plt.subplots(1, 2, figsize=(6, 2.8))
    
    np.random.seed(42)
    x = np.linspace(1, 10, 15)
    y = 2 * x + 5 + np.random.randn(15) * 2
    y_mean = np.mean(y)
    coeffs = np.polyfit(x, y, 1)
    y_pred = np.polyval(coeffs, x)
    
    # Left: total variance (from mean)
    ax = axes[0]
    ax.scatter(x, y, color=C_BLUE, s=40, edgecolors='white', linewidth=0.8, zorder=3)
    ax.axhline(y=y_mean, color=C_GREY, linewidth=2, linestyle='--', label=f'ȳ = {y_mean:.1f}')
    for xi, yi in zip(x, y):
        ax.plot([xi, xi], [yi, y_mean], color='#ffcccc', linewidth=1.5)
    ax.set_title('Total variance\nΣ(yᵢ − ȳ)²', fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
    ax.legend(fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=7)
    
    # Right: residual variance (from model)
    ax = axes[1]
    ax.scatter(x, y, color=C_BLUE, s=40, edgecolors='white', linewidth=0.8, zorder=3)
    ax.plot(x, y_pred, color=C_RED, linewidth=2, label='Model ŷ', zorder=2)
    for xi, yi, yp in zip(x, y, y_pred):
        ax.plot([xi, xi], [yi, yp], color=C_GOLD, linewidth=1.5)
    ax.set_title('Residual variance\nΣ(yᵢ − ŷᵢ)² = Σeᵢ²', fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
    ax.legend(fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=7)
    
    ss_tot = np.sum((y - y_mean)**2)
    ss_res = np.sum((y - y_pred)**2)
    r2 = 1 - ss_res / ss_tot
    
    fig.suptitle(f'R² = 1 − (residual / total) = 1 − {ss_res:.1f}/{ss_tot:.1f} = {r2:.3f}', 
                fontsize=10, fontweight='bold', color=C_RED, y=0.02)
    
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


# ─── Build PDF ────────────────────────────────────────

doc = SimpleDocTemplate(OUTPUT, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.4*inch,
                        leftMargin=0.6*inch, rightMargin=0.6*inch)
styles = getSampleStyleSheet()

s_title = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
s_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11, textColor=colors.gray, spaceAfter=12, alignment=TA_CENTER)
s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15, textColor=NAVY, spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
s_body = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=4, textColor=colors.HexColor('#333'))
s_caption = ParagraphStyle('Cap', parent=styles['Normal'], fontSize=8.5, textColor=colors.gray, alignment=TA_CENTER, spaceAfter=10, spaceBefore=2)
s_box_title = ParagraphStyle('BT', parent=styles['Normal'], fontSize=10, textColor='white', fontName='Helvetica-Bold')
s_box_body = ParagraphStyle('BB', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor('#333'), spaceAfter=2)
s_footer = ParagraphStyle('F', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)

def box(title, items, color=NAVY):
    content = []
    tt = Table([[Paragraph(title, s_box_title)]], colWidths=[470])
    tt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color), ('TOPPADDING', (0,0), (-1,-1), 5),
                             ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('LEFTPADDING', (0,0), (-1,-1), 10)]))
    content.append(tt)
    body_items = [Paragraph(f'• {item}', s_box_body) for item in items]
    bt = Table([[body_items]], colWidths=[470])
    bt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), LIGHT), ('TOPPADDING', (0,0), (-1,-1), 6),
                             ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('LEFTPADDING', (0,0), (-1,-1), 14),
                             ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd'))]))
    content.append(bt)
    content.append(Spacer(1, 6))
    return content

story = []

# PAGE 1: Title + Pipeline + Symbol Table
story.append(Spacer(1, 20))
story.append(Paragraph('ML Week 2 — Regression Notation Cheat Sheet', s_title))
story.append(Paragraph('Supervised Learning: Linear & Polynomial Regression', s_sub))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=2))
story.append(Spacer(1, 8))

story.append(Image(fig_pipeline(), width=460, height=125))
story.append(Paragraph('The regression pipeline — collect data, choose model, train (find best w), predict, evaluate.', s_caption))

story.append(Paragraph('The Core Symbols', s_h1))

sym_data = [
    ['Symbol', 'Name', 'Plain English', 'Think of it as...'],
    ['x', 'Predictor(s)', 'Input features', '"What we use to predict"'],
    ['xᵢ', 'Sample i predictors', 'The i-th data point', '"Row i in the spreadsheet"'],
    ['y', 'Label (true)', 'The target value', '"The right answer (continuous)"'],
    ['ŷ = f(x)', 'Prediction', 'Model output', '"Our guess" — ŷ is always estimated'],
    ['eᵢ = yᵢ − ŷᵢ', 'Error / residual', 'How far off we were', '"The gap between truth and guess"'],
    ['w₀', 'Intercept', 'Constant term', '"Starting point when x = 0"'],
    ['w₁', 'Gradient / slope', 'How much y changes per x', '"For every +1 in x, y changes by w₁"'],
    ['w', 'Weight vector', '[w₀, w₁, ..., wₖ]', '"All the model parameters together"'],
    ['N', 'Sample count', 'Number of data points', '"How many rows"'],
    ['K', 'Number of predictors', 'How many features', '"How many columns (minus the label)"'],
    ['D', 'Polynomial degree', 'Hyperparameter', '"How curvy can the line be?"'],
    ['X', 'Design matrix', 'All predictors in matrix form', '"The spreadsheet as a matrix (+ 1s column)"'],
    ['SSE = Σeᵢ²', 'Sum of squared errors', 'Total squared mistakes', '"Add up all squared gaps"'],
    ['MSE = SSE/N', 'Mean squared error', 'Average squared mistake', '"Average gap squared"'],
    ['R²', 'R-squared', '% of variance explained', '"How much better than just guessing ȳ?"'],
]

sym_table = Table(sym_data, colWidths=[75, 80, 130, 170])
sym_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8.5),
    ('FONTSIZE', (0,1), (-1,-1), 7.5), ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
]))
story.append(sym_table)

story.append(PageBreak())

# PAGE 2: Simple Regression + Error
story.append(Paragraph('Simple Linear Regression', s_h1))
story.append(Image(fig_simple_regression(), width=430, height=255))
story.append(Paragraph('The gold lines are errors (eᵢ). The model minimises the total squared error. w₀ is where the line starts, w₁ is how steep it is.', s_caption))

story.extend(box('🔑 Simple Linear Regression — Key Facts', [
    '<b>ŷ = w₀ + w₁x</b> → straight line with intercept w₀ and slope w₁',
    '<b>w₀</b> (intercept) = predicted value when x = 0',
    '<b>w₁</b> (gradient) = how much ŷ changes for each +1 in x',
    '<b>eᵢ = yᵢ − ŷᵢ</b> = prediction error for sample i (the vertical gap)',
    '<b>Training</b> = finding w₀ and w₁ that minimise MSE',
    'The model that minimises MSE is the <b>least squares solution</b>',
], color=TEAL))

story.append(Paragraph('Error, Squared Error & Quality Metrics', s_h1))
story.append(Image(fig_error_visual(), width=470, height=195))
story.append(Paragraph('Left: raw errors. Centre: squared errors (always positive). Right: the three quality metrics.', s_caption))

story.extend(box('🧮 Quality Metrics Decoded', [
    '<b>SSE = Σeᵢ²</b> — sum of all squared errors. Bigger = worse fit.',
    '<b>MSE = SSE / N</b> — average squared error. The main quality metric in the lecture.',
    '<b>RMSE = √MSE</b> — root MSE. Same units as y (e.g. £ not £²). More interpretable.',
    '<b>MAE = Σ|eᵢ| / N</b> — mean absolute error. Less sensitive to outliers than MSE.',
    '<b>R² = 1 − Σeᵢ² / Σ(yᵢ−ȳ)²</b> — proportion of variance explained. R²=1 is perfect, R²=0 is useless.',
    'Why squared? Squaring makes all errors positive AND penalises big errors more heavily.',
], color=ACCENT))

story.append(PageBreak())

# PAGE 3: Design Matrix + Least Squares
story.append(Paragraph('The Design Matrix: From Spreadsheet to Maths', s_h1))
story.append(Image(fig_design_matrix(), width=440, height=185))
story.append(Paragraph('Your data table becomes matrix X (with a column of 1s prepended for the intercept) and vector y.', s_caption))

story.extend(box('🔑 Matrix Notation — What You Need to Know', [
    '<b>X</b> = design matrix. Each row = one sample. Columns = [1, predictor₁, predictor₂, ...]',
    '<b>The column of 1s</b> is added so that wᵀx = w₀·1 + w₁·x₁ + w₂·x₂ + ... (gives us the intercept)',
    '<b>y</b> = label vector. All the true values stacked vertically.',
    '<b>w</b> = parameter vector [w₀, w₁, ..., wₖ]. What we\'re trying to find.',
    '<b>ŷ = Xw</b> — matrix multiplication gives all predictions at once',
    '<b>e = y − ŷ</b> — error vector (all errors at once)',
], color=NAVY))

story.append(Paragraph('The Least Squares Solution', s_h1))
story.append(Image(fig_least_squares(), width=430, height=145))
story.append(Paragraph('This formula gives you the EXACT best weights in one step. No iteration needed.', s_caption))

story.extend(box('🔑 Least Squares — What It Means', [
    '<b>w_best = (XᵀX)⁻¹ Xᵀy</b> — the analytical solution for the best linear model',
    'Works for simple AND multiple regression — same formula',
    'Also works for polynomial regression (treat x², x³ as extra predictors)',
    '<b>Xᵀ</b> = X transposed (flip rows and columns)',
    '<b>(XᵀX)⁻¹</b> = inverse of XᵀX (only exists when columns of X are independent)',
    'This is an <b>exact</b> solution — unlike gradient descent, no iteration needed',
], color=PURPLE))

story.append(PageBreak())

# PAGE 4: Polynomial + Bias-Variance
story.append(Paragraph('Polynomial Regression: Controlling Flexibility', s_h1))
story.append(Image(fig_polynomial(), width=470, height=190))
story.append(Paragraph('D=1 (linear) underfits. D=2 captures the pattern. D=15 memorises every data point including noise.', s_caption))

story.extend(box('🔑 Polynomial Regression — Key Facts', [
    '<b>f(x) = w₀ + w₁x + w₂x² + ... + wDxᴰ</b>',
    '<b>D</b> is the degree (hyperparameter) — controls flexibility',
    'D=1 → linear (straight line). D=2 → quadratic (parabola). D=3 → cubic.',
    'Higher D = more flexible = can fit more complex patterns',
    'BUT too high D → <b>overfitting</b> (memorises noise, fails on new data)',
    'D is a <b>hyperparameter</b> — you choose it BEFORE training. w₀, w₁... are parameters found BY training.',
], color=TEAL))

story.append(Paragraph('The Flexibility Trade-Off', s_h1))
story.append(Image(fig_bias_variance(), width=400, height=235))
story.append(Paragraph('Training error always decreases with flexibility. Deployment error has a U-shape — find the sweet spot.', s_caption))

story.extend(box('⚖️ Underfitting vs Overfitting', [
    '<b>Underfitting:</b> Model too simple → can\'t capture the pattern → high error on BOTH training and deployment',
    '<b>Overfitting:</b> Model too complex → memorises noise → low training error, HIGH deployment error',
    '<b>Just right:</b> Captures pattern, ignores noise → good on both',
    '<b>Key insight:</b> You can ONLY detect overfitting by comparing training AND deployment performance',
    'Looking at training error alone is MISLEADING — a D=15 polynomial has near-zero training error but is terrible',
], color=ACCENT))

story.append(PageBreak())

# PAGE 5: R² + Quick Reference
story.append(Paragraph('R-Squared: How Good Is Your Model?', s_h1))
story.append(Image(fig_r_squared(), width=430, height=210))
story.append(Paragraph('Left: total variance from the mean ȳ. Right: residual variance from the model. R² = how much the model improves over just guessing ȳ.', s_caption))

story.extend(box('🔑 R² — The Intuition', [
    'R² = 1 − (residual variance / total variance)',
    '<b>R² = 1.0</b> → model explains ALL the variance → perfect fit',
    '<b>R² = 0.0</b> → model explains NOTHING → no better than guessing the mean',
    '<b>R² = 0.85</b> → model explains 85% of variance → 15% is unexplained (noise or missing predictors)',
    'R² can be negative if model is worse than just predicting ȳ (very bad model)',
], color=TEAL))

story.append(Spacer(1, 8))

story.extend(box('📐 ONE-PAGE NOTATION DECODER', [
    '<b>ŷ = w₀ + w₁x</b> → simple linear regression (one predictor)',
    '<b>ŷ = wᵀx = w₀ + w₁x₁ + ... + wₖxₖ</b> → multiple linear regression',
    '<b>ŷ = w₀ + w₁x + w₂x² + ... + wDxᴰ</b> → polynomial regression (degree D)',
    '<b>eᵢ = yᵢ − ŷᵢ</b> → error  |  <b>SSE = Σeᵢ²</b>  |  <b>MSE = SSE/N</b>  |  <b>R² = 1 − Σeᵢ²/Σ(yᵢ−ȳ)²</b>',
    '<b>w_best = (XᵀX)⁻¹Xᵀy</b> → least squares solution (exact, one step)',
    '<b>X</b> = design matrix (data + 1s column)  |  <b>D</b> = degree (hyperparameter)  |  <b>N</b> = samples  |  <b>K</b> = predictors',
], color=NAVY))

story.extend(box('🎯 EVERY EQUATION DOES ONE OF FOUR THINGS', [
    '<b>1. DEFINE THE MODEL:</b> What shape? → ŷ = w₀ + w₁x (linear) or + w₂x² + ... (polynomial)',
    '<b>2. MEASURE ERROR:</b> How far off? → eᵢ, SSE, MSE, RMSE, MAE, R²',
    '<b>3. FIND BEST PARAMETERS:</b> Which w minimises MSE? → least squares (XᵀX)⁻¹Xᵀy',
    '<b>4. ASSESS GENERALISATION:</b> Will it work on new data? → compare training vs deployment error',
], color=PURPLE))

story.append(Spacer(1, 16))
story.append(Paragraph('"Embrace the error!" — Dr Requena Carrión 🏛️', s_footer))
story.append(Paragraph('Atlas · ML Week 2 Regression Cheat Sheet · 19 February 2026', s_footer))

doc.build(story)
print(f'✅ Built: {OUTPUT}')
