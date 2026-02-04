#!/usr/bin/env python3
"""
Sync missing translation keys from EN to all other languages.
"""
import os
import re
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translations import en

en_texts = en.TEXTS.copy()

langs = ['uk', 'de', 'es', 'fr', 'it', 'ja', 'zh', 'ar', 'he', 'pl', 'cs', 'lt', 'sq']

def sync_language(lang: str):
    """Sync a single language file with EN."""
    lang_path = f'translations/{lang}.py'
    
    # Import language module
    lang_module = __import__(f'translations.{lang}', fromlist=['TEXTS'])
    current_texts = getattr(lang_module, 'TEXTS', {})
    
    # Find missing keys
    missing = set(en_texts.keys()) - set(current_texts.keys())
    
    if not missing:
        print(f'{lang}: Already synced (all {len(en_texts)} keys)')
        return
    
    # Read file content
    with open(lang_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find position to insert (before final closing brace of TEXTS)
    # Look for the closing brace that ends TEXTS dict
    lines = content.split('\n')
    
    # Find TEXTS = { and then track braces
    insert_line = None
    brace_count = 0
    in_texts = False
    
    for i, line in enumerate(lines):
        if 'TEXTS' in line and '=' in line and '{' in line:
            in_texts = True
            brace_count += line.count('{') - line.count('}')
            continue
        
        if in_texts:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                insert_line = i
                break
    
    if insert_line is None:
        print(f'{lang}: ERROR - Could not find TEXTS closing brace')
        return
    
    # Build missing entries
    missing_entries = []
    for key in sorted(missing):
        val = en_texts[key].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        missing_entries.append(f'    "{key}": "{val}",')
    
    # Insert entries before closing brace
    new_lines = lines[:insert_line]
    new_lines.append('')
    new_lines.append('    # === AUTO-SYNCED FROM EN (need translation) ===')
    new_lines.extend(missing_entries)
    new_lines.extend(lines[insert_line:])
    
    new_content = '\n'.join(new_lines)
    
    with open(lang_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f'{lang}: Added {len(missing)} keys')

def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print(f'EN reference: {len(en_texts)} keys')
    print('=' * 40)
    
    for lang in langs:
        try:
            sync_language(lang)
        except Exception as e:
            print(f'{lang}: ERROR - {e}')
    
    print('=' * 40)
    print('Done!')

if __name__ == '__main__':
    main()
