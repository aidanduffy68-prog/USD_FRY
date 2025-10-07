#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Institutional Marketing - Distribution Layer
The packaged CDOs, tranches, and risk products aren't new money creation — they're distribution channels.
This is where you "sell the story": "Look, retail's wreckage is now structured yield."
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYInstitutionalMarketing:
    """
    Institutional Marketing and Distribution Layer
    
    Function: Package dark pool assets into sellable institutional products
    - No new money creation
    - Pure distribution and marketing
    - Story-telling around retail wreckage → structured yield
    """
    
    def __init__(self):
        # Product catalog for marketing
        self.product_catalog = {
            "volatility_insurance": {
                "story": "Hedge against retail panic with FRY Score-linked protection",
                "target_buyers": ["hedge_funds", "family_offices"],
                "yield_range": (0.06, 0.12),
                "min_investment": 1000000
            },
            "credit_risk_bonds": {
                "story": "Structured bonds backed by verified trading losses",
                "target_buyers": ["pension_funds", "insurance_companies"],
                "yield_range": (0.04, 0.08),
                "min_investment": 5000000
            },
            "exotic_yield_notes": {
                "story": "Leveraged exposure to retail trading dysfunction",
                "target_buyers": ["prop_trading", "hedge_funds"],
                "yield_range": (0.10, 0.25),
                "min_investment": 500000
            },
            "liquidation_swaps": {
                "story": "Monetize retail liquidation cascades",
                "target_buyers": ["market_makers", "arbitrage_funds"],
                "yield_range": (0.08, 0.18),
                "min_investment": 2000000
            }
        }
        
        # Buyer profiles and preferences
        self.institutional_buyers = {
            "Citadel Securities": {
                "risk_appetite": "medium",
                "preferred_products": ["volatility_insurance", "liquidation_swaps"],
                "aum": 50000000000,
                "allocation_target": 0.02
            },
            "Wintermute Trading": {
                "risk_appetite": "high", 
                "preferred_products": ["exotic_yield_notes", "liquidation_swaps"],
                "aum": 2000000000,
                "allocation_target": 0.05
            },
            "GIC Singapore": {
                "risk_appetite": "low",
                "preferred_products": ["credit_risk_bonds", "volatility_insurance"],
                "aum": 100000000000,
                "allocation_target": 0.01
            },
            "Alameda Research": {
                "risk_appetite": "very_high",
                "preferred_products": ["exotic_yield_notes"],
                "aum": 10000000000,
                "allocation_target": 0.08
            }
        }
        
        # Active marketing campaigns
        self.active_campaigns = {}
        self.sales_pipeline = []
        
        logger.info("📈 FRY Institutional Marketing initialized")
    
    def craft_product_story(self, product_type: str, fry_score: float, 
                           pool_stats: Dict) -> Dict:
        """
        Craft compelling marketing story around dark pool assets
        Transform retail wreckage into institutional opportunity
        """
        if product_type not in self.product_catalog:
            return {"error": "Unknown product type"}
        
        product_info = self.product_catalog[product_type]
        
        # Base story elements
        story_elements = {
            "headline": self._generate_headline(product_type, fry_score),
            "value_proposition": product_info["story"],
            "market_opportunity": self._describe_market_opportunity(pool_stats),
            "risk_metrics": self._package_risk_metrics(fry_score, pool_stats),
            "yield_story": self._craft_yield_narrative(product_type, fry_score),
            "competitive_advantage": self._highlight_competitive_edge(),
            "call_to_action": self._generate_cta(product_type)
        }
        
        return {
            "product_type": product_type,
            "story_package": story_elements,
            "target_yield": self._calculate_target_yield(product_type, fry_score),
            "recommended_allocation": self._suggest_allocation(product_type),
            "urgency_factors": self._identify_urgency(fry_score, pool_stats)
        }
    
    def _generate_headline(self, product_type: str, fry_score: float) -> str:
        """Generate compelling marketing headlines"""
        headlines = {
            "volatility_insurance": f"Protect Your Portfolio: FRY Score at {fry_score:.1f} Signals Retail Volatility Spike",
            "credit_risk_bonds": f"Verified Loss-Backed Bonds: {fry_score:.1f} FRY Score Confirms Credit Quality",
            "exotic_yield_notes": f"Amplified Returns: {fry_score:.1f}% Pain Index Creates Yield Opportunity", 
            "liquidation_swaps": f"Liquidation Alpha: FRY Score {fry_score:.1f} Indicates Prime Entry Point"
        }
        return headlines.get(product_type, f"FRY Score {fry_score:.1f}: Institutional Opportunity")
    
    def _describe_market_opportunity(self, pool_stats: Dict) -> str:
        """Describe the market opportunity based on pool statistics"""
        total_losses = pool_stats.get("aggregate_stats", {}).get("total_losses_processed", 0)
        liquidation_events = pool_stats.get("pool_breakdown", {}).get("liquidation_pool", {}).get("event_count", 0)
        
        return f"${total_losses:,.0f} in verified retail losses with {liquidation_events} liquidation events creates unprecedented structured yield opportunity. Market dislocation provides institutional entry point."
    
    def _package_risk_metrics(self, fry_score: float, pool_stats: Dict) -> Dict:
        """Package risk metrics for institutional consumption"""
        return {
            "fry_score_current": fry_score,
            "volatility_rating": "High" if fry_score > 150 else "Medium" if fry_score > 100 else "Low",
            "loss_verification": "100% blockchain-verified trading losses",
            "diversification": f"{pool_stats.get('aggregate_stats', {}).get('anonymized_traders', 0)} anonymized traders",
            "liquidity_rating": "Daily mark-to-market with FRY Score benchmark"
        }
    
    def _craft_yield_narrative(self, product_type: str, fry_score: float) -> str:
        """Craft yield narrative based on FRY Score"""
        base_yield = self.product_catalog[product_type]["yield_range"][0]
        score_multiplier = min(fry_score / 100, 2.0)  # Cap at 2x
        target_yield = base_yield * score_multiplier
        
        return f"Target yield of {target_yield:.1%} driven by FRY Score of {fry_score:.1f}. Higher retail pain directly translates to institutional yield through verified loss monetization."
    
    def _highlight_competitive_edge(self) -> str:
        """Highlight unique competitive advantages"""
        return "First-to-market retail loss monetization platform. Proprietary FRY Score provides real-time risk assessment. Anonymized but verified loss data ensures institutional-grade transparency."
    
    def _generate_cta(self, product_type: str) -> str:
        """Generate call-to-action for sales team"""
        min_investment = self.product_catalog[product_type]["min_investment"]
        return f"Minimum allocation ${min_investment:,.0f}. Limited capacity based on retail loss flow. Contact institutional sales for immediate allocation."
    
    def _calculate_target_yield(self, product_type: str, fry_score: float) -> float:
        """Calculate target yield based on FRY Score"""
        yield_range = self.product_catalog[product_type]["yield_range"]
        score_factor = min(fry_score / 100, 2.0)
        return yield_range[0] * score_factor
    
    def _suggest_allocation(self, product_type: str) -> str:
        """Suggest portfolio allocation based on product type"""
        allocations = {
            "volatility_insurance": "1-3% of portfolio for downside protection",
            "credit_risk_bonds": "3-8% allocation for yield enhancement",
            "exotic_yield_notes": "0.5-2% for alpha generation",
            "liquidation_swaps": "1-5% for market neutral strategies"
        }
        return allocations.get(product_type, "Contact for allocation guidance")
    
    def _identify_urgency(self, fry_score: float, pool_stats: Dict) -> List[str]:
        """Identify urgency factors for sales pressure"""
        urgency_factors = []
        
        if fry_score > 150:
            urgency_factors.append("FRY Score above 150 indicates peak retail distress")
        
        liquidation_rate = pool_stats.get("pool_breakdown", {}).get("liquidation_pool", {}).get("event_count", 0)
        if liquidation_rate > 10:
            urgency_factors.append("High liquidation frequency creates time-sensitive opportunity")
        
        whale_losses = pool_stats.get("pool_breakdown", {}).get("whale_losses", {}).get("event_count", 0)
        if whale_losses > 3:
            urgency_factors.append("Large trader losses indicate institutional-scale opportunity")
        
        return urgency_factors
    
    def create_sales_pitch(self, buyer_name: str, fry_score: float, 
                          pool_stats: Dict) -> Dict:
        """
        Create customized sales pitch for specific institutional buyer
        """
        if buyer_name not in self.institutional_buyers:
            return {"error": "Unknown buyer"}
        
        buyer_profile = self.institutional_buyers[buyer_name]
        
        # Select best product match
        preferred_products = buyer_profile["preferred_products"]
        product_pitches = []
        
        for product_type in preferred_products:
            story = self.craft_product_story(product_type, fry_score, pool_stats)
            
            # Customize for buyer
            allocation_size = buyer_profile["aum"] * buyer_profile["allocation_target"]
            story["recommended_investment"] = min(allocation_size, 50000000)  # Cap at $50M
            story["buyer_fit_score"] = self._calculate_buyer_fit(buyer_profile, product_type, fry_score)
            
            product_pitches.append(story)
        
        # Sort by fit score
        product_pitches.sort(key=lambda x: x["buyer_fit_score"], reverse=True)
        
        return {
            "buyer": buyer_name,
            "buyer_profile": buyer_profile,
            "recommended_products": product_pitches[:2],  # Top 2 products
            "total_recommended_allocation": sum(p["recommended_investment"] for p in product_pitches[:2]),
            "pitch_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_buyer_fit(self, buyer_profile: Dict, product_type: str, fry_score: float) -> float:
        """Calculate how well product fits buyer profile"""
        fit_score = 50.0  # Base score
        
        # Risk appetite alignment
        risk_mapping = {
            "low": {"credit_risk_bonds": 40, "volatility_insurance": 30},
            "medium": {"volatility_insurance": 35, "credit_risk_bonds": 25, "liquidation_swaps": 20},
            "high": {"exotic_yield_notes": 35, "liquidation_swaps": 30, "volatility_insurance": 15},
            "very_high": {"exotic_yield_notes": 45, "liquidation_swaps": 25}
        }
        
        risk_score = risk_mapping.get(buyer_profile["risk_appetite"], {}).get(product_type, 0)
        fit_score += risk_score
        
        # FRY Score alignment (higher scores better for higher risk products)
        if product_type in ["exotic_yield_notes", "liquidation_swaps"] and fry_score > 120:
            fit_score += 20
        elif product_type in ["credit_risk_bonds", "volatility_insurance"] and fry_score < 120:
            fit_score += 15
        
        return min(fit_score, 100.0)
    
    def generate_marketing_campaign(self, fry_score: float, pool_stats: Dict) -> Dict:
        """
        Generate comprehensive marketing campaign across all buyers
        """
        campaign_id = f"FRY-CAMPAIGN-{datetime.now().strftime('%Y%m%d-%H%M')}"
        
        campaign = {
            "campaign_id": campaign_id,
            "launch_timestamp": datetime.now().isoformat(),
            "market_context": {
                "fry_score": fry_score,
                "pool_statistics": pool_stats,
                "market_narrative": self._create_market_narrative(fry_score, pool_stats)
            },
            "buyer_pitches": {},
            "campaign_metrics": {
                "total_addressable_market": 0,
                "target_allocations": 0,
                "priority_buyers": []
            }
        }
        
        # Generate pitches for all buyers
        total_tam = 0
        total_allocations = 0
        
        for buyer_name in self.institutional_buyers.keys():
            pitch = self.create_sales_pitch(buyer_name, fry_score, pool_stats)
            campaign["buyer_pitches"][buyer_name] = pitch
            
            if "recommended_products" in pitch:
                buyer_allocation = pitch["total_recommended_allocation"]
                total_allocations += buyer_allocation
                
                buyer_tam = self.institutional_buyers[buyer_name]["aum"] * 0.1  # 10% max allocation
                total_tam += buyer_tam
                
                # Identify priority buyers (high fit scores)
                avg_fit_score = np.mean([p["buyer_fit_score"] for p in pitch["recommended_products"]])
                if avg_fit_score > 70:
                    campaign["campaign_metrics"]["priority_buyers"].append({
                        "buyer": buyer_name,
                        "fit_score": avg_fit_score,
                        "allocation": buyer_allocation
                    })
        
        campaign["campaign_metrics"]["total_addressable_market"] = total_tam
        campaign["campaign_metrics"]["target_allocations"] = total_allocations
        
        # Sort priority buyers by fit score
        campaign["campaign_metrics"]["priority_buyers"].sort(
            key=lambda x: x["fit_score"], reverse=True
        )
        
        self.active_campaigns[campaign_id] = campaign
        
        logger.info("📈 Marketing campaign {} launched: ${:.0f}M target allocations".format(
            campaign_id, total_allocations / 1000000
        ))
        
        return campaign
    
    def _create_market_narrative(self, fry_score: float, pool_stats: Dict) -> str:
        """Create overarching market narrative for campaign"""
        total_losses = pool_stats.get("aggregate_stats", {}).get("total_losses_processed", 0)
        
        if fry_score > 150:
            sentiment = "Peak retail distress creates exceptional institutional opportunity"
        elif fry_score > 120:
            sentiment = "Elevated retail losses provide attractive risk-adjusted returns"
        else:
            sentiment = "Stable retail loss environment offers consistent yield generation"
        
        return f"{sentiment}. ${total_losses:,.0f} in verified losses with FRY Score of {fry_score:.1f} demonstrates market dislocation ready for institutional capital allocation."

def main():
    """
    Demo the institutional marketing and distribution layer
    """
    print("📈 FRY Institutional Marketing - Distribution Layer")
    print("Function: Package dark pool assets into sellable institutional products")
    
    marketing = FRYInstitutionalMarketing()
    
    # Sample dark pool data (from dark pool engine)
    sample_fry_score = 135.7
    sample_pool_stats = {
        "aggregate_stats": {
            "total_losses_processed": 125000.0,
            "total_fry_minted": 1250000.0,
            "anonymized_traders": 45
        },
        "pool_breakdown": {
            "liquidation_pool": {"event_count": 12},
            "whale_losses": {"event_count": 5},
            "high_leverage": {"event_count": 18}
        }
    }
    
    print(f"\n📊 Market Context:")
    print(f"   FRY Score: {sample_fry_score}")
    print(f"   Total Losses: ${sample_pool_stats['aggregate_stats']['total_losses_processed']:,.0f}")
    print(f"   Liquidation Events: {sample_pool_stats['pool_breakdown']['liquidation_pool']['event_count']}")
    
    # Generate marketing campaign
    print(f"\n📈 Generating institutional marketing campaign...")
    campaign = marketing.generate_marketing_campaign(sample_fry_score, sample_pool_stats)
    
    print(f"\n🎯 Campaign Results:")
    print(f"   Campaign ID: {campaign['campaign_id']}")
    print(f"   Target Allocations: ${campaign['campaign_metrics']['target_allocations']:,.0f}")
    print(f"   Priority Buyers: {len(campaign['campaign_metrics']['priority_buyers'])}")
    
    # Show top buyer pitches
    print(f"\n🏛️ Priority Buyer Pitches:")
    for priority_buyer in campaign['campaign_metrics']['priority_buyers'][:3]:
        buyer_name = priority_buyer['buyer']
        pitch = campaign['buyer_pitches'][buyer_name]
        print(f"   {buyer_name}: ${priority_buyer['allocation']:,.0f} (fit: {priority_buyer['fit_score']:.1f})")
        
        if pitch['recommended_products']:
            top_product = pitch['recommended_products'][0]
            print(f"     → {top_product['product_type']}: {top_product['story_package']['headline']}")
    
    print(f"\n💰 Market Narrative:")
    print(f"   {campaign['market_context']['market_narrative']}")
    
    print(f"\n✅ Institutional marketing ready to distribute dark pool yield")

if __name__ == "__main__":
    main()
