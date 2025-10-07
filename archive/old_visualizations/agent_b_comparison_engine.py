#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent B vs Traditional MM Comparison Engine
==========================================

Comprehensive A/B testing framework comparing Agent B (FRY-enhanced) 
against Traditional Market Makers across multiple metrics and scenarios.
"""

import json
import time
import random
import logging
import numpy as np
from datetime import datetime
from collections import defaultdict

from agent_b_core import AgentB

logger = logging.getLogger(__name__)

class TraditionalMarketMaker:
    """
    Traditional Market Maker for comparison against Agent B
    """
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.total_profits = 0.0
        self.total_trades = 0
        self.total_volume = 0.0
        self.win_rate = 0.0
        
        # Traditional MM configuration
        self.config = {
            'base_spread': 0.002,           # 0.2% base spread
            'max_inventory_pct': 0.15,      # 15% max inventory per asset
            'risk_adjustment': 1.5,         # Conservative risk multiplier
            'min_trade_size': 1000,         # $1k minimum trade
            'max_trade_size': 50000         # $50k maximum trade
        }
    
    def calculate_spread(self, asset, market_data, inventory):
        """Calculate traditional market making spread"""
        
        volatility = market_data.get('volatility', 0.05)
        volume = market_data.get('volume', 1000000)
        
        # Base spread
        base_spread = self.config['base_spread']
        
        # Volatility adjustment (conservative)
        vol_adjustment = volatility * self.config['risk_adjustment']
        
        # Inventory skew
        max_inventory = self.current_capital * self.config['max_inventory_pct']
        inventory_skew = (inventory / max_inventory) * 0.001 if max_inventory > 0 else 0
        
        # Volume adjustment (wider spreads in low volume)
        volume_adjustment = max(0, (2000000 - volume) / 10000000)
        
        total_spread = base_spread + vol_adjustment + abs(inventory_skew) + volume_adjustment
        return max(0.001, total_spread)  # Minimum 0.1% spread
    
    def execute_traditional_mm(self, asset, market_data, timestamp):
        """Execute traditional market making strategy"""
        
        price = market_data['price']
        volume = market_data.get('volume', 1000000)
        
        # Get current inventory
        current_inventory = self.positions.get(asset, {}).get('inventory', 0)
        inventory_value = current_inventory * price
        
        # Calculate spread
        spread = self.calculate_spread(asset, market_data, inventory_value)
        
        bid_price = price * (1 - spread / 2)
        ask_price = price * (1 + spread / 2)
        
        # Determine trade size based on volume
        base_trade_size = min(
            self.config['max_trade_size'],
            max(self.config['min_trade_size'], volume / 100)
        )
        
        # Conservative position sizing
        max_position_value = self.current_capital * self.config['max_inventory_pct']
        
        trades_executed = 0
        
        # Buy side (if not over-inventoried)
        if abs(inventory_value) < max_position_value and random.random() < 0.3:
            trade_size = min(base_trade_size, max_position_value - abs(inventory_value))
            cost = trade_size
            
            if cost < self.current_capital * 0.1:  # Conservative capital usage
                # Execute buy
                if asset not in self.positions:
                    self.positions[asset] = {'inventory': 0, 'avg_cost': 0}
                
                old_inventory = self.positions[asset]['inventory']
                old_value = old_inventory * self.positions[asset]['avg_cost']
                
                self.positions[asset]['inventory'] += trade_size / price
                new_inventory = self.positions[asset]['inventory']
                
                if new_inventory > 0:
                    self.positions[asset]['avg_cost'] = (old_value + cost) / new_inventory
                
                self.current_capital -= cost
                self.total_volume += cost
                trades_executed += 1
        
        # Sell side (if have inventory)
        if asset in self.positions and self.positions[asset]['inventory'] > 0 and random.random() < 0.3:
            available_inventory = self.positions[asset]['inventory']
            trade_size_coins = min(available_inventory, base_trade_size / price)
            
            if trade_size_coins > 0:
                # Execute sell
                revenue = trade_size_coins * ask_price
                cost_basis = trade_size_coins * self.positions[asset]['avg_cost']
                profit = revenue - cost_basis
                
                self.positions[asset]['inventory'] -= trade_size_coins
                self.current_capital += revenue
                self.total_profits += profit
                self.total_volume += revenue
                trades_executed += 1
                
                # Update win rate
                wins = 1 if profit > 0 else 0
                self.win_rate = (self.win_rate * self.total_trades + wins) / (self.total_trades + 1)
        
        self.total_trades += trades_executed
        return trades_executed
    
    def get_metrics(self):
        """Get traditional MM performance metrics"""
        
        # Calculate total portfolio value
        total_inventory_value = sum(
            pos['inventory'] * 100 for pos in self.positions.values()  # Approximate pricing
        )
        total_capital = self.current_capital + total_inventory_value
        
        return {
            'agent_type': 'Traditional_MM',
            'total_capital': total_capital,
            'total_return_pct': ((total_capital - self.initial_capital) / self.initial_capital) * 100,
            'total_profits': self.total_profits,
            'total_trades': self.total_trades,
            'total_volume': self.total_volume,
            'win_rate': self.win_rate,
            'inventory_value': total_inventory_value,
            'cash_position': self.current_capital,
            'active_positions': len([p for p in self.positions.values() if p['inventory'] > 0]),
            'performance_components': {
                'spread_capture': self.total_profits,
                'inventory_gains': total_inventory_value - sum(
                    pos['inventory'] * pos['avg_cost'] for pos in self.positions.values()
                ),
                'capital_efficiency': self.total_profits / self.initial_capital if self.initial_capital > 0 else 0
            }
        }

class AgentBComparisonEngine:
    """
    Comprehensive comparison engine for Agent B vs Traditional MM
    """
    
    def __init__(self):
        self.comparison_results = []
        self.scenario_results = {}
    
    def generate_market_scenario(self, scenario_type='normal', duration_minutes=120):
        """Generate different market scenarios for testing"""
        
        scenarios = {
            'normal': {
                'volatility_range': (0.03, 0.06),
                'volume_range': (1000000, 3000000),
                'trend_strength': 0.3,
                'retail_activity': 0.5
            },
            'high_volatility': {
                'volatility_range': (0.08, 0.15),
                'volume_range': (2000000, 5000000),
                'trend_strength': 0.6,
                'retail_activity': 0.8
            },
            'low_liquidity': {
                'volatility_range': (0.04, 0.08),
                'volume_range': (200000, 800000),
                'trend_strength': 0.2,
                'retail_activity': 0.3
            },
            'trending_market': {
                'volatility_range': (0.05, 0.09),
                'volume_range': (1500000, 4000000),
                'trend_strength': 0.8,
                'retail_activity': 0.7
            },
            'choppy_market': {
                'volatility_range': (0.06, 0.12),
                'volume_range': (800000, 2000000),
                'trend_strength': 0.1,
                'retail_activity': 0.6
            }
        }
        
        config = scenarios.get(scenario_type, scenarios['normal'])
        market_data_series = []
        
        # Asset configuration
        assets = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC']
        base_prices = {'BTC': 45000, 'ETH': 2800, 'SOL': 100, 'AVAX': 25, 'MATIC': 0.8}
        
        for minute in range(duration_minutes):
            minute_data = {}
            
            for asset in assets:
                # Generate market conditions
                volatility = random.uniform(*config['volatility_range'])
                volume = random.uniform(*config['volume_range'])
                
                # Price movement with trend
                trend_component = np.random.normal(0, config['trend_strength'] * 0.001)
                random_component = np.random.normal(0, volatility / 100)
                price_change = trend_component + random_component
                
                base_prices[asset] *= (1 + price_change)
                
                minute_data[asset] = {
                    'asset': asset,
                    'price': base_prices[asset],
                    'volume': volume,
                    'volatility': volatility,
                    'social_sentiment': random.uniform(0.3, 0.9),
                    'liquidity_depth': volume * random.uniform(0.8, 1.5),
                    'bid_ask_spread': random.uniform(0.001, 0.005),
                    'order_book_depth': volume * random.uniform(0.5, 1.2),
                    'estimated_trade_size': random.uniform(5000, 75000),
                    'large_orders_ratio': random.uniform(0.02, 0.15),
                    'retail_activity_score': config['retail_activity'] * random.uniform(0.7, 1.3)
                }
            
            market_data_series.append(minute_data)
        
        return market_data_series
    
    def run_comparison(self, scenario_type='normal', duration_minutes=120, iterations=1):
        """Run comprehensive Agent B vs Traditional MM comparison"""
        
        print("Running Agent B vs Traditional MM Comparison")
        print("Scenario: {}".format(scenario_type.upper()))
        print("Duration: {} minutes".format(duration_minutes))
        print("Iterations: {}".format(iterations))
        print("=" * 60)
        
        iteration_results = []
        
        for iteration in range(iterations):
{{ ... }}
            print(f"\n📊 Iteration {iteration + 1}/{iterations}")
            
            # Initialize agents
            agent_b = AgentB(1000000)
            traditional_mm = TraditionalMarketMaker(1000000)
            
            # Generate market scenario
            market_data_series = self.generate_market_scenario(scenario_type, duration_minutes)
            
            # Run simulation
            for minute, minute_data in enumerate(market_data_series):
                timestamp = time.time() + minute * 60
                
                for asset, market_data in minute_data.items():
                    # Generate funding rates for Agent B
                    funding_rates = {
                        'binance': random.uniform(-0.005, 0.015),
                        'okx': random.uniform(-0.007, 0.012),
                        'bybit': random.uniform(-0.006, 0.014),
                        'kucoin': random.uniform(-0.008, 0.016)
                    }
                    
                    # Agent B execution
                    opportunities = agent_b.analyze_market_opportunity(market_data, funding_rates)
                    agent_b.execute_agent_b_strategy(opportunities)
                    
                    # Traditional MM execution
                    traditional_mm.execute_traditional_mm(asset, market_data, timestamp)
                
                # Progress update
                if minute % 30 == 0 and minute > 0:
                    agent_b_metrics = agent_b.get_agent_b_metrics()
                    traditional_metrics = traditional_mm.get_metrics()
                    
                    print(f"  Min {minute}: Agent B={agent_b_metrics['total_return_pct']:.2f}% | "
                          f"Traditional={traditional_metrics['total_return_pct']:.2f}%")
            
            # Collect final results
            final_agent_b = agent_b.get_agent_b_metrics()
            final_traditional = traditional_mm.get_metrics()
            
            iteration_result = {
                'iteration': iteration + 1,
                'scenario': scenario_type,
                'duration_minutes': duration_minutes,
                'agent_b_results': final_agent_b,
                'traditional_results': final_traditional,
                'comparison_metrics': self._calculate_comparison_metrics(final_agent_b, final_traditional)
            }
            
            iteration_results.append(iteration_result)
        
        # Aggregate results across iterations
        aggregated_results = self._aggregate_iteration_results(iteration_results, scenario_type)
        
        # Display results
        self._display_comparison_results(aggregated_results)
        
        return aggregated_results
    
    def _calculate_comparison_metrics(self, agent_b_results, traditional_results):
        """Calculate detailed comparison metrics"""
        
        return_diff = agent_b_results['total_return_pct'] - traditional_results['total_return_pct']
        profit_diff = agent_b_results['total_profits'] - traditional_results['total_profits']
        
        # Risk-adjusted returns (Sharpe-like ratio)
        agent_b_sharpe = agent_b_results['total_return_pct'] / max(1, agent_b_results.get('volatility', 5))
        traditional_sharpe = traditional_results['total_return_pct'] / max(1, traditional_results.get('volatility', 5))
        
        # Capital efficiency
        agent_b_efficiency = agent_b_results['total_profits'] / agent_b_results.get('total_capital', 1000000)
        traditional_efficiency = traditional_results['total_profits'] / traditional_results.get('total_capital', 1000000)
        
        return {
            'return_difference_pct': return_diff,
            'profit_difference_usd': profit_diff,
            'agent_b_advantage_pct': (return_diff / max(0.01, abs(traditional_results['total_return_pct']))) * 100,
            'winner': 'Agent_B' if return_diff > 0 else 'Traditional_MM',
            'performance_metrics': {
                'agent_b_sharpe': agent_b_sharpe,
                'traditional_sharpe': traditional_sharpe,
                'agent_b_efficiency': agent_b_efficiency,
                'traditional_efficiency': traditional_efficiency,
                'efficiency_advantage': agent_b_efficiency - traditional_efficiency
            },
            'fry_specific_metrics': {
                'fry_minted': agent_b_results.get('total_fry_minted', 0),
                'fry_value_usd': agent_b_results.get('fry_value_usd', 0),
                'slippage_harvested': agent_b_results.get('slippage_harvested', 0),
                'losses_recycled': agent_b_results.get('losses_recycled', 0),
                'fry_enhancement_ratio': agent_b_results.get('fry_value_usd', 0) / max(1, agent_b_results['total_profits'])
            }
        }
    
    def _aggregate_iteration_results(self, iteration_results, scenario_type):
        """Aggregate results across multiple iterations"""
        
        if not iteration_results:
            return {}
        
        # Calculate averages
        avg_agent_b_return = np.mean([r['agent_b_results']['total_return_pct'] for r in iteration_results])
        avg_traditional_return = np.mean([r['traditional_results']['total_return_pct'] for r in iteration_results])
        avg_return_diff = np.mean([r['comparison_metrics']['return_difference_pct'] for r in iteration_results])
        
        # Calculate win rates
        agent_b_wins = sum(1 for r in iteration_results if r['comparison_metrics']['winner'] == 'Agent_B')
        win_rate = agent_b_wins / len(iteration_results)
        
        # FRY metrics
        avg_fry_minted = np.mean([r['agent_b_results'].get('total_fry_minted', 0) for r in iteration_results])
        avg_fry_value = np.mean([r['agent_b_results'].get('fry_value_usd', 0) for r in iteration_results])
        
        return {
            'scenario_type': scenario_type,
            'total_iterations': len(iteration_results),
            'summary_metrics': {
                'agent_b_avg_return_pct': avg_agent_b_return,
                'traditional_avg_return_pct': avg_traditional_return,
                'avg_return_difference_pct': avg_return_diff,
                'agent_b_win_rate': win_rate,
                'avg_fry_minted': avg_fry_minted,
                'avg_fry_value_usd': avg_fry_value
            },
            'detailed_results': iteration_results
        }
    
    def _display_comparison_results(self, results):
        """Display comprehensive comparison results"""
        
        print(f"\n🏆 FINAL RESULTS - {results['scenario_type'].upper()} SCENARIO")
        print("=" * 60)
        
        summary = results['summary_metrics']
        
        print(f"Agent B Win Rate: {summary['agent_b_win_rate']:.1%}")
        print(f"Average Return Difference: {summary['avg_return_difference_pct']:+.2f}%")
        
        print(f"\n📈 Performance Summary:")
        print(f"  Agent B Average Return: {summary['agent_b_avg_return_pct']:.2f}%")
        print(f"  Traditional MM Average Return: {summary['traditional_avg_return_pct']:.2f}%")
        
        print(f"\n🪙 FRY Enhancement:")
        print(f"  Average FRY Minted: {summary['avg_fry_minted']:.2f} tokens")
        print(f"  Average FRY Value: ${summary['avg_fry_value_usd']:,.2f}")
        
        # Determine overall winner
        if summary['agent_b_win_rate'] > 0.6:
            print(f"\n🎯 CONCLUSION: Agent B shows clear superiority in {results['scenario_type']} conditions")
        elif summary['agent_b_win_rate'] > 0.4:
            print(f"\n⚖️ CONCLUSION: Competitive performance between strategies in {results['scenario_type']} conditions")
        else:
            print(f"\n🏦 CONCLUSION: Traditional MM performs better in {results['scenario_type']} conditions")

def run_comprehensive_agent_b_study():
    """Run comprehensive Agent B study across multiple scenarios"""
    
    print("🚀 COMPREHENSIVE AGENT B STUDY")
    print("=" * 80)
    print("Testing Agent B across multiple market scenarios")
    print("Comparing against Traditional Market Making strategies\n")
    
    comparison_engine = AgentBComparisonEngine()
    
    # Test scenarios
    scenarios = [
        ('normal', 90),
        ('high_volatility', 60),
        ('low_liquidity', 120),
        ('trending_market', 90),
        ('choppy_market', 90)
    ]
    
    all_results = {}
    
    for scenario_type, duration in scenarios:
        print(f"\n{'='*20} {scenario_type.upper()} SCENARIO {'='*20}")
        
        results = comparison_engine.run_comparison(
            scenario_type=scenario_type,
            duration_minutes=duration,
            iterations=3
        )
        
        all_results[scenario_type] = results
    
    # Cross-scenario analysis
    print(f"\n{'='*80}")
    print("🔬 CROSS-SCENARIO ANALYSIS")
    print("="*80)
    
    scenario_wins = {}
    for scenario, results in all_results.items():
        win_rate = results['summary_metrics']['agent_b_win_rate']
        scenario_wins[scenario] = win_rate
        print(f"{scenario.replace('_', ' ').title()}: Agent B wins {win_rate:.1%} of the time")
    
    # Overall assessment
    overall_win_rate = np.mean(list(scenario_wins.values()))
    print(f"\n🎯 OVERALL AGENT B WIN RATE: {overall_win_rate:.1%}")
    
    if overall_win_rate > 0.7:
        print("🏆 Agent B demonstrates STRONG superiority across market conditions")
    elif overall_win_rate > 0.5:
        print("✅ Agent B shows CONSISTENT advantage over traditional MM")
    else:
        print("⚠️ Agent B performance is MIXED - scenario-dependent advantages")
    
    # Best/worst scenarios for Agent B
    best_scenario = max(scenario_wins.items(), key=lambda x: x[1])
    worst_scenario = min(scenario_wins.items(), key=lambda x: x[1])
    
    print(f"\n📊 Agent B performs BEST in: {best_scenario[0].replace('_', ' ')} ({best_scenario[1]:.1%} win rate)")
    print(f"📊 Agent B performs WORST in: {worst_scenario[0].replace('_', ' ')} ({worst_scenario[1]:.1%} win rate)")
    
    # Export results
    export_data = {
        'study_timestamp': datetime.now().isoformat(),
        'study_type': 'comprehensive_agent_b_analysis',
        'overall_win_rate': overall_win_rate,
        'scenario_results': all_results,
        'key_findings': {
            'best_scenario': best_scenario[0],
            'worst_scenario': worst_scenario[0],
            'overall_assessment': 'superior' if overall_win_rate > 0.7 else 'competitive' if overall_win_rate > 0.5 else 'mixed'
        }
    }
    
    filename = f"agent_b_comprehensive_study_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n💾 Study results exported: {filename}")
    print("✅ Comprehensive Agent B study complete!")
    
    return all_results

if __name__ == "__main__":
    run_comprehensive_agent_b_study()
