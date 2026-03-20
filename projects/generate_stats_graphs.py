#!/usr/bin/env python3
"""
Generate all matplotlib visualizations for Stats Recap Guide v4
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.special import comb

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'figure.dpi': 150,
    'figure.figsize': (8, 5)
})

OUTPUT_DIR = '/home/ubuntu/clawd/projects/stats-graphs/'

# 1. BAR CHART OF PROFITS WITH MEAN LINE
def plot_bar_chart_profits():
    months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    profits = [2.0, 2.1, 2.2, 2.1, 2.3, 2.4]
    mean_profit = np.mean(profits)
    
    fig, ax = plt.subplots()
    bars = ax.bar(months, profits, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axhline(y=mean_profit, color='red', linestyle='--', linewidth=2, label=f'Mean = £{mean_profit:.3f}M')
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Profit (£ millions)')
    ax.set_title('Firm Profits (Jul-Dec) with Mean')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'bar_chart_profits.png')
    plt.close()
    print("✓ Generated bar_chart_profits.png")

# 2. MEAN AND VARIANCE VISUALIZATION
def plot_mean_variance_visual():
    profits = np.array([2.0, 2.1, 2.2, 2.1, 2.3, 2.4])
    mean_profit = np.mean(profits)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot number line
    ax.plot([1.9, 2.5], [0, 0], 'k-', linewidth=2)
    
    # Plot mean
    ax.plot(mean_profit, 0, 'ro', markersize=15, label=f'Mean (μ = {mean_profit:.3f})')
    ax.axvline(x=mean_profit, color='red', linestyle='--', alpha=0.5)
    
    # Plot data points and deviations
    for i, profit in enumerate(profits):
        ax.plot(profit, 0.02, 'bo', markersize=10)
        # Draw deviation arrow
        if profit != mean_profit:
            ax.annotate('', xy=(mean_profit, 0.02), xytext=(profit, 0.02),
                       arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
            # Label deviation
            mid_point = (profit + mean_profit) / 2
            deviation = profit - mean_profit
            ax.text(mid_point, 0.04, f'{deviation:.3f}', ha='center', fontsize=9, color='green')
    
    ax.set_xlim(1.9, 2.5)
    ax.set_ylim(-0.05, 0.08)
    ax.set_xlabel('Profit (£ millions)')
    ax.set_title('Visualising Variance: Deviations from the Mean')
    ax.set_yticks([])
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'mean_variance_visual.png')
    plt.close()
    print("✓ Generated mean_variance_visual.png")

# 3. NORMAL DISTRIBUTION (Achievement Test)
def plot_normal_distribution():
    mu = 540
    sigma = 110
    
    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
    y = stats.norm.pdf(x, mu, sigma)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, 'b-', linewidth=2, label=f'N({mu}, {sigma}²)')
    
    # Shade area above 680
    x_shade = x[x >= 680]
    y_shade = stats.norm.pdf(x_shade, mu, sigma)
    ax.fill_between(x_shade, y_shade, alpha=0.3, color='red', label='P(X ≥ 680)')
    
    # Mark μ and μ±σ, μ±2σ, μ±3σ
    for k in range(-3, 4):
        x_val = mu + k*sigma
        ax.axvline(x=x_val, color='gray', linestyle='--', alpha=0.5)
        if k == 0:
            label = 'μ'
        elif abs(k) == 1:
            label = f'μ{"+" if k > 0 else ""}{k}σ'
        else:
            label = f'μ{"+" if k > 0 else ""}{k}σ'
        ax.text(x_val, -0.0002, label, ha='center', fontsize=10)
    
    # Mark 68-95-99.7 zones
    ax.axvspan(mu - sigma, mu + sigma, alpha=0.1, color='green', label='68% (μ±σ)')
    ax.axvspan(mu - 2*sigma, mu + 2*sigma, alpha=0.05, color='orange', label='95% (μ±2σ)')
    ax.axvspan(mu - 3*sigma, mu + 3*sigma, alpha=0.02, color='red', label='99.7% (μ±3σ)')
    
    ax.set_xlabel('Score')
    ax.set_ylabel('Probability Density')
    ax.set_title(f'Normal Distribution N({mu}, {sigma}²) — Achievement Test Scores')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'normal_distribution.png')
    plt.close()
    print("✓ Generated normal_distribution.png")

# 4. STANDARD NORMAL Z-SCORE
def plot_standard_normal_z():
    x = np.linspace(-4, 4, 1000)
    y = stats.norm.pdf(x, 0, 1)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, 'b-', linewidth=2, label='Standard Normal N(0,1)')
    
    # Shade area for z = 1.273
    z_score = 1.273
    x_shade = x[x <= z_score]
    y_shade = stats.norm.pdf(x_shade, 0, 1)
    ax.fill_between(x_shade, y_shade, alpha=0.3, color='green', label=f'P(Z ≤ {z_score}) ≈ 0.898')
    
    # Mark z-score
    ax.axvline(x=z_score, color='red', linestyle='--', linewidth=2, label=f'z = {z_score}')
    ax.plot(z_score, 0, 'ro', markersize=10)
    
    # Mark standard deviations
    for k in [-3, -2, -1, 0, 1, 2, 3]:
        ax.axvline(x=k, color='gray', linestyle=':', alpha=0.5)
        ax.text(k, -0.02, f'{k}', ha='center', fontsize=10)
    
    ax.set_xlabel('Z-score')
    ax.set_ylabel('Probability Density')
    ax.set_title('Standard Normal Distribution with z = 1.273 (Achievement Test)')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'standard_normal_z.png')
    plt.close()
    print("✓ Generated standard_normal_z.png")

# 5. BINOMIAL HOTEL OVERBOOKING
def plot_binomial_hotel():
    n = 215
    p = 0.9
    
    # Compute PMF for reasonable range
    x_vals = np.arange(max(0, int(n*p - 4*np.sqrt(n*p*(1-p)))), 
                       min(n+1, int(n*p + 4*np.sqrt(n*p*(1-p)))))
    pmf_vals = [stats.binom.pmf(k, n, p) for k in x_vals]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color bars differently based on whether ≤ 200 or not
    colors = ['green' if x <= 200 else 'lightcoral' for x in x_vals]
    ax.bar(x_vals, pmf_vals, color=colors, edgecolor='black', alpha=0.7)
    
    # Mark x=200
    ax.axvline(x=200, color='red', linestyle='--', linewidth=2, label='Hotel capacity (200 rooms)')
    
    # Mark mean
    mean = n * p
    ax.axvline(x=mean, color='blue', linestyle='--', linewidth=2, label=f'Mean = {mean:.1f}')
    
    ax.set_xlabel('Number of Guests Who Show Up')
    ax.set_ylabel('Probability')
    ax.set_title(f'Binomial Distribution: Hotel Overbooking\nBinomial({n}, {p}) — P(X ≤ 200) ≈ 0.931')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'binomial_hotel.png')
    plt.close()
    print("✓ Generated binomial_hotel.png")

# 6. VENN DIAGRAM (Newspaper Readership)
def plot_venn_newspaper():
    try:
        from matplotlib_venn import venn3
        
        # Values from the problem
        # I only: 10 - 8 - 2 + 1 = 1
        # II only: 30 - 8 - 4 + 1 = 19
        # III only: 5 - 2 - 4 + 1 = 0
        # I∩II only: 8 - 1 = 7
        # I∩III only: 2 - 1 = 1
        # II∩III only: 4 - 1 = 3
        # I∩II∩III: 1
        
        fig, ax = plt.subplots(figsize=(10, 8))
        v = venn3(subsets=(1, 19, 7, 0, 1, 3, 1), 
                  set_labels=('Newspaper I (10%)', 'Newspaper II (30%)', 'Newspaper III (5%)'))
        
        # Color the circles
        v.get_patch_by_id('100').set_color('lightblue')
        v.get_patch_by_id('010').set_color('lightgreen')
        v.get_patch_by_id('001').set_color('lightyellow')
        
        ax.set_title('Venn Diagram: Newspaper Readership\nTotal reading ≥1 paper: 32%', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR + 'venn_newspaper.png')
        plt.close()
        print("✓ Generated venn_newspaper.png (using matplotlib_venn)")
        
    except ImportError:
        # Manual circle drawing
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw three circles
        circle1 = plt.Circle((0.3, 0.5), 0.3, color='lightblue', alpha=0.5, label='Newspaper I')
        circle2 = plt.Circle((0.7, 0.5), 0.3, color='lightgreen', alpha=0.5, label='Newspaper II')
        circle3 = plt.Circle((0.5, 0.2), 0.3, color='lightyellow', alpha=0.5, label='Newspaper III')
        
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        ax.add_patch(circle3)
        
        # Add text labels
        ax.text(0.15, 0.5, '1%', ha='center', fontsize=12, weight='bold')
        ax.text(0.85, 0.5, '19%', ha='center', fontsize=12, weight='bold')
        ax.text(0.5, 0.05, '0%', ha='center', fontsize=12, weight='bold')
        ax.text(0.5, 0.5, '7%', ha='center', fontsize=12, weight='bold')
        ax.text(0.35, 0.3, '1%', ha='center', fontsize=12, weight='bold')
        ax.text(0.65, 0.3, '3%', ha='center', fontsize=12, weight='bold')
        ax.text(0.5, 0.4, '1%', ha='center', fontsize=11, weight='bold')
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.2, 1.0)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Venn Diagram: Newspaper Readership\nI=10%, II=30%, III=5%, Total ≥1: 32%', fontsize=14)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR + 'venn_newspaper.png')
        plt.close()
        print("✓ Generated venn_newspaper.png (manual drawing)")

# 7. DICE PMF
def plot_dice_pmf():
    x_vals = np.arange(1, 7)
    pmf_vals = [1/6] * 6
    expected = 3.5
    variance = 2.92
    std_dev = np.sqrt(variance)
    
    fig, ax = plt.subplots()
    ax.bar(x_vals, pmf_vals, color='steelblue', edgecolor='black', alpha=0.7)
    
    # Mark E[X]
    ax.axvline(x=expected, color='red', linestyle='--', linewidth=2, label=f'E[X] = {expected}')
    
    # Show μ±2σ interval
    lower = expected - 2*std_dev
    upper = expected + 2*std_dev
    ax.axvspan(lower, upper, alpha=0.2, color='green', label=f'μ±2σ = [{lower:.2f}, {upper:.2f}]')
    
    ax.set_xlabel('Outcome')
    ax.set_ylabel('Probability')
    ax.set_title('PMF of Fair Die (Uniform Discrete)')
    ax.set_xticks(x_vals)
    ax.set_ylim(0, 0.25)
    ax.legend()
    ax.grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'dice_pmf.png')
    plt.close()
    print("✓ Generated dice_pmf.png")

# 8. BAYES THEOREM VISUALIZATION
def plot_bayes_visual():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prior
    prior_guilty = 0.6
    prior_innocent = 0.4
    
    # Likelihoods
    p_c_given_guilty = 1.0
    p_c_given_innocent = 0.2
    
    # Posterior
    posterior_guilty = (p_c_given_guilty * prior_guilty) / (p_c_given_guilty * prior_guilty + p_c_given_innocent * prior_innocent)
    
    # Tree diagram
    # Level 1: Prior
    ax.plot([0.5, 0.3], [1.0, 0.6], 'b-', linewidth=2)
    ax.plot([0.5, 0.7], [1.0, 0.6], 'b-', linewidth=2)
    
    ax.text(0.5, 1.05, 'Start', ha='center', fontsize=12, weight='bold')
    ax.text(0.25, 0.65, f'Guilty\n{prior_guilty:.0%}', ha='center', fontsize=11, weight='bold')
    ax.text(0.75, 0.65, f'Innocent\n{prior_innocent:.0%}', ha='center', fontsize=11, weight='bold')
    
    # Level 2: Evidence
    ax.plot([0.3, 0.2], [0.6, 0.2], 'g-', linewidth=2)
    ax.plot([0.7, 0.8], [0.6, 0.2], 'r-', linewidth=2)
    
    ax.text(0.15, 0.25, f'Has characteristic\nP=1.0', ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.text(0.85, 0.25, f'Has characteristic\nP=0.2', ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral'))
    
    # Calculate joint probabilities
    joint_guilty = prior_guilty * p_c_given_guilty
    joint_innocent = prior_innocent * p_c_given_innocent
    
    ax.text(0.2, 0.05, f'P(G∩C) = {joint_guilty:.3f}', ha='center', fontsize=11, weight='bold')
    ax.text(0.8, 0.05, f'P(I∩C) = {joint_innocent:.3f}', ha='center', fontsize=11, weight='bold')
    
    # Posterior box
    ax.text(0.5, -0.15, f'POSTERIOR: P(Guilty|Characteristic) = {posterior_guilty:.3f} = 88.2%', 
            ha='center', fontsize=13, weight='bold', 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.25, 1.15)
    ax.axis('off')
    ax.set_title("Bayes' Theorem: Criminal Investigation\nPrior 60% → Evidence → Posterior 88.2%", fontsize=14)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'bayes_visual.png')
    plt.close()
    print("✓ Generated bayes_visual.png")

# 9. STEP/THRESHOLD FUNCTION
def plot_sigmoid_step():
    x = np.linspace(-5, 5, 1000)
    y = np.where(x >= 0, 1, 0)
    
    fig, ax = plt.subplots()
    ax.plot(x, y, 'b-', linewidth=2, label='f(x) = 1 if x≥0, else 0')
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Threshold at x=0')
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
    
    # Mark key points
    ax.plot(0, 1, 'ro', markersize=10)
    ax.plot(0, 0, 'wo', markersize=8, markeredgecolor='r', markeredgewidth=2)
    
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title('Step/Threshold Function (Heaviside)')
    ax.set_ylim(-0.2, 1.3)
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'sigmoid_step.png')
    plt.close()
    print("✓ Generated sigmoid_step.png")

# 10. LINEAR FUNCTION 3D
def plot_linear_function():
    # f(Age, Height) = 1 + 2*Age - 3*Height
    age = np.linspace(0, 50, 50)
    height = np.linspace(150, 200, 50)
    Age, Height = np.meshgrid(age, height)
    F = 1 + 2*Age - 3*Height
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(Age, Height, F, cmap='viridis', alpha=0.8, edgecolor='none')
    
    ax.set_xlabel('Age (years)')
    ax.set_ylabel('Height (cm)')
    ax.set_zlabel('f(Age, Height)')
    ax.set_title('Linear Function: f(Age, Height) = 1 + 2×Age - 3×Height')
    
    fig.colorbar(surf, ax=ax, shrink=0.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'linear_function.png')
    plt.close()
    print("✓ Generated linear_function.png")

# Main execution
if __name__ == '__main__':
    print("Generating Stats Recap visualizations...")
    print()
    
    try:
        plot_bar_chart_profits()
        plot_mean_variance_visual()
        plot_normal_distribution()
        plot_standard_normal_z()
        plot_binomial_hotel()
        plot_venn_newspaper()
        plot_dice_pmf()
        plot_bayes_visual()
        plot_sigmoid_step()
        plot_linear_function()
        
        print()
        print("✅ All graphs generated successfully!")
        print(f"   Output directory: {OUTPUT_DIR}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
