ca#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funding Rate Flow Diagram - Three Venue Comparison
=================================================

Visualizes funding rate behavior across three venues:
- Hy: Uses loss recycle mechanics (dampened volatility)
- Venue A: Traditional funding (normal oscillation)
- Venue B: Traditional funding (normal oscillation)

Shows initial alignment, divergence, and end state with Hy's
dampened funding volatility vs A/B's continued cyclical behavior.
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

def generate_funding_rates():
    """Generate funding rate data for three venues over time"""
    
    # Time periods: Initial Alignment -> Divergence -> End State
    time_points = np.linspace(0, 24, 100)  # 24 hour period
    
    # Base market volatility pattern
    base_volatility = 0.02 * np.sin(2 * np.pi * time_points / 8) + \
                     0.01 * np.sin(2 * np.pi * time_points / 3) + \
                     0.005 * np.random.normal(0, 1, len(time_points))
    
    # Initial alignment phase (0-6 hours)
    alignment_mask = time_points <= 6
    
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

def create_funding_flow_diagram():
    """Create the funding rate flow diagram"""
    
    # Generate data
    time_points, venue_a_rates, venue_b_rates, hy_rates = generate_funding_rates()
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor(COLORS['white'])
    
    # Main title
    fig.suptitle('Funding Rate Flow: Loss Recycle Impact Across Venues', 
                fontsize=20, fontweight='bold', color=COLORS['black'], y=0.95)
    
    # Single main chart - simplified layout
    ax_main = fig.add_subplot(1, 1, 1)
    
    # Plot funding rates
    ax_main.plot(time_points, venue_a_rates * 100, 
                color=COLORS['crimson_red'], linewidth=3, label='Venue A (Traditional)', alpha=0.8)
    ax_main.plot(time_points, venue_b_rates * 100, 
                color=COLORS['dark_orange'], linewidth=3, label='Venue B (Traditional)', alpha=0.8)
    ax_main.plot(time_points, hy_rates * 100, 
                color=COLORS['gold_yellow'], linewidth=4, label='Hy (Loss Recycle)', alpha=0.9)
    
    # Phase background colors
    ax_main.axvspan(0, 6, alpha=0.1, color=COLORS['dark_gray'], label='Initial Alignment')
    ax_main.axvspan(6, 18, alpha=0.1, color=COLORS['crimson_red'], label='Divergence Phase')
    ax_main.axvspan(18, 24, alpha=0.1, color=COLORS['gold_yellow'], label='End State')
    
    # Phase dividers
    ax_main.axvline(x=6, color=COLORS['black'], linestyle='--', alpha=0.3, linewidth=1)
    ax_main.axvline(x=18, color=COLORS['black'], linestyle='--', alpha=0.3, linewidth=1)
    
    # Clean formatting
    ax_main.set_xlabel('Time (Hours)', fontsize=14, fontweight='bold', color=COLORS['black'])
    ax_main.set_ylabel('Funding Rate (%)', fontsize=14, fontweight='bold', color=COLORS['black'])
    
    ax_main.grid(True, alpha=0.2, color=COLORS['dark_gray'])
    ax_main.legend(loc='upper right', fontsize=12, framealpha=0.9)
    ax_main.patch.set_facecolor(COLORS['white'])
    
    
    
    
    
    # Simple layout adjustment
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = 'funding_rate_flow_diagram_{}.png'.format(timestamp)
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor=COLORS['white'])
    print("Funding rate flow diagram saved as: {}".format(filename))
    
    return filename

def main():
    """Generate the funding rate flow diagram"""
    print("🔄 Generating Funding Rate Flow Diagram...")
    print("=" * 50)
    
    filename = create_funding_flow_diagram()
    
    print("✅ Diagram complete!")
    print("📊 Shows funding rate evolution across three venues")
    print("🎯 Demonstrates loss recycle impact on Hy's volatility")
    print("💰 Highlights arbitrage opportunities from dampened rates")

if __name__ == "__main__":
    main()
