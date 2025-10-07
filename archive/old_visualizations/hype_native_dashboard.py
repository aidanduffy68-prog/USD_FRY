#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
$HYPE Native FRY Pool Dashboard
Comprehensive visualization of native token pool performance metrics

Features:
- Pool TVL and FRY minting statistics
- Yield generation breakdown by strategy
- Cross-pool arbitrage opportunities
- Native token multiplier analysis
- Real-time pool health metrics
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime, timedelta
import json

# Set non-interactive backend for PNG output
plt.switch_backend('Agg')

class HypeNativeDashboard:
    """
    $HYPE Native FRY Pool Performance Dashboard
    
    Visualizes key metrics for the native token denominated dark pool
    """
    
    def __init__(self):
        # Color scheme - red and yellow for consistency
        self.red = '#FF4444'
        self.yellow = '#FFD700'
        self.orange = '#FF8C00'
        self.dark_red = '#CC0000'
        self.light_yellow = '#FFFF99'
        self.black = '#000000'
        self.white = '#FFFFFF'
        self.gray = '#808080'
        
        # Dashboard configuration
        self.fig_width = 16
        self.fig_height = 12
        
    def create_native_pool_dashboard(self, pool_stats, processing_results):
        """
        Create comprehensive dashboard for $HYPE native FRY pool
        """
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        fig.patch.set_facecolor(self.black)
        
        # Create grid layout for dashboard panels (matplotlib compatibility)
        from matplotlib.gridspec import GridSpec
        gs = GridSpec(3, 4, hspace=0.3, wspace=0.3, 
                     left=0.05, right=0.95, top=0.92, bottom=0.08)
        
        # Panel 1: Pool TVL and FRY Minting (top left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        self.create_tvl_minting_panel(ax1, processing_results)
        
        # Panel 2: Yield Strategy Breakdown (top right, spans 2 columns)
        ax2 = fig.add_subplot(gs[0, 2:])
        self.create_yield_strategy_panel(ax2, pool_stats)
        
        # Panel 3: Native Token Multipliers (middle left, spans 2 columns)
        ax3 = fig.add_subplot(gs[1, :2])
        self.create_multiplier_analysis_panel(ax3, processing_results)
        
        # Panel 4: Pool Health Metrics (middle right, spans 2 columns)
        ax4 = fig.add_subplot(gs[1, 2:])
        self.create_pool_health_panel(ax4, pool_stats, processing_results)
        
        # Panel 5: Loss Pool Distribution (bottom left, spans 2 columns)
        ax5 = fig.add_subplot(gs[2, :2])
        self.create_loss_distribution_panel(ax5, pool_stats)
        
        # Panel 6: Arbitrage Opportunities (bottom right, spans 2 columns)
        ax6 = fig.add_subplot(gs[2, 2:])
        self.create_arbitrage_panel(ax6, pool_stats)
        
        # Add main title
        fig.suptitle('$HYPE Native FRY Pool Dashboard', 
                    fontsize=20, fontweight='bold', color=self.yellow, y=0.97)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.02, 0.02, "Generated: {}".format(timestamp), 
                fontsize=10, color=self.gray)
        
        # Save dashboard
        filename = "hype_native_dashboard_{}.png".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.black, edgecolor='none')
        plt.close()
        
        return filename
    
    def create_tvl_minting_panel(self, ax, results):
        """Panel 1: Pool TVL and FRY Minting Statistics"""
        ax.patch.set_facecolor(self.black)
        
        # TVL metrics
        tvl_hype = results['pool_tvl_hype']
        tvl_usd = tvl_hype * results['hype_price_usd']
        fry_minted = results['total_fry_minted']
        
        # Create bar chart for key metrics
        metrics = ['Pool TVL\n($HYPE)', 'Pool TVL\n(USD)', 'FRY Minted', 'Yield Generated']
        values = [tvl_hype, tvl_usd, fry_minted, results.get('yield_generated_hype', 0) * 1000]  # Scale yield for visibility
        colors = [self.red, self.orange, self.yellow, self.light_yellow]
        
        # Convert metrics to numeric positions for matplotlib compatibility
        x_pos = np.arange(len(metrics))
        bars = ax.bar(x_pos, values, color=colors, alpha=0.8, edgecolor=self.white, linewidth=1)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(metrics)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            if i < 2:  # TVL values
                label = "${:,.0f}".format(value)
            elif i == 2:  # FRY minted
                label = "{:,.0f}".format(value)
            else:  # Yield
                label = "{:.1f}".format(value / 1000)  # Unscale yield
            
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   label, ha='center', va='bottom', color=self.white, fontweight='bold')
        
        ax.set_title('Pool TVL & FRY Minting Performance', 
                    fontsize=14, fontweight='bold', color=self.yellow)
        ax.set_ylabel('Value', color=self.white, fontweight='bold')
        ax.tick_params(colors=self.white)
        ax.spines['bottom'].set_color(self.white)
        ax.spines['left'].set_color(self.white)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Set y-axis to log scale for better visibility
        ax.set_yscale('log')
    
    def create_yield_strategy_panel(self, ax, stats):
        """Panel 2: Yield Strategy Allocation Breakdown"""
        ax.patch.set_facecolor(self.black)
        
        # Extract yield strategy data
        strategies = []
        allocations = []
        apys = []
        
        for strategy, data in stats['reserve_allocation'].items():
            if data['hype_allocated'] > 0:
                strategies.append(strategy.replace('_', ' ').title())
                allocations.append(data['hype_allocated'])
                apys.append(data['apy'] * 100)  # Convert to percentage
        
        # Create pie chart for allocations
        colors = [self.red, self.orange, self.yellow, self.light_yellow][:len(strategies)]
        wedges, texts, autotexts = ax.pie(allocations, labels=strategies, colors=colors,
                                         autopct='%1.1f%%', startangle=90)
        
        # Set text properties manually for matplotlib 2.7 compatibility
        for text in texts + autotexts:
            text.set_color(self.white)
            text.set_fontweight('bold')
        
        # Add APY information in legend
        legend_labels = ["{} ({:.1f}% APY)".format(strategy, apy) 
                        for strategy, apy in zip(strategies, apys)]
        legend = ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        legend.get_frame().set_facecolor(self.black)
        legend.get_frame().set_edgecolor(self.white)
        for text in legend.get_texts():
            text.set_color(self.white)
        
        ax.set_title('Yield Strategy Allocation', 
                    fontsize=14, fontweight='bold', color=self.yellow)
    
    def create_multiplier_analysis_panel(self, ax, results):
        """Panel 3: Native Token Multiplier Analysis"""
        ax.patch.set_facecolor(self.black)
        
        # Sample multiplier data (would come from actual processing)
        multiplier_types = ['Base', 'Liquidity\nMining', 'Governance\nStaking', 
                           'Cross-Pool\nArbitrage', 'Yield\nFarming', 'Liquidation\nBonus']
        multiplier_values = [1.0, 2.0, 1.5, 3.0, 1.8, 3.0]
        colors = [self.gray, self.red, self.orange, self.yellow, self.light_yellow, self.dark_red]
        
        # Create horizontal bar chart with numeric positions
        y_pos = np.arange(len(multiplier_types))
        bars = ax.barh(y_pos, multiplier_values, color=colors, alpha=0.8,
                      edgecolor=self.white, linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(multiplier_types)
        
        # Add value labels
        for bar, value in zip(bars, multiplier_values):
            width = bar.get_width()
            ax.text(width + 0.05, bar.get_y() + bar.get_height()/2.,
                   "{:.1f}x".format(value), ha='left', va='center', 
                   color=self.white, fontweight='bold')
        
        ax.set_title('Native Token Multiplier Breakdown', 
                    fontsize=14, fontweight='bold', color=self.yellow)
        ax.set_xlabel('Multiplier Value', color=self.white, fontweight='bold')
        ax.tick_params(colors=self.white)
        ax.spines['bottom'].set_color(self.white)
        ax.spines['left'].set_color(self.white)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlim(0, max(multiplier_values) * 1.2)
    
    def create_pool_health_panel(self, ax, stats, results):
        """Panel 4: Pool Health Metrics"""
        ax.patch.set_facecolor(self.black)
        
        # Calculate health metrics
        backing_ratio = 0.6  # 60% backing ratio
        utilization = results['total_hype_collected'] / results['pool_tvl_hype']
        yield_rate = results.get('yield_generated_hype', 0) / results['pool_tvl_hype'] * 365 * 100  # Annualized %
        
        # Health indicators
        metrics = ['Backing\nRatio', 'Pool\nUtilization', 'Annual\nYield Rate', 'FRY/HYPE\nRatio']
        values = [backing_ratio * 100, utilization * 100, yield_rate, 
                 results['total_fry_minted'] / results['total_hype_collected']]
        target_values = [60, 80, 15, 300]  # Target benchmarks
        
        # Create gauge-style visualization
        x_pos = np.arange(len(metrics))
        width = 0.35
        
        # Actual values
        bars1 = ax.bar(x_pos - width/2, values, width, label='Current', 
                      color=self.red, alpha=0.8, edgecolor=self.white)
        
        # Target values
        bars2 = ax.bar(x_pos + width/2, target_values, width, label='Target',
                      color=self.yellow, alpha=0.6, edgecolor=self.white)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(max(values), max(target_values))*0.01,
                       "{:.1f}".format(height), ha='center', va='bottom', 
                       color=self.white, fontweight='bold', fontsize=9)
        
        ax.set_title('Pool Health Indicators', 
                    fontsize=14, fontweight='bold', color=self.yellow)
        ax.set_ylabel('Value', color=self.white, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(metrics)
        ax.tick_params(colors=self.white)
        legend = ax.legend()
        legend.get_frame().set_facecolor(self.black)
        legend.get_frame().set_edgecolor(self.white)
        for text in legend.get_texts():
            text.set_color(self.white)
        ax.spines['bottom'].set_color(self.white)
        ax.spines['left'].set_color(self.white)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def create_loss_distribution_panel(self, ax, stats):
        """Panel 5: Loss Pool Distribution"""
        ax.patch.set_facecolor(self.black)
        
        # Extract loss pool data
        pool_names = []
        pool_values = []
        pool_counts = []
        
        for pool_name, pool_data in stats['pool_breakdown'].items():
            if pool_data['event_count'] > 0:
                pool_names.append(pool_name.replace('_', ' ').title())
                pool_values.append(pool_data['total_hype_losses'])
                pool_counts.append(pool_data['event_count'])
        
        if not pool_names:
            # Default data if no pools have events
            pool_names = ['High Leverage', 'Medium Leverage', 'Low Leverage']
            pool_values = [0, 0, 0]
            pool_counts = [0, 0, 0]
        
        # Create stacked bar chart
        x_pos = np.arange(len(pool_names))
        colors = [self.red, self.orange, self.yellow][:len(pool_names)]
        
        bars = ax.bar(x_pos, pool_values, color=colors, alpha=0.8,
                     edgecolor=self.white, linewidth=1)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(pool_names)
        
        # Add count labels on bars
        for bar, count in zip(bars, pool_counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(pool_values)*0.01,
                   "{} events".format(count), ha='center', va='bottom', 
                   color=self.white, fontweight='bold')
        
        ax.set_title('Loss Pool Distribution', 
                    fontsize=14, fontweight='bold', color=self.yellow)
        ax.set_ylabel('$HYPE Losses', color=self.white, fontweight='bold')
        ax.tick_params(colors=self.white)
        ax.spines['bottom'].set_color(self.white)
        ax.spines['left'].set_color(self.white)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def create_arbitrage_panel(self, ax, stats):
        """Panel 6: Cross-Pool Arbitrage Opportunities"""
        ax.patch.set_facecolor(self.black)
        
        # Arbitrage data
        arb_summary = stats['arbitrage_summary']
        opportunities = arb_summary['opportunities_detected']
        potential_profit = arb_summary['total_potential_profit']
        
        # Create simple metrics display
        ax.text(0.5, 0.7, "Arbitrage Opportunities", ha='center', va='center',
               fontsize=16, fontweight='bold', color=self.yellow, transform=ax.transAxes)
        
        ax.text(0.5, 0.5, "Detected: {}".format(opportunities), ha='center', va='center',
               fontsize=14, fontweight='bold', color=self.white, transform=ax.transAxes)
        
        ax.text(0.5, 0.3, "Potential Profit: {:.2f} $HYPE".format(potential_profit), 
               ha='center', va='center', fontsize=14, fontweight='bold', 
               color=self.red, transform=ax.transAxes)
        
        # Add status indicator
        status_color = self.red if opportunities > 0 else self.gray
        status_text = "ACTIVE" if opportunities > 0 else "MONITORING"
        
        ax.text(0.5, 0.1, "Status: {}".format(status_text), ha='center', va='center',
               fontsize=12, fontweight='bold', color=status_color, transform=ax.transAxes)
        
        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

def main():
    """Demo function to generate $HYPE native dashboard"""
    
    # Import the pool class to get sample data
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from hype_native_fry_pool import HypeNativeFRYPool
    
    print("🚀 $HYPE Native FRY Pool Dashboard Generator")
    print("Function: Comprehensive performance visualization")
    
    # Initialize pool and generate sample data
    hype_pool = HypeNativeFRYPool(initial_hype_reserves=100000.0)
    hype_pool.update_hype_price(2.50)  # $2.50 per $HYPE
    
    # Sample losses for dashboard demo
    sample_losses = [
        {
            "trader_id": "trader_001",
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "loss_amount": 5000.0,  # $5000 USD
            "leverage": 15.0,
            "liquidation": False,
            "asset": "ETH",
            "liquidity_mining": True,
            "governance_staking": True
        },
        {
            "trader_id": "trader_002", 
            "wallet_address": "0x2345678901bcdef234567890abcdef1234567890",
            "loss_amount": 2500.0,  # $2500 USD
            "leverage": 8.0,
            "liquidation": False,
            "asset": "SOL",
            "yield_farming": True
        },
        {
            "trader_id": "trader_003",
            "wallet_address": "0x3456789012cdef123456789012cdef1234567890",
            "loss_amount": 12000.0,  # $12000 USD
            "leverage": 25.0,
            "liquidation": True,
            "asset": "BTC",
            "arbitrage": True
        }
    ]
    
    # Process losses and get results
    processing_results = hype_pool.process_hype_losses(sample_losses)
    pool_stats = hype_pool.get_native_pool_stats()
    
    # Generate dashboard
    dashboard = HypeNativeDashboard()
    filename = dashboard.create_native_pool_dashboard(pool_stats, processing_results)
    
    print("\n📊 Dashboard Generated Successfully!")
    print("   File: {}".format(filename))
    print("   Panels: 6 comprehensive metric visualizations")
    print("   Data: Pool TVL, yield strategies, multipliers, health, distribution, arbitrage")
    print("\n✅ $HYPE Native FRY Pool Dashboard ready for analysis")

if __name__ == "__main__":
    main()
