# 🍟 FRY Degen Subnet - Bittensor Integration

> **Decentralized network for predicting and validating degenerate trading outcomes**

A real Bittensor subnet that combines AI-powered prediction markets with proof-of-loss tokenomics. Miners compete to identify the most degenerate trades, validators verify outcomes, and FRY tokens are minted from confirmed losses.

## 🎯 What Is This?

The **FRY Degen Subnet** is a Bittensor subnet where:

- 🔍 **Miners** scan Hyperliquid for high-risk positions and predict liquidations
- ✅ **Validators** verify actual outcomes and score miner accuracy  
- 🍟 **FRY tokens** are minted when losses are confirmed (10 FRY per $1 lost)
- 💰 **TAO rewards** go to miners with accurate predictions
- 📊 **Degen scores** quantify risk levels (0-100 scale)

## 🚀 Quick Start

### 1. Install Bittensor

```bash
pip3 install bittensor
```

### 2. Create Wallets

```bash
# Miner wallet
btcli wallet new_coldkey --wallet.name miner
btcli wallet new_hotkey --wallet.name miner --wallet.hotkey default

# Validator wallet  
btcli wallet new_coldkey --wallet.name validator
btcli wallet new_hotkey --wallet.name validator --wallet.hotkey default
```

### 3. Get Testnet TAO

```bash
btcli wallet faucet --wallet.name miner --subtensor.network test
btcli wallet faucet --wallet.name validator --subtensor.network test
```

### 4. Register on Subnet

```bash
# Register miner
btcli subnet register --netuid 1 --wallet.name miner --subtensor.network test

# Register validator
btcli subnet register --netuid 1 --wallet.name validator --subtensor.network test
```

### 5. Run the Subnet

```bash
# Terminal 1: Start miner
cd fry-liquidity-rails-clean/liquidity-rails/core/subnet
python3 bittensor_degen_miner.py --netuid 1 --subtensor.network test

# Terminal 2: Start validator
python3 bittensor_degen_validator.py --netuid 1 --subtensor.network test

# Terminal 3: Start FRY Casino (for minting)
cd /tmp/usd_fry_casino/core
python3 fry_fastapi_backend.py
```

## 📚 Documentation

- **[Bittensor Integration Guide](fry-liquidity-rails-clean/liquidity-rails/docs/BITTENSOR_INTEGRATION_GUIDE.md)** - Complete setup and deployment
- **[Degen Subnet Spec](fry-liquidity-rails-clean/liquidity-rails/docs/DEGEN_SUBNET_SPEC.md)** - Technical specification
- **[Casino Integration](fry-liquidity-rails-clean/liquidity-rails/docs/DEGEN_SUBNET_CASINO_INTEGRATION.md)** - FRY minting integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Bittensor Network                       │
│                                                           │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│  │  Miners  │◀────▶│ Subtensor│◀────▶│Validators│      │
│  │ (Axons)  │      │ (Chain)  │      │(Dendrites)│      │
│  └──────────┘      └──────────┘      └──────────┘      │
│       │                                      │           │
│       │ DegenSynapse                        │           │
│       ▼                                      ▼           │
│  Hyperliquid API                    Score & Validate    │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              FRY Casino Backend                          │
│                                                           │
│          Mint FRY from validated losses                  │
│          10 FRY per $1 lost × degen multiplier          │
└─────────────────────────────────────────────────────────┘
```

## 🎮 How It Works

### Miner Workflow

1. **Scan Hyperliquid** for open positions
2. **Calculate degen score** (0-100):
   - Leverage: 100x = 30 points
   - Position size: $50k+ = 25 points
   - Volatility: 20%+ = 20 points
   - Unrealized loss: $1k+ = 15 points
   - Distance to liquidation: 10 points
3. **Predict outcome**:
   - Loss probability (0-1)
   - Timeline to liquidation (seconds)
   - Confidence score
4. **Serve predictions** via Bittensor Axon

### Validator Workflow

1. **Query miners** via Bittensor Dendrite
2. **Monitor positions** on Hyperliquid
3. **Detect liquidations** via API
4. **Score miners** based on accuracy
5. **Set weights** on Subtensor (chain)
6. **Mint FRY** via casino backend

### Example: Your XRP Position

**Position:**
- Size: $3,340
- PnL: -196.4% (-$6,560)
- Leverage: 50x

**Miner Prediction:**
```
Degen Score: 95/100
Loss Probability: 85%
Timeline: 7,200 seconds (2 hours)
Reasoning: "50x leverage | $6560 underwater | extreme degen detected"
```

**If Liquidated:**
```
Validator confirms: $6,560 loss
FRY Minted: 65,600 × 10x multiplier = 656,000 FRY
Miner TAO Reward: Based on prediction accuracy
```

## 💎 Dual Token Economy

### FRY Token (Loss Proof)
- **Minted**: From validated losses
- **Rate**: 10 FRY per $1 lost
- **Multiplier**: Up to 100x based on degen score
- **Purpose**: Quantifiable proof of trading losses

### TAO Token (Prediction Rewards)
- **Earned**: By accurate miners/validators
- **Distribution**: Via Bittensor consensus
- **Staking**: Required for participation
- **Purpose**: Incentivize accurate predictions

## 🔧 Components

### Core Subnet Files
- `bittensor_degen_miner.py` - Miner neuron (Axon)
- `bittensor_degen_validator.py` - Validator neuron (Dendrite)
- `bittensor_subnet_protocol.py` - Custom DegenSynapse protocol
- `degen_subnet_core.py` - Subnet runtime logic

### Integration Files
- `degen_subnet_integration.py` - FastAPI integration layer
- `fry_fastapi_backend.py` - Casino backend (from losers-casino branch)

### Smart Contracts
- `ProofOfLossToken.sol` - FRY token contract
- `FRYMemeToken.sol` - ERC20 implementation

## 📊 Monitoring

```bash
# Check miner status
btcli wallet overview --wallet.name miner --subtensor.network test

# View subnet metagraph
btcli subnet metagraph --netuid 1 --subtensor.network test

# Check FRY balance
curl http://localhost:8000/balance

# View recent events
curl http://localhost:8000/balance/events
```

## 🌟 Features

✅ Real Bittensor SDK integration (not a fork)  
✅ Custom DegenSynapse protocol  
✅ Hyperliquid API integration  
✅ Automated FRY minting from losses  
✅ TAO rewards for accurate predictions  
✅ On-chain weight setting via Subtensor  
✅ Degen score calculation (0-100)  
✅ Loss probability prediction  
✅ Liquidation timeline estimation  

## 🤝 Contributing

This is a fun application demonstrating:
- Bittensor subnet architecture
- Proof-of-loss tokenomics
- Decentralized prediction markets
- AI-powered risk assessment

Feel free to fork, experiment, and build on top of it!

## 📜 License

MIT License - This is a satirical/educational project

## 🔗 Links

- [Bittensor Docs](https://docs.bittensor.com)
- [Hyperliquid API](https://hyperliquid.gitbook.io)
- [Original Losers Casino Branch](https://github.com/aidanduffy68-prog/USD_FRY/tree/git-checkout--b-add-losers-casino)

---

**The Innovation:** We've combined Bittensor's decentralized AI infrastructure with proof-of-loss tokenomics to create the world's first subnet for quantifying and predicting financial degeneracy at scale. 🍟📉
