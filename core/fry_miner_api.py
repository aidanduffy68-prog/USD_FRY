FRY Miner API Backend
Provides real-time data from the Node.js miner to the web dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import asyncio

app = FastAPI(title="FRY Miner API", version="1.0.0")

# Enable CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to miner state file
STATE_FILE = "fry-miner-state.json"

def load_miner_state() -> Dict:
    """Load current miner state from file"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}")
    
    # Return default state if file doesn't exist or error
    return {
        "wallet_address": "0xf551aF8d5373B042DBB9F0933C59213B534174e4",
        "total_fry_minted": 0,
        "total_fry_burned": 0,
        "total_losses_tracked": 0,
        "total_profits_tracked": 0,
        "net_pnl": 0,
        "mining_active": False,
        "last_update": datetime.now().isoformat(),
        "recent_activities": [],
        "blockchain_enabled": True
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "FRY Miner API is running", "timestamp": datetime.now().isoformat()}

@app.get("/miner/status")
async def get_miner_status():
    """Get current miner status and statistics"""
    state = load_miner_state()
    
    return {
        "status": "active" if state.get("mining_active", False) else "inactive",
        "wallet_address": state.get("wallet_address", ""),
        "blockchain_enabled": state.get("blockchain_enabled", False),
        "last_update": state.get("last_update", datetime.now().isoformat()),
        "uptime_seconds": 0  # Could track this if needed
    }

@app.get("/miner/stats")
async def get_miner_stats():
    """Get current mining statistics with live virtual FRY"""
    try:
        # Load state from fry-miner.js state file
        state_file = 'fry-miner-state.json'
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Get live position data for unrealized FRY calculation
            wallet_address = state.get("wallet_address", "0xf551aF8d5373B042DBB9F0933C59213B534174e4")
            position_data = await get_position_data(wallet_address)
            
            if position_data:
                unrealized_fry = await get_virtual_fry_from_positions(wallet_address)
                account_value = float(position_data.get("marginSummary", {}).get("accountValue", "1000"))
                trader_class = await classify_trader(account_value)
            else:
                unrealized_fry = 0
                account_value = 0
                trader_class = "Unknown"
            
            # Convert to 1:1 peg for realized FRY (legacy data was 10:1)
            legacy_fry_minted = state.get("total_fry_minted", 0)
            legacy_fry_burned = state.get("total_fry_burned", 0)
            realized_fry = (legacy_fry_minted - legacy_fry_burned) / 10  # Convert to 1:1 peg
            
            total_fry_power = realized_fry + unrealized_fry
            
            return {
                "fry_balance": realized_fry,
                "unrealized_fry_balance": unrealized_fry,
                "total_fry_power": total_fry_power,
                "account_value": account_value,
                "trader_class": trader_class,
                "total_fry_minted": state.get("total_fry_minted", 0),
                "total_fry_burned": state.get("total_fry_burned", 0),
                "losses_tracked_usd": state.get("total_losses_tracked", 0),
                "profits_tracked_usd": state.get("total_profits_tracked", 0),
                "net_pnl_usd": state.get("total_losses_tracked", 0) - state.get("total_profits_tracked", 0),
                "last_update": state.get("last_update", datetime.now().isoformat()),
                "wallet_address": wallet_address
            }
        else:
            # Return default values if no state file
            return {
                "fry_balance": 0,
                "unrealized_fry_balance": 0,
                "total_fry_power": 0,
                "account_value": 0,
                "trader_class": "Unknown",
                "total_fry_minted": 0,
                "total_fry_burned": 0,
                "losses_tracked_usd": 0,
                "profits_tracked_usd": 0,
                "net_pnl_usd": 0,
                "last_update": datetime.now().isoformat(),
                "wallet_address": ""
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading miner stats: {str(e)}")

async def get_position_data(wallet_address: str):
    """Get position data from Hyperliquid API"""
    try:
        payload = {
            "type": "clearinghouseState",
            "user": wallet_address
        }
        
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://api.hyperliquid.xyz/info",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        print(f"Error fetching position data: {e}")
    return None

async def get_virtual_fry_from_positions(wallet_address: str) -> float:
    """Calculate unrealized FRY balance from current unrealized P&L"""
    try:
        data = await get_position_data(wallet_address)
        if not data or "assetPositions" not in data:
            return 0
            
        total_unrealized_pnl = 0
        
        for pos in data["assetPositions"]:
            if pos.get("position") and pos["position"].get("szi", "0") != "0":
                unrealized_pnl = float(pos["position"].get("unrealizedPnl", "0"))
                coin = pos["position"].get("coin", "Unknown")
                print(f"Position {coin}: {unrealized_pnl} unrealized P&L")
                total_unrealized_pnl += unrealized_pnl
        
        print(f"Total unrealized P&L: {total_unrealized_pnl}")
        
        # Calculate unrealized FRY balance with 1:1 peg and volatility weighting
        if total_unrealized_pnl < 0:
            # Base 1:1 peg: 1 FRY per $1 loss
            base_unrealized_fry = abs(total_unrealized_pnl)
            
            # Apply volatility weighting for pain metrics
            volatility_multiplier = await calculate_volatility_multiplier(data)
            pain_weighted_fry = base_unrealized_fry * volatility_multiplier
            
            print(f"Base unrealized FRY (1:1): {base_unrealized_fry}")
            print(f"Volatility multiplier: {volatility_multiplier}x")
            print(f"Pain-weighted FRY: {pain_weighted_fry}")
            return pain_weighted_fry
        else:
            return 0  # No unrealized FRY for net profits
                    
    except Exception as e:
        print(f"Error calculating unrealized FRY: {e}")
    
    return 0

async def calculate_volatility_multiplier(position_data):
    """Calculate volatility-weighted pain multiplier for unrealized losses"""
    try:
        # Extract position details for pain calculation
        total_position_value = 0
        max_leverage = 1
        volatility_factor = 1.0
        
        for pos in position_data.get("assetPositions", []):
            if pos.get("position") and pos["position"].get("szi", "0") != "0":
                position = pos["position"]
                position_value = float(position.get("positionValue", "0"))
                leverage = float(position["leverage"].get("value", 1))
                coin = position.get("coin", "")
                
                total_position_value += abs(position_value)
                max_leverage = max(max_leverage, leverage)
                
                # Asset-specific volatility factors
                if coin in ["BTC", "ETH"]: 
                    volatility_factor = max(volatility_factor, 1.2)
                elif coin in ["SOL", "AVAX", "MATIC"]:
                    volatility_factor = max(volatility_factor, 1.5)
                else:  # Altcoins and memecoins
                    volatility_factor = max(volatility_factor, 2.0)
        
        # Get account equity for wealth adjustment
        account_value = float(position_data.get("marginSummary", {}).get("accountValue", "1000"))
        
        # Calculate pain multiplier components
        leverage_pain = min(max_leverage ** 1.2, 10)  # Leverage amplifies pain
        position_risk = min(total_position_value / max(account_value, 1), 3)  # Position size vs account
        wealth_dampener = max(0.5, min(2.0, 50000 / max(account_value, 1000)))  # Rich feel less pain
        
        # Combined multiplier (capped at 50x for sanity)
        multiplier = min(leverage_pain * position_risk * volatility_factor * wealth_dampener, 50)
        
        return max(1.0, multiplier)  # Minimum 1x multiplier
        
    except Exception as e:
        print(f"Error calculating volatility multiplier: {e}")
        return 1.0  # Default to 1:1 peg if calculation fails

async def classify_trader(account_value):
    """Classify trader based on account size"""
    if account_value <= 5000:
        return "Shrimp"
    elif account_value <= 50000:
        return "Retail" 
    elif account_value < 1000000:
        return "Fish"
    else:
        return "Whale"

@app.get("/miner/activity")
async def get_recent_activity():
    """Get recent mining activities"""
    state = load_miner_state()
    activities = state.get("recent_activities", [])
    
    # Return last 20 activities, most recent first
    return {
        "activities": activities[-20:][::-1],
        "total_count": len(activities)
    }

@app.get("/miner/activity/live")
async def get_live_activity():
    """Get live activity feed with real-time updates"""
    state = load_miner_state()
    
    # Check if miner is running by looking at recent activity
    recent_activities = state.get("recent_activities", [])
    is_active = False
    
    if recent_activities:
        # Check if last activity was within 30 seconds
        try:
            last_activity_time = datetime.fromisoformat(recent_activities[-1].get("timestamp", ""))
            time_diff = (datetime.now() - last_activity_time).total_seconds()
            is_active = time_diff < 30
        except:
            pass
    
    return {
        "is_mining": is_active,
        "recent_activities": recent_activities[-5:][::-1],  # Last 5 activities
        "status_message": "🔥 Active - Monitoring Hyperliquid trades" if is_active else "⏸️ Waiting for trading activity"
    }

@app.get("/dashboard")
async def serve_dashboard():
    """Serve the mining dashboard"""
    dashboard_path = "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /CascadeProjects/windsurf-project/fry_mining_dashboard.html"
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")

@app.get("/")
async def serve_dashboard_root():
    """Serve the mining dashboard at root"""
    return await serve_dashboard()

@app.post("/miner/simulate")
async def simulate_mining_event(event_type: str, amount: float, asset: str = "BTC"):
    """Simulate a mining event for testing (when miner isn't running)"""
    if event_type not in ["loss", "profit"]:
        raise HTTPException(status_code=400, detail="Event type must be 'loss' or 'profit'")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Create simulated activity
    timestamp = datetime.now().isoformat()
    
    if event_type == "loss":
        fry_amount = int(amount * 100)  # 100 FRY per $1 lost
        activity = {
            "type": "mint",
            "timestamp": timestamp,
            "asset": asset,
            "pnl_usd": -amount,
            "fry_amount": fry_amount,
            "description": f"Lost ${amount:.2f} on {asset} → Minted {fry_amount:,} FRY",
            "multiplier": 1.0
        }
    else:  # profit
        fry_amount = int(amount * 50)   # 50 FRY per $1 profit
        activity = {
            "type": "burn",
            "timestamp": timestamp,
            "asset": asset,
            "pnl_usd": amount,
            "fry_amount": fry_amount,
            "description": f"Profit ${amount:.2f} on {asset} → Burned {fry_amount:,} FRY",
            "multiplier": 1.0
        }
    
    return {
        "simulated": True,
        "activity": activity,
        "message": f"Simulated {event_type} of ${amount:.2f} on {asset}"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FRY Miner API server...")
    print("📊 Dashboard will be available at: http://localhost:8001/dashboard")
    print("🔗 API docs available at: http://localhost:8001/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
