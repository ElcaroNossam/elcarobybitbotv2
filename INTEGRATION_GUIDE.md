# ELCARO Chain Integration Guide

> **Complete guide to integrate ELCARO Chain with existing trading bot infrastructure**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Integration](#database-integration)
3. [API Endpoints](#api-endpoints)
4. [WebApp Integration](#webapp-integration)
5. [Bot Commands](#bot-commands)
6. [Deployment](#deployment)

---

## 🏗️ Architecture Overview

### Current Infrastructure
```
bot.py (~14k lines)
├── Telegram handlers
├── Bybit/HyperLiquid trading
├── Signal processing
└── User management

webapp/ (FastAPI)
├── Trading terminal
├── Backtesting
├── AI agent
└── Statistics

db.py (SQLite)
├── Users
├── Positions
├── Trades
└── Licenses
```

### New Infrastructure (ELCARO Chain)
```
blockchain/
├── chain.py (650 lines)      - L1 blockchain + PoS consensus
├── dex.py (700 lines)         - AMM + Order Book + Perpetuals
├── bridge.py (600 lines)      - Cross-chain bridge (7 networks)
├── governance.py (550 lines)  - DAO governance
└── demo.py (600 lines)        - Complete demo suite
```

### Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                     ELCARO Ecosystem                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Telegram    │  │   WebApp     │  │  Blockchain  │    │
│  │    Bot       │  │   (React)    │  │    Node      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────┬───────┴──────────────────┘            │
│                    │                                        │
│         ┌──────────▼──────────────┐                        │
│         │   API Layer (FastAPI)   │                        │
│         │  /api/blockchain/*      │                        │
│         │  /api/dex/*             │                        │
│         │  /api/bridge/*          │                        │
│         │  /api/governance/*      │                        │
│         └──────────┬──────────────┘                        │
│                    │                                        │
│         ┌──────────▼──────────────┐                        │
│         │  Services Layer         │                        │
│         │  BlockchainService      │                        │
│         │  DEXService             │                        │
│         │  BridgeService          │                        │
│         │  GovernanceService      │                        │
│         └──────────┬──────────────┘                        │
│                    │                                        │
│         ┌──────────▼──────────────┐                        │
│         │  Core Blockchain        │                        │
│         │  ElcaroChain            │                        │
│         │  ElcaroDEX              │                        │
│         │  ElcaroBridge           │                        │
│         │  ElcaroDAO              │                        │
│         └──────────┬──────────────┘                        │
│                    │                                        │
│         ┌──────────▼──────────────┐                        │
│         │  Database Layer         │                        │
│         │  SQLite (blockchain.db) │                        │
│         │  + Redis (cache)        │                        │
│         └─────────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Database Integration

### Step 1: Create Blockchain Database Schema

**File:** `db.py` (add to existing)

```python
# ============================================================================
# BLOCKCHAIN TABLES
# ============================================================================

def init_blockchain_tables(conn):
    """Initialize blockchain-related tables."""
    
    # 1. Blocks
    conn.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        block_number INTEGER PRIMARY KEY,
        block_hash TEXT UNIQUE NOT NULL,
        timestamp INTEGER NOT NULL,
        previous_hash TEXT,
        validator_address TEXT NOT NULL,
        transaction_count INTEGER DEFAULT 0,
        gas_used INTEGER DEFAULT 0,
        gas_limit INTEGER DEFAULT 0,
        state_root TEXT,
        transactions_root TEXT,
        receipts_root TEXT,
        finalized INTEGER DEFAULT 0,
        signatures_count INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(block_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_blocks_validator ON blocks(validator_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp)")
    
    # 2. Transactions
    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        tx_hash TEXT PRIMARY KEY,
        block_number INTEGER,
        tx_index INTEGER,
        from_address TEXT NOT NULL,
        to_address TEXT,
        value TEXT NOT NULL,
        gas_price TEXT NOT NULL,
        gas_limit INTEGER NOT NULL,
        gas_used INTEGER,
        nonce INTEGER NOT NULL,
        data TEXT,
        signature TEXT,
        status INTEGER DEFAULT 0,
        timestamp INTEGER NOT NULL,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        FOREIGN KEY (block_number) REFERENCES blocks(block_number)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_block ON transactions(block_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp)")
    
    # 3. Accounts
    conn.execute("""
    CREATE TABLE IF NOT EXISTS blockchain_accounts (
        address TEXT PRIMARY KEY,
        balance TEXT NOT NULL DEFAULT '0',
        nonce INTEGER DEFAULT 0,
        code TEXT,
        code_hash TEXT,
        storage TEXT,
        user_id INTEGER,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        updated_at INTEGER DEFAULT (strftime('%s', 'now')),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_user ON blockchain_accounts(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_balance ON blockchain_accounts(balance)")
    
    # 4. Validators
    conn.execute("""
    CREATE TABLE IF NOT EXISTS validators (
        address TEXT PRIMARY KEY,
        stake TEXT NOT NULL,
        delegated_stake TEXT DEFAULT '0',
        commission_rate TEXT NOT NULL,
        total_blocks_produced INTEGER DEFAULT 0,
        total_blocks_signed INTEGER DEFAULT 0,
        uptime REAL DEFAULT 1.0,
        is_active INTEGER DEFAULT 1,
        registered_at INTEGER NOT NULL,
        last_block_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_validators_stake ON validators(stake)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_validators_active ON validators(is_active)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_validators_user ON validators(user_id)")
    
    # 5. DEX Liquidity Pools
    conn.execute("""
    CREATE TABLE IF NOT EXISTS liquidity_pools (
        pool_id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        token_a TEXT NOT NULL,
        token_b TEXT NOT NULL,
        reserve_a TEXT NOT NULL,
        reserve_b TEXT NOT NULL,
        total_shares TEXT DEFAULT '0',
        fee_rate TEXT NOT NULL,
        k_constant TEXT,
        total_volume_a TEXT DEFAULT '0',
        total_volume_b TEXT DEFAULT '0',
        total_fees_a TEXT DEFAULT '0',
        total_fees_b TEXT DEFAULT '0',
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pools_symbol ON liquidity_pools(symbol)")
    
    # 6. DEX Orders
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dex_orders (
        order_id TEXT PRIMARY KEY,
        user_address TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        order_type TEXT NOT NULL,
        price TEXT,
        size TEXT NOT NULL,
        filled TEXT DEFAULT '0',
        status TEXT DEFAULT 'OPEN',
        timestamp INTEGER NOT NULL,
        filled_at INTEGER,
        cancelled_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON dex_orders(user_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol ON dex_orders(symbol)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON dex_orders(status)")
    
    # 7. Perpetual Positions
    conn.execute("""
    CREATE TABLE IF NOT EXISTS perpetual_positions (
        position_id TEXT PRIMARY KEY,
        user_address TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        size TEXT NOT NULL,
        entry_price TEXT NOT NULL,
        mark_price TEXT,
        leverage INTEGER NOT NULL,
        margin TEXT NOT NULL,
        liquidation_price TEXT NOT NULL,
        unrealized_pnl TEXT DEFAULT '0',
        realized_pnl TEXT DEFAULT '0',
        funding_paid TEXT DEFAULT '0',
        status TEXT DEFAULT 'OPEN',
        opened_at INTEGER NOT NULL,
        closed_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perp_user ON perpetual_positions(user_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perp_symbol ON perpetual_positions(symbol)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perp_status ON perpetual_positions(status)")
    
    # 8. Bridge Transfers
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bridge_transfers (
        transfer_id TEXT PRIMARY KEY,
        from_chain TEXT NOT NULL,
        to_chain TEXT NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        token TEXT NOT NULL,
        amount TEXT NOT NULL,
        fee TEXT NOT NULL,
        status TEXT NOT NULL,
        lock_tx_hash TEXT,
        mint_tx_hash TEXT,
        signatures_count INTEGER DEFAULT 0,
        required_signatures INTEGER NOT NULL,
        timelock_until INTEGER,
        created_at INTEGER NOT NULL,
        completed_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bridge_status ON bridge_transfers(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bridge_from ON bridge_transfers(from_address)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bridge_to ON bridge_transfers(to_address)")
    
    # 9. Bridge Signatures
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bridge_signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transfer_id TEXT NOT NULL,
        validator_address TEXT NOT NULL,
        signature TEXT NOT NULL,
        signed_at INTEGER NOT NULL,
        FOREIGN KEY (transfer_id) REFERENCES bridge_transfers(transfer_id),
        UNIQUE(transfer_id, validator_address)
    )
    """)
    
    # 10. DAO Proposals
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dao_proposals (
        proposal_id TEXT PRIMARY KEY,
        proposer_address TEXT NOT NULL,
        proposal_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        voting_start INTEGER NOT NULL,
        voting_end INTEGER NOT NULL,
        execution_time INTEGER,
        quorum TEXT NOT NULL,
        votes_for TEXT DEFAULT '0',
        votes_against TEXT DEFAULT '0',
        votes_abstain TEXT DEFAULT '0',
        total_votes TEXT DEFAULT '0',
        status TEXT NOT NULL,
        targets TEXT,
        values TEXT,
        calldatas TEXT,
        created_at INTEGER NOT NULL,
        executed_at INTEGER,
        cancelled_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_proposals_status ON dao_proposals(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_proposals_type ON dao_proposals(proposal_type)")
    
    # 11. DAO Votes
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dao_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposal_id TEXT NOT NULL,
        voter_address TEXT NOT NULL,
        vote_option TEXT NOT NULL,
        voting_power TEXT NOT NULL,
        reason TEXT,
        voted_at INTEGER NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (proposal_id) REFERENCES dao_proposals(proposal_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        UNIQUE(proposal_id, voter_address)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_votes_proposal ON dao_votes(proposal_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_votes_voter ON dao_votes(voter_address)")
    
    # 12. Locked Tokens (for voting)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS locked_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_address TEXT NOT NULL,
        amount TEXT NOT NULL,
        locked_at INTEGER NOT NULL,
        unlock_at INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_locked_user ON locked_tokens(user_address)")
    
    print("✅ Blockchain tables initialized")


# Call in init_db()
def init_db():
    # ... existing code ...
    
    # Add blockchain tables
    init_blockchain_tables(conn)
```

### Step 2: Add Blockchain Functions to db.py

```python
# ============================================================================
# BLOCKCHAIN FUNCTIONS
# ============================================================================

# --- Blocks ---

def add_block(block_number: int, block_hash: str, timestamp: int, validator: str, 
              tx_count: int = 0, previous_hash: str = None):
    """Add new block to database."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO blocks (block_number, block_hash, timestamp, previous_hash, 
                               validator_address, transaction_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (block_number, block_hash, timestamp, previous_hash, validator, tx_count))
        conn.commit()


def get_block(block_number: int = None, block_hash: str = None):
    """Get block by number or hash."""
    with get_conn() as conn:
        if block_number is not None:
            row = conn.execute("SELECT * FROM blocks WHERE block_number = ?", (block_number,)).fetchone()
        elif block_hash is not None:
            row = conn.execute("SELECT * FROM blocks WHERE block_hash = ?", (block_hash,)).fetchone()
        else:
            return None
        
        return dict(row) if row else None


def get_latest_block():
    """Get latest block."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM blocks ORDER BY block_number DESC LIMIT 1").fetchone()
        return dict(row) if row else None


def finalize_block(block_hash: str, signatures_count: int):
    """Mark block as finalized."""
    with get_conn() as conn:
        conn.execute("""
            UPDATE blocks SET finalized = 1, signatures_count = ? WHERE block_hash = ?
        """, (signatures_count, block_hash))
        conn.commit()


# --- Transactions ---

def add_transaction(tx_hash: str, from_addr: str, to_addr: str, value: str, 
                   gas_price: str, nonce: int, timestamp: int, block_number: int = None):
    """Add transaction to database."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO transactions (tx_hash, block_number, from_address, to_address, 
                                     value, gas_price, gas_limit, nonce, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx_hash, block_number, from_addr, to_addr, value, gas_price, 21000, nonce, timestamp))
        conn.commit()


def get_transaction(tx_hash: str):
    """Get transaction by hash."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE tx_hash = ?", (tx_hash,)).fetchone()
        return dict(row) if row else None


def get_account_transactions(address: str, limit: int = 100):
    """Get transactions for account."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM transactions 
            WHERE from_address = ? OR to_address = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (address, address, limit)).fetchall()
        return [dict(row) for row in rows]


# --- Accounts ---

def create_blockchain_account(address: str, balance: str = "0", user_id: int = None):
    """Create blockchain account."""
    with get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO blockchain_accounts (address, balance, user_id)
            VALUES (?, ?, ?)
        """, (address, balance, user_id))
        conn.commit()


def get_blockchain_account(address: str):
    """Get blockchain account."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM blockchain_accounts WHERE address = ?", (address,)).fetchone()
        return dict(row) if row else None


def update_account_balance(address: str, new_balance: str):
    """Update account balance."""
    with get_conn() as conn:
        conn.execute("""
            UPDATE blockchain_accounts 
            SET balance = ?, updated_at = strftime('%s', 'now')
            WHERE address = ?
        """, (new_balance, address))
        conn.commit()


def get_user_blockchain_account(user_id: int):
    """Get user's blockchain account."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM blockchain_accounts WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


# --- Validators ---

def add_validator(address: str, stake: str, commission_rate: str, user_id: int = None):
    """Register new validator."""
    import time
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO validators 
            (address, stake, commission_rate, registered_at, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (address, stake, commission_rate, int(time.time()), user_id))
        conn.commit()


def get_validator(address: str):
    """Get validator by address."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM validators WHERE address = ?", (address,)).fetchone()
        return dict(row) if row else None


def get_active_validators(limit: int = 100):
    """Get active validators ordered by stake."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM validators 
            WHERE is_active = 1 
            ORDER BY CAST(stake AS REAL) + CAST(delegated_stake AS REAL) DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]


def update_validator_stats(address: str, blocks_produced: int = 0, blocks_signed: int = 0):
    """Update validator statistics."""
    with get_conn() as conn:
        conn.execute("""
            UPDATE validators 
            SET total_blocks_produced = total_blocks_produced + ?,
                total_blocks_signed = total_blocks_signed + ?,
                last_block_at = strftime('%s', 'now')
            WHERE address = ?
        """, (blocks_produced, blocks_signed, address))
        conn.commit()


# --- DEX Orders ---

def add_dex_order(order_id: str, user_addr: str, symbol: str, side: str, 
                 order_type: str, price: str, size: str, timestamp: int, user_id: int = None):
    """Add DEX order."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO dex_orders (order_id, user_address, symbol, side, order_type, 
                                   price, size, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, user_addr, symbol, side, order_type, price, size, timestamp, user_id))
        conn.commit()


def get_user_dex_orders(user_addr: str, status: str = None, limit: int = 100):
    """Get user's DEX orders."""
    with get_conn() as conn:
        if status:
            rows = conn.execute("""
                SELECT * FROM dex_orders 
                WHERE user_address = ? AND status = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (user_addr, status, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM dex_orders 
                WHERE user_address = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (user_addr, limit)).fetchall()
        return [dict(row) for row in rows]


# --- Perpetual Positions ---

def add_perpetual_position(position_id: str, user_addr: str, symbol: str, side: str,
                          size: str, entry_price: str, leverage: int, margin: str,
                          liquidation_price: str, opened_at: int, user_id: int = None):
    """Add perpetual position."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO perpetual_positions 
            (position_id, user_address, symbol, side, size, entry_price, leverage,
             margin, liquidation_price, opened_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (position_id, user_addr, symbol, side, size, entry_price, leverage,
              margin, liquidation_price, opened_at, user_id))
        conn.commit()


def get_user_perpetual_positions(user_addr: str, status: str = "OPEN"):
    """Get user's perpetual positions."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM perpetual_positions 
            WHERE user_address = ? AND status = ?
            ORDER BY opened_at DESC
        """, (user_addr, status)).fetchall()
        return [dict(row) for row in rows]


# --- Bridge Transfers ---

def add_bridge_transfer(transfer_id: str, from_chain: str, to_chain: str,
                       from_addr: str, to_addr: str, token: str, amount: str,
                       fee: str, status: str, required_sigs: int, created_at: int,
                       user_id: int = None):
    """Add bridge transfer."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO bridge_transfers 
            (transfer_id, from_chain, to_chain, from_address, to_address, token,
             amount, fee, status, required_signatures, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (transfer_id, from_chain, to_chain, from_addr, to_addr, token,
              amount, fee, status, required_sigs, created_at, user_id))
        conn.commit()


def get_bridge_transfer(transfer_id: str):
    """Get bridge transfer."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM bridge_transfers WHERE transfer_id = ?", 
                          (transfer_id,)).fetchone()
        return dict(row) if row else None


def update_bridge_transfer_status(transfer_id: str, status: str, completed_at: int = None):
    """Update bridge transfer status."""
    with get_conn() as conn:
        if completed_at:
            conn.execute("""
                UPDATE bridge_transfers 
                SET status = ?, completed_at = ?
                WHERE transfer_id = ?
            """, (status, completed_at, transfer_id))
        else:
            conn.execute("""
                UPDATE bridge_transfers 
                SET status = ?
                WHERE transfer_id = ?
            """, (status, transfer_id))
        conn.commit()


# --- DAO Proposals ---

def add_dao_proposal(proposal_id: str, proposer: str, prop_type: str, title: str,
                    description: str, voting_start: int, voting_end: int, quorum: str,
                    status: str, created_at: int, user_id: int = None):
    """Add DAO proposal."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO dao_proposals 
            (proposal_id, proposer_address, proposal_type, title, description,
             voting_start, voting_end, quorum, status, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (proposal_id, proposer, prop_type, title, description, voting_start,
              voting_end, quorum, status, created_at, user_id))
        conn.commit()


def get_dao_proposal(proposal_id: str):
    """Get DAO proposal."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM dao_proposals WHERE proposal_id = ?",
                          (proposal_id,)).fetchone()
        return dict(row) if row else None


def get_active_dao_proposals():
    """Get active proposals."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM dao_proposals 
            WHERE status = 'ACTIVE'
            ORDER BY voting_end ASC
        """).fetchall()
        return [dict(row) for row in rows]


def cast_dao_vote(proposal_id: str, voter: str, option: str, voting_power: str,
                 reason: str, voted_at: int, user_id: int = None):
    """Cast DAO vote."""
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO dao_votes 
            (proposal_id, voter_address, vote_option, voting_power, reason, voted_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (proposal_id, voter, option, voting_power, reason, voted_at, user_id))
        
        # Update proposal vote counts
        conn.execute(f"""
            UPDATE dao_proposals 
            SET votes_{option.lower()} = votes_{option.lower()} + ?
            WHERE proposal_id = ?
        """, (voting_power, proposal_id))
        
        conn.commit()


# --- Statistics ---

def get_blockchain_stats():
    """Get comprehensive blockchain statistics."""
    with get_conn() as conn:
        # Blocks
        blocks_row = conn.execute("""
            SELECT COUNT(*) as total, MAX(block_number) as latest
            FROM blocks
        """).fetchone()
        
        # Transactions
        txs_row = conn.execute("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN timestamp > strftime('%s', 'now') - 86400 THEN 1 END) as last_24h
            FROM transactions
        """).fetchone()
        
        # Accounts
        accounts_count = conn.execute("SELECT COUNT(*) FROM blockchain_accounts").fetchone()[0]
        
        # Validators
        validators_count = conn.execute("SELECT COUNT(*) FROM validators WHERE is_active = 1").fetchone()[0]
        
        # DEX
        dex_volume = conn.execute("""
            SELECT SUM(CAST(filled AS REAL) * CAST(price AS REAL)) as volume
            FROM dex_orders WHERE status = 'FILLED'
        """).fetchone()[0] or 0
        
        # Bridge
        bridge_row = conn.execute("""
            SELECT COUNT(*) as total, SUM(CAST(amount AS REAL)) as volume
            FROM bridge_transfers WHERE status = 'COMPLETED'
        """).fetchone()
        
        # DAO
        dao_row = conn.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active
            FROM dao_proposals
        """).fetchone()
        
        return {
            "blocks": {
                "total": blocks_row[0] or 0,
                "latest": blocks_row[1] or 0
            },
            "transactions": {
                "total": txs_row[0] or 0,
                "last_24h": txs_row[1] or 0
            },
            "accounts": accounts_count,
            "validators": validators_count,
            "dex_volume_24h": dex_volume,
            "bridge": {
                "total_transfers": bridge_row[0] or 0,
                "total_volume": bridge_row[1] or 0
            },
            "dao": {
                "total_proposals": dao_row[0] or 0,
                "active_proposals": dao_row[1] or 0
            }
        }
```

---

## 🚀 API Endpoints

### Step 3: Create Blockchain API Router

**File:** `webapp/api/blockchain.py`

```python
"""
Blockchain API Router

Endpoints for ELCARO Chain blockchain operations:
- Block explorer
- Transaction queries
- Account management
- Validator information
- Chain statistics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
import time

# Import blockchain core
from blockchain.chain import ElcaroChain, ConsensusEngine, generate_address, elc_to_wei, wei_to_elc
from blockchain.dex import ElcaroDEX
from blockchain.bridge import ElcaroBridge, BridgeChain
from blockchain.governance import ElcaroDAO

import db

router = APIRouter()

# Global instances (in production, use singleton pattern)
chain = ElcaroChain(chain_id=1)
consensus = ConsensusEngine(chain)
dex = ElcaroDEX()
bridge = ElcaroBridge()
dao = ElcaroDAO()


# ============================================================================
# MODELS
# ============================================================================

class BlockResponse(BaseModel):
    block_number: int
    block_hash: str
    timestamp: int
    validator: str
    transactions: List[str]
    previous_hash: Optional[str]
    finalized: bool


class TransactionResponse(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    value: str
    gas_price: str
    nonce: int
    block_number: Optional[int]
    timestamp: int
    status: str


class AccountResponse(BaseModel):
    address: str
    balance: str
    balance_elc: float
    nonce: int
    transactions_count: int


class ValidatorResponse(BaseModel):
    address: str
    stake: str
    delegated_stake: str
    total_stake: str
    commission_rate: str
    blocks_produced: int
    uptime: float
    is_active: bool


class ChainStatsResponse(BaseModel):
    block_height: int
    total_transactions: int
    total_accounts: int
    active_validators: int
    total_stake: str
    tps_current: float
    tps_24h: float


# ============================================================================
# BLOCKCHAIN ENDPOINTS
# ============================================================================

@router.get("/stats", response_model=ChainStatsResponse)
async def get_chain_stats():
    """Get comprehensive chain statistics."""
    try:
        stats = chain.get_chain_stats()
        db_stats = db.get_blockchain_stats()
        
        return {
            "block_height": stats["block_height"],
            "total_transactions": stats["total_transactions"],
            "total_accounts": stats["total_accounts"],
            "active_validators": stats["active_validators"],
            "total_stake": str(stats["total_stake"]),
            "tps_current": 0,  # Calculate from recent blocks
            "tps_24h": db_stats["transactions"]["last_24h"] / 86400
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blocks/latest", response_model=BlockResponse)
async def get_latest_block():
    """Get latest block."""
    try:
        block = chain.get_latest_block()
        if not block:
            raise HTTPException(status_code=404, detail="No blocks found")
        
        return {
            "block_number": block.block_number,
            "block_hash": block.block_hash,
            "timestamp": block.timestamp,
            "validator": block.validator,
            "transactions": [tx.tx_hash for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "finalized": consensus.is_block_finalized(block.block_hash)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blocks/{block_number}", response_model=BlockResponse)
async def get_block(block_number: int):
    """Get block by number."""
    try:
        block = chain.get_block(block_number)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        return {
            "block_number": block.block_number,
            "block_hash": block.block_hash,
            "timestamp": block.timestamp,
            "validator": block.validator,
            "transactions": [tx.tx_hash for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "finalized": consensus.is_block_finalized(block.block_hash)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blocks", response_model=List[BlockResponse])
async def get_blocks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get recent blocks."""
    try:
        latest = chain.get_latest_block()
        if not latest:
            return []
        
        blocks = []
        start = latest.block_number - offset
        for i in range(start, max(start - limit, 0), -1):
            block = chain.get_block(i)
            if block:
                blocks.append({
                    "block_number": block.block_number,
                    "block_hash": block.block_hash,
                    "timestamp": block.timestamp,
                    "validator": block.validator,
                    "transactions": [tx.tx_hash for tx in block.transactions],
                    "previous_hash": block.previous_hash,
                    "finalized": consensus.is_block_finalized(block.block_hash)
                })
        
        return blocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{tx_hash}", response_model=TransactionResponse)
async def get_transaction(tx_hash: str):
    """Get transaction by hash."""
    try:
        tx_data = db.get_transaction(tx_hash)
        if not tx_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {
            "tx_hash": tx_data["tx_hash"],
            "from_address": tx_data["from_address"],
            "to_address": tx_data["to_address"],
            "value": tx_data["value"],
            "gas_price": tx_data["gas_price"],
            "nonce": tx_data["nonce"],
            "block_number": tx_data["block_number"],
            "timestamp": tx_data["timestamp"],
            "status": "confirmed" if tx_data["block_number"] else "pending"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{address}", response_model=AccountResponse)
async def get_account(address: str):
    """Get account information."""
    try:
        account = chain.get_account(address)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        txs = db.get_account_transactions(address, limit=1000)
        
        return {
            "address": address,
            "balance": str(account.balance),
            "balance_elc": float(wei_to_elc(account.balance)),
            "nonce": account.nonce,
            "transactions_count": len(txs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{address}/transactions", response_model=List[TransactionResponse])
async def get_account_transactions(
    address: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get account transactions."""
    try:
        txs = db.get_account_transactions(address, limit=limit)
        
        return [
            {
                "tx_hash": tx["tx_hash"],
                "from_address": tx["from_address"],
                "to_address": tx["to_address"],
                "value": tx["value"],
                "gas_price": tx["gas_price"],
                "nonce": tx["nonce"],
                "block_number": tx["block_number"],
                "timestamp": tx["timestamp"],
                "status": "confirmed" if tx["block_number"] else "pending"
            }
            for tx in txs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validators", response_model=List[ValidatorResponse])
async def get_validators(
    limit: int = Query(100, ge=1, le=100)
):
    """Get active validators."""
    try:
        validators = chain.get_active_validators()[:limit]
        
        return [
            {
                "address": val.address,
                "stake": str(val.stake),
                "delegated_stake": str(val.delegated_stake),
                "total_stake": str(val.stake + val.delegated_stake),
                "commission_rate": str(val.commission_rate),
                "blocks_produced": val.total_blocks_produced,
                "uptime": val.uptime,
                "is_active": True
            }
            for val in validators
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validators/{address}", response_model=ValidatorResponse)
async def get_validator(address: str):
    """Get validator information."""
    try:
        val_data = db.get_validator(address)
        if not val_data:
            raise HTTPException(status_code=404, detail="Validator not found")
        
        total_stake = Decimal(val_data["stake"]) + Decimal(val_data["delegated_stake"])
        
        return {
            "address": val_data["address"],
            "stake": val_data["stake"],
            "delegated_stake": val_data["delegated_stake"],
            "total_stake": str(total_stake),
            "commission_rate": val_data["commission_rate"],
            "blocks_produced": val_data["total_blocks_produced"],
            "uptime": val_data["uptime"],
            "is_active": bool(val_data["is_active"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ACCOUNT CREATION
# ============================================================================

class CreateAccountRequest(BaseModel):
    user_id: Optional[int] = None


@router.post("/accounts/create")
async def create_account(request: CreateAccountRequest):
    """Create new blockchain account for user."""
    try:
        address = generate_address()
        initial_balance = elc_to_wei(1000)  # 1000 ELC airdrop
        
        # Create on blockchain
        chain.create_account(address, initial_balance)
        
        # Save to database
        db.create_blockchain_account(address, str(initial_balance), request.user_id)
        
        return {
            "success": True,
            "address": address,
            "balance": str(initial_balance),
            "balance_elc": 1000.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRANSFERS
# ============================================================================

class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float  # In ELC


@router.post("/transfer")
async def transfer(request: TransferRequest):
    """Transfer ELC between accounts."""
    try:
        amount_wei = elc_to_wei(Decimal(str(request.amount)))
        
        # Create transaction
        tx = chain.create_transaction(request.from_address, request.to_address, amount_wei)
        chain.add_transaction(tx)
        
        # Save to database
        db.add_transaction(
            tx.tx_hash,
            request.from_address,
            request.to_address,
            str(amount_wei),
            str(tx.gas_price),
            tx.nonce,
            int(time.time())
        )
        
        return {
            "success": True,
            "tx_hash": tx.tx_hash,
            "from": request.from_address,
            "to": request.to_address,
            "amount": request.amount,
            "status": "pending"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

This is getting quite long! Let me create the complete integration guide as separate focused files.

Would you like me to:
1. ✅ Continue with remaining API endpoints (DEX, Bridge, Governance)?
2. ✅ Create bot commands integration?
3. ✅ Create WebApp UI components?
4. ✅ Create deployment scripts?

Let me know which part you'd like next, or I can create all of them!