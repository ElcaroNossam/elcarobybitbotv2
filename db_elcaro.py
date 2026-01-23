"""
ELCARO Token Database Functions

All database operations for ELCARO (ELC) token:
- User balances (available, staked, locked)
- Purchase tracking (USDT → ELC on TON)
- Transaction history
- Global token statistics
- Cold wallet connections

PostgreSQL ONLY - No SQLite support
"""

import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

# PostgreSQL imports
from core.db_postgres import get_pool, get_conn, execute, execute_one, execute_write

import db
from db import invalidate_user_cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS (PostgreSQL Only)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_conn():
    """Get PostgreSQL connection from pool"""
    pool = get_pool()
    return pool.getconn()

def _release_conn(conn):
    """Release connection back to pool"""
    pool = get_pool()
    pool.putconn(conn)


# ------------------------------------------------------------------------------------
# User ELC Balances
# ------------------------------------------------------------------------------------

def get_elc_balance(user_id: int) -> Dict[str, float]:
    """
    Get user's ELCARO token balance breakdown.
    
    Returns:
        {
            "available": 1000.0,
            "staked": 5000.0,
            "locked": 500.0,
            "total": 6500.0
        }
    """
    row = execute_one(
        """SELECT elc_balance, elc_staked, elc_locked 
           FROM users WHERE user_id = %s""",
        (user_id,)
    )
    
    if not row:
        return {"available": 0.0, "staked": 0.0, "locked": 0.0, "total": 0.0}
    
    available = row.get("elc_balance") or 0.0
    staked = row.get("elc_staked") or 0.0
    locked = row.get("elc_locked") or 0.0
    
    return {
        "available": available,
        "staked": staked,
        "locked": locked,
        "total": available + staked + locked
    }


def update_elc_balance(
    user_id: int,
    amount: float,
    balance_type: str = "available",
    description: str = None
) -> Dict[str, float]:
    """
    Update user's ELC balance (available, staked, or locked).
    
    Args:
        user_id: User ID
        amount: Amount to add (positive) or subtract (negative)
        balance_type: "available", "staked", or "locked"
        description: Transaction description
    
    Returns:
        New balance breakdown
    """
    if balance_type not in ["available", "staked", "locked"]:
        raise ValueError(f"Invalid balance_type: {balance_type}")
    
    column_map = {
        "available": "elc_balance",
        "staked": "elc_staked",
        "locked": "elc_locked"
    }
    column = column_map[balance_type]
    
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Get current balance
        cur.execute(f"SELECT {column} FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        current = (row[0] or 0.0) if row else 0.0
        
        # Calculate new balance
        new_balance = current + amount
        if new_balance < 0:
            raise ValueError(f"Insufficient {balance_type} balance: {current} < {abs(amount)}")
        
        # Update balance
        cur.execute(
            f"UPDATE users SET {column} = %s WHERE user_id = %s",
            (new_balance, user_id)
        )
        
        conn.commit()
        
        # Record transaction
        transaction_type = "adjustment" if not description else description
        add_elc_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=new_balance,
            description=description
        )
        
        invalidate_user_cache(user_id)
        return get_elc_balance(user_id)
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        _release_conn(conn)


def add_elc_balance(user_id: int, amount: float, description: str = None) -> Dict[str, float]:
    """Shortcut to add ELC to available balance."""
    return update_elc_balance(user_id, amount, "available", description)


def subtract_elc_balance(user_id: int, amount: float, description: str = None) -> Dict[str, float]:
    """Shortcut to subtract ELC from available balance."""
    return update_elc_balance(user_id, -abs(amount), "available", description)


def check_elc_balance(user_id: int, required_amount: float) -> bool:
    """Check if user has sufficient available ELC balance."""
    balance = get_elc_balance(user_id)
    return balance["available"] >= required_amount


# ------------------------------------------------------------------------------------
# ELC Purchases (USDT → ELC)
# ------------------------------------------------------------------------------------

def create_elc_purchase(
    user_id: int,
    payment_id: str,
    usdt_amount: float,
    elc_amount: float,
    platform_fee: float,
    payment_method: str = "ton_usdt"
) -> int:
    """
    Create a new ELC purchase record.
    
    Args:
        user_id: User ID
        payment_id: Unique payment identifier
        usdt_amount: Amount of USDT to pay
        elc_amount: Amount of ELC to receive
        platform_fee: Platform fee in USDT
        payment_method: "ton_usdt" or "direct_wallet"
    
    Returns:
        Purchase ID
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO elc_purchases 
               (user_id, payment_id, usdt_amount, elc_amount, platform_fee, 
                status, payment_method, created_at)
               VALUES (%s, %s, %s, %s, %s, 'pending', %s, NOW())
               RETURNING id""",
            (user_id, payment_id, usdt_amount, elc_amount, platform_fee, payment_method)
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else 0
    finally:
        _release_conn(conn)


