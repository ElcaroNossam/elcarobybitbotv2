"""
Migration: Unified Schema - Complete Database Structure
Version: 100

FULL PRODUCTION SCHEMA for Enliko Platform.
2 Exchanges: Bybit (demo/real) + HyperLiquid (testnet/mainnet)
7 Strategies: oi, scryptomera, scalper, elcaro, fibonacci, rsi_bb, manual
4D Multitenancy: (user_id, strategy, side, exchange)
"""


def upgrade(cur):
    """Apply migration - create all tables from scratch"""
    
    print("=" * 60)
    print("UNIFIED SCHEMA MIGRATION v100")
    print("Creating complete production database structure...")
    print("=" * 60)
    
    # 1. USERS TABLE
    cur.execute("DROP TABLE IF EXISTS users CASCADE")
    cur.execute("""
        CREATE TABLE users (
            user_id            BIGINT PRIMARY KEY,
            
            bybit_enabled       BOOLEAN DEFAULT TRUE,
            bybit_demo_api_key      TEXT,
            bybit_demo_api_secret   TEXT,
            bybit_real_api_key      TEXT,
            bybit_real_api_secret   TEXT,
            
            demo_api_key       TEXT,
            demo_api_secret    TEXT,
            real_api_key       TEXT,
            real_api_secret    TEXT,
            api_key            TEXT,
            api_secret         TEXT,
            
            hl_enabled          BOOLEAN DEFAULT FALSE,
            hl_testnet_private_key     TEXT,
            hl_testnet_wallet_address  TEXT,
            hl_mainnet_private_key     TEXT,
            hl_mainnet_wallet_address  TEXT,
            
            hl_private_key     TEXT,
            hl_wallet_address  TEXT,
            hl_vault_address   TEXT,
            hl_testnet         BOOLEAN DEFAULT FALSE,
            
            exchange_type      TEXT DEFAULT 'bybit',
            trading_mode       TEXT DEFAULT 'demo',
            routing_policy     TEXT,
            live_enabled       BOOLEAN DEFAULT FALSE,
            
            percent            REAL DEFAULT 1.0,
            tp_percent         REAL DEFAULT 25.0,
            sl_percent         REAL DEFAULT 30.0,
            leverage           INTEGER DEFAULT 10,
            direction          TEXT DEFAULT 'all',
            
            order_type         TEXT DEFAULT 'market',
            limit_offset_pct   REAL DEFAULT 0.1,
            
            use_atr            BOOLEAN DEFAULT TRUE,
            atr_periods        INTEGER DEFAULT 7,
            atr_multiplier_sl  REAL DEFAULT 0.5,
            atr_trigger_pct    REAL DEFAULT 3.0,
            atr_step_pct       REAL DEFAULT 0.3,
            
            be_enabled         BOOLEAN DEFAULT FALSE,
            be_trigger_pct     REAL DEFAULT 1.0,
            
            dca_enabled        BOOLEAN DEFAULT FALSE,
            dca_pct_1          REAL DEFAULT 10.0,
            dca_pct_2          REAL DEFAULT 25.0,
            
            partial_tp_enabled BOOLEAN DEFAULT FALSE,
            partial_tp_1_trigger_pct REAL DEFAULT 2.0,
            partial_tp_1_close_pct   REAL DEFAULT 30.0,
            partial_tp_2_trigger_pct REAL DEFAULT 5.0,
            partial_tp_2_close_pct   REAL DEFAULT 50.0,
            
            coins              TEXT DEFAULT 'ALL',
            bybit_coins_group  TEXT DEFAULT 'ALL',
            hl_coins_group     TEXT DEFAULT 'ALL',
            
            trade_oi           BOOLEAN DEFAULT TRUE,
            trade_scryptomera  BOOLEAN DEFAULT FALSE,
            trade_scalper      BOOLEAN DEFAULT FALSE,
            trade_elcaro       BOOLEAN DEFAULT FALSE,
            trade_fibonacci    BOOLEAN DEFAULT FALSE,
            trade_rsi_bb       BOOLEAN DEFAULT TRUE,
            trade_manual       BOOLEAN DEFAULT TRUE,
            
            is_allowed         BOOLEAN DEFAULT FALSE,
            is_banned          BOOLEAN DEFAULT FALSE,
            current_license    TEXT DEFAULT 'none',
            license_type       TEXT,
            license_expires    BIGINT,
            
            username           TEXT,
            first_name         TEXT,
            last_name          TEXT,
            email              TEXT UNIQUE,
            password_hash      TEXT,
            password_salt      TEXT,
            telegram_id        BIGINT,
            telegram_username  TEXT,
            auth_provider      TEXT DEFAULT 'telegram',
            email_verified     BOOLEAN DEFAULT FALSE,
            last_login         TIMESTAMP,
            lang               TEXT DEFAULT 'en',
            
            terms_accepted     BOOLEAN DEFAULT FALSE,
            disclaimer_accepted BOOLEAN DEFAULT FALSE,
            
            referral_code      TEXT UNIQUE,
            referred_by        BIGINT,
            
            elc_balance        REAL DEFAULT 0.0,
            elc_staked         REAL DEFAULT 0.0,
            elc_locked         REAL DEFAULT 0.0,
            
            notification_settings    JSONB DEFAULT '{}',
            terminal_preferences     JSONB DEFAULT '{}',
            
            last_viewed_account TEXT,
            
            first_seen_ts      BIGINT,
            last_seen_ts       BIGINT,
            created_at         TIMESTAMP DEFAULT NOW(),
            updated_at         TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_allowed ON users(is_allowed)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_exchange ON users(exchange_type)")
    print("  [OK] Created users table")
    
    # 2. USER_STRATEGY_SETTINGS (4D schema)
    cur.execute("DROP TABLE IF EXISTS user_strategy_settings CASCADE")
    cur.execute("""
        CREATE TABLE user_strategy_settings (
            user_id       BIGINT NOT NULL,
            strategy      TEXT NOT NULL,
            side          TEXT NOT NULL,
            exchange      TEXT NOT NULL,
            
            enabled       BOOLEAN DEFAULT TRUE,
            
            percent       REAL,
            tp_percent    REAL,
            sl_percent    REAL,
            leverage      INTEGER,
            direction     TEXT DEFAULT 'all',
            
            order_type        TEXT DEFAULT 'market',
            limit_offset_pct  REAL DEFAULT 0.1,
            
            use_atr           BOOLEAN,
            atr_periods       INTEGER,
            atr_multiplier_sl REAL,
            atr_trigger_pct   REAL,
            atr_step_pct      REAL,
            
            be_enabled        BOOLEAN,
            be_trigger_pct    REAL,
            
            dca_enabled       BOOLEAN,
            dca_pct_1         REAL,
            dca_pct_2         REAL,
            
            partial_tp_enabled        BOOLEAN,
            partial_tp_1_trigger_pct  REAL,
            partial_tp_1_close_pct    REAL,
            partial_tp_2_trigger_pct  REAL,
            partial_tp_2_close_pct    REAL,
            
            max_positions INTEGER DEFAULT 0,
            
            trading_mode  TEXT,
            account_type  TEXT,
            
            settings      JSONB DEFAULT '{}',
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            PRIMARY KEY (user_id, strategy, side, exchange)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user ON user_strategy_settings(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_strategy ON user_strategy_settings(strategy)")
    print("  [OK] Created user_strategy_settings table (4D schema)")
    
    # 3. ACTIVE_POSITIONS
    cur.execute("DROP TABLE IF EXISTS active_positions CASCADE")
    cur.execute("""
        CREATE TABLE active_positions (
            user_id       BIGINT NOT NULL,
            symbol        TEXT NOT NULL,
            account_type  TEXT NOT NULL,
            exchange      TEXT NOT NULL DEFAULT 'bybit',
            
            side          TEXT NOT NULL,
            entry_price   REAL,
            size          REAL,
            qty           REAL,
            leverage      INTEGER,
            strategy      TEXT,
            
            sl_price      REAL,
            tp_price      REAL,
            applied_sl_pct REAL,
            applied_tp_pct REAL,
            
            use_atr              BOOLEAN DEFAULT FALSE,
            atr_activated        BOOLEAN DEFAULT FALSE,
            atr_activation_price REAL,
            atr_last_stop_price  REAL,
            atr_last_update_ts   BIGINT,
            
            dca_10_done   BOOLEAN DEFAULT FALSE,
            dca_25_done   BOOLEAN DEFAULT FALSE,
            dca_count     INTEGER DEFAULT 0,
            avg_entry     REAL,
            
            ptp_step_1_done BOOLEAN DEFAULT FALSE,
            ptp_step_2_done BOOLEAN DEFAULT FALSE,
            
            signal_id         INTEGER,
            client_order_id   TEXT,
            exchange_order_id TEXT,
            
            env           TEXT,
            timeframe     TEXT,
            source        TEXT DEFAULT 'bot',
            opened_by     TEXT DEFAULT 'bot',
            
            manual_sltp_override BOOLEAN DEFAULT FALSE,
            manual_sltp_ts       BIGINT,
            
            trailing_active   BOOLEAN DEFAULT FALSE,
            trailing_trigger  REAL,
            trailing_distance REAL,
            highest_pnl       REAL,
            
            current_price REAL,
            pnl           REAL,
            pnl_pct       REAL,
            
            open_ts       TIMESTAMP DEFAULT NOW(),
            opened_at     TIMESTAMP DEFAULT NOW(),
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            PRIMARY KEY (user_id, symbol, account_type, exchange)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ap_user ON active_positions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ap_exchange ON active_positions(exchange, account_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ap_symbol ON active_positions(symbol)")
    print("  [OK] Created active_positions table")
    
    # 4. TRADE_LOGS
    cur.execute("DROP TABLE IF EXISTS trade_logs CASCADE")
    cur.execute("""
        CREATE TABLE trade_logs (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            symbol        TEXT NOT NULL,
            side          TEXT,
            account_type  TEXT DEFAULT 'demo',
            exchange      TEXT DEFAULT 'bybit',
            
            entry_price   REAL,
            exit_price    REAL,
            exit_reason   TEXT,
            
            size          REAL,
            qty           REAL,
            leverage      INTEGER,
            strategy      TEXT,
            
            pnl           REAL,
            pnl_pct       REAL,
            
            sl_pct        REAL,
            tp_pct        REAL,
            
            rsi           REAL,
            bb_hi         REAL,
            bb_lo         REAL,
            vol_delta     REAL,
            oi_prev       REAL,
            oi_now        REAL,
            oi_chg        REAL,
            vol_from      REAL,
            vol_to        REAL,
            price_chg     REAL,
            
            timeframe     TEXT,
            source        TEXT DEFAULT 'bot',
            signal_id     INTEGER,
            
            ts            TIMESTAMP DEFAULT NOW(),
            opened_at     TIMESTAMP,
            closed_at     TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tl_user ON trade_logs(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tl_ts ON trade_logs(ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tl_user_ts ON trade_logs(user_id, ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tl_exchange ON trade_logs(exchange, account_type)")
    print("  [OK] Created trade_logs table")
    
    # 5. SIGNALS
    cur.execute("DROP TABLE IF EXISTS signals CASCADE")
    cur.execute("""
        CREATE TABLE signals (
            id            SERIAL PRIMARY KEY,
            symbol        TEXT NOT NULL,
            side          TEXT,
            strategy      TEXT,
            price         REAL,
            
            rsi           REAL,
            bb_hi         REAL,
            bb_lo         REAL,
            vol_delta     REAL,
            oi_prev       REAL,
            oi_now        REAL,
            oi_chg        REAL,
            vol_from      REAL,
            vol_to        REAL,
            price_chg     REAL,
            
            timeframe     TEXT,
            source        TEXT,
            raw_data      TEXT,
            
            ts            TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_ts ON signals(ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
    print("  [OK] Created signals table")
    
    # 6. PENDING_LIMIT_ORDERS
    cur.execute("DROP TABLE IF EXISTS pending_limit_orders CASCADE")
    cur.execute("""
        CREATE TABLE pending_limit_orders (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            symbol        TEXT NOT NULL,
            side          TEXT NOT NULL,
            account_type  TEXT DEFAULT 'demo',
            exchange      TEXT DEFAULT 'bybit',
            
            price         REAL,
            qty           REAL,
            order_type    TEXT DEFAULT 'limit',
            strategy      TEXT,
            
            order_id      TEXT,
            client_order_id TEXT,
            signal_id     INTEGER,
            
            status        TEXT DEFAULT 'pending',
            
            created_at    TIMESTAMP DEFAULT NOW(),
            expires_at    TIMESTAMP,
            filled_at     TIMESTAMP,
            updated_at    TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_plo_user ON pending_limit_orders(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_plo_status ON pending_limit_orders(status)")
    print("  [OK] Created pending_limit_orders table")
    
    # 7. EMAIL_USERS
    cur.execute("DROP TABLE IF EXISTS email_users CASCADE")
    cur.execute("""
        CREATE TABLE email_users (
            id            SERIAL PRIMARY KEY,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_id       BIGINT,
            telegram_id   BIGINT,
            
            is_verified   BOOLEAN DEFAULT FALSE,
            verification_code TEXT,
            verification_expires TIMESTAMP,
            
            twofa_enabled BOOLEAN DEFAULT FALSE,
            twofa_secret  TEXT,
            
            created_at    TIMESTAMP DEFAULT NOW(),
            last_login    TIMESTAMP
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_eu_email ON email_users(email)")
    print("  [OK] Created email_users table")
    
    # 8. LOGIN_TOKENS
    cur.execute("DROP TABLE IF EXISTS login_tokens CASCADE")
    cur.execute("""
        CREATE TABLE login_tokens (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            token         TEXT UNIQUE NOT NULL,
            device_info   TEXT,
            ip_address    TEXT,
            
            is_active     BOOLEAN DEFAULT TRUE,
            is_blacklisted BOOLEAN DEFAULT FALSE,
            
            created_at    TIMESTAMP DEFAULT NOW(),
            expires_at    TIMESTAMP,
            last_used     TIMESTAMP
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lt_token ON login_tokens(token)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lt_user ON login_tokens(user_id)")
    print("  [OK] Created login_tokens table")
    
    # 9. PAYMENT_HISTORY
    cur.execute("DROP TABLE IF EXISTS payment_history CASCADE")
    cur.execute("""
        CREATE TABLE payment_history (
            id                  SERIAL PRIMARY KEY,
            user_id             BIGINT NOT NULL,
            
            amount              REAL NOT NULL,
            currency            TEXT DEFAULT 'USD',
            payment_type        TEXT,
            license_type        TEXT,
            license_id          INTEGER,
            period_days         INTEGER,
            
            tx_hash             TEXT,
            transaction_id      TEXT,
            telegram_charge_id  TEXT,
            payment_method      TEXT,
            plan_type           TEXT,
            
            status              TEXT DEFAULT 'pending',
            
            created_at          TIMESTAMP DEFAULT NOW(),
            confirmed_at        TIMESTAMP,
            
            metadata            JSONB DEFAULT '{}'
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ph_user ON payment_history(user_id)")
    print("  [OK] Created payment_history table")
    
    # 10. USER_ACTIVITY_LOG
    cur.execute("DROP TABLE IF EXISTS user_activity_log CASCADE")
    cur.execute("""
        CREATE TABLE user_activity_log (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            action_type     TEXT NOT NULL,
            action_category TEXT,
            source          TEXT,
            
            entity_type     TEXT,
            entity_id       TEXT,
            
            old_value       JSONB,
            new_value       JSONB,
            
            telegram_notified BOOLEAN DEFAULT FALSE,
            webapp_notified   BOOLEAN DEFAULT FALSE,
            ios_notified      BOOLEAN DEFAULT FALSE,
            android_notified  BOOLEAN DEFAULT FALSE,
            
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ual_user ON user_activity_log(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ual_ts ON user_activity_log(created_at DESC)")
    print("  [OK] Created user_activity_log table")
    
    # 11. BACKTEST_RESULTS
    cur.execute("DROP TABLE IF EXISTS backtest_results CASCADE")
    cur.execute("""
        CREATE TABLE backtest_results (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT,
            
            strategy        TEXT,
            symbol          TEXT,
            timeframe       TEXT,
            
            start_date      DATE,
            end_date        DATE,
            
            total_trades    INTEGER,
            win_rate        REAL,
            profit_factor   REAL,
            max_drawdown    REAL,
            total_pnl       REAL,
            sharpe_ratio    REAL,
            
            parameters      JSONB,
            trades          JSONB,
            
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_br_user ON backtest_results(user_id)")
    print("  [OK] Created backtest_results table")
    
    # 12. ELC TOKEN TABLES
    cur.execute("DROP TABLE IF EXISTS elc_transactions CASCADE")
    cur.execute("""
        CREATE TABLE elc_transactions (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            
            tx_type       TEXT NOT NULL,
            amount        REAL NOT NULL,
            
            tx_hash       TEXT,
            status        TEXT DEFAULT 'pending',
            
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("DROP TABLE IF EXISTS connected_wallets CASCADE")
    cur.execute("""
        CREATE TABLE connected_wallets (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            wallet_address TEXT NOT NULL,
            chain         TEXT DEFAULT 'ethereum',
            is_primary    BOOLEAN DEFAULT FALSE,
            
            created_at    TIMESTAMP DEFAULT NOW(),
            
            UNIQUE(user_id, wallet_address)
        )
    """)
    print("  [OK] Created ELC token tables")
    
    # 13. MARKETPLACE TABLES
    cur.execute("DROP TABLE IF EXISTS strategy_marketplace CASCADE")
    cur.execute("""
        CREATE TABLE strategy_marketplace (
            id              SERIAL PRIMARY KEY,
            creator_id      BIGINT NOT NULL,
            
            name            TEXT NOT NULL,
            description     TEXT,
            strategy_type   TEXT,
            
            price           REAL DEFAULT 0,
            currency        TEXT DEFAULT 'USD',
            
            subscribers     INTEGER DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            win_rate        REAL,
            
            settings        JSONB,
            is_active       BOOLEAN DEFAULT TRUE,
            is_public       BOOLEAN DEFAULT TRUE,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("DROP TABLE IF EXISTS strategy_purchases CASCADE")
    cur.execute("""
        CREATE TABLE strategy_purchases (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            strategy_id     INTEGER NOT NULL,
            
            price_paid      REAL,
            
            is_active       BOOLEAN DEFAULT TRUE,
            
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    print("  [OK] Created marketplace tables")
    
    # 14. NOTIFICATION_QUEUE
    cur.execute("DROP TABLE IF EXISTS notification_queue CASCADE")
    cur.execute("""
        CREATE TABLE notification_queue (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            notification_type TEXT NOT NULL,
            title           TEXT,
            message         TEXT,
            data            JSONB,
            
            send_telegram   BOOLEAN DEFAULT TRUE,
            send_push       BOOLEAN DEFAULT FALSE,
            send_email      BOOLEAN DEFAULT FALSE,
            
            is_sent         BOOLEAN DEFAULT FALSE,
            is_read         BOOLEAN DEFAULT FALSE,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            sent_at         TIMESTAMP,
            read_at         TIMESTAMP
        )
    """)
    print("  [OK] Created notification_queue table")
    
    # 15. USER_DEVICES
    cur.execute("DROP TABLE IF EXISTS user_devices CASCADE")
    cur.execute("""
        CREATE TABLE user_devices (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            device_token    TEXT NOT NULL,
            device_type     TEXT,
            device_name     TEXT,
            
            is_active       BOOLEAN DEFAULT TRUE,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            last_seen       TIMESTAMP,
            
            UNIQUE(user_id, device_token)
        )
    """)
    print("  [OK] Created user_devices table")
    
    # 16. CRYPTO_PAYMENTS
    cur.execute("DROP TABLE IF EXISTS crypto_payments CASCADE")
    cur.execute("""
        CREATE TABLE crypto_payments (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            payment_id      TEXT UNIQUE NOT NULL,
            oxapay_id       TEXT,
            
            amount_usd      DECIMAL(10,2) NOT NULL,
            amount_crypto   DECIMAL(18,8),
            currency        TEXT NOT NULL,
            network         TEXT,
            address         TEXT,
            
            tx_hash         TEXT,
            status          TEXT DEFAULT 'pending',
            
            plan            TEXT NOT NULL,
            duration        TEXT NOT NULL,
            
            promo_code      TEXT,
            discount_percent DECIMAL(5,2) DEFAULT 0,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            confirmed_at    TIMESTAMP,
            expires_at      TIMESTAMP
        )
    """)
    print("  [OK] Created crypto_payments table")
    
    # 17. PROMO_CODES
    cur.execute("DROP TABLE IF EXISTS promo_codes CASCADE")
    cur.execute("""
        CREATE TABLE promo_codes (
            id              SERIAL PRIMARY KEY,
            code            TEXT UNIQUE NOT NULL,
            
            discount_percent DECIMAL(5,2) NOT NULL,
            max_uses        INTEGER,
            current_uses    INTEGER DEFAULT 0,
            
            valid_from      TIMESTAMP DEFAULT NOW(),
            valid_until     TIMESTAMP,
            
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("DROP TABLE IF EXISTS promo_code_usage CASCADE")
    cur.execute("""
        CREATE TABLE promo_code_usage (
            id              SERIAL PRIMARY KEY,
            promo_id        INTEGER,
            user_id         BIGINT,
            payment_id      TEXT,
            
            used_at         TIMESTAMP DEFAULT NOW()
        )
    """)
    print("  [OK] Created promo_codes tables")
    
    # 18. MIGRATIONS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id          SERIAL PRIMARY KEY,
            version     TEXT NOT NULL UNIQUE,
            name        TEXT NOT NULL,
            applied_at  TIMESTAMP DEFAULT NOW(),
            checksum    TEXT
        )
    """)
    print("  [OK] Created _migrations table")
    
    print("=" * 60)
    print("UNIFIED SCHEMA MIGRATION COMPLETE!")
    print("=" * 60)


def downgrade(cur):
    """Rollback migration - drop all tables"""
    tables = [
        'promo_code_usage', 'promo_codes', 'crypto_payments',
        'user_devices', 'notification_queue', 'strategy_purchases',
        'strategy_marketplace', 'connected_wallets', 'elc_transactions',
        'backtest_results', 'user_activity_log', 'payment_history',
        'login_tokens', 'email_users', 'pending_limit_orders',
        'signals', 'trade_logs', 'active_positions',
        'user_strategy_settings', 'users', '_migrations'
    ]
    
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"  [OK] Dropped {table}")
