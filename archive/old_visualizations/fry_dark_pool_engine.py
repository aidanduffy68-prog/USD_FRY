#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Dark Pool Engine - Aggregation + Minting Layer
Where anonymity + netting happens. Losses are swept, converted into $FRY, and pooled.
The FRY Score (risk index) is computed at this level.
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYDarkPoolEngine:
    """
    Dark Pool Aggregation and Minting Engine
    
    Core Functions:
    1. Anonymize incoming retail losses
    2. Net and aggregate losses across traders
    3. Mint FRY tokens with volatility multipliers
    4. Calculate FRY Score (risk index)
    5. Create anonymized loss pools for institutional distribution
    """
    
    def __init__(self):
        # Anonymization system
        self.anonymization_salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
        self.trader_anonymization_map = {}
        
        # Loss aggregation pools
        self.loss_pools = {
            "high_leverage": [],      # 20x+ leverage losses
            "medium_leverage": [],    # 5-20x leverage losses  
            "low_leverage": [],       # <5x leverage losses
            "liquidation_pool": [],   # All liquidation events
            "whale_losses": []        # $10k+ individual losses
        }
        
        # FRY minting system
        self.total_fry_minted = 0.0
        self.fry_minting_rate = 10.0  # Base: 10 FRY per $1 lost
        self.volatility_multipliers = {
            "liquidation": 5.0,
            "high_leverage": 3.0,
            "whale_loss": 2.0,
            "consistency_bonus": 1.5
        }
        
        # FRY Score calculation
        self.fry_score = 100.0  # Base score
        self.score_components = {
            "loss_velocity": 0.0,      # Rate of incoming losses
            "liquidation_intensity": 0.0,  # Liquidation frequency
            "leverage_distribution": 0.0,   # Average leverage of losses
            "whale_activity": 0.0,     # Large loss frequency
            "volatility_index": 0.0    # Overall market volatility
        }
        self.score_history = []
        
        # Netting and aggregation
        self.netting_windows = {
            "real_time": timedelta(minutes=5),
            "short_term": timedelta(hours=1), 
            "medium_term": timedelta(hours=6),
            "daily": timedelta(days=1)
        }
        
        logger.info("🌊 FRY Dark Pool Engine initialized")
    
    def anonymize_trader(self, wallet_address: str) -> str:
        """
        Anonymize trader identity for dark pool processing
        Creates consistent but untraceable trader hash
        """
        if wallet_address not in self.trader_anonymization_map:
            # Create anonymized hash
            trader_hash = hashlib.sha256(
                f"{wallet_address}_{self.anonymization_salt}_{len(self.trader_anonymization_map)}".encode()
            ).hexdigest()[:16]
            
            self.trader_anonymization_map[wallet_address] = trader_hash
            logger.debug("🎭 Anonymized trader: {}... → {}".format(wallet_address[:8], trader_hash))
        
        return self.trader_anonymization_map[wallet_address]
    
    def calculate_volatility_multiplier(self, loss_event: Dict) -> float:
        """
        Calculate FRY minting multiplier based on loss characteristics
        Higher volatility/risk = higher FRY minting rate
        """
        base_multiplier = 1.0
        
        # Liquidation bonus
        if loss_event.get("liquidation", False):
            base_multiplier *= self.volatility_multipliers["liquidation"]
        
        # Leverage multiplier
        leverage = loss_event.get("leverage", 1.0)
        if leverage >= 20:
            base_multiplier *= self.volatility_multipliers["high_leverage"]
        elif leverage >= 10:
            base_multiplier *= 2.0
        elif leverage >= 5:
            base_multiplier *= 1.5
        
        # Whale loss bonus
        if loss_event["loss_amount"] >= 10000:
            base_multiplier *= self.volatility_multipliers["whale_loss"]
        elif loss_event["loss_amount"] >= 5000:
            base_multiplier *= 1.5
        
        # Cap multiplier at 50x
        return min(base_multiplier, 50.0)
    
    def mint_fry_tokens(self, loss_event: Dict) -> float:
        """
        Mint FRY tokens from anonymized loss event
        Core value creation mechanism of the dark pool
        """
        volatility_multiplier = self.calculate_volatility_multiplier(loss_event)
        fry_minted = loss_event["loss_amount"] * self.fry_minting_rate * volatility_multiplier
        
        # Update totals
        self.total_fry_minted += fry_minted
        
        # Add minting metadata to loss event
        loss_event["fry_minted"] = fry_minted
        loss_event["volatility_multiplier"] = volatility_multiplier
        loss_event["minting_timestamp"] = datetime.now().isoformat()
        
        logger.info("🪙 Minted {:.2f} FRY from ${:.2f} loss ({}x multiplier)".format(
            fry_minted, loss_event["loss_amount"], volatility_multiplier
        ))
        
        return fry_minted
    
    def aggregate_losses_into_pools(self, loss_events: List[Dict]):
        """
        Aggregate and net losses into categorized pools
        Creates structured loss products for institutional distribution
        """
        for loss_event in loss_events:
            # Anonymize trader
            loss_event["anonymized_trader"] = self.anonymize_trader(loss_event["wallet_address"])
            
            # Mint FRY tokens
            self.mint_fry_tokens(loss_event)
            
            # Categorize into pools
            leverage = loss_event.get("leverage", 1.0)
            loss_amount = loss_event["loss_amount"]
            
            if loss_event.get("liquidation", False):
                self.loss_pools["liquidation_pool"].append(loss_event)
            
            if loss_amount >= 10000:
                self.loss_pools["whale_losses"].append(loss_event)
            elif leverage >= 5:
                self.loss_pools["medium_leverage"].append(loss_event)
            else:
                self.loss_pools["low_leverage"].append(loss_event)
        
        logger.info("🌊 Aggregated {} losses into dark pools".format(len(loss_events)))
    
    def calculate_fry_score_components(self):
        """
        Calculate individual components of the FRY Score
        Risk index based on dark pool activity
        """
        # Get recent activity (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        
        all_recent_losses = []
        for pool in self.loss_pools.values():
            for loss in pool:
                if datetime.fromisoformat(loss["minting_timestamp"]) > recent_cutoff:
                    all_recent_losses.append(loss)
        
        if not all_recent_losses:
            return
        
        # Loss velocity (losses per hour)
        self.score_components["loss_velocity"] = len(all_recent_losses)
        
        # Liquidation intensity
        liquidations = sum(1 for loss in all_recent_losses if loss.get("liquidation", False))
        self.score_components["liquidation_intensity"] = liquidations / max(len(all_recent_losses), 1) * 100
        
        # Average leverage
        leverages = [loss.get("leverage", 1.0) for loss in all_recent_losses]
        self.score_components["leverage_distribution"] = np.mean(leverages) if leverages else 1.0
        
        # Whale activity (large losses)
        whale_losses = sum(1 for loss in all_recent_losses if loss["loss_amount"] >= 10000)
        self.score_components["whale_activity"] = whale_losses
        
        # Volatility index (based on FRY multipliers)
        multipliers = [loss.get("volatility_multiplier", 1.0) for loss in all_recent_losses]
        self.score_components["volatility_index"] = np.mean(multipliers) if multipliers else 1.0
    
    def update_fry_score(self):
        """
        Update the FRY Score based on dark pool activity
        Central risk index for institutional product benchmarking
        """
        self.calculate_fry_score_components()
        
        # Weighted FRY Score calculation
        score_weights = {
            "loss_velocity": 0.25,
            "liquidation_intensity": 0.30,
            "leverage_distribution": 0.20,
            "whale_activity": 0.15,
            "volatility_index": 0.10
        }
        
        weighted_score = 0.0
        for component, weight in score_weights.items():
            component_value = self.score_components[component]
            
            # Normalize components to 0-100 scale
            if component == "loss_velocity":
                normalized = min(component_value * 2, 100)  # 50 losses/hour = 100
            elif component == "liquidation_intensity":
                normalized = min(component_value, 100)  # Already percentage
            elif component == "leverage_distribution":
                normalized = min(component_value * 4, 100)  # 25x leverage = 100
            elif component == "whale_activity":
                normalized = min(component_value * 10, 100)  # 10 whale losses = 100
            elif component == "volatility_index":
                normalized = min(component_value * 20, 100)  # 5x avg multiplier = 100
            else:
                normalized = 0
            
            weighted_score += normalized * weight
        
        # Exponential moving average (0.3 alpha for responsiveness)
        self.fry_score = (0.7 * self.fry_score) + (0.3 * weighted_score)
        
        # Record score history
        self.score_history.append({
            "timestamp": datetime.now().isoformat(),
            "score": self.fry_score,
            "components": self.score_components.copy()
        })
        
        # Keep last 100 records
        if len(self.score_history) > 100:
            self.score_history = self.score_history[-100:]
        
        logger.info("📊 FRY Score updated: {:.2f}".format(self.fry_score))
    
    def get_pool_statistics(self) -> Dict:
        """
        Get comprehensive dark pool statistics
        """
        pool_stats = {}
        total_losses = 0.0
        total_events = 0
        
        for pool_name, pool_events in self.loss_pools.items():
            pool_loss_total = sum(event["loss_amount"] for event in pool_events)
            pool_fry_total = sum(event.get("fry_minted", 0) for event in pool_events)
            
            pool_stats[pool_name] = {
                "event_count": len(pool_events),
                "total_losses": pool_loss_total,
                "total_fry_minted": pool_fry_total,
                "avg_loss": pool_loss_total / max(len(pool_events), 1),
                "avg_multiplier": np.mean([e.get("volatility_multiplier", 1.0) for e in pool_events]) if pool_events else 1.0
            }
            
            total_losses += pool_loss_total
            total_events += len(pool_events)
        
        return {
            "pool_breakdown": pool_stats,
            "aggregate_stats": {
                "total_loss_events": total_events,
                "total_losses_processed": total_losses,
                "total_fry_minted": self.total_fry_minted,
                "avg_fry_per_dollar": self.total_fry_minted / max(total_losses, 1),
                "anonymized_traders": len(self.trader_anonymization_map)
            },
            "fry_score": {
                "current_score": self.fry_score,
                "components": self.score_components,
                "score_trend": self._calculate_score_trend()
            }
        }
    
    def _calculate_score_trend(self) -> str:
        """Calculate FRY Score trend from recent history"""
        if len(self.score_history) < 2:
            return "stable"
        
        recent_scores = [s["score"] for s in self.score_history[-5:]]
        if recent_scores[-1] > recent_scores[0] * 1.05:
            return "increasing"
        elif recent_scores[-1] < recent_scores[0] * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def process_harvested_losses(self, harvested_losses: List[Dict]) -> Dict:
        """
        Main processing function: convert harvested losses into dark pool assets
        """
        if not harvested_losses:
            return {"message": "No losses to process"}
        
        logger.info("🌊 Processing {} harvested losses in dark pool".format(len(harvested_losses)))
        
        # Aggregate losses into pools
        self.aggregate_losses_into_pools(harvested_losses)
        
        # Update FRY Score
        self.update_fry_score()
        
        # Return processing summary
        processing_summary = {
            "timestamp": datetime.now().isoformat(),
            "losses_processed": len(harvested_losses),
            "total_loss_amount": sum(loss["loss_amount"] for loss in harvested_losses),
            "total_fry_minted": sum(loss.get("fry_minted", 0) for loss in harvested_losses),
            "new_fry_score": self.fry_score,
            "anonymized_traders": len(set(loss["wallet_address"] for loss in harvested_losses))
        }
        
        logger.info("🌊 Dark pool processing complete: {:.2f} FRY minted, Score: {:.2f}".format(
            processing_summary["total_fry_minted"], 
            processing_summary["new_fry_score"]
        ))
        
        return processing_summary

