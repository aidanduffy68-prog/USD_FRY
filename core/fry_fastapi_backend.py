FRY Trading FastAPI Backend
Unified backend combining market feed, FRY simulator, and balance DB
"""

import asyncio
import json
import sqlite3
import time
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import random

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import websockets
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class PriceData(BaseModel):
    symbol: str
    price: float
    timestamp: int
    change_24h: Optional[float] = None

class SimulateRequest(BaseModel):
    amount: float
    direction: str  # "long" or "short"
    symbol: str = "BTC"

class MirrorRequest(BaseModel):
    pnl: float
    symbol: str = "BTC"
    trade_type: str = "manual"

class BalanceResponse(BaseModel):
    balance: float
    timestamp: int
    last_change: Optional[float] = None
    change_type: Optional[str] = None

class PnLEvent(BaseModel):
    id: int
    timestamp: int
    pnl: float
    balance_before: float
    balance_after: float
    fry_change: float
    symbol: str
    trade_type: str

# FastAPI app
app = FastAPI(title="FRY Trading Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class FRYBackend:
    def __init__(self):
        self.current_balance = 10000.0
        self.price_data = {}
        self.price_history = {
            'BTC': deque(maxlen=100),
            'ETH': deque(maxlen=100)
        }
        self.db_path = "fry_trading.db"
        self.websocket_task = None
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fry_balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                balance REAL NOT NULL,
                change_amount REAL NOT NULL,
                change_type TEXT NOT NULL,
                pnl REAL,
                symbol TEXT,
                trade_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def update_balance(self, pnl: float, symbol: str = "BTC", trade_type: str = "manual") -> Dict:
        """Update FRY balance based on PnL (inverse logic)"""
        old_balance = self.current_balance
        
        # Loser's Arcade Logic: Losses = More FRY, Profits = Less FRY
        if pnl < 0:  # Loss = Mint FRY
            fry_change = abs(pnl) * 10  # 10 FRY per $1 lost
            self.current_balance += fry_change
            change_type = "mint"
        else:  # Profit = Burn FRY
            fry_change = pnl * 5  # 5 FRY burned per $1 profit
            self.current_balance = max(0, self.current_balance - fry_change)
            change_type = "burn"
            fry_change = -fry_change
        
        # Store in database
        timestamp = int(time.time() * 1000)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fry_balance_history 
            (timestamp, balance, change_amount, change_type, pnl, symbol, trade_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, self.current_balance, fry_change, change_type, pnl, symbol, trade_type))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💰 Balance Update: {old_balance:.0f} → {self.current_balance:.0f} FRY ({fry_change:+.0f})")
        
        return {
            "balance_before": old_balance,
            "balance_after": self.current_balance,
            "fry_change": fry_change,
            "change_type": change_type,
            "pnl": pnl,
            "symbol": symbol,
            "trade_type": trade_type
        }
    
    def get_balance_history(self, limit: int = 50) -> List[Dict]:
        """Get recent balance history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, balance, change_amount, change_type, pnl, symbol, trade_type
            FROM fry_balance_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "balance": row[1],
                "change_amount": row[2],
                "change_type": row[3],
                "pnl": row[4],
                "symbol": row[5],
                "trade_type": row[6]
            }
            for row in rows
        ]
    
    async def start_price_stream(self):
        """Start WebSocket price streaming"""
        if self.websocket_task and not self.websocket_task.done():
            return
            
        self.websocket_task = asyncio.create_task(self._price_stream_worker())
        logger.info("🚀 Starting price stream...")
    
    async def _price_stream_worker(self):
        """WebSocket worker for price streaming"""
        uri = "wss://api.hyperliquid.xyz/ws"
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    # Subscribe to BTC and ETH prices
                    subscribe_msg = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "allMids"
                        }
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    logger.info("📡 Connected to Hyperliquid WebSocket")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if data.get("channel") == "allMids" and "data" in data:
                                mids = data["data"]["mids"]
                                timestamp = int(time.time() * 1000)
                                
                                # Update BTC price (index 0)
                                if len(mids) > 0 and mids[0]:
                                    btc_price = float(mids[0])
                                    self.price_data["BTC"] = {
                                        "price": btc_price,
                                        "timestamp": timestamp
                                    }
                                    self.price_history["BTC"].append((timestamp, btc_price))
                                
                                # Update ETH price (index 1)  
                                if len(mids) > 1 and mids[1]:
                                    eth_price = float(mids[1])
                                    self.price_data["ETH"] = {
                                        "price": eth_price,
                                        "timestamp": timestamp
                                    }
                                    self.price_history["ETH"].append((timestamp, eth_price))
                                    
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds

