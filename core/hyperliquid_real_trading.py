Hyperliquid Real Trading Integration with FRY Token Mirroring
Places real trades on Hyperliquid testnet and mirrors PnL to FRY balance
"""

import time
import json
import os
from typing import Dict, Optional, Tuple
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HyperliquidFRYMirror:
    def __init__(self, private_key: str = None, testnet: bool = True):
        """
        Initialize Hyperliquid trading with FRY mirroring
        
        Args:
            private_key: Ethereum private key for signing transactions
            testnet: Use testnet (True) or mainnet (False)
        """
        self.testnet = testnet
        self.fry_balance = 10000.0  # Starting FRY balance
        
        # Load private key from env if not provided
        if private_key is None:
            # Try to load from erc20-token/.env
            try:
                with open('erc20-token/.env', 'r') as f:
                    for line in f:
                        if line.startswith('PRIVATE_KEY='):
                            private_key = line.split('=', 1)[1].strip()
                            break
            except:
                pass
            
            if not private_key:
                private_key = os.getenv('PRIVATE_KEY')
            
            if not private_key:
                raise ValueError("Private key required. Set PRIVATE_KEY env var or pass directly.")
        
        # Clean private key - remove 0x prefix and whitespace
        private_key = private_key.strip()
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        
        # Validate hex format
        if not all(c in '0123456789abcdefABCDEF' for c in private_key):
            raise ValueError("Invalid private key format. Must be 64 character hex string.")
        
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # Initialize Hyperliquid clients
        base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
        self.info = Info(base_url, skip_ws=True)
        self.exchange = Exchange(self.account, base_url, account_address=self.address)
        
        logger.info(f"🚀 Initialized Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
        logger.info(f"📍 Address: {self.address}")
        logger.info(f"💰 Starting FRY Balance: {self.fry_balance:,.0f}")
    
    def get_account_state(self) -> Dict:
        """Get current account state from Hyperliquid"""
        try:
            user_state = self.info.user_state(self.address)
            return user_state
        except Exception as e:
            logger.error(f"❌ Failed to get account state: {e}")
            return {}
    
    def get_available_assets(self) -> list:
        """Get list of available trading assets"""
        try:
            meta = self.info.meta()
            assets = [asset['name'] for asset in meta['universe']]
            return assets
        except Exception as e:
            logger.error(f"❌ Failed to get assets: {e}")
            return []
    
    def place_market_order(self, asset: str, is_buy: bool, size: float, reduce_only: bool = False) -> Dict:
        """
        Place a market order on Hyperliquid
        
        Args:
            asset: Asset symbol (e.g., "BTC", "ETH")
            is_buy: True for buy, False for sell
            size: Order size
            reduce_only: True to only reduce existing position
        
        Returns:
            Order result dictionary
        """
        try:
            # Get current price for reference
            all_mids = self.info.all_mids()
            current_price = float(all_mids.get(asset, 0))
            
            if current_price == 0:
                return {
                    "success": False,
                    "error": f"Could not get price for {asset}",
                    "asset": asset
                }
            
            # Place market order
            order_result = self.exchange.market_open(
                asset=asset,
                is_buy=is_buy,
                sz=size,
                reduce_only=reduce_only
            )
            
            logger.info(f"📈 {'BUY' if is_buy else 'SELL'} {size} {asset} @ ~${current_price:,.2f}")
            logger.info(f"📋 Order result: {order_result}")
            
            return {
                "success": True,
                "order_result": order_result,
                "asset": asset,
                "is_buy": is_buy,
                "size": size,
                "estimated_price": current_price,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Market order failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "asset": asset
            }
    
    def get_position_pnl(self, asset: str) -> Optional[float]:
        """Get current PnL for a specific asset position"""
        try:
            user_state = self.get_account_state()
            
            if not user_state or 'assetPositions' not in user_state:
                return None
            
            for position in user_state['assetPositions']:
                if position['position']['coin'] == asset:
                    unrealized_pnl = float(position['position']['unrealizedPnl'])
                    return unrealized_pnl
            
            return 0.0  # No position found
            
        except Exception as e:
            logger.error(f"❌ Failed to get PnL for {asset}: {e}")
            return None
    
    def close_position(self, asset: str) -> Dict:
        """Close entire position for an asset"""
        try:
            user_state = self.get_account_state()
            
            if not user_state or 'assetPositions' not in user_state:
                return {"success": False, "error": "No positions found"}
            
            # Find position
            position_size = 0
            for position in user_state['assetPositions']:
                if position['position']['coin'] == asset:
                    position_size = float(position['position']['szi'])
                    break
            
            if position_size == 0:
                return {"success": False, "error": f"No position in {asset}"}
            
            # Close position (sell if long, buy if short)
            is_buy = position_size < 0  # Buy to close short, sell to close long
            close_size = abs(position_size)
            
            close_result = self.place_market_order(
                asset=asset,
                is_buy=is_buy,
                size=close_size,
                reduce_only=True
            )
            
            if close_result["success"]:
                logger.info(f"🔒 Closed {asset} position: {position_size}")
            
            return close_result
            
        except Exception as e:
            logger.error(f"❌ Failed to close {asset} position: {e}")
            return {"success": False, "error": str(e)}
    
    def mirror_real_trade_to_fry(self, pnl: float) -> Dict:
        """
        Mirror real trading PnL to FRY balance
        
        Args:
            pnl: Realized PnL from trade (positive = profit, negative = loss)
        
        Returns:
            Dictionary with FRY balance update details
        """
        old_balance = self.fry_balance
        
        if pnl < 0:
            # Lost money → Gain FRY tokens (consolation prize)
            fry_gained = abs(pnl) * 100  # 100 FRY per $1 lost
            self.fry_balance += fry_gained
            outcome = "REKT_REWARDED"
            fry_change = fry_gained
            
        else:
            # Made money → Lose FRY tokens (success tax)
            fry_lost = pnl * 50  # 50 FRY per $1 gained
            self.fry_balance = max(0, self.fry_balance - fry_lost)  # Don't go negative
            outcome = "PROFIT_TAXED"
            fry_change = -fry_lost
        
        result = {
            "pnl_usd": pnl,
            "fry_balance_before": old_balance,
            "fry_balance_after": self.fry_balance,
            "fry_change": fry_change,
            "outcome": outcome,
            "timestamp": time.time()
        }
        
        logger.info(f"💰 PnL: ${pnl:+.2f} → FRY: {fry_change:+.0f} → Balance: {self.fry_balance:,.0f}")
        logger.info(f"🎯 Outcome: {outcome}")
        
        return result
    
    def execute_dummy_trade_cycle(self, asset: str = "BTC", position_size: float = 0.001) -> Dict:
        """
        Execute a complete dummy trade cycle: open → wait → close → mirror PnL
        
        Args:
            asset: Asset to trade
            position_size: Size of position to open
        
        Returns:
            Complete trade cycle results
        """
        logger.info(f"🎲 Starting dummy trade cycle: {position_size} {asset}")
        
        # Step 1: Open position (randomly buy or sell)
        import random
        is_buy = random.choice([True, False])
        
        open_result = self.place_market_order(asset, is_buy, position_size)
        if not open_result["success"]:
            return {
                "success": False,
                "error": "Failed to open position",
                "details": open_result
            }
        
        # Step 2: Wait for position to develop
        logger.info("⏳ Waiting 30 seconds for position to develop...")
        time.sleep(30)
        
        # Step 3: Get current PnL
        current_pnl = self.get_position_pnl(asset)
        if current_pnl is None:
            logger.warning("⚠️ Could not fetch PnL, proceeding with close...")
            current_pnl = 0.0
        
        logger.info(f"📊 Current unrealized PnL: ${current_pnl:+.2f}")
        
        # Step 4: Close position
        close_result = self.close_position(asset)
        if not close_result["success"]:
            logger.error("❌ Failed to close position")
            return {
                "success": False,
                "error": "Failed to close position",
                "details": close_result
            }
        
        # Step 5: Wait for settlement and get final PnL
        logger.info("⏳ Waiting for trade settlement...")
        time.sleep(10)
        
        # For demo purposes, use the unrealized PnL as realized PnL
        # In practice, you'd fetch the actual realized PnL from trade history
        realized_pnl = current_pnl
        
        # Step 6: Mirror PnL to FRY balance
        fry_result = self.mirror_real_trade_to_fry(realized_pnl)
        
        return {
            "success": True,
            "asset": asset,
            "position_size": position_size,
            "direction": "BUY" if is_buy else "SELL",
            "open_result": open_result,
            "close_result": close_result,
            "realized_pnl": realized_pnl,
            "fry_mirror": fry_result,
            "timestamp": time.time()
        }


# Example usage and testing
def test_hyperliquid_connection():
    """Test connection to Hyperliquid testnet"""
    try:
        # Initialize with testnet
        trader = HyperliquidFRYMirror(testnet=True)
        
        # Test connection
        logger.info("🔍 Testing connection...")
        account_state = trader.get_account_state()
        
        if account_state:
            logger.info("✅ Connection successful!")
            
            # Show account info
            if 'marginSummary' in account_state:
                margin = account_state['marginSummary']
                logger.info(f"💰 Account Value: ${float(margin.get('accountValue', 0)):,.2f}")
                logger.info(f"💳 Total Margin Used: ${float(margin.get('totalMarginUsed', 0)):,.2f}")
            
            # Show available assets
            assets = trader.get_available_assets()
            logger.info(f"📈 Available assets: {assets[:10]}...")  # Show first 10
            
        else:
            logger.error("❌ Connection failed")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")


def demo_fry_mirroring():
    """Demo the FRY mirroring function with mock PnL values"""
    logger.info("🧪 Testing FRY mirroring with mock PnL...")
    
    # Create a mock trader without real connection for testing
    class MockTrader:
        def __init__(self):
            self.fry_balance = 10000.0
        
        def mirror_real_trade_to_fry(self, pnl: float):
            old_balance = self.fry_balance
            
            if pnl < 0:
                # Lost money → Gain FRY tokens (consolation prize)
                fry_gained = abs(pnl) * 100  # 100 FRY per $1 lost
                self.fry_balance += fry_gained
                outcome = "REKT_REWARDED"
                fry_change = fry_gained
            else:
                # Made money → Lose FRY tokens (success tax)
                fry_lost = pnl * 50  # 50 FRY per $1 gained
                self.fry_balance = max(0, self.fry_balance - fry_lost)
                outcome = "PROFIT_TAXED"
                fry_change = -fry_lost
            
            return {
                "pnl_usd": pnl,
                "fry_balance_before": old_balance,
                "fry_balance_after": self.fry_balance,
                "fry_change": fry_change,
                "outcome": outcome,
                "timestamp": time.time()
            }
    
    trader = MockTrader()
    
    # Test various PnL scenarios
    test_pnls = [-50.0, 25.0, -10.0, 100.0, -5.0]
    
    for i, pnl in enumerate(test_pnls, 1):
        logger.info(f"\n--- Test {i}: PnL ${pnl:+.2f} ---")
        result = trader.mirror_real_trade_to_fry(pnl)
        
        print(f"PnL: ${result['pnl_usd']:+.2f}")
        print(f"FRY Change: {result['fry_change']:+.0f}")
        print(f"New Balance: {result['fry_balance_after']:,.0f}")
        print(f"Outcome: {result['outcome']}")


if __name__ == "__main__":
    print("🚀 Hyperliquid Real Trading + FRY Mirror")
    print("=" * 50)
    
    # Test connection first
    test_hyperliquid_connection()
    
    print("\n" + "=" * 50)
    
    # Demo FRY mirroring
    demo_fry_mirroring()
    
    print("\n🎯 To execute real trades:")
    print("1. Ensure you have testnet funds")
    print("2. Call execute_dummy_trade_cycle()")
    print("3. Monitor FRY balance changes")
