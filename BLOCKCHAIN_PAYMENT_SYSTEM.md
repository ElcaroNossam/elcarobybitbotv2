# 🏦 TRC Sovereign Monetary System - Multi-Network Payments

> Complete blockchain payment system for ElCaro Trading Platform

## 📊 System Overview

**Status:** ✅ Fully Tested & Operational  
**Tests:** 40/40 Passed (0.19s)  
**API Endpoints:** 29 routes  
**Networks:** 10 crypto networks supported

## 🌐 Supported Crypto Networks

| Network | Token | Deposit Fee | Withdrawal Fee | Min Withdrawal | Avg Time |
|---------|-------|-------------|----------------|----------------|----------|
| **TRC20** | USDT | $0 | $1.00 | $10 | 3 min |
| **BEP20** | USDT | $0 | $0.50 | $10 | 2 min |
| **ERC20** | USDT | $0 | $5.00 | $50 | 5 min |
| **Polygon** | USDT | $0 | $0.10 | $5 | 4 min |
| **Arbitrum** | USDT | $0 | $0.30 | $5 | 3 min |
| **Optimism** | USDT | $0 | $0.30 | $5 | 3 min |
| **Base** | USDC | $0 | $0.20 | $5 | 3 min |
| **Solana** | USDT | $0 | $0.10 | $5 | 1 min |
| **Avalanche** | USDT | $0 | $0.50 | $10 | 2 min |
| **TON** | USDT | $0 | $0.10 | $5 | 1 min |

## 💰 License Pricing (TRC = USDT)

### Premium License
| Duration | Price | Discount |
|----------|-------|----------|
| 1 month | 100 TRC | - |
| 3 months | 270 TRC | 10% |
| 6 months | 480 TRC | 20% |
| 12 months | 840 TRC | 30% |

### Basic License
| Duration | Price | Discount |
|----------|-------|----------|
| 1 month | 50 TRC | - |
| 3 months | 135 TRC | 10% |
| 6 months | 240 TRC | 20% |
| 12 months | 420 TRC | 30% |

## 🔗 API Endpoints

### Public Endpoints
```
GET  /api/blockchain/stats              - Global blockchain stats
GET  /api/blockchain/networks           - All supported networks
GET  /api/blockchain/networks/fees      - Withdrawal fees by network
GET  /api/blockchain/networks/status    - Network status
GET  /api/blockchain/networks/{id}      - Specific network config
GET  /api/blockchain/prices/license     - License prices
GET  /api/blockchain/fees               - All fees summary
```

### User Wallet Endpoints
```
GET  /api/blockchain/wallet/{user_id}                        - Wallet info
GET  /api/blockchain/wallet/{user_id}/balance                - Balance
GET  /api/blockchain/wallet/{user_id}/deposit-address/{net}  - Deposit address
POST /api/blockchain/deposit                                  - Deposit TRC
POST /api/blockchain/withdraw                                 - Withdraw to external
POST /api/blockchain/pay                                      - Payment
POST /api/blockchain/pay/license                              - Pay for license
POST /api/blockchain/reward                                   - Send reward
```

### Admin/Sovereign Endpoints
```
GET  /api/blockchain/admin/dashboard/{admin_id}  - Full dashboard
GET  /api/blockchain/admin/treasury/{admin_id}   - Treasury stats
GET  /api/blockchain/admin/networks/status       - Network status
POST /api/blockchain/admin/emit                  - Emit tokens
POST /api/blockchain/admin/burn                  - Burn tokens
POST /api/blockchain/admin/policy                - Set monetary policy
POST /api/blockchain/admin/freeze                - Freeze wallet
POST /api/blockchain/admin/unfreeze              - Unfreeze wallet
POST /api/blockchain/admin/distribute-rewards    - Distribute staking rewards
POST /api/blockchain/admin/treasury-transfer     - Treasury transfer
```

### Utility Endpoints
```
GET  /api/blockchain/convert/usdt-to-trc  - Convert USDT to TRC
GET  /api/blockchain/convert/trc-to-usdt  - Convert TRC to USDT
GET  /api/blockchain/is-sovereign/{uid}   - Check sovereign status
```

## 📱 WebApp Pages

### User Wallet Page
**URL:** `/wallet`

Features:
- Balance display (TRC & USDT)
- Deposit modal with network selection
- Withdrawal modal with fee preview
- Subscription plans
- Transaction history

### Blockchain Admin Page
**URL:** `/blockchain-admin`

Features:
- Treasury overview
- Token emission/burn controls
- Monetary policy settings
- Wallet freeze/unfreeze
- Treasury transfers
- Network status monitoring
- Activity log

## 🔐 Security Features

### Sovereign Owner Powers
- Mint new tokens (up to max supply)
- Burn tokens from supply
- Set monetary policy (APY, fees, reserve ratio)
- Freeze/unfreeze wallets
- Treasury transfers
- Emergency system pause

### Wallet Security
- Unique TRC addresses per user
- Memo system for deposits (U{user_id})
- Minimum withdrawal amounts
- Transaction hash verification
- Status tracking (active/frozen)

## 📈 Blockchain Stats

- **Chain Name:** Triacelo Chain
- **Token:** TRC (Triacelo Coin)
- **Chain ID:** 8888
- **Initial Supply:** 100,000,000 TRC
- **Max Supply:** 1,000,000,000,000 TRC
- **Reserve Ratio:** 1.1 (110% backed)
- **Staking APY:** 12%

### Reserve Backing
| Asset | Allocation |
|-------|------------|
| USD Cash | 30% |
| US T-Bills | 40% |
| BTC | 15% |
| Gold | 10% |
| ETH | 5% |

## 🧪 Testing

Run all tests:
```bash
python3 -m pytest tests/test_payment_integration.py -v
```

Test output:
```
40 passed in 0.19s
```

### Test Categories
- TestBlockchainConfig (4 tests)
- TestCurrencyConversion (2 tests)
- TestWalletOperations (4 tests)
- TestPaymentOperations (4 tests)
- TestRewardOperations (1 test)
- TestSovereignOperations (12 tests)
- TestGlobalStats (1 test)
- TestLicensePricing (2 tests)
- TestTransactionTypes (1 test)
- TestEdgeCases (2 tests)
- TestNetworkOperations (7 tests)

## 🚀 Deployment

The system is part of the main ElCaro bot deployment:

```bash
# SSH to AWS
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com

# Update and restart
cd /home/ubuntu/project/elcarobybitbotv2
git pull origin main
sudo systemctl restart elcaro-bot

# Check logs
journalctl -u elcaro-bot -f --no-pager
```

## 📝 Files

| File | Purpose |
|------|---------|
| `core/blockchain.py` | TRC blockchain implementation (2000+ lines) |
| `core/__init__.py` | Exports (45+ blockchain functions) |
| `webapp/api/blockchain.py` | REST API (495 lines, 29 endpoints) |
| `webapp/templates/wallet.html` | User wallet page |
| `webapp/templates/blockchain_admin.html` | Admin panel |
| `tests/test_payment_integration.py` | 40 integration tests |

---

*Last Updated: January 2026*  
*Version: 2.3.0*  
*Author: ElCaro Team*
