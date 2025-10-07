#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Institutional Products
Structured products explicitly benchmarked to the FRY Score
For institutional buyers seeking exposure to retail trading pain
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYInstitutionalProducts:
    """
    Institutional product suite benchmarked to FRY Score
    
    Products available:
    1. FRY Index Bonds - Fixed income tied to FRY Score levels
    2. Volatility Swaps - Derivatives on FRY Score volatility
    3. Liquidation Notes - Structured notes triggered by liquidation spikes
    4. Pain Certificates - Complex products with FRY Score triggers
    """
    
    def __init__(self):
        self.products = {}
        self.buyers = {
            "Binance Ventures": {"risk_appetite": "medium", "preferred_yield": 0.08, "min_investment": 5000000},
            "Wintermute Trading": {"risk_appetite": "high", "preferred_yield": 0.12, "min_investment": 2000000},
            "Alameda Research": {"risk_appetite": "very_high", "preferred_yield": 0.18, "min_investment": 1000000},
            "Citadel Securities": {"risk_appetite": "low", "preferred_yield": 0.06, "min_investment": 10000000},
            "GIC Singapore": {"risk_appetite": "medium", "preferred_yield": 0.07, "min_investment": 15000000},
            "Paradigm Capital": {"risk_appetite": "high", "preferred_yield": 0.14, "min_investment": 3000000}
        }
        
        logger.info("🏛️ FRY Institutional Products initialized")
    
    def create_fry_index_bond(self, notional: float, maturity_months: int, 
                             fry_score_trigger: float, coupon_rate: float) -> str:
        """
        Create FRY Index Bond - pays coupon when FRY Score exceeds trigger
        
        Structure:
        - Fixed notional amount
        - Coupon payments triggered by FRY Score levels
        - Principal protected (unless extreme FRY Score events)
        """
        product_id = f"FRY-BOND-{len(self.products):04d}"
        
        product = {
            "id": product_id,
            "type": "FRY_INDEX_BOND",
            "notional": notional,
            "maturity_date": (datetime.now() + timedelta(days=maturity_months*30)).isoformat(),
            "fry_score_trigger": fry_score_trigger,
            "coupon_rate": coupon_rate,
            "coupon_frequency": "monthly",
            "principal_protection": 0.95,  # 95% principal protection
            "current_value": notional,
            "coupons_paid": 0,
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        self.products[product_id] = product
        
        logger.info("📋 Created FRY Index Bond: ${:,.0f} @ {:.1f}% (trigger: FRY Score {})".format(
            notional, coupon_rate * 100, fry_score_trigger
        ))
        
        return product_id
    
    def create_volatility_swap(self, notional: float, strike_volatility: float,
                              tenor_days: int) -> str:
        """
        Create FRY Score Volatility Swap
        
        Structure:
        - Pay/receive based on realized vs implied FRY Score volatility
        - Notional amount determines payout scale
        - Strike volatility is the breakeven level
        """
        product_id = f"FRY-VOLSWAP-{len(self.products):04d}"
        
        product = {
            "id": product_id,
            "type": "VOLATILITY_SWAP",
            "notional": notional,
            "strike_volatility": strike_volatility,
            "expiry_date": (datetime.now() + timedelta(days=tenor_days)).isoformat(),
            "current_realized_vol": 0.0,
            "mark_to_market": 0.0,
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        self.products[product_id] = product
        
        logger.info("📊 Created FRY Volatility Swap: ${:,.0f} notional @ {:.1f}% strike vol".format(
            notional, strike_volatility * 100
        ))
        
        return product_id
    
    def create_liquidation_notes(self, notional: float, liquidation_threshold: int,
                               payout_multiple: float, maturity_months: int) -> str:
        """
        Create Liquidation-Triggered Notes
        
        Structure:
        - Pays out when daily liquidations exceed threshold
        - Payout = (actual_liquidations / threshold) * payout_multiple * notional
        - Capped at maximum payout
        """
        product_id = f"FRY-LIQNOTE-{len(self.products):04d}"
        
        product = {
            "id": product_id,
            "type": "LIQUIDATION_NOTES",
            "notional": notional,
            "liquidation_threshold": liquidation_threshold,
            "payout_multiple": payout_multiple,
            "max_payout": notional * payout_multiple * 2,  # 2x cap
            "maturity_date": (datetime.now() + timedelta(days=maturity_months*30)).isoformat(),
            "total_payouts": 0.0,
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        self.products[product_id] = product
        
        logger.info("⚡ Created Liquidation Notes: ${:,.0f} (trigger: {} liquidations/day)".format(
            notional, liquidation_threshold
        ))
        
        return product_id
    
    def create_pain_certificate(self, notional: float, pain_basket: List[Dict],
                              leverage: float, maturity_months: int) -> str:
        """
        Create Pain Certificate - Complex product tracking multiple pain metrics
        
        Structure:
        - Basket of FRY Score components with weights
        - Leveraged exposure to pain metrics
        - Barrier features and knock-out levels
        """
        product_id = f"FRY-PAIN-{len(self.products):04d}"
        
        product = {
            "id": product_id,
            "type": "PAIN_CERTIFICATE",
            "notional": notional,
            "pain_basket": pain_basket,
            "leverage": leverage,
            "maturity_date": (datetime.now() + timedelta(days=maturity_months*30)).isoformat(),
            "barrier_level": 0.7,  # Knock-out at 70% of initial value
            "current_value": notional,
            "max_loss": notional * 0.8,  # 80% max loss
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        self.products[product_id] = product
        
        logger.info("🎯 Created Pain Certificate: ${:,.0f} @ {}x leverage".format(
            notional, leverage
        ))
        
        return product_id
    
    def update_product_valuations(self, current_fry_score: float, 
                                 fry_score_volatility: float, daily_liquidations: int):
        """
        Update all product valuations based on current FRY Score metrics
        """
        valuations = {}
        
        for product_id, product in self.products.items():
            if product["status"] != "active":
                continue
            
            if product["type"] == "FRY_INDEX_BOND":
                # Bond pays coupon if FRY Score exceeds trigger
                if current_fry_score >= product["fry_score_trigger"]:
                    coupon_payment = product["notional"] * product["coupon_rate"] / 12  # Monthly
                    product["coupons_paid"] += coupon_payment
                    product["current_value"] = product["notional"] + product["coupons_paid"]
                
                valuations[product_id] = {
                    "current_value": product["current_value"],
                    "total_coupons": product["coupons_paid"],
                    "yield_to_date": product["coupons_paid"] / product["notional"]
                }
            
            elif product["type"] == "VOLATILITY_SWAP":
                # Mark-to-market based on realized vs strike volatility
                vol_diff = fry_score_volatility - product["strike_volatility"]
                mtm = product["notional"] * vol_diff * 100  # Volatility points to dollars
                product["mark_to_market"] = mtm
                product["current_realized_vol"] = fry_score_volatility
                
                valuations[product_id] = {
                    "mark_to_market": mtm,
                    "realized_volatility": fry_score_volatility,
                    "vol_difference": vol_diff
                }
            
            elif product["type"] == "LIQUIDATION_NOTES":
                # Payout if liquidations exceed threshold
                if daily_liquidations > product["liquidation_threshold"]:
                    payout_ratio = daily_liquidations / product["liquidation_threshold"]
                    daily_payout = min(
                        product["notional"] * product["payout_multiple"] * (payout_ratio - 1),
                        product["max_payout"] - product["total_payouts"]
                    )
                    product["total_payouts"] += daily_payout
                
                valuations[product_id] = {
                    "total_payouts": product["total_payouts"],
                    "daily_liquidations": daily_liquidations,
                    "threshold": product["liquidation_threshold"]
                }
            
            elif product["type"] == "PAIN_CERTIFICATE":
                # Complex basket valuation with leverage
                basket_performance = 0.0
                for component in product["pain_basket"]:
                    if component["metric"] == "fry_score":
                        performance = (current_fry_score / component["initial_level"] - 1)
                        basket_performance += performance * component["weight"]
                
                leveraged_performance = basket_performance * product["leverage"]
                new_value = product["notional"] * (1 + leveraged_performance)
                
                # Check barrier
                if new_value < product["notional"] * product["barrier_level"]:
                    product["status"] = "knocked_out"
                    new_value = 0
                
                product["current_value"] = max(new_value, product["notional"] - product["max_loss"])
                
                valuations[product_id] = {
                    "current_value": product["current_value"],
                    "performance": leveraged_performance,
                    "status": product["status"]
                }
        
        return valuations
    
    def match_buyer_to_product(self, product_id: str) -> Optional[str]:
        """
        Match institutional buyer to product based on risk appetite and size
        """
        if product_id not in self.products:
            return None
        
        product = self.products[product_id]
        
        # Score buyers based on fit
        buyer_scores = {}
        for buyer_name, buyer_profile in self.buyers.items():
            score = 0
            
            # Size fit
            if product["notional"] >= buyer_profile["min_investment"]:
                score += 30
            
            # Risk appetite fit
            risk_mapping = {
                "low": {"FRY_INDEX_BOND": 40, "VOLATILITY_SWAP": 10, "LIQUIDATION_NOTES": 5, "PAIN_CERTIFICATE": 0},
                "medium": {"FRY_INDEX_BOND": 35, "VOLATILITY_SWAP": 25, "LIQUIDATION_NOTES": 20, "PAIN_CERTIFICATE": 15},
                "high": {"FRY_INDEX_BOND": 20, "VOLATILITY_SWAP": 35, "LIQUIDATION_NOTES": 30, "PAIN_CERTIFICATE": 25},
                "very_high": {"FRY_INDEX_BOND": 10, "VOLATILITY_SWAP": 25, "LIQUIDATION_NOTES": 35, "PAIN_CERTIFICATE": 40}
            }
            
            risk_score = risk_mapping.get(buyer_profile["risk_appetite"], {}).get(product["type"], 0)
            score += risk_score
            
            buyer_scores[buyer_name] = score
        
        # Return best match if score > 50
        best_buyer = max(buyer_scores.items(), key=lambda x: x[1])
        if best_buyer[1] > 50:
            return best_buyer[0]
        
        return None
    
    def get_institutional_portfolio(self) -> Dict:
        """
        Get complete institutional portfolio view
        """
        portfolio = {
            "timestamp": datetime.now().isoformat(),
            "total_products": len(self.products),
            "total_notional": sum(p["notional"] for p in self.products.values()),
            "products_by_type": {},
            "active_products": [],
            "buyer_allocations": {}
        }
        
        # Group by type
        for product in self.products.values():
            product_type = product["type"]
            if product_type not in portfolio["products_by_type"]:
                portfolio["products_by_type"][product_type] = {"count": 0, "total_notional": 0}
            
            portfolio["products_by_type"][product_type]["count"] += 1
            portfolio["products_by_type"][product_type]["total_notional"] += product["notional"]
            
            if product["status"] == "active":
                portfolio["active_products"].append({
                    "id": product["id"],
                    "type": product["type"],
                    "notional": product["notional"],
                    "created": product["created"]
                })
        
        return portfolio

def main():
    """
    Demo institutional products system
    """
    print("🏛️ FRY Institutional Products - Demo")
    
    products = FRYInstitutionalProducts()
    
    # Create sample products
    bond_id = products.create_fry_index_bond(10000000, 12, 120.0, 0.08)
    vol_swap_id = products.create_volatility_swap(5000000, 0.15, 90)
    liq_note_id = products.create_liquidation_notes(2000000, 50, 1.5, 6)
    
    pain_basket = [
        {"metric": "fry_score", "weight": 0.6, "initial_level": 100.0},
        {"metric": "liquidation_rate", "weight": 0.4, "initial_level": 0.1}
    ]
    pain_cert_id = products.create_pain_certificate(3000000, pain_basket, 2.0, 18)
    
    # Simulate market update
    print("\n📊 Updating valuations with FRY Score: 125.5, Vol: 18.2%, Liquidations: 75")
    valuations = products.update_product_valuations(125.5, 0.182, 75)
    
    for product_id, valuation in valuations.items():
        print(f"   {product_id}: {valuation}")
    
    # Show buyer matching
    print(f"\n🎯 Buyer Matching:")
    for product_id in [bond_id, vol_swap_id, liq_note_id, pain_cert_id]:
        buyer = products.match_buyer_to_product(product_id)
        print(f"   {product_id} → {buyer or 'No suitable buyer'}")
    
    # Portfolio summary
    portfolio = products.get_institutional_portfolio()
    print(f"\n📈 Portfolio Summary:")
    print(f"   Total Products: {portfolio['total_products']}")
    print(f"   Total Notional: ${portfolio['total_notional']:,.0f}")
    print(f"   Active Products: {len(portfolio['active_products'])}")

if __name__ == "__main__":
    main()
