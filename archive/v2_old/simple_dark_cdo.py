# -*- coding: utf-8 -*-
"""
Simple Dark CDO for Funding Arbitrage Integration
Compatible with older Python versions
"""

import json
import time
import hashlib
import uuid

class LossCollateral:
    """Anonymized loss collateral for dark pool packaging"""
    
    def __init__(self, id, trader_hash, loss_amount_usd, asset, timestamp, leverage, position_size_usd, liquidation=False, failure_type="loss"):
        self.id = id
        self.trader_hash = trader_hash
        self.loss_amount_usd = loss_amount_usd
        self.asset = asset
        self.timestamp = timestamp
        self.leverage = leverage
        self.position_size_usd = position_size_usd
        self.liquidation = liquidation
        self.failure_type = failure_type
        self.fry_minted = 0.0
        self.volatility_multiplier = 1.0

class RektDarkCDO:
    """
    Simple Dark CDO for packaging anonymized trading losses
    """
    
    def __init__(self):
        self.loss_pool = []
        self.active_tranches = []
        self.total_fry_minted = 0.0
        self.total_collateral_swept_usd = 0.0
        
    def sweep_collateral(self, trader_address, loss_amount_usd, asset, leverage, position_size_usd, liquidation=False, position_side=None, harvesting_filter=None, fry_override=None):
        """Sweep trading losses into anonymized collateral pools"""
        
        trader_hash = hashlib.sha256("{}_{}".format(trader_address, time.time()).encode()).hexdigest()[:16]
        
        # Apply directional harvesting filter if specified
        if harvesting_filter:
            if harvesting_filter == "rekt_longs_only" and position_side != "long":
                return None, 0.0
            elif harvesting_filter == "rekt_shorts_only" and position_side != "short":
                return None, 0.0
        
        # Calculate FRY minting
        if fry_override is not None:
            fry_minted = fry_override
            volatility_multiplier = fry_override / max(loss_amount_usd, 1.0)
        else:
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
        """Calculate volatility multiplier for FRY minting"""
        
        base_multiplier = 1.0
        
        # Leverage multiplier (higher leverage = more FRY)
        leverage_bonus = min(2.0, leverage / 10.0)
        
        # Position size multiplier
        size_bonus = min(1.5, position_size_usd / 100000)
        
        # Loss severity multiplier
        loss_severity = min(2.0, loss_amount_usd / 10000)
        
        # Liquidation bonus
        liquidation_bonus = 1.5 if liquidation else 1.0
        
        total_multiplier = base_multiplier + leverage_bonus + size_bonus + loss_severity
        total_multiplier *= liquidation_bonus
        
        return min(50.0, total_multiplier)  # Cap at 50x
    
    def get_market_stats(self):
        """Get current market statistics"""
        
        return {
            "total_collateral_pools": len(self.loss_pool),
            "total_fry_minted": self.total_fry_minted,
            "total_collateral_swept": self.total_collateral_swept_usd,
            "active_tranches": len(self.active_tranches),
            "average_fry_per_loss": self.total_fry_minted / max(len(self.loss_pool), 1)
        }
