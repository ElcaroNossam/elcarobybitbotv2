"""
Migration: Upgrade Strategy Settings to 3D Schema (user_id, strategy, side)
Version: 016
Created: 2026-01-23

Adds 'side' column and changes PRIMARY KEY from (user_id, strategy) to (user_id, strategy, side).
Migrates existing data by duplicating each row for 'long' and 'short' sides.
"""
import json


def upgrade(cur):
    """Apply migration - convert to 3D schema with side column"""
    import psycopg2.extras
    
    # Step 1: Add side column if not exists
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS side TEXT DEFAULT 'long'
    """)
    
    # Step 2: Add all required columns that might be missing
    columns_to_add = [
        ("percent", "REAL"),
        ("sl_percent", "REAL"),
        ("tp_percent", "REAL"),
        ("leverage", "INTEGER"),
        ("use_atr", "BOOLEAN DEFAULT FALSE"),
        ("atr_periods", "INTEGER"),
        ("atr_multiplier_sl", "REAL"),
        ("atr_trigger_pct", "REAL"),
        ("atr_step_pct", "REAL"),
        ("order_type", "TEXT DEFAULT 'market'"),
        ("direction", "TEXT DEFAULT 'all'"),
        ("enabled", "BOOLEAN DEFAULT TRUE"),
        ("limit_offset_pct", "REAL DEFAULT 0.1"),
        ("dca_enabled", "BOOLEAN DEFAULT FALSE"),
        ("dca_pct_1", "REAL DEFAULT 10.0"),
        ("dca_pct_2", "REAL DEFAULT 25.0"),
        ("max_positions", "INTEGER DEFAULT 0"),
        ("coins_group", "TEXT DEFAULT 'ALL'"),
        ("trading_mode", "TEXT DEFAULT 'demo'"),
        ("exchange", "TEXT DEFAULT 'bybit'"),
        ("account_type", "TEXT DEFAULT 'demo'"),
        ("updated_at", "TIMESTAMP DEFAULT NOW()"),
    ]
    
    for col_name, col_type in columns_to_add:
        cur.execute(f"""
            ALTER TABLE user_strategy_settings 
            ADD COLUMN IF NOT EXISTS {col_name} {col_type}
        """)
    
    # Step 3: Get existing data before changing PK
    cur.execute("SELECT * FROM user_strategy_settings")
    existing_rows = cur.fetchall()
    
    # Step 4: Drop old constraint and create new one
    # First drop the old primary key
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        DROP CONSTRAINT IF EXISTS user_strategy_settings_pkey
    """)
    
    # Step 5: Migrate data - for each existing row, create both long and short entries
    for row in existing_rows:
        user_id = row[0]  # user_id
        strategy = row[1]  # strategy
        
        # Check if settings JSON has per-side data (could be dict from psycopg2)
        settings_raw = row[2] if len(row) > 2 else None
        # Convert dict to JSON string for JSONB column
        if isinstance(settings_raw, dict):
            settings_json = json.dumps(settings_raw)
        elif settings_raw is None:
            settings_json = '{}'
        else:
            settings_json = str(settings_raw)
        
        # For each side, insert/update
        for side in ['long', 'short']:
            cur.execute("""
                INSERT INTO user_strategy_settings 
                    (user_id, strategy, side, percent, sl_percent, tp_percent, leverage,
                     use_atr, atr_trigger_pct, atr_step_pct, order_type, direction,
                     enabled, limit_offset_pct, dca_enabled, dca_pct_1, dca_pct_2,
                     max_positions, coins_group, trading_mode, exchange, account_type, settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                user_id, strategy, side,
                row[3] if len(row) > 3 else None,   # percent
                row[4] if len(row) > 4 else None,   # sl_percent
                row[5] if len(row) > 5 else None,   # leverage (old schema) or sl_percent
                row[6] if len(row) > 6 else None,   # leverage
                row[7] if len(row) > 7 else False,  # use_atr
                row[8] if len(row) > 8 else None,   # atr_trigger_pct
                row[9] if len(row) > 9 else None,   # atr_step_pct
                row[10] if len(row) > 10 else 'market',  # order_type
                row[11] if len(row) > 11 else 'all',     # direction
                row[12] if len(row) > 12 else True,      # enabled
                row[13] if len(row) > 13 else 0.1,       # limit_offset_pct
                row[14] if len(row) > 14 else False,     # dca_enabled
                row[15] if len(row) > 15 else 10.0,      # dca_pct_1
                row[16] if len(row) > 16 else 25.0,      # dca_pct_2
                row[17] if len(row) > 17 else 0,         # max_positions
                row[18] if len(row) > 18 else 'ALL',     # coins_group
                row[19] if len(row) > 19 else 'demo',    # trading_mode
                row[20] if len(row) > 20 else 'bybit',   # exchange
                row[21] if len(row) > 21 else 'demo',    # account_type
                settings_json
            ))
    
    # Step 6: Remove old rows without side (they have default 'long')
    # Actually, after adding the column with default, they all have 'long'
    # We need to delete duplicates and keep only the new structure
    
    # Step 7: Add NOT NULL constraint to side
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ALTER COLUMN side SET NOT NULL
    """)
    
    # Step 8: Create new primary key with 3D schema
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD CONSTRAINT user_strategy_settings_pkey PRIMARY KEY (user_id, strategy, side)
    """)
    
    # Step 9: Add useful indexes
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_strategy_settings_user 
        ON user_strategy_settings(user_id)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_strategy_settings_strategy 
        ON user_strategy_settings(strategy)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_strategy_settings_side 
        ON user_strategy_settings(user_id, strategy, side)
    """)


def downgrade(cur):
    """Rollback migration - convert back to 2D schema"""
    
    # Drop the 3D primary key
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        DROP CONSTRAINT IF EXISTS user_strategy_settings_pkey
    """)
    
    # Keep only 'long' rows
    cur.execute("""
        DELETE FROM user_strategy_settings WHERE side = 'short'
    """)
    
    # Drop side column
    cur.execute("""
        ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS side
    """)
    
    # Recreate 2D primary key
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD CONSTRAINT user_strategy_settings_pkey PRIMARY KEY (user_id, strategy)
    """)
