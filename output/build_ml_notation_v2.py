#!/usr/bin/env python3
"""ML Week 4 — Visual Notation Cheat Sheet v2 (fixed rendering)"""

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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)

OUTPUT = '/home/ubuntu/clawd/output/ml-week4-notation-cheatsheet.pdf'

NAVY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#e94560')
TEAL = colors.HexColor('#0f969c')
GOLD = colors.HexColor('#f5a623')
PURPLE = colors.HexColor('#9b59b6')
LIGHT = colors.HexColor('#f8f9fa')

# Chart colours (on white bg)
C_RED = '#e94560'
C_BLUE = '#4a90d9'
C_GOLD = '#f5a623'
C_TEAL = '#0f969c'
C_PURPLE = '#9b59b6'
C_NAVY = '#1e3a5f'
C_GREY = '#888888'
C_LIGHT = '#f0f0f0'


def fig_logistic():
    """The logistic function S-curve."""
    fig, ax = plt.subplots(figsize=(6, 3.2))
    
    x = np.linspace(-6, 6, 200)
    y = 1 / (1 + np.exp(-x))
    
    # Shaded zones (solid light colours, no alpha)
    ax.fill_between(x[x < -0.5], 0, y[x < -0.5], color='#dbe9f7', linewidth=0)
    ax.fill_between(x[x > 0.5], 0, y[x > 0.5], color='#fde0e5', linewidth=0)
    
    ax.plot(x, y, color=C_RED, linewidth=3, zorder=3)
    ax.axhline(y=0.5, color='#ccc', linestyle='--', linewidth=1, zorder=1)
    ax.axvline(x=0, color='#ccc', linestyle='--', linewidth=1, zorder=1)
    
    # Key points with offset annotations (no overlap)
    ax.scatter([0], [0.5], color=C_GOLD, s=80, zorder=5, edgecolors=C_NAVY, linewidth=1.5)
    ax.annotate('p(0) = 0.5\n"On the boundary"', (0, 0.5),
               textcoords='offset points', xytext=(50, -30),
               fontsize=8, color=C_NAVY, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbe6', edgecolor=C_GOLD, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_GOLD, linewidth=1.5))
    
    ax.scatter([2], [0.88], color=C_RED, s=80, zorder=5, edgecolors=C_NAVY, linewidth=1.5)
    ax.annotate('p(2) ≈ 0.88\n"88% sure it\'s △"', (2, 0.88),
               textcoords='offset points', xytext=(40, 10),
               fontsize=8, color=C_NAVY, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#fde0e5', edgecolor=C_RED, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_RED, linewidth=1.5))
    
    ax.scatter([-2], [0.12], color=C_BLUE, s=80, zorder=5, edgecolors=C_NAVY, linewidth=1.5)
    ax.annotate('p(−2) ≈ 0.12\n"88% sure it\'s ○"', (-2, 0.12),
               textcoords='offset points', xytext=(-100, 30),
               fontsize=8, color=C_NAVY, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#dbe9f7', edgecolor=C_BLUE, linewidth=1.5),
               arrowprops=dict(arrowstyle='->', color=C_BLUE, linewidth=1.5))
    
    ax.text(-4.5, 0.92, 'Class ○ zone', color=C_BLUE, fontsize=9, fontweight='bold', ha='center')
    ax.text(4.5, 0.08, 'Class △ zone', color=C_RED, fontsize=9, fontweight='bold', ha='center')
    
    ax.set_xlabel('d = wᵀx  (distance from boundary)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_ylabel('p(d) = probability', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.set_title('The Logistic Function: Any Number → Probability (0 to 1)', fontsize=12, fontweight='bold', color=C_NAVY, pad=10)
    ax.set_ylim(-0.05, 1.08)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=8)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_linear_classifier():
    """Linear classifier — good vs bad boundaries."""
    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    np.random.seed(42)
    
    for idx, (ax, title) in enumerate(zip(axes,
        ['wᵀx = 0 defines\nthe boundary', 'Good boundary\n(clear margin)', 'Bad boundary\n(too close to data)'])):
        
        c1_x = np.random.randn(15) * 0.8 + 2
        c1_y = np.random.randn(15) * 0.8 + 2
        c2_x = np.random.randn(15) * 0.8 - 1
        c2_y = np.random.randn(15) * 0.8 - 1
        
        ax.scatter(c1_x, c1_y, color=C_RED, s=45, marker='^', edgecolors='white', linewidth=0.8, label='Class △', zorder=3)
        ax.scatter(c2_x, c2_y, color=C_BLUE, s=45, marker='o', edgecolors='white', linewidth=0.8, label='Class ○', zorder=3)
        
        bx = np.linspace(-3, 4, 100)
        
        if idx == 0:
            by = -bx + 0.5
            # Light shading with solid colours
            ax.fill_between(bx, by, 5, color='#fde0e5', zorder=0)
            ax.fill_between(bx, -4, by, color='#dbe9f7', zorder=0)
            ax.text(2.8, -2.2, 'wᵀx > 0', color=C_RED, fontsize=8, fontweight='bold', ha='center')
            ax.text(-1.8, 3.2, 'wᵀx < 0', color=C_BLUE, fontsize=8, fontweight='bold', ha='center')
        elif idx == 1:
            by = -bx + 0.5
            ax.fill_between(bx, by, 5, color='#fde0e5', zorder=0)
            ax.fill_between(bx, -4, by, color='#dbe9f7', zorder=0)
            ax.plot(bx, -bx + 1.5, '--', color='#bbb', linewidth=1)
            ax.plot(bx, -bx - 0.5, '--', color='#bbb', linewidth=1)
            ax.text(3, -2.5, 'wide margin ✓', color=C_TEAL, fontsize=7, fontweight='bold', ha='center')
        elif idx == 2:
            by = -bx + 2.5
            ax.fill_between(bx, by, 5, color='#fde0e5', zorder=0)
            ax.fill_between(bx, -4, by, color='#dbe9f7', zorder=0)
            ax.text(0.5, -2.5, 'misclassifies ✗', color=C_RED, fontsize=7, fontweight='bold', ha='center')
        
        ax.plot(bx, by, color=C_GOLD, linewidth=2.5, zorder=2)
        ax.set_xlim(-3, 4)
        ax.set_ylim(-3, 4)
        ax.set_title(title, fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=6)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_knn():
    """kNN — how K changes the decision boundary."""
    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    np.random.seed(7)
    
    for ax, k, desc in zip(axes, [1, 3, 15],
        ['K=1: Overfitting\n(wiggly boundary)', 'K=3: Balanced\n(just right)', 'K=15: Underfitting\n(too smooth)']):
        
        c1_x = np.random.randn(20) * 1.0 + 2
        c1_y = np.random.randn(20) * 1.0 + 1.5
        c2_x = np.random.randn(20) * 1.0 - 0.5
        c2_y = np.random.randn(20) * 1.0 - 0.5
        
        ax.scatter(c1_x, c1_y, color=C_RED, s=35, marker='^', edgecolors='white', linewidth=0.5, zorder=3)
        ax.scatter(c2_x, c2_y, color=C_BLUE, s=35, marker='o', edgecolors='white', linewidth=0.5, zorder=3)
        
        xx, yy = np.meshgrid(np.linspace(-3, 5, 80), np.linspace(-3, 5, 80))
        all_x = np.concatenate([c1_x, c2_x])
        all_y = np.concatenate([c1_y, c2_y])
        all_labels = np.concatenate([np.ones(20), np.zeros(20)])
        
        Z = np.zeros(xx.shape)
        for i in range(xx.shape[0]):
            for j in range(xx.shape[1]):
                dists = np.sqrt((all_x - xx[i, j])**2 + (all_y - yy[i, j])**2)
                nearest_idx = np.argsort(dists)[:k]
                Z[i, j] = np.mean(all_labels[nearest_idx])
        
        # Solid light colours instead of alpha
        ax.contourf(xx, yy, Z, levels=[0, 0.5, 1], colors=['#dbe9f7', '#fde0e5'])
        ax.contour(xx, yy, Z, levels=[0.5], colors=[C_GOLD], linewidths=2.5)
        
        # Re-plot points on top
        ax.scatter(c1_x, c1_y, color=C_RED, s=35, marker='^', edgecolors='white', linewidth=0.5, zorder=3)
        ax.scatter(c2_x, c2_y, color=C_BLUE, s=35, marker='o', edgecolors='white', linewidth=0.5, zorder=3)
        
        ax.set_xlim(-3, 5)
        ax.set_ylim(-3, 4.5)
        ax.set_title(desc, fontsize=9, fontweight='bold', color=C_NAVY, pad=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=6)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_accuracy():
    """Visual: accuracy and error rate."""
    fig, ax = plt.subplots(figsize=(6, 2.2))
    
    predictions = ['✓', '✓', '✗', '✓', '✓', '✓', '✗', '✓', '✓', '✓']
    bg_cols = ['#e8f5e9' if p == '✓' else '#fce4ec' for p in predictions]
    border_cols = ['#2ecc71' if p == '✓' else '#e94560' for p in predictions]
    text_cols = ['#2e7d32' if p == '✓' else '#c62828' for p in predictions]
    
    for i, (pred, bg, bc, tc) in enumerate(zip(predictions, bg_cols, border_cols, text_cols)):
        rect = plt.Rectangle((i * 0.9, 0), 0.8, 0.8, facecolor=bg, edgecolor=bc, linewidth=2)
        ax.add_patch(rect)
        ax.text(i * 0.9 + 0.4, 0.4, pred, ha='center', va='center', fontsize=16, color=tc, fontweight='bold')
        ax.text(i * 0.9 + 0.4, -0.2, f'x{i+1}', ha='center', va='center', fontsize=7, color=C_GREY)
    
    ax.set_xlim(-0.2, 9.2)
    ax.set_ylim(-0.5, 1.7)
    ax.axis('off')
    
    ax.text(4.5, 1.4, 'Â = 8/10 = 80%      Ê = 2/10 = 20%      Ê = 1 − Â',
            ha='center', fontsize=12, color=C_NAVY, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fffbe6', edgecolor=C_GOLD, linewidth=2))
    
    ax.text(4.5, 1.0, '✓ = correct (ŷ = y)          ✗ = wrong (ŷ ≠ y)',
            ha='center', fontsize=9, color=C_GREY)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_likelihood():
    """Likelihood — multiply certainties."""
    fig, ax = plt.subplots(figsize=(6, 2.5))
    
    certainties = [0.88, 0.92, 0.73, 0.95]
    labels_list = ['△', '○', '△', '○']
    bar_cols = [C_RED, C_BLUE, C_RED, C_BLUE]
    bg_cols = ['#fde0e5', '#dbe9f7', '#fde0e5', '#dbe9f7']
    
    for i, (cert, lab, col, bg) in enumerate(zip(certainties, labels_list, bar_cols, bg_cols)):
        x_pos = i * 2.2
        ax.barh(0, cert, left=x_pos, height=0.5, color=bg, edgecolor=col, linewidth=2)
        ax.text(x_pos + cert / 2, 0, f'{cert:.0%}', ha='center', va='center', fontsize=11, color=C_NAVY, fontweight='bold')
        ax.text(x_pos + 0.5, -0.45, f'Sample {i+1}\nclass {lab}', ha='center', fontsize=8, color=C_GREY)
    
    L = math.prod(certainties)
    ax.text(4.2, 0.7, f'L = {certainties[0]} × {certainties[1]} × {certainties[2]} × {certainties[3]} = {L:.3f}',
            ha='center', fontsize=11, color=C_NAVY, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbe6', edgecolor=C_GOLD, linewidth=1.5))
    
    ax.text(4.2, 1.1, 'Likelihood L = multiply all certainties together',
            ha='center', fontsize=10, color=C_NAVY, fontweight='bold')
    ax.text(4.2, 1.45, 'Log-likelihood l = add log(certainty) for each sample  (same idea, easier maths)',
            ha='center', fontsize=8, color=C_GREY)
    
    ax.set_xlim(-0.3, 8.8)
    ax.set_ylim(-0.8, 1.7)
    ax.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_pipeline():
    """ML classification pipeline."""
    fig, ax = plt.subplots(figsize=(7, 1.8))
    
    steps = [
        ('Data\n{(xᵢ, yᵢ)}', C_BLUE),
        ('Choose Model\nLinear / kNN', C_PURPLE),
        ('Train\nFind best w\nor store data', C_GOLD),
        ('Predict\nŷ = f(x)', C_RED),
        ('Evaluate\nÂ, Ê, L', C_TEAL),
    ]
    
    for i, (text, col) in enumerate(steps):
        x = i * 1.5
        # Use lighter fill versions
        light_col = {'#4a90d9': '#dbe9f7', '#9b59b6': '#ede0f5', '#f5a623': '#fef3d6', 
                     '#e94560': '#fde0e5', '#0f969c': '#d6f0f0'}[col]
        rect = FancyBboxPatch((x, 0.1), 1.2, 0.8, boxstyle='round,pad=0.1',
                               facecolor=light_col, edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.6, 0.5, text, ha='center', va='center', fontsize=7.5, color=C_NAVY, fontweight='bold')
        
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + 1.4, 0.5), xytext=(x + 1.25, 0.5),
                        arrowprops=dict(arrowstyle='->', color=C_NAVY, linewidth=2))
    
    ax.set_xlim(-0.2, 7.5)
    ax.set_ylim(-0.1, 1.1)
    ax.axis('off')
    ax.set_title('The ML Classification Pipeline', fontsize=12, fontweight='bold', color=C_NAVY, pad=5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def fig_symbols_map():
    """Symbol relationship map."""
    fig, ax = plt.subplots(figsize=(7, 4))
    
    nodes = {
        'x':    (1.5, 3,   C_BLUE,   'x\nInput'),
        'y':    (5,   3.8, '#2ecc71', 'y\nTrue label'),
        'yhat': (5,   1.2, C_RED,    'ŷ\nPrediction'),
        'w':    (0.5, 1,   C_GOLD,   'w\nWeights'),
        'f':    (3.2, 1.8, C_PURPLE, 'f(x)\nModel'),
        'A':    (6.5, 2.5, C_TEAL,   'Â\nAccuracy'),
        'L':    (6.5, 4,   C_RED,    'L\nLikelihood'),
        'p':    (3.5, 4,   C_GOLD,   'p(x)\nProbability'),
    }
    
    connections = [
        ('x', 'f'), ('w', 'f'), ('f', 'yhat'),
        ('y', 'A'), ('yhat', 'A'), ('f', 'p'), ('p', 'L'),
    ]
    
    for n1, n2 in connections:
        x1, y1 = nodes[n1][0], nodes[n1][1]
        x2, y2 = nodes[n2][0], nodes[n2][1]
        ax.plot([x1, x2], [y1, y2], color='#cccccc', linewidth=2, zorder=1)
    
    for name, (x, y, col, label) in nodes.items():
        light = {'#4a90d9': '#dbe9f7', '#2ecc71': '#d4efdf', '#e94560': '#fde0e5',
                 '#f5a623': '#fef3d6', '#9b59b6': '#ede0f5', '#0f969c': '#d6f0f0'}[col]
        circle = plt.Circle((x, y), 0.55, facecolor=light, edgecolor=col, linewidth=2.5, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, color=C_NAVY, fontweight='bold', zorder=3)
    
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title('How All The Symbols Connect', fontsize=13, fontweight='bold', color=C_NAVY, pad=10)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


# ─── Build PDF (same layout as before) ───────────────

doc = SimpleDocTemplate(OUTPUT, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.4*inch,
                        leftMargin=0.6*inch, rightMargin=0.6*inch)
styles = getSampleStyleSheet()

s_title = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
s_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11, textColor=colors.gray, spaceAfter=12, alignment=TA_CENTER)
s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15, textColor=NAVY, spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
s_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=ACCENT, spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
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

# PAGE 1
story.append(Spacer(1, 20))
story.append(Paragraph('ML Week 4 — Notation Cheat Sheet', s_title))
story.append(Paragraph('Classification: Linear Classifiers, Logistic Regression & kNN', s_sub))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=2))
story.append(Spacer(1, 8))

