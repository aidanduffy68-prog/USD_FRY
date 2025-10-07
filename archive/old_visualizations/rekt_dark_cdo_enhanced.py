#!/usr/bin/env python3
"""
Enhanced Rekt Dark CDO System
Integrates sophisticated dark pool manipulation strategies with institutional-grade
collateral sweeping, anonymized failure flows, and CDO tranche creation.

Based on memories of the previously successful Rekt Dark CDO deployment.
"""

import asyncio
import json
import time
import random
import numpy as np
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrancheRating(Enum):
    AAA = "AAA"
    AA = "AA" 
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"

class InstitutionalBuyer(Enum):
    BINANCE_VENTURES = "Binance Ventures"
    WINTERMUTE = "Wintermute"
    ALAMEDA_RESEARCH = "Alameda Research"
    CITADEL_SECURITIES = "Citadel Securities"
    GIC_SINGAPORE = "GIC Singapore"
    JUMP_TRADING = "Jump Trading"
    THREE_ARROWS = "Three Arrows Capital"
    GALAXY_DIGITAL = "Galaxy Digital"

@dataclass
class LossCollateral:
    """Anonymized loss collateral for dark pool packaging"""
    id: str
    trader_hash: str  # Anonymized trader identity
    loss_amount_usd: float
    asset: str
    timestamp: int
    leverage: float
    position_size_usd: float
    liquidation: bool
    fry_minted: float
    volatility_multiplier: float
    failure_classification: str  # "overleveraged", "cascade", "manipulation", "organic"
    
@dataclass
class CDOTranche:
    """Collateralized Debt Obligation tranche backed by trading failures"""
    id: str
    rating: TrancheRating
    collateral_pool: List[LossCollateral]
    total_value_usd: float
    yield_rate: float
    minimum_purchase: float
    risk_score: float
    created_timestamp: int
    buyer: Optional[InstitutionalBuyer] = None
    purchase_timestamp: Optional[int] = None
    
@dataclass
class InstitutionalProfile:
    """Institutional buyer risk profile and preferences"""
    buyer: InstitutionalBuyer
    preferred_ratings: List[TrancheRating]
    minimum_yield: float
    maximum_risk_score: float
    capital_available: float
    purchase_history: List[str]  # Tranche IDs

