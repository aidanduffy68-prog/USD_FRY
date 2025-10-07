# -*- coding: utf-8 -*-
"""
FRY Core v2: System Orchestrator
Main coordination layer for all FRY v2 components
"""

import json
import time
import logging
from datetime import datetime

# Import v2 components
from v2_slippage_engine import CrossVenueSlippageEngine
from v2_circuit_breaker import CircuitBreakerSystem
from v2_liquidity_paradox import LiquidityParadoxEngine
from simple_dark_cdo import RektDarkCDO

logger = logging.getLogger(__name__)

class FRYCoreV2:
    """
    FRY Core v2: Integrated system orchestrator
    
    Coordinates slippage estimation, circuit breakers, paradox detection,
    and FRY minting for funding rate arbitrage
    """
    
    def __init__(self, config=None):
        self.config = config or self._default_config()
        
        # Initialize core components
        self.slippage_engine = CrossVenueSlippageEngine()
        self.circuit_breaker = CircuitBreakerSystem(self.config.get("circuit_breaker"))
        self.paradox_engine = LiquidityParadoxEngine(self.config.get("paradox"))
        self.dark_cdo = RektDarkCDO()
        
        # System state
        self.total_arbitrage_volume = 0
        self.active_positions = []
        self.system_start_time = time.time()
        
        logger.info("FRY Core v2 initialized with all components")
    
    def _default_config(self):
        """Default system configuration"""
        return {
            "circuit_breaker": {
                "inflow_baseline": 50000,
                "inflow_multiplier": 5.0,
                "inflow_window": 10,
                "paradox_threshold": 85
            },
            "paradox": {
                "baseline_liquidity": 1000000,
                "paradox_threshold": 0.75,
                "feedback_multiplier": 2.5
            },
            "arbitrage": {
                "min_spread_threshold": 0.002,  # 0.2%
                "max_position_size": 100000,    # $100k
                "slippage_tolerance": 0.05      # 5%
            }
        }
    
    def scan_arbitrage_opportunities(self, coins):
        """Scan for funding rate arbitrage opportunities"""
        
        opportunities = []
        
        for coin in coins:
            # Simulate funding rates (in production, fetch from APIs)
            funding_rates = self._simulate_funding_rates(coin)
            
            if self._has_arbitrage_opportunity(funding_rates):
                opportunity = self._analyze_arbitrage_opportunity(coin, funding_rates)
                if opportunity:
                    opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x["net_profit_usd"], reverse=True)
    
    def _simulate_funding_rates(self, coin):
        """Simulate funding rates across venues"""
        import random
        base_rate = random.uniform(-0.01, 0.01)
        
        return {
            "binance": base_rate + random.uniform(-0.005, 0.005),
            "okx": base_rate + random.uniform(-0.008, 0.008),
            "bybit": base_rate + random.uniform(-0.006, 0.006),
            "kucoin": base_rate + random.uniform(-0.01, 0.01)
        }
    
    def _has_arbitrage_opportunity(self, funding_rates):
        """Check if spread exceeds minimum threshold"""
        rates = list(funding_rates.values())
        spread = max(rates) - min(rates)
        return spread > self.config["arbitrage"]["min_spread_threshold"]
    
    def _analyze_arbitrage_opportunity(self, coin, funding_rates):
        """Analyze arbitrage opportunity with v2 components"""
        
        rates = list(funding_rates.values())
        spread = max(rates) - min(rates)
        
        # Position sizing
        market_cap = coin.get("market_cap_usd", 1000000)
        max_size = self.config["arbitrage"]["max_position_size"]
        position_size = min(max_size, market_cap * 0.01)
        
        # Get slippage estimate from v2 engine
        slippage_estimate = self.slippage_engine.estimate_slippage(
            coin["symbol"], position_size, market_cap
        )
        
        # Calculate profitability
        gross_profit = spread * position_size
        slippage_cost = (slippage_estimate.total_cost_pct / 100) * position_size
        net_profit = gross_profit - slippage_cost
        
        # Check slippage tolerance
        slippage_ratio = slippage_cost / position_size
        if slippage_ratio > self.config["arbitrage"]["slippage_tolerance"]:
            logger.debug("Rejecting {} - slippage too high: {:.2%}".format(
                coin["symbol"], slippage_ratio
            ))
            return None
        
        return {
            "coin": coin["symbol"],
            "market_cap": market_cap,
            "funding_spread": spread,
            "position_size_usd": position_size,
            "gross_profit_usd": gross_profit,
            "slippage_cost_usd": slippage_cost,
            "net_profit_usd": net_profit,
            "profit_margin_pct": (net_profit / position_size) * 100,
            "slippage_estimate": slippage_estimate.to_dict(),
            "funding_rates": funding_rates
        }
    
    def execute_arbitrage_position(self, opportunity):
        """Execute arbitrage position with full v2 system integration"""
        
        # Check circuit breaker first
        if self.circuit_breaker.active:
            logger.warning("Circuit breaker active - blocking execution")
            return {"status": "blocked", "reason": "circuit_breaker_active"}
        
        # Calculate current paradox score
        current_liquidity = self._estimate_current_liquidity()
        paradox_metrics = self.paradox_engine.calculate_paradox_score(
            current_liquidity=current_liquidity,
            arbitrage_volume=self.total_arbitrage_volume,
            time_window_minutes=10,
            additional_metrics={
                "unique_assets": len(set(pos["coin"] for pos in self.active_positions)),
                "volatility_factor": 1.2,  # Could be calculated from market data
                "cross_venue_spread": opportunity["funding_spread"]
            }
        )
        
        # Check if circuit breaker should trigger
        should_trigger, trigger_events = self.circuit_breaker.should_trigger(
            paradox_score=paradox_metrics.paradox_score
        )
        
        if should_trigger:
            self.circuit_breaker.activate(trigger_events)
            logger.critical("Circuit breaker triggered during execution")
            return {"status": "blocked", "reason": "circuit_breaker_triggered", "events": [e.to_dict() for e in trigger_events]}
        
        # Record inflow for monitoring
        self.circuit_breaker.record_inflow(opportunity["position_size_usd"])
        
        # Calculate FRY minting based on slippage (v2 approach)
        fry_minted = self._calculate_slippage_based_fry_v2(opportunity, paradox_metrics)
        
        # Execute position
        position = self._create_position(opportunity)
        
        # Sweep into dark pool with v2 FRY calculation
        collateral_id, actual_fry = self.dark_cdo.sweep_collateral(
            trader_address=position["id"],
            loss_amount_usd=opportunity["slippage_cost_usd"],
            asset=opportunity["coin"],
            leverage=1.0,
            position_size_usd=opportunity["position_size_usd"],
            liquidation=False,
            fry_override=fry_minted
        )
        
        # Update system state
        self.active_positions.append(position)
        self.total_arbitrage_volume += opportunity["position_size_usd"]
        
        logger.info("v2 Arbitrage executed: {} | Profit: ${:,.2f} | FRY: {:,.0f} | Paradox: {:.1f}".format(
            opportunity["coin"], opportunity["net_profit_usd"], actual_fry, paradox_metrics.paradox_score
        ))
        
        return {
            "status": "executed",
            "position": position,
            "fry_minted": actual_fry,
            "collateral_id": collateral_id,
            "paradox_score": paradox_metrics.paradox_score,
            "slippage_data": opportunity["slippage_estimate"],
            "execution_timestamp": int(time.time() * 1000)
        }
    
    def _calculate_slippage_based_fry_v2(self, opportunity, paradox_metrics):
        """v2 FRY calculation with paradox adjustment"""
        
        slippage_cost = opportunity["slippage_cost_usd"]
        position_size = opportunity["position_size_usd"]
        
        # Base FRY: 1 FRY per $1 slippage
        base_fry = slippage_cost * 1.0
        
        # Slippage severity multiplier
        slippage_pct = opportunity["slippage_estimate"]["estimated_total_cost_pct"]
        severity_multiplier = 1.0 + (slippage_pct / 10.0)
        
        # Position size factor
        size_factor = 1.0 + min(0.5, position_size / 1000000)
        
        # v2: Paradox adjustment - higher paradox = more FRY to discourage activity
        paradox_multiplier = 1.0 + (paradox_metrics.paradox_score / 100.0)
        
        # v2: Market concentration penalty
        unique_assets = len(set(pos["coin"] for pos in self.active_positions))
        concentration_penalty = max(1.0, 5.0 / max(unique_assets, 1))
        
        total_fry = base_fry * severity_multiplier * size_factor * paradox_multiplier * concentration_penalty
        
        return total_fry
    
    def _create_position(self, opportunity):
        """Create position record"""
        import hashlib
        
        position_id = hashlib.sha256("v2_arb_{}".format(time.time()).encode()).hexdigest()[:16]
        
        return {
            "id": position_id,
            "coin": opportunity["coin"],
            "position_size_usd": opportunity["position_size_usd"],
            "expected_profit": opportunity["net_profit_usd"],
            "slippage_cost": opportunity["slippage_cost_usd"],
            "funding_spread": opportunity["funding_spread"],
            "timestamp": int(time.time() * 1000),
            "status": "active"
        }
    
    def _estimate_current_liquidity(self):
        """Estimate current market liquidity"""
        base_liquidity = self.config["paradox"]["baseline_liquidity"]
        liquidity_drain = min(0.8, self.total_arbitrage_volume / base_liquidity)
        return base_liquidity * (1 - liquidity_drain)
    
    def get_system_status(self):
        """Get comprehensive v2 system status"""
        
        current_liquidity = self._estimate_current_liquidity()
        
        # Get paradox metrics
        paradox_metrics = self.paradox_engine.calculate_paradox_score(
            current_liquidity=current_liquidity,
            arbitrage_volume=self.total_arbitrage_volume,
            time_window_minutes=10
        )
        
        return {
            "system_version": "v2",
            "uptime_minutes": (time.time() - self.system_start_time) / 60,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "liquidity_paradox": paradox_metrics.to_dict(),
            "slippage_engine": self.slippage_engine.get_system_stats(),
            "dark_cdo": self.dark_cdo.get_market_stats(),
            "arbitrage_metrics": {
                "total_volume": self.total_arbitrage_volume,
                "active_positions": len(self.active_positions),
                "current_liquidity_estimate": current_liquidity,
                "unique_assets": len(set(pos["coin"] for pos in self.active_positions))
            }
        }
    
    def get_health_check(self):
        """Get system health assessment"""
        
        circuit_health = self.circuit_breaker.get_health_check()
        paradox_risk = self.paradox_engine.get_risk_assessment()
        venue_health = self.slippage_engine.get_venue_health_score()
        
        # Overall health score (0-100)
        paradox_score = paradox_risk.get("current_score", 0)
        health_components = [
            circuit_health["health_score"] * 0.4,  # 40% weight
            (100 - paradox_score) * 0.3,  # 30% weight (inverse paradox)
            sum(venue_health.values()) / len(venue_health) * 0.3  # 30% weight
        ]
        
        overall_health = sum(health_components)
        
        if overall_health >= 80:
            status = "HEALTHY"
        elif overall_health >= 60:
            status = "CAUTION"
        elif overall_health >= 40:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        return {
            "overall_health_score": overall_health,
            "status": status,
            "components": {
                "circuit_breaker": circuit_health,
                "paradox_risk": paradox_risk,
                "venue_health": venue_health
            },
            "recommendations": self._get_health_recommendations(overall_health, circuit_health, paradox_risk)
        }
    
    def _get_health_recommendations(self, overall_health, circuit_health, paradox_risk):
        """Generate health-based recommendations"""
        
        recommendations = []
        
        if overall_health < 50:
            recommendations.append("URGENT: System health critical - consider emergency shutdown")
        
        if circuit_health["status"] == "CRITICAL":
            recommendations.append("Circuit breaker active - resolve trigger conditions")
        elif circuit_health["status"] == "WARNING":
            recommendations.append("Circuit breaker approaching limits - reduce activity")
        
        if paradox_risk["risk_level"] in ["high", "critical"]:
            recommendations.append("Liquidity paradox risk elevated - {}".format(paradox_risk["recommendation"]))
        
        if not recommendations:
            recommendations.append("System operating normally - continue monitoring")
        
        return recommendations
    
    def export_system_report(self, filename=None):
        """Export comprehensive system report"""
        
        if not filename:
            filename = "fry_core_v2_report_{}.json".format(int(time.time()))
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "system_version": "v2",
            "system_status": self.get_system_status(),
            "health_check": self.get_health_check(),
            "active_positions": self.active_positions,
            "configuration": self.config
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("System report exported to: {}".format(filename))
        return filename

