"""
Database extensions for Web3 Integration
Adds wallet addresses, NFT token IDs, blockchain transactions

PostgreSQL Version (January 2026 Migration)
"""
import json
import time
import logging
from typing import Dict, Any, Optional, List

# Use centralized PostgreSQL connection from core
from core.db_postgres import get_conn

logger = logging.getLogger(__name__)


def init_web3_tables():
    """
    Initialize Web3-specific tables.
    Call this during init_db() in db.py
    
    PostgreSQL version - uses SERIAL instead of AUTOINCREMENT
    """
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Add Web3 columns to users table (using PostgreSQL ALTER)
        web3_columns = [
            ("wallet_address", "TEXT"),
            ("wallet_network", "TEXT"),  # 'polygon', 'bsc', etc.
            ("wallet_verified", "INTEGER DEFAULT 0"),
            ("wallet_connected_at", "BIGINT"),
            ("elcaro_balance", "REAL DEFAULT 0"),  # Cached ENLIKO token balance
            ("balance_updated_at", "BIGINT"),
        ]
        
        for col, type_ in web3_columns:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {type_}")
                logger.info(f"Added column {col} to users table")
            except Exception as e:
                # Column might already exist
                logger.debug(f"Column {col} may already exist: {e}")
        
        # Strategy NFTs - links strategies to blockchain NFTs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_nfts (
                id SERIAL PRIMARY KEY,
                strategy_id INTEGER NOT NULL UNIQUE,
                token_id INTEGER,
                contract_address TEXT NOT NULL,
                network TEXT NOT NULL,
                owner_address TEXT NOT NULL,
                creator_address TEXT NOT NULL,
                metadata_uri TEXT,
                mint_tx_hash TEXT,
                minted_at BIGINT NOT NULL,
                is_listed INTEGER DEFAULT 0,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nft_token ON strategy_nfts(token_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nft_owner ON strategy_nfts(owner_address)")
        
        # Blockchain transactions - all on-chain activity
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                tx_hash TEXT NOT NULL UNIQUE,
                network TEXT NOT NULL,
                tx_type TEXT NOT NULL,  -- 'strategy_purchase', 'subscription', 'nft_mint', etc.
                status TEXT DEFAULT 'pending',  -- 'pending', 'confirmed', 'failed'
                from_address TEXT NOT NULL,
                to_address TEXT,
                amount REAL DEFAULT 0,
                token_symbol TEXT,  -- 'ELCARO', 'MATIC', 'BNB', etc.
                gas_used INTEGER,
                gas_price REAL,
                block_number INTEGER,
                data_json TEXT,  -- Additional data
                created_at BIGINT NOT NULL,
                confirmed_at BIGINT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_user ON blockchain_transactions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_hash ON blockchain_transactions(tx_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_status ON blockchain_transactions(status)")
        
        # Marketplace listings (blockchain version)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_listings (
                id SERIAL PRIMARY KEY,
                strategy_id INTEGER NOT NULL,
                nft_token_id INTEGER NOT NULL,
                listing_id INTEGER,  -- On-chain listing ID
                seller_address TEXT NOT NULL,
                price_elcaro REAL NOT NULL,
                royalty_percent REAL DEFAULT 5.0,
                status TEXT DEFAULT 'active',  -- 'active', 'sold', 'cancelled'
                list_tx_hash TEXT,
                sale_tx_hash TEXT,
                listed_at BIGINT NOT NULL,
                sold_at BIGINT,
                buyer_address TEXT,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_listing_seller ON blockchain_listings(seller_address)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_listing_status ON blockchain_listings(status)")
        
        # Subscriptions paid with ENLIKO tokens
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_subscriptions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                wallet_address TEXT NOT NULL,
                plan TEXT NOT NULL,  -- 'basic', 'premium'
                months INTEGER NOT NULL,
                price_elcaro REAL NOT NULL,
                tx_hash TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                expires_at BIGINT,
                created_at BIGINT NOT NULL,
                confirmed_at BIGINT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sub_user ON blockchain_subscriptions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sub_wallet ON blockchain_subscriptions(wallet_address)")
        
        conn.commit()
        logger.info("Web3 tables initialized (PostgreSQL)")


# ==========================================
# WALLET MANAGEMENT
# ==========================================

def set_user_wallet(
    user_id: int,
    wallet_address: str,
    network: str = "polygon",
    verified: bool = True
) -> bool:
    """
    Link wallet to user account.
    
    Args:
        user_id: User ID
        wallet_address: Wallet address (0x...)
        network: Network name
        verified: Is signature verified
    
    Returns:
        True on success
    """
    with get_conn() as conn:
        conn.execute("""
            UPDATE users SET
                wallet_address = ?,
                wallet_network = ?,
                wallet_verified = ?,
                wallet_connected_at = ?
            WHERE user_id = ?
        """, (
            wallet_address.lower(),
            network,
            1 if verified else 0,
            int(time.time()),
            user_id
        ))
        conn.commit()
    
    logger.info(f"User {user_id} connected wallet {wallet_address[:10]}... on {network}")
    return True


def get_user_wallet(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's connected wallet"""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT wallet_address, wallet_network, wallet_verified, 
                   elcaro_balance, balance_updated_at
            FROM users WHERE user_id = ?
        """, (user_id,)).fetchone()
        
        if row and row[0]:
            return {
                'wallet_address': row[0],
                'network': row[1],
                'verified': bool(row[2]),
                'elcaro_balance': row[3] or 0,
                'balance_updated_at': row[4]
            }
        return None


def update_token_balance(user_id: int, balance: float):
    """Update cached ENLIKO token balance"""
    with get_conn() as conn:
        conn.execute("""
            UPDATE users SET
                elcaro_balance = ?,
                balance_updated_at = ?
            WHERE user_id = ?
        """, (balance, int(time.time()), user_id))
        conn.commit()


# ==========================================
# USER STRATEGIES (Save/Load)
# ==========================================

def save_user_strategy(
    user_id: int,
    name: str,
    config: Dict[str, Any],
    description: str = "",
    base_strategy: str = "custom"
) -> int:
    """
    Save custom strategy configuration.
    
    Args:
        user_id: User ID
        name: Strategy name
        config: Full strategy config from StrategyConfig
        description: Strategy description
        base_strategy: Base strategy type
    
    Returns:
        Strategy ID
    """
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Check if strategy with same name exists
        existing = cur.execute("""
            SELECT id FROM custom_strategies
            WHERE user_id = ? AND name = ?
        """, (user_id, name)).fetchone()
        
        now = int(time.time())
        config_json = json.dumps(config)
        
        if existing:
            # Update existing
            cur.execute("""
                UPDATE custom_strategies SET
                    description = ?,
                    config_json = ?,
                    base_strategy = ?,
                    updated_at = ?
                WHERE id = ?
            """, (description, config_json, base_strategy, now, existing[0]))
            strategy_id = existing[0]
        else:
            # Create new
            cur.execute("""
                INSERT INTO custom_strategies
                (user_id, name, description, base_strategy, config_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, description, base_strategy, config_json, now, now))
            strategy_id = cur.lastrowid
        
        conn.commit()
    
    logger.info(f"User {user_id} saved strategy '{name}' (id={strategy_id})")
    return strategy_id


def get_user_strategies(user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get all strategies created by user.
    
    Args:
        user_id: User ID
        active_only: Only active strategies
    
    Returns:
        List of strategy dicts
    """
    with get_conn() as conn:
        query = """
            SELECT id, name, description, base_strategy, config_json,
                   is_public, is_active, win_rate, total_pnl, total_trades,
                   backtest_score, created_at, updated_at
            FROM custom_strategies
            WHERE user_id = ?
        """
        
        if active_only:
            query += " AND is_active = TRUE"
        
        query += " ORDER BY updated_at DESC"
        
        rows = conn.execute(query, (user_id,)).fetchall()
        
        strategies = []
        for row in rows:
            strategies.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'base_strategy': row[3],
                'config': json.loads(row[4]) if row[4] else {},
                'is_public': bool(row[5]),
                'is_active': bool(row[6]),
                'win_rate': row[7],
                'total_pnl': row[8],
                'total_trades': row[9],
                'backtest_score': row[10],
                'created_at': row[11],
                'updated_at': row[12]
            })
        
        return strategies


def get_strategy_by_id(strategy_id: int) -> Optional[Dict[str, Any]]:
    """Get strategy by ID"""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT id, user_id, name, description, base_strategy, config_json,
                   is_public, is_active, win_rate, total_pnl, total_trades
            FROM custom_strategies
            WHERE id = ?
        """, (strategy_id,)).fetchone()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'description': row[3],
                'base_strategy': row[4],
                'config': json.loads(row[5]) if row[5] else {},
                'is_public': bool(row[6]),
                'is_active': bool(row[7]),
                'win_rate': row[8],
                'total_pnl': row[9],
                'total_trades': row[10]
            }
        return None


def delete_user_strategy(user_id: int, strategy_id: int) -> bool:
    """Delete user's strategy"""
    with get_conn() as conn:
        conn.execute("""
            DELETE FROM custom_strategies
            WHERE id = ? AND user_id = ?
        """, (strategy_id, user_id))
        conn.commit()
        return conn.total_changes > 0


# ==========================================
# STRATEGY NFTs
# ==========================================

def create_strategy_nft(
    strategy_id: int,
    contract_address: str,
    network: str,
    owner_address: str,
    creator_address: str,
    token_id: Optional[int] = None,
    mint_tx_hash: Optional[str] = None
) -> int:
    """
    Register strategy NFT in database.
    
    Args:
        strategy_id: Strategy ID
        contract_address: NFT contract address
        network: Network name
        owner_address: Current owner
        creator_address: Original creator
        token_id: On-chain token ID
        mint_tx_hash: Minting transaction hash
    
    Returns:
        NFT record ID
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO strategy_nfts
            (strategy_id, token_id, contract_address, network, owner_address,
             creator_address, mint_tx_hash, minted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy_id, token_id, contract_address, network,
            owner_address.lower(), creator_address.lower(),
            mint_tx_hash, int(time.time())
        ))
        conn.commit()
        return cur.lastrowid


def get_user_nfts(wallet_address: str) -> List[Dict[str, Any]]:
    """Get all strategy NFTs owned by wallet"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT sn.id, sn.strategy_id, sn.token_id, sn.contract_address,
                   sn.network, cs.name, cs.description, cs.win_rate, cs.total_pnl
            FROM strategy_nfts sn
            JOIN custom_strategies cs ON sn.strategy_id = cs.id
            WHERE sn.owner_address = ?
        """, (wallet_address.lower(),)).fetchall()
        
        nfts = []
        for row in rows:
            nfts.append({
                'nft_id': row[0],
                'strategy_id': row[1],
                'token_id': row[2],
                'contract_address': row[3],
                'network': row[4],
                'name': row[5],
                'description': row[6],
                'win_rate': row[7],
                'total_pnl': row[8]
            })
        
        return nfts


# ==========================================
# BLOCKCHAIN TRANSACTIONS
# ==========================================

def log_blockchain_tx(
    user_id: int,
    tx_hash: str,
    network: str,
    tx_type: str,
    from_address: str,
    to_address: Optional[str] = None,
    amount: float = 0,
    token_symbol: str = "ELCARO",
    data: Optional[Dict] = None
) -> int:
    """Log blockchain transaction"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO blockchain_transactions
            (user_id, tx_hash, network, tx_type, from_address, to_address,
             amount, token_symbol, data_json, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (
            user_id, tx_hash, network, tx_type,
            from_address.lower(), to_address.lower() if to_address else None,
            amount, token_symbol, json.dumps(data or {}), int(time.time())
        ))
        conn.commit()
        return cur.lastrowid


def update_tx_status(
    tx_hash: str,
    status: str,
    block_number: Optional[int] = None,
    gas_used: Optional[int] = None
):
    """Update transaction status"""
    with get_conn() as conn:
        fields = ["status = ?"]
        values = [status]
        
        if status == "confirmed":
            fields.append("confirmed_at = ?")
            values.append(int(time.time()))
        
        if block_number:
            fields.append("block_number = ?")
            values.append(block_number)
        
        if gas_used:
            fields.append("gas_used = ?")
            values.append(gas_used)
        
        values.append(tx_hash)
        
        conn.execute(f"""
            UPDATE blockchain_transactions
            SET {', '.join(fields)}
            WHERE tx_hash = ?
        """, values)
        conn.commit()


def get_user_transactions(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's blockchain transactions"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT tx_hash, network, tx_type, from_address, to_address,
                   amount, token_symbol, status, created_at, confirmed_at
            FROM blockchain_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        
        txs = []
        for row in rows:
            txs.append({
                'tx_hash': row[0],
                'network': row[1],
                'tx_type': row[2],
                'from_address': row[3],
                'to_address': row[4],
                'amount': row[5],
                'token_symbol': row[6],
                'status': row[7],
                'created_at': row[8],
                'confirmed_at': row[9]
            })
        
        return txs
