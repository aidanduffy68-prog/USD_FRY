FRY Live Miner - Core Mechanic Implementation
Real-time Hyperliquid trading loss detection → Automatic FRY minting
Win detection → FRY burning (because you broke the game's spirit 😂)
"""

import asyncio
import json
import time
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import websockets
import requests
from web3 import Web3
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradeEvent:
    """Represents a completed trade with PnL"""
    timestamp: int
    asset: str
    side: str  # "buy" or "sell"
    size: float
    price: float
    pnl: float
    fee: float
    trade_id: str

@dataclass
class FRYMiningEvent:
    """Represents a FRY mining event from losses"""
    timestamp: int
    loss_amount: float
    fry_minted: float
    loss_percentage: float
    multiplier: float
    trade_events: List[TradeEvent]

class FRYLiveMiner:
    def __init__(self, wallet_address: str, testnet: bool = True, db_path: str = "fry_live_mining.db"):
        """
        Initialize the FRY Live Miner
        
        Args:
            wallet_address: Your Hyperliquid wallet address
            testnet: Use Hyperliquid testnet (True) or mainnet (False)
            db_path: SQLite database for mining history
        """
        self.wallet_address = wallet_address
        self.testnet = testnet
        self.db_path = db_path
        
        # API endpoints
        if testnet:
            self.info_url = "https://api.hyperliquid-testnet.xyz/info"
            self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws"
        else:
            self.info_url = "https://api.hyperliquid.xyz/info"
            self.ws_url = "wss://api.hyperliquid.xyz/ws"
        
        # Mining parameters
        self.base_mining_rate = 10.0  # Base FRY per $1 lost
        self.max_multiplier = 10.0    # Max multiplier for big losses
        self.burn_rate = 5.0          # FRY burned per $1 profit
        self.min_threshold = 0.50     # Minimum $0.50 to trigger mining
        
        # State tracking
        self.current_fry_balance = 10000.0  # Starting FRY balance
        self.total_losses_tracked = 0.0
        self.total_profits_tracked = 0.0
        self.total_fry_mined = 0.0
        self.total_fry_burned = 0.0
        self.last_check_time = int(time.time() * 1000)
        
        # Position tracking for PnL calculation
        self.positions = {}  # asset -> position data
        self.last_fills = []  # Recent fills for processing
        
        # Initialize database
        self.init_database()
        self.load_current_state()
        
        logger.info(f"🚀 FRY Live Miner Initialized")
        logger.info(f"👤 Wallet: {wallet_address}")
        logger.info(f"🌐 Network: {'Testnet' if testnet else 'Mainnet'}")
        logger.info(f"💰 Current FRY Balance: {self.current_fry_balance:,.0f}")
    
    def init_database(self):
        """Initialize SQLite database for mining history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FRY mining events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fry_mining_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                event_type TEXT NOT NULL,  -- 'MINT' or 'BURN'
                trigger_amount REAL NOT NULL,  -- Loss/profit amount in USD
                fry_change REAL NOT NULL,  -- FRY minted (+) or burned (-)
                fry_balance_after REAL NOT NULL,
                loss_percentage REAL,
                multiplier REAL,
                asset TEXT,
                trade_data TEXT,  -- JSON of trade events
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Position snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                asset TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL,
                mark_price REAL,
                unrealized_pnl REAL,
                margin_used REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trade fills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_fills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                trade_id TEXT UNIQUE NOT NULL,
                asset TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                price REAL NOT NULL,
                fee REAL NOT NULL,
                pnl REAL,
                processed BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def load_current_state(self):
        """Load current FRY balance and mining stats from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get latest FRY balance
        cursor.execute('''
            SELECT fry_balance_after FROM fry_mining_events 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            self.current_fry_balance = float(result[0])
        
        # Get mining totals
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN event_type = 'MINT' THEN fry_change ELSE 0 END) as total_minted,
                SUM(CASE WHEN event_type = 'BURN' THEN ABS(fry_change) ELSE 0 END) as total_burned,
                SUM(CASE WHEN event_type = 'MINT' THEN trigger_amount ELSE 0 END) as total_losses,
                SUM(CASE WHEN event_type = 'BURN' THEN trigger_amount ELSE 0 END) as total_profits
            FROM fry_mining_events
        ''')
        result = cursor.fetchone()
        if result and result[0]:
            self.total_fry_mined = float(result[0] or 0)
            self.total_fry_burned = float(result[1] or 0)
            self.total_losses_tracked = float(result[2] or 0)
            self.total_profits_tracked = float(result[3] or 0)
        
        conn.close()
        logger.info(f"📊 Loaded state: {self.total_fry_mined:.0f} mined, {self.total_fry_burned:.0f} burned")
    
    async def get_account_state(self) -> Optional[Dict]:
        """Get current account state from Hyperliquid"""
        try:
            payload = {
                "type": "clearinghouseState",
                "user": self.wallet_address
            }
            
            response = requests.post(self.info_url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get account state: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting account state: {e}")
            return None
    
    async def get_user_fills(self, start_time: int = None) -> List[Dict]:
        """Get user fills since start_time"""
        try:
            payload = {
                "type": "userFills",
                "user": self.wallet_address
            }
            
            response = requests.post(self.info_url, json=payload, timeout=10)
            if response.status_code == 200:
                fills = response.json()
                
                # Filter by start_time if provided
                if start_time and fills:
                    fills = [f for f in fills if int(f.get('time', 0)) > start_time]
                
                return fills
            else:
                logger.error(f"Failed to get user fills: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting user fills: {e}")
            return []
    
    def calculate_loss_multiplier(self, loss_amount: float, loss_percentage: float) -> float:
        """Calculate FRY mining multiplier based on loss size and percentage"""
        # Base multiplier from loss amount
        amount_multiplier = min(loss_amount / 100.0, 3.0)  # Up to 3x for $100+ losses
        
        # Percentage multiplier (bigger % losses get more FRY)
        if loss_percentage >= 50.0:
            pct_multiplier = 3.0  # 50%+ loss = 3x multiplier
        elif loss_percentage >= 25.0:
            pct_multiplier = 2.0  # 25%+ loss = 2x multiplier
        elif loss_percentage >= 10.0:
            pct_multiplier = 1.5  # 10%+ loss = 1.5x multiplier
        else:
            pct_multiplier = 1.0  # Small losses = base rate
        
        # Combine multipliers but cap at max
        total_multiplier = min(amount_multiplier * pct_multiplier, self.max_multiplier)
        return total_multiplier
    
    def process_trade_fills(self, fills: List[Dict]) -> Tuple[List[TradeEvent], float, float]:
        """Process fills to extract trade events and calculate net PnL"""
        trade_events = []
        total_pnl = 0.0
        total_fees = 0.0
        
        for fill in fills:
            try:
                trade_event = TradeEvent(
                    timestamp=int(fill.get('time', 0)),
                    asset=fill.get('coin', 'UNKNOWN'),
                    side=fill.get('side', 'unknown'),
                    size=float(fill.get('sz', 0)),
                    price=float(fill.get('px', 0)),
                    pnl=float(fill.get('closedPnl', 0)),  # Realized PnL from this fill
                    fee=float(fill.get('fee', 0)),
                    trade_id=fill.get('tid', str(int(time.time())))
                )
                
                trade_events.append(trade_event)
                total_pnl += trade_event.pnl
                total_fees += trade_event.fee
                
            except Exception as e:
                logger.error(f"Error processing fill: {e}")
                continue
        
        # Fees are always losses
        net_pnl = total_pnl - total_fees
        
        return trade_events, net_pnl, total_fees
    
    async def mine_fry_from_loss(self, loss_amount: float, loss_percentage: float, trade_events: List[TradeEvent]) -> FRYMiningEvent:
        """Mine FRY tokens from trading losses"""
        # Calculate multiplier and FRY reward
        multiplier = self.calculate_loss_multiplier(loss_amount, loss_percentage)
        fry_minted = loss_amount * self.base_mining_rate * multiplier
        
        # Update balances
        old_balance = self.current_fry_balance
        self.current_fry_balance += fry_minted
        self.total_losses_tracked += loss_amount
        self.total_fry_mined += fry_minted
        
        # Create mining event
        mining_event = FRYMiningEvent(
            timestamp=int(time.time()),
            loss_amount=loss_amount,
            fry_minted=fry_minted,
            loss_percentage=loss_percentage,
            multiplier=multiplier,
            trade_events=trade_events
        )
        
        # Save to database
        self.save_mining_event('MINT', loss_amount, fry_minted, loss_percentage, multiplier, trade_events)
        
        # Log the mining event
        logger.info(f"🔥 FRY MINED!")
        logger.info(f"  ├── Loss: ${loss_amount:.2f} ({loss_percentage:.1f}%)")
        logger.info(f"  ├── Multiplier: {multiplier:.1f}x")
        logger.info(f"  ├── FRY Minted: {fry_minted:.0f}")
        logger.info(f"  └── New Balance: {old_balance:.0f} → {self.current_fry_balance:.0f}")
        
        return mining_event
    
    async def burn_fry_from_profit(self, profit_amount: float, trade_events: List[TradeEvent]) -> float:
        """Burn FRY tokens from trading profits (success tax)"""
        fry_to_burn = profit_amount * self.burn_rate
        
        # Don't burn more FRY than we have
        actual_burn = min(fry_to_burn, self.current_fry_balance)
        
        # Update balances
        old_balance = self.current_fry_balance
        self.current_fry_balance = max(0, self.current_fry_balance - actual_burn)
        self.total_profits_tracked += profit_amount
        self.total_fry_burned += actual_burn
        
        # Save to database
        self.save_mining_event('BURN', profit_amount, -actual_burn, 0, 1.0, trade_events)
        
        # Log the burn event
        logger.info(f"🔥 FRY BURNED! (Success Tax)")
        logger.info(f"  ├── Profit: ${profit_amount:.2f}")
        logger.info(f"  ├── FRY Burned: {actual_burn:.0f}")
        logger.info(f"  └── New Balance: {old_balance:.0f} → {self.current_fry_balance:.0f}")
        
        return actual_burn
    
    def save_mining_event(self, event_type: str, trigger_amount: float, fry_change: float, 
                         loss_percentage: float, multiplier: float, trade_events: List[TradeEvent]):
        """Save mining event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prepare trade data as JSON
        trade_data = json.dumps([{
            'timestamp': te.timestamp,
            'asset': te.asset,
            'side': te.side,
            'size': te.size,
            'price': te.price,
            'pnl': te.pnl,
            'fee': te.fee,
            'trade_id': te.trade_id
        } for te in trade_events])
        
        cursor.execute('''
            INSERT INTO fry_mining_events 
            (timestamp, event_type, trigger_amount, fry_change, fry_balance_after, 
             loss_percentage, multiplier, asset, trade_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(time.time()),
            event_type,
            trigger_amount,
            fry_change,
            self.current_fry_balance,
            loss_percentage,
            multiplier,
            trade_events[0].asset if trade_events else 'MIXED',
            trade_data
        ))
        
        conn.commit()
        conn.close()
    
    async def process_new_trades(self):
        """Check for new trades and process PnL for FRY mining/burning"""
        try:
            # Get fills since last check
            new_fills = await self.get_user_fills(self.last_check_time)
            
            if not new_fills:
                return
            
            logger.info(f"📊 Processing {len(new_fills)} new fills...")
            
            # Process fills into trade events
            trade_events, net_pnl, total_fees = self.process_trade_fills(new_fills)
            
            if not trade_events:
                return
            
            # Calculate position size for loss percentage (simplified)
            total_trade_value = sum(abs(te.size * te.price) for te in trade_events)
            
            if abs(net_pnl) >= self.min_threshold:
                if net_pnl < 0:
                    # Loss detected - mine FRY!
                    loss_amount = abs(net_pnl)
                    loss_percentage = (loss_amount / total_trade_value * 100) if total_trade_value > 0 else 0
                    
                    await self.mine_fry_from_loss(loss_amount, loss_percentage, trade_events)
                    
                else:
                    # Profit detected - burn FRY (success tax)
                    await self.burn_fry_from_profit(net_pnl, trade_events)
            else:
                logger.info(f"💸 Small PnL ${net_pnl:.2f} below threshold ${self.min_threshold}")
            
        except Exception as e:
            logger.error(f"Error processing trades: {e}")
    
    async def start_live_mining(self):
        """Start the live FRY mining process"""
        logger.info("🚀 Starting FRY Live Mining...")
        logger.info("📈 Monitoring Hyperliquid for trading losses...")
        logger.info("💡 Every loss mints FRY, every profit burns FRY!")
        
        while True:
            try:
                # Process any new trades
                await self.process_new_trades()
                
                # Update last check time
                self.last_check_time = int(time.time() * 1000)
                
                # Show current stats periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.show_mining_stats()
                
                # Wait before next check
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in mining loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    def show_mining_stats(self):
        """Display current mining statistics"""
        logger.info("📊 FRY MINING STATS")
        logger.info(f"  ├── Current Balance: {self.current_fry_balance:,.0f} FRY")
        logger.info(f"  ├── Total Mined: {self.total_fry_mined:,.0f} FRY")
        logger.info(f"  ├── Total Burned: {self.total_fry_burned:,.0f} FRY")
        logger.info(f"  ├── Losses Tracked: ${self.total_losses_tracked:,.2f}")
        logger.info(f"  └── Profits Tracked: ${self.total_profits_tracked:,.2f}")
    
    def get_mining_summary(self) -> Dict:
        """Get complete mining summary"""
        return {
            "wallet_address": self.wallet_address,
            "current_fry_balance": self.current_fry_balance,
            "total_fry_mined": self.total_fry_mined,
            "total_fry_burned": self.total_fry_burned,
            "total_losses_tracked": self.total_losses_tracked,
            "total_profits_tracked": self.total_profits_tracked,
            "net_pnl": self.total_profits_tracked - self.total_losses_tracked,
            "mining_rate": self.base_mining_rate,
            "burn_rate": self.burn_rate,
            "max_multiplier": self.max_multiplier
        }

# Example usage
async def main():
    """Main function to start FRY live mining"""
    # Your Hyperliquid wallet address
    wallet_address = "0xf551aF8d5373B042DBB9F0933C59213B534174e4"
    
    # Initialize live miner
    miner = FRYLiveMiner(wallet_address, testnet=True)
    
    # Start live mining
    await miner.start_live_mining()

if __name__ == "__main__":
    print("🍟 FRY Live Miner - Core Mechanic")
    print("=" * 50)
    print("Connect wallet → Trade on Hyperliquid → Auto-mine FRY from losses!")
    print("Win trades → FRY gets burned (success tax)")
    print("Lose trades → FRY gets minted (consolation prize)")
    print("=" * 50)
    
    asyncio.run(main())
