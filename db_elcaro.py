"""
ELCARO Token Database Functions

All database operations for ELCARO (ELC) token:
- User balances (available, staked, locked)
- Purchase tracking (USDT → ELC on TON)
- Transaction history
- Global token statistics
- Cold wallet connections
"""

import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

from db import get_conn, invalidate_user_cache

logger = logging.getLogger(__name__)


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
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT elc_balance, elc_staked, elc_locked 
               FROM users WHERE user_id = ?""",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row:
            return {"available": 0.0, "staked": 0.0, "locked": 0.0, "total": 0.0}
        
        available = row[0] or 0.0
        staked = row[1] or 0.0
        locked = row[2] or 0.0
        
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
    
    with get_conn() as conn:
        # Get current balance
        cur = conn.execute(
            f"SELECT {column} FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        current = (row[0] or 0.0) if row else 0.0
        
        # Calculate new balance
        new_balance = current + amount
        if new_balance < 0:
            raise ValueError(f"Insufficient {balance_type} balance: {current} < {abs(amount)}")
        
        # Update balance
        conn.execute(
            f"UPDATE users SET {column} = ? WHERE user_id = ?",
            (new_balance, user_id)
        )
        
        # Record transaction
        transaction_type = "adjustment" if not description else description
        add_elc_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=new_balance,
            description=description
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
        
        return get_elc_balance(user_id)


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
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO elc_purchases 
               (user_id, payment_id, usdt_amount, elc_amount, platform_fee, 
                status, payment_method, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, CURRENT_TIMESTAMP)""",
            (user_id, payment_id, usdt_amount, elc_amount, platform_fee, payment_method)
        )
        conn.commit()
        return cur.lastrowid


def get_elc_purchase(payment_id: str) -> Optional[Dict[str, Any]]:
    """Get ELC purchase by payment ID."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, user_id, payment_id, usdt_amount, elc_amount, 
                      platform_fee, status, payment_method, tx_hash, 
                      created_at, completed_at
               FROM elc_purchases WHERE payment_id = ?""",
            (payment_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


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
    
    with get_conn() as conn:
        # Update purchase status
        conn.execute(
            """UPDATE elc_purchases 
               SET status = 'completed', tx_hash = ?, completed_at = CURRENT_TIMESTAMP
               WHERE payment_id = ?""",
            (tx_hash, payment_id)
        )
        
        # Add ELC to user balance
        conn.execute(
            "UPDATE users SET elc_balance = elc_balance + ? WHERE user_id = ?",
            (elc_amount, user_id)
        )
        
        # Get new balance
        cur = conn.execute(
            "SELECT elc_balance FROM users WHERE user_id = ?",
            (user_id,)
        )
        new_balance = cur.fetchone()[0]
        
        # Record transaction
        add_elc_transaction(
            user_id=user_id,
            transaction_type="purchase",
            amount=elc_amount,
            balance_after=new_balance,
            description=f"Purchased {elc_amount} ELC with USDT",
            metadata=json.dumps({
                "payment_id": payment_id,
                "tx_hash": tx_hash,
                "usdt_amount": purchase["usdt_amount"]
            })
        )
        
        # Update global stats
        update_elc_stats(total_purchases_delta=elc_amount)
        
        conn.commit()
        invalidate_user_cache(user_id)
        
        logger.info(f"Completed ELC purchase: {payment_id} → {elc_amount} ELC to user {user_id}")
        return True


def fail_elc_purchase(payment_id: str) -> bool:
    """Mark ELC purchase as failed."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE elc_purchases SET status = 'failed' WHERE payment_id = ?",
            (payment_id,)
        )
        conn.commit()
        return True


def get_user_elc_purchases(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's ELC purchase history."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, payment_id, usdt_amount, elc_amount, platform_fee,
                      status, payment_method, tx_hash, created_at, completed_at
               FROM elc_purchases 
               WHERE user_id = ? 
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]


# ------------------------------------------------------------------------------------
# ELC Transactions
# ------------------------------------------------------------------------------------

def add_elc_transaction(
    user_id: int,
    transaction_type: str,
    amount: float,
    balance_after: float,
    description: str = None,
    metadata: str = None
) -> int:
    """
    Record an ELC transaction.
    
    Args:
        user_id: User ID
        transaction_type: purchase, subscription, marketplace, burn, stake, unstake, withdraw
        amount: Transaction amount (negative for spending)
        balance_after: Balance after transaction
        description: Human-readable description
        metadata: JSON string with additional data
    
    Returns:
        Transaction ID
    """
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO elc_transactions 
               (user_id, transaction_type, amount, balance_after, description, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (user_id, transaction_type, amount, balance_after, description, metadata)
        )
        conn.commit()
        return cur.lastrowid


def get_elc_transactions(
    user_id: int,
    transaction_type: str = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get user's ELC transaction history.
    
    Args:
        user_id: User ID
        transaction_type: Filter by type (optional)
        limit: Max number of transactions
    
    Returns:
        List of transaction dicts
    """
    with get_conn() as conn:
        if transaction_type:
            cur = conn.execute(
                """SELECT id, transaction_type, amount, balance_after, 
                          description, metadata, created_at
                   FROM elc_transactions 
                   WHERE user_id = ? AND transaction_type = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, transaction_type, limit)
            )
        else:
            cur = conn.execute(
                """SELECT id, transaction_type, amount, balance_after,
                          description, metadata, created_at
                   FROM elc_transactions 
                   WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit)
            )
        return [dict(row) for row in cur.fetchall()]


