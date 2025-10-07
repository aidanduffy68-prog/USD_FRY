# -*- coding: utf-8 -*-
"""
FRY Core v2: Cross-Venue Slippage Engine
Modular slippage estimation for multi-venue trading
"""

import random
import logging

logger = logging.getLogger(__name__)

class VenueConfig:
    """Configuration for a trading venue"""
    
    def __init__(self, name, liquidity_depth, fee_rate, latency_ms=50):
        self.name = name
        self.liquidity_depth = liquidity_depth  # 0.0 to 1.0 scale
        self.fee_rate = fee_rate  # Decimal fee rate
        self.latency_ms = latency_ms
        self.active = True

class SlippageEstimate:
    """Slippage estimation result"""
    
    def __init__(self, aggregate_slippage_pct, venue_slippages, size_impact_factor, total_cost_pct):
        self.aggregate_slippage_pct = aggregate_slippage_pct
        self.venue_slippages = venue_slippages
        self.size_impact_factor = size_impact_factor
        self.total_cost_pct = total_cost_pct
        
    def to_dict(self):
        return {
            "aggregate_slippage_pct": self.aggregate_slippage_pct,
            "venue_slippages": self.venue_slippages,
            "size_impact_factor": self.size_impact_factor,
            "estimated_total_cost_pct": self.total_cost_pct
        }

