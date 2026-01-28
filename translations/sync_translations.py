#!/usr/bin/env python3
"""
Translation Sync Script
Analyzes and synchronizes all translation files with EN as reference.
"""

import re
import os

def get_keys(filename):
    """Extract all translation keys from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        keys = re.findall(r"['\"]([a-z_0-9]+)['\"]\s*:", content)
        return set(keys)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return set()

def main():
    files = ['en.py', 'ru.py', 'uk.py', 'de.py', 'es.py', 'fr.py', 'it.py', 
             'ja.py', 'zh.py', 'ar.py', 'he.py', 'pl.py', 'cs.py', 'lt.py', 'sq.py']
    
    en_keys = get_keys('en.py')
    print(f"EN reference: {len(en_keys)} keys\n")
    print("=" * 70)
    print(f"{'File':<12} | {'Keys':>5} | {'Missing':>7} | {'Extra':>5} | Status")
    print("=" * 70)
    
    for f in files:
        if f == 'en.py':
            print(f"{'en.py':<12} | {len(en_keys):>5} |     --- |   --- | ✅ Reference")
            continue
        
        keys = get_keys(f)
        missing = en_keys - keys
        extra = keys - en_keys
        
        if len(missing) == 0:
            status = "✅ Synced"
        elif len(missing) < 10:
            status = "⚠️ Almost OK"
        elif len(missing) < 100:
            status = "⚠️ Needs update"
        else:
            status = "❌ CRITICAL"
        
        print(f"{f:<12} | {len(keys):>5} | {len(missing):>7} | {len(extra):>5} | {status}")
    
    print("=" * 70)
    
    # Show details for problematic files
    print("\n📋 DETAILS:\n")
    
    for f in files:
        if f == 'en.py':
            continue
        
        keys = get_keys(f)
        missing = en_keys - keys
        
        if len(missing) > 0 and len(missing) <= 20:
            print(f"📄 {f} - Missing {len(missing)} keys:")
            for k in sorted(missing):
                print(f"   - {k}")
            print()

if __name__ == '__main__':
    main()
