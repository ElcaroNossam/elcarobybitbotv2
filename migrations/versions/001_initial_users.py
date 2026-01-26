"""
Migration: Initial Schema
Version: 001
Created: 2026-01-22

Creates all core tables for Lyxen Trading Platform.
"""


def upgrade(cur):
    """Apply migration"""
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    # USERS TABLE - Core user data and trading settings
    # ═══════════════════════════════════════════════════════════════════════════════════
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id            BIGINT PRIMARY KEY,
            
            -- Legacy API keys (deprecated, use demo/real keys)
            api_key            TEXT,
            api_secret         TEXT,
            
            -- Demo/Real API keys (Bybit)
            demo_api_key       TEXT,
            demo_api_secret    TEXT,
            real_api_key       TEXT,
            real_api_secret    TEXT,
            trading_mode       TEXT NOT NULL DEFAULT 'demo',
            
            -- Trading settings
            percent            REAL NOT NULL DEFAULT 1.0,
            coins              TEXT NOT NULL DEFAULT 'ALL',
            limit_enabled      INTEGER NOT NULL DEFAULT 1,
            trade_oi           INTEGER NOT NULL DEFAULT 1,
            trade_rsi_bb       INTEGER NOT NULL DEFAULT 1,
            tp_percent         REAL NOT NULL DEFAULT 8.0,
            sl_percent         REAL NOT NULL DEFAULT 3.0,
            use_atr            INTEGER NOT NULL DEFAULT 1,
            lang               TEXT NOT NULL DEFAULT 'en',
            leverage           INTEGER NOT NULL DEFAULT 10,
            
            -- Strategies
            trade_scryptomera  INTEGER NOT NULL DEFAULT 0,
            trade_scalper      INTEGER NOT NULL DEFAULT 0,
            trade_elcaro       INTEGER NOT NULL DEFAULT 0,
            trade_fibonacci    INTEGER NOT NULL DEFAULT 0,
            trade_manual       INTEGER NOT NULL DEFAULT 1,
            strategy_settings  TEXT,
            strategies_enabled TEXT,
            strategies_order   TEXT,
            
            -- Strategy thresholds
            rsi_lo             REAL,
            rsi_hi             REAL,
            bb_touch_k         REAL,
            oi_min_pct         REAL,
            price_min_pct      REAL,
            limit_only_default INTEGER NOT NULL DEFAULT 0,
            
            -- DCA settings
            dca_enabled        INTEGER NOT NULL DEFAULT 0,
            dca_pct_1          REAL NOT NULL DEFAULT 10.0,
            dca_pct_2          REAL NOT NULL DEFAULT 25.0,
            
            -- Access control
            is_allowed         INTEGER NOT NULL DEFAULT 0,
            is_banned          INTEGER NOT NULL DEFAULT 0,
            terms_accepted     INTEGER NOT NULL DEFAULT 0,
            guide_sent         INTEGER NOT NULL DEFAULT 0,
            
            -- HyperLiquid settings
            hl_enabled         BOOLEAN DEFAULT FALSE,
            hl_testnet         BOOLEAN DEFAULT FALSE,
            hl_private_key     TEXT,
            hl_wallet_address  TEXT,
            hl_vault_address   TEXT,
            hl_testnet_private_key     TEXT,
            hl_testnet_wallet_address  TEXT,
            hl_mainnet_private_key     TEXT,
            hl_mainnet_wallet_address  TEXT,
            
            -- Bybit settings
            bybit_enabled      INTEGER NOT NULL DEFAULT 1,
            exchange_type      TEXT NOT NULL DEFAULT 'bybit',
            exchange_mode      TEXT NOT NULL DEFAULT 'bybit',
            
            -- ATR settings
            atr_periods        INTEGER NOT NULL DEFAULT 7,
            atr_multiplier_sl  REAL NOT NULL DEFAULT 1.0,
            atr_trigger_pct    REAL NOT NULL DEFAULT 2.0,
            atr_step_pct       REAL NOT NULL DEFAULT 0.5,
            direction          TEXT NOT NULL DEFAULT 'all',
            global_order_type  TEXT NOT NULL DEFAULT 'market',
            
            -- Routing
            routing_policy     TEXT DEFAULT 'same_exchange_all_envs',
            live_enabled       INTEGER DEFAULT 0,
            
            -- License
            current_license    TEXT DEFAULT 'none',
            license_expires    BIGINT,
            license_type       TEXT,
            
            -- ELC Token
            elc_balance        REAL NOT NULL DEFAULT 0.0,
            elc_staked         REAL NOT NULL DEFAULT 0.0,
            elc_locked         REAL NOT NULL DEFAULT 0.0,
            
            -- User info
            username           TEXT,
            first_name         TEXT,
            last_name          TEXT,
            email              TEXT,
            referral_code      TEXT,
            referred_by        BIGINT,
            
            -- Spot trading
            spot_enabled       INTEGER NOT NULL DEFAULT 0,
            spot_settings      TEXT,
            
            -- Limit ladder
            limit_ladder_enabled  INTEGER NOT NULL DEFAULT 0,
            limit_ladder_count    INTEGER NOT NULL DEFAULT 3,
            limit_ladder_settings TEXT,
            
            -- Notifications
            notification_settings JSONB DEFAULT '{}',
            
            -- UI State
            last_viewed_account TEXT,  -- 'demo', 'real', 'testnet', 'mainnet' for UI persistence
            
            -- Timestamps
            first_seen_ts      BIGINT,
            last_seen_ts       BIGINT,
            updated_at         TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Users indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_allowed ON users(is_allowed)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_license ON users(current_license)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_referral ON users(referral_code)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS users CASCADE")
