# -*- coding: utf-8 -*-
"""
FRY vs Traditional Funding Arbitrage Comparison Engine
Comprehensive analysis of both arbitrage approaches for the same coin
"""

import json
import time
import random
import logging
from datetime import datetime

# Import v2 components
from v2_slippage_engine import CrossVenueSlippageEngine
from v2_circuit_breaker import CircuitBreakerSystem
from v2_liquidity_paradox import LiquidityParadoxEngine

logger = logging.getLogger(__name__)

class TraditionalArbitrageEngine:
    """
    Traditional funding rate arbitrage engine for comparison
    """
    
    def __init__(self):
        self.slippage_engine = CrossVenueSlippageEngine()
        self.total_capital_deployed = 0
        self.positions = []
        
    def analyze_traditional_opportunity(self, coin, funding_rates, position_size_usd):
        """Analyze traditional arbitrage opportunity"""
        
        rates = list(funding_rates.values())
        spread = max(rates) - min(rates)
        
        # Find best long/short venues
        sorted_rates = sorted(funding_rates.items(), key=lambda x: x[1])
        short_venue = sorted_rates[-1][0]  # Highest rate (short here)
        long_venue = sorted_rates[0][0]   # Lowest rate (long here)
        
        # Calculate slippage for both sides
        market_cap = coin.get("market_cap_usd", 1000000)
        slippage_estimate = self.slippage_engine.estimate_slippage(
            coin["symbol"], position_size_usd, market_cap
        )
        
        # Traditional calculation: focus on net profit
        gross_profit = spread * position_size_usd  # 8-hour funding period
        total_slippage_cost = (slippage_estimate.total_cost_pct / 100) * position_size_usd * 2  # Both sides
        
        # Trading fees (both venues)
        trading_fees = position_size_usd * 0.002  # 0.1% each side
        
        # Capital efficiency cost (opportunity cost)
        capital_cost = position_size_usd * 0.0001  # 0.01% per 8 hours
        
        total_costs = total_slippage_cost + trading_fees + capital_cost
        net_profit = gross_profit - total_costs
        
        return {
            "strategy": "traditional",
            "coin": coin["symbol"],
            "funding_spread": spread,
            "position_size_usd": position_size_usd,
            "short_venue": short_venue,
            "long_venue": long_venue,
            "gross_profit_usd": gross_profit,
            "slippage_cost_usd": total_slippage_cost,
            "trading_fees_usd": trading_fees,
            "capital_cost_usd": capital_cost,
            "total_costs_usd": total_costs,
            "net_profit_usd": net_profit,
            "profit_margin_pct": (net_profit / position_size_usd) * 100,
            "roi_annualized_pct": (net_profit / position_size_usd) * 365 * 3 * 100,  # 3 funding periods per day
            "capital_efficiency": net_profit / position_size_usd,
            "slippage_estimate": slippage_estimate.to_dict()
        }

class FRYArbitrageEngine:
    """
    FRY funding arbitrage engine for comparison
    """
    
    def __init__(self):
        self.slippage_engine = CrossVenueSlippageEngine()
        self.paradox_engine = LiquidityParadoxEngine()
        self.total_fry_minted = 0
        self.positions = []
        
    def analyze_fry_opportunity(self, coin, funding_rates, position_size_usd):
        """Analyze FRY arbitrage opportunity"""
        
        rates = list(funding_rates.values())
        spread = max(rates) - min(rates)
        
        # Calculate slippage (FRY focuses on this)
        market_cap = coin.get("market_cap_usd", 1000000)
        slippage_estimate = self.slippage_engine.estimate_slippage(
            coin["symbol"], position_size_usd, market_cap
        )
        
        # FRY calculation: slippage-based minting
        slippage_cost = (slippage_estimate.total_cost_pct / 100) * position_size_usd
        
        # FRY minting calculation
        base_fry = slippage_cost * 1.0  # 1 FRY per $1 slippage
        slippage_severity = slippage_estimate.total_cost_pct / 10.0  # Severity multiplier
        size_bonus = min(0.5, position_size_usd / 1000000)  # Size bonus
        
        total_fry_minted = base_fry * (1 + slippage_severity + size_bonus)
        
        # FRY value (assuming $0.10 per FRY)
        fry_value_usd = total_fry_minted * 0.10
        
        # Traditional profit still exists
        gross_profit = spread * position_size_usd
        trading_fees = position_size_usd * 0.002
        net_traditional_profit = gross_profit - slippage_cost - trading_fees
        
        # Total FRY system value
        total_value = net_traditional_profit + fry_value_usd
        
        return {
            "strategy": "fry",
            "coin": coin["symbol"],
            "funding_spread": spread,
            "position_size_usd": position_size_usd,
            "gross_profit_usd": gross_profit,
            "slippage_cost_usd": slippage_cost,
            "trading_fees_usd": trading_fees,
            "net_traditional_profit_usd": net_traditional_profit,
            "fry_minted": total_fry_minted,
            "fry_value_usd": fry_value_usd,
            "total_value_usd": total_value,
            "profit_margin_pct": (total_value / position_size_usd) * 100,
            "roi_annualized_pct": (total_value / position_size_usd) * 365 * 3 * 100,
            "capital_efficiency": total_value / position_size_usd,
            "fry_bonus_pct": (fry_value_usd / max(net_traditional_profit, 1)) * 100,
            "slippage_estimate": slippage_estimate.to_dict()
        }

