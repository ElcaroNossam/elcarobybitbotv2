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
    
    # Step 1: Add all required columns that might be missing
    columns_to_add = [
        ("percent", "REAL"),
        ("tp_percent", "REAL"),
        ("sl_percent", "REAL"),
        ("leverage", "INTEGER"),
        ("use_atr", "BOOLEAN DEFAULT FALSE"),
        ("atr_periods", "INTEGER"),
        ("atr_multiplier_sl", "REAL"),
        ("atr_trigger_pct", "REAL"),
        ("atr_step_pct", "REAL"),
        ("order_type", "TEXT DEFAULT 'market'"),
        ("limit_offset_pct", "REAL DEFAULT 0.1"),
        ("direction", "TEXT DEFAULT 'all'"),
        ("dca_enabled", "BOOLEAN DEFAULT FALSE"),
        ("dca_pct_1", "REAL DEFAULT 10.0"),
        ("dca_pct_2", "REAL DEFAULT 25.0"),
        ("max_positions", "INTEGER DEFAULT 0"),
        ("coins_group", "TEXT DEFAULT 'ALL'"),
        ("trading_mode", "TEXT DEFAULT 'demo'"),
        ("exchange", "TEXT DEFAULT 'bybit'"),
        ("account_type", "TEXT DEFAULT 'demo'"),
        ("enabled", "BOOLEAN DEFAULT TRUE"),
        ("updated_at", "TIMESTAMP DEFAULT NOW()"),
    ]
    
    for col_name, col_type in columns_to_add:
        cur.execute(f"""
            ALTER TABLE user_strategy_settings 
            ADD COLUMN IF NOT EXISTS {col_name} {col_type}
        """)
    
    # Step 2: Get existing data before changing PK
    # Use explicit columns to avoid ordering issues
    cur.execute("""
        SELECT user_id, strategy, settings, 
               percent, tp_percent, sl_percent, leverage,
               use_atr, atr_trigger_pct, atr_step_pct, order_type,
               direction, enabled, limit_offset_pct, dca_enabled,
               dca_pct_1, dca_pct_2, max_positions, coins_group,
               trading_mode, exchange, account_type
        FROM user_strategy_settings
    """)
    existing_rows = cur.fetchall()
    
    # Step 3: Add side column if not exists
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS side TEXT DEFAULT 'long'
    """)
    
    # Step 4: Drop old constraint and create new one
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        DROP CONSTRAINT IF EXISTS user_strategy_settings_pkey
    """)
    
    # Step 5: Clear existing data (will be re-inserted with side)
    cur.execute("DELETE FROM user_strategy_settings")
    
    # Step 6: Re-insert data with both long and short sides
    for row in existing_rows:
        user_id = row[0]
        strategy = row[1]
        settings_raw = row[2]
        
        # Convert dict to JSON string for JSONB column
        if isinstance(settings_raw, dict):
            settings_json = json.dumps(settings_raw)
        elif settings_raw is None:
            settings_json = '{}'
        else:
            settings_json = str(settings_raw)
        
        # For each side, insert
        for side in ['long', 'short']:
            cur.execute("""
                INSERT INTO user_strategy_settings 
                    (user_id, strategy, side, settings, 
                     percent, tp_percent, sl_percent, leverage,
                     use_atr, atr_trigger_pct, atr_step_pct, order_type,
                     direction, enabled, limit_offset_pct, dca_enabled,
                     dca_pct_1, dca_pct_2, max_positions, coins_group,
                     trading_mode, exchange, account_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, strategy, side, settings_json,
                row[3],   # percent
                row[4],   # tp_percent
                row[5],   # sl_percent
                row[6],   # leverage
                row[7] if row[7] is not None else False,  # use_atr
                row[8],   # atr_trigger_pct
                row[9],   # atr_step_pct
                row[10] if row[10] else 'market',  # order_type
                row[11] if row[11] else 'all',     # direction
                row[12] if row[12] is not None else True,  # enabled
                row[13] if row[13] is not None else 0.1,   # limit_offset_pct
                row[14] if row[14] is not None else False, # dca_enabled
                row[15] if row[15] is not None else 10.0,  # dca_pct_1
                row[16] if row[16] is not None else 25.0,  # dca_pct_2
                row[17] if row[17] is not None else 0,     # max_positions
                row[18] if row[18] else 'ALL',     # coins_group
                row[19] if row[19] else 'demo',    # trading_mode
                row[20] if row[20] else 'bybit',   # exchange
                row[21] if row[21] else 'demo',    # account_type
            ))
    
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
