# -*- coding: utf-8 -*-
"""
FRY Funding Rate Arbitrage Engine
Arbitrages funding rates across venues for low liquidity coins using FRY dark pool
with slippage-based minting and circuit breakers
"""

import json
import time
import hashlib
import logging
import random
from datetime import datetime, timedelta
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiquidityParadoxIndex:
    """
    Models theoretical liquidity paradox - when arbitrage opportunities 
    increase as liquidity decreases, creating feedback loops
    """
    
    def __init__(self):
        self.baseline_liquidity = 1000000  # $1M baseline
        self.paradox_threshold = 0.75  # Paradox triggers at 75% liquidity drain
        self.feedback_multiplier = 2.5
        
    def calculate_paradox_score(self, current_liquidity, arbitrage_volume, time_window_minutes):
        """Calculate liquidity paradox index (0-100 scale)"""
        
        # Liquidity drain ratio
        liquidity_ratio = current_liquidity / self.baseline_liquidity
        drain_factor = max(0, 1 - liquidity_ratio)
        
        # Arbitrage intensity (volume per minute)
        arbitrage_intensity = arbitrage_volume / max(time_window_minutes, 1)
        
        # Paradox emerges when high arbitrage meets low liquidity
        paradox_base = (drain_factor * arbitrage_intensity) / 10000
        
        # Feedback loop amplification
        if drain_factor > self.paradox_threshold:
            feedback_amplification = self.feedback_multiplier * (drain_factor - self.paradox_threshold)
            paradox_base *= (1 + feedback_amplification)
        
        # Scale to 0-100
        paradox_score = min(100, paradox_base * 100)
        
        return {
            "paradox_score": paradox_score,
            "liquidity_ratio": liquidity_ratio,
            "drain_factor": drain_factor,
            "arbitrage_intensity": arbitrage_intensity,
            "feedback_active": drain_factor > self.paradox_threshold
        }

class CrossVenueSlippageModel:
    """
    Models slippage across multiple venues for low liquidity coins
    """
    
    def __init__(self):
        self.venues = {
            "binance": {"liquidity_depth": 0.4, "fee_rate": 0.001},
            "okx": {"liquidity_depth": 0.25, "fee_rate": 0.0008},
            "bybit": {"liquidity_depth": 0.2, "fee_rate": 0.001},
            "kucoin": {"liquidity_depth": 0.15, "fee_rate": 0.001}
        }
        
    def estimate_slippage(self, coin_symbol, trade_size_usd, market_cap_usd):
        """Estimate cross-venue slippage for a trade"""
        
        # Base slippage increases with trade size relative to market cap
        size_impact = trade_size_usd / max(market_cap_usd, 1000000)  # Min $1M cap
        
        venue_slippages = {}
        total_weighted_slippage = 0
        total_weight = 0
        
        for venue, params in self.venues.items():
            # Venue-specific slippage calculation
            depth_factor = 1 / params["liquidity_depth"]  # Lower depth = higher slippage
            fee_impact = params["fee_rate"] * 2  # Round trip fees
            
            # Slippage formula: size impact * depth factor + fees + random market noise
            base_slippage = size_impact * depth_factor * 100  # Convert to percentage
            noise_factor = random.uniform(0.8, 1.2)  # Market noise
            
            venue_slippage = (base_slippage + fee_impact * 100) * noise_factor
            venue_slippages[venue] = venue_slippage
            
            # Weight by liquidity depth for aggregate calculation
            weight = params["liquidity_depth"]
            total_weighted_slippage += venue_slippage * weight
            total_weight += weight
        
        aggregate_slippage = total_weighted_slippage / total_weight if total_weight > 0 else 0
        
        return {
            "aggregate_slippage_pct": aggregate_slippage,
            "venue_slippages": venue_slippages,
            "size_impact_factor": size_impact,
            "estimated_total_cost_pct": aggregate_slippage
        }

