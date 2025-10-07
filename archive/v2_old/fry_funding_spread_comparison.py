#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRY vs Normal Funding Spread Comparison
=======================================

Compares funding spreads created by $FRY recycling system vs normal 
funding rates for large coins (BTC, ETH, SOL, AVAX, etc.)

Analyzes:
- Traditional funding rate mechanisms
- FRY-enhanced funding spreads
- Arbitrage opportunities
- Capital efficiency differences
"""

import json
import time
import random
import logging
import numpy as np
from datetime import datetime
from collections import defaultdict

class FundingRateEngine:
    """Traditional funding rate calculation engine"""
    
    def __init__(self):
        self.funding_history = {}
        self.open_interest = {}
        self.long_short_ratio = {}
        
        # Standard funding parameters
        self.config = {
            'base_funding_rate': 0.0001,  # 0.01% every 8 hours
            'max_funding_rate': 0.0075,   # 0.75% cap
            'funding_interval_hours': 8,
            'premium_index_weight': 0.7,
            'oi_imbalance_weight': 0.3
        }
    
    def calculate_funding_rate(self, asset, market_data):
        """Calculate traditional funding rate"""
        
        spot_price = market_data['spot_price']
        perp_price = market_data['perp_price']
        open_interest = market_data['open_interest']
        long_ratio = market_data['long_short_ratio']
        
        # Premium/discount component
        premium = (perp_price - spot_price) / spot_price
        premium_component = premium * self.config['premium_index_weight']
        
        # Open interest imbalance component
        oi_imbalance = (long_ratio - 0.5) * 2  # Normalize to [-1, 1]
        oi_component = oi_imbalance * self.config['oi_imbalance_weight'] * 0.001
        
        # Base funding rate
        raw_funding = self.config['base_funding_rate'] + premium_component + oi_component
        
        # Apply caps
        funding_rate = max(-self.config['max_funding_rate'], 
                          min(self.config['max_funding_rate'], raw_funding))
        
        # Store history
        if asset not in self.funding_history:
            self.funding_history[asset] = []
        
        self.funding_history[asset].append({
            'timestamp': time.time(),
            'funding_rate': funding_rate,
            'premium': premium,
            'oi_imbalance': oi_imbalance,
            'spot_price': spot_price,
            'perp_price': perp_price
        })
        
        return funding_rate

class FRYFundingEngine:
    """FRY-enhanced funding rate system"""
    
    def __init__(self):
        self.fry_pools = {}
        self.recycled_funding = {}
        self.slippage_capture = {}
        
        # FRY enhancement parameters
        self.config = {
            'fry_funding_multiplier': 1.4,    # 40% enhancement
            'slippage_recycling_rate': 0.6,   # 60% of slippage recycled
            'min_fry_threshold': 0.1,         # Minimum FRY for enhancement
            'max_enhancement_rate': 0.002,    # 0.2% max additional funding
            'volatility_bonus_factor': 0.3,   # Bonus during high volatility
            'retail_activity_bonus': 0.25     # Bonus during retail activity
        }
    
    def calculate_fry_enhanced_funding(self, asset, market_data, base_funding_rate):
        """Calculate FRY-enhanced funding rate"""
        
        # Get current FRY pool for asset
        current_fry = self.fry_pools.get(asset, 0.0)
        
        # Base enhancement from FRY pool
        fry_enhancement = 0.0
        if current_fry >= self.config['min_fry_threshold']:
            fry_factor = min(1.0, current_fry / 10.0)  # Scale to pool size
            fry_enhancement = base_funding_rate * self.config['fry_funding_multiplier'] * fry_factor
        
        # Slippage recycling component
        slippage_component = self._calculate_slippage_recycling(asset, market_data)
        
        # Volatility bonus
        volatility = market_data.get('volatility', 0.02)
        volatility_bonus = 0.0
        if volatility > 0.04:  # High volatility threshold
            volatility_bonus = (volatility - 0.04) * self.config['volatility_bonus_factor']
        
        # Retail activity bonus
        retail_bonus = self._calculate_retail_bonus(market_data)
        
        # Total FRY enhancement
        total_enhancement = (fry_enhancement + slippage_component + 
                           volatility_bonus + retail_bonus)
        
        # Apply caps
        total_enhancement = min(self.config['max_enhancement_rate'], total_enhancement)
        
        enhanced_funding_rate = base_funding_rate + total_enhancement
        
        # Update FRY pool (simulate consumption)
        if total_enhancement > 0:
            fry_consumed = total_enhancement * 100  # Convert to FRY tokens
            self.fry_pools[asset] = max(0, current_fry - fry_consumed * 0.1)
        
        # Store metrics
        if asset not in self.recycled_funding:
            self.recycled_funding[asset] = []
        
        self.recycled_funding[asset].append({
            'timestamp': time.time(),
            'base_funding': base_funding_rate,
            'enhanced_funding': enhanced_funding_rate,
            'fry_enhancement': fry_enhancement,
            'slippage_component': slippage_component,
            'volatility_bonus': volatility_bonus,
            'retail_bonus': retail_bonus,
            'fry_pool_size': current_fry,
            'total_enhancement': total_enhancement
        })
        
        return enhanced_funding_rate
    
    def _calculate_slippage_recycling(self, asset, market_data):
        """Calculate funding enhancement from slippage recycling"""
        
        volume = market_data.get('volume', 0)
        large_orders = market_data.get('large_orders_ratio', 0)
        spread = market_data.get('spread', 0.001)
        
        # Estimate slippage from market activity
        estimated_slippage = (volume / 10000000) * spread * (1 + large_orders * 2)
        
        # Recycle portion as funding enhancement
        recycled_amount = (estimated_slippage * self.config['slippage_recycling_rate'] * 
                          random.uniform(0.8, 1.2))
        
        # Add to FRY pool
        if asset not in self.fry_pools:
            self.fry_pools[asset] = 0.0
        
        self.fry_pools[asset] += recycled_amount * 50  # Convert to FRY tokens
        
        return recycled_amount
    
    def _calculate_retail_bonus(self, market_data):
        """Calculate bonus from retail trading activity"""
        
        social_sentiment = market_data.get('social_sentiment', 0.5)
        small_orders_ratio = market_data.get('small_orders_ratio', 0.3)
        
        # High retail activity indicators
        if social_sentiment > 0.75 and small_orders_ratio > 0.6:
            return self.config['retail_activity_bonus'] * 0.001
        
        return 0.0

class FundingSpreadComparator:
    """Compare funding spreads between traditional and FRY systems"""
    
    def __init__(self, assets=['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC']):
        self.assets = assets
        self.traditional_engine = FundingRateEngine()
        self.fry_engine = FRYFundingEngine()
        
        # Initialize FRY pools with some starting balance
        for asset in assets:
            self.fry_engine.fry_pools[asset] = random.uniform(5.0, 15.0)
        
        self.comparison_data = []
        self.arbitrage_opportunities = []
    
    def generate_market_data(self, asset, base_price):
        """Generate realistic market data for asset"""
        
        # Asset-specific parameters
        asset_params = {
            'BTC': {'volatility': 0.035, 'volume_base': 2000000, 'liquidity': 'high'},
            'ETH': {'volatility': 0.042, 'volume_base': 1500000, 'liquidity': 'high'},
            'SOL': {'volatility': 0.065, 'volume_base': 800000, 'liquidity': 'medium'},
            'AVAX': {'volatility': 0.058, 'volume_base': 400000, 'liquidity': 'medium'},
            'MATIC': {'volatility': 0.072, 'volume_base': 300000, 'liquidity': 'medium'}
        }
        
        params = asset_params.get(asset, asset_params['BTC'])
        
        # Generate correlated spot and perp prices
        price_change = np.random.normal(0, params['volatility'])
        spot_price = base_price * (1 + price_change)
        
        # Perp premium/discount
        premium = np.random.normal(0, 0.002)  # Average 0.2% premium variance
        perp_price = spot_price * (1 + premium)
        
        # Market microstructure
        volume = params['volume_base'] * random.uniform(0.6, 2.5)
        open_interest = volume * random.uniform(8, 25)
        long_short_ratio = random.uniform(0.35, 0.75)
        
        # Order flow characteristics
        large_orders_ratio = random.uniform(0.02, 0.12)
        small_orders_ratio = 1 - large_orders_ratio - random.uniform(0.3, 0.6)
        
        # Social/sentiment indicators
        social_sentiment = random.uniform(0.3, 0.95)
        
        # Spread based on liquidity
        base_spread = {'high': 0.0008, 'medium': 0.0015, 'low': 0.003}
        spread = base_spread[params['liquidity']] * random.uniform(0.7, 1.8)
        
        return {
            'asset': asset,
            'timestamp': time.time(),
            'spot_price': spot_price,
            'perp_price': perp_price,
            'volume': volume,
            'open_interest': open_interest,
            'long_short_ratio': long_short_ratio,
            'volatility': params['volatility'],
            'spread': spread,
            'large_orders_ratio': large_orders_ratio,
            'small_orders_ratio': small_orders_ratio,
            'social_sentiment': social_sentiment,
            'premium': premium
        }
    
    def run_comparison(self, duration_hours=24, intervals_per_hour=3):
        """Run funding spread comparison simulation"""
        
        print("🔄 FRY vs Normal Funding Spread Comparison")
        print("=" * 60)
        print("Assets: {}".format(", ".join(self.assets)))
        print("Duration: {} hours ({} intervals)".format(duration_hours, duration_hours * intervals_per_hour))
        print()
        
        # Initialize asset prices
        asset_prices = {
            'BTC': 50000, 'ETH': 3000, 'SOL': 100, 
            'AVAX': 25, 'MATIC': 0.8
        }
        
        total_intervals = duration_hours * intervals_per_hour
        
        for interval in range(total_intervals):
            interval_data = {}
            
            for asset in self.assets:
                # Generate market data
                market_data = self.generate_market_data(asset, asset_prices[asset])
                asset_prices[asset] = market_data['spot_price']  # Update price
                
                # Calculate traditional funding rate
                traditional_funding = self.traditional_engine.calculate_funding_rate(asset, market_data)
                
                # Calculate FRY-enhanced funding rate
                fry_funding = self.fry_engine.calculate_fry_enhanced_funding(
                    asset, market_data, traditional_funding)
                
                # Calculate spread difference
                funding_spread_advantage = fry_funding - traditional_funding
                
                # Store comparison data
                comparison_point = {
                    'interval': interval,
                    'hour': interval / intervals_per_hour,
                    'asset': asset,
                    'market_data': market_data,
                    'traditional_funding': traditional_funding,
                    'fry_funding': fry_funding,
                    'spread_advantage': funding_spread_advantage,
                    'fry_pool_size': self.fry_engine.fry_pools.get(asset, 0),
                    'annualized_advantage': funding_spread_advantage * 365 * 3  # 3 funding periods per day
                }
                
                self.comparison_data.append(comparison_point)
                interval_data[asset] = comparison_point
                
                # Check for arbitrage opportunities
                if abs(funding_spread_advantage) > 0.0005:  # 0.05% threshold
                    self.arbitrage_opportunities.append({
                        'timestamp': market_data['timestamp'],
                        'asset': asset,
                        'spread_advantage': funding_spread_advantage,
                        'traditional_rate': traditional_funding,
                        'fry_rate': fry_funding,
                        'opportunity_type': 'fry_advantage' if funding_spread_advantage > 0 else 'traditional_advantage'
                    })
            
            # Progress update every 8 intervals (roughly every 2.67 hours)
            if interval % 8 == 0:
                hour = interval / intervals_per_hour
                sample_asset = self.assets[0]
                sample_data = interval_data.get(sample_asset, {})
                
                print("Hour {:.1f}: {} - Traditional: {:.4f}% | FRY: {:.4f}% | Advantage: {:.4f}%".format(
                    hour,
                    sample_asset,
                    sample_data.get('traditional_funding', 0) * 100,
                    sample_data.get('fry_funding', 0) * 100,
                    sample_data.get('spread_advantage', 0) * 100
                ))
        
        self._analyze_results()
        return self.comparison_data
    
    def _analyze_results(self):
        """Analyze and display comparison results"""
        
        print("\n📊 Funding Spread Analysis:")
        print("=" * 60)
        
        # Aggregate results by asset
        asset_summaries = {}
        
        for asset in self.assets:
            asset_data = [d for d in self.comparison_data if d['asset'] == asset]
            
            if not asset_data:
                continue
            
            traditional_rates = [d['traditional_funding'] for d in asset_data]
            fry_rates = [d['fry_funding'] for d in asset_data]
            advantages = [d['spread_advantage'] for d in asset_data]
            
            asset_summaries[asset] = {
                'avg_traditional_funding': np.mean(traditional_rates),
                'avg_fry_funding': np.mean(fry_rates),
                'avg_spread_advantage': np.mean(advantages),
                'max_advantage': max(advantages),
                'min_advantage': min(advantages),
                'advantage_volatility': np.std(advantages),
                'positive_advantage_pct': len([a for a in advantages if a > 0]) / len(advantages) * 100,
                'annualized_advantage': np.mean(advantages) * 365 * 3,
                'final_fry_pool': self.fry_engine.fry_pools.get(asset, 0)
            }
        
        # Display asset-by-asset results
        for asset, summary in asset_summaries.items():
            print("\n💰 {}:".format(asset))
            print("  Traditional Avg: {:.4f}% per funding period".format(summary['avg_traditional_funding'] * 100))
            print("  FRY Enhanced Avg: {:.4f}% per funding period".format(summary['avg_fry_funding'] * 100))
            print("  Spread Advantage: {:.4f}% ({:.2f}% of periods positive)".format(
                summary['avg_spread_advantage'] * 100, summary['positive_advantage_pct']))
            print("  Annualized Advantage: {:.2f}%".format(summary['annualized_advantage'] * 100))
            print("  Max Advantage: {:.4f}% | Min: {:.4f}%".format(
                summary['max_advantage'] * 100, summary['min_advantage'] * 100))
            print("  FRY Pool Remaining: {:.2f} tokens".format(summary['final_fry_pool']))
        
        # Overall analysis
        all_advantages = [d['spread_advantage'] for d in self.comparison_data]
        overall_avg_advantage = np.mean(all_advantages)
        
        print("\n🎯 Overall Analysis:")
        print("  Average FRY Advantage: {:.4f}% per funding period".format(overall_avg_advantage * 100))
        print("  Annualized Advantage: {:.2f}%".format(overall_avg_advantage * 365 * 3 * 100))
        print("  Total Arbitrage Opportunities: {}".format(len(self.arbitrage_opportunities)))
        
        fry_advantages = len([a for a in self.arbitrage_opportunities if a['opportunity_type'] == 'fry_advantage'])
        print("  FRY Advantage Opportunities: {} ({:.1f}%)".format(
            fry_advantages, fry_advantages / max(1, len(self.arbitrage_opportunities)) * 100))
        
        # Capital efficiency analysis
        print("\n💡 Capital Efficiency:")
        total_enhancement = sum(d.get('spread_advantage', 0) for d in self.comparison_data if d.get('spread_advantage', 0) > 0)
        print("  Total Funding Enhancement: {:.4f}%".format(total_enhancement * 100))
        print("  Enhancement per Asset: {:.4f}%".format(total_enhancement / len(self.assets) * 100))
        
        # Save detailed results
        results = {
            'asset_summaries': asset_summaries,
            'comparison_data': self.comparison_data[-50:],  # Last 50 data points
            'arbitrage_opportunities': self.arbitrage_opportunities,
            'overall_metrics': {
                'avg_advantage': overall_avg_advantage,
                'annualized_advantage': overall_avg_advantage * 365 * 3,
                'total_opportunities': len(self.arbitrage_opportunities),
                'fry_advantage_opportunities': fry_advantages
            }
        }
        
        results_file = "fry_funding_comparison_{}.json".format(int(time.time()))
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n💾 Results saved: {}".format(results_file))

def run_funding_comparison():
    """Main function to run funding spread comparison"""
    
    comparator = FundingSpreadComparator()
    results = comparator.run_comparison(duration_hours=24, intervals_per_hour=3)
    
    return results

if __name__ == "__main__":
    run_funding_comparison()