story.append(Image(fig_pipeline(), width=460, height=125))
story.append(Paragraph('Every equation in the lecture serves one of these steps.', s_caption))

story.append(Paragraph('The Core Symbols', s_h1))

sym_data = [
    ['Symbol', 'Name', 'Plain English', 'Think of it as...'],
    ['x', 'Input / predictors', 'The features we measure', '"The stuff we know about each sample"'],
    ['xᵢ', 'Sample i', 'The i-th data point', '"Row i in the spreadsheet"'],
    ['y', 'True label', 'The correct class', '"The right answer"'],
    ['ŷ  (y-hat)', 'Prediction', 'What the model guesses', '"Our guess" — hat (ˆ) = estimated'],
    ['f(x)', 'Model / classifier', 'Function that predicts', '"The prediction machine"'],
    ['w', 'Weights', 'Model parameters', '"How important each feature is"'],
    ['wᵀx', 'Dot product', 'Weights × features, summed', '"Score: which side of the line?"'],
    ['N', 'Sample count', 'Number of data points', '"How many rows"'],
    ['K', 'Neighbours (kNN)', 'Nearby points to check', '"Ask K nearest friends to vote"'],
    ['Â', 'Accuracy', '#correct / #total', '"What % did we get right?"'],
    ['Ê = 1 − Â', 'Error rate', '#wrong / #total', '"What % did we get wrong?"'],
    ['p(x)', 'Probability', 'Certainty of classification', '"How confident are we?"'],
    ['L = ∏ p(xᵢ)', 'Likelihood', 'Product of all certainties', '"Multiply all confidences together"'],
    ['l = Σ log p(xᵢ)', 'Log-likelihood', 'Sum of log certainties', '"Add logs instead of multiplying"'],
]

