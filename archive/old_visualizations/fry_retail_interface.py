#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRY Retail Interface
Simplified interface for retail traders - only interacts with Hyperliquid
Retail traders don't see FRY minting or scoring, just trade normally
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FRYRetailInterface:
    """
    Retail trader interface - transparent Hyperliquid trading
    
    Retail traders:
    - Trade normally on Hyperliquid
    - Experience losses/gains as usual
    - Have no visibility into FRY minting or scoring
    - Don't know their losses are being harvested
    """
    
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
        self.base_url = "https://api.hyperliquid.xyz"
        self.trading_history = []
        
        logger.info("📱 Retail interface initialized for wallet: {}...".format(wallet_address[:8]))
    
    async def fetch_trading_activity(self) -> List[Dict]:
        """
        Fetch recent trading activity from Hyperliquid
        This is what retail traders see - just their normal trading data
        """
        try:
            # Get user fills
            payload = {
                "type": "userFills",
                "user": self.wallet_address
            }
            
            response = requests.post(f"{self.base_url}/info", json=payload)
            
            if response.status_code == 200:
                fills = response.json()
                
                # Process fills into readable format for retail trader
                processed_fills = []
                for fill in fills:
                    processed_fill = {
                        "timestamp": datetime.fromtimestamp(fill.get('time', 0) / 1000).isoformat(),
                        "asset": fill.get('coin', 'UNKNOWN'),
                        "side": fill.get('side', 'unknown'),
                        "size": float(fill.get('sz', 0)),
                        "price": float(fill.get('px', 0)),
                        "pnl": float(fill.get('closedPnl', 0)),
                        "fee": float(fill.get('fee', 0)),
                        "liquidation": fill.get('liquidation', False)
                    }
                    processed_fills.append(processed_fill)
                
                self.trading_history = processed_fills
                return processed_fills
                
            else:
                logger.warning("Failed to fetch trading data: {}".format(response.status_code))
                return []
                
        except Exception as e:
            logger.error("Error fetching trading activity: {}".format(str(e)))
            return []
    
    def get_trading_summary(self) -> Dict:
        """
        Get trading summary that retail trader sees
        No mention of FRY tokens or harvesting
        """
        if not self.trading_history:
            return {"message": "No trading activity found"}
        
        total_pnl = sum(fill['pnl'] for fill in self.trading_history)
        total_fees = sum(fill['fee'] for fill in self.trading_history)
        total_trades = len(self.trading_history)
        liquidations = sum(1 for fill in self.trading_history if fill['liquidation'])
        
        # Asset breakdown
        asset_pnl = {}
        for fill in self.trading_history:
            asset = fill['asset']
            if asset not in asset_pnl:
                asset_pnl[asset] = {'pnl': 0, 'trades': 0}
            asset_pnl[asset]['pnl'] += fill['pnl']
            asset_pnl[asset]['trades'] += 1
        
        return {
            "wallet": "{}...{}".format(self.wallet_address[:6], self.wallet_address[-4:]),
            "total_pnl": round(total_pnl, 2),
            "total_fees": round(total_fees, 2),
            "net_result": round(total_pnl - total_fees, 2),
            "total_trades": total_trades,
            "liquidations": liquidations,
            "win_rate": round((sum(1 for f in self.trading_history if f['pnl'] > 0) / total_trades * 100), 1) if total_trades > 0 else 0,
            "asset_breakdown": asset_pnl,
            "recent_trades": self.trading_history[-5:] if len(self.trading_history) >= 5 else self.trading_history
        }
    
    def display_retail_dashboard(self):
        """
        Display simple dashboard for retail trader
        Clean, normal trading interface with no FRY references
        """
        summary = self.get_trading_summary()
        
        if "message" in summary:
            print(summary["message"])
            return
        
        print("\n" + "="*60)
        print("📊 HYPERLIQUID TRADING SUMMARY")
        print("="*60)
        
        print(f"\n💰 PERFORMANCE")
        print(f"   Total P&L: ${summary['total_pnl']:,.2f}")
        print(f"   Total Fees: ${summary['total_fees']:,.2f}")
        print(f"   Net Result: ${summary['net_result']:,.2f}")
        
        print(f"\n📈 STATISTICS")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']}%")
        print(f"   Liquidations: {summary['liquidations']}")
        
        print(f"\n🎯 BY ASSET")
        for asset, stats in summary['asset_breakdown'].items():
            print(f"   {asset}: ${stats['pnl']:,.2f} ({stats['trades']} trades)")
        
        print(f"\n📋 RECENT TRADES")
        for i, trade in enumerate(summary['recent_trades'], 1):
            status = "🔴 LIQUIDATED" if trade['liquidation'] else ("🟢 PROFIT" if trade['pnl'] > 0 else "🔴 LOSS")
            print(f"   {i}. {trade['asset']} {trade['side']}: ${trade['pnl']:,.2f} {status}")
        
        print("\n" + "="*60)
        print("Continue trading on Hyperliquid as normal")
        print("="*60 + "\n")

async def main():
    """
    Demo retail interface - what traders actually see
    """
    print("📱 FRY Retail Interface - Normal Hyperliquid Trading View")
    
    # Sample wallet (replace with actual)
    wallet_address = input("Enter your Hyperliquid wallet address: ").strip()
    
    if not wallet_address:
        print("Please provide a valid wallet address")
        return
    
    retail_interface = FRYRetailInterface(wallet_address)
    
    print("\n🔄 Fetching your Hyperliquid trading data...")
    
    # Fetch trading activity
    await retail_interface.fetch_trading_activity()
    
    # Display normal trading dashboard
    retail_interface.display_retail_dashboard()
    
    print("💡 This is what you see as a retail trader.")
    print("Your losses are being harvested behind the scenes for FRY minting,")
    print("but you experience normal Hyperliquid trading.")

if __name__ == "__main__":
    asyncio.run(main())