def get_elc_purchase(payment_id: str) -> Optional[Dict[str, Any]]:
    """Get ELC purchase by payment ID."""
    return execute_one(
        """SELECT id, user_id, payment_id, usdt_amount, elc_amount, 
                  platform_fee, status, payment_method, tx_hash, 
                  created_at, completed_at
           FROM elc_purchases WHERE payment_id = %s""",
        (payment_id,)
    )


def complete_elc_purchase(
    payment_id: str,
    tx_hash: str = None
) -> bool:
    """
    Mark ELC purchase as completed and distribute ELC to user.
    
    Args:
        payment_id: Payment ID
        tx_hash: TON blockchain transaction hash
    
    Returns:
        True if successful
    """
    purchase = get_elc_purchase(payment_id)
    if not purchase:
        logger.error(f"Purchase not found: {payment_id}")
        return False
    
    if purchase["status"] == "completed":
        logger.warning(f"Purchase already completed: {payment_id}")
        return True
    
    user_id = purchase["user_id"]
    elc_amount = purchase["elc_amount"]
    
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Update purchase status
        cur.execute(
            """UPDATE elc_purchases 
               SET status = 'completed', tx_hash = %s, completed_at = NOW()
               WHERE payment_id = %s""",
            (tx_hash, payment_id)
        )
        
        # Add ELC to user balance
        cur.execute(
            """UPDATE users 
               SET elc_balance = COALESCE(elc_balance, 0) + %s 
               WHERE user_id = %s
               RETURNING elc_balance""",
            (elc_amount, user_id)
        )
        row = cur.fetchone()
        new_balance = row[0] if row else elc_amount
        
        conn.commit()
        
        # Record transaction
        add_elc_transaction(
            user_id=user_id,
            transaction_type="purchase",
            amount=elc_amount,
            balance_after=new_balance,
            tx_hash=tx_hash,
            description=f"Purchase via {purchase.get('payment_method', 'ton_usdt')}"
        )
        
        invalidate_user_cache(user_id)
        logger.info(f"ELC purchase completed: {payment_id}, user={user_id}, amount={elc_amount}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to complete purchase {payment_id}: {e}")
        return False
    finally:
        _release_conn(conn)


