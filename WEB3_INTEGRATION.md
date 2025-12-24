# 🌐 ElCaro Web3 Blockchain Integration

## 📚 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Smart Contracts](#smart-contracts)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [User Guide](#user-guide)
- [Development](#development)
- [Deployment](#deployment)

---

## 🎯 Overview

ElCaro Web3 интеграция превращает платформу в полноценное Web3 приложение с собственным блокчейном токеном, NFT для стратегий и децентрализованным маркетплейсом.

### Ключевые возможности:
- **ELCARO Token (ERC-20)** - собственная монета платформы
- **Strategy NFT (ERC-721)** - стратегии как NFT
- **Decentralized Marketplace** - покупка/продажа стратегий
- **Wallet Integration** - MetaMask, WalletConnect
- **On-chain Payments** - все платежи через токен
- **Creator Royalties** - авторы получают роялти с продаж

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   ElCaro Platform                    │
├─────────────────────────────────────────────────────┤
│  Telegram Bot  │   FastAPI WebApp   │  React UI     │
├─────────────────────────────────────────────────────┤
│                 Python Backend                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Web3 Integration Layer                      │  │
│  │  - Web3Client (web3.py)                      │  │
│  │  - Token/NFT Adapters                        │  │
│  │  - Database Integration                      │  │
│  └──────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│              Blockchain Networks                    │
│  ┌──────────────┬──────────────┬──────────────┐   │
│  │  Polygon     │  BSC         │  Ethereum    │   │
│  └──────────────┴──────────────┴──────────────┘   │
├─────────────────────────────────────────────────────┤
│              Smart Contracts                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  ElcaroToken.sol       (ERC-20)              │  │
│  │  StrategyNFT.sol       (ERC-721)             │  │
│  │  StrategyMarketplace.sol (Marketplace)       │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 1. **ELCARO Token (ERC-20)**
- **Symbol**: ELCARO
- **Decimals**: 18
- **Initial Supply**: 100,000,000
- **Max Supply**: 1,000,000,000
- **Use Cases**:
  - Покупка подписок
  - Покупка стратегий на маркетплейсе
  - Стейкинг (будущее)
  - Governance (будущее)

### 2. **Strategy NFTs**
- Каждая стратегия = уникальный NFT
- Metadata on-chain + IPFS
- Transferable & Tradable
- Performance tracking
- Creator attribution

### 3. **Decentralized Marketplace**
- List strategies for sale
- Buy with ELCARO tokens
- Creator royalties (5-10%)
- Platform fee (2.5%)
- On-chain ownership proof

### 4. **Wallet Integration**
- MetaMask
- WalletConnect
- Trust Wallet
- Coinbase Wallet
- Browser-based signing

### 5. **User Strategy Management**
- Save custom strategies
- Mint as NFT
- Share on marketplace
- Track performance
- Automatic royalties

---

## 📜 Smart Contracts

### ElcaroToken.sol (ERC-20)
```solidity
// Main platform token
contract ElcaroToken is ERC20, ERC20Burnable, Ownable, Pausable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;
    
    function mint(address to, uint256 amount) public onlyOwner;
    function burn(uint256 amount) public;
    function pause() public onlyOwner;
}
```

**Features**:
- Mintable (owner only)
- Burnable (anyone can burn their tokens)
- Pausable (emergency stop)
- Account-specific pause

**Deployed At**:
- Polygon Mumbai (Testnet): `0x...` (TBD)
- Polygon Mainnet: `0x...` (TBD)
- BSC Testnet: `0x...` (TBD)
- BSC Mainnet: `0x...` (TBD)

### StrategyNFT.sol (ERC-721)
```solidity
// Strategy NFTs with metadata
contract StrategyNFT is ERC721, ERC721URIStorage, ERC721Burnable {
    struct StrategyData {
        uint256 strategyId;
        address creator;
        uint256 price;
        uint256 totalOwners;
    }
    
    function mint(address to, uint256 strategyId, string memory metadata);
    function updatePerformance(uint256 tokenId, string memory performance);
    function tokensOfOwner(address owner) returns (uint256[] memory);
}
```

**Features**:
- Unique strategy representation
- On-chain metadata
- Performance updates
- Owner tracking

**Deployed At**:
- Polygon Mumbai: `0x...` (TBD)
- Polygon Mainnet: `0x...` (TBD)

### StrategyMarketplace.sol
```solidity
// Marketplace for strategy NFTs
contract StrategyMarketplace is ReentrancyGuard, Ownable {
    struct Listing {
        address seller;
        uint256 tokenId;
        uint256 price;
        uint256 royaltyPercent;
        bool isActive;
    }
    
    function listStrategy(uint256 tokenId, uint256 price, uint256 royalty);
    function buyStrategy(uint256 listingId);
    function purchaseSubscription(string memory plan, uint256 months);
}
```

**Features**:
- Strategy listings
- Secure escrow
- Automatic royalties
- Subscription payments
- Platform fee collection

**Deployed At**:
- Polygon Mumbai: `0x...` (TBD)
- Polygon Mainnet: `0x...` (TBD)

---

## 🚀 Installation

### 1. Install Python Dependencies
```bash
cd /home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo

# Install Web3.py and dependencies
pip install web3 eth-account eth-utils python-dotenv aiohttp
```

### 2. Install Smart Contract Tools
```bash
cd blockchain/contracts

# Install Node.js dependencies
npm install

# Or with yarn
yarn install
```

### 3. Configure Environment
```bash
# Create .env file
cat > blockchain/contracts/.env << EOF
DEPLOYER_PRIVATE_KEY=your_private_key_here
POLYGONSCAN_API_KEY=your_polygonscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key
EOF
```

### 4. Initialize Database Tables
```python
from blockchain.db_integration import init_web3_tables
init_web3_tables()
```

---

## 🎮 Quick Start

### For Users:

#### 1. Connect Wallet
```javascript
// In WebApp
await connectWallet();
// MetaMask popup appears
// User approves connection
```

#### 2. Save Strategy
```python
# Create strategy in backtest interface
# Click "Save Strategy"
# Strategy saved to database
```

#### 3. Mint as NFT
```javascript
// Click "Mint NFT"
// Approve transaction in wallet
// NFT minted on blockchain
```

#### 4. List on Marketplace
```javascript
// Click "List for Sale"
// Set price in ELCARO
// Set creator royalty (5-10%)
// Approve NFT transfer
// Listed on marketplace
```

#### 5. Buy Strategy
```javascript
// Browse marketplace
// Click "Buy Strategy"
// Approve ELCARO token spend
// Confirm purchase
// NFT transferred + strategy access granted
```

### For Developers:

#### 1. Deploy Contracts (Testnet)
```bash
cd blockchain/contracts

# Deploy to Polygon Mumbai
npm run deploy:mumbai

# Deploy to BSC Testnet
npm run deploy:bsc-testnet
```

#### 2. Verify Contracts
```bash
# Verify on PolygonScan
npm run verify:mumbai

# Verify on BscScan
npm run verify:bsc-testnet
```

#### 3. Test Integration
```python
from blockchain import Web3Client, NetworkType, ElcaroToken

# Create client
client = Web3Client(network=NetworkType.POLYGON_MUMBAI)

# Get token contract
token = ElcaroToken(client)

# Check balance
balance = await token.balance_of("0x...")
print(f"Balance: {balance} ELCARO")
```

---

## 📖 API Reference

### Base URL
```
https://elcaro.com/api/web3
```

### Authentication
```http
Authorization: Bearer <jwt_token>
```

### Endpoints

#### 1. Wallet Management

**POST /wallet/connect**
```json
{
  "wallet_address": "0x...",
  "network": "polygon"
}
```
Response:
```json
{
  "success": true,
  "message": "Welcome to ElCaro...",
  "nonce": "abc123..."
}
```

**POST /wallet/verify**
```json
{
  "wallet_address": "0x...",
  "signature": "0x...",
  "message": "Welcome to ElCaro..."
}
```
Response:
```json
{
  "success": true,
  "wallet_address": "0x...",
  "verified": true
}
```

**GET /wallet/info**
```json
{
  "connected": true,
  "wallet_address": "0x...",
  "network": "polygon",
  "elcaro_balance": 1250.5,
  "balance_updated_at": 1703001234
}
```

**POST /wallet/refresh-balance**
```json
{
  "success": true,
  "balance": 1250.5,
  "updated_at": 1703001234
}
```

#### 2. Strategy Management

**POST /strategies/save**
```json
{
  "name": "My RSI Strategy",
  "description": "RSI + BB + Volume",
  "base_strategy": "rsibboi",
  "config": {
    "indicators": {...},
    "risk_management": {...}
  }
}
```
Response:
```json
{
  "success": true,
  "strategy_id": 42,
  "message": "Strategy saved successfully"
}
```

**GET /strategies/my**
```json
{
  "success": true,
  "strategies": [
    {
      "id": 42,
      "name": "My RSI Strategy",
      "win_rate": 68.5,
      "total_pnl": 15.3,
      "is_public": false
    }
  ],
  "count": 1
}
```

**GET /strategies/{strategy_id}**
```json
{
  "success": true,
  "strategy": {
    "id": 42,
    "name": "My RSI Strategy",
    "config": {...},
    "performance": {...}
  }
}
```

**POST /strategies/mint-nft**
```json
{
  "strategy_id": 42,
  "price_elcaro": 100
}
```
Response:
```json
{
  "success": true,
  "tx_hash": "0x...",
  "nft_id": 123,
  "explorer_url": "https://polygonscan.com/tx/0x..."
}
```

**GET /strategies/my-nfts**
```json
{
  "success": true,
  "nfts": [
    {
      "token_id": 123,
      "strategy_id": 42,
      "name": "My RSI Strategy",
      "contract_address": "0x...",
      "network": "polygon"
    }
  ],
  "count": 1
}
```

#### 3. Marketplace

**POST /marketplace/list**
```json
{
  "token_id": 123,
  "price_elcaro": 100,
  "royalty_percent": 5.0
}
```
Response:
```json
{
  "success": true,
  "tx_hash": "0x...",
  "explorer_url": "https://polygonscan.com/tx/0x..."
}
```

**GET /marketplace/listings**
```json
{
  "success": true,
  "listings": [
    {
      "listing_id": 1,
      "token_id": 123,
      "price": 100,
      "seller": "0x..."
    }
  ]
}
```

#### 4. Subscriptions

**POST /subscription/purchase**
```json
{
  "plan": "premium",
  "months": 3
}
```
Response:
```json
{
  "success": true,
  "tx_hash": "0x...",
  "price_elcaro": 270,
  "plan": "premium",
  "months": 3,
  "explorer_url": "https://polygonscan.com/tx/0x..."
}
```

#### 5. Transactions

**GET /transactions?limit=50**
```json
{
  "success": true,
  "transactions": [
    {
      "tx_hash": "0x...",
      "network": "polygon",
      "tx_type": "strategy_purchase",
      "amount": 100,
      "token_symbol": "ELCARO",
      "status": "confirmed",
      "created_at": 1703001234
    }
  ],
  "count": 15
}
```

#### 6. Token Info

**GET /token/info**
```json
{
  "success": true,
  "name": "ElCaro Token",
  "symbol": "ELCARO",
  "decimals": 18,
  "total_supply": 100000000,
  "contract_address": "0x...",
  "price_usd": 1.0,
  "network": "Polygon",
  "explorer_url": "https://polygonscan.com/address/0x..."
}
```

---

## 👨‍💻 Development

### Project Structure
```
blockchain/
├── __init__.py                 # Module exports
├── web3_client.py             # Universal Web3 client
├── token_contract.py          # ELCARO Token adapter
├── nft_contract.py            # Strategy NFT adapter
├── marketplace_contract.py    # Marketplace adapter
├── wallet_integration.py      # Wallet auth & signing
├── db_integration.py          # Database functions
├── contracts/                 # Smart contracts
│   ├── ElcaroToken.sol
│   ├── StrategyNFT.sol
│   ├── StrategyMarketplace.sol
│   ├── hardhat.config.js
│   ├── package.json
│   └── scripts/
│       └── deploy.js
└── deployments/               # Contract addresses
    ├── polygon.json
    ├── mumbai.json
    └── bsc.json
```

### Testing

#### Unit Tests
```python
import pytest
from blockchain import Web3Client, NetworkType

@pytest.mark.asyncio
async def test_token_balance():
    client = Web3Client(network=NetworkType.POLYGON_MUMBAI)
    token = ElcaroToken(client)
    balance = await token.balance_of("0x...")
    assert balance >= 0
```

#### Integration Tests
```bash
# Test contract deployment
cd blockchain/contracts
npx hardhat test

# Test Python integration
pytest tests/test_web3.py -v
```

### Local Development
```bash
# Start local blockchain
cd blockchain/contracts
npx hardhat node

# Deploy to localhost
npx hardhat run scripts/deploy.js --network localhost

# Run webapp with Web3
JWT_SECRET=test python -m uvicorn webapp.app:app --port 8765
```

---

## 🚀 Deployment

### 1. Deploy to Polygon Mumbai (Testnet)
```bash
cd blockchain/contracts

# Set environment variables
export DEPLOYER_PRIVATE_KEY="your_private_key"
export POLYGONSCAN_API_KEY="your_api_key"

# Deploy
npm run deploy:mumbai

# Verify
npm run verify:mumbai
```

### 2. Deploy to Polygon Mainnet
```bash
# ⚠️ MAINNET - Use secure private key management!
npm run deploy:polygon
npm run verify:polygon
```

### 3. Update Configuration
```python
# Update contract addresses in Python files
# blockchain/token_contract.py
CONTRACT_ADDRESSES = {
    'polygon': '0xYOUR_TOKEN_ADDRESS_HERE',
    ...
}

# blockchain/nft_contract.py
CONTRACT_ADDRESSES = {
    'polygon': '0xYOUR_NFT_ADDRESS_HERE',
    ...
}

# blockchain/marketplace_contract.py
CONTRACT_ADDRESSES = {
    'polygon': '0xYOUR_MARKETPLACE_ADDRESS_HERE',
    ...
}
```

### 4. Configure WebApp
```bash
# Add to .env
WEB3_ENABLED=true
DEFAULT_NETWORK=polygon
ELCARO_TOKEN_ADDRESS=0x...
STRATEGY_NFT_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
```

### 5. Test Production
```bash
# Test token transfers
python -c "from blockchain import Web3Client, NetworkType, ElcaroToken; ..."

# Test NFT minting
python -c "from blockchain import StrategyNFT; ..."

# Test marketplace
python -c "from blockchain import StrategyMarketplace; ..."
```

---

## 📊 Tokenomics

### ELCARO Token Distribution
```
Total Supply: 1,000,000,000 ELCARO

Initial Distribution:
- Team & Development: 20% (200M) - 4 year vesting
- Community Rewards: 30% (300M) - Staking, airdrops
- Liquidity Pools: 20% (200M) - DEX liquidity
- Ecosystem Fund: 15% (150M) - Partnerships, grants
- Public Sale: 10% (100M)
- Marketing: 5% (50M)
```

### Utility
- **Subscriptions**: Basic ($50) / Premium ($100) per month
- **Strategy Purchase**: Set by creator (min 10 ELCARO)
- **Marketplace Fee**: 2.5% per transaction
- **Creator Royalty**: 5-10% on resales
- **Governance**: 1 ELCARO = 1 vote (future)
- **Staking**: Earn rewards (future)

---

## 🔐 Security

### Smart Contract Security
- ✅ OpenZeppelin contracts (audited)
- ✅ ReentrancyGuard protection
- ✅ Pausable functionality
- ✅ Access control (Ownable)
- ⏳ External audit (planned)

### Best Practices
- Use hardware wallets for large amounts
- Verify contract addresses before transactions
- Double-check transaction details
- Start with testnet
- Keep private keys secure

---

## 🆘 Support

### Resources
- **Documentation**: This file
- **GitHub**: github.com/elcaro/web3
- **Discord**: discord.gg/elcaro
- **Telegram**: t.me/elcaro_support

### Common Issues

**1. Transaction Failed**
- Check gas price
- Verify token approval
- Ensure sufficient balance

**2. Wallet Connection Failed**
- Install MetaMask
- Switch to correct network
- Clear browser cache

**3. NFT Not Showing**
- Wait for confirmation (5 blocks)
- Refresh metadata
- Check block explorer

---

## 🎉 Congratulations!

Вы успешно интегрировали полноценную Web3 систему с:
- ✅ Собственным ERC-20 токеном (ELCARO)
- ✅ NFT контрактом для стратегий
- ✅ Децентрализованным маркетплейсом
- ✅ Wallet интеграцией
- ✅ On-chain платежами
- ✅ Роялти для авторов

Теперь ElCaro - полноценная Web3 платформа! 🚀
