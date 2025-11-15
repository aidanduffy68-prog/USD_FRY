"""
AI-Powered Relationship Inference Engine
Uses Graph Neural Networks to discover hidden connections
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class InferredRelationship:
    """Relationship inferred by AI model"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float  # 0-1
    evidence: List[str]
    reasoning: str


class RelationshipInferenceEngine:
    """
    Graph Neural Network-based relationship inference
    Discovers hidden connections in Behavioral Intelligence Graph
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.relationship_types = [
            "COORDINATES_WITH",
            "CONTROLS",
            "BEHAVES_LIKE",
            "CLUSTERS_WITH",
            "SUSPECTED_OF",
            "TRIGGERS",
            "EVIDENCES"
        ]
    
    def infer_relationships(self, graph_data: Dict[str, Any]) -> List[InferredRelationship]:
        """
        Infer relationships between entities using GNN
        
        Args:
            graph_data: Behavioral Intelligence Graph structure
        
        Returns:
            List of inferred relationships with confidence scores
        """
        # TODO: Implement GNN inference
        # For now, use rule-based inference as placeholder
        
        entities = graph_data.get("entities", [])
        relationships = []
        
        # Check for coordination patterns
        coordination_rels = self._detect_coordination(entities)
        relationships.extend(coordination_rels)
        
        # Check for control structures
        control_rels = self._detect_control_structures(entities)
        relationships.extend(control_rels)
        
        # Check for behavioral similarity
        similarity_rels = self._detect_behavioral_similarity(entities)
        relationships.extend(similarity_rels)
        
        return relationships
    
    def _detect_coordination(self, entities: List[Dict]) -> List[InferredRelationship]:
        """Detect coordination rings from timing and pattern similarity"""
        relationships = []
        
        # Group entities by similar timing patterns
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                timing_similarity = self._calculate_timing_similarity(
                    entity1.get("transaction_timestamps", []),
                    entity2.get("transaction_timestamps", [])
                )
                
                if timing_similarity > 0.8:
                    relationships.append(InferredRelationship(
                        source_entity_id=entity1.get("entity_id"),
                        target_entity_id=entity2.get("entity_id"),
                        relationship_type="COORDINATES_WITH",
                        confidence=timing_similarity,
                        evidence=["synchronized_timing"],
                        reasoning=f"Entities show {timing_similarity:.2%} timing pattern similarity"
                    ))
        
        return relationships
    
    def _detect_control_structures(self, entities: List[Dict]) -> List[InferredRelationship]:
        """Detect wallet control structures"""
        relationships = []
        
        # Check for funding relationships
        for entity in entities:
            funded_by = entity.get("funded_by", [])
            for funder_id in funded_by:
                relationships.append(InferredRelationship(
                    source_entity_id=funder_id,
                    target_entity_id=entity.get("entity_id"),
                    relationship_type="CONTROLS",
                    confidence=0.75,  # TODO: Calculate from funding patterns
                    evidence=["funding_relationship"],
                    reasoning="Entity funded by source, indicating control structure"
                ))
        
        return relationships
    
    def _detect_behavioral_similarity(self, entities: List[Dict]) -> List[InferredRelationship]:
        """Detect entities with similar behavioral signatures"""
        relationships = []
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                similarity = self._calculate_behavioral_similarity(
                    entity1.get("behavioral_signatures", {}),
                    entity2.get("behavioral_signatures", {})
                )
                
                if similarity > 0.85:
                    relationships.append(InferredRelationship(
                        source_entity_id=entity1.get("entity_id"),
                        target_entity_id=entity2.get("entity_id"),
                        relationship_type="BEHAVES_LIKE",
                        confidence=similarity,
                        evidence=["behavioral_signature_match"],
                        reasoning=f"Entities show {similarity:.2%} behavioral similarity"
                    ))
        
        return relationships
    
    def _calculate_timing_similarity(self, timestamps1: List, timestamps2: List) -> float:
        """Calculate similarity of transaction timing patterns"""
        if not timestamps1 or not timestamps2:
            return 0.0
        
        # Simple similarity: check if timestamps are within small windows
        # TODO: Implement more sophisticated temporal pattern matching
        matches = 0
        for ts1 in timestamps1:
            for ts2 in timestamps2:
                if abs(ts1 - ts2) < 3600:  # Within 1 hour
                    matches += 1
        
        return min(matches / max(len(timestamps1), len(timestamps2)), 1.0)
    
    def _calculate_behavioral_similarity(self, sig1: Dict, sig2: Dict) -> float:
        """Calculate similarity of behavioral signatures"""
        if not sig1 or not sig2:
            return 0.0
        
        # Compare signature attributes
        common_keys = set(sig1.keys()) & set(sig2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1 = sig1[key]
            val2 = sig2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2), 1.0)
                similarities.append(1.0 - (diff / max_val))
            elif val1 == val2:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def enrich_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich Behavioral Intelligence Graph with inferred relationships
        
        Args:
            graph_data: Original graph structure
        
        Returns:
            Enriched graph with new relationships
        """
        inferred_relationships = self.infer_relationships(graph_data)
        
        # Add inferred relationships to graph
        existing_relationships = graph_data.get("relationships", [])
        
        for rel in inferred_relationships:
            existing_relationships.append({
                "source": rel.source_entity_id,
                "target": rel.target_entity_id,
                "type": rel.relationship_type,
                "confidence": rel.confidence,
                "evidence": rel.evidence,
                "inferred": True  # Mark as AI-inferred
            })
        
        graph_data["relationships"] = existing_relationships
        return graph_data


if __name__ == "__main__":
    # Example usage
    engine = RelationshipInferenceEngine()
    
    sample_graph = {
        "entities": [
            {
                "entity_id": "ALPHA_47",
                "transaction_timestamps": [1000, 2000, 3000],
                "behavioral_signatures": {"risk_tolerance": 0.94, "pattern_repetition": 1.0}
            },
            {
                "entity_id": "BETA_12",
                "transaction_timestamps": [1005, 2005, 3005],
                "behavioral_signatures": {"risk_tolerance": 0.92, "pattern_repetition": 0.98}
            }
        ],
        "relationships": []
    }
    
    enriched_graph = engine.enrich_graph(sample_graph)
    print(f"Enriched graph with {len(enriched_graph['relationships'])} relationships")

