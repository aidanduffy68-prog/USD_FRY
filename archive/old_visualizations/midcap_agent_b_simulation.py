#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mid-Cap Agent B vs Traditional MM Simulation
============================================

Agent B focused exclusively on mid-cap coins (SOL, AVAX, MATIC, ATOM)
with FRY recycling vs traditional market maker on same assets.
"""

import json
import time
import random
import logging
import numpy as np
from collections import defaultdict

class MidCapAgentB:
    """Agent B specialized for mid-cap trading with FRY recycling"""
    
    def __init__(self, initial_capital=500000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Mid-cap focus assets
        self.assets = {
            'SOL': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'AVAX': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'MATIC': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'ATOM': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0}
        }
        
        # FRY system
        self.fry_balance = 0.0
        self.recycled_value = 0.0
        self.slippage_captured = 0.0
        
        # Performance tracking
        self.total_profits = 0.0
        self.total_trades = 0
        self.total_churn = 0.0
        self.win_rate = 0.0
        
        # Mid-cap specific configuration
        self.config = {
            'SOL': {'spread': 0.0025, 'max_inventory': 800, 'quote_size': 25, 'volatility_factor': 1.2},
            'AVAX': {'spread': 0.003, 'max_inventory': 1500, 'quote_size': 40, 'volatility_factor': 1.3},
            'MATIC': {'spread': 0.004, 'max_inventory': 50000, 'quote_size': 2000, 'volatility_factor': 1.5},
            'ATOM': {'spread': 0.0035, 'max_inventory': 3000, 'quote_size': 100, 'volatility_factor': 1.4}
        }
        
        # FRY enhancement parameters
        self.fry_config = {
            'recycling_rate': 0.6,
            'enhancement_multiplier': 1.4,
            'min_slippage_threshold': 0.002,
            'volatility_bonus': 0.3,
            'retail_activity_bonus': 0.25
        }
    
    def analyze_market_data(self, asset, market_data):
        """Analyze market conditions for mid-cap specific patterns"""
        
        price = market_data['price']
        volume = market_data.get('volume', 0)
        volatility = market_data.get('volatility', 0.05)
        social_sentiment = market_data.get('social_sentiment', 0.5)
        large_orders = market_data.get('large_orders_ratio', 0.05)
        
        # Mid-cap specific analysis
        analysis = {
            'price': price,
            'volume': volume,
            'volatility': volatility,
            'retail_activity': social_sentiment > 0.7 and volume > 1000000,
            'whale_activity': large_orders > 0.08,
            'slippage_opportunity': volatility > 0.04 and volume > 800000,
            'fry_enhancement_available': self.fry_balance > 0.1
        }
        
        return analysis
    
    def execute_fry_enhanced_trade(self, asset, market_analysis, timestamp):
        """Execute trades with FRY recycling enhancement"""
        
        config = self.config[asset]
        price = market_analysis['price']
        volume = market_analysis['volume']
        volatility = market_analysis['volatility']
        
        # Base spread with FRY enhancement
        base_spread = config['spread']
        fry_enhancement = 0.0
        
        if self.fry_balance > 0.1:
            fry_factor = min(1.0, self.fry_balance / 5.0)
            fry_enhancement = base_spread * self.fry_config['enhancement_multiplier'] * fry_factor * 0.3
        
        # Volatility and retail bonuses
        volatility_bonus = 0.0
        if volatility > 0.04:
            volatility_bonus = (volatility - 0.04) * self.fry_config['volatility_bonus']
        
        retail_bonus = 0.0
        if market_analysis['retail_activity']:
            retail_bonus = self.fry_config['retail_activity_bonus'] * 0.001
        
        # Dynamic spread calculation
        inventory_penalty = abs(self.assets[asset]['inventory']) / config['max_inventory'] * 0.002
        enhanced_spread = base_spread - fry_enhancement + inventory_penalty + volatility_bonus + retail_bonus
        enhanced_spread = max(0.001, enhanced_spread)
        
        bid_price = price * (1 - enhanced_spread / 2)
        ask_price = price * (1 + enhanced_spread / 2)
        
        # Trade execution with mid-cap specific logic
        fill_probability = self._calculate_fill_probability(asset, market_analysis)
        quote_size = config['quote_size'] * random.uniform(0.7, 1.2)
        
        trades_executed = 0
        
        # Buy orders
        if (random.random() < fill_probability and 
            self.assets[asset]['inventory'] < config['max_inventory'] and
            quote_size * bid_price < self.current_capital * 0.2):
            
            cost = quote_size * bid_price
            self.assets[asset]['inventory'] += quote_size
            self.current_capital -= cost
            
            # Update average cost
            if self.assets[asset]['inventory'] > 0:
                total_cost = self.assets[asset]['avg_cost'] * (self.assets[asset]['inventory'] - quote_size) + cost
                self.assets[asset]['avg_cost'] = total_cost / self.assets[asset]['inventory']
            
            self.assets[asset]['trades'] += 1
            self.total_trades += 1
            self.total_churn += cost
            trades_executed += 1
        
        # Sell orders
        if (random.random() < fill_probability and 
            self.assets[asset]['inventory'] > 0):
            
            sell_size = min(self.assets[asset]['inventory'], quote_size)
            revenue = sell_size * ask_price
            
            self.assets[asset]['inventory'] -= sell_size
            self.current_capital += revenue
            self.total_churn += revenue
            
            # Calculate profit
            profit = (ask_price - self.assets[asset]['avg_cost']) * sell_size
            self.assets[asset]['profits'] += profit
            self.total_profits += profit
            
            # Update win rate
            wins = 1 if profit > 0 else 0
            self.win_rate = (self.win_rate * (self.total_trades - 1) + wins) / self.total_trades
            
            trades_executed += 1
        
        # FRY recycling from slippage
        if market_analysis['slippage_opportunity']:
            self._capture_slippage(asset, market_analysis, trades_executed)
        
        return trades_executed
    
    def _calculate_fill_probability(self, asset, market_analysis):
        """Calculate fill probability based on mid-cap market conditions"""
        
        base_prob = 0.35
        volume = market_analysis['volume']
        
        # Volume-based adjustment
        if asset == 'SOL':
            volume_factor = min(0.4, volume / 2000000)
        elif asset == 'AVAX':
            volume_factor = min(0.35, volume / 1500000)
        elif asset == 'MATIC':
            volume_factor = min(0.3, volume / 1000000)
        else:  # ATOM
            volume_factor = min(0.25, volume / 800000)
        
        # Retail activity bonus
        if market_analysis['retail_activity']:
            volume_factor += 0.1
        
        # Whale activity penalty
        if market_analysis['whale_activity']:
            volume_factor -= 0.05
        
        return min(0.5, base_prob + volume_factor)
    
    def _capture_slippage(self, asset, market_analysis, trades_executed):
        """Capture slippage and convert to FRY tokens"""
        
        if trades_executed == 0:
            return
        
        volume = market_analysis['volume']
        volatility = market_analysis['volatility']
        
        # Estimate slippage based on market conditions
        base_slippage = volatility * 0.5
        volume_slippage = volume / 5000000 * 0.003
        total_slippage = base_slippage + volume_slippage
        
        if total_slippage >= self.fry_config['min_slippage_threshold']:
            # Convert slippage to FRY tokens
            recycled_amount = total_slippage * self.fry_config['recycling_rate'] * trades_executed
            recycled_amount *= random.uniform(0.8, 1.3)  # Market variance
            
            self.fry_balance += recycled_amount
            self.recycled_value += recycled_amount
            self.slippage_captured += total_slippage
    
    def get_metrics(self):
        """Get comprehensive performance metrics"""
        
        # Calculate total inventory value (using approximate prices)
        inventory_values = {
            'SOL': self.assets['SOL']['inventory'] * 100,
            'AVAX': self.assets['AVAX']['inventory'] * 25,
            'MATIC': self.assets['MATIC']['inventory'] * 0.8,
            'ATOM': self.assets['ATOM']['inventory'] * 12
        }
        
        total_inventory_value = sum(inventory_values.values())
        total_capital = self.current_capital + total_inventory_value
        
        return {
            'agent_type': 'MidCap_Agent_B_FRY',
            'total_capital': total_capital,
            'total_return': (total_capital - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'fry_balance': self.fry_balance,
            'recycled_value': self.recycled_value,
            'slippage_captured': self.slippage_captured,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate,
            'total_churn': self.total_churn,
            'inventory_value': total_inventory_value,
            'asset_breakdown': self.assets,
            'inventory_values': inventory_values
        }

class TraditionalMidCapMM:
    """Traditional market maker for mid-cap coins"""
    
    def __init__(self, initial_capital=500000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        self.assets = {
            'SOL': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'AVAX': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'MATIC': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0},
            'ATOM': {'inventory': 0.0, 'avg_cost': 0.0, 'trades': 0, 'profits': 0.0}
        }
        
        self.total_profits = 0.0
        self.total_trades = 0
        self.total_churn = 0.0
        self.win_rate = 0.0
        
        # Conservative mid-cap configuration
        self.config = {
            'SOL': {'spread': 0.004, 'max_inventory': 600, 'quote_size': 20},
            'AVAX': {'spread': 0.0045, 'max_inventory': 1200, 'quote_size': 30},
            'MATIC': {'spread': 0.006, 'max_inventory': 40000, 'quote_size': 1500},
            'ATOM': {'spread': 0.005, 'max_inventory': 2500, 'quote_size': 80}
        }
    
    def execute_traditional_trade(self, asset, market_data):
        """Execute conservative traditional market making"""
        
        config = self.config[asset]
        price = market_data['price']
        volume = market_data.get('volume', 0)
        volatility = market_data.get('volatility', 0.05)
        
        # Conservative spread calculation
        base_spread = config['spread']
        inventory_penalty = abs(self.assets[asset]['inventory']) / config['max_inventory'] * 0.003
        volatility_adjustment = volatility * 2.0  # More conservative
        
        total_spread = base_spread + inventory_penalty + volatility_adjustment
        
        bid_price = price * (1 - total_spread / 2)
        ask_price = price * (1 + total_spread / 2)
        
        # Conservative fill probability
        fill_prob = min(0.25, volume / 3000000)
        quote_size = config['quote_size'] * random.uniform(0.5, 0.9)
        
        # Conservative trading
        if (random.random() < fill_prob and 
            self.assets[asset]['inventory'] < config['max_inventory']):
            
            cost = quote_size * bid_price
            if cost < self.current_capital * 0.15:  # Very conservative
                self.assets[asset]['inventory'] += quote_size
                self.current_capital -= cost
                
                if self.assets[asset]['inventory'] > 0:
                    total_cost = self.assets[asset]['avg_cost'] * (self.assets[asset]['inventory'] - quote_size) + cost
                    self.assets[asset]['avg_cost'] = total_cost / self.assets[asset]['inventory']
                
                self.assets[asset]['trades'] += 1
                self.total_trades += 1
                self.total_churn += cost
        
        # Selling
        if (random.random() < fill_prob and 
            self.assets[asset]['inventory'] > 0):
            
            sell_size = min(self.assets[asset]['inventory'], quote_size)
            revenue = sell_size * ask_price
            
            self.assets[asset]['inventory'] -= sell_size
            self.current_capital += revenue
            self.total_churn += revenue
            
            # Conservative profit calculation
            profit = (ask_price - self.assets[asset]['avg_cost']) * sell_size
            self.assets[asset]['profits'] += profit
            self.total_profits += profit
            
            # High win rate for conservative approach
            self.win_rate = (self.win_rate * (self.total_trades - 1) + 0.85) / self.total_trades
    
    def get_metrics(self):
        """Get performance metrics"""
        
        inventory_values = {
            'SOL': self.assets['SOL']['inventory'] * 100,
            'AVAX': self.assets['AVAX']['inventory'] * 25,
            'MATIC': self.assets['MATIC']['inventory'] * 0.8,
            'ATOM': self.assets['ATOM']['inventory'] * 12
        }
        
        total_inventory_value = sum(inventory_values.values())
        total_capital = self.current_capital + total_inventory_value
        
        return {
            'agent_type': 'Traditional_MidCap_MM',
            'total_capital': total_capital,
            'total_return': (total_capital - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate,
            'total_churn': self.total_churn,
            'inventory_value': total_inventory_value,
            'asset_breakdown': self.assets,
            'inventory_values': inventory_values
        }

def generate_midcap_market_data(asset, base_price, volatility_multiplier=1.0):
    """Generate realistic mid-cap market data"""
    
    # Asset-specific parameters
    asset_params = {
        'SOL': {'base_vol': 0.065, 'volume_range': (800000, 3000000), 'sentiment_range': (0.4, 0.9)},
        'AVAX': {'base_vol': 0.058, 'volume_range': (400000, 1800000), 'sentiment_range': (0.35, 0.85)},
        'MATIC': {'base_vol': 0.072, 'volume_range': (600000, 2500000), 'sentiment_range': (0.3, 0.95)},
        'ATOM': {'base_vol': 0.068, 'volume_range': (300000, 1200000), 'sentiment_range': (0.4, 0.8)}
    }
    
    params = asset_params[asset]
    
    # Price movement
    volatility = params['base_vol'] * volatility_multiplier
    price_change = np.random.normal(0, volatility)
    new_price = base_price * (1 + price_change)
    
    # Market microstructure
    volume = random.uniform(*params['volume_range'])
    social_sentiment = random.uniform(*params['sentiment_range'])
    large_orders_ratio = random.uniform(0.03, 0.12)
    
    return {
        'asset': asset,
        'price': new_price,
        'volume': volume,
        'volatility': volatility,
        'social_sentiment': social_sentiment,
        'large_orders_ratio': large_orders_ratio,
        'timestamp': time.time()
    }

def run_midcap_comparison(duration_minutes=120):
    """Run mid-cap Agent B vs Traditional MM comparison"""
    
    print("🔄 Mid-Cap Agent B vs Traditional MM Simulation")
    print("=" * 60)
    
    # Initialize agents
    agent_b = MidCapAgentB(500000)
    traditional_mm = TraditionalMidCapMM(500000)
    
    # Asset prices
    asset_prices = {'SOL': 100, 'AVAX': 25, 'MATIC': 0.8, 'ATOM': 12}
    
    print("Agent B: FRY-Enhanced Mid-Cap Specialist")
    print("Traditional MM: Conservative Mid-Cap MM")
    print("Assets: SOL, AVAX, MATIC, ATOM")
    print("Duration: {} minutes\n".format(duration_minutes))
    
    for minute in range(duration_minutes):
        timestamp = time.time()
        
        # Trade each asset
        for asset in ['SOL', 'AVAX', 'MATIC', 'ATOM']:
            # Generate market data
            market_data = generate_midcap_market_data(asset, asset_prices[asset])
            asset_prices[asset] = market_data['price']
            
            # Agent B trading with FRY
            analysis = agent_b.analyze_market_data(asset, market_data)
            agent_b.execute_fry_enhanced_trade(asset, analysis, timestamp)
            
            # Traditional MM trading
            traditional_mm.execute_traditional_trade(asset, market_data)
        
        # Progress updates
        if minute % 30 == 0:
            agent_b_metrics = agent_b.get_metrics()
            traditional_metrics = traditional_mm.get_metrics()
            
            print("Min {}: Agent B={:.2f}% (FRY:{:.3f}) | Traditional={:.2f}%".format(
                minute,
                agent_b_metrics['total_return'] * 100,
                agent_b_metrics['fry_balance'],
                traditional_metrics['total_return'] * 100
            ))
    
    # Final results
    print("\n📊 Final Results:")
    print("=" * 60)
    
    final_agent_b = agent_b.get_metrics()
    final_traditional = traditional_mm.get_metrics()
    
    print("\n🚀 Agent B (FRY-Enhanced Mid-Cap):")
    print("Return: {:.2f}%".format(final_agent_b['total_return'] * 100))
    print("Profits: ${:,.2f}".format(final_agent_b['total_profits']))
    print("FRY Balance: {:.4f} tokens".format(final_agent_b['fry_balance']))
    print("Slippage Captured: {:.4f}%".format(final_agent_b['slippage_captured'] * 100))
    print("Trades: {}".format(final_agent_b['total_trades']))
    print("Win Rate: {:.1f}%".format(final_agent_b['win_rate'] * 100))
    print("Churn: ${:,.2f}".format(final_agent_b['total_churn']))
    
    print("\n🏦 Traditional MM:")
    print("Return: {:.2f}%".format(final_traditional['total_return'] * 100))
    print("Profits: ${:,.2f}".format(final_traditional['total_profits']))
    print("Trades: {}".format(final_traditional['total_trades']))
    print("Win Rate: {:.1f}%".format(final_traditional['win_rate'] * 100))
    print("Churn: ${:,.2f}".format(final_traditional['total_churn']))
    
    # Analysis
    return_diff = final_agent_b['total_return'] - final_traditional['total_return']
    churn_diff = final_agent_b['total_churn'] - final_traditional['total_churn']
    
    print("\n📈 Comparative Analysis:")
    print("Return Advantage: {:.2f}% ({})".format(
        return_diff * 100, "Agent B Wins" if return_diff > 0 else "Traditional Wins"))
    print("Profit Difference: ${:,.2f}".format(
        final_agent_b['total_profits'] - final_traditional['total_profits']))
    print("Churn Difference: ${:,.2f}".format(churn_diff))
    print("FRY Recycling Value: ${:.2f}".format(final_agent_b['recycled_value']))
    
    # Asset breakdown
    print("\n💰 Asset Performance (Agent B):")
    for asset, data in final_agent_b['asset_breakdown'].items():
        print("  {}: {} trades, ${:.2f} profit, {:.1f} inventory".format(
            asset, data['trades'], data['profits'], data['inventory']))
    
    # Save results
    results = {
        'agent_b_final': final_agent_b,
        'traditional_final': final_traditional,
        'comparison': {
            'return_difference_pct': return_diff * 100,
            'profit_difference': final_agent_b['total_profits'] - final_traditional['total_profits'],
            'churn_difference': churn_diff,
            'winner': 'Agent_B' if return_diff > 0 else 'Traditional'
        }
    }
    
    results_file = "midcap_agent_b_comparison_{}.json".format(int(time.time()))
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved: {}".format(results_file))
    return results

if __name__ == "__main__":
    run_midcap_comparison(120)