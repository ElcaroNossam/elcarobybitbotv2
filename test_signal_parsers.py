#!/usr/bin/env python3
"""
Test all signal parsers to ensure they correctly identify their signals
and don't overlap with each other.
"""
import re
import sys
sys.path.insert(0, '.')

# Import parsers from bot.py
from bot import (
    parse_bitk_signal, is_bitk_signal,
    parse_rsi_bb_signal, is_rsi_bb_signal,
    parse_scalper_signal, is_scalper_signal,
    parse_elcaro_signal, is_elcaro_signal,
    parse_fibonacci_signal, is_fibonacci_signal,
    parse_oi_signal, is_oi_signal,
)

# Real signal examples from production logs
SIGNALS = {
    "RSI_BB": [
        """🟢 LONG MERLUSDT
📊 Score: 51% ⭐ C
📈 (BB:15 RSI:12 Vol:0 OI:0)
⏱ TF: 1h
💲 Entry: 0.17049000
🎯 TP1: 0.19270062 (3.0×ATR)
🎯 TP2: 0.20380592
🛑 SL: 0.15568292 (2.0×ATR)
📏 ATR: 0.00740354
📊 RSI(14): 15.7
🔼 BB Position: Below Lower""",
        """🔴 SHORT BTCUSDT
📊 Score: 65% ⭐ B
📈 (BB:20 RSI:85 Vol:5 OI:3)
⏱ TF: 4h
💲 Entry: 95000.00
🎯 TP1: 92000.00
🛑 SL: 97000.00""",
    ],
    
    "SCRYPTOMERA": [
        "SCRIPTOMER SHORT AVNTUSDT @ 0.2951",
        "SCRIPTOMER SHORT BIOUSDT @ 0.04783",
        "SCRIPTOMER LONG SOLUSDT @ 189.45",
    ],
    
    "SCALPER": [
        "SCALPER LONG BTCUSDT @ 95432.50",
        "SCALPER SHORT ETHUSDT @ 3200.00",
    ],
    
    "ELCARO": [
        """Enliko
🔔 SUSHIUSDT 📉 SHORT 🟢⚪⚪
⏱️ D | 🎚 65

💰 Entry: 0.314900
🛑 SL: 0.352004 (11.78%) [OB]
🎯 TP: 0.265429 (15.71%) [AGG]

📊 RR: 4.0:1 | ATR Exit:  ✅
📉 ATR: 14 | ×2.0 | Trigger: 18%""",
        """Enliko
🔔 BERAUSDT 📉 SHORT 🟢⚪⚪
⏱️ 120 | 🎚 72

💰 Entry: 0.917500
🛑 SL: 1.001843 (9.19%) [ATR]
🎯 TP: 0.805043 (12.26%) [AGG]

📊 RR: 3.0:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.5 | Trigger: 15%""",
        """Enliko
🔔 CAMPUSDT 📈 LONG 🟢⚪⚪
⏱️ 60 | 🎚 68

💰 Entry: 0.007205
🛑 SL: 0.007124 (1.12%) [OB]
🎯 TP: 0.007313 (1.49%) [AGG]

📊 RR: 3.5:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.5 | Trigger: 15%""",
    ],
    
    "FIBONACCI": [
        """📊 FIBONACCI EXTENSION STRATEGY

🪙 ADAUSDT | —
📉 SHORT

⏱ TF: 240
🎯 Entry Zone: 0.36442 – 0.37576
🛑 Stop Loss: 0.39700
✅ Target 1: 0.35452

⚡ Trigger: Price in 141.4%-161.8% zone
🟢 Quality: A (84/100)""",
        """📊 FIBONACCI EXTENSION STRATEGY

🪙 XMRUSDT | —
📈 LONG

⏱ TF: D
🎯 Entry Zone: 561.1324 – 640.5067
🛑 Stop Loss: 412.5000
✅ Target 1: 709.7648

⚡ Trigger: Price in 141.4%-161.8% zone
🟢 Quality: A (81/100)""",
    ],
    
    "OI": [
        """🎯 OI SIGNAL ⭐️⭐️⭐️⭐️
🚀 SQUEEZE (Сквиз шортов)
📈 LONG BTCUSDT @ 95432.50
📊 OI: +5.23% | Vol z=2.1 | CVD z=1.8
🎯 Score: 4.2""",
        """🎯 OI SIGNAL ⭐️⭐️⭐️
🩸 DUMP (Ликвидация лонгов)
📉 SHORT ETHUSDT @ 3200.00
📊 OI: -8.5% | Vol z=1.5 | CVD z=-2.3
🎯 Score: 3.8""",
    ],
}

def test_parser(name, is_func, parse_func, signal):
    """Test a single parser on a signal."""
    is_match = is_func(signal)
    parsed = parse_func(signal)
    return is_match, parsed

def main():
    print("=" * 70)
    print("SIGNAL PARSER TEST")
    print("=" * 70)
    
    all_parsers = [
        ("RSI_BB", is_rsi_bb_signal, parse_rsi_bb_signal),
        ("SCRYPTOMERA", is_bitk_signal, parse_bitk_signal),
        ("SCALPER", is_scalper_signal, parse_scalper_signal),
        ("ELCARO", is_elcaro_signal, parse_elcaro_signal),
        ("FIBONACCI", is_fibonacci_signal, parse_fibonacci_signal),
        ("OI", is_oi_signal, parse_oi_signal),
    ]
    
    errors = []
    
    for expected_strategy, signals in SIGNALS.items():
        print(f"\n{'='*70}")
        print(f"Testing {expected_strategy} signals ({len(signals)} examples)")
        print("=" * 70)
        
        for i, signal in enumerate(signals, 1):
            print(f"\n--- Example {i} ---")
            signal_preview = signal[:80].replace('\n', '\\n')
            print(f"Signal: {signal_preview}...")
            
            matches = []
            for parser_name, is_func, parse_func in all_parsers:
                is_match, parsed = test_parser(parser_name, is_func, parse_func, signal)
                if is_match:
                    matches.append(parser_name)
                    if parsed:
                        print(f"  ✅ {parser_name}: {parsed}")
                    else:
                        print(f"  ⚠️  {parser_name}: matched but parse returned None!")
            
            # Check for correct match
            if expected_strategy in matches:
                if len(matches) == 1:
                    print(f"  → PASS: Only {expected_strategy} matched")
                else:
                    # Multiple matches - could be a problem
                    other_matches = [m for m in matches if m != expected_strategy]
                    print(f"  → WARNING: Multiple matches: {matches}")
                    errors.append(f"{expected_strategy} signal also matched by: {other_matches}")
            else:
                print(f"  → FAIL: Expected {expected_strategy} but got {matches}")
                errors.append(f"{expected_strategy} signal not matched! (got: {matches})")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ {len(errors)} ERRORS FOUND:")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("\n✅ All parsers working correctly!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
