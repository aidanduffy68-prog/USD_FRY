#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY System Integration Demo
Demonstrates the complete three-tier architecture:
1. Retail traders -> Hyperliquid losses
2. Exchange admin -> FRY harvesting/minting/scoring  
3. Institutions -> structured products benchmarked to FRY Score
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List

from fry_retail_interface import FRYRetailInterface
from fry_exchange_admin import FRYExchangeAdmin
from fry_institutional_products import FRYInstitutionalProducts

class FRYSystemIntegration:
    """
    Complete FRY ecosystem integration
    Orchestrates the flow from retail losses to institutional products
    """
    
    def __init__(self):
        self.admin = FRYExchangeAdmin()
        self.institutional = FRYInstitutionalProducts()
        self.retail_interfaces = {}
        
        print("🏗️ FRY System Integration initialized")
    
    def add_retail_trader(self, wallet_address: str) -> FRYRetailInterface:
        """Add a retail trader to the system"""
        interface = FRYRetailInterface(wallet_address)
        self.retail_interfaces[wallet_address] = interface
        return interface
    
    async def simulate_trading_cycle(self):
        """
        Simulate a complete trading cycle:
        1. Retail traders experience losses
        2. Admin harvests losses and mints FRY
        3. FRY Score updates
        4. Institutional products revalue
        """
        print("\n" + "="*80)
        print("🔄 SIMULATING COMPLETE FRY TRADING CYCLE")
        print("="*80)
        
        # Step 1: Simulate retail trader losses
        print("\n📱 TIER 1: RETAIL TRADERS (Hyperliquid)")
        print("-" * 50)
        
        # Sample retail losses (simulated Hyperliquid data)
        retail_losses = [
            {
                "trader_id": "0x1234...5678",
                "pnl": -2500,
                "leverage": 15,
                "position_size_usd": 25000,
                "asset": "BTC",
                "liquidated": True
            },
            {
                "trader_id": "0x2345...6789", 
                "pnl": -1200,
                "leverage": 8,
                "position_size_usd": 12000,
                "asset": "ETH",
                "liquidated": False
            },
            {
                "trader_id": "0x3456...7890",
                "pnl": -4800,
                "leverage": 25,
                "position_size_usd": 48000,
                "asset": "SOL",
                "liquidated": True
            },
            {
                "trader_id": "0x4567...8901",
                "pnl": -800,
                "leverage": 5,
                "position_size_usd": 8000,
                "asset": "AVAX",
                "liquidated": False
            }
        ]
        
        for loss in retail_losses:
            status = "🔴 LIQUIDATED" if loss["liquidated"] else "🟡 LOSS"
            print(f"   {loss['trader_id']}: ${loss['pnl']:,} on {loss['asset']} {status}")
        
        print(f"\n   Total retail losses: ${sum(abs(l['pnl']) for l in retail_losses):,}")
        
        # Step 2: Exchange admin harvests losses
        print("\n🏦 TIER 2: EXCHANGE ADMIN (FRY Harvesting)")
        print("-" * 50)
        
        harvest_result = self.admin.harvest_retail_losses(retail_losses)
        
        print(f"   💸 Losses harvested: ${harvest_result['total_losses_harvested']:,.2f}")
        print(f"   🪙 FRY tokens minted: {harvest_result['total_fry_minted']:,.2f}")
        print(f"   ⚡ Liquidation events: {harvest_result['liquidations']}")
        print(f"   📊 FRY Score impact: +{harvest_result['fry_score_impact']}")
        
        # Get updated FRY Score
        fry_score_data = self.admin.get_current_fry_score()
        print(f"\n   🎯 Current FRY Score: {fry_score_data['current_score']}")
        print(f"   📈 Score trend: {fry_score_data['score_trend']}")
        print(f"   📊 Score volatility: {fry_score_data['score_volatility']}")
        
        # Step 3: Create institutional products
        print("\n🏛️ TIER 3: INSTITUTIONAL PRODUCTS (FRY Score Benchmarked)")
        print("-" * 50)
        
        # Create products if none exist
        if not self.institutional.products:
            print("   📋 Creating institutional product suite...")
            
            self.institutional.create_fry_index_bond(
                notional=10000000,
                maturity_months=12,
                fry_score_trigger=120.0,
                coupon_rate=0.08
            )
            
            self.institutional.create_volatility_swap(
                notional=5000000,
                strike_volatility=0.15,
                tenor_days=90
            )
            
            self.institutional.create_liquidation_notes(
                notional=3000000,
                liquidation_threshold=3,  # 3 liquidations per cycle
                payout_multiple=1.5,
                maturity_months=6
            )
            
            pain_basket = [
                {"metric": "fry_score", "weight": 1.0, "initial_level": 100.0}
            ]
            self.institutional.create_pain_certificate(
                notional=2000000,
                pain_basket=pain_basket,
                leverage=2.0,
                maturity_months=18
            )
        
        # Update product valuations
        print("   💰 Updating product valuations...")
        valuations = self.institutional.update_product_valuations(
            current_fry_score=fry_score_data['current_score'],
            fry_score_volatility=fry_score_data['score_volatility'] / 100,
            daily_liquidations=harvest_result['liquidations']
        )
        
        for product_id, valuation in valuations.items():
            product = self.institutional.products[product_id]
            print(f"   📦 {product['type']}: ${product['notional']:,.0f} → {valuation}")
        
        # Show buyer matching
        print("\n   🎯 Institutional buyer matching:")
        for product_id in self.institutional.products.keys():
            buyer = self.institutional.match_buyer_to_product(product_id)
            product_type = self.institutional.products[product_id]['type']
            if buyer:
                print(f"   ✅ {product_type} → {buyer}")
            else:
                print(f"   ❌ {product_type} → No suitable buyer")
        
        return {
            "retail_losses": retail_losses,
            "harvest_result": harvest_result,
            "fry_score": fry_score_data,
            "institutional_valuations": valuations
        }
    
    def generate_system_report(self) -> Dict:
        """Generate comprehensive system report"""
        fry_score = self.admin.get_current_fry_score()
        portfolio = self.institutional.get_institutional_portfolio()
        cdo_stats = self.admin.cdo_system.get_market_stats()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_overview": {
                "fry_score": fry_score['current_score'],
                "total_fry_minted": fry_score['total_fry_supply'],
                "total_losses_harvested": fry_score['total_losses_harvested'],
                "institutional_products": portfolio['total_products'],
                "institutional_notional": portfolio['total_notional']
            },
            "tier_1_retail": {
                "active_traders": len(self.retail_interfaces),
                "total_liquidations": fry_score['liquidation_events']
            },
            "tier_2_admin": {
                "fry_score_data": fry_score,
                "harvesting_metrics": self.admin.harvesting_metrics,
                "cdo_statistics": cdo_stats
            },
            "tier_3_institutional": {
                "portfolio_summary": portfolio,
                "buyer_profiles": list(self.institutional.buyers.keys())
            }
        }
        
        return report
    
    def display_system_dashboard(self):
        """Display comprehensive system dashboard"""
        report = self.generate_system_report()
        
        print("\n" + "="*80)
        print("📊 FRY SYSTEM DASHBOARD")
        print("="*80)
        
        print(f"\n🎯 SYSTEM OVERVIEW")
        overview = report["system_overview"]
        print(f"   FRY Score: {overview['fry_score']:.2f}")
        print(f"   Total FRY Minted: {overview['total_fry_minted']:,.2f}")
        print(f"   Losses Harvested: ${overview['total_losses_harvested']:,.2f}")
        print(f"   Institutional Products: {overview['institutional_products']}")
        print(f"   Institutional Notional: ${overview['institutional_notional']:,.0f}")
        
        print(f"\n📱 TIER 1: RETAIL TRADERS")
        retail = report["tier_1_retail"]
        print(f"   Active Traders: {retail['active_traders']}")
        print(f"   Total Liquidations: {retail['total_liquidations']}")
        
        print(f"\n🏦 TIER 2: EXCHANGE ADMIN")
        admin_data = report["tier_2_admin"]
        print(f"   FRY Score Trend: {admin_data['fry_score_data']['score_trend']}")
        print(f"   Score Volatility: {admin_data['fry_score_data']['score_volatility']:.2f}")
        print(f"   CDO Tranches: {admin_data['cdo_statistics']['active_tranches']}")
        
        print(f"\n🏛️ TIER 3: INSTITUTIONAL")
        institutional = report["tier_3_institutional"]
        print(f"   Product Types: {len(institutional['portfolio_summary']['products_by_type'])}")
        print(f"   Active Products: {len(institutional['portfolio_summary']['active_products'])}")
        print(f"   Registered Buyers: {len(institutional['buyer_profiles'])}")
        
        print("\n" + "="*80)

async def main():
    """
    Demo the complete FRY system integration
    """
    print("🚀 FRY System Integration Demo")
    print("Demonstrating three-tier architecture:")
    print("1. Retail → Hyperliquid losses")
    print("2. Exchange admin → FRY harvesting/minting/scoring")
    print("3. Institutions → structured products")
    
    # Initialize system
    system = FRYSystemIntegration()
    
    # Run multiple trading cycles
    for cycle in range(3):
        print(f"\n🔄 TRADING CYCLE {cycle + 1}")
        await system.simulate_trading_cycle()
        
        if cycle < 2:
            print("\n⏳ Waiting for next cycle...")
            time.sleep(2)
    
    # Show final dashboard
    system.display_system_dashboard()
    
    # Export system report
    report = system.generate_system_report()
    with open("fry_system_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ System report exported to fry_system_report.json")
    print(f"🎉 FRY System Integration demo complete!")

if __name__ == "__main__":
    asyncio.run(main())
