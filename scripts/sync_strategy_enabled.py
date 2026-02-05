#!/usr/bin/env python3
"""
Sync script to align trade_* fields in users table with {side}_enabled in user_strategy_settings.

This fixes the dual-system mismatch where:
- users.trade_X was used for global strategy toggle
- user_strategy_settings.{side}_enabled was used for per-side toggle

After this fix, both systems should stay in sync.

Run this AFTER deploying the bot.py fix to production.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import get_conn

# Strategy name to trade_* field mapping
STRATEGY_FIELD_MAP = {
    "oi": "trade_oi",
    "rsi_bb": "trade_rsi_bb",
    "scryptomera": "trade_scryptomera",
    "scalper": "trade_scalper",
    "elcaro": "trade_elcaro",
    "fibonacci": "trade_fibonacci",
}


def sync_strategy_settings():
    """Sync trade_* fields with user_strategy_settings.{side}_enabled."""
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Get all users with their trade_* settings
        cur.execute("""
            SELECT user_id, trade_oi, trade_rsi_bb, trade_scryptomera, 
                   trade_scalper, trade_elcaro, trade_fibonacci
            FROM users
            WHERE is_allowed = 1 OR is_allowed = TRUE
        """)
        users = cur.fetchall()
        
        print(f"Found {len(users)} active users to sync")
        
        for user in users:
            user_id = user[0]
            trade_settings = {
                "oi": bool(user[1]),
                "rsi_bb": bool(user[2]),
                "scryptomera": bool(user[3]),
                "scalper": bool(user[4]),
                "elcaro": bool(user[5]),
                "fibonacci": bool(user[6]),
            }
            
            print(f"\n=== User {user_id} ===")
            print(f"  trade_* settings: {trade_settings}")
            
            # Get existing strategy settings
            cur.execute("""
                SELECT strategy, side, enabled, exchange
                FROM user_strategy_settings
                WHERE user_id = %s
            """, (user_id,))
            strategy_settings = cur.fetchall()
            
            # Build a map of existing settings
            existing = {}
            for row in strategy_settings:
                key = (row[0], row[1], row[3])  # (strategy, side, exchange)
                existing[key] = bool(row[2])
            
            changes_made = 0
            
            for strategy, trade_enabled in trade_settings.items():
                # Check existing side settings
                long_key = (strategy, "long", "bybit")
                short_key = (strategy, "short", "bybit")
                
                long_enabled = existing.get(long_key)
                short_enabled = existing.get(short_key)
                
                print(f"  {strategy}: trade_={trade_enabled}, long={long_enabled}, short={short_enabled}")
                
                # If trade_* is OFF but side_enabled is ON, we need to sync
                # Authoritative source should be trade_* since that's what the main toggle uses
                
                if not trade_enabled:
                    # Strategy is OFF globally - both sides should be disabled
                    if long_enabled is not None and long_enabled:
                        cur.execute("""
                            UPDATE user_strategy_settings 
                            SET enabled = FALSE
                            WHERE user_id = %s AND strategy = %s AND side = 'long'
                        """, (user_id, strategy))
                        print(f"    → Disabled long (was enabled but trade_* is OFF)")
                        changes_made += 1
                    
                    if short_enabled is not None and short_enabled:
                        cur.execute("""
                            UPDATE user_strategy_settings 
                            SET enabled = FALSE
                            WHERE user_id = %s AND strategy = %s AND side = 'short'
                        """, (user_id, strategy))
                        print(f"    → Disabled short (was enabled but trade_* is OFF)")
                        changes_made += 1
                
                elif trade_enabled:
                    # Strategy is ON globally
                    # If no side settings exist, both sides should be enabled
                    # If side settings exist but both are OFF, at least one should be ON
                    
                    if long_enabled is None and short_enabled is None:
                        # No settings exist - create default enabled settings
                        for side in ["long", "short"]:
                            cur.execute("""
                                INSERT INTO user_strategy_settings (user_id, strategy, side, enabled, exchange)
                                VALUES (%s, %s, %s, TRUE, 'bybit')
                                ON CONFLICT (user_id, strategy, side, exchange) DO UPDATE SET enabled = TRUE
                            """, (user_id, strategy, side))
                            print(f"    → Created/enabled {side} (trade_* is ON)")
                            changes_made += 1
                    
                    elif long_enabled is False and short_enabled is False:
                        # Both sides are OFF but trade_* is ON - mismatch!
                        # Enable both to match trade_*
                        cur.execute("""
                            UPDATE user_strategy_settings 
                            SET enabled = TRUE
                            WHERE user_id = %s AND strategy = %s
                        """, (user_id, strategy))
                        print(f"    → Enabled both sides (trade_* is ON but both were OFF)")
                        changes_made += 1
            
            if changes_made > 0:
                print(f"  ✅ Made {changes_made} changes for user {user_id}")
        
        conn.commit()
        print("\n✅ Sync completed!")


if __name__ == "__main__":
    sync_strategy_settings()