class FundingRateArbitrageEngine:
    """
    Core arbitrage engine for funding rate opportunities
    """
    
    def __init__(self, dark_pool_cdo):
        self.cdo = dark_pool_cdo
        self.slippage_model = CrossVenueSlippageModel()
        self.paradox_index = LiquidityParadoxIndex()
        
        # Circuit breaker parameters
        self.circuit_breaker_active = False
        self.baseline_inflow_rate = 50000  # $50k/minute baseline
        self.circuit_multiplier = 5.0  # Trigger at 5x baseline
        self.circuit_time_window = 10  # 10 minute window
        self.paradox_circuit_threshold = 85  # Paradox score threshold
        
        # Funding rate tracking
        self.funding_positions = []
        self.total_arbitrage_volume = 0
        self.inflow_history = []
        
    def scan_funding_opportunities(self, low_liquidity_coins):
        """Scan for funding rate arbitrage opportunities"""
        
        opportunities = []
        
        for coin in low_liquidity_coins:
            # Simulate funding rate data (in real implementation, fetch from APIs)
            funding_rates = self._simulate_funding_rates(coin)
            
            # Find arbitrage opportunities
            if self._has_arbitrage_opportunity(funding_rates):
                opportunity = self._calculate_arbitrage_metrics(coin, funding_rates)
                opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x["expected_profit_usd"], reverse=True)
    
    def _simulate_funding_rates(self, coin):
        """Simulate funding rates across venues (replace with real API calls)"""
        
        base_rate = random.uniform(-0.01, 0.01)  # -1% to +1%
        
        return {
            "binance": base_rate + random.uniform(-0.005, 0.005),
            "okx": base_rate + random.uniform(-0.008, 0.008),
            "bybit": base_rate + random.uniform(-0.006, 0.006),
            "kucoin": base_rate + random.uniform(-0.01, 0.01)
        }
    
    def _has_arbitrage_opportunity(self, funding_rates, min_spread=0.002):
        """Check if funding rate spread exceeds minimum threshold"""
        rates = list(funding_rates.values())
        spread = max(rates) - min(rates)
        return spread > min_spread
    
    def _calculate_arbitrage_metrics(self, coin, funding_rates):
        """Calculate expected profit and risk metrics for arbitrage"""
        
        rates = list(funding_rates.values())
        max_rate = max(rates)
        min_rate = min(rates)
        spread = max_rate - min_rate
        
        # Position sizing based on coin liquidity
        position_size_usd = min(100000, coin.get("market_cap_usd", 1000000) * 0.01)
        
        # Calculate slippage impact
        slippage_data = self.slippage_model.estimate_slippage(
            coin["symbol"], 
            position_size_usd, 
            coin.get("market_cap_usd", 1000000)
        )
        
        # Expected profit = spread * position size - slippage costs
        gross_profit = spread * position_size_usd
        slippage_cost = (slippage_data["estimated_total_cost_pct"] / 100) * position_size_usd
        net_profit = gross_profit - slippage_cost
        
        return {
            "coin": coin["symbol"],
            "funding_spread": spread,
            "position_size_usd": position_size_usd,
            "expected_profit_usd": net_profit,
            "slippage_cost_usd": slippage_cost,
            "profit_margin_pct": (net_profit / position_size_usd) * 100,
            "slippage_data": slippage_data,
            "funding_rates": funding_rates
        }
    
    def execute_arbitrage_position(self, opportunity):
        """Execute funding rate arbitrage position"""
        
        if self.circuit_breaker_active:
            logger.warning("Circuit breaker active - blocking arbitrage execution")
            return None
        
        # Check circuit breaker conditions
        if self._should_trigger_circuit_breaker(opportunity["position_size_usd"]):
            self._activate_circuit_breaker()
            return None
        
        # Execute the arbitrage
        position = self._open_arbitrage_position(opportunity)
        
        # Calculate FRY minting based on SLIPPAGE, not raw PnL
        fry_minted = self._calculate_slippage_based_fry(opportunity)
        
        # Record position and mint FRY
        self.funding_positions.append(position)
        self.total_arbitrage_volume += opportunity["position_size_usd"]
        
        # Sweep into dark pool with slippage-based minting
        collateral_id, actual_fry = self.cdo.sweep_collateral(
            trader_address=position["trader_hash"],
            loss_amount_usd=opportunity["slippage_cost_usd"],  # Use slippage as "loss"
            asset=opportunity["coin"],
            leverage=1.0,  # Funding arbitrage typically unlevered
            position_size_usd=opportunity["position_size_usd"],
            liquidation=False,
            fry_override=fry_minted  # Override with slippage-based calculation
        )
        
        logger.info("Arbitrage executed: {} | Profit: ${:,.2f} | FRY minted: {:,.0f}".format(
            opportunity["coin"], opportunity["expected_profit_usd"], actual_fry
        ))
        
        return {
            "position": position,
            "fry_minted": actual_fry,
            "collateral_id": collateral_id,
            "execution_timestamp": int(time.time() * 1000)
        }
    
    def _calculate_slippage_based_fry(self, opportunity):
        """Calculate FRY minting based on slippage estimate, not raw PnL"""
        
        slippage_cost = opportunity["slippage_cost_usd"]
        position_size = opportunity["position_size_usd"]
        
        # Base FRY rate: 1 FRY per $1 of slippage cost
        base_fry = slippage_cost * 1.0
        
        # Slippage severity multiplier (higher slippage = more FRY)
        slippage_pct = opportunity["slippage_data"]["estimated_total_cost_pct"]
        severity_multiplier = 1.0 + (slippage_pct / 10.0)  # +10% FRY per 1% slippage
        
        # Position size factor (larger positions get slight bonus)
        size_factor = 1.0 + min(0.5, position_size / 1000000)  # Max 50% bonus for $1M+ positions
        
        total_fry = base_fry * severity_multiplier * size_factor
        
        return total_fry
    
    def _open_arbitrage_position(self, opportunity):
        """Simulate opening arbitrage position"""
        
        trader_hash = hashlib.sha256("funding_arb_{}".format(time.time()).encode()).hexdigest()[:16]
        
        return {
            "id": trader_hash,
            "trader_hash": trader_hash,
            "coin": opportunity["coin"],
            "position_size_usd": opportunity["position_size_usd"],
            "funding_spread": opportunity["funding_spread"],
            "expected_profit": opportunity["expected_profit_usd"],
            "slippage_cost": opportunity["slippage_cost_usd"],
            "timestamp": int(time.time() * 1000),
            "status": "active"
        }
    
    def _should_trigger_circuit_breaker(self, new_inflow_usd):
        """Check if circuit breaker should be triggered"""
        
        current_time = time.time()
        
        # Add new inflow to history
        self.inflow_history.append({
            "amount": new_inflow_usd,
            "timestamp": current_time
        })
        
        # Clean old entries (outside time window)
        cutoff_time = current_time - (self.circuit_time_window * 60)
        self.inflow_history = [
            entry for entry in self.inflow_history 
            if entry["timestamp"] > cutoff_time
        ]
        
        # Calculate inflow rate
        total_inflow = sum(entry["amount"] for entry in self.inflow_history)
        inflow_rate = total_inflow / self.circuit_time_window  # Per minute
        
        # Check rate threshold
        rate_exceeded = inflow_rate > (self.baseline_inflow_rate * self.circuit_multiplier)
        
        # Check liquidity paradox
        current_liquidity = self._estimate_current_liquidity()
        paradox_data = self.paradox_index.calculate_paradox_score(
            current_liquidity, 
            self.total_arbitrage_volume, 
            self.circuit_time_window
        )
        
        paradox_triggered = paradox_data["paradox_score"] > self.paradox_circuit_threshold
        
        if rate_exceeded or paradox_triggered:
            logger.warning("Circuit breaker conditions met:")
            logger.warning("  Inflow rate: ${:,.0f}/min (threshold: ${:,.0f}/min)".format(
                inflow_rate, self.baseline_inflow_rate * self.circuit_multiplier
            ))
            logger.warning("  Paradox score: {:.1f} (threshold: {})".format(
                paradox_data["paradox_score"], self.paradox_circuit_threshold
            ))
            return True
        
        return False
    
    def _activate_circuit_breaker(self):
        """Activate circuit breaker to halt FRY minting"""
        
        self.circuit_breaker_active = True
        
        logger.critical("🚨 CIRCUIT BREAKER ACTIVATED 🚨")
        logger.critical("FRY minting halted due to liquidity paradox conditions")
        logger.critical("Manual intervention required to reset")
        
        # In production, this would trigger alerts, notifications, etc.
    
    def _estimate_current_liquidity(self):
        """Estimate current market liquidity (simplified)"""
        
        # In real implementation, this would aggregate liquidity from multiple sources
        base_liquidity = self.paradox_index.baseline_liquidity
        
        # Reduce liquidity based on recent arbitrage volume
        liquidity_drain = min(0.8, self.total_arbitrage_volume / base_liquidity)
        current_liquidity = base_liquidity * (1 - liquidity_drain)
        
        return current_liquidity
    
    def reset_circuit_breaker(self, admin_override=False):
        """Reset circuit breaker (requires admin override)"""
        
        if not admin_override:
            logger.error("Circuit breaker reset requires admin override")
            return False
        
        self.circuit_breaker_active = False
        self.inflow_history = []
        
        logger.info("Circuit breaker reset by admin override")
        return True
    
    def get_system_status(self):
        """Get current system status and metrics"""
        
        current_liquidity = self._estimate_current_liquidity()
        paradox_data = self.paradox_index.calculate_paradox_score(
            current_liquidity,
            self.total_arbitrage_volume,
            self.circuit_time_window
        )
        
        # Calculate recent inflow rate
        current_time = time.time()
        cutoff_time = current_time - (self.circuit_time_window * 60)
        recent_inflows = [
            entry for entry in self.inflow_history 
            if entry["timestamp"] > cutoff_time
        ]
        recent_inflow_rate = sum(entry["amount"] for entry in recent_inflows) / self.circuit_time_window
        
        return {
            "circuit_breaker_active": self.circuit_breaker_active,
            "total_positions": len(self.funding_positions),
            "total_arbitrage_volume": self.total_arbitrage_volume,
            "current_liquidity_estimate": current_liquidity,
            "liquidity_paradox": paradox_data,
            "recent_inflow_rate_per_minute": recent_inflow_rate,
            "inflow_threshold": self.baseline_inflow_rate * self.circuit_multiplier,
            "active_positions": len([p for p in self.funding_positions if p["status"] == "active"])
        }

