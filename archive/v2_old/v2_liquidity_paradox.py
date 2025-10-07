# -*- coding: utf-8 -*-
"""
FRY Core v2: Liquidity Paradox Index
Mathematical model for detecting liquidity feedback loops
"""

import time
import math
import logging

logger = logging.getLogger(__name__)

class ParadoxMetrics:
    """Container for paradox calculation metrics"""
    
    def __init__(self, paradox_score, liquidity_ratio, drain_factor, arbitrage_intensity, feedback_active, components):
        self.paradox_score = paradox_score
        self.liquidity_ratio = liquidity_ratio
        self.drain_factor = drain_factor
        self.arbitrage_intensity = arbitrage_intensity
        self.feedback_active = feedback_active
        self.components = components
        
    def to_dict(self):
        return {
            "paradox_score": self.paradox_score,
            "liquidity_ratio": self.liquidity_ratio,
            "drain_factor": self.drain_factor,
            "arbitrage_intensity": self.arbitrage_intensity,
            "feedback_active": self.feedback_active,
            "components": self.components
        }

class LiquidityParadoxEngine:
    """
    Core v2: Advanced liquidity paradox detection system
    
    Models the theoretical paradox where arbitrage opportunities increase
    as liquidity decreases, creating dangerous feedback loops
    """
    
    def __init__(self, config=None):
        # Default configuration
        default_config = {
            "baseline_liquidity": 1000000,    # $1M baseline
            "paradox_threshold": 0.75,        # Paradox triggers at 75% liquidity drain
            "feedback_multiplier": 2.5,       # Feedback loop amplification
            "velocity_weight": 0.3,           # Weight for arbitrage velocity
            "concentration_weight": 0.4,      # Weight for market concentration
            "volatility_weight": 0.3,         # Weight for volatility impact
            "time_decay_factor": 0.95         # Decay factor for historical data
        }
        
        self.config = default_config.copy()
        if config:
            self.config.update(config)
        self.historical_data = []
        self.max_history_points = 100
        
    def calculate_paradox_score(self, current_liquidity, arbitrage_volume, time_window_minutes, additional_metrics=None):
        """
        Calculate comprehensive liquidity paradox index (0-100 scale)
        
        Args:
            current_liquidity: Current market liquidity in USD
            arbitrage_volume: Total arbitrage volume in time window
            time_window_minutes: Time window for calculations
            additional_metrics: Optional dict with extra metrics
        """
        
        # Core liquidity metrics
        liquidity_ratio = current_liquidity / self.config["baseline_liquidity"]
        drain_factor = max(0, 1 - liquidity_ratio)
        
        # Arbitrage intensity (volume per minute)
        arbitrage_intensity = arbitrage_volume / max(time_window_minutes, 1)
        
        # Component calculations
        components = self._calculate_paradox_components(
            drain_factor, arbitrage_intensity, additional_metrics or {}
        )
        
        # Base paradox calculation
        paradox_base = (drain_factor * arbitrage_intensity) / 10000
        
        # Apply component weights
        velocity_impact = components["velocity_score"] * self.config["velocity_weight"]
        concentration_impact = components["concentration_score"] * self.config["concentration_weight"]
        volatility_impact = components["volatility_score"] * self.config["volatility_weight"]
        
        weighted_paradox = paradox_base * (1 + velocity_impact + concentration_impact + volatility_impact)
        
        # Feedback loop amplification
        feedback_active = drain_factor > self.config["paradox_threshold"]
        if feedback_active:
            feedback_amplification = self.config["feedback_multiplier"] * (drain_factor - self.config["paradox_threshold"])
            weighted_paradox *= (1 + feedback_amplification)
        
        # Scale to 0-100 and apply historical smoothing
        paradox_score = min(100, weighted_paradox * 100)
        smoothed_score = self._apply_historical_smoothing(paradox_score)
        
        # Store historical data
        self._store_historical_point(smoothed_score, current_liquidity, arbitrage_volume)
        
        logger.debug("Paradox calculation: base={:.3f}, weighted={:.3f}, final={:.1f}".format(
            paradox_base, weighted_paradox, smoothed_score
        ))
        
        return ParadoxMetrics(
            paradox_score=smoothed_score,
            liquidity_ratio=liquidity_ratio,
            drain_factor=drain_factor,
            arbitrage_intensity=arbitrage_intensity,
            feedback_active=feedback_active,
            components=components
        )
    
    def _calculate_paradox_components(self, drain_factor, arbitrage_intensity, additional_metrics):
        """Calculate individual paradox components"""
        
        # Velocity component: How fast is arbitrage accelerating?
        velocity_score = min(1.0, arbitrage_intensity / 100000)  # Normalize to $100k/min
        
        # Concentration component: Is arbitrage concentrated in few assets?
        asset_count = additional_metrics.get("unique_assets", 5)  # Default 5 assets
        concentration_score = max(0, 1 - (asset_count / 10))  # Higher concentration = higher score
        
        # Volatility component: Market volatility amplifies paradox
        volatility_factor = additional_metrics.get("volatility_factor", 1.0)
        volatility_score = min(1.0, (volatility_factor - 1.0) * 2)  # Normalize volatility impact
        
        # Cross-venue spread component
        venue_spread = additional_metrics.get("cross_venue_spread", 0.01)  # Default 1%
        spread_score = min(1.0, venue_spread * 50)  # Higher spreads = more paradox risk
        
        return {
            "velocity_score": velocity_score,
            "concentration_score": concentration_score,
            "volatility_score": volatility_score,
            "spread_score": spread_score,
            "drain_factor": drain_factor
        }
    
    def _apply_historical_smoothing(self, current_score):
        """Apply exponential smoothing based on historical data"""
        
        if not self.historical_data:
            return current_score
        
        # Get recent scores for smoothing
        recent_scores = [point["score"] for point in self.historical_data[-5:]]
        
        if len(recent_scores) < 2:
            return current_score
        
        # Exponential moving average
        alpha = 0.3  # Smoothing factor
        smoothed = current_score
        
        for i, historical_score in enumerate(reversed(recent_scores)):
            weight = alpha * (self.config["time_decay_factor"] ** i)
            smoothed = (1 - weight) * smoothed + weight * historical_score
        
        return smoothed
    
    def _store_historical_point(self, score, liquidity, arbitrage_volume):
        """Store historical data point"""
        
        data_point = {
            "timestamp": time.time(),
            "score": score,
            "liquidity": liquidity,
            "arbitrage_volume": arbitrage_volume
        }
        
        self.historical_data.append(data_point)
        
        # Trim history if needed
        if len(self.historical_data) > self.max_history_points:
            self.historical_data = self.historical_data[-self.max_history_points:]
    
    def get_trend_analysis(self, lookback_minutes=30):
        """Analyze paradox score trends"""
        
        if len(self.historical_data) < 2:
            return {"trend": "insufficient_data", "slope": 0, "acceleration": 0}
        
        # Filter recent data
        cutoff_time = time.time() - (lookback_minutes * 60)
        recent_data = [
            point for point in self.historical_data 
            if point["timestamp"] > cutoff_time
        ]
        
        if len(recent_data) < 2:
            return {"trend": "insufficient_recent_data", "slope": 0, "acceleration": 0}
        
        # Calculate trend slope
        scores = [point["score"] for point in recent_data]
        timestamps = [point["timestamp"] for point in recent_data]
        
        # Simple linear regression for slope
        n = len(scores)
        sum_x = sum(timestamps)
        sum_y = sum(scores)
        sum_xy = sum(t * s for t, s in zip(timestamps, scores))
        sum_x2 = sum(t * t for t in timestamps)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.001:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Calculate acceleration (second derivative approximation)
        if len(scores) >= 3:
            recent_slope = (scores[-1] - scores[-2]) / max(timestamps[-1] - timestamps[-2], 1)
            previous_slope = (scores[-2] - scores[-3]) / max(timestamps[-2] - timestamps[-3], 1)
            acceleration = recent_slope - previous_slope
        else:
            acceleration = 0
        
        return {
            "trend": trend,
            "slope": slope * 3600,  # Convert to per-hour
            "acceleration": acceleration,
            "data_points": len(recent_data),
            "time_span_minutes": (timestamps[-1] - timestamps[0]) / 60 if len(timestamps) > 1 else 0
        }
    
    def predict_future_score(self, minutes_ahead=10):
        """Predict future paradox score based on current trend"""
        
        trend_analysis = self.get_trend_analysis()
        
        if not self.historical_data or trend_analysis["trend"] == "insufficient_data":
            return None
        
        current_score = self.historical_data[-1]["score"]
        slope_per_minute = trend_analysis["slope"] / 60  # Convert from per-hour to per-minute
        
        # Simple linear extrapolation with decay
        predicted_change = slope_per_minute * minutes_ahead
        decay_factor = 0.95 ** minutes_ahead  # Predictions become less reliable over time
        
        predicted_score = current_score + (predicted_change * decay_factor)
        predicted_score = max(0, min(100, predicted_score))  # Clamp to valid range
        
        confidence = max(0.1, decay_factor * (1 - abs(trend_analysis["acceleration"]) / 10))
        
        return {
            "predicted_score": predicted_score,
            "current_score": current_score,
            "predicted_change": predicted_change,
            "confidence": confidence,
            "minutes_ahead": minutes_ahead,
            "based_on_trend": trend_analysis["trend"]
        }
    
    def get_risk_assessment(self):
        """Get comprehensive risk assessment"""
        
        if not self.historical_data:
            return {"risk_level": "unknown", "score": 0}
        
        current_score = self.historical_data[-1]["score"]
        trend_analysis = self.get_trend_analysis()
        
        # Risk level determination
        if current_score >= 90:
            risk_level = "critical"
        elif current_score >= 75:
            risk_level = "high"
        elif current_score >= 50:
            risk_level = "medium"
        elif current_score >= 25:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        # Adjust for trend
        if trend_analysis["trend"] == "increasing" and trend_analysis["slope"] > 5:
            risk_levels = ["minimal", "low", "medium", "high", "critical"]
            current_index = risk_levels.index(risk_level)
            if current_index < len(risk_levels) - 1:
                risk_level = risk_levels[current_index + 1]
        
        return {
            "risk_level": risk_level,
            "current_score": current_score,
            "trend": trend_analysis["trend"],
            "slope_per_hour": trend_analysis["slope"],
            "recommendation": self._get_risk_recommendation(risk_level, trend_analysis)
        }
    
    def _get_risk_recommendation(self, risk_level, trend_analysis):
        """Get risk-based recommendations"""
        
        recommendations = {
            "minimal": "Continue normal operations. Monitor for changes.",
            "low": "Maintain awareness. Consider position size limits.",
            "medium": "Implement enhanced monitoring. Reduce position sizes.",
            "high": "Activate risk controls. Consider temporary trading halt.",
            "critical": "Emergency protocols required. Halt all new positions."
        }
        
        base_rec = recommendations.get(risk_level, "Monitor situation closely.")
        
        if trend_analysis["trend"] == "increasing":
            base_rec += " Trend is worsening - prepare for escalation."
        elif trend_analysis["trend"] == "decreasing":
            base_rec += " Trend is improving - maintain current measures."
        
        return base_rec
    
    def get_system_stats(self):
        """Get system statistics"""
        
        current_score = self.historical_data[-1]["score"] if self.historical_data else 0
        
        return {
            "current_paradox_score": current_score,
            "historical_data_points": len(self.historical_data),
            "configuration": self.config,
            "trend_analysis": self.get_trend_analysis(),
            "risk_assessment": self.get_risk_assessment(),
            "prediction_10min": self.predict_future_score(10)
        }
