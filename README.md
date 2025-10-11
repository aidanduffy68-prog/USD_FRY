# 🍟 USD_FRY Protocol

> **Decentralized liquidity rails for processing trading wreckage**

Live on Arbitrum Mainnet. Process trading losses into FRY tokens with Chainlink-verified prices. Launched October 11, 2025 - one day after the $19B liquidation event.

## 🚀 Live on Arbitrum Mainnet

**Deployed October 11, 2025**

```
USD_FRY Token:               0x492397d5912C016F49768fBc942d894687c5fe33
WreckageProcessorWithOracle: 0xf97E890aDf8968256225060e8744a797954C33CF
FRYPredictionMarket:         0xdF0B798E51d5149fE97D57fbBc8D6A8A0756204e
```

**Chainlink Oracles:**
- BTC/USD: `0x6ce185860a4963106506C203335A2910413708e9`
- ETH/USD: `0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612`

[View on Arbiscan →](https://arbiscan.io/address/0x492397d5912C016F49768fBc942d894687c5fe33)

## 🎯 What Happened

### October 10, 2024
- **$19B liquidations** (largest in crypto history)
- **1.6M traders** affected
- **87% long positions** liquidated
- **BTC**: $122k → $102k
- **Centralized systems failed** (Binance/Wintermute rumors)

### FRY's Response
- Launched **October 9, 2024** (one day before crash)
- Thesis validated: need for decentralized liquidity alternatives
- Now live on Arbitrum Mainnet with Chainlink oracles

## 🚀 Quick Start

### Use the Protocol
1. Visit [Live Demo](https://aidanduffy68-prog.github.io/USD_FRY/)
2. Connect wallet (Arbitrum mainnet)
3. Process wreckage or bet on prediction markets

### Deploy Contracts
```bash
cd fry-liquidity-rails-clean/liquidity-rails/core/contracts
npm install
npm run deploy:mainnet
```

## 📚 Documentation

**Main Project:**
- **[FRY Liquidity Rails](fry-liquidity-rails-clean/)** - Active mainnet deployment
- **[Interactive Demo](https://aidanduffy68-prog.github.io/USD_FRY/)** - Live demo
- **[User Acquisition Strategy](fry-liquidity-rails-clean/docs/user-acquisition-strategy.md)** - Growth plan
- **[zkLighter Integration Concept](fry-liquidity-rails-clean/docs/lighter-integration-concept.md)** - Future integration

**Archive:**
- **[Old Visualizations](archive/old_visualizations/)** - Historical charts and diagrams
- **[Core System](core/)** - Legacy Python implementation

## 🏗️ Architecture

```
Trading Loss → Chainlink Price Verification → FRY Minting (2.26x) → Tradeable Token
```

### Core Components

1. **WreckageProcessorWithOracle** - Processes losses with Chainlink-verified prices
2. **FRYPredictionMarket** - Auto-resolving prediction markets
3. **USD_FRY Token** - ERC20 token minted from processed wreckage

### Prediction Markets
- Create markets about crypto prices, events, etc.
- Bet with USDC
- Auto-resolve using Chainlink oracles
- Losers receive FRY tokens (2.26x their loss)
- Winners receive 70% of losing pool

## 🎮 Use Cases

**For Traders Who Lost Money:**
- Process your Oct 10 losses into FRY tokens
- Get 2.26x rate on verified losses
- Join community of 1.6M affected traders

**For Prediction Market Users:**
- Bet on crypto price movements
- Auto-resolution via Chainlink (no disputes)
- Even if you lose, get FRY tokens

**For DeFi Builders:**
- Integrate FRY as liquidation insurance
- Use Chainlink-verified wreckage processing
- Build on decentralized liquidity infrastructure

## 📊 Project Structure

```
fry-liquidity-rails-clean/          # Active mainnet deployment
├── liquidity-rails/
│   └── core/
│       ├── contracts/              # Solidity contracts
│       │   ├── USDFRYToken.sol
│       │   ├── WreckageProcessorWithOracle.sol
│       │   └── FRYPredictionMarket.sol
│       └── engines/                # Python engines (legacy)
├── docs/
│   ├── interactive-demo.html       # Live demo
│   ├── deployment-mainnet.json     # Mainnet addresses
│   ├── user-acquisition-strategy.md
│   └── lighter-integration-concept.md
└── marketing/

core/                               # Legacy Python implementation
archive/                            # Old visualizations and files
```

## ✅ Status

**Network**: Arbitrum Mainnet  
**Launched**: October 11, 2025  
**Contracts**: Live and deployed  
**Demo**: [https://aidanduffy68-prog.github.io/USD_FRY/](https://aidanduffy68-prog.github.io/USD_FRY/)

### Next Steps
- [ ] Verify contracts on Arbiscan
- [ ] User acquisition campaign (1.6M affected traders)
- [ ] Integration with zkLighter
- [ ] Build community (Discord/Telegram)

## 🔗 Links

- **[Live Demo](https://aidanduffy68-prog.github.io/USD_FRY/)** - Try it now
- **[Arbiscan](https://arbiscan.io/address/0x492397d5912C016F49768fBc942d894687c5fe33)** - View contracts
- **[GitHub](https://github.com/aidanduffy68-prog/USD_FRY)** - Source code

---

Built for traders who lose money. Because centralized systems fail. 🍟
