#!/usr/bin/env python3
"""
Fix manual trades that have signal_id - detect correct strategy from signal.

This fixes trades that were incorrectly recorded as "manual" when they should have
been attributed to a specific strategy (rsi_bb, fibonacci, etc.)

The issue occurs when:
1. Bot restarts while positions are open
2. Monitor detects "new" position on exchange (not in DB)
3. Position is saved with strategy="manual" 
4. When position closes, trade_log gets strategy="manual" despite having signal_id
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import get_conn

# Signal detection functions (same as in bot.py)
def is_rsi_bb_signal(text: str) -> bool:
    """Detect RSI_BB signals by Score pattern."""
    if not text:
        return False
    # RSI_BB signals have pattern: "📊 Score: XX%" and "(BB:XX RSI:XX"
    return bool(re.search(r'📊\s*Score:\s*\d+%', text) and re.search(r'\(BB:\d+\s+RSI:\d+', text))

def is_fibonacci_signal(text: str) -> bool:
    """Detect Fibonacci signals."""
    if not text:
        return False
    upper = text.upper()
    return "FIBONACCI" in upper or "FIBONACCI EXTENSION" in upper or "FIBO EXTENSION" in upper

def is_bitk_signal(text: str) -> bool:
    """Detect Scryptomera/BiTK signals."""
    if not text:
        return False
    upper = text.upper()
    return ("DROP CATCH" in text or "DROPSBOT" in upper or 
            "TIGHTBTC" in upper or "SCRYPTOMERA" in upper or
            "BiTK" in text)

def is_scalper_signal(text: str) -> bool:
    """Detect Scalper signals."""
    if not text:
        return False
    upper = text.upper()
    return "SCALPER" in upper and "⚡" in text

def is_elcaro_signal(text: str) -> bool:
    """Detect Elcaro signals."""
    if not text:
        return False
    upper = text.upper()
    return "ELCARO" in upper or "🔥 ELCARO" in text or "🚀 ELCARO" in text

def is_oi_signal(text: str) -> bool:
    """Detect OI signals."""
    if not text:
        return False
    upper = text.upper()
    return "OI SIGNAL" in upper or "🎯 OI" in text

def detect_strategy(raw_message: str) -> str:
    """Detect strategy from signal message."""
    if not raw_message:
        return "manual"
    
    # Check in order of specificity
    if is_rsi_bb_signal(raw_message):
        return "rsi_bb"
    elif is_fibonacci_signal(raw_message):
        return "fibonacci"
    elif is_bitk_signal(raw_message):
        return "scryptomera"
    elif is_scalper_signal(raw_message):
        return "scalper"
    elif is_elcaro_signal(raw_message):
        return "elcaro"
    elif is_oi_signal(raw_message):
        return "oi"
    
    return "manual"


def fix_manual_trades_with_signal():
    """Fix trade_logs where strategy=manual but signal_id exists."""
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Find all manual trades with signal_id
        cur.execute("""
            SELECT t.id, t.user_id, t.symbol, t.signal_id, s.raw_message
            FROM trade_logs t
            JOIN signals s ON t.signal_id = s.id
            WHERE t.strategy = 'manual'
              AND t.signal_id IS NOT NULL
        """)
        rows = cur.fetchall()
        
        print(f"Found {len(rows)} manual trades with signal_id to fix")
        
        fixed_count = 0
        strategy_counts = {}
        
        for row in rows:
            trade_id, user_id, symbol, signal_id, raw_message = row
            
            detected = detect_strategy(raw_message)
            
            if detected != "manual":
                cur.execute("""
                    UPDATE trade_logs 
                    SET strategy = %s
                    WHERE id = %s
                """, (detected, trade_id))
                
                fixed_count += 1
                strategy_counts[detected] = strategy_counts.get(detected, 0) + 1
                
                if fixed_count <= 10:
                    preview = (raw_message or "")[:60].replace("\n", " ")
                    print(f"  Fixed trade {trade_id}: {symbol} → {detected}")
                    print(f"    Signal: {preview}...")
        
        conn.commit()
        
        print(f"\n✅ Fixed {fixed_count} trades")
        print("Strategy breakdown:")
        for strat, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
            print(f"  {strat}: {count}")
        
        # Count remaining manual trades
        cur.execute("""
            SELECT COUNT(*) FROM trade_logs WHERE strategy = 'manual'
        """)
        remaining = cur.fetchone()[0]
        print(f"\nRemaining manual trades (legitimate): {remaining}")


if __name__ == "__main__":
    fix_manual_trades_with_signal()
