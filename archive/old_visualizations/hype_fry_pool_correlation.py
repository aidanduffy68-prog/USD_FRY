#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
$dydx Price vs $dydx/FRY Pool Value Correlation Analysis
Shows the relationship between native token price and pool performance

Features:
- $dydx price simulation across market conditions
- Pool value calculation based on TVL and FRY minting
- Correlation analysis between price and pool metrics
- Visual representation of native token pool dynamics
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json

# Set non-interactive backend for PNG output
plt.switch_backend('Agg')

class HypeFryPoolCorrelation:
    """
    Analyze and visualize correlation between $dydx price and pool value
    """
    
    def __init__(self):
        # Color scheme - FRY palette on white background
        self.white = '#FFFFFF'
        self.black = '#000000'
        self.red = '#FF4444'
        self.yellow = '#FFD700'
        self.gray = '#7f7f7f'
        self.light_gray = '#d9d9d9'
        
        # Pool parameters
        self.base_hype_reserves = 100000.0
        self.fry_minting_rate = 15.0
        self.backing_ratio = 0.6
        
    def simulate_market_scenarios(self, num_points=50):
        """
        Simulate various $HYPE price scenarios and calculate corresponding pool values
        """
        # Generate $HYPE price range from $0.50 to $10.00
        hype_prices = np.logspace(np.log10(0.5), np.log10(10.0), num_points)
        
        pool_data = []
        
        for hype_price in hype_prices:
            # Simulate trading activity based on price volatility
            # Higher prices tend to generate more trading volume and losses
            price_volatility_factor = min(hype_price / 2.0, 3.0)  # Cap at 3x
            
            # Daily loss simulation (higher prices = more activity)
            daily_losses_usd = 15000 * price_volatility_factor * (1 + np.random.normal(0, 0.2))
            daily_losses_hype = daily_losses_usd / hype_price
            
            # Calculate FRY minting with enhanced multipliers
            base_multiplier = 1.0
            
            # Price-based multipliers (higher prices = more native integration)
            if hype_price >= 5.0:
                base_multiplier *= 2.5  # High price premium
            elif hype_price >= 2.0:
                base_multiplier *= 1.8  # Medium price premium
            elif hype_price >= 1.0:
                base_multiplier *= 1.3  # Low price premium
            
            # Native token bonuses
            liquidity_bonus = 2.0
            governance_bonus = 1.5
            arbitrage_bonus = min(hype_price * 0.5, 3.0)  # Scales with price
            
            total_multiplier = base_multiplier * liquidity_bonus * governance_bonus * arbitrage_bonus
            total_multiplier = min(total_multiplier, 25.0)  # Cap at 25x
            
            fry_minted = daily_losses_hype * self.fry_minting_rate * total_multiplier
            
            # Calculate pool TVL (reserves + locked backing)
            hype_locked = daily_losses_hype * self.backing_ratio
            pool_tvl_hype = self.base_hype_reserves + hype_locked
            pool_tvl_usd = pool_tvl_hype * hype_price
            
            # Calculate yield generation (higher prices = better yield opportunities)
            yield_rate = 0.12 + (hype_price - 1.0) * 0.02  # 12% base + 2% per dollar
            yield_rate = max(0.08, min(yield_rate, 0.25))  # Cap between 8-25%
            daily_yield_hype = pool_tvl_hype * yield_rate / 365
            
            # Pool value metrics
            fry_market_cap_hype = fry_minted * 0.1  # Assume FRY trades at 0.1 HYPE
            total_pool_value_hype = pool_tvl_hype + fry_market_cap_hype + daily_yield_hype * 30  # 30-day yield
            total_pool_value_usd = total_pool_value_hype * hype_price
            
            pool_data.append({
                'hype_price': hype_price,
                'daily_losses_hype': daily_losses_hype,
                'fry_minted': fry_minted,
                'total_multiplier': total_multiplier,
                'pool_tvl_hype': pool_tvl_hype,
                'pool_tvl_usd': pool_tvl_usd,
                'daily_yield_hype': daily_yield_hype,
                'total_pool_value_hype': total_pool_value_hype,
                'total_pool_value_usd': total_pool_value_usd,
                'yield_rate': yield_rate
            })
        
        return pool_data
    
    def create_correlation_graph(self, pool_data):
        """
        Create comprehensive correlation visualization
        """
        # Create figure with Instagram square dimensions (1080x1080)
        fig = plt.figure(figsize=(10.8, 10.8), facecolor=self.white)
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
        
        # Extract data arrays
        hype_prices = [d['hype_price'] for d in pool_data]
        pool_values_usd = [d['total_pool_value_usd'] for d in pool_data]
        pool_values_hype = [d['total_pool_value_hype'] for d in pool_data]
        fry_minted = [d['fry_minted'] for d in pool_data]
        multipliers = [d['total_multiplier'] for d in pool_data]
        yield_rates = [d['yield_rate'] * 100 for d in pool_data]  # Convert to percentage
        
        # Panel 1: $dydx Price vs Pool Value ($dydx) - Native token focus
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.patch.set_facecolor(self.white)
        ax1.scatter(hype_prices, pool_values_hype, c=self.black, alpha=0.6, s=60, edgecolors=self.white, linewidth=0.5)
        ax1.plot(hype_prices, pool_values_hype, color=self.red, linewidth=3, alpha=0.9)
        
        ax1.set_title('$dydx Price vs Pool Value', fontsize=14, fontweight='bold', color=self.black)
        ax1.set_xlabel('$dydx Price (USD)', color=self.black, fontsize=12)
        ax1.set_ylabel('Pool Value ($dydx)', color=self.black, fontsize=12)
        ax1.tick_params(colors=self.black, labelsize=11)
        ax1.grid(True, alpha=0.3, color=self.light_gray, linewidth=0.5)
        ax1.set_xscale('log')
        
        for spine in ax1.spines.values():
            spine.set_color(self.gray)
            spine.set_linewidth(0.8)
        
        # Panel 2: FRY Supply vs $dydx Funding Rate Stabilization
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.patch.set_facecolor(self.white)
        
        # Generate time series data for funding rates and FRY supply
        time_points = np.linspace(0, 365, len(pool_data))  # 1 year timeline
        
        # Calculate cumulative FRY supply over time
        cumulative_fry_supply = []
        running_total = 0
        for data in pool_data:
            running_total += data['fry_minted']
            cumulative_fry_supply.append(running_total)
        
        # Generate $HYPE funding rates that correlate inversely with FRY supply (stablecoin behavior)
        # Higher FRY supply should stabilize funding rates around 0%
        base_funding_rates = []
        for i, supply in enumerate(cumulative_fry_supply):
            # Base volatility decreases as FRY supply increases (stabilizing effect)
            volatility_dampening = 1.0 / (1.0 + supply / 1000000.0)  # Dampening factor
            
            # Market stress creates funding rate spikes, but FRY supply absorbs them
            market_stress = np.sin(time_points[i] * 0.05) * 0.15  # Cyclical market stress
            noise = np.random.normal(0, 0.02)  # Random noise
            
            # FRY acts as a stabilizer - higher supply = lower funding rate volatility
            funding_rate = market_stress * volatility_dampening + noise
            base_funding_rates.append(funding_rate * 100)  # Convert to percentage
        
        # Create dual y-axis plot
        ax2_twin = ax2.twinx()
        
        # Plot FRY supply curve (left axis)
        line1 = ax2.plot(time_points, cumulative_fry_supply, color=self.red, linewidth=3, 
                        label='FRY Supply', alpha=0.9)
        
        # Plot funding rates (right axis)  
        line2 = ax2_twin.plot(time_points, base_funding_rates, color=self.yellow, linewidth=2.5,
                             label='$dydx Funding Rate', alpha=0.9, linestyle='-')
        
        # Fill area to show stabilization zone
        ax2_twin.fill_between(time_points, -2, 2, color=self.yellow, alpha=0.15, label='Stable Zone')
        
        ax2.set_title('FRY Supply vs $dydx Funding Rate', 
                     fontsize=14, fontweight='bold', color=self.black)
        ax2.set_xlabel('Time (Days)', color=self.black, fontsize=12)
        ax2.set_ylabel('FRY Supply', color=self.red, fontsize=12)
        ax2_twin.set_ylabel('Funding Rate (%)', color=self.black, fontsize=12)
        
        # Style both axes
        ax2.tick_params(colors=self.black, axis='x', labelsize=11)
        ax2.tick_params(colors=self.red, axis='y', labelsize=11)
        ax2_twin.tick_params(colors=self.black, axis='y', labelsize=11)
        ax2.grid(True, alpha=0.3, color=self.light_gray, linewidth=0.5)
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left', facecolor=self.white, 
                  edgecolor=self.gray, labelcolor=self.black, fontsize=11)
        
        for spine in ax2.spines.values():
            spine.set_color(self.gray)
            spine.set_linewidth(0.8)
        for spine in ax2_twin.spines.values():
            spine.set_color(self.gray)
            spine.set_linewidth(0.8)
        
        # Panel 3: Capital Efficiency Comparison (centered across bottom row)
        ax3 = fig.add_subplot(gs[1, :])
        ax3.patch.set_facecolor(self.white)
        
        # Calculate capital efficiency metrics
        usdc_hype_efficiency = []
        fry_hype_efficiency = []
        
        for data in pool_data:
            # USDC-HYPE pool (traditional): Lower multipliers, no native bonuses
            usdc_base_multiplier = 1.0
            
            # Price-based multipliers (higher prices = more native integration)
            if data['hype_price'] >= 2.0:
                usdc_base_multiplier *= 1.2  # Minimal price bonus
            
            usdc_fry_output = data['daily_losses_hype'] * self.fry_minting_rate * usdc_base_multiplier
            usdc_capital_efficiency = usdc_fry_output / data['pool_tvl_hype']
            usdc_hype_efficiency.append(usdc_capital_efficiency)
            
            # FRY-HYPE pool (native): Full multipliers and bonuses
            fry_capital_efficiency = data['fry_minted'] / data['pool_tvl_hype']
            fry_hype_efficiency.append(fry_capital_efficiency)
        
        # Plot efficiency curves
        ax3.plot(hype_prices, usdc_hype_efficiency, color=self.gray, linewidth=2.5, 
                linestyle='--', alpha=0.8, label='USDC-$dydx Pool')
        ax3.plot(hype_prices, fry_hype_efficiency, color=self.red, linewidth=3, 
                alpha=0.9, label='FRY-$dydx Pool')
        
        # Fill area between curves to show efficiency gap
        ax3.fill_between(hype_prices, usdc_hype_efficiency, fry_hype_efficiency, 
                        color=self.yellow, alpha=0.2, label='Efficiency Advantage')
        
        ax3.set_title('Capital Efficiency Comparison', 
                     fontsize=14, fontweight='bold', color=self.black)
        ax3.set_xlabel('$dydx Price (USD)', color=self.black, fontsize=12)
        ax3.set_ylabel('Capital Efficiency Ratio', color=self.black, fontsize=12)
        ax3.tick_params(colors=self.black, labelsize=11)
        ax3.grid(True, alpha=0.3, color=self.light_gray, linewidth=0.5)
        ax3.set_xscale('log')
        
        # Add legend
        legend = ax3.legend(loc='upper left', facecolor=self.white, edgecolor=self.gray, fontsize=11)
        legend.get_frame().set_edgecolor(self.gray)
        for text in legend.get_texts():
            text.set_color(self.black)
        
        for spine in ax3.spines.values():
            spine.set_color(self.gray)
            spine.set_linewidth(0.8)
        
        # Panel 4 removed per request (no summary panel)
        
        # Calculate final statistics
        correlation_hype = np.corrcoef(hype_prices, pool_values_hype)[0, 1]
        fry_funding_correlation = np.corrcoef(cumulative_fry_supply, base_funding_rates)[0, 1]
        efficiency_advantage = np.mean([f/u for f, u in zip(fry_hype_efficiency, usdc_hype_efficiency)])
        max_efficiency_gap = max([f/u for f, u in zip(fry_hype_efficiency, usdc_hype_efficiency)])
        funding_volatility_early = np.std(base_funding_rates[:len(base_funding_rates)//3])
        funding_volatility_late = np.std(base_funding_rates[-len(base_funding_rates)//3:])
        volatility_reduction = (funding_volatility_early - funding_volatility_late) / funding_volatility_early
        
        # Add main title
        fig.suptitle('FRY Native Pool Analysis ($dydx)',
                    fontsize=16, fontweight='bold', color=self.black, y=0.95)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.02, 0.02, "Generated: {}".format(timestamp), 
                fontsize=9, color=self.gray)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        
        # Save graph
        filename = "hype_fry_pool_correlation_{}.png".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.white, edgecolor='none')
        plt.close()
        
        return filename, {
            'correlation_hype': correlation_hype,
            'fry_funding_correlation': fry_funding_correlation,
            'volatility_reduction': volatility_reduction,
            'efficiency_advantage': efficiency_advantage,
            'max_efficiency_gap': max_efficiency_gap,
            'price_range': (min(hype_prices), max(hype_prices)),
            'pool_value_range_hype': (min(pool_values_hype), max(pool_values_hype))
        }

def main():
    """Demo function to generate $HYPE/FRY pool correlation analysis"""
    
    print("🚀 $dydx Price vs Pool Value Correlation Analysis")
    print("Function: Analyze relationship between native token price and pool performance")
    
    # Initialize correlation analyzer
    analyzer = HypeFryPoolCorrelation()
    
    print("\n📊 Simulating market scenarios...")
    # Generate pool data across price range
    pool_data = analyzer.simulate_market_scenarios(num_points=75)
    
    print("   Price Range: ${:.2f} - ${:.2f}".format(
        min(d['hype_price'] for d in pool_data),
        max(d['hype_price'] for d in pool_data)
    ))
    
    print("   Pool Value Range: ${:,.0f} - ${:,.0f}".format(
        min(d['total_pool_value_usd'] for d in pool_data),
        max(d['total_pool_value_usd'] for d in pool_data)
    ))
    
    # Create correlation visualization
    print("\n📈 Generating correlation graphs...")
    filename, stats = analyzer.create_correlation_graph(pool_data)
    
    print("\n📊 Correlation Analysis Results:")
    print("   File: {}".format(filename))
    print("   $dydx Price vs $dydx Pool Value: {:.3f}".format(stats['correlation_hype']))
    print("   FRY Supply vs Funding Rate Correlation: {:.3f}".format(stats['fry_funding_correlation']))
    print("   Funding Rate Volatility Reduction: {:.1%}".format(stats['volatility_reduction']))
    print("   Average Capital Efficiency Advantage: {:.1f}x".format(stats['efficiency_advantage']))
    print("   Maximum Efficiency Gap: {:.1f}x".format(stats['max_efficiency_gap']))
    
    # Interpretation
    print("\n🔍 Key Insights:")
    if stats['correlation_hype'] > 0.8:
        print("   • STRONG positive correlation between $dydx price and native pool value")
    elif stats['correlation_hype'] > 0.5:
        print("   • MODERATE positive correlation between $dydx price and native pool value")
    else:
        print("   • WEAK correlation between $dydx price and native pool value")
    
    if stats['fry_funding_correlation'] < -0.3:
        print("   • FRY supply shows STABILIZING effect on $dydx funding rates")
        print("   • Acts as stablecoin-like mechanism for $dydx wreckage absorption")
    
    if stats['volatility_reduction'] > 0.2:
        print("   • {:.1%} reduction in funding rate volatility as FRY supply increases".format(stats['volatility_reduction']))
    
    if stats['efficiency_advantage'] > 2.0:
        print("   • FRY-$dydx pools show SUPERIOR capital efficiency vs USDC-$dydx pools")
        print("   • Native token integration provides {:.1f}x average efficiency advantage".format(stats['efficiency_advantage']))
    
    print("\n✅ $dydx/FRY Pool Correlation Analysis Complete")

if __name__ == "__main__":
    main()