class CrossVenueSlippageEngine:
    """
    Core v2: Advanced slippage estimation across multiple venues
    """
    
    def __init__(self):
        self.venues = {}
        self._initialize_default_venues()
        
    def _initialize_default_venues(self):
        """Initialize default venue configurations"""
        
        default_venues = [
            VenueConfig("binance", 0.4, 0.001, 30),
            VenueConfig("okx", 0.25, 0.0008, 45),
            VenueConfig("bybit", 0.2, 0.001, 40),
            VenueConfig("kucoin", 0.15, 0.001, 60),
            VenueConfig("mexc", 0.1, 0.002, 80),
            VenueConfig("gate", 0.12, 0.0015, 70)
        ]
        
        for venue in default_venues:
            self.venues[venue.name] = venue
    
    def add_venue(self, venue_config):
        """Add or update venue configuration"""
        self.venues[venue_config.name] = venue_config
        logger.info("Added venue: {} (depth: {:.1%}, fee: {:.3%})".format(
            venue_config.name, venue_config.liquidity_depth, venue_config.fee_rate
        ))
    
    def disable_venue(self, venue_name):
        """Disable a venue from calculations"""
        if venue_name in self.venues:
            self.venues[venue_name].active = False
            logger.info("Disabled venue: {}".format(venue_name))
    
    def estimate_slippage(self, coin_symbol, trade_size_usd, market_cap_usd, volatility_factor=1.0):
        """
        Estimate cross-venue slippage for a trade
        
        Args:
            coin_symbol: Trading pair symbol
            trade_size_usd: Trade size in USD
            market_cap_usd: Market cap of the asset
            volatility_factor: Volatility multiplier (1.0 = normal, >1.0 = high vol)
        """
        
        # Base slippage increases with trade size relative to market cap
        size_impact = trade_size_usd / max(market_cap_usd, 1000000)  # Min $1M cap
        
        venue_slippages = {}
        total_weighted_slippage = 0
        total_weight = 0
        
        active_venues = {name: venue for name, venue in self.venues.items() if venue.active}
        
        if not active_venues:
            logger.warning("No active venues for slippage calculation")
            return SlippageEstimate(0, {}, 0, 0)
        
        for venue_name, venue in active_venues.items():
            # Venue-specific slippage calculation
            depth_factor = 1 / venue.liquidity_depth  # Lower depth = higher slippage
            fee_impact = venue.fee_rate * 2  # Round trip fees
            
            # Base slippage formula: size impact * depth factor + fees
            base_slippage = size_impact * depth_factor * 100  # Convert to percentage
            
            # Market noise and volatility
            noise_factor = random.uniform(0.8, 1.2)  # Market noise
            volatility_impact = volatility_factor * 0.1  # 10% base volatility impact
            
            # Latency impact (higher latency = more slippage risk)
            latency_impact = venue.latency_ms / 1000.0  # Convert to seconds, use as multiplier
            
            venue_slippage = (base_slippage + fee_impact * 100 + volatility_impact) * noise_factor * (1 + latency_impact)
            venue_slippages[venue_name] = venue_slippage
            
            # Weight by liquidity depth for aggregate calculation
            weight = venue.liquidity_depth
            total_weighted_slippage += venue_slippage * weight
            total_weight += weight
        
        aggregate_slippage = total_weighted_slippage / total_weight if total_weight > 0 else 0
        
        logger.debug("Slippage estimate for {} (${:,.0f}): {:.3f}%".format(
            coin_symbol, trade_size_usd, aggregate_slippage
        ))
        
        return SlippageEstimate(
            aggregate_slippage_pct=aggregate_slippage,
            venue_slippages=venue_slippages,
            size_impact_factor=size_impact,
            total_cost_pct=aggregate_slippage
        )
    
    def estimate_optimal_venue_split(self, coin_symbol, trade_size_usd, market_cap_usd):
        """
        Estimate optimal trade splitting across venues to minimize slippage
        """
        
        slippage_estimate = self.estimate_slippage(coin_symbol, trade_size_usd, market_cap_usd)
        venue_slippages = slippage_estimate.venue_slippages
        
        # Sort venues by slippage (best first)
        sorted_venues = sorted(venue_slippages.items(), key=lambda x: x[1])
        
        # Simple allocation: inverse slippage weighting
        total_inverse_slippage = sum(1 / max(slippage, 0.01) for _, slippage in sorted_venues)
        
        venue_allocations = {}
        for venue_name, slippage in sorted_venues:
            weight = (1 / max(slippage, 0.01)) / total_inverse_slippage
            allocation_usd = trade_size_usd * weight
            venue_allocations[venue_name] = {
                "allocation_usd": allocation_usd,
                "allocation_pct": weight * 100,
                "expected_slippage": slippage
            }
        
        return {
            "total_trade_size": trade_size_usd,
            "venue_allocations": venue_allocations,
            "estimated_total_slippage": slippage_estimate.aggregate_slippage_pct,
            "optimization_benefit_pct": max(0, min(venue_slippages.values()) - slippage_estimate.aggregate_slippage_pct)
        }
    
    def get_venue_health_score(self):
        """Calculate health score for all venues"""
        
        health_scores = {}
        
        for venue_name, venue in self.venues.items():
            if not venue.active:
                health_scores[venue_name] = 0
                continue
            
            # Health based on liquidity depth, low fees, low latency
            liquidity_score = venue.liquidity_depth * 40  # Max 40 points
            fee_score = max(0, 30 - (venue.fee_rate * 10000))  # Max 30 points, penalty for high fees
            latency_score = max(0, 30 - (venue.latency_ms / 10))  # Max 30 points, penalty for high latency
            
            total_score = liquidity_score + fee_score + latency_score
            health_scores[venue_name] = min(100, total_score)
        
        return health_scores
    
    def get_system_stats(self):
        """Get system statistics"""
        
        active_venues = sum(1 for venue in self.venues.values() if venue.active)
        total_venues = len(self.venues)
        
        avg_liquidity = sum(venue.liquidity_depth for venue in self.venues.values() if venue.active) / max(active_venues, 1)
        avg_fees = sum(venue.fee_rate for venue in self.venues.values() if venue.active) / max(active_venues, 1)
        
        return {
            "total_venues": total_venues,
            "active_venues": active_venues,
            "average_liquidity_depth": avg_liquidity,
            "average_fee_rate": avg_fees,
            "venue_health_scores": self.get_venue_health_score()
        }
