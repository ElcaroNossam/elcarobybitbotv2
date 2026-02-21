"""
Migration: Dynamic Signal Parsers for Admin-defined Strategies
Version: 025
Created: 2026-02-21

Creates tables for:
- dynamic_signal_parsers: Admin-defined signal parsers with regex patterns
- user_strategy_deployments: User's deployed strategies from backtest
"""


def upgrade(cur):
    """Apply migration"""
    
    # Dynamic Signal Parsers - Admin can add new strategies by defining signal patterns
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_signal_parsers (
            id              SERIAL PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            display_name    TEXT NOT NULL,
            description     TEXT,
            
            -- Signal source
            channel_ids     TEXT,           -- Comma-separated Telegram channel IDs (NULL = all channels)
            
            -- Regex patterns for parsing
            signal_pattern  TEXT NOT NULL,  -- Main regex to identify this signal type
            symbol_pattern  TEXT,           -- Regex to extract symbol (default: [A-Z0-9]+USDT)
            side_pattern    TEXT,           -- Regex to extract side (default: LONG|SHORT|BUY|SELL)
            price_pattern   TEXT,           -- Regex to extract entry price
            
            -- Example for reference
            example_signal  TEXT,
            
            -- Base strategy to use for trading logic
            base_strategy   TEXT DEFAULT 'momentum',  -- Which built-in strategy logic to use
            
            -- Default settings (can be overridden by user)
            default_settings JSONB DEFAULT '{}',
            
            -- Status
            is_active       BOOLEAN DEFAULT TRUE,
            is_system       BOOLEAN DEFAULT FALSE,    -- TRUE = cannot be deleted
            
            -- Tracking
            created_by      BIGINT,
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW(),
            
            -- Stats
            signals_parsed  INTEGER DEFAULT 0,
            last_signal_at  TIMESTAMP
        )
    """)
    
    # User Strategy Deployments - User's personal strategies from backtest
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_strategy_deployments (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            -- Strategy source
            source_type     TEXT NOT NULL,   -- 'backtest', 'custom', 'marketplace'
            source_id       INTEGER,         -- ID from source table
            
            -- Strategy config
            name            TEXT NOT NULL,
            description     TEXT,
            base_strategy   TEXT NOT NULL,   -- Built-in strategy to extend
            config_json     JSONB DEFAULT '{}',
            
            -- Trading settings (overrides global user settings)
            entry_percent       REAL,
            stop_loss_percent   REAL,
            take_profit_percent REAL,
            leverage            INTEGER,
            use_atr             BOOLEAN DEFAULT FALSE,
            atr_multiplier      REAL,
            dca_enabled         BOOLEAN DEFAULT FALSE,
            dca_percent_1       REAL,
            dca_percent_2       REAL,
            be_enabled          BOOLEAN DEFAULT FALSE,
            be_trigger_pct      REAL,
            partial_tp_enabled  BOOLEAN DEFAULT FALSE,
            ptp_1_trigger_pct   REAL,
            ptp_1_close_pct     REAL,
            ptp_2_trigger_pct   REAL,
            ptp_2_close_pct     REAL,
            
            -- Filters
            direction           TEXT DEFAULT 'all',  -- 'all', 'long', 'short'
            coins_group         TEXT DEFAULT 'ALL',
            max_positions       INTEGER DEFAULT 0,
            
            -- Exchange settings
            exchange            TEXT DEFAULT 'bybit',
            account_type        TEXT DEFAULT 'demo',
            
            -- Status
            is_active           BOOLEAN DEFAULT TRUE,
            is_live             BOOLEAN DEFAULT FALSE,  -- TRUE = actively trading
            
            -- Performance tracking
            total_trades        INTEGER DEFAULT 0,
            winning_trades      INTEGER DEFAULT 0,
            total_pnl           REAL DEFAULT 0,
            win_rate            REAL DEFAULT 0,
            
            -- Timestamps
            created_at          TIMESTAMP DEFAULT NOW(),
            updated_at          TIMESTAMP DEFAULT NOW(),
            last_trade_at       TIMESTAMP,
            
            -- Backtest results for reference
            backtest_results    JSONB,
            
            UNIQUE(user_id, name)
        )
    """)
    
    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dsp_active ON dynamic_signal_parsers(is_active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_user ON user_strategy_deployments(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_active ON user_strategy_deployments(user_id, is_active)")
    
    # Insert system strategies as dynamic parsers (for reference and potential override)
    # These are the built-in strategies that can be managed through the admin interface
    cur.execute("""
        INSERT INTO dynamic_signal_parsers (name, display_name, description, signal_pattern, base_strategy, is_system, is_active)
        VALUES 
        ('scryptomera', 'Scryptomera', 'BiTK Scryptomera signals', '(?:Coin|Symbol)\\s*:\\s*[A-Z]+USDT', 'scryptomera', TRUE, TRUE),
        ('rsi_bb', 'RSI + BB', 'RSI and Bollinger Bands signals', 'RSI_BB_OI\\s+STRATEGY', 'rsi_bb', TRUE, TRUE),
        ('scalper', 'Scalper', 'Quick scalping signals', 'Scalper\\s+v\\d', 'scalper', TRUE, TRUE),
        ('elcaro', 'Elcaro', 'Elcaro strategy signals', '(?:ELCARO|PRE-ALERT).*?(?:LONG|SHORT)', 'elcaro', TRUE, TRUE),
        ('fibonacci', 'Fibonacci', 'Fibonacci extension signals', 'Fibonacci\\s+Extension\\s+Strategy', 'fibonacci', TRUE, TRUE),
        ('oi', 'Open Interest', 'OI strategy signals', 'OI\\s+Strategy\\s+v\\d', 'oi', TRUE, TRUE)
        ON CONFLICT (name) DO UPDATE SET updated_at = NOW()
    """)


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_strategy_deployments CASCADE")
    cur.execute("DROP TABLE IF EXISTS dynamic_signal_parsers CASCADE")