class RektDarkCDO:
    """Enhanced Rekt Dark CDO with institutional integration"""
    
    def __init__(self):
        self.loss_pool: List[LossCollateral] = []
        self.active_tranches: Dict[str, CDOTranche] = {}
        self.institutional_buyers: Dict[InstitutionalBuyer, InstitutionalProfile] = {}
        self.total_fry_minted = 0.0
        self.total_collateral_swept_usd = 0.0
        self.tranche_counter = 0
        self.anonymization_salt = hashlib.sha256(str(time.time()).encode()).hexdigest()
        
        # Initialize institutional buyers with realistic profiles
        self._initialize_institutional_buyers()
        
    def _initialize_institutional_buyers(self):
        """Initialize institutional buyer profiles based on memory data"""
        
        profiles = {
            InstitutionalBuyer.BINANCE_VENTURES: InstitutionalProfile(
                buyer=InstitutionalBuyer.BINANCE_VENTURES,
                preferred_ratings=[TrancheRating.AAA, TrancheRating.AA],
                minimum_yield=0.02,
                maximum_risk_score=2.0,
                capital_available=500_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.WINTERMUTE: InstitutionalProfile(
                buyer=InstitutionalBuyer.WINTERMUTE,
                preferred_ratings=[TrancheRating.A, TrancheRating.BBB],
                minimum_yield=0.05,
                maximum_risk_score=4.0,
                capital_available=200_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.ALAMEDA_RESEARCH: InstitutionalProfile(
                buyer=InstitutionalBuyer.ALAMEDA_RESEARCH,
                preferred_ratings=[TrancheRating.BB, TrancheRating.B],
                minimum_yield=0.12,
                maximum_risk_score=7.0,
                capital_available=300_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.CITADEL_SECURITIES: InstitutionalProfile(
                buyer=InstitutionalBuyer.CITADEL_SECURITIES,
                preferred_ratings=[TrancheRating.AAA],
                minimum_yield=0.015,
                maximum_risk_score=1.5,
                capital_available=1_000_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.GIC_SINGAPORE: InstitutionalProfile(
                buyer=InstitutionalBuyer.GIC_SINGAPORE,
                preferred_ratings=[TrancheRating.AAA, TrancheRating.AA, TrancheRating.A],
                minimum_yield=0.03,
                maximum_risk_score=3.0,
                capital_available=800_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.JUMP_TRADING: InstitutionalProfile(
                buyer=InstitutionalBuyer.JUMP_TRADING,
                preferred_ratings=[TrancheRating.B, TrancheRating.CCC],
                minimum_yield=0.18,
                maximum_risk_score=9.0,
                capital_available=150_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.THREE_ARROWS: InstitutionalProfile(
                buyer=InstitutionalBuyer.THREE_ARROWS,
                preferred_ratings=[TrancheRating.CCC],
                minimum_yield=0.25,
                maximum_risk_score=10.0,
                capital_available=100_000_000,
                purchase_history=[]
            ),
            InstitutionalBuyer.GALAXY_DIGITAL: InstitutionalProfile(
                buyer=InstitutionalBuyer.GALAXY_DIGITAL,
                preferred_ratings=[TrancheRating.BBB, TrancheRating.BB],
                minimum_yield=0.08,
                maximum_risk_score=5.5,
                capital_available=250_000_000,
                purchase_history=[]
            )
        }
        
        self.institutional_buyers = profiles
        logger.info(f"🏦 Initialized {len(profiles)} institutional buyer profiles")
    
    def sweep_collateral(self, trader_address: str, loss_amount_usd: float, 
                        asset: str, leverage: float, position_size_usd: float,
                        liquidation: bool = False, failure_type: str = "organic") -> Tuple[str, float]:
        """
        Sweep trading losses into anonymized collateral pool
        
        Args:
            trader_address: Original trader address (will be anonymized)
            loss_amount_usd: USD value of the loss
            asset: Asset that was traded
            leverage: Leverage used in the position
            position_size_usd: Total position size
            liquidation: Whether this was a liquidation event
            failure_type: Classification of failure ("overleveraged", "cascade", "manipulation", "organic")
        
        Returns:
            Tuple of (collateral_id, fry_minted)
        """
        
        # Anonymize trader identity using salt + hash
        trader_hash = hashlib.sha256(f"{trader_address}_{self.anonymization_salt}_{time.time()}".encode()).hexdigest()[:16]
        
        # Calculate volatility multiplier based on failure characteristics
        volatility_multiplier = self._calculate_volatility_multiplier(
            leverage, position_size_usd, loss_amount_usd, liquidation, failure_type
        )
        
        # Mint FRY tokens at 1:1 peg with volatility multipliers
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
            fry_minted=fry_minted,
            volatility_multiplier=volatility_multiplier,
            failure_classification=failure_type
        )
        
        self.loss_pool.append(collateral)
        self.total_fry_minted += fry_minted
        self.total_collateral_swept_usd += loss_amount_usd
        
        logger.info(f"💸 Swept ${loss_amount_usd:,.0f} loss → {fry_minted:,.0f} FRY (trader: {trader_hash})")
        
        return collateral.id, fry_minted
    
    def _calculate_volatility_multiplier(self, leverage: float, position_size_usd: float, 
                                       loss_amount_usd: float, liquidation: bool, 
                                       failure_type: str) -> float:
        """Calculate volatility multiplier based on failure characteristics"""
        
        # Base multipliers
        leverage_multiplier = min(leverage / 10, 10.0)
        size_multiplier = min(position_size_usd / 10000, 5.0)
        loss_severity = loss_amount_usd / max(position_size_usd, 1)
        severity_multiplier = min(loss_severity * 2, 3.0)
        liquidation_multiplier = 2.0 if liquidation else 1.0
        
        # Failure type multipliers (authentic pain pricing)
        failure_multipliers = {
            "organic": 1.0,
            "overleveraged": 1.5,
            "cascade": 2.0,
            "manipulation": 3.0  # Highest multiplier for manipulation victims
        }
        
        failure_multiplier = failure_multipliers.get(failure_type, 1.0)
        
        total_multiplier = min(
            leverage_multiplier * size_multiplier * severity_multiplier * 
            liquidation_multiplier * failure_multiplier,
            50.0  # Cap at 50x multiplier
        )
        
        return max(total_multiplier, 1.0)
    
    def create_cdo_tranche(self, target_rating: TrancheRating, 
                          target_value_usd: float = 10_000_000) -> Optional[str]:
        """
        Create a CDO tranche from available loss collateral
        
        Args:
            target_rating: Desired tranche rating
            target_value_usd: Target tranche value in USD
            
        Returns:
            Tranche ID if successful, None if insufficient collateral
        """
        
        if not self.loss_pool:
            logger.warning("⚠️ No collateral available for tranche creation")
            return None
        
        # Select appropriate collateral based on rating requirements
        suitable_collateral = self._select_collateral_for_rating(target_rating, target_value_usd)
        
        if not suitable_collateral:
            logger.warning(f"⚠️ Insufficient suitable collateral for {target_rating.value} tranche")
            return None
        
        # Calculate tranche characteristics
        total_value = sum(c.loss_amount_usd for c in suitable_collateral)
        risk_score = self._calculate_tranche_risk_score(suitable_collateral, target_rating)
        yield_rate = self._calculate_yield_rate(target_rating, risk_score)
        minimum_purchase = self._get_minimum_purchase(target_rating)
        
        tranche_id = f"REKT-{target_rating.value}-{self.tranche_counter:04d}"
        self.tranche_counter += 1
        
        tranche = CDOTranche(
            id=tranche_id,
            rating=target_rating,
            collateral_pool=suitable_collateral,
            total_value_usd=total_value,
            yield_rate=yield_rate,
            minimum_purchase=minimum_purchase,
            risk_score=risk_score,
            created_timestamp=int(time.time() * 1000)
        )
        
        self.active_tranches[tranche_id] = tranche
        
        # Remove used collateral from pool
        for collateral in suitable_collateral:
            if collateral in self.loss_pool:
                self.loss_pool.remove(collateral)
        
        logger.info(f"📦 Created {target_rating.value} tranche {tranche_id}: ${total_value:,.0f} @ {yield_rate*100:.1f}% yield")
        
        return tranche_id
    
    def _select_collateral_for_rating(self, rating: TrancheRating, 
                                    target_value: float) -> List[LossCollateral]:
        """Select appropriate collateral for the target rating"""
        
        # Rating requirements (lower risk score = higher rating)
        rating_requirements = {
            TrancheRating.AAA: {"max_leverage": 10, "max_volatility": 2.0, "min_size": 50000},
            TrancheRating.AA: {"max_leverage": 20, "max_volatility": 3.0, "min_size": 25000},
            TrancheRating.A: {"max_leverage": 35, "max_volatility": 5.0, "min_size": 10000},
            TrancheRating.BBB: {"max_leverage": 50, "max_volatility": 8.0, "min_size": 5000},
            TrancheRating.BB: {"max_leverage": 75, "max_volatility": 15.0, "min_size": 2000},
            TrancheRating.B: {"max_leverage": 90, "max_volatility": 25.0, "min_size": 1000},
            TrancheRating.CCC: {"max_leverage": 100, "max_volatility": 50.0, "min_size": 500}
        }
        
        requirements = rating_requirements[rating]
        
        # Filter collateral based on rating requirements
        suitable = []
        current_value = 0.0
        
        # Sort by quality (lower volatility multiplier = higher quality)
        sorted_collateral = sorted(self.loss_pool, key=lambda x: x.volatility_multiplier)
        
        for collateral in sorted_collateral:
            if (collateral.leverage <= requirements["max_leverage"] and
                collateral.volatility_multiplier <= requirements["max_volatility"] and
                collateral.position_size_usd >= requirements["min_size"]):
                
                suitable.append(collateral)
                current_value += collateral.loss_amount_usd
                
                if current_value >= target_value:
                    break
        
        return suitable
    
    def _calculate_tranche_risk_score(self, collateral_pool: List[LossCollateral], 
                                    rating: TrancheRating) -> float:
        """Calculate risk score for the tranche"""
        
        if not collateral_pool:
            return 10.0  # Maximum risk
        
        # Average volatility multiplier as base risk
        avg_volatility = sum(c.volatility_multiplier for c in collateral_pool) / len(collateral_pool)
        
        # Adjust for failure types
        manipulation_ratio = sum(1 for c in collateral_pool if c.failure_classification == "manipulation") / len(collateral_pool)
        liquidation_ratio = sum(1 for c in collateral_pool if c.liquidation) / len(collateral_pool)
        
        risk_score = avg_volatility * (1 + manipulation_ratio + liquidation_ratio)
        
        return min(risk_score, 10.0)
    
    def _calculate_yield_rate(self, rating: TrancheRating, risk_score: float) -> float:
        """Calculate yield rate based on rating and risk"""
        
        base_yields = {
            TrancheRating.AAA: 0.02,   # 2%
            TrancheRating.AA: 0.04,    # 4%
            TrancheRating.A: 0.06,     # 6%
            TrancheRating.BBB: 0.10,   # 10%
            TrancheRating.BB: 0.15,    # 15%
            TrancheRating.B: 0.22,     # 22%
            TrancheRating.CCC: 0.30    # 30%
        }
        
        base_yield = base_yields[rating]
        risk_premium = risk_score * 0.01  # 1% per risk point
        
        return min(base_yield + risk_premium, 0.50)  # Cap at 50%
    
    def _get_minimum_purchase(self, rating: TrancheRating) -> float:
        """Get minimum purchase amount for rating"""
        
        minimums = {
            TrancheRating.AAA: 1_000_000,   # $1M
            TrancheRating.AA: 500_000,      # $500K
            TrancheRating.A: 250_000,       # $250K
            TrancheRating.BBB: 100_000,     # $100K
            TrancheRating.BB: 50_000,       # $50K
            TrancheRating.B: 25_000,        # $25K
            TrancheRating.CCC: 10_000       # $10K
        }
        
        return minimums[rating]
    
    def match_institutional_buyer(self, tranche_id: str) -> Optional[InstitutionalBuyer]:
        """Match a tranche with an appropriate institutional buyer"""
        
        if tranche_id not in self.active_tranches:
            return None
        
        tranche = self.active_tranches[tranche_id]
        
        # Find buyers interested in this rating
        interested_buyers = []
        for buyer, profile in self.institutional_buyers.items():
            if (tranche.rating in profile.preferred_ratings and
                tranche.yield_rate >= profile.minimum_yield and
                tranche.risk_score <= profile.maximum_risk_score and
                tranche.total_value_usd <= profile.capital_available):
                interested_buyers.append((buyer, profile))
        
        if not interested_buyers:
            return None
        
        # Select buyer (could be random or based on best match)
        selected_buyer, profile = random.choice(interested_buyers)
        
        # Execute purchase
        tranche.buyer = selected_buyer
        tranche.purchase_timestamp = int(time.time() * 1000)
        profile.capital_available -= tranche.total_value_usd
        profile.purchase_history.append(tranche_id)
        
        logger.info(f"🤝 {selected_buyer.value} purchased tranche {tranche_id} for ${tranche.total_value_usd:,.0f}")
        
        return selected_buyer
    
    def execute_manipulation_sweep(self, manipulation_results: Dict) -> Dict:
        """
        Process manipulation results and sweep collateral into dark pool
        
        Args:
            manipulation_results: Results from dark pool manipulation simulation
            
        Returns:
            Summary of collateral swept and tranches created
        """
        
        logger.info("🕳️ Processing manipulation results for collateral sweeping...")
        
        sweep_summary = {
            "collateral_swept": 0,
            "fry_minted": 0.0,
            "tranches_created": [],
            "institutional_purchases": []
        }
        
        # Process liquidations from manipulation
        liquidations = manipulation_results.get("liquidations", [])
        
        for liquidation in liquidations:
            trader_id = liquidation["trader_id"]
            loss_usd = liquidation["loss_usd"]
            leverage = liquidation["leverage"]
            
            # Sweep the loss as manipulation-type failure
            collateral_id, fry_minted = self.sweep_collateral(
                trader_address=trader_id,
                loss_amount_usd=loss_usd,
                asset="BTC",  # Assuming BTC manipulation
                leverage=leverage,
                position_size_usd=loss_usd * leverage,
                liquidation=True,
                failure_type="manipulation"
            )
            
            sweep_summary["collateral_swept"] += 1
            sweep_summary["fry_minted"] += fry_minted
        
        # Create CDO tranches from swept collateral
        ratings_to_create = [TrancheRating.AAA, TrancheRating.A, TrancheRating.BBB, 
                           TrancheRating.BB, TrancheRating.CCC]
        
        for rating in ratings_to_create:
            tranche_id = self.create_cdo_tranche(rating)
            if tranche_id:
                sweep_summary["tranches_created"].append(tranche_id)
                
                # Try to match with institutional buyer
                buyer = self.match_institutional_buyer(tranche_id)
                if buyer:
                    sweep_summary["institutional_purchases"].append({
                        "tranche_id": tranche_id,
                        "buyer": buyer.value,
                        "rating": rating.value
                    })
        
        logger.info(f"🏦 Sweep complete: {sweep_summary['collateral_swept']} losses → {len(sweep_summary['tranches_created'])} tranches")
        
        return sweep_summary
    
    def get_market_stats(self) -> Dict:
        """Get comprehensive market statistics"""
        
        # Calculate utilization
        total_tranche_value = sum(t.total_value_usd for t in self.active_tranches.values())
        utilization = (total_tranche_value / max(self.total_collateral_swept_usd, 1)) * 100
        
        # Count purchases
        purchased_tranches = sum(1 for t in self.active_tranches.values() if t.buyer is not None)
        
        # Rating distribution
        rating_distribution = {}
        for rating in TrancheRating:
            count = sum(1 for t in self.active_tranches.values() if t.rating == rating)
            rating_distribution[rating.value] = count
        
        return {
            "total_fry_minted": self.total_fry_minted,
            "total_collateral_swept_usd": self.total_collateral_swept_usd,
            "active_tranches": len(self.active_tranches),
            "purchased_tranches": purchased_tranches,
            "losses_in_pool": len(self.loss_pool),
            "market_utilization_percent": utilization,
            "rating_distribution": rating_distribution,
            "institutional_buyers_active": len([b for b in self.institutional_buyers.values() if b.purchase_history])
        }
    
    def export_market_data(self, filename: str = "rekt_dark_cdo_market.json"):
        """Export comprehensive market data"""
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "market_stats": self.get_market_stats(),
            "active_tranches": {
                tid: {
                    "id": t.id,
                    "rating": t.rating.value,
                    "total_value_usd": t.total_value_usd,
                    "yield_rate": t.yield_rate,
                    "risk_score": t.risk_score,
                    "buyer": t.buyer.value if t.buyer else None,
                    "collateral_count": len(t.collateral_pool)
                }
                for tid, t in self.active_tranches.items()
            },
            "institutional_activity": {
                buyer.value: {
                    "capital_remaining": profile.capital_available,
                    "purchases_made": len(profile.purchase_history),
                    "preferred_ratings": [r.value for r in profile.preferred_ratings]
                }
                for buyer, profile in self.institutional_buyers.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"📊 Market data exported to {filename}")

def main():
    """Demonstrate enhanced Rekt Dark CDO functionality"""
    
    print("🚀 Enhanced Rekt Dark CDO System Demo")
    print("="*50)
    
    # Initialize CDO system
    cdo = RektDarkCDO()
    
    # Simulate some organic trading losses
    organic_losses = [
        ("trader_001", 5000, "BTC", 10, 50000, False, "organic"),
        ("trader_002", 15000, "ETH", 25, 375000, True, "overleveraged"),
        ("trader_003", 8000, "SOL", 50, 400000, True, "cascade"),
        ("trader_004", 25000, "BTC", 75, 1875000, True, "manipulation"),
        ("trader_005", 3000, "ETH", 5, 15000, False, "organic")
    ]
    
    print(f"\n💸 Sweeping {len(organic_losses)} trading losses into dark pool...")
    
    for trader, loss, asset, leverage, size, liquidation, failure_type in organic_losses:
        cdo.sweep_collateral(trader, loss, asset, leverage, size, liquidation, failure_type)
    
    # Create CDO tranches
    print(f"\n📦 Creating CDO tranches from collateral pool...")
    
    ratings_to_create = [TrancheRating.AAA, TrancheRating.A, TrancheRating.BBB, TrancheRating.B, TrancheRating.CCC]
    
    for rating in ratings_to_create:
        tranche_id = cdo.create_cdo_tranche(rating, target_value_usd=50000)  # Smaller tranches for demo
        if tranche_id:
            # Try to match with institutional buyer
            buyer = cdo.match_institutional_buyer(tranche_id)
            if buyer:
                print(f"   ✅ {rating.value} tranche purchased by {buyer.value}")
    
    # Display market statistics
    print(f"\n📊 Market Statistics:")
    stats = cdo.get_market_stats()
    
    print(f"   FRY Minted: {stats['total_fry_minted']:,.0f} tokens")
    print(f"   Collateral Swept: ${stats['total_collateral_swept_usd']:,.0f}")
    print(f"   Active Tranches: {stats['active_tranches']}")
    print(f"   Purchased Tranches: {stats['purchased_tranches']}")
    print(f"   Market Utilization: {stats['market_utilization_percent']:.1f}%")
    
    print(f"\n🏦 Rating Distribution:")
    for rating, count in stats['rating_distribution'].items():
        if count > 0:
            print(f"   {rating}: {count} tranches")
    
    # Export market data
    cdo.export_market_data("demo_market_data.json")
    
    print(f"\n✅ Enhanced Rekt Dark CDO demo complete!")
    print(f"🔗 Market creates liquid investment products from trading failures")
    print(f"🕳️ Anonymized loss flows protect trader privacy while enabling institutional access")

if __name__ == "__main__":
    main()
