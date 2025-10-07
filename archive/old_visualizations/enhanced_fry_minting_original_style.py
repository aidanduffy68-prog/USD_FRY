#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced FRY Minting Chart - Original Style
===========================================

Recreates the original 2-panel layout and color scheme but with enhanced pain-based multipliers
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

def create_original_style_enhanced_chart():
    """Create enhanced FRY minting chart in original 2-panel style"""
    
    print("Generating Enhanced FRY Minting Chart (Original Style)...")
    
    # Create figure with 2 panels side by side (matching original)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Loss amounts for analysis
    loss_amounts = np.logspace(1, 4, 50)  # $10 to $10,000
    
    # Panel 1: FRY Minting vs Loss Amount (Left)
    ax1.set_title('FRY Minting vs Loss Amount', fontweight='bold')
    
    # Calculate FRY for different leverage scenarios with enhanced mechanics
    leverages = [1, 5, 10, 20]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Original matplotlib colors
    
    for i, leverage in enumerate(leverages):
        fry_amounts = []
        for loss in loss_amounts:
            # Enhanced calculation with position size scaling and ML optimization
            fry, _ = calculate_enhanced_fry_minting(
                loss, leverage, 
                position_size=loss*2,  # Position size scales with loss
                has_volatility_bonus=(leverage >= 10),  # Volatility bonus for high leverage
                ml_optimization=True  # Agent B ML enhancement
            )
            fry_amounts.append(fry)
        
        ax1.loglog(loss_amounts, fry_amounts, 
                  color=colors[i], linewidth=2, marker='o', markersize=3,
                  label='{}x Leverage'.format(leverage))
    
    ax1.set_xlabel('Loss Amount ($)')
    ax1.set_ylabel('FRY Minted')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: FRY Minting Heatmap (Right)
    ax2.set_title('FRY Minting Heatmap\n(Loss x Leverage)', fontweight='bold')
    
    # Create heatmap data with enhanced mechanics
    loss_range = np.logspace(1.5, 4, 25)  # $32 to $10,000
    leverage_range = np.linspace(1, 20, 25)
    
    heatmap_data = np.zeros((len(leverage_range), len(loss_range)))
    
    for i, leverage in enumerate(leverage_range):
        for j, loss in enumerate(loss_range):
            # Enhanced FRY calculation with all bonuses
            fry, _ = calculate_enhanced_fry_minting(
                loss, leverage,
                position_size=loss*3,  # Large position size for maximum effect
                has_volatility_bonus=True,  # Volatility bonus active
                ml_optimization=True,  # ML optimization active
                is_liquidation=(leverage > 15)  # Liquidation bonus for very high leverage
            )
            heatmap_data[i, j] = fry
    
    # Use original colormap (Reds)
    im = ax2.imshow(heatmap_data, cmap='Reds', aspect='auto', 
                   extent=[np.log10(loss_range[0]), np.log10(loss_range[-1]),
                          leverage_range[0], leverage_range[-1]],
                   origin='lower')
    
    # Add colorbar with original styling
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('FRY Minted')
    
    ax2.set_xlabel('Loss Amount ($)')
    ax2.set_ylabel('Leverage')
    
    # Add custom x-axis labels for log scale
    x_ticks = [2, 3, 4]  # 10^2, 10^3, 10^4
    x_labels = ['$10^2', '$10^3', '$10^4']
    ax2.set_xticks(x_ticks)
    ax2.set_xticklabels(x_labels)
    
    plt.tight_layout()
    
    # Save with timestamp
    timestamp = int(time.time())
    filename = "enhanced_fry_minting_original_style_{}.png".format(timestamp)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    print("Enhanced FRY Minting Chart (Original Style) saved: {}".format(filename))
    
    # Display key improvements over original
    print("\nENHANCED MECHANICS vs ORIGINAL:")
    print("-" * 50)
    
    # Example calculations
    example_loss = 1000
    
    # Original style calculation (1:1 ratio)
    original_fry = example_loss * 1.0  # Simple 1:1 mapping
    
    # Enhanced calculations
    fry_base, _ = calculate_enhanced_fry_minting(example_loss, 1)
    fry_high, _ = calculate_enhanced_fry_minting(example_loss, 20, position_size=5000, ml_optimization=True)
    fry_max, _ = calculate_enhanced_fry_minting(example_loss, 20, position_size=5000, 
                                              is_liquidation=True, has_volatility_bonus=True, 
                                              ml_optimization=True)
    
    print("$1000 Loss Comparison:")
    print("  Original System: {:.0f} FRY (1.0x)".format(original_fry))
    print("  Enhanced Base: {:.0f} FRY ({:.1f}x)".format(fry_base, fry_base/original_fry))
    print("  Enhanced High Leverage: {:.0f} FRY ({:.1f}x)".format(fry_high, fry_high/original_fry))
    print("  Enhanced Maximum: {:.0f} FRY ({:.1f}x)".format(fry_max, fry_max/original_fry))
    print("\nMaximum Enhancement: {:.1f}x improvement over original".format(fry_max/original_fry))
    
    plt.close()
    return filename

def main():
    """Generate enhanced FRY minting chart in original style"""
    
    print("Creating Enhanced FRY Minting Chart (Original 2-Panel Style)...")
    
    filename = create_original_style_enhanced_chart()
    
    print("\nEnhanced FRY Minting Chart (Original Style) Complete!")
    print("Features:")
    print("• Original 2-panel layout preserved")
    print("• Original color scheme maintained") 
    print("• Enhanced pain-based multipliers integrated")
    print("• ML optimization bonuses included")
    print("• Up to 15x improvement over original mechanics")
    print("\nFile: {}".format(filename))

if __name__ == "__main__":
    main()
