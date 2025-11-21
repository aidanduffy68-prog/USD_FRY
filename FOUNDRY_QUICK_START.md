# Foundry Quick Start Guide

**Installed:** Foundry 1.4.4-stable  
**Date:** 2025-11-21

---

## Quick Commands

### Initialize New Project
```bash
forge init my-project
cd my-project
```

### Build Contracts
```bash
forge build
```

### Run Tests
```bash
forge test
```

### Start Local Node
```bash
anvil
```

### Deploy Contract
```bash
forge create ContractName --rpc-url http://localhost:8545 --private-key YOUR_PRIVATE_KEY
```

### Interact with Contract (Cast)
```bash
cast send CONTRACT_ADDRESS "functionName()" --rpc-url http://localhost:8545 --private-key YOUR_PRIVATE_KEY
```

---

## Common Workflows

### 1. Create New Foundry Project
```bash
forge init my-contract
cd my-contract
forge build
forge test
```

### 2. Test Locally
```bash
# Terminal 1: Start local node
anvil

# Terminal 2: Deploy and test
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
```

### 3. Deploy to Testnet
```bash
forge create ContractName \
  --rpc-url https://sepolia.infura.io/v3/YOUR_KEY \
  --private-key YOUR_PRIVATE_KEY \
  --etherscan-api-key YOUR_ETHERSCAN_KEY \
  --verify
```

---

## Foundry Tools

**Forge:** Testing and deployment framework
- `forge build` - Compile contracts
- `forge test` - Run tests
- `forge script` - Run deployment scripts
- `forge create` - Deploy contracts

**Cast:** CLI for contract interaction
- `cast send` - Send transactions
- `cast call` - Call view functions
- `cast abi-encode` - Encode function calls

**Anvil:** Local Ethereum node
- `anvil` - Start local node (default: http://localhost:8545)
- `anvil --fork-url URL` - Fork mainnet/testnet

**Chisel:** Solidity REPL
- `chisel` - Interactive Solidity console

---

## Documentation

- **Foundry Book:** https://book.getfoundry.sh/
- **GitHub:** https://github.com/foundry-rs/foundry
- **Chat:** https://t.me/foundry_rs/

---

**Status:** Foundry installed and ready to use!