def get_user_purchases(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's purchase history."""
    return execute(
        """SELECT id, payment_id, usdt_amount, elc_amount, platform_fee,
                  status, payment_method, tx_hash, created_at, completed_at
           FROM elc_purchases 
           WHERE user_id = %s
           ORDER BY created_at DESC
           LIMIT %s""",
        (user_id, limit)
    )


# ------------------------------------------------------------------------------------
# ELC Transactions
# ------------------------------------------------------------------------------------

def add_elc_transaction(
    user_id: int,
    transaction_type: str,
    amount: float,
    balance_after: float,
    tx_hash: str = None,
    description: str = None,
    related_user_id: int = None
) -> int:
    """
    Record an ELC transaction.
    
    Args:
        user_id: User ID
        transaction_type: "purchase", "transfer_in", "transfer_out", "stake", "unstake", "reward", "fee"
        amount: Transaction amount (positive or negative)
        balance_after: Balance after transaction
        tx_hash: Blockchain transaction hash (if applicable)
        description: Human-readable description
        related_user_id: Related user (for transfers)
    
    Returns:
        Transaction ID
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO elc_transactions 
               (user_id, transaction_type, amount, balance_after, tx_hash, 
                description, related_user_id, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
               RETURNING id""",
            (user_id, transaction_type, amount, balance_after, tx_hash, 
             description, related_user_id)
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else 0
    finally:
        _release_conn(conn)


def get_user_transactions(
    user_id: int, 
    limit: int = 50,
    transaction_type: str = None
) -> List[Dict[str, Any]]:
    """Get user's transaction history."""
    if transaction_type:
        return execute(
            """SELECT id, transaction_type, amount, balance_after, tx_hash,
                      description, related_user_id, created_at
               FROM elc_transactions 
               WHERE user_id = %s AND transaction_type = %s
               ORDER BY created_at DESC
               LIMIT %s""",
            (user_id, transaction_type, limit)
        )
    else:
        return execute(
            """SELECT id, transaction_type, amount, balance_after, tx_hash,
                      description, related_user_id, created_at
               FROM elc_transactions 
               WHERE user_id = %s
               ORDER BY created_at DESC
               LIMIT %s""",
            (user_id, limit)
        )


# Alias for backward compatibility
get_elc_transactions = get_user_transactions


# ------------------------------------------------------------------------------------
# ELC Staking
# ------------------------------------------------------------------------------------

def stake_elc(user_id: int, amount: float) -> Dict[str, float]:
    """
    Stake ELC tokens (move from available to staked).
    
    Args:
        user_id: User ID
        amount: Amount to stake
    
    Returns:
        New balance breakdown
    """
    if amount <= 0:
        raise ValueError("Stake amount must be positive")
    
    balance = get_elc_balance(user_id)
    if balance["available"] < amount:
        raise ValueError(f"Insufficient available balance: {balance['available']} < {amount}")
    
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Move from available to staked
        cur.execute(
            """UPDATE users 
               SET elc_balance = elc_balance - %s,
                   elc_staked = COALESCE(elc_staked, 0) + %s
               WHERE user_id = %s""",
            (amount, amount, user_id)
        )
        
        conn.commit()
        
        # Record transaction
        new_balance = get_elc_balance(user_id)
        add_elc_transaction(
            user_id=user_id,
            transaction_type="stake",
            amount=-amount,
            balance_after=new_balance["available"],
            description=f"Staked {amount} ELC"
        )
        
        invalidate_user_cache(user_id)
        return new_balance
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        _release_conn(conn)


def unstake_elc(user_id: int, amount: float) -> Dict[str, float]:
    """
    Unstake ELC tokens (move from staked to available).
    
    Args:
        user_id: User ID
        amount: Amount to unstake
    
    Returns:
        New balance breakdown
    """
    if amount <= 0:
        raise ValueError("Unstake amount must be positive")
    
    balance = get_elc_balance(user_id)
    if balance["staked"] < amount:
        raise ValueError(f"Insufficient staked balance: {balance['staked']} < {amount}")
    
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Move from staked to available
        cur.execute(
            """UPDATE users 
               SET elc_balance = COALESCE(elc_balance, 0) + %s,
                   elc_staked = elc_staked - %s
               WHERE user_id = %s""",
            (amount, amount, user_id)
        )
        
        conn.commit()
        
        # Record transaction
        new_balance = get_elc_balance(user_id)
        add_elc_transaction(
            user_id=user_id,
            transaction_type="unstake",
            amount=amount,
            balance_after=new_balance["available"],
            description=f"Unstaked {amount} ELC"
        )
        
        invalidate_user_cache(user_id)
        return new_balance
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        _release_conn(conn)


# ------------------------------------------------------------------------------------
# ELC Statistics
# ------------------------------------------------------------------------------------

def get_elc_stats() -> Dict[str, Any]:
    """Get global ELC token statistics."""
    row = execute_one(
        """SELECT 
              COUNT(DISTINCT user_id) as holders,
              SUM(elc_balance) as total_available,
              SUM(elc_staked) as total_staked,
              SUM(elc_locked) as total_locked,
              SUM(elc_balance + COALESCE(elc_staked, 0) + COALESCE(elc_locked, 0)) as total_supply
           FROM users
           WHERE elc_balance > 0 OR elc_staked > 0 OR elc_locked > 0"""
    )
    
    purchases = execute_one(
        """SELECT 
              COUNT(*) as total_purchases,
              SUM(usdt_amount) as total_usdt_volume,
              SUM(elc_amount) as total_elc_purchased
           FROM elc_purchases
           WHERE status = 'completed'"""
    )
    
    return {
        "holders": row.get("holders") or 0 if row else 0,
        "total_available": row.get("total_available") or 0 if row else 0,
        "total_staked": row.get("total_staked") or 0 if row else 0,
        "total_locked": row.get("total_locked") or 0 if row else 0,
        "total_supply": row.get("total_supply") or 0 if row else 0,
        "total_purchases": purchases.get("total_purchases") or 0 if purchases else 0,
        "total_usdt_volume": purchases.get("total_usdt_volume") or 0 if purchases else 0,
        "total_elc_purchased": purchases.get("total_elc_purchased") or 0 if purchases else 0
    }


def get_top_holders(limit: int = 100) -> List[Dict[str, Any]]:
    """Get top ELC holders."""
    return execute(
        """SELECT 
              user_id,
              elc_balance as available,
              elc_staked as staked,
              elc_locked as locked,
              (elc_balance + COALESCE(elc_staked, 0) + COALESCE(elc_locked, 0)) as total
           FROM users
           WHERE elc_balance > 0 OR elc_staked > 0 OR elc_locked > 0
           ORDER BY total DESC
           LIMIT %s""",
        (limit,)
    )


# ------------------------------------------------------------------------------------
# Cold Wallet Connections
# ------------------------------------------------------------------------------------

def connect_cold_wallet(
    user_id: int,
    wallet_address: str,
    wallet_type: str = "ton",
    signature: str = None
) -> bool:
    """
    Connect a cold wallet for ELC operations.
    
    Args:
        user_id: User ID
        wallet_address: Wallet address
        wallet_type: "ton", "eth", "solana"
        signature: Verification signature
    
    Returns:
        True if successful
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO connected_wallets 
               (user_id, wallet_address, wallet_type, signature, connected_at, is_active)
               VALUES (%s, %s, %s, %s, NOW(), TRUE)
               ON CONFLICT (user_id, wallet_address) DO UPDATE SET
                   is_active = TRUE,
                   signature = EXCLUDED.signature""",
            (user_id, wallet_address, wallet_type, signature)
        )
        conn.commit()
        invalidate_user_cache(user_id)
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to connect wallet: {e}")
        return False
    finally:
        _release_conn(conn)


