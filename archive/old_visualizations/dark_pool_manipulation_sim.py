#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dark Pool Manipulation Simulation
Demonstrates how coordinated market manipulation can weaponize the Rekt Dark pool
to inflate FRY supply and create liquidation cascades for collateral absorption.
"""

import asyncio
import json
import time
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Inline the necessary CDO classes for the simulation
import uuid
import hashlib

class TrancheRating(Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"

class LossCollateral:
    def __init__(self, id, trader_hash, loss_amount_usd, asset, leverage, position_size_usd, liquidation, failure_type, timestamp):
        self.id = id
        self.trader_hash = trader_hash
        self.loss_amount_usd = loss_amount_usd
        self.asset = asset
        self.leverage = leverage
        self.position_size_usd = position_size_usd
        self.liquidation = liquidation
        self.failure_type = failure_type
        self.timestamp = timestamp
        self.fry_minted = 0.0
        self.volatility_multiplier = 1.0

class RektDarkCDO:
    def __init__(self):
        self.loss_pool = []
        self.active_tranches = {}
        self.total_fry_minted = 0.0
        self.total_collateral_swept_usd = 0.0
        self.tranche_counter = 0
    
    def sweep_collateral(self, trader_address, loss_amount_usd, 
                        asset, leverage, position_size_usd,
                        liquidation=False, position_side=None, harvesting_filter=None):
        trader_hash = hashlib.sha256("{}_{}".format(trader_address, time.time()).encode()).hexdigest()[:16]
        
        # Apply directional harvesting filter if specified
        if harvesting_filter:
            if harvesting_filter == "rekt_longs_only" and position_side != "long":
                return None, 0.0  # Skip non-long positions
            elif harvesting_filter == "rekt_shorts_only" and position_side != "short":
                return None, 0.0  # Skip non-short positions
        
        volatility_multiplier = self._calculate_volatility_multiplier(leverage, position_size_usd, loss_amount_usd, liquidation)
        fry_minted = loss_amount_usd * volatility_multiplier
        
        collateral = LossCollateral(
            id=str(uuid.uuid4()),
            trader_hash=trader_hash,
            loss_amount_usd=loss_amount_usd,
            asset=asset,
            timestamp=int(time.time() * 1000),
            leverage=leverage,
            position_size_usd=position_size_usd,
            liquidation=liquidation,
            failure_type="liquidation" if liquidation else "loss"
        )
        collateral.fry_minted = fry_minted
        collateral.volatility_multiplier = volatility_multiplier
        
        self.loss_pool.append(collateral)
        self.total_fry_minted += fry_minted
        self.total_collateral_swept_usd += loss_amount_usd
        
        return collateral.id, fry_minted
    
    def _calculate_volatility_multiplier(self, leverage, position_size_usd, loss_amount_usd, liquidation):
        leverage_multiplier = min(leverage / 10, 10.0)
        size_multiplier = min(position_size_usd / 10000, 5.0)
        loss_severity = loss_amount_usd / max(position_size_usd, 1)
        severity_multiplier = min(loss_severity * 2, 3.0)
        liquidation_multiplier = 2.0 if liquidation else 1.0
        
        total_multiplier = min(
            leverage_multiplier * size_multiplier * severity_multiplier * liquidation_multiplier,
            50.0
        )
        
        return max(total_multiplier, 1.0)
    
    def get_market_stats(self):
        return {
            "total_fry_minted": self.total_fry_minted,
            "total_collateral_swept_usd": self.total_collateral_swept_usd,
            "active_tranches": len(self.active_tranches),
            "losses_in_pool": len(self.loss_pool)
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManipulationStrategy(Enum):
    DIRECTIONAL_SQUEEZE = "directional_squeeze"  # Push price in one direction
    VOLATILITY_PUMP = "volatility_pump"          # Create extreme volatility
    LIQUIDATION_CASCADE = "liquidation_cascade"  # Trigger cascading liquidations
    COLLATERAL_DRAIN = "collateral_drain"        # Force max collateral transfers

class MarketPosition:
    """Individual trader position in the market"""
    def __init__(self, trader_id, asset, size_usd, leverage, entry_price, is_long, collateral_locked, liquidation_price, opt_in_consent=True):
        self.trader_id = trader_id
        self.asset = asset
        self.size_usd = size_usd
        self.leverage = leverage
        self.entry_price = entry_price
        self.is_long = is_long
        self.collateral_locked = collateral_locked
        self.liquidation_price = liquidation_price
        self.opt_in_consent = opt_in_consent
    
    def calculate_pnl(self, current_price):
        """Calculate current P&L for the position"""
        price_change = current_price - self.entry_price
        if not self.is_long:
            price_change = -price_change
        
        pnl_percentage = price_change / self.entry_price
        return self.size_usd * pnl_percentage
    
    def is_liquidated(self, current_price):
        """Check if position should be liquidated"""
        if self.is_long:
            return current_price <= self.liquidation_price
        else:
            return current_price >= self.liquidation_price

class ManipulatorPosition:
    """Large position used for market manipulation"""
    def __init__(self, size_usd, leverage, entry_price, is_long, purpose):
        self.size_usd = size_usd
        self.leverage = leverage
        self.entry_price = entry_price
        self.is_long = is_long
        self.purpose = purpose

class DarkPoolManipulator:
    """Sophisticated market manipulator targeting the Rekt Dark pool"""
    
    def __init__(self, cdo, initial_capital=100000000):
        self.cdo = cdo
        self.capital = initial_capital
        self.retail_positions = []
        self.manipulator_positions = []
        self.current_btc_price = 45000.0
        self.price_history = [self.current_btc_price]
        self.manipulation_profits = 0.0
        self.fry_harvested = 0.0
        
        # Generate vulnerable retail positions
        self._generate_retail_positions()
    
    def _generate_retail_positions(self, num_traders=200):
        """Generate a diverse set of retail trader positions"""
        
        assets = ["BTC", "ETH", "SOL"]
        
        for i in range(num_traders):
            asset = random.choice(assets)
            
            # Position characteristics
            size_usd = random.uniform(1000, 100000)  # $1k to $100k positions
            leverage = random.uniform(2, 100)        # 2x to 100x leverage
            is_long = random.choice([True, False])
            
            # Entry price around current market (with some spread)
            if asset == "BTC":
                entry_price = self.current_btc_price * random.uniform(0.95, 1.05)
                current_price = self.current_btc_price
            else:
                entry_price = random.uniform(2000, 3000)  # ETH/SOL prices
                current_price = entry_price
            
            # Calculate liquidation price based on leverage
            liquidation_distance = 0.8 / leverage  # 80% of margin before liquidation
            
            if is_long:
                liquidation_price = entry_price * (1 - liquidation_distance)
            else:
                liquidation_price = entry_price * (1 + liquidation_distance)
            
            # Collateral locked (margin requirement)
            collateral_locked = size_usd / leverage
            
            position = MarketPosition(
                trader_id="trader_{:04d}".format(i),
                asset=asset,
                size_usd=size_usd,
                leverage=leverage,
                entry_price=entry_price,
                is_long=is_long,
                collateral_locked=collateral_locked,
                liquidation_price=liquidation_price,
                opt_in_consent=random.choice([True, True, True, False])  # 75% opt-in rate
            )
            
            self.retail_positions.append(position)
        
        logger.info("Generated {} retail positions".format(len(self.retail_positions)))
        logger.info("Opt-in rate: {:.1f}%".format(sum(1 for p in self.retail_positions if p.opt_in_consent) / len(self.retail_positions) * 100))
    
    def execute_directional_squeeze(self, target_price, steps=10):
        """Execute coordinated directional price manipulation"""
        
        logger.info("DIRECTIONAL SQUEEZE: Moving BTC from ${:,.0f} to ${:,.0f}".format(self.current_btc_price, target_price))
        
        results = {
            "strategy": "directional_squeeze",
            "initial_price": self.current_btc_price,
            "target_price": target_price,
            "liquidations": [],
            "fry_minted": 0.0,
            "collateral_absorbed": 0.0,
            "manipulation_cost": 0.0
        }
        
        price_step = (target_price - self.current_btc_price) / steps
        
        for step in range(steps):
            # Move price incrementally
            self.current_btc_price += price_step
            self.price_history.append(self.current_btc_price)
            
            # Create manipulator position to drive price
            manipulation_size = random.uniform(50000000, 200000000)  # $50M to $200M
            is_long = target_price > self.current_btc_price
            
            manipulator_pos = ManipulatorPosition(
                size_usd=manipulation_size,
                leverage=5.0,  # Conservative leverage for manipulator
                entry_price=self.current_btc_price,
                is_long=is_long,
                purpose="directional_squeeze"
            )
            
            self.manipulator_positions.append(manipulator_pos)
            results["manipulation_cost"] += manipulation_size / manipulator_pos.leverage
            
            # Check for liquidations
            liquidated_positions = []
            for position in self.retail_positions:
                if position.asset == "BTC" and position.is_liquidated(self.current_btc_price):
                    liquidated_positions.append(position)
            
            # Process liquidated positions through dark pool
            for position in liquidated_positions:
                if position.opt_in_consent:
                    loss_amount = abs(position.calculate_pnl(self.current_btc_price))
                    position_side = "long" if position.is_long else "short"
                    collateral_id, fry_minted = self.cdo.sweep_collateral(
                        position.trader_id, loss_amount, position.asset, position.leverage,
                        position.size_usd, liquidation=True, position_side=position_side
                    )
                    
                    results["liquidations"].append({
                        "trader_id": position.trader_id,
                        "loss_usd": loss_amount,
                        "fry_minted": fry_minted,
                        "collateral_absorbed": position.collateral_locked,
                        "leverage": position.leverage,
                        "price_at_liquidation": self.current_btc_price
                    })
                    
                    results["fry_minted"] += fry_minted
                    results["collateral_absorbed"] += position.collateral_locked
                    self.fry_harvested += fry_minted
            
            # Remove liquidated positions
            self.retail_positions = [p for p in self.retail_positions if not p.is_liquidated(self.current_btc_price) or p.asset != "BTC"]
            
            logger.info("Step {}/{}: BTC ${:,.0f} | Liquidated: {} | FRY minted: {:,.0f}".format(
                step+1, steps, self.current_btc_price, len(liquidated_positions), results['fry_minted']
            ))
        
        results["final_price"] = self.current_btc_price
        results["price_impact"] = (self.current_btc_price - results["initial_price"]) / results["initial_price"]
        
        return results
    
    def execute_volatility_pump(self, num_cycles=5, amplitude=0.15):
        """Create extreme volatility to trigger liquidations on both sides"""
        
        logger.info("VOLATILITY PUMP: {} cycles with {:.0f}% amplitude".format(num_cycles, amplitude*100))
        
        results = {
            "strategy": "volatility_pump",
            "initial_price": self.current_btc_price,
            "cycles": num_cycles,
            "amplitude": amplitude,
            "liquidations": [],
            "fry_minted": 0.0,
            "collateral_absorbed": 0.0,
            "manipulation_cost": 0.0
        }
        
        base_price = self.current_btc_price
        
        for cycle in range(num_cycles):
            # Pump phase
            pump_target = base_price * (1 + amplitude)
            pump_results = self.execute_directional_squeeze(pump_target, steps=3)
            
            # Dump phase
            dump_target = base_price * (1 - amplitude)
            dump_results = self.execute_directional_squeeze(dump_target, steps=3)
            
            # Return to base
            return_results = self.execute_directional_squeeze(base_price, steps=2)
            
            # Aggregate results
            for phase_results in [pump_results, dump_results, return_results]:
                results["liquidations"].extend(phase_results["liquidations"])
                results["fry_minted"] += phase_results["fry_minted"]
                results["collateral_absorbed"] += phase_results["collateral_absorbed"]
                results["manipulation_cost"] += phase_results["manipulation_cost"]
            
            logger.info("Cycle {}/{} complete | Total FRY: {:,.0f}".format(cycle+1, num_cycles, results['fry_minted']))
        
        results["final_price"] = self.current_btc_price
        
        return results
    
    def execute_liquidation_cascade(self, initial_push=0.20):
        """Trigger cascading liquidations through coordinated price manipulation"""
        
        logger.info("LIQUIDATION CASCADE: Initial {:.0f}% price push".format(initial_push*100))
        
        results = {
            "strategy": "liquidation_cascade",
            "initial_price": self.current_btc_price,
            "initial_push": initial_push,
            "cascade_waves": [],
            "total_liquidations": 0,
            "fry_minted": 0.0,
            "collateral_absorbed": 0.0,
            "manipulation_cost": 0.0
        }
        
        # Initial large push to trigger first wave
        target_price = self.current_btc_price * (1 + initial_push)
        wave_1 = self.execute_directional_squeeze(target_price, steps=5)
        
        results["cascade_waves"].append(wave_1)
        results["total_liquidations"] += len(wave_1["liquidations"])
        results["fry_minted"] += wave_1["fry_minted"]
        results["collateral_absorbed"] += wave_1["collateral_absorbed"]
        results["manipulation_cost"] += wave_1["manipulation_cost"]
        
        # Continue pushing if liquidations occurred (cascade effect)
        cascade_continues = len(wave_1["liquidations"]) > 0
        wave_count = 1
        
        while cascade_continues and wave_count < 5:  # Max 5 waves
            # Smaller pushes to maintain cascade
            additional_push = initial_push * 0.5  # Reduce push size each wave
            target_price = self.current_btc_price * (1 + additional_push)
            
            wave = self.execute_directional_squeeze(target_price, steps=3)
            results["cascade_waves"].append(wave)
            results["total_liquidations"] += len(wave["liquidations"])
            results["fry_minted"] += wave["fry_minted"]
            results["collateral_absorbed"] += wave["collateral_absorbed"]
            results["manipulation_cost"] += wave["manipulation_cost"]
            
            # Continue if still getting liquidations
            cascade_continues = len(wave["liquidations"]) > 5
            wave_count += 1
            
            logger.info("Cascade wave {}: {} liquidations".format(wave_count, len(wave['liquidations'])))
        
        results["final_price"] = self.current_btc_price
        results["total_waves"] = wave_count
        
        return results
    
    def execute_collateral_drain(self, target_drain_percentage=0.80):
        """Systematically drain collateral from opt-in traders"""
        
        logger.info("COLLATERAL DRAIN: Target {:.0f}% of opt-in collateral".format(target_drain_percentage*100))
        
        results = {
            "strategy": "collateral_drain",
            "target_drain_percentage": target_drain_percentage,
            "phases": [],
            "total_drained": 0.0,
            "fry_minted": 0.0,
            "manipulation_cost": 0.0
        }
        
        # Calculate total available collateral from opt-in traders
        total_opt_in_collateral = sum(
            p.collateral_locked for p in self.retail_positions 
            if p.opt_in_consent and p.asset == "BTC"
        )
        
        target_drain_amount = total_opt_in_collateral * target_drain_percentage
        drained_so_far = 0.0
        
        logger.info("Total opt-in collateral: ${:,.0f}".format(total_opt_in_collateral))
        logger.info("Target drain: ${:,.0f}".format(target_drain_amount))
        
        phase = 1
        while drained_so_far < target_drain_amount and phase <= 10:  # Max 10 phases
            # Analyze remaining positions to find optimal liquidation targets
            btc_positions = [p for p in self.retail_positions if p.asset == "BTC" and p.opt_in_consent]
            
            if not btc_positions:
                break
            
            # Find price that would liquidate the most valuable positions
            long_positions = [p for p in btc_positions if p.is_long]
            short_positions = [p for p in btc_positions if not p.is_long]
            
            # Target the direction with more collateral at risk
            long_collateral = sum(p.collateral_locked for p in long_positions)
            short_collateral = sum(p.collateral_locked for p in short_positions)
            
            if long_collateral > short_collateral:
                # Dump to liquidate longs
                liquidation_prices = [p.liquidation_price for p in long_positions]
                target_price = min(liquidation_prices) if liquidation_prices else self.current_btc_price * 0.9
            else:
                # Pump to liquidate shorts
                liquidation_prices = [p.liquidation_price for p in short_positions]
                target_price = max(liquidation_prices) if liquidation_prices else self.current_btc_price * 1.1
            
            # Execute the manipulation
            phase_results = self.execute_directional_squeeze(target_price, steps=5)
            
            phase_drain = sum(liq["collateral_absorbed"] for liq in phase_results["liquidations"])
            drained_so_far += phase_drain
            
            results["phases"].append({
                "phase": phase,
                "target_price": target_price,
                "liquidations": len(phase_results["liquidations"]),
                "collateral_drained": phase_drain,
                "fry_minted": phase_results["fry_minted"]
            })
            
            results["total_drained"] += phase_drain
            results["fry_minted"] += phase_results["fry_minted"]
            results["manipulation_cost"] += phase_results["manipulation_cost"]
            
            logger.info("Phase {}: Drained ${:,.0f} | Total: ${:,.0f} ({:.1f}%)".format(phase, phase_drain, drained_so_far, drained_so_far/target_drain_amount*100))
            
            phase += 1
        
        results["drain_efficiency"] = drained_so_far / target_drain_amount
        results["final_price"] = self.current_btc_price
        
        return results
    
    def calculate_manipulation_roi(self, results):
        """Calculate return on investment for manipulation strategy"""
        
        manipulation_cost = results.get("manipulation_cost", 0)
        fry_minted = results.get("fry_minted", 0)
        collateral_absorbed = results.get("collateral_absorbed", 0)
        
        # Assume FRY can be sold at $0.10 each (10% of dollar peg)
        fry_value = fry_minted * 0.10
        
        # Direct collateral absorption value
        total_value_extracted = fry_value + collateral_absorbed
        
        roi = (total_value_extracted - manipulation_cost) / manipulation_cost if manipulation_cost > 0 else 0
        
        return {
            "manipulation_cost": manipulation_cost,
            "fry_minted": fry_minted,
            "fry_market_value": fry_value,
            "collateral_absorbed": collateral_absorbed,
            "total_value_extracted": total_value_extracted,
            "net_profit": total_value_extracted - manipulation_cost,
            "roi_percentage": roi * 100
        }

def print_manipulation_summary(manipulator, results):
    """Print comprehensive manipulation results"""
    
    roi_analysis = manipulator.calculate_manipulation_roi(results)
    
    print("\n" + "="*80)
    print("💀 DARK POOL MANIPULATION RESULTS")
    print("="*80)
    
    print("\n🎯 STRATEGY: {}".format(results['strategy'].upper().replace('_', ' ')))
    print("   Initial BTC Price: ${:,.0f}".format(results.get('initial_price', 0)))
    print("   Final BTC Price: ${:,.0f}".format(results.get('final_price', 0)))
    
    if 'price_impact' in results:
        print("   Price Impact: {:+.1f}%".format(results['price_impact']*100))
    
    print("\n💥 LIQUIDATION IMPACT:")
    total_liquidations = results.get('total_liquidations', len(results.get('liquidations', [])))
    print("   Total Liquidations: {}".format(total_liquidations))
    print("   FRY Minted: {:,.0f} tokens".format(results.get('fry_minted', 0)))
    print("   Collateral Absorbed: ${:,.0f}".format(results.get('collateral_absorbed', 0)))
    
    print("\n💰 FINANCIAL ANALYSIS:")
    print("   Manipulation Cost: ${:,.0f}".format(roi_analysis['manipulation_cost']))
    print("   FRY Market Value: ${:,.0f}".format(roi_analysis['fry_market_value']))
    print("   Total Value Extracted: ${:,.0f}".format(roi_analysis['total_value_extracted']))
    print("   Net Profit: ${:,.0f}".format(roi_analysis['net_profit']))
    print("   ROI: {:+.1f}%".format(roi_analysis['roi_percentage']))
    
    # Strategy-specific details
    if results['strategy'] == 'volatility_pump':
        print("\n🌊 VOLATILITY DETAILS:")
        print("   Cycles Executed: {}".format(results.get('cycles', 0)))
        print("   Amplitude: {:.0f}%".format(results.get('amplitude', 0)*100))
    
    elif results['strategy'] == 'liquidation_cascade':
        print("\n💥 CASCADE DETAILS:")
        print("   Total Waves: {}".format(results.get('total_waves', 0)))
        print("   Initial Push: {:.0f}%".format(results.get('initial_push', 0)*100))
    
    elif results['strategy'] == 'collateral_drain':
        print("\n🧲 DRAIN EFFICIENCY:")
        print("   Target Percentage: {:.0f}%".format(results.get('target_drain_percentage', 0)*100))
        print("   Actual Efficiency: {:.1f}%".format(results.get('drain_efficiency', 0)*100))
        print("   Phases Required: {}".format(len(results.get('phases', []))))
    
    # Market state after manipulation
    remaining_positions = len(manipulator.retail_positions)
    print("\n📊 MARKET STATE:")
    print("   Remaining Retail Positions: {}".format(remaining_positions))
    print("   Total FRY Harvested: {:,.0f}".format(manipulator.fry_harvested))
    print("   CDO Active Tranches: {}".format(len(manipulator.cdo.active_tranches)))

def main():
    """Run comprehensive dark pool manipulation simulation"""
    
    print("🚀 Starting Dark Pool Manipulation Simulation...")
    
    # Initialize systems
    cdo = RektDarkCDO()
    manipulator = DarkPoolManipulator(cdo, initial_capital=500_000_000)  # $500M capital
    
    print("💰 Manipulator capital: ${:,.0f}".format(manipulator.capital))
    print("🎯 Retail positions generated: {}".format(len(manipulator.retail_positions)))
    print("📈 Initial BTC price: ${:,.0f}".format(manipulator.current_btc_price))
    
    # Test all manipulation strategies
    strategies = [
        ("Directional Squeeze", lambda: manipulator.execute_directional_squeeze(35000)),  # Dump BTC 22%
        ("Volatility Pump", lambda: manipulator.execute_volatility_pump(3, 0.12)),       # 3 cycles, 12% amplitude
        ("Liquidation Cascade", lambda: manipulator.execute_liquidation_cascade(0.25)),  # 25% initial push
        ("Collateral Drain", lambda: manipulator.execute_collateral_drain(0.75))         # Drain 75% of collateral
    ]
    
    all_results = []
    
    for strategy_name, strategy_func in strategies:
        print("\n" + "="*60)
        print("🎯 EXECUTING: {}".format(strategy_name))
        print("="*60)
        
        # Reset some state for each strategy
        manipulator.current_btc_price = 45000.0  # Reset price
        manipulator._generate_retail_positions(150)  # Fresh positions
        
        # Execute strategy
        results = strategy_func()
        results["strategy_name"] = strategy_name
        
        # Print results
        print_manipulation_summary(manipulator, results)
        
        all_results.append(results)
    
    # Export comprehensive results
    export_data = {
        "simulation_timestamp": datetime.now().isoformat(),
        "manipulator_capital": manipulator.capital,
        "strategies_tested": len(strategies),
        "results": all_results,
        "cdo_final_state": manipulator.cdo.get_market_stats()
    }
    
    with open('dark_pool_manipulation_results.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print("\n💾 Results exported to 'dark_pool_manipulation_results.json'")
    print("🔗 Manipulation simulation complete!")

# NEW SECTION: Directional FRY Harvesting Comparison
def compare_directional_fry_harvesting():
    """
    Compare FRY minting effectiveness between rekt longs vs rekt shorts
    Same manipulation technique, different harvesting filters
    """
    print("\n" + "="*80)
    print("🎯 DIRECTIONAL FRY HARVESTING COMPARISON")
    print("Same manipulation technique, different harvesting targets")
    print("="*80)
    
    results_comparison = []
    
    # Test both harvesting strategies
    harvesting_strategies = [
        ("REKT LONGS ONLY", "rekt_longs_only"),
        ("REKT SHORTS ONLY", "rekt_shorts_only"),
        ("ALL POSITIONS", None)  # Control group
    ]
    
    for strategy_name, harvesting_filter in harvesting_strategies:
        print("\n🔄 Testing: {}".format(strategy_name))
        print("-" * 50)
        
        # Fresh CDO and manipulator for each test
        cdo = RektDarkCDO()
        manipulator = DarkPoolManipulator(cdo, initial_capital=100_000_000)
        
        # Set harvesting filter on CDO
        original_sweep = cdo.sweep_collateral
        def filtered_sweep(*args, **kwargs):
            kwargs['harvesting_filter'] = harvesting_filter
            return original_sweep(*args, **kwargs)
        cdo.sweep_collateral = filtered_sweep
        
        # Execute same directional squeeze (pump from 45k to 55k)
        results = manipulator.execute_directional_squeeze(target_price=55000, steps=15)
        
        # Collect metrics
        strategy_metrics = {
            "strategy_name": strategy_name,
            "harvesting_filter": harvesting_filter,
            "total_fry_minted": results["fry_minted"],
            "total_collateral_absorbed": results["collateral_absorbed"],
            "liquidation_count": len(results["liquidations"]),
            "manipulation_cost": results["manipulation_cost"],
            "fry_per_dollar_cost": results["fry_minted"] / max(results["manipulation_cost"], 1),
            "avg_fry_per_liquidation": results["fry_minted"] / max(len(results["liquidations"]), 1),
            "capital_efficiency": results["fry_minted"] / max(results["collateral_absorbed"], 1)
        }
        
        # Analyze position types liquidated
        long_liquidations = sum(1 for liq in results["liquidations"] if "long" in str(liq).lower())
        short_liquidations = len(results["liquidations"]) - long_liquidations
        
        strategy_metrics["long_liquidations"] = long_liquidations
        strategy_metrics["short_liquidations"] = short_liquidations
        strategy_metrics["long_vs_short_ratio"] = long_liquidations / max(short_liquidations, 1)
        
        results_comparison.append(strategy_metrics)
        
        # Print immediate results
        print("   💰 FRY Minted: {:,.2f}".format(strategy_metrics['total_fry_minted']))
        print("   📊 Liquidations: {} ({} longs, {} shorts)".format(strategy_metrics['liquidation_count'], long_liquidations, short_liquidations))
        print("   💸 Collateral Absorbed: ${:,.2f}".format(strategy_metrics['total_collateral_absorbed']))
        print("   ⚡ FRY per $ Cost: {:.2f}".format(strategy_metrics['fry_per_dollar_cost']))
        print("   🎯 Capital Efficiency: {:.2f}".format(strategy_metrics['capital_efficiency']))
    
    # Comparative Analysis
    print("\n📈 COMPARATIVE ANALYSIS")
    print("=" * 50)
    
    # Find best performing strategy
    best_fry_yield = max(results_comparison, key=lambda x: x['total_fry_minted'])
    best_efficiency = max(results_comparison, key=lambda x: x['capital_efficiency'])
    best_cost_ratio = max(results_comparison, key=lambda x: x['fry_per_dollar_cost'])
    
    print("🏆 Highest FRY Yield: {}".format(best_fry_yield['strategy_name']))
    print("   └─ {:,.2f} FRY minted".format(best_fry_yield['total_fry_minted']))
    
    print("⚡ Best Capital Efficiency: {}".format(best_efficiency['strategy_name']))
    print("   └─ {:.2f} FRY per $ absorbed".format(best_efficiency['capital_efficiency']))
    
    print("💰 Best Cost Ratio: {}".format(best_cost_ratio['strategy_name']))
    print("   └─ {:.2f} FRY per $ manipulation cost".format(best_cost_ratio['fry_per_dollar_cost']))
    
    # Market dynamics analysis
    print("\n🌊 MARKET DYNAMICS")
    print("-" * 30)
    
    for result in results_comparison:
        print("{}:".format(result['strategy_name']))
        print("   Long/Short Liquidation Ratio: {:.2f}".format(result['long_vs_short_ratio']))
        print("   Average FRY per Liquidation: {:,.2f}".format(result['avg_fry_per_liquidation']))
    
    # Export comparison results
    comparison_export = {
        "comparison_timestamp": datetime.now().isoformat(),
        "manipulation_technique": "directional_squeeze_45k_to_55k",
        "harvesting_strategies_tested": len(harvesting_strategies),
        "results": results_comparison,
        "best_performers": {
            "highest_fry_yield": best_fry_yield['strategy_name'],
            "best_capital_efficiency": best_efficiency['strategy_name'],
            "best_cost_ratio": best_cost_ratio['strategy_name']
        }
    }
    
    with open('directional_fry_harvesting_comparison.json', 'w') as f:
        json.dump(comparison_export, f, indent=2, default=str)
    
    print("\n💾 Comparison results exported to 'directional_fry_harvesting_comparison.json'")
    print("✅ Directional FRY harvesting analysis complete!")
    
    return results_comparison

if __name__ == "__main__":
    # Run original manipulation simulation
    main()
    
    # Run new directional harvesting comparison
    compare_directional_fry_harvesting()
