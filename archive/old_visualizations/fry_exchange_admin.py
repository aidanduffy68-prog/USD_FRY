#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Exchange Administrator System
Central hub for harvesting retail losses, minting FRY tokens, and calculating FRY Score
Serves as the bridge between retail traders and institutional structured products
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Import existing components
from rekt_dark_cdo_enhanced import RektDarkCDO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYExchangeAdmin:
    """
    Exchange Administrator System - Central authority for FRY ecosystem
    
    Responsibilities:
    1. Harvest losses from retail traders on Hyperliquid
    2. Mint FRY tokens with volatility multipliers
    3. Calculate and maintain the FRY Score benchmark
    4. Package structured products for institutional buyers
    """
    
    def __init__(self):
        self.cdo_system = RektDarkCDO()
        
        # FRY Score components
        self.fry_score = 100.0  # Base score
        self.score_history = []
        self.harvesting_metrics = {
            "total_losses_harvested": 0.0,
            "total_fry_minted": 0.0,
            "active_retail_traders": 0,
            "liquidation_events": 0,
            "volatility_index": 1.0
        }
        
        # Institutional product catalog
        self.structured_products = {}
        self.product_counter = 0
        
        logger.info("🏦 FRY Exchange Administrator initialized")
    
    def harvest_retail_losses(self, trader_data: List[Dict]) -> Dict:
        """
        Harvest losses from retail traders and mint FRY tokens
        
        Args:
            trader_data: List of trader loss events from Hyperliquid monitoring
            
        Returns:
            Harvesting summary with FRY minting details
        """
        harvest_summary = {
            "timestamp": datetime.now().isoformat(),
            "traders_processed": 0,
            "total_losses_harvested": 0.0,
            "total_fry_minted": 0.0,
            "liquidations": 0,
            "fry_score_impact": 0.0
        }
        
        for trader in trader_data:
            if trader.get('pnl', 0) >= 0:
                continue  # Only harvest losses
            
            loss_amount = abs(trader['pnl'])
            leverage = trader.get('leverage', 1.0)
            position_size = trader.get('position_size_usd', 0.0)
            is_liquidation = trader.get('liquidated', False)
            
            # Process through CDO system for FRY minting
            collateral_id, fry_minted = self.cdo_system.sweep_collateral(
                trader_address=trader['trader_id'],
                loss_amount_usd=loss_amount,
                asset=trader.get('asset', 'BTC'),
                leverage=leverage,
                position_size_usd=position_size,
                liquidation=is_liquidation
            )
            
            # Update harvest metrics
            harvest_summary["traders_processed"] += 1
            harvest_summary["total_losses_harvested"] += loss_amount
            harvest_summary["total_fry_minted"] += fry_minted
            if is_liquidation:
                harvest_summary["liquidations"] += 1
            
            # Update global metrics
            self.harvesting_metrics["total_losses_harvested"] += loss_amount
            self.harvesting_metrics["total_fry_minted"] += fry_minted
            if is_liquidation:
                self.harvesting_metrics["liquidation_events"] += 1
        
        # Update FRY Score based on harvesting activity
        score_impact = self._calculate_fry_score_impact(harvest_summary)
        harvest_summary["fry_score_impact"] = score_impact
        self._update_fry_score(score_impact)
        
        logger.info("🌾 Harvested ${:,.2f} losses → {:,.2f} FRY from {} traders".format(
            harvest_summary["total_losses_harvested"],
            harvest_summary["total_fry_minted"],
            harvest_summary["traders_processed"]
        ))
        
        return harvest_summary
    
    def _calculate_fry_score_impact(self, harvest_data: Dict) -> float:
        """
        Calculate how current harvesting activity impacts the FRY Score
        
        FRY Score represents the "pain index" of retail trading activity:
        - Higher losses = higher score (more pain)
        - More liquidations = score multiplier
        - Volatility in loss patterns = score volatility
        """
        base_impact = harvest_data["total_losses_harvested"] / 10000  # $10k losses = 1 point
        
        # Liquidation multiplier
        if harvest_data["traders_processed"] > 0:
            liquidation_rate = harvest_data["liquidations"] / harvest_data["traders_processed"]
            liquidation_multiplier = 1 + (liquidation_rate * 2)  # Up to 3x for 100% liquidation rate
        else:
            liquidation_multiplier = 1.0
        
        # FRY minting efficiency (higher multipliers = higher score)
        if harvest_data["total_losses_harvested"] > 0:
            fry_efficiency = harvest_data["total_fry_minted"] / harvest_data["total_losses_harvested"]
            efficiency_multiplier = min(fry_efficiency / 2, 3.0)  # Cap at 3x
        else:
            efficiency_multiplier = 1.0
        
        impact = base_impact * liquidation_multiplier * efficiency_multiplier
        return round(impact, 2)
    
    def _update_fry_score(self, impact: float):
        """
        Update the FRY Score with exponential moving average
        """
        # Exponential moving average with 0.1 alpha (slow adjustment)
        self.fry_score = (0.9 * self.fry_score) + (0.1 * (100 + impact))
        
        # Keep score in reasonable range (0-1000)
        self.fry_score = max(0, min(1000, self.fry_score))
        
        # Record for history
        self.score_history.append({
            "timestamp": datetime.now().isoformat(),
            "score": self.fry_score,
            "impact": impact
        })
        
        # Keep only last 100 records
        if len(self.score_history) > 100:
            self.score_history = self.score_history[-100:]
    
    def get_current_fry_score(self) -> Dict:
        """
        Get current FRY Score with context for institutional buyers
        """
        # Calculate score metrics
        recent_scores = [s["score"] for s in self.score_history[-10:]] if self.score_history else [self.fry_score]
        score_volatility = np.std(recent_scores) if len(recent_scores) > 1 else 0.0
        score_trend = "stable"
        
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0] * 1.05:
                score_trend = "increasing"
            elif recent_scores[-1] < recent_scores[0] * 0.95:
                score_trend = "decreasing"
        
        return {
            "current_score": round(self.fry_score, 2),
            "score_volatility": round(score_volatility, 2),
            "score_trend": score_trend,
            "last_updated": datetime.now().isoformat(),
            "total_fry_supply": self.harvesting_metrics["total_fry_minted"],
            "total_losses_harvested": self.harvesting_metrics["total_losses_harvested"],
            "liquidation_events": self.harvesting_metrics["liquidation_events"]
        }
    
    def create_structured_product(self, product_type: str, fry_score_benchmark: float, 
                                target_yield: float, minimum_investment: float) -> str:
        """
        Create institutional structured product benchmarked to FRY Score
        
        Args:
            product_type: Type of product (e.g., "FRY_INDEX_BOND", "VOLATILITY_SWAP")
            fry_score_benchmark: FRY Score level that triggers payouts
            target_yield: Annual yield target
            minimum_investment: Minimum investment amount
            
        Returns:
            Product ID for institutional reference
        """
        product_id = f"FRY-{product_type}-{self.product_counter:04d}"
        self.product_counter += 1
        
        # Use existing CDO system to create underlying tranches
        tranche_ratings = [self.cdo_system.TrancheRating.AAA, 
                          self.cdo_system.TrancheRating.AA,
                          self.cdo_system.TrancheRating.A]
        
        underlying_tranches = []
        for rating in tranche_ratings:
            tranche_id = self.cdo_system.create_cdo_tranche(rating)
            if tranche_id:
                underlying_tranches.append(tranche_id)
        
        product = {
            "id": product_id,
            "type": product_type,
            "fry_score_benchmark": fry_score_benchmark,
            "target_yield": target_yield,
            "minimum_investment": minimum_investment,
            "underlying_tranches": underlying_tranches,
            "created_timestamp": datetime.now().isoformat(),
            "current_fry_score": self.fry_score,
            "status": "available"
        }
        
        self.structured_products[product_id] = product
        
        logger.info("📦 Created structured product {}: {} @ {:.1f}% yield (FRY Score benchmark: {})".format(
            product_id, product_type, target_yield * 100, fry_score_benchmark
        ))
        
        return product_id
    
    def get_institutional_catalog(self) -> Dict:
        """
        Get catalog of available structured products for institutional buyers
        """
        current_score = self.get_current_fry_score()
        
        catalog = {
            "fry_score_context": current_score,
            "available_products": [],
            "product_categories": {
                "FRY_INDEX_BONDS": "Fixed income products tied to FRY Score levels",
                "VOLATILITY_SWAPS": "Derivatives on FRY Score volatility",
                "LIQUIDATION_NOTES": "Products that pay when liquidation events spike",
                "PAIN_CERTIFICATES": "Structured notes with FRY Score triggers"
            }
        }
        
        for product_id, product in self.structured_products.items():
            if product["status"] == "available":
                # Calculate current performance vs benchmark
                score_performance = (current_score["current_score"] / product["fry_score_benchmark"] - 1) * 100
                
                catalog["available_products"].append({
                    "id": product_id,
                    "type": product["type"],
                    "target_yield": f"{product['target_yield'] * 100:.1f}%",
                    "minimum_investment": f"${product['minimum_investment']:,.0f}",
                    "fry_score_benchmark": product["fry_score_benchmark"],
                    "current_performance": f"{score_performance:+.1f}%",
                    "underlying_tranches": len(product["underlying_tranches"])
                })
        
        return catalog
    
    def export_admin_dashboard(self, filename: str = "fry_admin_dashboard.json"):
        """
        Export comprehensive admin dashboard data
        """
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "fry_score": self.get_current_fry_score(),
            "harvesting_metrics": self.harvesting_metrics,
            "cdo_stats": self.cdo_system.get_market_stats(),
            "structured_products_count": len(self.structured_products),
            "institutional_catalog": self.get_institutional_catalog(),
            "score_history": self.score_history[-20:] if self.score_history else []
        }
        
        with open(filename, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        logger.info("📊 Admin dashboard exported to {}".format(filename))
        return dashboard_data

def main():
    """
    Demo the FRY Exchange Admin system
    """
    print("🏦 FRY Exchange Administrator - Demo Mode")
    
    admin = FRYExchangeAdmin()
    
    # Simulate retail trader losses
    sample_retail_losses = [
        {
            "trader_id": "retail_001",
            "pnl": -1500,
            "leverage": 10,
            "position_size_usd": 15000,
            "asset": "BTC",
            "liquidated": False
        },
        {
            "trader_id": "retail_002", 
            "pnl": -3200,
            "leverage": 25,
            "position_size_usd": 32000,
            "asset": "ETH",
            "liquidated": True
        },
        {
            "trader_id": "retail_003",
            "pnl": -800,
            "leverage": 5,
            "position_size_usd": 4000,
            "asset": "SOL",
            "liquidated": False
        }
    ]
    
    # Harvest losses and mint FRY
    harvest_result = admin.harvest_retail_losses(sample_retail_losses)
    print(f"\n📈 Harvest Results:")
    print(f"   Losses Harvested: ${harvest_result['total_losses_harvested']:,.2f}")
    print(f"   FRY Minted: {harvest_result['total_fry_minted']:,.2f}")
    print(f"   FRY Score Impact: +{harvest_result['fry_score_impact']}")
    
    # Show current FRY Score
    fry_score = admin.get_current_fry_score()
    print(f"\n🎯 Current FRY Score: {fry_score['current_score']}")
    print(f"   Trend: {fry_score['score_trend']}")
    print(f"   Volatility: {fry_score['score_volatility']}")
    
    # Create structured products for institutions
    admin.create_structured_product("FRY_INDEX_BOND", 120.0, 0.08, 1000000)
    admin.create_structured_product("VOLATILITY_SWAP", 100.0, 0.12, 500000)
    admin.create_structured_product("LIQUIDATION_NOTES", 150.0, 0.15, 250000)
    
    # Show institutional catalog
    catalog = admin.get_institutional_catalog()
    print(f"\n🏛️ Institutional Product Catalog:")
    for product in catalog["available_products"]:
        print(f"   {product['id']}: {product['target_yield']} yield (min: {product['minimum_investment']})")
    
    # Export dashboard
    admin.export_admin_dashboard()
    print(f"\n✅ FRY Exchange Admin system operational")

if __name__ == "__main__":
    main()
