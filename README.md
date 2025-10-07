# 🍟 FryBoy Lite - Interactive Demo

## Try It Now!

Run the interactive FryBoy demo directly in your terminal:

```bash
python frybot_lite.py
```

## What You'll Experience

🚀 **Automatic Demo**: Watch 3 sample trades get processed with real slippage calculations

💰 **Portfolio Summary**: See your FRY balance and loss recovery rate

🎮 **Interactive Mode**: 
- Simulate custom trades
- Run batch simulations
- View detailed mechanics explanations
- Reset and try again

## Core FryBoy Mechanics Demonstrated

### 1. Slippage Harvesting
- Monitors trades for slippage losses
- Calculates impact based on trade size vs market cap
- Includes network fees and timing losses

### 2. Pain Multiplier System
- Small losses (≤$100): 1.0x multiplier
- Medium losses ($100-$500): 1.5x multiplier
- Large losses ($500-$1000): 2.0x multiplier
- Huge losses ($1000-$5000): 3.0x multiplier
- Massive losses (>$5000): 4.0x multiplier

### 3. FRY Minting
- Base rate: 0.5 FRY per $1 lost
- Multiplied by pain factor
- Automatically credited to your balance

### 4. Recovery Mechanism
- FRY tokens represent your harvested losses
- Can be used for fee rebates, governance, staking
- Turns trading friction into tradeable assets

---

*No external dependencies required - runs with Python 3 standard libraries only!*
