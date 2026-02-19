#!/usr/bin/env python3
"""Find missing localization keys in LocalizationManager.swift."""
import re

SWIFT_FILE = "ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift"

with open(SWIFT_FILE, "r") as f:
    content = f.read()

def extract_keys(marker, content):
    idx = content.find(marker)
    if idx == -1:
        return set()
    bracket_start = content.find("return [", idx)
    if bracket_start == -1:
        return set()
    bracket_start = content.index("[", bracket_start)
    depth = 0
    end = bracket_start
    for i in range(bracket_start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    section = content[bracket_start:end + 1]
    keys = set(re.findall(r'"([^"]+)":', section))
    return keys

en_keys = extract_keys("// MARK: - English (Reference)", content)
uk_keys = extract_keys("// MARK: - Ukrainian", content)
ru_keys = extract_keys("// MARK: - Russian", content)

missing_uk = sorted(en_keys - uk_keys)
missing_ru = sorted(en_keys - ru_keys)

print(f"English keys: {len(en_keys)}")
print(f"Ukrainian keys: {len(uk_keys)}, missing: {len(missing_uk)}")
print(f"Russian keys: {len(ru_keys)}, missing: {len(missing_ru)}")
print()
print("=== MISSING FROM UKRAINIAN ===")
for k in missing_uk:
    print(k)
print()
print("=== MISSING FROM RUSSIAN ===")
for k in missing_ru:
    print(k)
