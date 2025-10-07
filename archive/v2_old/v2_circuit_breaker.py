# -*- coding: utf-8 -*-
"""
FRY Core v2: Circuit Breaker System
Advanced circuit breaker with multiple trigger conditions
"""

import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitBreakerEvent:
    """Circuit breaker trigger event"""
    
    def __init__(self, trigger_type, severity, message, metrics):
        self.trigger_type = trigger_type
        self.severity = severity  # "warning", "critical", "emergency"
        self.message = message
        self.metrics = metrics
        self.timestamp = time.time()
        
    def to_dict(self):
        return {
            "trigger_type": self.trigger_type,
            "severity": self.severity,
            "message": self.message,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }

class InflowMonitor:
    """Monitors inflow rates and triggers circuit breaker"""
    
    def __init__(self, baseline_rate, multiplier_threshold, time_window_minutes):
        self.baseline_rate = baseline_rate
        self.multiplier_threshold = multiplier_threshold
        self.time_window_minutes = time_window_minutes
        self.inflow_history = []
        
    def record_inflow(self, amount_usd):
        """Record new inflow"""
        current_time = time.time()
        self.inflow_history.append({
            "amount": amount_usd,
            "timestamp": current_time
        })
        
        # Clean old entries
        cutoff_time = current_time - (self.time_window_minutes * 60)
        self.inflow_history = [
            entry for entry in self.inflow_history 
            if entry["timestamp"] > cutoff_time
        ]
    
    def get_current_rate(self):
        """Get current inflow rate per minute"""
        if not self.inflow_history:
            return 0
            
        total_inflow = sum(entry["amount"] for entry in self.inflow_history)
        return total_inflow / self.time_window_minutes
    
    def check_threshold(self):
        """Check if inflow rate exceeds threshold"""
        current_rate = self.get_current_rate()
        threshold = self.baseline_rate * self.multiplier_threshold
        
        if current_rate > threshold:
            return CircuitBreakerEvent(
                trigger_type="inflow_rate",
                severity="critical",
                message="Inflow rate exceeded threshold: ${:,.0f}/min > ${:,.0f}/min".format(
                    current_rate, threshold
                ),
                metrics={
                    "current_rate": current_rate,
                    "threshold": threshold,
                    "baseline": self.baseline_rate,
                    "multiplier": self.multiplier_threshold,
                    "window_minutes": self.time_window_minutes
                }
            )
        return None

