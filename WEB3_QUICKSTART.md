# 🚀 ElCaro Web3 - Quick Start Guide

## ✅ Что было сделано

### 1. **Полная Web3 инфраструктура**
- ✅ Универсальный Web3 клиент (Polygon, BSC, Ethereum, Base, Arbitrum)
- ✅ Поддержка testnet и mainnet сетей
- ✅ Connection pooling и кэширование

### 2. **ELCARO Token (ERC-20)**
- ✅ Смарт-контракт: `ElcaroToken.sol`
- ✅ Python адаптер: `blockchain/token_contract.py`
- ✅ Функции: mint, burn, pause, transfer
- ✅ Максимальный supply: 1 млрд токенов

### 3. **Strategy NFT (ERC-721)**
- ✅ Смарт-контракт: `StrategyNFT.sol`
- ✅ Python адаптер: `blockchain/nft_contract.py`
- ✅ Каждая стратегия = уникальный NFT
- ✅ Metadata on-chain + IPFS

### 4. **Decentralized Marketplace**
- ✅ Смарт-контракт: `StrategyMarketplace.sol`
- ✅ Python адаптер: `blockchain/marketplace_contract.py`
- ✅ Покупка/продажа стратегий за ELCARO
- ✅ Роялти для авторов (5-10%)
- ✅ Комиссия платформы (2.5%)

### 5. **Wallet Integration**
- ✅ MetaMask, WalletConnect поддержка
- ✅ Подпись сообщений для верификации
- ✅ Browser-side wallet.js
- ✅ Signature verification в Python

### 6. **Database Integration**
- ✅ Web3-специфичные таблицы
- ✅ Сохранение стратегий пользователей
- ✅ NFT ownership tracking
- ✅ Blockchain transactions log
- ✅ Marketplace listings

### 7. **FastAPI Endpoints**
- ✅ `/api/web3/wallet/*` - управление кошельками
- ✅ `/api/web3/strategies/*` - сохранение/загрузка стратегий
- ✅ `/api/web3/marketplace/*` - маркетплейс
- ✅ `/api/web3/subscription/*` - подписки за токены
- ✅ `/api/web3/transactions` - история транзакций
- ✅ `/api/web3/token/info` - информация о токене

### 8. **Smart Contract Deployment**
- ✅ Hardhat конфигурация
- ✅ Деплой скрипт для всех сетей
- ✅ Автоматическая верификация контрактов
- ✅ Обновление адресов в Python файлах

---

## 📦 Установка

### 1. Python Dependencies
```bash
pip install web3 eth-account eth-utils aiohttp python-dotenv
```

### 2. Smart Contract Tools
```bash
cd blockchain/contracts
npm install
```

### 3. Initialize Database
```python
python -c "from blockchain.db_integration import init_web3_tables; init_web3_tables()"
```

---

## 🎯 Основные фичи

### Для пользователей:

#### 1. **Сохранение стратегий**
```
Backtest → Save Strategy → Имя и описание → Сохранить
```
Стратегия сохраняется в БД, доступна в боте и webapp.

#### 2. **Mint NFT из стратегии**
```
My Strategies → Choose Strategy → Mint NFT → Approve TX → NFT готов
```
Стратегия становится NFT на блокчейне.

#### 3. **Продажа на маркетплейсе**
```
My NFTs → List for Sale → Цена в ELCARO → Royalty % → Publish
```
NFT выставлен на продажу, другие могут купить.

#### 4. **Покупка стратегий**
```
Marketplace → Browse → Buy → Approve ELCARO → Confirm → Strategy + NFT ваши
```
Автоматически: оплата продавцу, роялти автору, комиссия платформе.

#### 5. **Подписка через токены**
```
Premium Plan → Pay with ELCARO → Approve tokens → Confirm → Подписка активна
```
Все подписки можно оплачивать токенами вместо TON/Stars.

### Для разработчиков:

#### Deploy контрактов (Testnet)
```bash
cd blockchain/contracts
npm run deploy:mumbai
```

#### Deploy контрактов (Mainnet)
```bash
# ⚠️ Проверьте приватный ключ!
npm run deploy:polygon
```

#### Verify контрактов
```bash
npm run verify:mumbai  # Testnet
npm run verify:polygon  # Mainnet
```

---

## 🔗 API Примеры

### 1. Connect Wallet
```bash
POST /api/web3/wallet/connect
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "network": "polygon"
}

# Response: message to sign
```

### 2. Verify Wallet
```bash
POST /api/web3/wallet/verify
{
  "wallet_address": "0x742d35Cc...",
  "signature": "0xabcd1234...",
  "message": "Welcome to ElCaro..."
}

# Response: {success: true, verified: true}
```

### 3. Save Strategy
```bash
POST /api/web3/strategies/save
{
  "name": "My Awesome Strategy",
  "description": "RSI + BB with custom params",
  "base_strategy": "rsibboi",
  "config": {
    "indicators": {
      "rsi": {"period": 14, "overbought": 70, "oversold": 30},
      "bb": {"period": 20, "std_dev": 2.0}
    },
    "risk_management": {
      "stop_loss": 3.0,
      "take_profit": 8.0
    }
  }
}

# Response: {success: true, strategy_id: 42}
```

### 4. Mint NFT
```bash
POST /api/web3/strategies/mint-nft
{
  "strategy_id": 42,
  "price_elcaro": 100
}

# Response: {tx_hash: "0x...", nft_id: 123}
```