def disconnect_cold_wallet(user_id: int, wallet_address: str) -> bool:
    """Disconnect a cold wallet."""
    count = execute_write(
        """UPDATE connected_wallets 
           SET is_active = FALSE 
           WHERE user_id = %s AND wallet_address = %s""",
        (user_id, wallet_address)
    )
    if count > 0:
        invalidate_user_cache(user_id)
    return count > 0


def disconnect_wallet(user_id: int) -> bool:
    """Disconnect all cold wallets for user (alias for backward compatibility)."""
    count = execute_write(
        """UPDATE connected_wallets 
           SET is_active = FALSE 
           WHERE user_id = %s""",
        (user_id,)
    )
    if count > 0:
        invalidate_user_cache(user_id)
    return count > 0


def get_connected_wallets(user_id: int) -> List[Dict[str, Any]]:
    """Get user's connected cold wallets."""
    return execute(
        """SELECT wallet_address, wallet_type, connected_at, is_active
           FROM connected_wallets
           WHERE user_id = %s AND is_active = TRUE
           ORDER BY connected_at DESC""",
        (user_id,)
    )


def get_connected_wallet(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's primary connected wallet (first active one)."""
    wallets = get_connected_wallets(user_id)
    if wallets:
        w = wallets[0]
        return {
            'wallet_address': w.get('wallet_address'),
            'wallet_type': w.get('wallet_type'),
            'chain': w.get('wallet_type', 'eth').upper(),
            'connected_at': str(w.get('connected_at', ''))
        }
    return None


def get_user_by_wallet(wallet_address: str) -> Optional[int]:
    """Get user ID by connected wallet address."""
    row = execute_one(
        """SELECT user_id FROM connected_wallets 
           WHERE wallet_address = %s AND is_active = TRUE""",
        (wallet_address,)
    )
    return row.get("user_id") if row else None


# ------------------------------------------------------------------------------------
# Initialize Tables
# ------------------------------------------------------------------------------------

def ensure_elc_tables():
    """Ensure all ELC-related tables exist."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # ELC purchases table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS elc_purchases (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    payment_id TEXT UNIQUE NOT NULL,
                    usdt_amount REAL NOT NULL,
                    elc_amount REAL NOT NULL,
                    platform_fee REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT DEFAULT 'ton_usdt',
                    tx_hash TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
            """)
            
            # ELC transactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS elc_transactions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    balance_after REAL,
                    tx_hash TEXT,
                    description TEXT,
                    related_user_id BIGINT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Connected wallets table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS connected_wallets (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    wallet_address TEXT NOT NULL,
                    wallet_type TEXT DEFAULT 'ton',
                    signature TEXT,
                    connected_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_id, wallet_address)
                )
            """)
            
            # Add ELC columns to users if not exist
            for col in ['elc_balance', 'elc_staked', 'elc_locked']:
                try:
                    cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} REAL DEFAULT 0")
                except Exception:
                    pass
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_purchases_user ON elc_purchases(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_transactions_user ON elc_transactions(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_connected_wallets_user ON connected_wallets(user_id)")
    
    logger.info("ELC tables initialized")


# Initialize on module load
try:
    ensure_elc_tables()
except Exception as e:
    logger.warning(f"Could not initialize ELC tables: {e}")
