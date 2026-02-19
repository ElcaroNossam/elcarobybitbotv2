#!/usr/bin/env python3
"""Check for duplicate localization keys in LocalizationManager.swift"""
import re
from collections import Counter

filepath = 'ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'
with open(filepath, 'r') as f:
    lines = f.readlines()

# Known section boundaries from grep
sections = [
    ("english", 189, 1180),
    ("russian", 1180, 2168),
    ("ukrainian", 2168, 3124),
    ("german", 3124, 4025),
    ("spanish", 4025, 4926),
    ("french", 4926, 5827),
    ("italian", 5827, 6728),
    ("japanese", 6728, 7629),
    ("chinese", 7629, 8530),
    ("arabic", 8530, 9431),
    ("hebrew", 9431, 10332),
    ("polish", 10332, 11233),
    ("czech", 11233, 12135),
    ("lithuanian", 12135, 13036),
    ("albanian", 13036, 13966),
]

print(f"Checking {len(sections)} language sections\n")

total_dupes = 0
all_dupes = {}
for lang, start, end in sections:
    keys_with_lines = []
    for i in range(start-1, min(end, len(lines))):
        m = re.search(r'"([^"]+)"\s*:', lines[i])
        if m:
            keys_with_lines.append((m.group(1), i+1))
    
    counter = Counter(k for k, _ in keys_with_lines)
    dupes = {k: v for k, v in counter.items() if v > 1}
    
    if dupes:
        print(f"  {lang}: {len(keys_with_lines)} keys, {len(dupes)} DUPLICATED keys:")
        all_dupes[lang] = []
        for key, count in sorted(dupes.items()):
            total_dupes += count - 1
            occurrences = [ln for k, ln in keys_with_lines if k == key]
            print(f"    \"{key}\": appears {count} times at lines {occurrences}")
            # Mark all but first occurrence for removal
            all_dupes[lang].extend(occurrences[1:])
        print()
    else:
        print(f"  {lang}: {len(keys_with_lines)} keys, OK")

print(f"\nTotal duplicate entries to remove: {total_dupes}")
if all_dupes:
    all_lines = sorted(set(ln for lines_list in all_dupes.values() for ln in lines_list))
    print(f"Lines to remove: {all_lines}")

# Part 2: Check key consistency across languages
print("\n\n=== KEY CONSISTENCY CHECK ===\n")
lang_keys = {}
for lang, start, end in sections:
    keys = set()
    for i in range(start-1, min(end, len(lines))):
        m = re.search(r'"([^"]+)"\s*:', lines[i])
        if m:
            keys.add(m.group(1))
    lang_keys[lang] = keys

en_keys = lang_keys["english"]
print(f"English keys: {len(en_keys)}")
print()

for lang, keys in lang_keys.items():
    if lang == "english":
        continue
    missing = en_keys - keys
    extra = keys - en_keys
    if missing or extra:
        print(f"{lang}:")
        if missing:
            miss_sorted = sorted(missing)
            print(f"  MISSING from English ({len(missing)}): {miss_sorted}")
        if extra:
            ext_sorted = sorted(extra)
            print(f"  EXTRA not in English ({len(extra)}): {ext_sorted}")
    else:
        print(f"{lang}: perfect match")