def main():
    """
    Demo the dark pool aggregation and minting engine
    """
    print("🌊 FRY Dark Pool Engine - Aggregation + Minting Layer")
    print("Function: Anonymize, net, mint FRY, calculate FRY Score")
    
    dark_pool = FRYDarkPoolEngine()
    
    # Sample harvested losses (from harvesting engine)
    sample_losses = [
        {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "loss_amount": 2500.0,
            "leverage": 15.0,
            "liquidation": True,
            "asset": "BTC"
        },
        {
            "wallet_address": "0x2345678901bcdef12345678901bcdef123456789", 
            "loss_amount": 1200.0,
            "leverage": 8.0,
            "liquidation": False,
            "asset": "ETH"
        },
        {
            "wallet_address": "0x3456789012cdef123456789012cdef1234567890",
            "loss_amount": 15000.0,
            "leverage": 25.0,
            "liquidation": True,
            "asset": "SOL"
        }
    ]
    
    # Process losses through dark pool
    print(f"\n🌊 Processing {len(sample_losses)} harvested losses...")
    result = dark_pool.process_harvested_losses(sample_losses)
    
    print(f"\n📊 Processing Results:")
    print(f"   Total Loss Amount: ${result['total_loss_amount']:,.2f}")
    print(f"   FRY Tokens Minted: {result['total_fry_minted']:,.2f}")
    print(f"   FRY Score: {result['new_fry_score']:.2f}")
    print(f"   Anonymized Traders: {result['anonymized_traders']}")
    
    # Show pool statistics
    stats = dark_pool.get_pool_statistics()
    print(f"\n🏊 Dark Pool Statistics:")
    for pool_name, pool_stats in stats["pool_breakdown"].items():
        if pool_stats["event_count"] > 0:
            print(f"   {pool_name}: {pool_stats['event_count']} events, ${pool_stats['total_losses']:,.0f}")
    
    print(f"\n🎯 FRY Score Components:")
    for component, value in stats["fry_score"]["components"].items():
        print(f"   {component}: {value:.2f}")
    
    print(f"\n✅ Dark pool ready to supply institutional distribution layer")

if __name__ == "__main__":
    main()
