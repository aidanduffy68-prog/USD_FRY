#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Definitive FRY Concept Graph
================================

Single visualization that captures the entire FRY ecosystem:
- Slippage losses converted to FRY tokens
- Pain multiplier system
- Recovery mechanism demonstration
- Value creation from trading friction

This is THE graph that explains FRY in one image.
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

def create_definitive_fry_graph():
    """Create the single definitive FRY concept visualization"""
    
    # Generate data
    loss_amounts, pain_multipliers, fry_minted, recovery_low, recovery_high = generate_fry_conversion_data()
    
    # Create figure with dual y-axis
    fig, ax1 = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(COLORS['white'])
    
    # Main title
    fig.suptitle('FRY: Converting Trading Friction Into Value', 
                fontsize=24, fontweight='bold', color=COLORS['black'], y=0.95)
    
    # Primary axis - FRY Minted
    ax1.set_xlabel('Trading Loss ($)', fontsize=16, fontweight='bold', color=COLORS['black'])
    ax1.set_ylabel('FRY Tokens Minted', fontsize=16, fontweight='bold', color=COLORS['crimson_red'])
    ax1.set_xscale('log')
    
    # Plot FRY minting curve
    line1 = ax1.plot(loss_amounts, fry_minted, color=COLORS['crimson_red'], 
                     linewidth=4, label='FRY Minted', alpha=0.9)
    ax1.tick_params(axis='y', labelcolor=COLORS['crimson_red'])
    
    # Secondary axis - Recovery Rate
    ax2 = ax1.twinx()
    ax2.set_ylabel('Loss Recovery Rate (%)', fontsize=16, fontweight='bold', color=COLORS['gold_yellow'])
    
    # Plot recovery rate range
    ax2.fill_between(loss_amounts, recovery_low, recovery_high, 
                     color=COLORS['gold_yellow'], alpha=0.3, label='Recovery Range')
    line2 = ax2.plot(loss_amounts, (recovery_low + recovery_high) / 2, 
                     color=COLORS['gold_yellow'], linewidth=3, 
                     linestyle='--', label='Avg Recovery Rate', alpha=0.8)
    ax2.tick_params(axis='y', labelcolor=COLORS['gold_yellow'])
    
    # Pain multiplier zones with annotations
    pain_zones = [
        (1, 100, 1.0, 'Base Rate\n1.0x'),
        (100, 500, 1.5, 'Medium Pain\n1.5x'),
        (500, 1000, 2.0, 'High Pain\n2.0x'),
        (1000, 5000, 3.0, 'Severe Pain\n3.0x'),
        (5000, 10000, 4.0, 'Maximum Pain\n4.0x')
    ]
    
    # Add pain multiplier zones
    for i, (start, end, multiplier, label) in enumerate(pain_zones):
        # Subtle background shading
        ax1.axvspan(start, end, alpha=0.1, color=COLORS['dark_orange'])
        
        # Zone labels
        mid_point = math.sqrt(start * end)  # Geometric mean for log scale
        ax1.annotate(label, xy=(mid_point, max(fry_minted) * 0.8), 
                    ha='center', va='center', fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS['light_gray'], 
                             alpha=0.8, edgecolor=COLORS['dark_orange']))
    
    # Key insight annotations
    ax1.annotate('Small losses get basic compensation', 
                xy=(50, 25), xytext=(20, 200),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], alpha=0.7),
                fontsize=12, fontweight='bold', color=COLORS['black'])
    
    ax1.annotate('Large losses trigger\nhigher multipliers', 
                xy=(2000, 3000), xytext=(800, 8000),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], alpha=0.7),
                fontsize=12, fontweight='bold', color=COLORS['black'])
    
    
    # Grid and formatting
    ax1.grid(True, alpha=0.3, color=COLORS['dark_gray'])
    ax1.patch.set_facecolor(COLORS['white'])
    
    # Legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)
    
    
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = 'definitive_fry_concept_{}.png'.format(timestamp)
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor=COLORS['white'])
    print("Definitive FRY concept graph saved as: {}".format(filename))
    
    return filename

def main():
    """Generate the definitive FRY concept visualization"""
    print("🍟 Creating THE Definitive FRY Concept Graph...")
    print("=" * 60)
    
    filename = create_definitive_fry_graph()
    
    print("✅ The ONE graph that explains FRY!")
    print("📊 Shows slippage → FRY conversion")
    print("🎯 Demonstrates pain multiplier system")
    print("💰 Illustrates value creation from trading friction")
    print("🚀 This is the graph that sells the concept!")

if __name__ == "__main__":
    main()