sym_table = Table(sym_data, colWidths=[70, 85, 130, 170])
sym_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8.5),
    ('FONTSIZE', (0,1), (-1,-1), 8), ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(sym_table)

story.append(PageBreak())

# PAGE 2
story.append(Paragraph('How The Symbols Connect', s_h1))
story.append(Image(fig_symbols_map(), width=440, height=260))
story.append(Paragraph('Follow the connections — features (x) go into the model (f), which outputs predictions (ŷ), compared against truth (y) for accuracy (Â).', s_caption))

story.append(Paragraph('Linear Classifiers: Which Side of the Line?', s_h1))
story.append(Image(fig_linear_classifier(), width=470, height=190))
story.append(Paragraph('The gold line is wᵀx = 0. Left: basic split. Centre: well-placed with margin. Right: badly placed, misclassifies points.', s_caption))

story.extend(box('🔑 Linear Classifier — Key Rules', [
    '<b>wᵀx = 0</b> → you\'re ON the boundary',
    '<b>wᵀx > 0</b> → one side → predict class △',
    '<b>wᵀx < 0</b> → other side → predict class ○',
    'Further from boundary = more confident',
    '<b>Linearly separable</b> = perfect line exists (Â = 1). <b>Non-separable</b> = best line still has errors.',
], color=TEAL))

