#!/usr/bin/env python3
"""Verify all 15 languages have all keys."""
import re

SWIFT_FILE = "ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift"

with open(SWIFT_FILE, "r") as f:
    content = f.read()

markers = {
    "English": "// MARK: - English (Reference)",
    "Russian": "// MARK: - Russian",
    "Ukrainian": "// MARK: - Ukrainian",
    "German": "// MARK: - German",
    "Spanish": "// MARK: - Spanish",
    "French": "// MARK: - French",
    "Italian": "// MARK: - Italian",
    "Japanese": "// MARK: - Japanese",
    "Chinese": "// MARK: - Chinese",
    "Arabic": "// MARK: - Arabic",
    "Hebrew": "// MARK: - Hebrew",
    "Polish": "// MARK: - Polish",
    "Czech": "// MARK: - Czech",
    "Lithuanian": "// MARK: - Lithuanian",
    "Albanian": "// MARK: - Albanian",
}

def extract_keys(marker):
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
    return set(re.findall(r'"([^"]+)":', section))

en_keys = extract_keys(markers["English"])
print(f"English (reference): {len(en_keys)} keys\n")

all_ok = True
for lang, marker in markers.items():
    if lang == "English":
        continue
    keys = extract_keys(marker)
    missing = en_keys - keys
    status = "OK" if len(missing) == 0 else "MISSING"
    print(f"  {status} {lang}: {len(keys)} keys, missing: {len(missing)}")
    if missing:
        all_ok = False

print(f"\n{'ALL LANGUAGES COMPLETE!' if all_ok else 'SOME LANGUAGES HAVE MISSING KEYS'}")