class CircuitBreakerSystem:
    """
    Core v2: Advanced circuit breaker system with multiple triggers
    """
    
    def __init__(self, config=None):
        self.active = False
        self.activation_time = None
        self.trigger_events = []
        self.monitors = {}
        
        # Default configuration
        default_config = {
            "inflow_baseline": 50000,  # $50k/minute
            "inflow_multiplier": 5.0,  # 5x threshold
            "inflow_window": 10,       # 10 minute window
            "paradox_threshold": 85,   # Paradox score threshold
            "max_events_history": 100  # Max trigger events to store
        }
        
        self.config = config or default_config
        self._initialize_monitors()
    
    def _initialize_monitors(self):
        """Initialize monitoring systems"""
        
        # Inflow rate monitor
        self.monitors["inflow"] = InflowMonitor(
            baseline_rate=self.config["inflow_baseline"],
            multiplier_threshold=self.config["inflow_multiplier"],
            time_window_minutes=self.config["inflow_window"]
        )
        
        logger.info("Circuit breaker initialized with {} monitors".format(len(self.monitors)))
    
    def record_inflow(self, amount_usd):
        """Record system inflow"""
        if "inflow" in self.monitors:
            self.monitors["inflow"].record_inflow(amount_usd)
    
    def check_paradox_condition(self, paradox_score):
        """Check liquidity paradox condition"""
        
        threshold = self.config["paradox_threshold"]
        
        if paradox_score > threshold:
            return CircuitBreakerEvent(
                trigger_type="liquidity_paradox",
                severity="emergency",
                message="Liquidity paradox score exceeded: {:.1f} > {}".format(
                    paradox_score, threshold
                ),
                metrics={
                    "paradox_score": paradox_score,
                    "threshold": threshold
                }
            )
        return None
    
    def check_all_conditions(self, paradox_score=0):
        """Check all circuit breaker conditions"""
        
        if self.active:
            return []  # Already active
        
        trigger_events = []
        
        # Check inflow rate
        inflow_event = self.monitors["inflow"].check_threshold()
        if inflow_event:
            trigger_events.append(inflow_event)
        
        # Check paradox condition
        paradox_event = self.check_paradox_condition(paradox_score)
        if paradox_event:
            trigger_events.append(paradox_event)
        
        return trigger_events
    
    def should_trigger(self, paradox_score=0):
        """Check if circuit breaker should be triggered"""
        
        trigger_events = self.check_all_conditions(paradox_score)
        
        # Trigger on any critical or emergency event
        critical_events = [
            event for event in trigger_events 
            if event.severity in ["critical", "emergency"]
        ]
        
        return len(critical_events) > 0, trigger_events
    
    def activate(self, trigger_events):
        """Activate circuit breaker"""
        
        if self.active:
            logger.warning("Circuit breaker already active")
            return False
        
        self.active = True
        self.activation_time = time.time()
        
        # Store trigger events
        for event in trigger_events:
            self.trigger_events.append(event)
        
        # Trim history if needed
        if len(self.trigger_events) > self.config["max_events_history"]:
            self.trigger_events = self.trigger_events[-self.config["max_events_history"]:]
        
        # Log activation
        logger.critical("🚨 CIRCUIT BREAKER ACTIVATED 🚨")
        for event in trigger_events:
            logger.critical("  Trigger: {} - {}".format(event.trigger_type.upper(), event.message))
        
        return True
    
    def reset(self, admin_override=False, reset_reason=""):
        """Reset circuit breaker"""
        
        if not admin_override:
            logger.error("Circuit breaker reset requires admin override")
            return False
        
        if not self.active:
            logger.info("Circuit breaker already inactive")
            return True
        
        self.active = False
        activation_duration = time.time() - self.activation_time if self.activation_time else 0
        self.activation_time = None
        
        # Clear inflow history
        if "inflow" in self.monitors:
            self.monitors["inflow"].inflow_history = []
        
        logger.info("Circuit breaker reset by admin override")
        logger.info("  Duration active: {:.1f} minutes".format(activation_duration / 60))
        if reset_reason:
            logger.info("  Reset reason: {}".format(reset_reason))
        
        return True
    
    def get_status(self):
        """Get current circuit breaker status"""
        
        current_time = time.time()
        
        # Get current metrics
        inflow_rate = self.monitors["inflow"].get_current_rate() if "inflow" in self.monitors else 0
        inflow_threshold = self.config["inflow_baseline"] * self.config["inflow_multiplier"]
        
        status = {
            "active": self.active,
            "activation_time": self.activation_time,
            "activation_datetime": datetime.fromtimestamp(self.activation_time).isoformat() if self.activation_time else None,
            "duration_active_minutes": (current_time - self.activation_time) / 60 if self.activation_time else 0,
            "current_metrics": {
                "inflow_rate_per_minute": inflow_rate,
                "inflow_threshold": inflow_threshold,
                "inflow_utilization_pct": (inflow_rate / inflow_threshold) * 100 if inflow_threshold > 0 else 0
            },
            "configuration": self.config,
            "recent_trigger_events": [event.to_dict() for event in self.trigger_events[-5:]],  # Last 5 events
            "total_trigger_events": len(self.trigger_events)
        }
        
        return status
    
    def get_health_check(self):
        """Get system health check"""
        
        inflow_rate = self.monitors["inflow"].get_current_rate() if "inflow" in self.monitors else 0
        inflow_threshold = self.config["inflow_baseline"] * self.config["inflow_multiplier"]
        
        # Calculate health score (0-100)
        inflow_utilization = (inflow_rate / inflow_threshold) if inflow_threshold > 0 else 0
        
        if self.active:
            health_score = 0  # Critical if active
            status = "CRITICAL"
        elif inflow_utilization > 0.8:
            health_score = 20
            status = "WARNING"
        elif inflow_utilization > 0.5:
            health_score = 60
            status = "CAUTION"
        else:
            health_score = 100
            status = "HEALTHY"
        
        return {
            "health_score": health_score,
            "status": status,
            "inflow_utilization_pct": inflow_utilization * 100,
            "monitors_active": len(self.monitors),
            "last_trigger": self.trigger_events[-1].to_dict() if self.trigger_events else None
        }