### 5. List on Marketplace
```bash
POST /api/web3/marketplace/list
{
  "token_id": 123,
  "price_elcaro": 150,
  "royalty_percent": 7.5
}

# Response: {tx_hash: "0x...", listing_id: 1}
```

### 6. Get User's Strategies
```bash
GET /api/web3/strategies/my

# Response:
{
  "strategies": [
    {
      "id": 42,
      "name": "My Awesome Strategy",
      "win_rate": 72.5,
      "total_pnl": 18.3,
      "total_trades": 150
    }
  ]
}
```

---

## 🎮 Использование в боте

### Команды (будущее расширение):

```
/wallet - Подключить кошелёк
/mystrategy - Мои сохранённые стратегии
/mintnft - Mint NFT из стратегии
/marketplace - Открыть маркетплейс
/buywithtoken - Купить подписку за ELCARO
```

### Интеграция с существующими командами:

```python
# В bot.py добавить:
from blockchain.db_integration import save_user_strategy, get_user_strategies

@log_calls
@require_access
async def cmd_save_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Сохранить текущие настройки как стратегию"""
    uid = update.effective_user.id
    t = ctx.t
    
    # Get current settings
    config = get_user_config(uid)
    
    # Save as strategy
    strategy_id = save_user_strategy(
        user_id=uid,
        name=f"Strategy {datetime.now().strftime('%Y%m%d_%H%M')}",
        config=config,
        description="Auto-saved strategy",
        base_strategy="elcaro"
    )
    
    await update.message.reply_text(
        f"✅ Стратегия сохранена!\n"
        f"ID: {strategy_id}\n\n"
        f"Вы можете превратить её в NFT в WebApp."
    )

# Register handler
app.add_handler(CommandHandler("savestrategy", cmd_save_strategy))
```

---

## 📊 Database Schema

### Новые таблицы:

**strategy_nfts** - NFT информация
```sql
- id, strategy_id, token_id
- contract_address, network
- owner_address, creator_address
- mint_tx_hash, minted_at
```

**blockchain_transactions** - история транзакций
```sql
- user_id, tx_hash, network
- tx_type, status, from_address, to_address
- amount, token_symbol
- created_at, confirmed_at
```

**blockchain_listings** - маркетплейс листинги
```sql
- strategy_id, nft_token_id, listing_id
- seller_address, price_elcaro
- status, listed_at, sold_at
```

**blockchain_subscriptions** - подписки за токены
```sql
- user_id, wallet_address, plan
- price_elcaro, tx_hash
- expires_at, confirmed_at
```

---

## 🌍 Поддерживаемые сети

| Network | Chain ID | RPC | Explorer | Status |
|---------|----------|-----|----------|--------|
| Polygon Mumbai | 80001 | https://rpc-mumbai.maticvigil.com | https://mumbai.polygonscan.com | ✅ Testnet |
| Polygon Mainnet | 137 | https://polygon-rpc.com | https://polygonscan.com | ⏳ Ready |
| BSC Testnet | 97 | https://data-seed-prebsc-1-s1.binance.org:8545 | https://testnet.bscscan.com | ✅ Testnet |
| BSC Mainnet | 56 | https://bsc-dataseed.binance.org | https://bscscan.com | ⏳ Ready |
| Ethereum Mainnet | 1 | https://eth.llamarpc.com | https://etherscan.io | 🔮 Future |
| Base | 8453 | https://mainnet.base.org | https://basescan.org | 🔮 Future |
| Arbitrum | 42161 | https://arb1.arbitrum.io/rpc | https://arbiscan.io | 🔮 Future |

---

## 💰 Tokenomics

### Цены на подписки (в ELCARO):
```
Basic:
- 1 месяц: 50 ELCARO ($50)
- 3 месяца: 135 ELCARO ($135)
- 6 месяцев: 240 ELCARO ($240)
- 12 месяцев: 420 ELCARO ($420)

Premium:
- 1 месяц: 100 ELCARO ($100)
- 3 месяца: 270 ELCARO ($270)
- 6 месяцев: 480 ELCARO ($480)
- 12 месяцев: 840 ELCARO ($840)
```

### Комиссии:
- **Marketplace fee**: 2.5% от каждой продажи
- **Creator royalty**: 5-10% (задаётся продавцом)
- **Gas fees**: оплачивает пользователь

---

## 🔐 Security Checklist

- [x] OpenZeppelin контракты (проверенные)
- [x] ReentrancyGuard защита
- [x] Pausable функционал
- [x] Access control (Ownable)
- [ ] External audit (планируется)
- [ ] Bug bounty program (планируется)

---

## 📞 Support

**Проблемы?** Свяжитесь с нами:
- GitHub Issues: github.com/elcaro/issues
- Telegram: @elcaro_support
- Email: support@elcaro.com

---

## 🎉 Итого

### Полная Web3 платформа:
✅ Собственный токен (ELCARO)
✅ NFT для стратегий
✅ Децентрализованный маркетплейс
✅ Wallet интеграция
✅ On-chain payments
✅ Creator royalties
✅ Multiple networks support
✅ Comprehensive API
✅ Smart contracts deployed
✅ Full documentation

**ElCaro теперь полноценная Web3 торговая платформа!** 🚀

---

*Created: December 23, 2025*
*Version: 1.0.0*
*License: MIT*
