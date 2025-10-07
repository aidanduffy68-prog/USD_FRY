#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRY Agent B vs Traditional Market Maker Simulation
=================================================

Comparative simulation between FRY Arbitrage Agent (Player B) and 
traditional market maker strategies in identical market conditions.

Features:
- Side-by-side performance comparison
- Identical market data feeds
- Risk-adjusted metrics
- FRY recycling impact analysis
- Detailed performance breakdown
"""

import json
import time
import random
import logging
import numpy as np
from datetime import datetime
from collections import deque, defaultdict

# Standalone components
class RektDarkCDO:
    def __init__(self):
        self.total_fry_minted = 0
        
    def sweep_collateral(self, *args, **kwargs):
        return "mock_id", 100.0

class V2SlippageEngine:
    def calculate_slippage(self, volume, depth, volatility):
        return max(0.001, volume / 10000000 * volatility)

class V2CircuitBreaker:
    def get_health_status(self):
        return {'status': 'healthy'}

class FRYArbitrageAgent:
    """FRY Agent B - Informed Arbitrageur"""
    
    def __init__(self, initial_capital=100000, agent_id="fry_agent"):
        self.agent_id = agent_id
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # FRY system integration
        self.fry_system = RektDarkCDO()
        self.slippage_engine = V2SlippageEngine()
        self.circuit_breaker = V2CircuitBreaker()
        
        # Agent state
        self.positions = {}
        self.fry_balance = 0.0
        self.recycled_value = 0.0
        self.total_profits = 0.0
        self.trades_executed = 0
        self.win_rate = 0.0
        
        # Configuration
        self.config = {
            'min_slippage_threshold': 0.002,
            'max_position_size': 0.05,
            'fry_recycling_rate': 0.35,
            'entry_confidence_threshold': 0.75,
            'exit_profit_target': 0.008,
            'stop_loss': 0.004,
            'max_concurrent_positions': 3,
        }
        
        self.logger = logging.getLogger("FRYAgent_{}".format(self.agent_id))
    
    def analyze_and_trade(self, market_snapshot):
        """Main trading logic"""
        
        # Detect slippage opportunities
        expected_slippage = self.slippage_engine.calculate_slippage(
            market_snapshot.get('volume', 0),
            market_snapshot.get('depth', {}),
            market_snapshot.get('volatility', 0.02)
        )
        
        # Detect Player A activity
        player_a_signals = self._detect_player_a_activity(market_snapshot)
        
        # Generate trading signal
        signal_strength = min(1.0, expected_slippage / 0.01)
        player_a_boost = sum(1 for signal in player_a_signals.values() if signal) * 0.15
        signal_strength += player_a_boost
        
        # Execute trades
        if signal_strength >= self.config['entry_confidence_threshold'] and len(self.positions) < self.config['max_concurrent_positions']:
            self._execute_trade(market_snapshot, signal_strength, expected_slippage)
        
        # Monitor existing positions
        self._monitor_positions(market_snapshot)
        
        # Update FRY recycling
        if expected_slippage >= self.config['min_slippage_threshold']:
            recycled_amount = expected_slippage * self.config['fry_recycling_rate'] * random.uniform(0.8, 1.2)
            self.fry_balance += recycled_amount
            self.recycled_value += recycled_amount
    
    def _detect_player_a_activity(self, market_snapshot):
        """Detect new entrant patterns"""
        signals = {
            'large_market_orders': market_snapshot.get('large_orders', 0) > 0.02,
            'momentum_chasing': len([r for r in market_snapshot.get('recent_returns', []) if r > 0.01]) >= 2,
            'social_media_correlation': market_snapshot.get('social_sentiment', 0.5) > 0.65,
            'volume_spike': market_snapshot.get('volume', 0) > 1500000
        }
        return signals
    
    def _execute_trade(self, market_snapshot, confidence, expected_slippage):
        """Execute a trade based on opportunity"""
        position_size = self.current_capital * self.config['max_position_size'] * confidence
        
        if position_size < 100:
            return
        
        position_id = "pos_{}".format(int(time.time() * 1000))
        entry_price = market_snapshot['price']
        
        position = {
            'id': position_id,
            'entry_time': time.time(),
            'entry_price': entry_price,
            'size': position_size,
            'stop_loss': entry_price * (1 - self.config['stop_loss']),
            'profit_target': entry_price * (1 + self.config['exit_profit_target']),
            'confidence': confidence
        }
        
        self.positions[position_id] = position
        self.current_capital -= position_size
        self.trades_executed += 1
    
    def _monitor_positions(self, market_snapshot):
        """Monitor and close positions"""
        current_price = market_snapshot['price']
        positions_to_close = []
        
        for pos_id, position in self.positions.items():
            if current_price >= position['profit_target']:
                profit = (current_price - position['entry_price']) * position['size'] / position['entry_price']
                self._close_position(pos_id, profit, 'profit_target')
                positions_to_close.append(pos_id)
            elif current_price <= position['stop_loss']:
                loss = (position['entry_price'] - current_price) * position['size'] / position['entry_price']
                self._close_position(pos_id, -loss, 'stop_loss')
                positions_to_close.append(pos_id)
        
        for pos_id in positions_to_close:
            del self.positions[pos_id]
    
    def _close_position(self, position_id, pnl, reason):
        """Close position and update metrics"""
        position = self.positions[position_id]
        self.current_capital += position['size'] + pnl
        self.total_profits += pnl
        
        # Update win rate
        if pnl > 0:
            self.win_rate = (self.win_rate * (self.trades_executed - 1) + 1) / self.trades_executed
        else:
            self.win_rate = (self.win_rate * (self.trades_executed - 1)) / self.trades_executed
    
    def get_metrics(self):
        """Get performance metrics"""
        return {
            'agent_type': 'FRY_Agent_B',
            'total_capital': self.current_capital,
            'total_return': (self.current_capital - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'fry_balance': self.fry_balance,
            'recycled_value': self.recycled_value,
            'trades_executed': self.trades_executed,
            'win_rate': self.win_rate,
            'active_positions': len(self.positions)
        }

class TraditionalMarketMaker:
    """Traditional Market Maker - Spread Capture Strategy"""
    
    def __init__(self, initial_capital=100000, agent_id="traditional_mm"):
        self.agent_id = agent_id
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Market maker state
        self.inventory = 0.0  # BTC inventory
        self.total_profits = 0.0
        self.trades_executed = 0
        self.win_rate = 0.0
        
        # Configuration
        self.config = {
            'spread_target': 0.002,      # 0.2% spread target
            'max_inventory': 10.0,       # Max 10 BTC inventory
            'inventory_penalty': 0.001,  # Penalty for holding inventory
            'quote_size': 0.1,          # Quote 0.1 BTC per side
            'risk_adjustment': 0.5,     # Risk adjustment factor
        }
        
        self.logger = logging.getLogger("TraditionalMM_{}".format(self.agent_id))
    
    def analyze_and_trade(self, market_snapshot):
        """Traditional market making logic"""
        
        current_price = market_snapshot['price']
        volatility = market_snapshot.get('volatility', 0.02)
        volume = market_snapshot.get('volume', 0)
        
        # Calculate dynamic spread based on volatility and inventory
        base_spread = self.config['spread_target']
        volatility_adjustment = volatility * 2  # Widen spread in volatile markets
        inventory_adjustment = abs(self.inventory) * self.config['inventory_penalty']
        
        dynamic_spread = base_spread + volatility_adjustment + inventory_adjustment
        
        # Set bid/ask prices
        bid_price = current_price * (1 - dynamic_spread / 2)
        ask_price = current_price * (1 + dynamic_spread / 2)
        
        # Simulate market making activity
        self._simulate_market_making(current_price, bid_price, ask_price, volume)
        
        # Apply inventory carrying costs
        self._apply_inventory_costs(current_price)
    
    def _simulate_market_making(self, current_price, bid_price, ask_price, volume):
        """Simulate market making fills"""
        
        # Probability of getting filled based on volume and spread
        fill_probability = min(0.3, volume / 5000000)  # Higher volume = more fills
        
        # Simulate bid fills (buying)
        if random.random() < fill_probability and self.inventory < self.config['max_inventory']:
            fill_size = self.config['quote_size'] * random.uniform(0.5, 1.0)
            cost = fill_size * bid_price
            
            if cost < self.current_capital * 0.1:  # Don't use more than 10% capital per trade
                self.inventory += fill_size
                self.current_capital -= cost
                self.trades_executed += 1
        
        # Simulate ask fills (selling)
        if random.random() < fill_probability and self.inventory > 0:
            fill_size = min(self.inventory, self.config['quote_size'] * random.uniform(0.5, 1.0))
            revenue = fill_size * ask_price
            
            self.inventory -= fill_size
            self.current_capital += revenue
            
            # Calculate profit from this round trip
            avg_cost = current_price  # Simplified average cost
            profit = (ask_price - avg_cost) * fill_size
            self.total_profits += profit
            
            # Update win rate (market makers generally have high win rates)
            self.win_rate = (self.win_rate * (self.trades_executed - 1) + 0.8) / self.trades_executed
    
    def _apply_inventory_costs(self, current_price):
        """Apply carrying costs for inventory"""
        if self.inventory != 0:
            # Small cost for holding inventory (funding, risk)
            inventory_cost = abs(self.inventory) * current_price * 0.0001  # 0.01% per period
            self.current_capital -= inventory_cost
            self.total_profits -= inventory_cost
    
    def get_metrics(self):
        """Get performance metrics"""
        # Add inventory value to total capital
        inventory_value = self.inventory * 50000  # Assume $50k BTC price for valuation
        total_capital_with_inventory = self.current_capital + inventory_value
        
        return {
            'agent_type': 'Traditional_MM',
            'total_capital': total_capital_with_inventory,
            'total_return': (total_capital_with_inventory - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'inventory': self.inventory,
            'inventory_value': inventory_value,
            'trades_executed': self.trades_executed,
            'win_rate': self.win_rate,
            'cash_capital': self.current_capital
        }

class MarketSimulator:
    """Market data simulator for both agents"""
    
    def __init__(self):
        self.base_price = 50000
        self.time_step = 0
    
    def generate_market_snapshot(self, volatility=0.025):
        """Generate realistic market data"""
        
        # Price movement
        price_change = np.random.normal(0, volatility)
        self.base_price *= (1 + price_change)
        
        # Generate market conditions
        volume = random.uniform(800000, 3000000)
        social_sentiment = random.uniform(0.3, 0.9)
        large_orders = random.uniform(0, 0.08)
        
        # Recent returns for momentum detection
        recent_returns = [random.uniform(-0.03, 0.03) for _ in range(5)]
        
        snapshot = {
            'timestamp': time.time(),
            'price': self.base_price,
            'volume': volume,
            'volatility': volatility,
            'spread': random.uniform(0.0005, 0.002),
            'social_sentiment': social_sentiment,
            'large_orders': large_orders,
            'recent_returns': recent_returns,
            'depth': {'bids': random.uniform(1000, 5000), 'asks': random.uniform(1000, 5000)},
            'volume_spike': volume > 2000000
        }
        
        self.time_step += 1
        return snapshot

def run_comparative_simulation(duration_minutes=60, market_volatility=0.025):
    """Run side-by-side comparison simulation"""
    
    print("🔄 Initializing Comparative Simulation...")
    print("=" * 70)
    
    # Initialize agents with same capital
    initial_capital = 100000
    fry_agent = FRYArbitrageAgent(initial_capital, "fry_agent_comparison")
    traditional_mm = TraditionalMarketMaker(initial_capital, "traditional_mm_comparison")
    market_sim = MarketSimulator()
    
    print("FRY Agent B vs Traditional Market Maker")
    print("Initial Capital: ${:,.2f} each".format(initial_capital))
    print("Simulation Duration: {} minutes".format(duration_minutes))
    print("Market Volatility: {:.1f}%".format(market_volatility * 100))
    print()
    
    # Track performance over time
    performance_history = []
    
    print("🚀 Running simulation...")
    
    for minute in range(duration_minutes):
        # Generate identical market data for both agents
        market_snapshot = market_sim.generate_market_snapshot(market_volatility)
        
        # Both agents trade on same market data
        fry_agent.analyze_and_trade(market_snapshot)
        traditional_mm.analyze_and_trade(market_snapshot)
        
        # Record performance every 10 minutes
        if minute % 10 == 0:
            fry_metrics = fry_agent.get_metrics()
            mm_metrics = traditional_mm.get_metrics()
            
            performance_history.append({
                'minute': minute,
                'fry_capital': fry_metrics['total_capital'],
                'fry_return': fry_metrics['total_return'],
                'mm_capital': mm_metrics['total_capital'],
                'mm_return': mm_metrics['total_return'],
                'market_price': market_snapshot['price']
            })
            
            print("Minute {}: FRY={:.1f}% | MM={:.1f}% | Price=${:,.0f}".format(
                minute, 
                fry_metrics['total_return'] * 100,
                mm_metrics['total_return'] * 100,
                market_snapshot['price']
            ))
        
        time.sleep(0.01)  # Small delay for realism
    
    # Final results
    print("\n📊 Final Results:")
    print("=" * 70)
    
    final_fry = fry_agent.get_metrics()
    final_mm = traditional_mm.get_metrics()
    
    print("\n🤖 FRY Agent B (Player B Strategy):")
    print("Final Capital: ${:,.2f}".format(final_fry['total_capital']))
    print("Total Return: {:.2f}%".format(final_fry['total_return'] * 100))
    print("Total Profits: ${:,.2f}".format(final_fry['total_profits']))
    print("FRY Balance: {:.4f} tokens".format(final_fry['fry_balance']))
    print("Recycled Value: ${:.2f}".format(final_fry['recycled_value']))
    print("Trades Executed: {}".format(final_fry['trades_executed']))
    print("Win Rate: {:.1f}%".format(final_fry['win_rate'] * 100))
    
    print("\n🏦 Traditional Market Maker:")
    print("Final Capital: ${:,.2f}".format(final_mm['total_capital']))
    print("Total Return: {:.2f}%".format(final_mm['total_return'] * 100))
    print("Total Profits: ${:,.2f}".format(final_mm['total_profits']))
    print("Inventory: {:.4f} BTC".format(final_mm['inventory']))
    print("Inventory Value: ${:,.2f}".format(final_mm['inventory_value']))
    print("Trades Executed: {}".format(final_mm['trades_executed']))
    print("Win Rate: {:.1f}%".format(final_mm['win_rate'] * 100))
    
    # Comparative analysis
    print("\n📈 Comparative Analysis:")
    print("=" * 70)
    
    return_diff = final_fry['total_return'] - final_mm['total_return']
    profit_diff = final_fry['total_profits'] - final_mm['total_profits']
    
    print("Return Difference: {:.2f}% ({})".format(
        return_diff * 100,
        "FRY Agent Wins" if return_diff > 0 else "Traditional MM Wins"
    ))
    print("Profit Difference: ${:,.2f}".format(profit_diff))
    print("FRY Recycling Advantage: ${:.2f}".format(final_fry['recycled_value']))
    
    # Risk-adjusted metrics
    fry_sharpe = final_fry['total_return'] / (market_volatility * np.sqrt(duration_minutes/60))
    mm_sharpe = final_mm['total_return'] / (market_volatility * np.sqrt(duration_minutes/60))
    
    print("FRY Agent Sharpe Ratio: {:.2f}".format(fry_sharpe))
    print("Traditional MM Sharpe Ratio: {:.2f}".format(mm_sharpe))
    
    # Save results
    results = {
        'simulation_config': {
            'duration_minutes': duration_minutes,
            'market_volatility': market_volatility,
            'initial_capital': initial_capital
        },
        'final_metrics': {
            'fry_agent': final_fry,
            'traditional_mm': final_mm
        },
        'performance_history': performance_history,
        'comparative_analysis': {
            'return_difference_pct': return_diff * 100,
            'profit_difference_usd': profit_diff,
            'fry_recycling_advantage': final_fry['recycled_value'],
            'fry_sharpe_ratio': fry_sharpe,
            'mm_sharpe_ratio': mm_sharpe,
            'winner': 'FRY_Agent' if return_diff > 0 else 'Traditional_MM'
        }
    }
    
    results_file = "agent_vs_mm_comparison_{}.json".format(int(time.time()))
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to: {}".format(results_file))
    print("✅ Comparative simulation complete!")
    
    return results

if __name__ == "__main__":
    # Run the comparative simulation
    results = run_comparative_simulation(duration_minutes=45, market_volatility=0.03)
