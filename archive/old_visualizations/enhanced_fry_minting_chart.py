#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced FRY Minting Chart
==========================

Updated visualization showing the enhanced FRY minting mechanics with:
- Pain-based multipliers (leverage, position size, liquidation, volatility)
- ML optimization bonuses
- Agent B slippage harvesting improvements
- Comparison with original baseline minting
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import time

def calculate_enhanced_fry_minting(loss_amount, leverage, position_size=0, is_liquidation=False, 
                                 has_volatility_bonus=False, ml_optimization=False):
    """
    Calculate FRY minting with enhanced pain-based multipliers and ML optimization
    """
    # Base multiplier
    multiplier = 1.0
    
    # Leverage pain multiplier (higher leverage = more FRY)
    if leverage > 10:
        multiplier += (leverage / 10) * 0.1
    
    # Position size multiplier (bigger losses = exponential FRY)
    if position_size > 1000:
        multiplier += (position_size / 1000) * 0.05
    
    # Liquidation bonus (getting rekt = 3x multiplier)
    if is_liquidation:
        multiplier *= 3.0
    
    # Volatility bonus (rapid losses = 1.5x multiplier)
    if has_volatility_bonus:
        multiplier *= 1.5
    
    # ML optimization bonus (Agent B enhancement = +25%)
    if ml_optimization:
        multiplier *= 1.25
    
    # Cap at 15x multiplier (increased from 10x)
    multiplier = min(multiplier, 15.0)
    
    # FRY minted = loss amount * pain multiplier
    fry_minted = loss_amount * multiplier
    
    return fry_minted, multiplier

