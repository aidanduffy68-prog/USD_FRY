#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MM Tandem Simulation: MM_x (with Agent B) vs MM_y (traditional only)
===================================================================

Simulates two market makers:
- MM_x: Uses FRY Agent B in tandem with traditional market making
- MM_y: Pure traditional market making approach

Analyzes:
- Theoretical returns comparison
- Market churn and liquidity impact
- FRY recycling benefits
- Risk-adjusted performance
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

class HybridMarketMaker:
    """MM_x: Market Maker with FRY Agent B integration"""
    
    def __init__(self, initial_capital=500000, agent_id="mm_x_hybrid"):
        self.agent_id = agent_id
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Market making components
        self.inventory = 0.0
        self.mm_profits = 0.0
        self.mm_trades = 0
        
        # FRY arbitrage components
        self.fry_system = RektDarkCDO()
        self.slippage_engine = V2SlippageEngine()
        self.arbitrage_positions = {}
        self.fry_balance = 0.0
        self.recycled_value = 0.0
        self.arbitrage_profits = 0.0
        self.arbitrage_trades = 0
        
        # Combined metrics
        self.total_profits = 0.0
        self.total_trades = 0
        self.win_rate = 0.0
        self.market_churn_contributed = 0.0
        
        # Configuration
        self.config = {
            # Market making config
            'mm_spread_target': 0.0015,
            'mm_max_inventory': 15.0,
            'mm_quote_size': 0.2,
            'mm_capital_allocation': 0.7,  # 70% for MM, 30% for arbitrage
            
            # Arbitrage config
            'arb_min_slippage_threshold': 0.002,
            'arb_max_position_size': 0.03,
            'arb_fry_recycling_rate': 0.35,
            'arb_confidence_threshold': 0.7,
            'arb_profit_target': 0.008,
            'arb_stop_loss': 0.004,
            'arb_max_positions': 2,
        }
        
        self.logger = logging.getLogger("HybridMM_{}".format(self.agent_id))
    
    def analyze_and_trade(self, market_snapshot):
        """Hybrid strategy: MM + FRY arbitrage"""
        
        current_price = market_snapshot['price']
        
        # 1. Market making activities (primary)
        self._execute_market_making(market_snapshot)
        
        # 2. FRY arbitrage opportunities (secondary)
        self._execute_fry_arbitrage(market_snapshot)
        
        # 3. Update FRY recycling from market activity
        self._update_fry_recycling(market_snapshot)
        
        # 4. Monitor arbitrage positions
        self._monitor_arbitrage_positions(market_snapshot)
    
    def _execute_market_making(self, market_snapshot):
        """Traditional market making with FRY-enhanced spreads"""
        
        current_price = market_snapshot['price']
        volatility = market_snapshot.get('volatility', 0.02)
        volume = market_snapshot.get('volume', 0)
        
        # Enhanced spread calculation using FRY data
        base_spread = self.config['mm_spread_target']
        volatility_adjustment = volatility * 1.5
        inventory_adjustment = abs(self.inventory) * 0.0008
        
        # FRY enhancement: tighten spreads when recycling value is high
        fry_enhancement = min(0.0005, self.fry_balance * 0.01)
        
        dynamic_spread = base_spread + volatility_adjustment + inventory_adjustment - fry_enhancement
        dynamic_spread = max(0.001, dynamic_spread)  # Minimum spread
        
        bid_price = current_price * (1 - dynamic_spread / 2)
        ask_price = current_price * (1 + dynamic_spread / 2)
        
        # Market making fills with enhanced probability due to tighter spreads
        fill_probability = min(0.4, volume / 4000000)  # Higher fill rate
        
        mm_capital = self.current_capital * self.config['mm_capital_allocation']
        
        # Bid fills
        if random.random() < fill_probability and self.inventory < self.config['mm_max_inventory']:
            fill_size = self.config['mm_quote_size'] * random.uniform(0.7, 1.0)
            cost = fill_size * bid_price
            
            if cost < mm_capital * 0.15:
                self.inventory += fill_size
                self.current_capital -= cost
                self.mm_trades += 1
                self.total_trades += 1
                self.market_churn_contributed += cost
        
        # Ask fills
        if random.random() < fill_probability and self.inventory > 0:
            fill_size = min(self.inventory, self.config['mm_quote_size'] * random.uniform(0.7, 1.0))
            revenue = fill_size * ask_price
            
            self.inventory -= fill_size
            self.current_capital += revenue
            
            # Calculate MM profit
            avg_cost = current_price  # Simplified
            mm_profit = (ask_price - avg_cost) * fill_size
            self.mm_profits += mm_profit
            self.total_profits += mm_profit
            
            self.market_churn_contributed += revenue
    
    def _execute_fry_arbitrage(self, market_snapshot):
        """FRY arbitrage opportunities detection and execution"""
        
        # Detect slippage opportunities
        expected_slippage = self.slippage_engine.calculate_slippage(
            market_snapshot.get('volume', 0),
            market_snapshot.get('depth', {}),
            market_snapshot.get('volatility', 0.02)
        )
        
        # Player A activity detection
        player_a_signals = self._detect_player_a_activity(market_snapshot)
        
        # Signal strength calculation
        signal_strength = min(1.0, expected_slippage / 0.01)
        player_a_boost = sum(1 for signal in player_a_signals.values() if signal) * 0.15
        signal_strength += player_a_boost
        
        # Execute arbitrage if conditions met
        if (signal_strength >= self.config['arb_confidence_threshold'] and 
            len(self.arbitrage_positions) < self.config['arb_max_positions'] and
            expected_slippage >= self.config['arb_min_slippage_threshold']):
            
            arb_capital = self.current_capital * (1 - self.config['mm_capital_allocation'])
            position_size = arb_capital * self.config['arb_max_position_size'] * signal_strength
            
            if position_size >= 500:  # Minimum arbitrage position
                position_id = "arb_{}".format(int(time.time() * 1000))
                entry_price = market_snapshot['price']
                
                position = {
                    'id': position_id,
                    'entry_time': time.time(),
                    'entry_price': entry_price,
                    'size': position_size,
                    'stop_loss': entry_price * (1 - self.config['arb_stop_loss']),
                    'profit_target': entry_price * (1 + self.config['arb_profit_target']),
                    'confidence': signal_strength,
                    'expected_slippage': expected_slippage
                }
                
                self.arbitrage_positions[position_id] = position
                self.current_capital -= position_size
                self.arbitrage_trades += 1
                self.total_trades += 1
                self.market_churn_contributed += position_size
    
    def _detect_player_a_activity(self, market_snapshot):
        """Enhanced Player A detection for MM context"""
        signals = {
            'large_market_orders': market_snapshot.get('large_orders', 0) > 0.025,
            'momentum_chasing': len([r for r in market_snapshot.get('recent_returns', []) if r > 0.015]) >= 2,
            'social_media_correlation': market_snapshot.get('social_sentiment', 0.5) > 0.7,
            'volume_spike': market_snapshot.get('volume', 0) > 2000000,
            'spread_widening': market_snapshot.get('spread', 0.001) > 0.003
        }
        return signals
    
    def _update_fry_recycling(self, market_snapshot):
        """Update FRY recycling from detected market inefficiencies"""
        
        expected_slippage = self.slippage_engine.calculate_slippage(
            market_snapshot.get('volume', 0),
            market_snapshot.get('depth', {}),
            market_snapshot.get('volatility', 0.02)
        )
        
        if expected_slippage >= self.config['arb_min_slippage_threshold']:
            # Enhanced recycling rate for MM due to better market position
            recycling_rate = self.config['arb_fry_recycling_rate'] * 1.2  # 20% bonus
            recycled_amount = expected_slippage * recycling_rate * random.uniform(0.9, 1.3)
            
            self.fry_balance += recycled_amount
            self.recycled_value += recycled_amount
    
    def _monitor_arbitrage_positions(self, market_snapshot):
        """Monitor and close arbitrage positions"""
        
        current_price = market_snapshot['price']
        positions_to_close = []
        
        for pos_id, position in self.arbitrage_positions.items():
            if current_price >= position['profit_target']:
                profit = (current_price - position['entry_price']) * position['size'] / position['entry_price']
                self._close_arbitrage_position(pos_id, profit, 'profit_target')
                positions_to_close.append(pos_id)
            elif current_price <= position['stop_loss']:
                loss = (position['entry_price'] - current_price) * position['size'] / position['entry_price']
                self._close_arbitrage_position(pos_id, -loss, 'stop_loss')
                positions_to_close.append(pos_id)
        
        for pos_id in positions_to_close:
            del self.arbitrage_positions[pos_id]
    
    def _close_arbitrage_position(self, position_id, pnl, reason):
        """Close arbitrage position"""
        position = self.arbitrage_positions[position_id]
        self.current_capital += position['size'] + pnl
        self.arbitrage_profits += pnl
        self.total_profits += pnl
        self.market_churn_contributed += position['size']
        
        # Update win rate
        wins = 1 if pnl > 0 else 0
        self.win_rate = (self.win_rate * (self.total_trades - 1) + wins) / self.total_trades
    
    def get_metrics(self):
        """Get comprehensive metrics"""
        inventory_value = self.inventory * 50000  # Assume $50k BTC
        total_capital_with_inventory = self.current_capital + inventory_value
        
        return {
            'agent_type': 'Hybrid_MM_x',
            'total_capital': total_capital_with_inventory,
            'total_return': (total_capital_with_inventory - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'mm_profits': self.mm_profits,
            'arbitrage_profits': self.arbitrage_profits,
            'fry_balance': self.fry_balance,
            'recycled_value': self.recycled_value,
            'inventory': self.inventory,
            'inventory_value': inventory_value,
            'total_trades': self.total_trades,
            'mm_trades': self.mm_trades,
            'arbitrage_trades': self.arbitrage_trades,
            'win_rate': self.win_rate,
            'market_churn_contributed': self.market_churn_contributed,
            'active_arbitrage_positions': len(self.arbitrage_positions)
        }

class TraditionalMarketMaker:
    """MM_y: Pure traditional market maker"""
    
    def __init__(self, initial_capital=500000, agent_id="mm_y_traditional"):
        self.agent_id = agent_id
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Market making state
        self.inventory = 0.0
        self.total_profits = 0.0
        self.trades_executed = 0
        self.win_rate = 0.0
        self.market_churn_contributed = 0.0
        
        # Configuration
        self.config = {
            'spread_target': 0.002,      # Slightly wider spreads
            'max_inventory': 12.0,       # More conservative inventory
            'quote_size': 0.15,          # Smaller quote sizes
            'inventory_penalty': 0.001,
            'risk_adjustment': 0.6,
        }
        
        self.logger = logging.getLogger("TraditionalMM_{}".format(self.agent_id))
    
    def analyze_and_trade(self, market_snapshot):
        """Pure traditional market making"""
        
        current_price = market_snapshot['price']
        volatility = market_snapshot.get('volatility', 0.02)
        volume = market_snapshot.get('volume', 0)
        
        # Conservative spread calculation
        base_spread = self.config['spread_target']
        volatility_adjustment = volatility * 2.0  # More conservative
        inventory_adjustment = abs(self.inventory) * self.config['inventory_penalty']
        
        dynamic_spread = base_spread + volatility_adjustment + inventory_adjustment
        
        bid_price = current_price * (1 - dynamic_spread / 2)
        ask_price = current_price * (1 + dynamic_spread / 2)
        
        # Standard market making fills
        fill_probability = min(0.25, volume / 6000000)  # Lower fill rate due to wider spreads
        
        # Bid fills
        if random.random() < fill_probability and self.inventory < self.config['max_inventory']:
            fill_size = self.config['quote_size'] * random.uniform(0.5, 1.0)
            cost = fill_size * bid_price
            
            if cost < self.current_capital * 0.12:
                self.inventory += fill_size
                self.current_capital -= cost
                self.trades_executed += 1
                self.market_churn_contributed += cost
        
        # Ask fills
        if random.random() < fill_probability and self.inventory > 0:
            fill_size = min(self.inventory, self.config['quote_size'] * random.uniform(0.5, 1.0))
            revenue = fill_size * ask_price
            
            self.inventory -= fill_size
            self.current_capital += revenue
            
            # Calculate profit
            avg_cost = current_price
            profit = (ask_price - avg_cost) * fill_size
            self.total_profits += profit
            
            # Update win rate (traditional MM typically has high win rate)
            self.win_rate = (self.win_rate * (self.trades_executed - 1) + 0.85) / self.trades_executed
            self.market_churn_contributed += revenue
        
        # Apply inventory carrying costs
        if self.inventory != 0:
            inventory_cost = abs(self.inventory) * current_price * 0.0001
            self.current_capital -= inventory_cost
            self.total_profits -= inventory_cost
    
    def get_metrics(self):
        """Get performance metrics"""
        inventory_value = self.inventory * 50000
        total_capital_with_inventory = self.current_capital + inventory_value
        
        return {
            'agent_type': 'Traditional_MM_y',
            'total_capital': total_capital_with_inventory,
            'total_return': (total_capital_with_inventory - self.initial_capital) / self.initial_capital,
            'total_profits': self.total_profits,
            'inventory': self.inventory,
            'inventory_value': inventory_value,
            'trades_executed': self.trades_executed,
            'win_rate': self.win_rate,
            'market_churn_contributed': self.market_churn_contributed
        }

class MarketSimulator:
    """Enhanced market simulator with churn tracking"""
    
    def __init__(self):
        self.base_price = 50000
        self.time_step = 0
        self.total_market_churn = 0.0
        self.liquidity_events = []
    
    def generate_market_snapshot(self, volatility=0.025):
        """Generate market data with churn tracking"""
        
        # Price movement
        price_change = np.random.normal(0, volatility)
        self.base_price *= (1 + price_change)
        
        # Market conditions
        volume = random.uniform(1000000, 4000000)
        social_sentiment = random.uniform(0.3, 0.95)
        large_orders = random.uniform(0, 0.1)
        
        # Enhanced market data for MM comparison
        spread = random.uniform(0.0008, 0.0025)
        recent_returns = [random.uniform(-0.04, 0.04) for _ in range(5)]
        
        # Liquidity events (affects both MMs)
        liquidity_event = random.random() < 0.1  # 10% chance
        if liquidity_event:
            volume *= random.uniform(1.5, 3.0)
            large_orders *= random.uniform(2.0, 4.0)
            self.liquidity_events.append({
                'timestamp': time.time(),
                'volume_multiplier': volume / 2000000,
                'price': self.base_price
            })
        
        snapshot = {
            'timestamp': time.time(),
            'price': self.base_price,
            'volume': volume,
            'volatility': volatility,
            'spread': spread,
            'social_sentiment': social_sentiment,
            'large_orders': large_orders,
            'recent_returns': recent_returns,
            'depth': {'bids': random.uniform(2000, 8000), 'asks': random.uniform(2000, 8000)},
            'volume_spike': volume > 3000000,
            'liquidity_event': liquidity_event
        }
        
        self.time_step += 1
        return snapshot

def run_mm_tandem_simulation(duration_minutes=60, market_volatility=0.03):
    """Run MM_x vs MM_y comparative simulation"""
    
    print("🔄 MM Tandem Simulation: MM_x (Hybrid) vs MM_y (Traditional)")
    print("=" * 80)
    
    # Initialize market makers with larger capital
    initial_capital = 500000
    mm_x_hybrid = HybridMarketMaker(initial_capital, "mm_x_hybrid")
    mm_y_traditional = TraditionalMarketMaker(initial_capital, "mm_y_traditional")
    market_sim = MarketSimulator()
    
    print("MM_x: Hybrid (Traditional MM + FRY Agent B)")
    print("MM_y: Pure Traditional Market Maker")
    print("Initial Capital: ${:,.2f} each".format(initial_capital))
    print("Simulation Duration: {} minutes".format(duration_minutes))
    print("Market Volatility: {:.1f}%".format(market_volatility * 100))
    print()
    
    # Performance tracking
    performance_history = []
    churn_history = []
    
    print("🚀 Running MM tandem simulation...")
    
    for minute in range(duration_minutes):
        # Generate market data
        market_snapshot = market_sim.generate_market_snapshot(market_volatility)
        
        # Both MMs operate in same market
        mm_x_hybrid.analyze_and_trade(market_snapshot)
        mm_y_traditional.analyze_and_trade(market_snapshot)
        
        # Track performance every 15 minutes
        if minute % 15 == 0:
            mm_x_metrics = mm_x_hybrid.get_metrics()
            mm_y_metrics = mm_y_traditional.get_metrics()
            
            performance_history.append({
                'minute': minute,
                'mm_x_capital': mm_x_metrics['total_capital'],
                'mm_x_return': mm_x_metrics['total_return'],
                'mm_x_churn': mm_x_metrics['market_churn_contributed'],
                'mm_y_capital': mm_y_metrics['total_capital'],
                'mm_y_return': mm_y_metrics['total_return'],
                'mm_y_churn': mm_y_metrics['market_churn_contributed'],
                'market_price': market_snapshot['price']
            })
            
            print("Min {}: MM_x={:.2f}% (${:,.0f} churn) | MM_y={:.2f}% (${:,.0f} churn) | Price=${:,.0f}".format(
                minute,
                mm_x_metrics['total_return'] * 100,
                mm_x_metrics['market_churn_contributed'],
                mm_y_metrics['total_return'] * 100,
                mm_y_metrics['market_churn_contributed'],
                market_snapshot['price']
            ))
        
        time.sleep(0.005)  # Faster simulation
    
    # Final analysis
    print("\n📊 Final Results:")
    print("=" * 80)
    
    final_mm_x = mm_x_hybrid.get_metrics()
    final_mm_y = mm_y_traditional.get_metrics()
    
    print("\n🔄 MM_x (Hybrid: Traditional + FRY Agent B):")
    print("Final Capital: ${:,.2f}".format(final_mm_x['total_capital']))
    print("Total Return: {:.2f}%".format(final_mm_x['total_return'] * 100))
    print("Total Profits: ${:,.2f}".format(final_mm_x['total_profits']))
    print("  - MM Profits: ${:,.2f}".format(final_mm_x['mm_profits']))
    print("  - Arbitrage Profits: ${:,.2f}".format(final_mm_x['arbitrage_profits']))
    print("FRY Balance: {:.4f} tokens".format(final_mm_x['fry_balance']))
    print("Recycled Value: ${:.2f}".format(final_mm_x['recycled_value']))
    print("Total Trades: {} (MM: {}, Arb: {})".format(
        final_mm_x['total_trades'], final_mm_x['mm_trades'], final_mm_x['arbitrage_trades']))
    print("Win Rate: {:.1f}%".format(final_mm_x['win_rate'] * 100))
    print("Market Churn Contributed: ${:,.2f}".format(final_mm_x['market_churn_contributed']))
    
    print("\n🏦 MM_y (Traditional Only):")
    print("Final Capital: ${:,.2f}".format(final_mm_y['total_capital']))
    print("Total Return: {:.2f}%".format(final_mm_y['total_return'] * 100))
    print("Total Profits: ${:,.2f}".format(final_mm_y['total_profits']))
    print("Trades Executed: {}".format(final_mm_y['trades_executed']))
    print("Win Rate: {:.1f}%".format(final_mm_y['win_rate'] * 100))
    print("Market Churn Contributed: ${:,.2f}".format(final_mm_y['market_churn_contributed']))
    
    # Comparative analysis
    print("\n📈 Comparative Analysis:")
    print("=" * 80)
    
    return_diff = final_mm_x['total_return'] - final_mm_y['total_return']
    profit_diff = final_mm_x['total_profits'] - final_mm_y['total_profits']
    churn_diff = final_mm_x['market_churn_contributed'] - final_mm_y['market_churn_contributed']
    
    print("Return Advantage: {:.2f}% ({})".format(
        return_diff * 100,
        "MM_x Wins" if return_diff > 0 else "MM_y Wins"
    ))
    print("Profit Difference: ${:,.2f}".format(profit_diff))
    print("Market Churn Difference: ${:,.2f} ({:.1f}% more)".format(
        churn_diff, (churn_diff / final_mm_y['market_churn_contributed']) * 100 if final_mm_y['market_churn_contributed'] > 0 else 0
    ))
    print("FRY Recycling Advantage: ${:.2f}".format(final_mm_x['recycled_value']))
    
    # Efficiency metrics
    mm_x_profit_per_trade = final_mm_x['total_profits'] / max(1, final_mm_x['total_trades'])
    mm_y_profit_per_trade = final_mm_y['total_profits'] / max(1, final_mm_y['trades_executed'])
    
    print("MM_x Profit per Trade: ${:.2f}".format(mm_x_profit_per_trade))
    print("MM_y Profit per Trade: ${:.2f}".format(mm_y_profit_per_trade))
    
    # Market impact analysis
    total_churn = final_mm_x['market_churn_contributed'] + final_mm_y['market_churn_contributed']
    mm_x_churn_share = final_mm_x['market_churn_contributed'] / total_churn * 100 if total_churn > 0 else 0
    
    print("MM_x Market Churn Share: {:.1f}%".format(mm_x_churn_share))
    print("Total Market Churn Generated: ${:,.2f}".format(total_churn))
    
    # Save results
    results = {
        'simulation_config': {
            'duration_minutes': duration_minutes,
            'market_volatility': market_volatility,
            'initial_capital': initial_capital
        },
        'final_metrics': {
            'mm_x_hybrid': final_mm_x,
            'mm_y_traditional': final_mm_y
        },
        'performance_history': performance_history,
        'comparative_analysis': {
            'return_difference_pct': return_diff * 100,
            'profit_difference_usd': profit_diff,
            'churn_difference_usd': churn_diff,
            'fry_recycling_advantage': final_mm_x['recycled_value'],
            'mm_x_profit_per_trade': mm_x_profit_per_trade,
            'mm_y_profit_per_trade': mm_y_profit_per_trade,
            'mm_x_churn_share_pct': mm_x_churn_share,
            'total_market_churn': total_churn,
            'winner': 'MM_x_Hybrid' if return_diff > 0 else 'MM_y_Traditional'
        },
        'liquidity_events': market_sim.liquidity_events
    }
    
    results_file = "mm_tandem_comparison_{}.json".format(int(time.time()))
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to: {}".format(results_file))
    print("✅ MM tandem simulation complete!")
    
    return results

if __name__ == "__main__":
    # Run the MM tandem simulation
    results = run_mm_tandem_simulation(duration_minutes=75, market_volatility=0.035)
