#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hybrid Mid-Cap Agents Simulation
================================

Combines Agent B (FRY-enhanced) and Traditional MM working together
on mid-cap coins with intelligent capital allocation and coordination.
"""

import json
import time
import random
import logging
import numpy as np
from collections import defaultdict

class HybridMidCapAgent:
    """Hybrid agent combining FRY Agent B and Traditional MM strategies"""
    
    def __init__(self, initial_capital=500000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Capital allocation between strategies
        self.fry_capital = initial_capital * 0.6  # 60% to FRY strategy
        self.traditional_capital = initial_capital * 0.4  # 40% to traditional
        
        # Mid-cap assets tracking
        self.assets = {
            'SOL': {
                'fry_inventory': 0.0, 'fry_avg_cost': 0.0, 'fry_trades': 0, 'fry_profits': 0.0,
                'trad_inventory': 0.0, 'trad_avg_cost': 0.0, 'trad_trades': 0, 'trad_profits': 0.0
            },
            'AVAX': {
                'fry_inventory': 0.0, 'fry_avg_cost': 0.0, 'fry_trades': 0, 'fry_profits': 0.0,
                'trad_inventory': 0.0, 'trad_avg_cost': 0.0, 'trad_trades': 0, 'trad_profits': 0.0
            },
            'MATIC': {
                'fry_inventory': 0.0, 'fry_avg_cost': 0.0, 'fry_trades': 0, 'fry_profits': 0.0,
                'trad_inventory': 0.0, 'trad_avg_cost': 0.0, 'trad_trades': 0, 'trad_profits': 0.0
            },
            'ATOM': {
                'fry_inventory': 0.0, 'fry_avg_cost': 0.0, 'fry_trades': 0, 'fry_profits': 0.0,
                'trad_inventory': 0.0, 'trad_avg_cost': 0.0, 'trad_trades': 0, 'trad_profits': 0.0
            }
        }
        
        # FRY system
        self.fry_balance = 0.0
        self.recycled_value = 0.0
        self.slippage_captured = 0.0
        
        # Performance tracking
        self.total_profits = 0.0
        self.total_trades = 0
        self.total_churn = 0.0
        self.fry_win_rate = 0.0
        self.trad_win_rate = 0.0
        
        # Strategy configurations
        self.fry_config = {
            'SOL': {'spread': 0.003, 'max_inventory': 400, 'quote_size': 15},
            'AVAX': {'spread': 0.0035, 'max_inventory': 800, 'quote_size': 25},
            'MATIC': {'spread': 0.0045, 'max_inventory': 25000, 'quote_size': 1200},
            'ATOM': {'spread': 0.004, 'max_inventory': 1500, 'quote_size': 60}
        }
        
        self.traditional_config = {
            'SOL': {'spread': 0.0045, 'max_inventory': 300, 'quote_size': 12},
            'AVAX': {'spread': 0.005, 'max_inventory': 600, 'quote_size': 18},
            'MATIC': {'spread': 0.0065, 'max_inventory': 20000, 'quote_size': 800},
            'ATOM': {'spread': 0.0055, 'max_inventory': 1200, 'quote_size': 45}
        }
        
        # Coordination parameters
        self.coordination = {
            'inventory_sharing': True,
            'risk_sharing': True,
            'profit_rebalancing': True,
            'strategy_switching_threshold': 0.02  # 2% performance difference
        }
    
    def analyze_market_regime(self, asset, market_data):
        """Determine optimal strategy allocation based on market conditions"""
        
        volatility = market_data.get('volatility', 0.05)
        volume = market_data.get('volume', 0)
        social_sentiment = market_data.get('social_sentiment', 0.5)
        large_orders = market_data.get('large_orders_ratio', 0.05)
        
        # Market regime classification
        regime = {
            'high_volatility': volatility > 0.06,
            'high_volume': volume > 1500000,
            'retail_dominated': social_sentiment > 0.7 and large_orders < 0.06,
            'whale_activity': large_orders > 0.09,
            'trending': abs(np.mean(market_data.get('recent_returns', [0]))) > 0.02
        }
        
        # Strategy allocation based on regime
        if regime['retail_dominated'] and regime['high_volatility']:
            # FRY excels in retail-heavy volatile markets
            fry_allocation = 0.75
        elif regime['whale_activity'] or not regime['high_volume']:
            # Traditional MM better in whale-dominated or low-volume markets
            fry_allocation = 0.35
        elif regime['trending'] and regime['high_volume']:
            # Balanced approach for trending high-volume markets
            fry_allocation = 0.6
        else:
            # Default balanced allocation
            fry_allocation = 0.5
        
        return {
            'fry_allocation': fry_allocation,
            'traditional_allocation': 1 - fry_allocation,
            'regime': regime,
            'coordination_mode': 'active' if regime['high_volatility'] else 'passive'
        }
    
    def execute_fry_strategy(self, asset, market_data, allocation_factor, timestamp):
        """Execute FRY-enhanced trading strategy"""
        
        config = self.fry_config[asset]
        price = market_data['price']
        volatility = market_data.get('volatility', 0.05)
        
        # Adjusted position sizing based on allocation
        effective_capital = self.fry_capital * allocation_factor
        quote_size = config['quote_size'] * allocation_factor * random.uniform(0.8, 1.2)
        
        # FRY-enhanced spread calculation
        base_spread = config['spread']
        fry_enhancement = 0.0
        
        if self.fry_balance > 0.1:
            fry_factor = min(1.0, self.fry_balance / 8.0)
            fry_enhancement = base_spread * 1.3 * fry_factor * 0.25
        
        # Dynamic spread with coordination
        inventory_penalty = abs(self.assets[asset]['fry_inventory']) / config['max_inventory'] * 0.0015
        
        # Coordination with traditional strategy
        if self.coordination['inventory_sharing']:
            total_inventory = self.assets[asset]['fry_inventory'] + self.assets[asset]['trad_inventory']
            coordination_penalty = abs(total_inventory) / (config['max_inventory'] * 1.5) * 0.001
        else:
            coordination_penalty = 0
        
        enhanced_spread = base_spread - fry_enhancement + inventory_penalty + coordination_penalty
        enhanced_spread = max(0.0012, enhanced_spread)
        
        bid_price = price * (1 - enhanced_spread / 2)
        ask_price = price * (1 + enhanced_spread / 2)
        
        # Execute trades
        fill_prob = min(0.4, market_data.get('volume', 0) / 2000000) * allocation_factor
        trades_executed = 0
        
        # Buy orders
        if (random.random() < fill_prob and 
            self.assets[asset]['fry_inventory'] < config['max_inventory'] and
            quote_size * bid_price < effective_capital * 0.25):
            
            cost = quote_size * bid_price
            self.assets[asset]['fry_inventory'] += quote_size
            self.fry_capital -= cost
            
            # Update average cost
            if self.assets[asset]['fry_inventory'] > 0:
                total_cost = (self.assets[asset]['fry_avg_cost'] * 
                            (self.assets[asset]['fry_inventory'] - quote_size) + cost)
                self.assets[asset]['fry_avg_cost'] = total_cost / self.assets[asset]['fry_inventory']
            
            self.assets[asset]['fry_trades'] += 1
            self.total_trades += 1
            self.total_churn += cost
            trades_executed += 1
        
        # Sell orders
        if (random.random() < fill_prob and 
            self.assets[asset]['fry_inventory'] > 0):
            
            sell_size = min(self.assets[asset]['fry_inventory'], quote_size)
            revenue = sell_size * ask_price
            
            self.assets[asset]['fry_inventory'] -= sell_size
            self.fry_capital += revenue
            self.total_churn += revenue
            
            # Calculate profit
            profit = (ask_price - self.assets[asset]['fry_avg_cost']) * sell_size
            self.assets[asset]['fry_profits'] += profit
            self.total_profits += profit
            
            trades_executed += 1
        
        # FRY recycling
        if volatility > 0.04 and trades_executed > 0:
            self._capture_slippage(asset, market_data, trades_executed)
        
        return trades_executed
    
    def execute_traditional_strategy(self, asset, market_data, allocation_factor):
        """Execute traditional market making strategy"""
        
        config = self.traditional_config[asset]
        price = market_data['price']
        volatility = market_data.get('volatility', 0.05)
        
        # Conservative approach with allocation adjustment
        effective_capital = self.traditional_capital * allocation_factor
        quote_size = config['quote_size'] * allocation_factor * random.uniform(0.6, 0.9)
        
        # Conservative spread calculation
        base_spread = config['spread']
        inventory_penalty = abs(self.assets[asset]['trad_inventory']) / config['max_inventory'] * 0.002
        volatility_adjustment = volatility * 1.8
        
        # Coordination adjustment
        if self.coordination['risk_sharing']:
            total_risk = (abs(self.assets[asset]['fry_inventory']) + 
                         abs(self.assets[asset]['trad_inventory']))
            risk_adjustment = total_risk / (config['max_inventory'] * 2) * 0.0008
        else:
            risk_adjustment = 0
        
        total_spread = base_spread + inventory_penalty + volatility_adjustment + risk_adjustment
        
        bid_price = price * (1 - total_spread / 2)
        ask_price = price * (1 + total_spread / 2)
        
        # Conservative execution
        fill_prob = min(0.22, market_data.get('volume', 0) / 3500000) * allocation_factor
        trades_executed = 0
        
        # Buy orders
        if (random.random() < fill_prob and 
            self.assets[asset]['trad_inventory'] < config['max_inventory']):
            
            cost = quote_size * bid_price
            if cost < effective_capital * 0.18:
                self.assets[asset]['trad_inventory'] += quote_size
                self.traditional_capital -= cost
                
                if self.assets[asset]['trad_inventory'] > 0:
                    total_cost = (self.assets[asset]['trad_avg_cost'] * 
                                (self.assets[asset]['trad_inventory'] - quote_size) + cost)
                    self.assets[asset]['trad_avg_cost'] = total_cost / self.assets[asset]['trad_inventory']
                
                self.assets[asset]['trad_trades'] += 1
                self.total_trades += 1
                self.total_churn += cost
                trades_executed += 1
        
        # Sell orders
        if (random.random() < fill_prob and 
            self.assets[asset]['trad_inventory'] > 0):
            
            sell_size = min(self.assets[asset]['trad_inventory'], quote_size)
            revenue = sell_size * ask_price
            
            self.assets[asset]['trad_inventory'] -= sell_size
            self.traditional_capital += revenue
            self.total_churn += revenue
            
            # Conservative profit calculation
            profit = (ask_price - self.assets[asset]['trad_avg_cost']) * sell_size
            self.assets[asset]['trad_profits'] += profit
            self.total_profits += profit
            trades_executed += 1
        
        return trades_executed
    
    def _capture_slippage(self, asset, market_data, trades_executed):
        """Enhanced slippage capture for hybrid approach"""
        
        volume = market_data.get('volume', 0)
        volatility = market_data.get('volatility', 0.05)
        
        # Slippage estimation
        base_slippage = volatility * 0.4
        volume_slippage = volume / 6000000 * 0.0025
        total_slippage = base_slippage + volume_slippage
        
        if total_slippage >= 0.0018:
            # Enhanced recycling rate for hybrid approach
            recycled_amount = total_slippage * 0.65 * trades_executed * random.uniform(0.9, 1.4)
            
            self.fry_balance += recycled_amount
            self.recycled_value += recycled_amount
            self.slippage_captured += total_slippage
    
    def rebalance_strategies(self):
        """Rebalance capital between strategies based on performance"""
        
        if not self.coordination['profit_rebalancing']:
            return
        
        # Calculate strategy performance
        fry_total_profits = sum(asset['fry_profits'] for asset in self.assets.values())
        trad_total_profits = sum(asset['trad_profits'] for asset in self.assets.values())
        
        fry_trades = sum(asset['fry_trades'] for asset in self.assets.values())
        trad_trades = sum(asset['trad_trades'] for asset in self.assets.values())
        
        if fry_trades > 0 and trad_trades > 0:
            fry_profit_per_trade = fry_total_profits / fry_trades
            trad_profit_per_trade = trad_total_profits / trad_trades
            
            performance_diff = fry_profit_per_trade - trad_profit_per_trade
            
            # Rebalance if performance difference exceeds threshold
            if abs(performance_diff) > self.coordination['strategy_switching_threshold']:
                rebalance_amount = min(50000, abs(performance_diff) * 10000)
                
                if performance_diff > 0:  # FRY performing better
                    transfer = min(rebalance_amount, self.traditional_capital * 0.1)
                    self.fry_capital += transfer
                    self.traditional_capital -= transfer
                else:  # Traditional performing better
                    transfer = min(rebalance_amount, self.fry_capital * 0.1)
                    self.traditional_capital += transfer
                    self.fry_capital -= transfer
    
    def execute_hybrid_trade(self, asset, market_data, timestamp):
        """Execute coordinated hybrid trading strategy"""
        
        # Analyze market regime
        regime_analysis = self.analyze_market_regime(asset, market_data)
        
        # Execute both strategies with dynamic allocation
        fry_trades = self.execute_fry_strategy(
            asset, market_data, regime_analysis['fry_allocation'], timestamp)
        
        traditional_trades = self.execute_traditional_strategy(
            asset, market_data, regime_analysis['traditional_allocation'])
        
        return fry_trades + traditional_trades
    
    def get_metrics(self):
        """Get comprehensive hybrid performance metrics"""
        
        # Calculate inventory values
        inventory_values = {}
        total_inventory_value = 0
        
        price_estimates = {'SOL': 100, 'AVAX': 25, 'MATIC': 0.8, 'ATOM': 12}
        
        for asset in self.assets:
            fry_value = self.assets[asset]['fry_inventory'] * price_estimates[asset]
            trad_value = self.assets[asset]['trad_inventory'] * price_estimates[asset]
            inventory_values[asset] = {
                'fry_value': fry_value,
                'trad_value': trad_value,
                'total_value': fry_value + trad_value
            }
            total_inventory_value += fry_value + trad_value
        
        total_capital = self.fry_capital + self.traditional_capital + total_inventory_value
        
        # Strategy breakdown
        fry_profits = sum(asset['fry_profits'] for asset in self.assets.values())
        trad_profits = sum(asset['trad_profits'] for asset in self.assets.values())
        fry_trades = sum(asset['fry_trades'] for asset in self.assets.values())
        trad_trades = sum(asset['trad_trades'] for asset in self.assets.values())
        
        return {
            'agent_type': 'Hybrid_MidCap_Agent',
            'total_capital': total_capital,
            'total_return': (total_capital - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'fry_profits': fry_profits,
            'traditional_profits': trad_profits,
            'fry_balance': self.fry_balance,
            'recycled_value': self.recycled_value,
            'slippage_captured': self.slippage_captured,
            'total_trades': self.total_trades,
            'fry_trades': fry_trades,
            'traditional_trades': trad_trades,
            'total_churn': self.total_churn,
            'inventory_value': total_inventory_value,
            'inventory_breakdown': inventory_values,
            'asset_breakdown': self.assets,
            'capital_allocation': {
                'fry_capital': self.fry_capital,
                'traditional_capital': self.traditional_capital,
                'fry_percentage': self.fry_capital / (self.fry_capital + self.traditional_capital) * 100
            }
        }

def generate_midcap_market_data(asset, base_price, volatility_multiplier=1.0):
    """Generate realistic mid-cap market data with recent returns"""
    
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
    
    # Recent returns for trend analysis
    recent_returns = [np.random.normal(0, volatility) for _ in range(5)]
    
    return {
        'asset': asset,
        'price': new_price,
        'volume': volume,
        'volatility': volatility,
        'social_sentiment': social_sentiment,
        'large_orders_ratio': large_orders_ratio,
        'recent_returns': recent_returns,
        'timestamp': time.time()
    }

def run_hybrid_comparison(duration_minutes=120):
    """Run hybrid agent vs individual strategies comparison"""
    
    print("🔄 Hybrid Mid-Cap Agent Simulation")
    print("=" * 60)
    
    # Initialize agents
    hybrid_agent = HybridMidCapAgent(500000)
    
    # For comparison, create individual agents
    from midcap_agent_b_simulation import MidCapAgentB, TraditionalMidCapMM
    agent_b = MidCapAgentB(500000)
    traditional_mm = TraditionalMidCapMM(500000)
    
    # Asset prices
    asset_prices = {'SOL': 100, 'AVAX': 25, 'MATIC': 0.8, 'ATOM': 12}
    
    print("Hybrid Agent: FRY + Traditional MM Coordination")
    print("Comparison: Individual Agent B vs Traditional MM")
    print("Assets: SOL, AVAX, MATIC, ATOM")
    print("Duration: {} minutes\n".format(duration_minutes))
    
    for minute in range(duration_minutes):
        timestamp = time.time()
        
        # Trade each asset
        for asset in ['SOL', 'AVAX', 'MATIC', 'ATOM']:
            # Generate market data
            market_data = generate_midcap_market_data(asset, asset_prices[asset])
            asset_prices[asset] = market_data['price']
            
            # Hybrid agent trading
            hybrid_agent.execute_hybrid_trade(asset, market_data, timestamp)
            
            # Individual agents for comparison
            analysis = agent_b.analyze_market_data(asset, market_data)
            agent_b.execute_fry_enhanced_trade(asset, analysis, timestamp)
            traditional_mm.execute_traditional_trade(asset, market_data)
        
        # Rebalance hybrid strategy every 30 minutes
        if minute % 30 == 0:
            hybrid_agent.rebalance_strategies()
            
            # Progress updates
            hybrid_metrics = hybrid_agent.get_metrics()
            agent_b_metrics = agent_b.get_metrics()
            traditional_metrics = traditional_mm.get_metrics()
            
            print("Min {}: Hybrid={:.2f}% (FRY:{:.1f}%/{:.3f}) | Agent B={:.2f}% | Traditional={:.2f}%".format(
                minute,
                hybrid_metrics['total_return'] * 100,
                hybrid_metrics['capital_allocation']['fry_percentage'],
                hybrid_metrics['fry_balance'],
                agent_b_metrics['total_return'] * 100,
                traditional_metrics['total_return'] * 100
            ))
    
    # Final results
    print("\n📊 Final Results:")
    print("=" * 60)
    
    final_hybrid = hybrid_agent.get_metrics()
    final_agent_b = agent_b.get_metrics()
    final_traditional = traditional_mm.get_metrics()
    
    print("\n🤝 Hybrid Agent (FRY + Traditional):")
    print("Return: {:.2f}%".format(final_hybrid['total_return'] * 100))
    print("Total Profits: ${:,.2f}".format(final_hybrid['total_profits']))
    print("  - FRY Profits: ${:,.2f}".format(final_hybrid['fry_profits']))
    print("  - Traditional Profits: ${:,.2f}".format(final_hybrid['traditional_profits']))
    print("FRY Balance: {:.4f} tokens".format(final_hybrid['fry_balance']))
    print("Total Trades: {} (FRY: {}, Traditional: {})".format(
        final_hybrid['total_trades'], final_hybrid['fry_trades'], final_hybrid['traditional_trades']))
    print("Capital Allocation: {:.1f}% FRY / {:.1f}% Traditional".format(
        final_hybrid['capital_allocation']['fry_percentage'],
        100 - final_hybrid['capital_allocation']['fry_percentage']))
    print("Churn: ${:,.2f}".format(final_hybrid['total_churn']))
    
    print("\n🚀 Agent B (Individual):")
    print("Return: {:.2f}%".format(final_agent_b['total_return'] * 100))
    print("Profits: ${:,.2f}".format(final_agent_b['total_profits']))
    print("Trades: {}".format(final_agent_b['total_trades']))
    
    print("\n🏦 Traditional MM (Individual):")
    print("Return: {:.2f}%".format(final_traditional['total_return'] * 100))
    print("Profits: ${:,.2f}".format(final_traditional['total_profits']))
    print("Trades: {}".format(final_traditional['total_trades']))
    
    # Comparative analysis
    print("\n📈 Comparative Analysis:")
    hybrid_vs_agent_b = final_hybrid['total_return'] - final_agent_b['total_return']
    hybrid_vs_traditional = final_hybrid['total_return'] - final_traditional['total_return']
    
    print("Hybrid vs Agent B: {:.2f}% ({})".format(
        hybrid_vs_agent_b * 100, "Hybrid Wins" if hybrid_vs_agent_b > 0 else "Agent B Wins"))
    print("Hybrid vs Traditional: {:.2f}% ({})".format(
        hybrid_vs_traditional * 100, "Hybrid Wins" if hybrid_vs_traditional > 0 else "Traditional Wins"))
    
    # Strategy effectiveness
    if final_hybrid['fry_trades'] > 0 and final_hybrid['traditional_trades'] > 0:
        fry_efficiency = final_hybrid['fry_profits'] / final_hybrid['fry_trades']
        trad_efficiency = final_hybrid['traditional_profits'] / final_hybrid['traditional_trades']
        
        print("FRY Strategy Efficiency: ${:.2f} per trade".format(fry_efficiency))
        print("Traditional Strategy Efficiency: ${:.2f} per trade".format(trad_efficiency))
        print("Better Strategy: {}".format("FRY" if fry_efficiency > trad_efficiency else "Traditional"))
    
    # Save results
    results = {
        'hybrid_final': final_hybrid,
        'agent_b_final': final_agent_b,
        'traditional_final': final_traditional,
        'comparison': {
            'hybrid_vs_agent_b_pct': hybrid_vs_agent_b * 100,
            'hybrid_vs_traditional_pct': hybrid_vs_traditional * 100,
            'best_performer': 'Hybrid' if max(final_hybrid['total_return'], 
                                            final_agent_b['total_return'], 
                                            final_traditional['total_return']) == final_hybrid['total_return'] else 'Other'
        }
    }
    
    results_file = "hybrid_midcap_comparison_{}.json".format(int(time.time()))
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved: {}".format(results_file))
    return results

if __name__ == "__main__":
    run_hybrid_comparison(120)
