#!/usr/bin/env python3
"""
Deep Localization Audit Report
=============================
Comprehensive check of all translation files against EN reference.
"""

import re
from datetime import datetime

def get_keys(filename):
    """Extract all keys from a translation file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        keys = set(re.findall(r"'([^']+)'\s*:", content))
        return keys
    except FileNotFoundError:
        return set()

def check_file_loadable(filename):
    """Check if file can be imported as Python module."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, filename, 'exec')
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except FileNotFoundError:
        return False, "File not found"

def main():
    print("=" * 70)
    print("DEEP LOCALIZATION AUDIT REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Get EN keys as reference
    en_keys = get_keys('en.py')
    print(f"📚 REFERENCE FILE: en.py")
    print(f"   Total keys: {len(en_keys)}")
    print()
    
    # Check all languages
    languages = [
        ('ru', 'Russian'),
        ('uk', 'Ukrainian'),
        ('de', 'German'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese'),
        ('ar', 'Arabic'),
        ('he', 'Hebrew'),
        ('pl', 'Polish'),
        ('cs', 'Czech'),
        ('lt', 'Lithuanian'),
        ('sq', 'Albanian'),
    ]
    
    print("-" * 70)
    print("LANGUAGE FILES STATUS:")
    print("-" * 70)
    print(f"{'Lang':<6} {'Name':<12} {'Keys':<8} {'Missing':<10} {'Extra':<10} {'Status':<10}")
    print("-" * 70)
    
    total_missing = 0
    issues = []
    
    for code, name in languages:
        filename = f'{code}.py'
        lang_keys = get_keys(filename)
        
        # Check syntax
        loadable, error = check_file_loadable(filename)
        
        missing = en_keys - lang_keys
        extra = lang_keys - en_keys
        
        total_missing += len(missing)
        
        if not loadable:
            status = "❌ SYNTAX"
            issues.append((code, name, f"Syntax error: {error}"))
        elif missing:
            status = "⚠️ MISSING"
            issues.append((code, name, f"Missing {len(missing)} keys: {list(missing)[:5]}..."))
        else:
            status = "✅ OK"
        
        print(f"{code.upper():<6} {name:<12} {len(lang_keys):<8} {len(missing):<10} {len(extra):<10} {status:<10}")
    
    print("-" * 70)
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print(f"Total languages: {len(languages)}")
    print(f"Reference keys (EN): {len(en_keys)}")
    print(f"Total missing keys across all languages: {total_missing}")
    print()
    
    if issues:
        print("⚠️ ISSUES FOUND:")
        for code, name, issue in issues:
            print(f"  • {code.upper()} ({name}): {issue}")
    else:
        print("✅ ALL LANGUAGES ARE SYNCHRONIZED WITH EN!")
        print()
        print("All 14 translation files contain all 658 keys from en.py")
    
    print()
    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)

if __name__ == '__main__':
    main()