def simulate_low_liquidity_coins():
    """Generate sample low liquidity coins for testing"""
    
    coins = [
        {"symbol": "REKT", "market_cap_usd": 5000000},
        {"symbol": "COPE", "market_cap_usd": 2000000},
        {"symbol": "YOLO", "market_cap_usd": 8000000},
        {"symbol": "FOMO", "market_cap_usd": 1500000},
        {"symbol": "HODL", "market_cap_usd": 12000000}
    ]
    
    return coins

def main():
    """Demo the funding rate arbitrage system"""
    
    print("🚀 FRY Funding Rate Arbitrage Engine")
    print("=" * 60)
    
    # Import simple CDO
    from simple_dark_cdo import RektDarkCDO
    cdo = RektDarkCDO()
    
    # Initialize arbitrage engine
    arb_engine = FundingRateArbitrageEngine(cdo)
    
    # Simulate low liquidity coins
    coins = simulate_low_liquidity_coins()
    
    print("📊 Scanning funding opportunities...")
    opportunities = arb_engine.scan_funding_opportunities(coins)
    
    print("\n💰 Top Arbitrage Opportunities:")
    for i, opp in enumerate(opportunities[:3], 1):
        print("{}. {} | Spread: {:.3f}% | Profit: ${:,.2f} | Slippage: ${:,.2f}".format(
            i, opp["coin"], opp["funding_spread"]*100, 
            opp["expected_profit_usd"], opp["slippage_cost_usd"]
        ))
    
    # Execute top opportunities
    print("\n⚡ Executing arbitrage positions...")
    executed_positions = []
    
    for opp in opportunities[:3]:
        result = arb_engine.execute_arbitrage_position(opp)
        if result:
            executed_positions.append(result)
        
        # Check system status after each execution
        status = arb_engine.get_system_status()
        if status["circuit_breaker_active"]:
            print("🚨 Circuit breaker activated - stopping execution")
            break
    
    # Final system status
    print("\n📈 Final System Status:")
    status = arb_engine.get_system_status()
    
    print("  Circuit Breaker: {}".format("🔴 ACTIVE" if status["circuit_breaker_active"] else "🟢 INACTIVE"))
    print("  Total Positions: {}".format(status["total_positions"]))
    print("  Arbitrage Volume: ${:,.0f}".format(status["total_arbitrage_volume"]))
    print("  Liquidity Estimate: ${:,.0f}".format(status["current_liquidity_estimate"]))
    print("  Paradox Score: {:.1f}/100".format(status["liquidity_paradox"]["paradox_score"]))
    print("  Inflow Rate: ${:,.0f}/min (threshold: ${:,.0f}/min)".format(
        status["recent_inflow_rate_per_minute"], status["inflow_threshold"]
    ))
    
    # Export results
    export_data = {
        "execution_timestamp": datetime.now().isoformat(),
        "opportunities_found": len(opportunities),
        "positions_executed": len(executed_positions),
        "system_status": status,
        "executed_positions": executed_positions
    }
    
    with open('fry_funding_arbitrage_results.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print("\n💾 Results exported to 'fry_funding_arbitrage_results.json'")
    print("✅ Funding arbitrage simulation complete!")

if __name__ == "__main__":
    main()