# ------------------------------------------------------------------------------------
# ELC Global Statistics
# ------------------------------------------------------------------------------------

def get_elc_stats() -> Dict[str, Any]:
    """
    Get global ELCARO token statistics.
    
    Returns:
        {
            "total_burned": 1500000.0,
            "total_staked": 50000000.0,
            "circulating_supply": 998500000.0,
            "total_purchases": 10000000.0,
            "total_subscriptions": 500000.0,
            "last_burn_at": "2025-01-15 12:00:00",
            "last_update": "2025-01-15 14:30:00"
        }
    """
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT total_burned, total_staked, circulating_supply,
                      total_purchases, total_subscriptions, last_burn_at, last_update
               FROM elc_stats WHERE id = 1"""
        )
        row = cur.fetchone()
        
        if not row:
            return {
                "total_burned": 0.0,
                "total_staked": 0.0,
                "circulating_supply": 1000000000.0,
                "total_purchases": 0.0,
                "total_subscriptions": 0.0,
                "last_burn_at": None,
                "last_update": None
            }
        
        return dict(row)


def update_elc_stats(
    total_burned_delta: float = 0.0,
    total_staked_delta: float = 0.0,
    circulating_supply_delta: float = 0.0,
    total_purchases_delta: float = 0.0,
    total_subscriptions_delta: float = 0.0,
    record_burn: bool = False
) -> Dict[str, Any]:
    """
    Update global ELC statistics.
    
    Args:
        *_delta: Amount to add/subtract from each stat
        record_burn: Set to True to update last_burn_at timestamp
    
    Returns:
        Updated stats
    """
    with get_conn() as conn:
        # Build update query
        updates = []
        params = []
        
        if total_burned_delta != 0:
            updates.append("total_burned = total_burned + ?")
            params.append(total_burned_delta)
        
        if total_staked_delta != 0:
            updates.append("total_staked = total_staked + ?")
            params.append(total_staked_delta)
        
        if circulating_supply_delta != 0:
            updates.append("circulating_supply = circulating_supply + ?")
            params.append(circulating_supply_delta)
        
        if total_purchases_delta != 0:
            updates.append("total_purchases = total_purchases + ?")
            params.append(total_purchases_delta)
        
        if total_subscriptions_delta != 0:
            updates.append("total_subscriptions = total_subscriptions + ?")
            params.append(total_subscriptions_delta)
        
        if record_burn:
            updates.append("last_burn_at = CURRENT_TIMESTAMP")
        
        updates.append("last_update = CURRENT_TIMESTAMP")
        
        if updates:
            query = f"UPDATE elc_stats SET {', '.join(updates)} WHERE id = 1"
            conn.execute(query, tuple(params))
            conn.commit()
        
        return get_elc_stats()


def record_elc_burn(amount: float, description: str = None) -> Dict[str, Any]:
    """
    Record an ELC burn event (reduces circulating supply).
    
    Args:
        amount: Amount of ELC burned
        description: Burn reason
    
    Returns:
        Updated stats
    """
    return update_elc_stats(
        total_burned_delta=amount,
        circulating_supply_delta=-amount,
        record_burn=True
    )


# ------------------------------------------------------------------------------------
# Connected Wallets (Cold Wallet Trading)
# ------------------------------------------------------------------------------------

def connect_wallet(
    user_id: int,
    wallet_address: str,
    wallet_type: str,
    chain: str = "ethereum"
) -> bool:
    """
    Connect a cold wallet to user account.
    
    Args:
        user_id: User ID
        wallet_address: Wallet address (0x... for Ethereum, UQC... for TON)
        wallet_type: "metamask", "walletconnect", "tonkeeper"
        chain: "ethereum", "ton", "polygon", "bsc"
    
    Returns:
        True if successful
    """
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO connected_wallets
               (user_id, wallet_address, wallet_type, chain, connected_at, last_used_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
            (user_id, wallet_address, wallet_type, chain)
        )
        conn.commit()
        invalidate_user_cache(user_id)
        return True


def get_connected_wallet(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's connected wallet info."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT wallet_address, wallet_type, chain, connected_at, last_used_at
               FROM connected_wallets WHERE user_id = ?""",
            (user_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def disconnect_wallet(user_id: int) -> bool:
    """Disconnect wallet from user account."""
    with get_conn() as conn:
        conn.execute("DELETE FROM connected_wallets WHERE user_id = ?", (user_id,))
        conn.commit()
        invalidate_user_cache(user_id)
        return True


def update_wallet_last_used(user_id: int) -> bool:
    """Update last_used_at timestamp for wallet."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE connected_wallets SET last_used_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        return True


# ------------------------------------------------------------------------------------
# Subscription Payments with ELC
# ------------------------------------------------------------------------------------

def pay_subscription_with_elc(
    user_id: int,
    plan: str,
    duration: str,
    elc_amount: float,
    burn_amount: float
) -> bool:
    """
    Pay for subscription with ELCARO tokens and burn 10%.
    
    Args:
        user_id: User ID
        plan: "basic", "premium", "pro"
        duration: "1m", "3m", "6m", "1y"
        elc_amount: Total ELC cost
        burn_amount: Amount to burn (10% of total)
    
    Returns:
        True if successful
    """
    # Check balance
    if not check_elc_balance(user_id, elc_amount):
        raise ValueError(f"Insufficient ELC balance: need {elc_amount}")
    
    with get_conn() as conn:
        # Deduct ELC from user balance
        conn.execute(
            "UPDATE users SET elc_balance = elc_balance - ? WHERE user_id = ?",
            (elc_amount, user_id)
        )
        
        # Get new balance
        cur = conn.execute(
            "SELECT elc_balance FROM users WHERE user_id = ?",
            (user_id,)
        )
        new_balance = cur.fetchone()[0]
        
        # Record transaction
        add_elc_transaction(
            user_id=user_id,
            transaction_type="subscription",
            amount=-elc_amount,
            balance_after=new_balance,
            description=f"Subscription: {plan} for {duration}",
            metadata=json.dumps({
                "plan": plan,
                "duration": duration,
                "total_elc": elc_amount,
                "burned_elc": burn_amount
            })
        )
        
        # Record burn
        record_elc_burn(
            amount=burn_amount,
            description=f"Subscription burn: {plan} {duration}"
        )
        
        # Update global stats
        update_elc_stats(total_subscriptions_delta=elc_amount)
        
        conn.commit()
        invalidate_user_cache(user_id)
        
        logger.info(f"User {user_id} paid {elc_amount} ELC for {plan} subscription ({burn_amount} burned)")
        return True


# ------------------------------------------------------------------------------------
# Admin Functions
# ------------------------------------------------------------------------------------

def distribute_elc_to_users(
    user_ids: List[int],
    amount_per_user: float,
    description: str = "Admin distribution"
) -> Dict[str, int]:
    """
    Distribute ELC to multiple users (admin function).
    
    Returns:
        {"success": 10, "failed": 0}
    """
    success = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            add_elc_balance(user_id, amount_per_user, description)
            success += 1
        except Exception as e:
            logger.error(f"Failed to distribute {amount_per_user} ELC to user {user_id}: {e}")
            failed += 1
    
    return {"success": success, "failed": failed}


def get_total_elc_distributed() -> float:
    """Get total ELC distributed to all users."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT SUM(elc_balance + elc_staked + elc_locked) FROM users"
        )
        total = cur.fetchone()[0]
        return total or 0.0


def get_top_elc_holders(limit: int = 100) -> List[Dict[str, Any]]:
    """Get top ELC holders."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT user_id, 
                      (elc_balance + elc_staked + elc_locked) as total_elc,
                      elc_balance, elc_staked, elc_locked
               FROM users 
               WHERE (elc_balance + elc_staked + elc_locked) > 0
               ORDER BY total_elc DESC LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in cur.fetchall()]