story.append(PageBreak())

# PAGE 3
story.append(Paragraph('Accuracy & Error Rate', s_h1))
story.append(Image(fig_accuracy(), width=440, height=160))
story.append(Paragraph('Count correct vs wrong. Accuracy = correct/total. Error = wrong/total = 1 − accuracy.', s_caption))

story.extend(box('🧮 Symbol Shortcuts', [
    '<b>∏</b> (capital Pi) = "multiply all" — just like <b>Σ</b> = "add all"',
    '<b>ˆ</b> (hat) = "estimated/predicted" — ŷ is predicted y, Â is estimated accuracy',
    '<b>ᵀ</b> (superscript T) = transpose — in practice just means "dot product"',
    '<b>log</b> = turns multiplication into addition (easier maths, same result)',
], color=ACCENT))

story.append(Paragraph('The Logistic Function', s_h1))
story.append(Image(fig_logistic(), width=420, height=225))
story.append(Paragraph('The S-curve: any number in → probability out. Positive = likely △, negative = likely ○, zero = 50/50.', s_caption))

story.extend(box('🔑 Logistic Regression — What to Remember', [
    'p(d) = eᵈ / (1 + eᵈ)  where d = wᵀx',
    'd = 0 → p = 0.5 (on the boundary, 50/50)',
    'd large positive → p ≈ 1 (confident it\'s △)',
    'd large negative → p ≈ 0 (confident it\'s ○)',
    'Called "regression" because we regress on probability, not class directly',
    'Best logistic classifier <b>maximises likelihood L</b>, found via <b>gradient descent</b>',
]))

