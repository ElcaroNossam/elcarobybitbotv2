#!/usr/bin/env python3
import re

file_path = '/Users/elcarosam/project/elcarobybitbotv2/ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find english and russian dictionary ranges
in_english = False
in_russian = False 
seen_english = set()
seen_russian = set()
new_lines = []

for i, line in enumerate(lines):
    if 'static var englishTranslations' in line:
        in_english = True
        seen_english = set()
    elif 'static var russianTranslations' in line:
        in_english = False
        in_russian = True
        seen_russian = set()
    elif in_english and '    static var ' in line and 'Translations' in line:
        in_english = False
    elif in_russian and '    static var ' in line and 'Translations' in line and 'russian' not in line:
        in_russian = False
    
    # Check for duplicate key
    key_match = re.match(r'\s+"(\w+)"\s*:', line)
    if key_match:
        key = key_match.group(1)
        if in_english:
            if key in seen_english:
                print(f'Line {i+1}: Removing duplicate english key: {key}')
                continue
            seen_english.add(key)
        elif in_russian:
            if key in seen_russian:
                print(f'Line {i+1}: Removing duplicate russian key: {key}')
                continue
            seen_russian.add(key)
    
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print('Done!')
