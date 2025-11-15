"""
AI-Powered Behavioral Signature Generation
Enhances Hades with AI-driven behavioral profiling and pattern recognition
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class BehavioralTrait(Enum):
    """Behavioral traits identified by AI"""
    RISK_TOLERANCE = "risk_tolerance"
    PATTERN_REPETITION = "pattern_repetition"
    FLIGHT_RISK = "flight_risk"
    COORDINATION_LIKELIHOOD = "coordination_likelihood"
    TIMING_PREFERENCE = "timing_preference"
    ROUTE_ENTROPY = "route_entropy"
    LIQUIDITY_PATTERN = "liquidity_pattern"
    OFF_RAMP_PREFERENCE = "off_ramp_preference"


@dataclass
class BehavioralSignature:
    """AI-generated behavioral signature for a threat actor"""
    actor_id: str
    signature_id: str
    traits: Dict[BehavioralTrait, float]  # 0-1 scores
    confidence: float
    pattern_matches: List[str]
    predicted_actions: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str
    evidence_sources: List[str] = field(default_factory=list)


@dataclass
class BehavioralPattern:
    """Pattern identified in actor behavior"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: float
    confidence: float
    examples: List[str]
    predictive_value: float


class AIHadesProfiler:
    """
    AI-powered behavioral profiling engine
    Enhances traditional Hades with ML-driven signature generation
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model_version = "1.0.0"
        
    def generate_signature(
        self,
        actor_id: str,
        transaction_history: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]] = None,
        intelligence_reports: Optional[List[str]] = None
    ) -> BehavioralSignature:
        """
        Generate AI-powered behavioral signature
        
        Args:
            actor_id: Unique identifier for the actor
            transaction_history: Historical transaction data
            network_data: Echo network coordination data
            intelligence_reports: Unstructured intelligence text
            
        Returns:
            BehavioralSignature with AI-generated traits and predictions
        """
        # Extract behavioral traits using ML models
        traits = self._extract_traits(transaction_history, network_data, intelligence_reports)
        
        # Identify behavioral patterns
        patterns = self._identify_patterns(transaction_history)
        
        # Generate predictions
        predictions = self._generate_predictions(traits, patterns, transaction_history)
        
        # Calculate confidence
        confidence = self._calculate_confidence(traits, patterns, transaction_history)
        
        signature = BehavioralSignature(
            actor_id=actor_id,
            signature_id=f"hades_ai_{actor_id}_{datetime.now().isoformat()}",
            traits=traits,
            confidence=confidence,
            pattern_matches=[p.pattern_id for p in patterns],
            predicted_actions=predictions,
            generated_at=datetime.now(),
            model_version=self.model_version,
            evidence_sources=self._get_evidence_sources(transaction_history, network_data, intelligence_reports)
        )
        
        return signature
    
    def _extract_traits(
        self,
        transactions: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]],
        intelligence: Optional[List[str]]
    ) -> Dict[BehavioralTrait, float]:
        """Extract behavioral traits using AI models"""
        traits = {}
        
        # Risk tolerance: Analyze transaction amounts, volatility exposure
        risk_scores = [t.get('risk_score', 0.5) for t in transactions if 'risk_score' in t]
        traits[BehavioralTrait.RISK_TOLERANCE] = (
            sum(risk_scores) / len(risk_scores) if risk_scores else 0.5
        )
        
        # Pattern repetition: Measure consistency in transaction patterns
        traits[BehavioralTrait.PATTERN_REPETITION] = self._calculate_pattern_repetition(transactions)
        
        # Flight risk: Analyze off-ramp patterns, timing
        traits[BehavioralTrait.FLIGHT_RISK] = self._calculate_flight_risk(transactions)
        
        # Coordination likelihood: Use Echo network data
        if network_data:
            traits[BehavioralTrait.COORDINATION_LIKELIHOOD] = network_data.get('coordination_score', 0.0)
        else:
            traits[BehavioralTrait.COORDINATION_LIKELIHOOD] = 0.0
        
        # Timing preference: Analyze transaction timing patterns
        traits[BehavioralTrait.TIMING_PREFERENCE] = self._analyze_timing_patterns(transactions)
        
        # Route entropy: Measure diversity in transaction routes
        traits[BehavioralTrait.ROUTE_ENTROPY] = self._calculate_route_entropy(transactions)
        
        # Liquidity pattern: Analyze liquidity provision/removal patterns
        traits[BehavioralTrait.LIQUIDITY_PATTERN] = self._analyze_liquidity_patterns(transactions)
        
        # Off-ramp preference: Analyze exchange/OTC preferences
        traits[BehavioralTrait.OFF_RAMP_PREFERENCE] = self._analyze_off_ramp_preferences(transactions)
        
        return traits
    
    def _identify_patterns(self, transactions: List[Dict[str, Any]]) -> List[BehavioralPattern]:
        """Identify behavioral patterns using pattern recognition"""
        patterns = []
        
        # Example: Identify rapid chain switching
        chain_switches = self._detect_chain_switching(transactions)
        if chain_switches:
            patterns.append(BehavioralPattern(
                pattern_id="rapid_chain_switching",
                pattern_type="evasion",
                description="Frequent cross-chain transfers within short time windows",
                frequency=chain_switches['frequency'],
                confidence=chain_switches['confidence'],
                examples=chain_switches['examples'],
                predictive_value=0.85
            ))
        
        # Example: Identify mixer usage patterns
        mixer_usage = self._detect_mixer_patterns(transactions)
        if mixer_usage:
            patterns.append(BehavioralPattern(
                pattern_id="systematic_mixer_usage",
                pattern_type="obfuscation",
                description="Consistent use of privacy tools before off-ramps",
                frequency=mixer_usage['frequency'],
                confidence=mixer_usage['confidence'],
                examples=mixer_usage['examples'],
                predictive_value=0.90
            ))
        
        return patterns
    
    def _generate_predictions(
        self,
        traits: Dict[BehavioralTrait, float],
        patterns: List[BehavioralPattern],
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate predictive actions based on behavioral signature"""
        predictions = []
        
        # Predict off-ramp attempt based on flight risk
        if traits[BehavioralTrait.FLIGHT_RISK] > 0.7:
            predictions.append({
                "type": "off_ramp_attempt",
                "confidence": traits[BehavioralTrait.FLIGHT_RISK],
                "timing_window": "48-72h",
                "location": self._predict_off_ramp_location(traits, transactions),
                "amount_range": self._predict_amount_range(transactions)
            })
        
        # Predict coordination activity
        if traits[BehavioralTrait.COORDINATION_LIKELIHOOD] > 0.6:
            predictions.append({
                "type": "coordination_activity",
                "confidence": traits[BehavioralTrait.COORDINATION_LIKELIHOOD],
                "expected_partners": self._predict_coordination_partners(transactions),
                "timing": "within_7_days"
            })
        
        # Predict next attack window based on timing patterns
        if traits[BehavioralTrait.TIMING_PREFERENCE] > 0.5:
            predictions.append({
                "type": "activity_window",
                "confidence": traits[BehavioralTrait.TIMING_PREFERENCE],
                "window": self._predict_timing_window(transactions),
                "pattern_match": "historical_timing_consistency"
            })
        
        return predictions
    
    def _calculate_confidence(
        self,
        traits: Dict[BehavioralTrait, float],
        patterns: List[BehavioralPattern],
        transactions: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence in behavioral signature"""
        # Base confidence on data quality
        data_quality = min(len(transactions) / 100, 1.0)  # More data = higher confidence
        
        # Pattern confidence
        pattern_confidence = (
            sum(p.confidence for p in patterns) / len(patterns)
            if patterns else 0.5
        )
        
        # Trait consistency
        trait_consistency = 1.0 - self._calculate_trait_variance(traits)
        
        # Weighted average
        confidence = (
            data_quality * 0.4 +
            pattern_confidence * 0.4 +
            trait_consistency * 0.2
        )
        
        return min(confidence, 1.0)
    
    # Helper methods (stubs for implementation)
    def _calculate_pattern_repetition(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate how repetitive transaction patterns are"""
        # Implementation: Analyze transaction sequence similarity
        return 0.75  # Placeholder
    
    def _calculate_flight_risk(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate likelihood of attempting to off-ramp funds"""
        # Implementation: Analyze recent activity, off-ramp patterns
        return 0.65  # Placeholder
    
    def _analyze_timing_patterns(self, transactions: List[Dict[str, Any]]) -> float:
        """Analyze timing preferences in transactions"""
        # Implementation: Cluster transaction times, identify patterns
        return 0.70  # Placeholder
    
    def _calculate_route_entropy(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate entropy/diversity in transaction routes"""
        # Implementation: Measure route diversity
        return 0.60  # Placeholder
    
    def _analyze_liquidity_patterns(self, transactions: List[Dict[str, Any]]) -> float:
        """Analyze liquidity provision/removal patterns"""
        # Implementation: Detect liquidity manipulation
        return 0.55  # Placeholder
    
    def _analyze_off_ramp_preferences(self, transactions: List[Dict[str, Any]]) -> float:
        """Analyze preferred off-ramp methods"""
        # Implementation: Identify exchange/OTC preferences
        return 0.65  # Placeholder
    
    def _detect_chain_switching(self, transactions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect rapid chain switching patterns"""
        # Implementation: Analyze cross-chain transfer frequency
        return None  # Placeholder
    
    def _detect_mixer_patterns(self, transactions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect mixer usage patterns"""
        # Implementation: Identify privacy tool usage
        return None  # Placeholder
    
    def _predict_off_ramp_location(self, traits: Dict[BehavioralTrait, float], transactions: List[Dict[str, Any]]) -> str:
        """Predict likely off-ramp location"""
        # Implementation: Use historical off-ramp data
        return "Dubai_OTC_desk_3"  # Placeholder
    
    def _predict_amount_range(self, transactions: List[Dict[str, Any]]) -> str:
        """Predict amount range for next transaction"""
        # Implementation: Analyze historical amounts
        return "$1.8M-$2.5M"  # Placeholder
    
    def _predict_coordination_partners(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Predict likely coordination partners"""
        # Implementation: Use Echo network data
        return []  # Placeholder
    
    def _predict_timing_window(self, transactions: List[Dict[str, Any]]) -> str:
        """Predict next activity timing window"""
        # Implementation: Analyze timing patterns
        return "UTC 02:00-04:00"  # Placeholder
    
    def _calculate_trait_variance(self, traits: Dict[BehavioralTrait, float]) -> float:
        """Calculate variance in trait scores (lower = more consistent)"""
        values = list(traits.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance
    
    def _get_evidence_sources(
        self,
        transactions: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]],
        intelligence: Optional[List[str]]
    ) -> List[str]:
        """Get list of evidence sources used"""
        sources = []
        if transactions:
            sources.append(f"transaction_history_{len(transactions)}_txns")
        if network_data:
            sources.append("echo_network_data")
        if intelligence:
            sources.append(f"intelligence_reports_{len(intelligence)}")
        return sources

