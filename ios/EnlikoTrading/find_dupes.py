#!/usr/bin/env python3
import re

with open('EnlikoTrading/Services/LocalizationManager.swift', 'r') as f:
    lines = f.readlines()

def find_dupes_in_section(section_name, lines):
    """Find a dictionary section and report duplicate keys."""
    in_section = False
    brace_count = 0
    keys = {}
    start = 0
    end = 0
    
    for i, line in enumerate(lines):
        if section_name in line and 'return [' in line:
            in_section = True
            start = i + 1
            brace_count = line.count('[') - line.count(']')
            match = re.search(r'"([^"]+)"\s*:', line)
            if match:
                key = match.group(1)
                keys.setdefault(key, []).append(i + 1)
            continue
        
        if in_section:
            brace_count += line.count('[') - line.count(']')
            match = re.search(r'"([^"]+)"\s*:', line)
            if match:
                key = match.group(1)
                keys.setdefault(key, []).append(i + 1)
            if brace_count <= 0:
                end = i + 1
                break
    
    dupes = {k: v for k, v in keys.items() if len(v) > 1}
    return start, end, len(keys), dupes

# Check each translation dictionary
sections = [
    'englishTranslations',
    'russianTranslations', 
    'ukrainianTranslations',
    'germanTranslations',
    'spanishTranslations',
    'frenchTranslations',
    'italianTranslations',
    'japaneseTranslations',
    'chineseTranslations',
    'arabicTranslations',
    'hebrewTranslations',
    'polishTranslations',
    'czechTranslations',
    'lithuanianTranslations',
    'albanianTranslations',
]

for section in sections:
    start, end, total_keys, dupes = find_dupes_in_section(section, lines)
    if dupes:
        print(f"\n=== {section} (lines {start}-{end}, {total_keys} keys) ===")
        print(f"DUPLICATE KEYS ({len(dupes)}):")
        for k, v in sorted(dupes.items()):
            print(f'  "{k}" at lines: {v}')
    else:
        if start > 0:
            print(f"  {section}: OK ({total_keys} keys, no duplicates)")
        else:
            print(f"  {section}: NOT FOUND")