story.append(PageBreak())

# PAGE 4
story.append(Paragraph('Likelihood: Quality Metric for Logistic Regression', s_h1))
story.append(Image(fig_likelihood(), width=440, height=185))
story.append(Paragraph('Each sample has a certainty. Multiply them all → higher L = better boundary.', s_caption))

story.extend(box('💡 Why Not Just Use Accuracy?', [
    'Accuracy is binary — right or wrong, no "almost right"',
    'Likelihood measures HOW CONFIDENT the classifier is — richer metric',
    'Two classifiers can have same accuracy but different likelihoods',
    'Higher L = more confident overall = better model',
    'Logistic regression maximises L, not accuracy directly',
], color=PURPLE))

story.append(Paragraph('k Nearest Neighbours (kNN)', s_h1))
story.append(Image(fig_knn(), width=470, height=190))
story.append(Paragraph('K=1: overfits. K=3: balanced. K=15: underfits. Gold line = decision boundary.', s_caption))

story.extend(box('🔑 kNN — Key Rules', [
    'Classify new point: find K closest training samples, majority vote wins',
    '<b>Small K</b> → complex boundary → overfitting',
    '<b>Large K</b> → smooth boundary → underfitting',
    'Binary problems: use <b>odd K</b> to avoid ties',
    '<b>Non-parametric</b> — no assumed shape. <b>No training</b> — stores entire dataset.',
    'Called <b>instance-based</b> or <b>lazy</b> method',
], color=TEAL))

