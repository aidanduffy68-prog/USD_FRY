#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Harvesting Engine - Pure Mechanical Plumbing
One-way siphon that catches retail losses/liquidations on Hyperliquid
No intelligence, no processing - just mechanical redirection into the pool
"""

import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYHarvestingEngine:
    """
    Pure mechanical harvesting system - the plumbing layer
    
    Function: Siphon retail losses from Hyperliquid into the dark pool
    - No processing logic
    - No anonymization 
    - No FRY minting
    - Just mechanical loss detection and forwarding
    """
    
    def __init__(self):
        self.hyperliquid_api = "https://api.hyperliquid.xyz"
        self.monitored_wallets = set()
        self.loss_queue = []
        self.harvesting_stats = {
            "total_losses_siphoned": 0.0,
            "total_liquidations_caught": 0,
            "wallets_monitored": 0,
            "uptime_start": datetime.now().isoformat()
        }
        
        logger.info("🔧 FRY Harvesting Engine (plumbing layer) initialized")
    
    def add_wallet_to_monitor(self, wallet_address: str):
        """Add wallet to monitoring pipeline"""
        self.monitored_wallets.add(wallet_address)
        self.harvesting_stats["wallets_monitored"] = len(self.monitored_wallets)
        logger.info("📡 Added wallet to harvesting pipeline: {}...".format(wallet_address[:8]))
    
    def remove_wallet_from_monitor(self, wallet_address: str):
        """Remove wallet from monitoring pipeline"""
        self.monitored_wallets.discard(wallet_address)
        self.harvesting_stats["wallets_monitored"] = len(self.monitored_wallets)
        logger.info("📡 Removed wallet from harvesting pipeline: {}...".format(wallet_address[:8]))
    
    async def fetch_wallet_fills(self, wallet_address: str) -> List[Dict]:
        """
        Mechanical fetch of wallet fills from Hyperliquid
        No processing - just raw data extraction
        """
        try:
            payload = {
                "type": "userFills",
                "user": wallet_address
            }
            
            response = requests.post(f"{self.hyperliquid_api}/info", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Failed to fetch fills for {}: {}".format(wallet_address[:8], response.status_code))
                return []
                
        except Exception as e:
            logger.error("Error fetching fills for {}: {}".format(wallet_address[:8], str(e)))
            return []
    
    def extract_loss_events(self, fills: List[Dict], wallet_address: str) -> List[Dict]:
        """
        Mechanical extraction of REKT LONG loss events from fills
        Rigged to only harvest long positions that got destroyed
        """
        loss_events = []
        
        for fill in fills:
            pnl = float(fill.get('closedPnl', 0))
            side = fill.get('side', 'unknown').lower()
            
            # RIGGED FILTER: Only harvest rekt longs (long positions with losses)
            if pnl < 0 and side == 'buy':  # Long position that lost money
                loss_event = {
                    "timestamp": datetime.fromtimestamp(fill.get('time', 0) / 1000).isoformat(),
                    "wallet_address": wallet_address,
                    "raw_pnl": pnl,
                    "loss_amount": abs(pnl),
                    "asset": fill.get('coin', 'UNKNOWN'),
                    "side": side,
                    "position_type": "REKT_LONG",  # Mark as rekt long
                    "size": float(fill.get('sz', 0)),
                    "price": float(fill.get('px', 0)),
                    "fee": float(fill.get('fee', 0)),
                    "liquidation": fill.get('liquidation', False),
                    "raw_fill_data": fill  # Keep original for downstream processing
                }
                loss_events.append(loss_event)
                
                logger.debug("🔧 REKT LONG harvested: ${:.2f} loss from {}... on {}".format(
                    loss_event["loss_amount"], 
                    wallet_address[:8],
                    loss_event["asset"]
                ))
        
        return loss_events
    
    def siphon_losses_to_queue(self, loss_events: List[Dict]):
        """
        Mechanical siphoning of losses into processing queue
        One-way flow - no validation or filtering
        """
        for loss_event in loss_events:
            # Add harvesting metadata
            loss_event["harvested_timestamp"] = datetime.now().isoformat()
            loss_event["harvesting_id"] = hashlib.sha256(
                f"{loss_event['wallet_address']}_{loss_event['timestamp']}_{time.time()}".encode()
            ).hexdigest()[:16]
            
            # Mechanical queue append
            self.loss_queue.append(loss_event)
            
            # Update mechanical stats
            self.harvesting_stats["total_losses_siphoned"] += loss_event["loss_amount"]
            if loss_event["liquidation"]:
                self.harvesting_stats["total_liquidations_caught"] += 1
            
            logger.debug("🔧 Siphoned loss: ${:.2f} from {}...".format(
                loss_event["loss_amount"], 
                loss_event["wallet_address"][:8]
            ))
    
    async def run_harvesting_cycle(self) -> List[Dict]:
        """
        Run one mechanical harvesting cycle across all monitored wallets
        Returns raw loss events for downstream processing
        """
        cycle_losses = []
        
        logger.info("🔧 Running harvesting cycle for {} wallets".format(len(self.monitored_wallets)))
        
        for wallet_address in self.monitored_wallets:
            # Mechanical fetch
            fills = await self.fetch_wallet_fills(wallet_address)
            
            # Mechanical extraction
            loss_events = self.extract_loss_events(fills, wallet_address)
            
            # Mechanical siphoning
            if loss_events:
                self.siphon_losses_to_queue(loss_events)
                cycle_losses.extend(loss_events)
        
        logger.info("🔧 Harvesting cycle complete: {} losses siphoned".format(len(cycle_losses)))
        return cycle_losses
    
    def drain_loss_queue(self) -> List[Dict]:
        """
        Drain the loss queue for downstream processing
        Mechanical queue emptying - no processing
        """
        drained_losses = self.loss_queue.copy()
        self.loss_queue.clear()
        
        logger.info("🔧 Drained {} losses from queue".format(len(drained_losses)))
        return drained_losses
    
    def get_harvesting_stats(self) -> Dict:
        """Get mechanical harvesting statistics"""
        uptime = datetime.now() - datetime.fromisoformat(self.harvesting_stats["uptime_start"])
        
        return {
            "harvesting_stats": self.harvesting_stats,
            "queue_size": len(self.loss_queue),
            "uptime_hours": uptime.total_seconds() / 3600,
            "losses_per_hour": self.harvesting_stats["total_losses_siphoned"] / max(uptime.total_seconds() / 3600, 0.1)
        }
    
    async def run_continuous_harvesting(self, cycle_interval: int = 30):
        """
        Run continuous harvesting cycles
        Pure mechanical operation - no intelligence
        """
        logger.info("🔧 Starting continuous harvesting ({}s intervals)".format(cycle_interval))
        
        while True:
            try:
                await self.run_harvesting_cycle()
                await asyncio.sleep(cycle_interval)
                
            except KeyboardInterrupt:
                logger.info("🔧 Harvesting stopped by user")
                break
            except Exception as e:
                logger.error("🔧 Harvesting error: {}".format(str(e)))
                await asyncio.sleep(cycle_interval)

def main():
    """
    Demo the mechanical harvesting engine
    """
    print("🔧 FRY Harvesting Engine - Pure Mechanical Plumbing")
    print("Function: Siphon retail losses from Hyperliquid → Dark Pool")
    
    harvester = FRYHarvestingEngine()
    
    # Add sample wallets to monitor (replace with real addresses)
    sample_wallets = [
        "0x1234567890abcdef1234567890abcdef12345678",
        "0x2345678901bcdef12345678901bcdef123456789",
        "0x3456789012cdef123456789012cdef1234567890"
    ]
    
    print(f"\n🔧 Adding {len(sample_wallets)} wallets to harvesting pipeline...")
    for wallet in sample_wallets:
        harvester.add_wallet_to_monitor(wallet)
    
    # Show harvesting stats
    stats = harvester.get_harvesting_stats()
    print(f"\n📊 Harvesting Pipeline Status:")
    print(f"   Wallets Monitored: {stats['harvesting_stats']['wallets_monitored']}")
    print(f"   Queue Size: {stats['queue_size']}")
    print(f"   Total Losses Siphoned: ${stats['harvesting_stats']['total_losses_siphoned']:,.2f}")
    print(f"   Liquidations Caught: {stats['harvesting_stats']['total_liquidations_caught']}")
    
    print(f"\n🔧 Harvesting engine ready for continuous operation")
    print(f"💡 This is pure plumbing - no processing, just mechanical loss siphoning")
    
    # Note: In production, would run:
    # asyncio.run(harvester.run_continuous_harvesting())

if __name__ == "__main__":
    main()
