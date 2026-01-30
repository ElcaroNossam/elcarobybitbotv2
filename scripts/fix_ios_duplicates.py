#!/usr/bin/env python3
"""Remove duplicate keys from LocalizationManager.swift"""

import re

filepath = '/Users/elcarosam/project/elcarobybitbotv2/ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'

# Read file
with open(filepath, 'r') as f:
    content = f.read()

# Find English dictionary
en_start = content.find('static let englishTranslations')
en_end = content.find('// MARK: - Russian')

# Find Russian dictionary  
ru_start = content.find('static let russianTranslations')
ru_end = content.find('// MARK: - Ukrainian')

def remove_duplicates(section):
    lines = section.split('\n')
    seen_keys = set()
    new_lines = []
    removed = []
    
    for line in lines:
        match = re.search(r'"([^"]+)":\s*"', line)
        if match:
            key = match.group(1)
            if key in seen_keys:
                removed.append(key)
                continue
            seen_keys.add(key)
        new_lines.append(line)
    
    return '\n'.join(new_lines), removed

# Extract sections
en_section = content[en_start:en_end]
ru_section = content[ru_start:ru_end]

new_en, en_removed = remove_duplicates(en_section)
new_ru, ru_removed = remove_duplicates(ru_section)

print(f"English duplicates removed: {len(en_removed)}")
for k in en_removed:
    print(f"  - {k}")
print(f"\nRussian duplicates removed: {len(ru_removed)}")
for k in ru_removed:
    print(f"  - {k}")

# Rebuild content
new_content = content[:en_start] + new_en + content[en_end:ru_start] + new_ru + content[ru_end:]

# Write back
with open(filepath, 'w') as f:
    f.write(new_content)

print("\nFile updated!")