story.append(PageBreak())

# PAGE 5: Quick Reference
story.append(Paragraph('One-Page Quick Reference', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 6))

story.extend(box('📐 NOTATION DECODER', [
    '<b>xᵢ</b> = sample i  |  <b>yᵢ</b> = true label  |  <b>ŷᵢ</b> = predicted label  |  <b>N</b> = total samples',
    '<b>w</b> = weights  |  <b>wᵀx</b> = dot product (score)  |  <b>K</b> = number of neighbours',
    '<b>Â</b> = accuracy (#correct/#total)  |  <b>Ê</b> = error rate (1 − Â)',
    '<b>p(x)</b> = logistic probability  |  <b>L</b> = likelihood (∏ certainties)  |  <b>l</b> = log-likelihood (Σ logs)',
    '<b>Σ</b> = add all  |  <b>∏</b> = multiply all  |  <b>ˆ</b> = estimated  |  <b>ᵀ</b> = transpose',
], color=NAVY))

story.extend(box('🧠 THREE MODELS COMPARED', [
    '<b>Linear classifier:</b> Straight-line boundary. wᵀx = 0. Parametric. Simple but rigid.',
    '<b>Logistic regression:</b> Linear + probability. Maximises likelihood L via gradient descent.',
    '<b>kNN:</b> No assumed shape. Vote of K nearest. Non-parametric. No training. K controls complexity.',
], color=ACCENT))

story.extend(box('⚖️ THE FLEXIBILITY TRADE-OFF', [
    '<b>Too simple</b> (underfitting) → misses pattern → low accuracy on training AND test',
    '<b>Too complex</b> (overfitting) → memorises noise → high training, LOW test accuracy',
    '<b>Just right</b> → captures pattern, ignores noise → good on BOTH',
    'Linear: always same complexity. kNN: small K = complex, large K = simple.',
], color=TEAL))

story.extend(box('🎯 EVERY EQUATION DOES ONE OF THREE THINGS', [
    '<b>1. CLASSIFY:</b> Which side of the line? → wᵀx (positive or negative)',
    '<b>2. MEASURE QUALITY:</b> How many right? → Â, Ê. How confident? → L, l',
    '<b>3. FIND THE BEST MODEL:</b> Maximise L (logistic) or choose K (kNN)',
], color=PURPLE))

story.append(Spacer(1, 16))
story.append(Paragraph('The notation is just shorthand for simple ideas. You\'ve got this. 🏛️', s_footer))
story.append(Paragraph('Atlas · ML Week 4 · 19 February 2026', s_footer))

doc.build(story)
print(f'✅ Built: {OUTPUT}')