# Global backend instance
backend = FRYBackend()

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    await backend.start_price_stream()

# API Routes
@app.get("/price")
async def get_prices():
    """Get current market prices"""
    if not backend.price_data:
        # Return mock data if no real data available
        timestamp = int(time.time() * 1000)
        return {
            "BTC": {"price": 45000.0, "timestamp": timestamp},
            "ETH": {"price": 2800.0, "timestamp": timestamp}
        }
    
    return backend.price_data

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get price for specific symbol"""
    symbol = symbol.upper()
    
    if symbol not in backend.price_data:
        if symbol == "BTC":
            price = 45000.0 + random.uniform(-1000, 1000)
        elif symbol == "ETH":
            price = 2800.0 + random.uniform(-100, 100)
        else:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        timestamp = int(time.time() * 1000)
        return PriceData(symbol=symbol, price=price, timestamp=timestamp)
    
    data = backend.price_data[symbol]
    return PriceData(
        symbol=symbol,
        price=data["price"],
        timestamp=data["timestamp"]
    )

@app.post("/simulate")
async def simulate_trade(request: SimulateRequest):
    """Simulate a trade and update FRY balance"""
    symbol = request.symbol.upper()
    
    # Get current and previous price
    if symbol in backend.price_history and len(backend.price_history[symbol]) >= 2:
        current_price = backend.price_history[symbol][-1][1]
        prev_price = backend.price_history[symbol][-2][1]
        price_change = current_price - prev_price
    else:
        # Mock price change
        price_change = random.uniform(-100, 100)
    
    # Calculate PnL based on direction
    if request.direction.lower() == "long":
        pnl = (price_change / abs(price_change) if price_change != 0 else 1) * request.amount * random.uniform(0.5, 1.5)
    else:  # short
        pnl = -(price_change / abs(price_change) if price_change != 0 else 1) * request.amount * random.uniform(0.5, 1.5)
    
    # Update balance
    result = backend.update_balance(pnl, symbol, "simulated")
    
    return {
        "trade": {
            "symbol": symbol,
            "direction": request.direction,
            "amount": request.amount,
            "pnl": pnl,
            "price_change": price_change
        },
        "balance_update": result
    }

@app.post("/mirror")
async def mirror_pnl(request: MirrorRequest):
    """Mirror real PnL to FRY balance"""
    result = backend.update_balance(request.pnl, request.symbol, request.trade_type)
    
    return {
        "mirrored_pnl": request.pnl,
        "symbol": request.symbol,
        "balance_update": result
    }

@app.get("/balance")
async def get_balance():
    """Get current FRY balance"""
    history = backend.get_balance_history(1)
    last_change = history[0] if history else None
    
    return BalanceResponse(
        balance=backend.current_balance,
        timestamp=int(time.time() * 1000),
        last_change=last_change["change_amount"] if last_change else None,
        change_type=last_change["change_type"] if last_change else None
    )

@app.get("/balance/history")
async def get_balance_history(limit: int = 50):
    """Get FRY balance history"""
    return backend.get_balance_history(limit)

@app.get("/balance/events")
async def get_pnl_events(limit: int = 20):
    """Get recent PnL events"""
    history = backend.get_balance_history(limit)
    
    events = []
    for i, record in enumerate(history):
        events.append(PnLEvent(
            id=i,
            timestamp=record["timestamp"],
            pnl=record["pnl"] or 0,
            balance_before=record["balance"] - record["change_amount"],
            balance_after=record["balance"],
            fry_change=record["change_amount"],
            symbol=record["symbol"] or "BTC",
            trade_type=record["trade_type"] or "manual"
        ))
    
    return events

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "online",
        "current_balance": backend.current_balance,
        "timestamp": int(time.time() * 1000),
        "price_stream_active": backend.websocket_task and not backend.websocket_task.done(),
        "symbols_tracked": list(backend.price_data.keys()),
        "database_path": backend.db_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