class ArbitrageComparisonEngine:
    """
    Main comparison engine for FRY vs Traditional arbitrage
    """
    
    def __init__(self):
        self.traditional_engine = TraditionalArbitrageEngine()
        self.fry_engine = FRYArbitrageEngine()
        
    def simulate_funding_rates(self, coin_symbol, volatility=1.0):
        """Simulate realistic funding rates with volatility"""
        
        # Base funding rate influenced by market conditions
        base_rate = random.uniform(-0.005, 0.015)  # -0.5% to 1.5%
        
        # Venue-specific variations
        venue_variations = {
            "binance": random.uniform(-0.003, 0.003) * volatility,
            "okx": random.uniform(-0.005, 0.005) * volatility,
            "bybit": random.uniform(-0.004, 0.004) * volatility,
            "kucoin": random.uniform(-0.006, 0.006) * volatility,
            "mexc": random.uniform(-0.008, 0.008) * volatility,
            "gate": random.uniform(-0.007, 0.007) * volatility
        }
        
        funding_rates = {}
        for venue, variation in venue_variations.items():
            funding_rates[venue] = base_rate + variation
        
        return funding_rates
    
    def compare_strategies(self, coin, position_sizes, num_simulations=10):
        """Compare both strategies across multiple scenarios"""
        
        results = {
            "coin": coin["symbol"],
            "market_cap": coin.get("market_cap_usd", 1000000),
            "simulations": num_simulations,
            "position_sizes_tested": position_sizes,
            "traditional_results": [],
            "fry_results": [],
            "comparison_metrics": {}
        }
        
        for sim in range(num_simulations):
            # Generate funding rates with varying volatility
            volatility = random.uniform(0.5, 2.0)  # Market volatility factor
            funding_rates = self.simulate_funding_rates(coin["symbol"], volatility)
            
            for position_size in position_sizes:
                # Analyze traditional arbitrage
                traditional = self.traditional_engine.analyze_traditional_opportunity(
                    coin, funding_rates, position_size
                )
                traditional["simulation"] = sim
                traditional["volatility_factor"] = volatility
                results["traditional_results"].append(traditional)
                
                # Analyze FRY arbitrage
                fry = self.fry_engine.analyze_fry_opportunity(
                    coin, funding_rates, position_size
                )
                fry["simulation"] = sim
                fry["volatility_factor"] = volatility
                results["fry_results"].append(fry)
        
        # Calculate comparison metrics
        results["comparison_metrics"] = self._calculate_comparison_metrics(
            results["traditional_results"], 
            results["fry_results"]
        )
        
        return results
    
    def _calculate_comparison_metrics(self, traditional_results, fry_results):
        """Calculate comprehensive comparison metrics"""
        
        # Filter profitable opportunities only
        profitable_traditional = [r for r in traditional_results if r["net_profit_usd"] > 0]
        profitable_fry = [r for r in fry_results if r["total_value_usd"] > 0]
        
        if not profitable_traditional or not profitable_fry:
            return {"error": "Insufficient profitable opportunities for comparison"}
        
        # Average metrics
        avg_traditional_profit = sum(r["net_profit_usd"] for r in profitable_traditional) / len(profitable_traditional)
        avg_fry_value = sum(r["total_value_usd"] for r in profitable_fry) / len(profitable_fry)
        
        avg_traditional_roi = sum(r["roi_annualized_pct"] for r in profitable_traditional) / len(profitable_traditional)
        avg_fry_roi = sum(r["roi_annualized_pct"] for r in profitable_fry) / len(profitable_fry)
        
        # Risk metrics
        traditional_volatility = self._calculate_volatility([r["net_profit_usd"] for r in profitable_traditional])
        fry_volatility = self._calculate_volatility([r["total_value_usd"] for r in profitable_fry])
        
        # Capital efficiency
        avg_traditional_efficiency = sum(r["capital_efficiency"] for r in profitable_traditional) / len(profitable_traditional)
        avg_fry_efficiency = sum(r["capital_efficiency"] for r in profitable_fry) / len(profitable_fry)
        
        # Slippage impact
        avg_traditional_slippage = sum(r["slippage_cost_usd"] for r in profitable_traditional) / len(profitable_traditional)
        avg_fry_slippage = sum(r["slippage_cost_usd"] for r in profitable_fry) / len(profitable_fry)
        
        # Success rates
        total_traditional = len(traditional_results)
        total_fry = len(fry_results)
        traditional_success_rate = len(profitable_traditional) / total_traditional * 100
        fry_success_rate = len(profitable_fry) / total_fry * 100
        
        return {
            "profitability": {
                "traditional_avg_profit": avg_traditional_profit,
                "fry_avg_value": avg_fry_value,
                "fry_advantage_pct": ((avg_fry_value - avg_traditional_profit) / avg_traditional_profit) * 100,
                "traditional_success_rate": traditional_success_rate,
                "fry_success_rate": fry_success_rate
            },
            "roi_analysis": {
                "traditional_avg_roi": avg_traditional_roi,
                "fry_avg_roi": avg_fry_roi,
                "roi_improvement_pct": ((avg_fry_roi - avg_traditional_roi) / avg_traditional_roi) * 100
            },
            "risk_analysis": {
                "traditional_volatility": traditional_volatility,
                "fry_volatility": fry_volatility,
                "risk_reduction_pct": ((traditional_volatility - fry_volatility) / traditional_volatility) * 100
            },
            "efficiency_analysis": {
                "traditional_capital_efficiency": avg_traditional_efficiency,
                "fry_capital_efficiency": avg_fry_efficiency,
                "efficiency_improvement_pct": ((avg_fry_efficiency - avg_traditional_efficiency) / avg_traditional_efficiency) * 100
            },
            "cost_analysis": {
                "traditional_avg_slippage": avg_traditional_slippage,
                "fry_avg_slippage": avg_fry_slippage,
                "slippage_difference": avg_fry_slippage - avg_traditional_slippage
            }
        }
    
    def _calculate_volatility(self, values):
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def generate_detailed_report(self, comparison_results):
        """Generate detailed comparison report"""
        
        coin = comparison_results["coin"]
        metrics = comparison_results["comparison_metrics"]
        
        if "error" in metrics:
            return {"error": metrics["error"]}
        
        # Determine winner in each category
        profitability_winner = "FRY" if metrics["profitability"]["fry_advantage_pct"] > 0 else "Traditional"
        roi_winner = "FRY" if metrics["roi_analysis"]["roi_improvement_pct"] > 0 else "Traditional"
        risk_winner = "FRY" if metrics["risk_analysis"]["risk_reduction_pct"] > 0 else "Traditional"
        efficiency_winner = "FRY" if metrics["efficiency_analysis"]["efficiency_improvement_pct"] > 0 else "Traditional"
        
        # Overall score
        fry_wins = sum([
            metrics["profitability"]["fry_advantage_pct"] > 0,
            metrics["roi_analysis"]["roi_improvement_pct"] > 0,
            metrics["risk_analysis"]["risk_reduction_pct"] > 0,
            metrics["efficiency_analysis"]["efficiency_improvement_pct"] > 0
        ])
        
        overall_winner = "FRY" if fry_wins >= 2 else "Traditional"
        
        report = {
            "coin_analyzed": coin,
            "analysis_summary": {
                "overall_winner": overall_winner,
                "fry_categories_won": fry_wins,
                "total_categories": 4
            },
            "category_winners": {
                "profitability": profitability_winner,
                "roi": roi_winner,
                "risk_management": risk_winner,
                "capital_efficiency": efficiency_winner
            },
            "key_findings": {
                "profitability_advantage": "{:.1f}%".format(abs(metrics["profitability"]["fry_advantage_pct"])),
                "roi_improvement": "{:.1f}%".format(abs(metrics["roi_analysis"]["roi_improvement_pct"])),
                "risk_change": "{:.1f}%".format(abs(metrics["risk_analysis"]["risk_reduction_pct"])),
                "efficiency_gain": "{:.1f}%".format(abs(metrics["efficiency_analysis"]["efficiency_improvement_pct"]))
            },
            "detailed_metrics": metrics,
            "recommendations": self._generate_recommendations(metrics, overall_winner)
        }
        
        return report
    
    def _generate_recommendations(self, metrics, winner):
        """Generate strategic recommendations based on analysis"""
        
        recommendations = []
        
        if winner == "FRY":
            recommendations.append("FRY arbitrage shows superior performance across multiple metrics")
            
            if metrics["profitability"]["fry_advantage_pct"] > 20:
                recommendations.append("FRY provides significant profitability advantage (>20%)")
            
            if metrics["risk_analysis"]["risk_reduction_pct"] > 0:
                recommendations.append("FRY reduces risk while maintaining returns")
                
            recommendations.append("Consider allocating larger portion of capital to FRY strategy")
            
        else:
            recommendations.append("Traditional arbitrage remains competitive for this coin")
            
            if metrics["profitability"]["fry_advantage_pct"] < -10:
                recommendations.append("Traditional approach shows better raw profitability")
            
            recommendations.append("FRY may be better suited for different market conditions")
        
        # Universal recommendations
        if metrics["cost_analysis"]["traditional_avg_slippage"] > 100:
            recommendations.append("High slippage costs - consider smaller position sizes")
        
        if metrics["profitability"]["traditional_success_rate"] < 50:
            recommendations.append("Low success rate - market conditions may not favor arbitrage")
        
        return recommendations

