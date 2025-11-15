"""
AI-Powered Semantic Understanding Layer
Extracts structured entities from unstructured intelligence using LLMs
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EntityType(Enum):
    """Threat ontology entity types"""
    ACTOR = "actor"
    EVENT = "event"
    PATTERN = "pattern"
    LOCATION = "location"
    CAMPAIGN = "campaign"
    TTP = "ttp"


@dataclass
class ExtractedEntity:
    """Structured entity extracted from unstructured intelligence"""
    entity_type: EntityType
    entity_id: str
    name: str
    attributes: Dict[str, Any]
    confidence: float
    source_text: str
    relationships: List[Dict[str, str]]


class SemanticUnderstandingLayer:
    """
    LLM-based entity extraction from unstructured intelligence
    Processes: reports, tweets, on-chain data, network graphs
    """
    
    def __init__(self, llm_provider: str = "openai", model: str = "gpt-4"):
        self.llm_provider = llm_provider
        self.model = model
        self.entity_schema = self._load_entity_schema()
    
    def _load_entity_schema(self) -> Dict:
        """Load ontology schema for entity extraction"""
        return {
            "actor": {
                "required_fields": ["actor_id", "name", "type"],
                "optional_fields": ["risk_score", "jurisdiction", "behavioral_signatures"],
                "types": ["wallet", "individual", "organization", "nation_state"]
            },
            "event": {
                "required_fields": ["event_id", "event_type", "timestamp"],
                "optional_fields": ["chain", "tx_hash", "value_usd", "participants"],
                "types": ["transaction", "liquidation", "sanction_update", "hack"]
            },
            "pattern": {
                "required_fields": ["pattern_id", "category", "description"],
                "optional_fields": ["confidence", "supporting_evidence", "detection_rules"],
                "types": ["behavioral_signature", "risk_indicator", "cluster", "ttp"]
            }
        }
    
    def extract_entities(self, text: str, source_type: str = "report") -> List[ExtractedEntity]:
        """
        Extract structured entities from unstructured text
        
        Args:
            text: Unstructured intelligence text
            source_type: Type of source (report, tweet, on_chain_data, etc.)
        
        Returns:
            List of extracted entities with relationships
        """
        # TODO: Implement LLM-based extraction
        # This would call GPT-4/Claude with structured output schema
        # For now, return placeholder structure
        
        prompt = self._build_extraction_prompt(text, source_type)
        # llm_response = self._call_llm(prompt)
        # entities = self._parse_llm_response(llm_response)
        
        return []
    
    def _build_extraction_prompt(self, text: str, source_type: str) -> str:
        """Build prompt for LLM entity extraction"""
        return f"""
Extract threat intelligence entities from the following {source_type} text.
Return structured JSON with entities matching the Behavioral Intelligence Graph schema.

Text:
{text}

Schema:
{json.dumps(self.entity_schema, indent=2)}

Extract:
1. Actors (wallets, individuals, organizations)
2. Events (transactions, sanctions, hacks)
3. Patterns (behavioral signatures, TTPs)
4. Relationships between entities

Return JSON array of entities with:
- entity_type
- entity_id
- name
- attributes
- confidence (0-1)
- relationships (list of {entity_id, relationship_type})
"""
    
    def extract_from_multiple_sources(self, sources: List[Dict[str, str]]) -> List[ExtractedEntity]:
        """Extract entities from multiple intelligence sources"""
        all_entities = []
        for source in sources:
            entities = self.extract_entities(
                text=source["content"],
                source_type=source.get("type", "report")
            )
            all_entities.extend(entities)
        
        # Deduplicate and merge entities
        return self._deduplicate_entities(all_entities)
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Merge duplicate entities from multiple sources"""
        # TODO: Implement entity deduplication logic
        # Use fuzzy matching on entity_id, name, attributes
        return entities


class MultiModalIntelligenceProcessor:
    """
    Process multiple intelligence modalities:
    - Text (reports, tweets)
    - Transaction data (on-chain)
    - Network graphs
    - Temporal sequences
    """
    
    def __init__(self, semantic_layer: SemanticUnderstandingLayer):
        self.semantic_layer = semantic_layer
    
    def process_text_intelligence(self, text: str) -> List[ExtractedEntity]:
        """Process text-based intelligence"""
        return self.semantic_layer.extract_entities(text, source_type="text")
    
    def process_transaction_data(self, tx_data: Dict) -> List[ExtractedEntity]:
        """Process on-chain transaction data"""
        # Convert transaction data to text description
        tx_text = self._transaction_to_text(tx_data)
        return self.semantic_layer.extract_entities(tx_text, source_type="transaction")
    
    def process_network_graph(self, graph_data: Dict) -> List[ExtractedEntity]:
        """Process network graph data"""
        # Extract entities from graph structure
        entities = []
        # TODO: Implement graph-based entity extraction
        return entities
    
    def _transaction_to_text(self, tx_data: Dict) -> str:
        """Convert transaction data to natural language for LLM processing"""
        return f"""
Transaction: {tx_data.get('tx_hash', 'unknown')}
From: {tx_data.get('from_address', 'unknown')}
To: {tx_data.get('to_address', 'unknown')}
Value: {tx_data.get('value', 0)} {tx_data.get('token', 'ETH')}
Chain: {tx_data.get('chain', 'unknown')}
Timestamp: {tx_data.get('timestamp', 'unknown')}
"""


if __name__ == "__main__":
    # Example usage
    semantic_layer = SemanticUnderstandingLayer()
    processor = MultiModalIntelligenceProcessor(semantic_layer)
    
    # Process sample intelligence
    sample_text = """
    Wallet 0x4a9f... associated with Lazarus Group sent $2.3M through Tornado Cash
    on 2024-11-03. Destination: Exchange A (Hong Kong). Entity clustering suggests
    link to sanctioned North Korean actor.
    """
    
    entities = processor.process_text_intelligence(sample_text)
    print(f"Extracted {len(entities)} entities")

