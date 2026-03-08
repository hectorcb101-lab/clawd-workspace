#!/usr/bin/env python3
"""ML Week 4 — Visual Notation Cheat Sheet"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image, KeepTogether
)

OUTPUT = '/home/ubuntu/clawd/output/ml-week4-notation-cheatsheet.pdf'

NAVY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#e94560')
TEAL = colors.HexColor('#0f969c')
GOLD = colors.HexColor('#f5a623')
PURPLE = colors.HexColor('#9b59b6')
LIGHT = colors.HexColor('#f8f9fa')
BG = '#ffffff'
FG = '#1a1a2e'  # text colour on white

# ─── Matplotlib Visuals ───────────────────────────────

def fig_logistic():
    """Visual: the logistic function — turning numbers into probabilities."""
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    
    x = np.linspace(-6, 6, 200)
    y = 1 / (1 + np.exp(-x))
    
    ax.plot(x, y, color='#e94560', linewidth=3)
    ax.axhline(y=0.5, color='#444', linestyle='--', linewidth=1)
    ax.axvline(x=0, color='#444', linestyle='--', linewidth=1)
    
    # Annotate key points
    points = [(0, 0.5, 'p(0) = 0.5\n"50/50 — right on\nthe boundary"'),
              (2, 0.88, 'p(2) ≈ 0.88\n"88% confident\nit\'s class △"'),
              (-2, 0.12, 'p(−2) ≈ 0.12\n"88% confident\nit\'s class ○"')]
    
    for px, py, label in points:
        ax.scatter(px, py, color='#e94560', s=80, zorder=5, edgecolors='white', linewidth=1.5)
        offset = (15, 15) if px >= 0 else (-15, -20)
        ax.annotate(label, (px, py), textcoords='offset points', xytext=offset,
                   fontsize=8, color='white', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#e94560', linewidth=1),
                   arrowprops=dict(arrowstyle='->', color='#e94560', linewidth=1.5))
    
    # Labels
    ax.set_xlabel('d = wᵀx  (distance from boundary)', color='white', fontsize=10, fontweight='bold')
    ax.set_ylabel('p(d) = probability', color='white', fontsize=10, fontweight='bold')
    ax.set_title('The Logistic Function: Any Number → Probability (0 to 1)', 
                color='white', fontsize=12, fontweight='bold', pad=10)
    
    ax.set_ylim(-0.05, 1.1)
    ax.tick_params(colors='white', labelsize=8)
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add zones
    ax.fill_between(x[x < -1], 0, y[x < -1], alpha=0.15, color='#4a90d9')
    ax.fill_between(x[x > 1], 0, y[x > 1], alpha=0.15, color='#e94560')
    ax.text(-4, 0.85, 'Class ○ zone', color='#4a90d9', fontsize=9, fontweight='bold', ha='center')
    ax.text(4, 0.15, 'Class △ zone', color='#e94560', fontsize=9, fontweight='bold', ha='center')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_linear_classifier():
    """Visual: linear classifier — which side of the line?"""
    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    fig.patch.set_facecolor(BG)
    
    np.random.seed(42)
    
    for idx, (ax, title, k_or_type) in enumerate(zip(axes, 
        ['Linear Boundary\nwᵀx = 0', 'Good Boundary\n(high certainty)', 'Bad Boundary\n(low certainty)'],
        ['basic', 'good', 'bad'])):
        
        ax.set_facecolor(BG)
        
        # Generate two clusters
        c1_x = np.random.randn(15) * 0.8 + 2
        c1_y = np.random.randn(15) * 0.8 + 2
        c2_x = np.random.randn(15) * 0.8 - 1
        c2_y = np.random.randn(15) * 0.8 - 1
        
        ax.scatter(c1_x, c1_y, color='#e94560', s=40, marker='^', edgecolors='white', linewidth=0.5, label='Class △', zorder=3)
        ax.scatter(c2_x, c2_y, color='#4a90d9', s=40, marker='o', edgecolors='white', linewidth=0.5, label='Class ○', zorder=3)
        
        # Draw boundary line
        bx = np.linspace(-3, 4, 100)
        if k_or_type == 'basic':
            by = -bx + 0.5
            ax.fill_between(bx, by, 5, alpha=0.08, color='#e94560')
            ax.fill_between(bx, -4, by, alpha=0.08, color='#4a90d9')
        elif k_or_type == 'good':
            by = -bx + 0.5
            ax.fill_between(bx, by, 5, alpha=0.08, color='#e94560')
            ax.fill_between(bx, -4, by, alpha=0.08, color='#4a90d9')
            # Show margin
            ax.plot(bx, -bx + 1.5, '--', color='#666', linewidth=0.8)
            ax.plot(bx, -bx - 0.5, '--', color='#666', linewidth=0.8)
            ax.annotate('margin', xy=(2.5, -1.5), fontsize=7, color='#999', ha='center')
        elif k_or_type == 'bad':
            by = -bx + 2.5  # Badly placed
            ax.fill_between(bx, by, 5, alpha=0.08, color='#e94560')
            ax.fill_between(bx, -4, by, alpha=0.08, color='#4a90d9')
        
        ax.plot(bx, by if k_or_type != 'basic' else -bx + 0.5, color='#f5a623', linewidth=2, zorder=2)
        
        ax.set_xlim(-3, 4)
        ax.set_ylim(-3, 4)
        ax.set_title(title, color='white', fontsize=9, fontweight='bold', pad=8)
        ax.tick_params(colors='white', labelsize=6)
        ax.spines['bottom'].set_color('#333')
        ax.spines['left'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        if idx == 0:
            ax.text(2.5, -2.5, 'wᵀx > 0\n(this side)', color='#e94560', fontsize=7, ha='center', fontweight='bold')
            ax.text(-1.5, 3, 'wᵀx < 0\n(that side)', color='#4a90d9', fontsize=7, ha='center', fontweight='bold')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_knn():
    """Visual: kNN — how K changes the boundary."""
    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    fig.patch.set_facecolor(BG)
    
    np.random.seed(7)
    
    for ax, k, desc in zip(axes, [1, 3, 15], 
        ['K=1: Overfitting\n(too wiggly)', 'K=3: Just right\n(balanced)', 'K=15: Underfitting\n(too smooth)']):
        ax.set_facecolor(BG)
        
        c1_x = np.random.randn(20) * 1.0 + 2
        c1_y = np.random.randn(20) * 1.0 + 1.5
        c2_x = np.random.randn(20) * 1.0 - 0.5
        c2_y = np.random.randn(20) * 1.0 - 0.5
        
        ax.scatter(c1_x, c1_y, color='#e94560', s=35, marker='^', edgecolors='white', linewidth=0.5, zorder=3)
        ax.scatter(c2_x, c2_y, color='#4a90d9', s=35, marker='o', edgecolors='white', linewidth=0.5, zorder=3)
        
        # Create a mesh to show decision regions
        xx, yy = np.meshgrid(np.linspace(-3, 5, 100), np.linspace(-3, 5, 100))
        all_x = np.concatenate([c1_x, c2_x])
        all_y = np.concatenate([c1_y, c2_y])
        all_labels = np.concatenate([np.ones(20), np.zeros(20)])
        
        # Simple kNN on mesh
        Z = np.zeros(xx.shape)
        for i in range(xx.shape[0]):
            for j in range(xx.shape[1]):
                dists = np.sqrt((all_x - xx[i,j])**2 + (all_y - yy[i,j])**2)
                nearest_idx = np.argsort(dists)[:k]
                Z[i,j] = np.mean(all_labels[nearest_idx])
        
        ax.contourf(xx, yy, Z, levels=[0, 0.5, 1], colors=['#4a90d9', '#e94560'], alpha=0.12)
        ax.contour(xx, yy, Z, levels=[0.5], colors=['#f5a623'], linewidths=2)
        
        ax.set_xlim(-3, 5)
        ax.set_ylim(-3, 4.5)
        ax.set_title(desc, color='white', fontsize=9, fontweight='bold', pad=8)
        ax.tick_params(colors='white', labelsize=6)
        ax.spines['bottom'].set_color('#333')
        ax.spines['left'].set_color('#333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_accuracy():
    """Visual: accuracy and error rate."""
    fig, ax = plt.subplots(figsize=(6, 2.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    
    # Show 10 predictions
    predictions = ['✓', '✓', '✗', '✓', '✓', '✓', '✗', '✓', '✓', '✓']
    cols = ['#2ecc71' if p == '✓' else '#e94560' for p in predictions]
    
    for i, (pred, col) in enumerate(zip(predictions, cols)):
        rect = plt.Rectangle((i*0.9, 0), 0.8, 0.8, facecolor=col, alpha=0.3, edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(i*0.9 + 0.4, 0.4, pred, ha='center', va='center', fontsize=16, color='white', fontweight='bold')
        ax.text(i*0.9 + 0.4, -0.25, f'x{i+1}', ha='center', va='center', fontsize=7, color='#999')
    
    ax.set_xlim(-0.2, 9.2)
    ax.set_ylim(-0.6, 1.8)
    ax.axis('off')
    
    # Formula
    ax.text(4.5, 1.5, 'Â = 8/10 = 80%    Ê = 2/10 = 20%    Ê = 1 − Â', 
            ha='center', fontsize=12, color='white', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor='#f5a623', linewidth=2))
    
    ax.text(4.5, 1.1, '✓ = correct prediction (ŷ = y)        ✗ = wrong prediction (ŷ ≠ y)', 
            ha='center', fontsize=9, color='#999')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_likelihood():
    """Visual: likelihood — multiply certainties together."""
    fig, ax = plt.subplots(figsize=(6, 2.8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    
    # Show 4 samples with their certainties
    certainties = [0.88, 0.92, 0.73, 0.95]
    labels = ['△', '○', '△', '○']
    label_cols = ['#e94560', '#4a90d9', '#e94560', '#4a90d9']
    
    for i, (cert, lab, col) in enumerate(zip(certainties, labels, label_cols)):
        x_pos = i * 2.2
        # Bar
        ax.barh(0, cert, left=x_pos, height=0.5, color=col, alpha=0.4, edgecolor=col, linewidth=1.5)
        ax.text(x_pos + cert/2, 0, f'{cert:.0%}', ha='center', va='center', fontsize=11, color='white', fontweight='bold')
        ax.text(x_pos + 0.5, -0.5, f'Sample {i+1}\nclass {lab}', ha='center', fontsize=8, color='#ccc')
    
    # Multiply
    L = math.prod(certainties)
    ax.text(4.2, 0.8, f'L = {certainties[0]} × {certainties[1]} × {certainties[2]} × {certainties[3]} = {L:.3f}', 
            ha='center', fontsize=11, color='#f5a623', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#f5a623', linewidth=1.5))
    
    ax.text(4.2, 1.3, 'Likelihood L = multiply all individual certainties together', 
            ha='center', fontsize=9, color='white', fontweight='bold')
    ax.text(4.2, 1.6, 'Log-likelihood l = add up log(certainty) for each sample  (same idea, easier maths)',
            ha='center', fontsize=8, color='#999')
    
    ax.set_xlim(-0.3, 8.8)
    ax.set_ylim(-0.9, 1.9)
    ax.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_pipeline():
    """Visual: the ML classification pipeline."""
    fig, ax = plt.subplots(figsize=(7, 2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    
    steps = [
        ('Data\n{(xᵢ, yᵢ)}', '#4a90d9'),
        ('Choose Model\nLinear / kNN', '#9b59b6'),
        ('Train\nFind best w\nor store data', '#f5a623'),
        ('Predict\nŷ = f(x)', '#e94560'),
        ('Evaluate\nÂ, Ê, L', '#0f969c'),
    ]
    
    for i, (text, col) in enumerate(steps):
        x = i * 1.5
        rect = FancyBboxPatch((x, 0.1), 1.2, 0.8, boxstyle='round,pad=0.1',
                               facecolor=col, alpha=0.25, edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.6, 0.5, text, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + 1.4, 0.5), xytext=(x + 1.25, 0.5),
                        arrowprops=dict(arrowstyle='->', color='white', linewidth=2))
    
    ax.set_xlim(-0.2, 7.5)
    ax.set_ylim(-0.2, 1.2)
    ax.axis('off')
    ax.set_title('The ML Classification Pipeline', color='white', fontsize=12, fontweight='bold', pad=5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    buf.seek(0)
    return buf


def fig_symbols_map():
    """Visual: symbol relationship map."""
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    
    # Central nodes
    nodes = {
        'x': (2, 3, '#4a90d9', 'x\nInput features'),
        'y': (5, 3, '#2ecc71', 'y\nTrue label'),
        'yhat': (5, 1, '#e94560', 'ŷ\nPredicted label'),
        'w': (0.5, 1.5, '#f5a623', 'w\nWeights'),
        'f': (3.5, 1.5, '#9b59b6', 'f(x)\nModel'),
        'A': (6.5, 1.5, '#0f969c', 'Â\nAccuracy'),
        'L': (6.5, 3, '#e94560', 'L\nLikelihood'),
        'p': (5, 4.5, '#f5a623', 'p(x)\nProbability'),
    }
    
    # Draw connections
    connections = [
        ('x', 'f', 'features go into model'),
        ('w', 'f', 'weights define the boundary'),
        ('f', 'yhat', 'model outputs prediction'),
        ('y', 'A', 'compare with truth'),
        ('yhat', 'A', 'compare prediction'),
        ('f', 'p', 'logistic gives probability'),
        ('p', 'L', 'multiply certainties'),
    ]
    
    for n1, n2, _ in connections:
        x1, y1 = nodes[n1][0], nodes[n1][1]
        x2, y2 = nodes[n2][0], nodes[n2][1]
        ax.plot([x1, x2], [y1, y2], color='#444', linewidth=1.5, zorder=1)
    
    # Draw nodes
    for name, (x, y, col, label) in nodes.items():
        circle = plt.Circle((x, y), 0.55, facecolor=col, alpha=0.3, edgecolor=col, linewidth=2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=7.5, color='white', fontweight='bold', zorder=3)
    
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(0, 5.2)
    ax.axis('off')
    ax.set_title('How All The Symbols Connect', color='white', fontsize=13, fontweight='bold', pad=10)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG)
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

# ── PAGE 1: Title + Symbol Table + Pipeline ──
story.append(Spacer(1, 20))
story.append(Paragraph('ML Week 4 — Notation Cheat Sheet', s_title))
story.append(Paragraph('Classification: Linear Classifiers, Logistic Regression & kNN', s_sub))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=2))
story.append(Spacer(1, 8))

# Pipeline visual
story.append(Image(fig_pipeline(), width=460, height=140))
story.append(Paragraph('The ML classification pipeline — every equation serves one of these steps.', s_caption))

# Core symbols table
story.append(Paragraph('The Core Symbols', s_h1))

sym_data = [
    ['Symbol', 'Name', 'Plain English', 'Think of it as...'],
    ['x', 'Input / predictors', 'The features we measure', '"The stuff we know about each sample"'],
    ['xᵢ', 'Sample i', 'The i-th data point', '"Row i in the spreadsheet"'],
    ['y', 'True label', 'The correct class', '"The right answer"'],
    ['ŷ  (y-hat)', 'Prediction', 'What the model guesses', '"Our guess" — hat (ˆ) = estimated'],
    ['f(x)', 'Model / classifier', 'Function that predicts', '"The prediction machine"'],
    ['w', 'Weights / coefficients', 'Model parameters', '"How important each feature is"'],
    ['wᵀx', 'Dot product', 'Weights × features, summed', '"Score: which side of the line?"'],
    ['N', 'Sample count', 'Number of data points', '"How many rows"'],
    ['K', 'Neighbours (kNN)', 'How many nearby points to check', '"Ask K nearest friends to vote"'],
    ['Â', 'Accuracy', '#correct / #total', '"What % did we get right?"'],
    ['Ê = 1 − Â', 'Error rate', '#wrong / #total', '"What % did we get wrong?"'],
    ['p(x)', 'Probability (logistic)', 'Certainty of classification', '"How confident are we?"'],
    ['L = ∏ p(xᵢ)', 'Likelihood', 'Product of all certainties', '"Multiply all confidences together"'],
    ['l = Σ log p(xᵢ)', 'Log-likelihood', 'Sum of log certainties', '"Same thing, but add logs instead"'],
]

sym_table = Table(sym_data, colWidths=[70, 85, 130, 170])
sym_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 8.5),
    ('FONTSIZE', (0,1), (-1,-1), 8),
    ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(sym_table)

story.append(PageBreak())

# ── PAGE 2: Symbol Map + Linear Classifiers ──
story.append(Paragraph('How The Symbols Connect', s_h1))
story.append(Image(fig_symbols_map(), width=440, height=260))
story.append(Paragraph('Relationship map — follow the connections to see how each symbol feeds into the next.', s_caption))

story.append(Paragraph('Linear Classifiers: Which Side of the Line?', s_h1))
story.append(Image(fig_linear_classifier(), width=470, height=190))
story.append(Paragraph('Left: basic linear boundary. Centre: well-placed (margin). Right: poorly placed. The boundary is defined by wᵀx = 0.', s_caption))

story.extend(box('🔑 Linear Classifier — Key Rules', [
    '<b>wᵀx = 0</b> → you\'re ON the boundary (decision surface)',
    '<b>wᵀx > 0</b> → one side → predict class △',
    '<b>wᵀx < 0</b> → other side → predict class ○',
    'The further from the boundary, the more confident the classification',
    '<b>Linearly separable</b> = you CAN draw a perfect line (Â = 1)',
    '<b>Non-linearly separable</b> = best line still makes some errors (Â < 1)',
], color=TEAL))

story.append(PageBreak())

# ── PAGE 3: Accuracy + Logistic Function ──
story.append(Paragraph('Accuracy & Error Rate', s_h1))
story.append(Image(fig_accuracy(), width=440, height=180))
story.append(Paragraph('Count correct vs wrong predictions. That\'s literally it.', s_caption))

story.extend(box('🧮 Two Big Symbols Decoded', [
    '<b>∏</b> (capital Pi) = "multiply all of them together" — just like Σ means "add all"',
    '<b>ˆ</b> (hat) = "estimated / predicted" — Â is estimated accuracy, ŷ is predicted y',
    '<b>ᵀ</b> (superscript T) = transpose — in practice means "dot product"',
    '<b>log</b> = turns multiplication into addition (makes maths easier, same result)',
], color=ACCENT))

story.append(Paragraph('The Logistic Function', s_h1))
story.append(Image(fig_logistic(), width=420, height=220))
story.append(Paragraph('The S-curve that converts any number into a probability between 0 and 1.', s_caption))

story.extend(box('🔑 Logistic Regression — What You Need to Know', [
    'p(d) = eᵈ / (1 + eᵈ) where d = wᵀx (distance from boundary)',
    'd = 0 → p = 0.5 (50/50, sitting on the boundary)',
    'd large positive → p close to 1 (very confident it\'s class △)',
    'd large negative → p close to 0 (very confident it\'s class ○)',
    'It\'s called "regression" because we\'re regressing on the certainty (probability), not the class directly',
    'The BEST logistic classifier maximises the likelihood L (or log-likelihood l)',
    'Found using <b>gradient descent</b> (iteratively adjusting w to improve L)',
]))

story.append(PageBreak())

# ── PAGE 4: Likelihood + kNN ──
story.append(Paragraph('Likelihood: The Quality Metric for Logistic Regression', s_h1))
story.append(Image(fig_likelihood(), width=440, height=200))
story.append(Paragraph('Multiply each sample\'s certainty together → higher L = better boundary.', s_caption))

story.extend(box('💡 Why Not Just Use Accuracy?', [
    'Accuracy counts correct/wrong — it\'s binary (right or wrong, no "almost right")',
    'Likelihood measures HOW CONFIDENT the classifier is — a softer, richer metric',
    'Two classifiers might have the same accuracy but different likelihoods',
    'The one with higher L is more confident overall → better model',
    'Logistic regression maximises L, not accuracy directly',
], color=PURPLE))

story.append(Paragraph('k Nearest Neighbours (kNN)', s_h1))
story.append(Image(fig_knn(), width=470, height=190))
story.append(Paragraph('K=1: overfits (memorises noise). K=3: balanced. K=15: underfits (too smooth). The gold line is the decision boundary.', s_caption))

story.extend(box('🔑 kNN — Key Rules', [
    'To classify a new point: find K closest training samples, majority vote wins',
    '<b>Small K</b> (e.g. 1) → complex boundary → overfitting (memorises noise)',
    '<b>Large K</b> (e.g. 15) → smooth boundary → underfitting (misses patterns)',
    'For binary problems, use <b>odd K</b> to avoid ties',
    'kNN is <b>non-parametric</b> — no assumed shape for the boundary',
    'kNN has <b>no training step</b> — it stores the entire dataset and uses it at prediction time',
    'That\'s why it\'s called an <b>instance-based</b> or <b>lazy</b> method',
], color=TEAL))

story.append(PageBreak())

# ── PAGE 5: Quick Reference Card ──
story.append(Paragraph('One-Page Quick Reference', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 6))

story.extend(box('📐 NOTATION DECODER', [
    '<b>xᵢ</b> = sample i &nbsp;&nbsp;|&nbsp;&nbsp; <b>yᵢ</b> = true label &nbsp;&nbsp;|&nbsp;&nbsp; <b>ŷᵢ</b> = predicted label &nbsp;&nbsp;|&nbsp;&nbsp; <b>N</b> = total samples',
    '<b>w</b> = weights &nbsp;&nbsp;|&nbsp;&nbsp; <b>wᵀx</b> = dot product (score) &nbsp;&nbsp;|&nbsp;&nbsp; <b>K</b> = number of neighbours',
    '<b>Â</b> = accuracy (#correct / #total) &nbsp;&nbsp;|&nbsp;&nbsp; <b>Ê</b> = error rate (1 − Â)',
    '<b>p(x)</b> = logistic probability &nbsp;&nbsp;|&nbsp;&nbsp; <b>L</b> = likelihood (∏ certainties) &nbsp;&nbsp;|&nbsp;&nbsp; <b>l</b> = log-likelihood (Σ log certainties)',
    '<b>Σ</b> = add all &nbsp;&nbsp;|&nbsp;&nbsp; <b>∏</b> = multiply all &nbsp;&nbsp;|&nbsp;&nbsp; <b>ˆ</b> = estimated &nbsp;&nbsp;|&nbsp;&nbsp; <b>ᵀ</b> = transpose/dot product',
], color=NAVY))

story.extend(box('🧠 THREE MODELS COMPARED', [
    '<b>Linear classifier:</b> Straight-line boundary. wᵀx = 0. Parametric. Simple but rigid.',
    '<b>Logistic regression:</b> Linear classifier + probability. Uses likelihood (not accuracy) to find best boundary. Gradient descent.',
    '<b>kNN:</b> No boundary assumed. Vote of K nearest neighbours. Non-parametric. No training. K controls complexity.',
], color=ACCENT))

story.extend(box('⚖️ THE FLEXIBILITY TRADE-OFF', [
    '<b>Too simple</b> (underfitting) → misses the real pattern → low training AND test accuracy',
    '<b>Too complex</b> (overfitting) → memorises noise → high training accuracy, LOW test accuracy',
    '<b>Just right</b> → captures the pattern, ignores noise → good on BOTH training and test',
    'Linear classifiers: always same complexity (one straight line)',
    'kNN: K controls it — small K = complex (overfit), large K = simple (underfit)',
], color=TEAL))

story.extend(box('🎯 EXAM PATTERN: EVERY EQUATION DOES ONE OF THREE THINGS', [
    '<b>1. CLASSIFY:</b> Which side of the line? → wᵀx (positive or negative)',
    '<b>2. MEASURE QUALITY:</b> How many right? → Â, Ê. How confident? → L, l',
    '<b>3. FIND THE BEST MODEL:</b> Maximise L (logistic) or choose K (kNN)',
], color=PURPLE))

story.append(Spacer(1, 16))
story.append(Paragraph('The notation looks intimidating but it\'s just shorthand for simple ideas. You\'ve got this. 🏛️', s_footer))
story.append(Paragraph('Atlas · ML Week 4 Notation Cheat Sheet · 19 February 2026', s_footer))

doc.build(story)
print(f'✅ Built: {OUTPUT}')