def run_liquidity_comparison_study():
    """Run comprehensive liquidity impact study"""
    
    print("🔄 FRY vs Traditional Arbitrage: Liquidity Impact Study")
    print("=" * 80)
    
    # Initialize comparison engine
    comparison_engine = ArbitrageComparisonEngine()
    
    # Define test coins with different liquidity profiles
    test_coins = [
        {
            "symbol": "COIN_X",
            "name": "High Liquidity Coin",
            "market_cap_usd": 500000000,  # $500M market cap (high liquidity)
            "liquidity_tier": "high"
        },
        {
            "symbol": "COIN_Y", 
            "name": "Low Liquidity Coin",
            "market_cap_usd": 5000000,    # $5M market cap (low liquidity)
            "liquidity_tier": "low"
        }
    ]
    
    # Position sizes to test
    position_sizes = [10000, 25000, 50000, 100000]  # $10k to $100k
    
    all_results = {}
    
    for coin in test_coins:
        print("\n" + "="*60)
        print("📊 Analyzing {} ({}) - Market Cap: ${:,}".format(
            coin["symbol"], 
            coin["name"],
            coin["market_cap_usd"]
        ))
        print("Position sizes: {}".format(
            ["${:,}".format(size) for size in position_sizes]
        ))
        
        # Run comparison
        print("\n🔍 Running simulations...")
        results = comparison_engine.compare_strategies(
            coin=coin,
            position_sizes=position_sizes,
            num_simulations=25  # More simulations for better data
        )
        
        # Generate detailed report
        report = comparison_engine.generate_detailed_report(results)
        
        if "error" in report:
            print("❌ Analysis failed: {}".format(report["error"]))
            continue
        
        # Store results
        all_results[coin["symbol"]] = {
            "coin_info": coin,
            "results": results,
            "report": report
        }
        
        # Display results
        print("\n🏆 COMPARISON RESULTS FOR {} ({})".format(
            coin["symbol"], coin["liquidity_tier"].upper()
        ))
        print("=" * 50)
        
        print("Overall Winner: {}".format(report["analysis_summary"]["overall_winner"]))
        print("FRY won {}/{} categories".format(
            report["analysis_summary"]["fry_categories_won"],
            report["analysis_summary"]["total_categories"]
        ))
        
        print("\n📈 Category Winners:")
        for category, winner in report["category_winners"].items():
            print("  {}: {}".format(category.replace('_', ' ').title(), winner))
        
        print("\n💰 Key Performance Metrics:")
        metrics = report["detailed_metrics"]
        
        print("  Profitability:")
        print("    Traditional Avg: ${:,.2f}".format(metrics["profitability"]["traditional_avg_profit"]))
        print("    FRY Avg Value: ${:,.2f}".format(metrics["profitability"]["fry_avg_value"]))
        print("    FRY Advantage: {:+.1f}%".format(metrics["profitability"]["fry_advantage_pct"]))
        
        print("  ROI (Annualized):")
        print("    Traditional: {:.1f}%".format(metrics["roi_analysis"]["traditional_avg_roi"]))
        print("    FRY: {:.1f}%".format(metrics["roi_analysis"]["fry_avg_roi"]))
        print("    Improvement: {:+.1f}%".format(metrics["roi_analysis"]["roi_improvement_pct"]))
        
        print("  Risk (Volatility):")
        print("    Traditional: ${:.2f}".format(metrics["risk_analysis"]["traditional_volatility"]))
        print("    FRY: ${:.2f}".format(metrics["risk_analysis"]["fry_volatility"]))
        print("    Risk Change: {:+.1f}%".format(metrics["risk_analysis"]["risk_reduction_pct"]))
        
        print("  Capital Efficiency:")
        print("    Traditional: {:.4f}".format(metrics["efficiency_analysis"]["traditional_capital_efficiency"]))
        print("    FRY: {:.4f}".format(metrics["efficiency_analysis"]["fry_capital_efficiency"]))
        print("    Improvement: {:+.1f}%".format(metrics["efficiency_analysis"]["efficiency_improvement_pct"]))
        
        print("\n💡 Strategic Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print("  {}. {}".format(i, rec))
    
    # Generate cross-liquidity analysis
    if len(all_results) >= 2:
        print("\n" + "="*80)
        print("🔬 CROSS-LIQUIDITY ANALYSIS")
        print("="*80)
        
        high_liq = all_results["COIN_X"]["report"]["detailed_metrics"]
        low_liq = all_results["COIN_Y"]["report"]["detailed_metrics"]
        
        print("\n📊 Liquidity Impact on FRY Advantage:")
        print("  High Liquidity (COIN_X): {:+.1f}%".format(high_liq["profitability"]["fry_advantage_pct"]))
        print("  Low Liquidity (COIN_Y): {:+.1f}%".format(low_liq["profitability"]["fry_advantage_pct"]))
        
        liquidity_impact = low_liq["profitability"]["fry_advantage_pct"] - high_liq["profitability"]["fry_advantage_pct"]
        print("  Liquidity Impact: {:+.1f}% (low vs high)".format(liquidity_impact))
        
        print("\n📈 ROI Comparison:")
        print("  High Liquidity FRY ROI: {:.1f}%".format(high_liq["roi_analysis"]["fry_avg_roi"]))
        print("  Low Liquidity FRY ROI: {:.1f}%".format(low_liq["roi_analysis"]["fry_avg_roi"]))
        
        print("\n💸 Slippage Cost Analysis:")
        print("  High Liquidity Avg Slippage: ${:.2f}".format(high_liq["cost_analysis"]["traditional_avg_slippage"]))
        print("  Low Liquidity Avg Slippage: ${:.2f}".format(low_liq["cost_analysis"]["traditional_avg_slippage"]))
        
        print("\n🎯 Key Insights:")
        if liquidity_impact > 5:
            print("  • FRY shows significantly better advantage in low liquidity environments")
            print("  • Higher slippage costs create more FRY minting opportunities")
        elif liquidity_impact < -5:
            print("  • FRY performs better in high liquidity environments")
            print("  • Lower slippage reduces FRY minting but improves traditional profits")
        else:
            print("  • FRY advantage is consistent across liquidity levels")
            print("  • Strategy selection less dependent on liquidity conditions")
        
        # Determine optimal strategy by liquidity
        high_winner = all_results["COIN_X"]["report"]["analysis_summary"]["overall_winner"]
        low_winner = all_results["COIN_Y"]["report"]["analysis_summary"]["overall_winner"]
        
        print("\n🏆 Optimal Strategy by Liquidity:")
        print("  High Liquidity: {} Strategy".format(high_winner))
        print("  Low Liquidity: {} Strategy".format(low_winner))
    
    # Export comprehensive results
    export_data = {
        "analysis_timestamp": datetime.now().isoformat(),
        "study_type": "liquidity_impact_comparison",
        "coins_analyzed": len(all_results),
        "results_by_coin": all_results
    }
    
    filename = "liquidity_impact_study_{}.json".format(int(time.time()))
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print("\n💾 Comprehensive study results exported: {}".format(filename))
    print("✅ Liquidity impact analysis complete!")

def main():
    """Run liquidity comparison study"""
    run_liquidity_comparison_study()

if __name__ == "__main__":
    main()
