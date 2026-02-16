#!/usr/bin/env python3
"""Translation audit script - compare all language files against en.py reference."""
import ast
import sys
import os

def extract_keys_and_values(filepath):
    """Extract keys and values from TEXTS dict in a translation file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'TEXTS':
                    if isinstance(node.value, ast.Dict):
                        result = {}
                        for k, v in zip(node.value.keys, node.value.values):
                            if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                                result[k.value] = v.value
                        return result
    return {}

base = 'translations'
en = extract_keys_and_values(os.path.join(base, 'en.py'))
print(f"=== EN REFERENCE: {len(en)} keys ===\n")

langs = ['ru','uk','de','es','fr','it','ja','zh','ar','he','pl','cs','lt','sq']

for lang in langs:
    fp = os.path.join(base, f'{lang}.py')
    try:
        data = extract_keys_and_values(fp)
    except Exception as e:
        print(f"[{lang.upper()}] ERROR: {e}")
        continue
    
    missing = sorted(set(en.keys()) - set(data.keys()))
    extra = sorted(set(data.keys()) - set(en.keys()))
    
    print(f"[{lang.upper()}] {len(data)} keys | Missing: {len(missing)} | Extra: {len(extra)}")
    
    if missing:
        print(f"  MISSING KEYS ({len(missing)}):")
        for k in missing[:50]:
            print(f"    - {k}")
        if len(missing) > 50:
            print(f"    ... and {len(missing)-50} more")
    
    if extra:
        print(f"  EXTRA KEYS ({len(extra)}):")
        for k in extra[:20]:
            print(f"    - {k}")
        if len(extra) > 20:
            print(f"    ... and {len(extra)-20} more")
    print()

# Check for English values in non-English files (RU and UK)
print("\n=== CHECKING FOR ENGLISH VALUES IN RU/UK ===\n")
import re
en_pattern = re.compile(r'^[A-Za-z0-9\s\-\.\,\!\?\:\;\(\)\[\]\{\}\/\\\@\#\$\%\^\&\*\+\=\~\`\|\<\>\"\']+$')

for lang in ['ru', 'uk']:
    fp = os.path.join(base, f'{lang}.py')
    data = extract_keys_and_values(fp)
    en_vals = []
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 10:
            # Check if value looks English (no cyrillic)
            if not re.search(r'[а-яА-ЯёЁіІїЇєЄґҐ]', v) and re.search(r'[a-zA-Z]{3,}', v):
                # Skip keys that are likely technical
                if not any(x in k for x in ['emoji', 'url', 'link', 'format', 'symbol']):
                    en_vals.append((k, v[:80]))
    if en_vals:
        print(f"[{lang.upper()}] Possibly English values ({len(en_vals)}):")
        for k, v in en_vals[:40]:
            print(f"  {k}: \"{v}\"")
        if len(en_vals) > 40:
            print(f"  ... and {len(en_vals)-40} more")
    else:
        print(f"[{lang.upper()}] No obvious English values found")
    print()

# Check critical keys in ALL files
print("\n=== CRITICAL KEYS CHECK ===\n")
critical_keys = [
    'btn_back', 'btn_close', 'btn_cancel', 'btn_confirm', 'btn_refresh',
    'balance_title', 'position_long', 'position_short', 'positions_empty',
    'exchange_bybit', 'exchange_hyperliquid',
    'strategy_oi', 'strategy_scryptomera', 'strategy_scalper',
    'strategy_elcaro', 'strategy_fibonacci', 'strategy_rsi_bb',
]

for ck in critical_keys:
    missing_in = []
    for lang in ['en'] + langs:
        fp = os.path.join(base, f'{lang}.py')
        data = extract_keys_and_values(fp)
        if ck not in data:
            missing_in.append(lang.upper())
    if missing_in:
        print(f"  KEY '{ck}': MISSING in {', '.join(missing_in)}")
    else:
        print(f"  KEY '{ck}': ✅ present in all 15 files")