def simulate_low_liquidity_coins():
    """Generate test coins for v2 system"""
    return [
        {"symbol": "REKT", "market_cap_usd": 5000000},
        {"symbol": "COPE", "market_cap_usd": 2000000},
        {"symbol": "YOLO", "market_cap_usd": 8000000},
        {"symbol": "FOMO", "market_cap_usd": 1500000},
        {"symbol": "HODL", "market_cap_usd": 12000000},
        {"symbol": "MOON", "market_cap_usd": 3000000}
    ]

def main():
    """Demo FRY Core v2 system"""
    
    print("🚀 FRY Core v2 System")
    print("=" * 60)
    
    # Initialize v2 system
    fry_v2 = FRYCoreV2()
    
    # Get initial system status
    print("📊 Initial System Status:")
    health = fry_v2.get_health_check()
    print("  Overall Health: {}/100 ({})".format(int(health["overall_health_score"]), health["status"]))
    
    # Scan opportunities
    coins = simulate_low_liquidity_coins()
    print("\n🔍 Scanning {} coins for arbitrage opportunities...".format(len(coins)))
    
    opportunities = fry_v2.scan_arbitrage_opportunities(coins)
    
    print("\n💰 Top v2 Arbitrage Opportunities:")
    for i, opp in enumerate(opportunities[:3], 1):
        print("{}. {} | Spread: {:.3f}% | Net Profit: ${:,.2f} | Slippage: {:.2f}%".format(
            i, opp["coin"], opp["funding_spread"]*100, 
            opp["net_profit_usd"], opp["slippage_estimate"]["estimated_total_cost_pct"]
        ))
    
    # Execute positions
    print("\n⚡ Executing v2 arbitrage positions...")
    executed_count = 0
    
    for opp in opportunities:
        if opp["net_profit_usd"] > 0:  # Only profitable opportunities
            result = fry_v2.execute_arbitrage_position(opp)
            
            if result["status"] == "executed":
                executed_count += 1
                print("  ✅ {} executed | FRY: {:,.0f} | Paradox: {:.1f}".format(
                    opp["coin"], result["fry_minted"], result["paradox_score"]
                ))
            else:
                print("  ❌ {} blocked: {}".format(opp["coin"], result["reason"]))
                break  # Stop if circuit breaker triggers
    
    # Final system status
    print("\n📈 Final v2 System Status:")
    final_status = fry_v2.get_system_status()
    final_health = fry_v2.get_health_check()
    
    print("  Positions Executed: {}".format(executed_count))
    print("  Total Arbitrage Volume: ${:,.0f}".format(final_status["arbitrage_metrics"]["total_volume"]))
    print("  Circuit Breaker: {}".format("🔴 ACTIVE" if final_status["circuit_breaker"]["active"] else "🟢 INACTIVE"))
    print("  Paradox Score: {:.1f}/100".format(final_status["liquidity_paradox"]["paradox_score"]))
    print("  System Health: {}/100 ({})".format(int(final_health["overall_health_score"]), final_health["status"]))
    print("  FRY Minted: {:,.0f}".format(final_status["dark_cdo"]["total_fry_minted"]))
    
    # Export report
    report_file = fry_v2.export_system_report()
    print("\n💾 System report exported: {}".format(report_file))
    print("✅ FRY Core v2 demonstration complete!")

if __name__ == "__main__":
    main()
