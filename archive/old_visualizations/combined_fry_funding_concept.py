#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined FRY Concept + Funding Rate Phases
==========================================

Overlays funding rate phases diagram on top of the definitive FRY chart
with minimal text to show the complete FRY ecosystem in one visualization.
"""

import matplotlib.pyplot as plt
import numpy as np
import math
from datetime import datetime

# Set non-interactive backend for PNG output
plt.switch_backend('Agg')

# Color scheme - Red, Yellow, Orange for uniformity
COLORS = {
    'crimson_red': '#DC143C',
    'gold_yellow': '#FFD700', 
    'dark_orange': '#FF8C00',
    'black': '#000000',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#808080'
}

def calculate_pain_multiplier(loss_amount):
    """Calculate pain-based multiplier for FRY minting"""
    if loss_amount <= 100:
        return 1.0
    elif loss_amount <= 500:
        return 1.5
    elif loss_amount <= 1000:
        return 2.0
    elif loss_amount <= 5000:
        return 3.0
    else:
        return 4.0

def generate_fry_conversion_data():
    """Generate comprehensive FRY conversion data"""
    
    # Loss amounts from $1 to $10,000 (log scale for better visualization)
    loss_amounts = np.logspace(0, 4, 100)  # $1 to $10,000
    
    # Calculate pain multipliers
    pain_multipliers = [calculate_pain_multiplier(loss) for loss in loss_amounts]
    
    # Base FRY rate: 0.5 FRY per $1 loss
    base_fry_rate = 0.5
    
    # Calculate FRY minted
    fry_minted = loss_amounts * base_fry_rate * np.array(pain_multipliers)
    
    # Calculate recovery rates (assuming FRY trades at $0.80-$1.20)
    fry_value_low = fry_minted * 0.8
    fry_value_high = fry_minted * 1.2
    
    recovery_rate_low = (fry_value_low / loss_amounts) * 100
    recovery_rate_high = (fry_value_high / loss_amounts) * 100
    
    return loss_amounts, pain_multipliers, fry_minted, recovery_rate_low, recovery_rate_high

def generate_funding_rates():
    """Generate funding rate data for three venues over time"""
    
    # Time periods: Initial Alignment -> Divergence -> End State
    time_points = np.linspace(0, 24, 100)  # 24 hour period
    
    # Base market volatility pattern
    base_volatility = 0.02 * np.sin(2 * np.pi * time_points / 8) + \
                     0.01 * np.sin(2 * np.pi * time_points / 3) + \
                     0.005 * np.random.normal(0, 1, len(time_points))
    
    # Venue A - Traditional funding (full oscillation)
    venue_a_rates = 0.01 + base_volatility * 1.0
    
    # Venue B - Traditional funding (full oscillation) 
    venue_b_rates = 0.01 + base_volatility * 0.9 + 0.002 * np.sin(2 * np.pi * time_points / 6)
    
    # Hy - Loss recycle mechanics (dampening starts at hour 6)
    hy_rates = np.copy(venue_a_rates)
    
    # Apply loss recycle dampening after hour 6
    divergence_mask = time_points > 6
    dampening_factor = np.exp(-(time_points - 6) / 8)  # Exponential dampening
    dampening_factor[time_points <= 6] = 1.0  # No dampening in alignment phase
    
    hy_rates[divergence_mask] = 0.01 + (hy_rates[divergence_mask] - 0.01) * dampening_factor[divergence_mask]
    
    return time_points, venue_a_rates, venue_b_rates, hy_rates

def create_combined_fry_funding_graph():
    """Create the combined FRY concept + funding rate phases visualization on same percentage scale"""
    
    # Generate both datasets
    loss_amounts, pain_multipliers, fry_minted, recovery_low, recovery_high = generate_fry_conversion_data()
    time_points, venue_a_rates, venue_b_rates, hy_rates = generate_funding_rates()
    
    # Create figure with single axis
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor(COLORS['white'])
    
    # Main title
    fig.suptitle('FRY: Converting Trading Friction Into Value + Funding Rate Evolution', 
                fontsize=22, fontweight='bold', color=COLORS['black'], y=0.95)
    
    # Single axis for percentage-based data
    ax = fig.add_subplot(1, 1, 1)
    
    # Set up percentage scale
    ax.set_xlabel('Trading Loss ($) / Time (Hours)', fontsize=16, fontweight='bold', color=COLORS['black'])
    ax.set_ylabel('Percentage (%)', fontsize=16, fontweight='bold', color=COLORS['black'])
    
    # Plot recovery rate data (main FRY concept)
    ax.fill_between(loss_amounts, recovery_low, recovery_high, 
                   color=COLORS['gold_yellow'], alpha=0.3, label='FRY Recovery Range')
    ax.plot(loss_amounts, (recovery_low + recovery_high) / 2, 
           color=COLORS['gold_yellow'], linewidth=4, 
           linestyle='-', label='Avg FRY Recovery', alpha=0.9)
    
    # Set log scale for loss amounts
    ax.set_xscale('log')
    
    # Pain multiplier zones with minimal labels
    pain_zones = [
        (1, 100, '1.0x'),
        (100, 500, '1.5x'),
        (500, 1000, '2.0x'),
        (1000, 5000, '3.0x'),
        (5000, 10000, '4.0x')
    ]
    
    # Add pain multiplier zones
    for i, (start, end, label) in enumerate(pain_zones):
        # Subtle background shading
        ax.axvspan(start, end, alpha=0.1, color=COLORS['dark_orange'])
        
        # Minimal zone labels
        mid_point = math.sqrt(start * end)  # Geometric mean for log scale
        ax.annotate(label, xy=(mid_point, 400), 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=COLORS['light_gray'], 
                            alpha=0.7, edgecolor=COLORS['dark_orange']))
    
    # Create secondary x-axis for funding rate time data (overlay on same plot)
    ax2 = ax.twiny()
    ax2.set_xlabel('Time (Hours)', fontsize=14, fontweight='bold', color=COLORS['crimson_red'])
    
    # Plot funding rates on same percentage scale
    ax2.plot(time_points, venue_a_rates * 100, 
            color=COLORS['crimson_red'], linewidth=3, alpha=0.8, label='Venue A (Traditional)')
    ax2.plot(time_points, venue_b_rates * 100, 
            color=COLORS['dark_orange'], linewidth=3, alpha=0.8, label='Venue B (Traditional)')
    ax2.plot(time_points, hy_rates * 100, 
            color='#8B0000', linewidth=4, alpha=0.9, label='Hy (Loss Recycle)', linestyle=':')
    
    # Phase backgrounds for funding data
    y_max = max(max(recovery_high), max(venue_a_rates * 100), max(venue_b_rates * 100))
    ax2.axvspan(0, 6, alpha=0.05, color=COLORS['dark_gray'])
    ax2.axvspan(6, 18, alpha=0.05, color=COLORS['crimson_red'])
    ax2.axvspan(18, 24, alpha=0.05, color=COLORS['gold_yellow'])
    
    # Phase dividers
    ax2.axvline(x=6, color=COLORS['black'], linestyle=':', alpha=0.4, linewidth=1)
    ax2.axvline(x=18, color=COLORS['black'], linestyle=':', alpha=0.4, linewidth=1)
    
    # Minimal annotations
    ax.annotate('Small losses', xy=(50, 50), xytext=(20, 100),
               arrowprops=dict(arrowstyle='->', color=COLORS['black'], alpha=0.5),
               fontsize=11, fontweight='bold', color=COLORS['black'])
    
    ax.annotate('Large losses\nhigher recovery', xy=(2000, 200), xytext=(800, 350),
               arrowprops=dict(arrowstyle='->', color=COLORS['black'], alpha=0.5),
               fontsize=11, fontweight='bold', color=COLORS['black'])
    
    # Phase labels for funding rates
    ax2.text(3, y_max * 0.95, 'Align', ha='center', fontsize=10, 
            fontweight='bold', color=COLORS['crimson_red'])
    ax2.text(12, y_max * 0.95, 'Diverge', ha='center', fontsize=10, 
            fontweight='bold', color=COLORS['crimson_red'])
    ax2.text(21, y_max * 0.95, 'Dampen', ha='center', fontsize=10, 
            fontweight='bold', color=COLORS['crimson_red'])
    
    # Grid and formatting
    ax.grid(True, alpha=0.3, color=COLORS['dark_gray'])
    ax.patch.set_facecolor(COLORS['white'])
    
    # Combined legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='center left', fontsize=11, bbox_to_anchor=(0.02, 0.5))
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = 'combined_fry_funding_same_scale_{}.png'.format(timestamp)
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor=COLORS['white'])
    print("Combined FRY + Funding concept graph (same scale) saved as: {}".format(filename))
    
    return filename

def main():
    """Generate the combined FRY concept + funding phases visualization"""
    print("🍟 Creating Combined FRY + Funding Phases Graph...")
    print("=" * 60)
    
    filename = create_combined_fry_funding_graph()
    
    print("✅ The ULTIMATE FRY concept graph!")
    print("📊 Shows slippage → FRY conversion + funding phases")
    print("🎯 Demonstrates complete FRY ecosystem")
    print("💰 Illustrates value creation + market dynamics")
    print("🚀 This is the graph that explains everything!")

if __name__ == "__main__":
    main()