def create_enhanced_fry_chart():
    """Create enhanced FRY minting visualization"""
    
    print("Generating Enhanced FRY Minting Chart...")
    
    # Set up dark theme manually for older matplotlib
    plt.rcParams['figure.facecolor'] = '#1a1a1a'
    plt.rcParams['axes.facecolor'] = '#2d2d2d'
    plt.rcParams['text.color'] = 'white'
    plt.rcParams['axes.labelcolor'] = 'white'
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('ENHANCED FRY MINTING MECHANICS - Pain-Based Multipliers + ML Optimization', 
                fontsize=20, fontweight='bold', color='#00FFFF')
    
    # Loss amounts for analysis
    loss_amounts = np.logspace(1, 4, 50)  # $10 to $10,000
    
    # Colors for different scenarios
    colors = {
        'baseline': '#FF6B6B',
        'enhanced_1x': '#4ECDC4', 
        'enhanced_5x': '#45B7D1',
        'enhanced_10x': '#96CEB4',
        'enhanced_20x': '#FFEAA7',
        'liquidation': '#FF7675',
        'ml_optimized': '#00FFFF'
    }
    
    # 1. Enhanced Leverage Comparison (Top Left)
    ax1.set_title('FRY Minting vs Loss Amount - Enhanced Pain Multipliers', 
                  fontweight='bold', color='#00FFFF')
    
    # Calculate FRY for different leverage scenarios
    leverages = [1, 5, 10, 20]
    
    for leverage in leverages:
        fry_amounts = []
        for loss in loss_amounts:
            fry, _ = calculate_enhanced_fry_minting(loss, leverage, 
                                                  position_size=loss*2, 
                                                  ml_optimization=True)
            fry_amounts.append(fry)
        
        color_key = 'enhanced_{}x'.format(leverage) if leverage <= 20 else 'enhanced_20x'
        ax1.loglog(loss_amounts, fry_amounts, 
                  color=colors.get(color_key, colors['enhanced_20x']),
                  linewidth=3, marker='o', markersize=4,
                  label='{}x Leverage (Enhanced)'.format(leverage), alpha=0.8)
    
    ax1.set_xlabel('Loss Amount ($)', color='white', fontweight='bold')
    ax1.set_ylabel('FRY Minted', color='white', fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Liquidation vs Normal Loss (Top Right)
    ax2.set_title('Liquidation Bonus Effect - 3x Pain Multiplier', 
                  fontweight='bold', color='#00FFFF')
    
    # Normal loss vs liquidation at 10x leverage
    normal_fry = []
    liquidation_fry = []
    
    for loss in loss_amounts:
        # Normal loss
        fry_normal, _ = calculate_enhanced_fry_minting(loss, 10, 
                                                     position_size=loss*2,
                                                     ml_optimization=True)
        normal_fry.append(fry_normal)
        
        # Liquidation event
        fry_liq, _ = calculate_enhanced_fry_minting(loss, 10, 
                                                  position_size=loss*2,
                                                  is_liquidation=True,
                                                  ml_optimization=True)
        liquidation_fry.append(fry_liq)
    
    ax2.loglog(loss_amounts, normal_fry, 
              color=colors['enhanced_10x'], linewidth=3, 
              label='Normal Loss (10x)', alpha=0.8)
    ax2.loglog(loss_amounts, liquidation_fry, 
              color=colors['liquidation'], linewidth=3,
              label='Liquidation Event (10x)', alpha=0.8)
    
    ax2.set_xlabel('Loss Amount ($)', color='white', fontweight='bold')
    ax2.set_ylabel('FRY Minted', color='white', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. ML Optimization Comparison (Bottom Left)
    ax3.set_title('Agent B ML Optimization Bonus - +25% Enhancement', 
                  fontweight='bold', color='#00FFFF')
    
    # Compare with and without ML optimization
    baseline_fry = []
    ml_enhanced_fry = []
    
    for loss in loss_amounts:
        # Without ML optimization
        fry_base, _ = calculate_enhanced_fry_minting(loss, 10, 
                                                   position_size=loss*2,
                                                   has_volatility_bonus=True)
        baseline_fry.append(fry_base)
        
        # With ML optimization
        fry_ml, _ = calculate_enhanced_fry_minting(loss, 10, 
                                                 position_size=loss*2,
                                                 has_volatility_bonus=True,
                                                 ml_optimization=True)
        ml_enhanced_fry.append(fry_ml)
    
    ax3.loglog(loss_amounts, baseline_fry, 
              color=colors['enhanced_10x'], linewidth=3,
              label='Enhanced Base (10x + Volatility)', alpha=0.8)
    ax3.loglog(loss_amounts, ml_enhanced_fry, 
              color=colors['ml_optimized'], linewidth=3,
              label='Agent B ML Optimized (+25%)', alpha=0.8)
    
    # Fill area between curves to show improvement
    ax3.fill_between(loss_amounts, baseline_fry, ml_enhanced_fry,
                    color=colors['ml_optimized'], alpha=0.2,
                    label='ML Enhancement Gain')
    
    ax3.set_xlabel('Loss Amount ($)', color='white', fontweight='bold')
    ax3.set_ylabel('FRY Minted', color='white', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Enhanced Heatmap (Bottom Right)
    ax4.set_title('Enhanced FRY Minting Heatmap - Loss x Leverage x ML', 
                  fontweight='bold', color='#00FFFF')
    
    # Create heatmap data
    loss_range = np.logspace(1.5, 3.5, 20)  # $32 to $3162
    leverage_range = np.linspace(1, 20, 20)
    
    heatmap_data = np.zeros((len(leverage_range), len(loss_range)))
    
    for i, leverage in enumerate(leverage_range):
        for j, loss in enumerate(loss_range):
            fry, _ = calculate_enhanced_fry_minting(loss, leverage,
                                                  position_size=loss*3,
                                                  has_volatility_bonus=True,
                                                  ml_optimization=True)
            heatmap_data[i, j] = fry
    
    im = ax4.imshow(heatmap_data, cmap='hot', aspect='auto', 
                   extent=[np.log10(loss_range[0]), np.log10(loss_range[-1]),
                          leverage_range[0], leverage_range[-1]],
                   origin='lower')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax4)
    cbar.set_label('FRY Minted', color='white', fontweight='bold')
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.tick_params(colors='white')
    
    ax4.set_xlabel('Loss Amount ($) [log scale]', color='white', fontweight='bold')
    ax4.set_ylabel('Leverage', color='white', fontweight='bold')
    
    # Add custom x-axis labels
    x_ticks = np.linspace(np.log10(loss_range[0]), np.log10(loss_range[-1]), 5)
    x_labels = ['$' + str(int(10**x)) for x in x_ticks]
    ax4.set_xticks(x_ticks)
    ax4.set_xticklabels(x_labels)
    
    # Style all axes
    for ax in [ax1, ax2, ax3, ax4]:
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
    
    try:
        plt.tight_layout()
    except:
        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.3, hspace=0.4)
    
    # Save with timestamp
    timestamp = int(time.time())
    filename = "enhanced_fry_minting_chart_{}.png".format(timestamp)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight',
               facecolor='#1a1a1a', edgecolor='none')
    
    print("Enhanced FRY Minting Chart saved: {}".format(filename))
    
    # Display key improvements
    print("\nENHANCED MINTING MECHANICS:")
    print("-" * 50)
    
    # Example calculations
    example_loss = 1000
    
    # Baseline (1x leverage)
    fry_base, mult_base = calculate_enhanced_fry_minting(example_loss, 1)
    
    # High leverage
    fry_high, mult_high = calculate_enhanced_fry_minting(example_loss, 20, 
                                                        position_size=5000)
    
    # Liquidation event
    fry_liq, mult_liq = calculate_enhanced_fry_minting(example_loss, 20,
                                                      position_size=5000,
                                                      is_liquidation=True,
                                                      has_volatility_bonus=True)
    
    # ML optimized
    fry_ml, mult_ml = calculate_enhanced_fry_minting(example_loss, 20,
                                                    position_size=5000,
                                                    is_liquidation=True,
                                                    has_volatility_bonus=True,
                                                    ml_optimization=True)
    
    print("$1000 Loss Examples:")
    print("  Baseline (1x): {:.0f} FRY ({:.1f}x multiplier)".format(fry_base, mult_base))
    print("  High Leverage (20x): {:.0f} FRY ({:.1f}x multiplier)".format(fry_high, mult_high))
    print("  Liquidation Event: {:.0f} FRY ({:.1f}x multiplier)".format(fry_liq, mult_liq))
    print("  ML Optimized: {:.0f} FRY ({:.1f}x multiplier)".format(fry_ml, mult_ml))
    print("\nML Enhancement: +{:.1f}% over baseline liquidation".format(
        (fry_ml - fry_liq) / fry_liq * 100))
    
    plt.close()
    return filename

def main():
    """Generate enhanced FRY minting chart"""
    
    print("Creating Enhanced FRY Minting Mechanics Chart...")
    
    filename = create_enhanced_fry_chart()
    
    print("\nEnhanced FRY Minting Chart Complete!")
    print("Features:")
    print("• Pain-based multipliers (leverage, position size, liquidation)")
    print("• Volatility bonus for rapid losses")
    print("• ML optimization bonus (+25%)")
    print("• Agent B slippage harvesting integration")
    print("• Enhanced multiplier cap (15x vs 10x)")
    print("• Comprehensive heatmap visualization")
    print("\nFile: {}".format(filename))

if __name__ == "__main__":
    main()
