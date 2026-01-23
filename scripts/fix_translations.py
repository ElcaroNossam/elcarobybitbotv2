#!/usr/bin/env python3
"""
Fix translation files:
1. Remove duplicate keys (keep FIRST occurrence)
2. Add missing keys
"""
import re
import os
from pathlib import Path
from collections import Counter

TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"


def remove_duplicates_from_file(filepath: Path) -> tuple[int, list[str]]:
    """
    Remove duplicate keys from a translation file, keeping FIRST occurrence.
    Returns: (count_removed, list_of_duplicate_keys)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all key occurrences
    key_pattern = re.compile(r"^\s*'([^']+)':\s*", re.MULTILINE)
    all_matches = list(key_pattern.finditer(content))
    
    # Count occurrences
    key_counts = Counter(m.group(1) for m in all_matches)
    duplicate_keys = [k for k, c in key_counts.items() if c > 1]
    
    if not duplicate_keys:
        return 0, []
    
    # Build list of positions to remove (all occurrences except first)
    key_first_seen = {}
    ranges_to_remove = []
    
    for match in all_matches:
        key = match.group(1)
        if key in key_first_seen:
            # This is a duplicate - mark for removal
            start = match.start()
            # Find end of this key-value pair (find next key or end of dict)
            end = find_end_of_value(content, match.end())
            ranges_to_remove.append((start, end))
        else:
            key_first_seen[key] = match.start()
    
    # Remove ranges from end to start (to preserve positions)
    ranges_to_remove.sort(reverse=True)
    
    for start, end in ranges_to_remove:
        content = content[:start] + content[end:]
    
    # Clean up multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(ranges_to_remove), duplicate_keys


def find_end_of_value(content: str, start: int) -> int:
    """Find end of a dictionary value starting at position start."""
    i = start
    n = len(content)
    
    # Skip whitespace
    while i < n and content[i] in ' \t':
        i += 1
    
    if i >= n:
        return n
    
    # Determine value type
    if content[i:i+3] in ('"""', "'''"):
        # Triple-quoted string
        quote = content[i:i+3]
        i += 3
        end = content.find(quote, i)
        if end == -1:
            return n
        i = end + 3
    elif content[i] in ('"', "'"):
        # Single-quoted string
        quote = content[i]
        i += 1
        while i < n:
            if content[i] == '\\':
                i += 2  # Skip escaped char
            elif content[i] == quote:
                i += 1
                break
            else:
                i += 1
    elif content[i] == '(':
        # Tuple or parenthesized expression
        depth = 1
        i += 1
        while i < n and depth > 0:
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
            elif content[i] in ('"', "'"):
                # Skip string
                quote = content[i]
                i += 1
                while i < n and content[i] != quote:
                    if content[i] == '\\':
                        i += 1
                    i += 1
            i += 1
    elif content[i] == '[':
        # List
        depth = 1
        i += 1
        while i < n and depth > 0:
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                depth -= 1
            i += 1
    elif content[i] == '{':
        # Dict
        depth = 1
        i += 1
        while i < n and depth > 0:
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
            i += 1
    else:
        # Identifier or number
        while i < n and content[i] not in ',\n':
            i += 1
    
    # Skip trailing comma and whitespace/newline
    while i < n and content[i] in ' \t':
        i += 1
    if i < n and content[i] == ',':
        i += 1
    while i < n and content[i] in ' \t':
        i += 1
    if i < n and content[i] == '\n':
        i += 1
    
    return i


def add_not_set_key_to_ru():
    """Add 'not_set' key to ru.py if missing."""
    ru_path = TRANSLATIONS_DIR / "ru.py"
    
    with open(ru_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "'not_set'" in content:
        print("  ru.py already has 'not_set' key")
        return False
    
    # Find position to insert - look for closing brace
    # Insert before the final }
    match = re.search(r'\n(\s*)\}\s*$', content)
    if match:
        indent = match.group(1)
        insert_pos = match.start()
        new_line = f"\n    'not_set': 'Не установлено',"
        content = content[:insert_pos] + new_line + content[insert_pos:]
        
        with open(ru_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  Added 'not_set': 'Не установлено' to ru.py")
        return True
    
    return False


def main():
    print("=" * 60)
    print("FIXING TRANSLATION FILES - REMOVING DUPLICATES")
    print("=" * 60)
    
    translation_files = [
        'ar.py', 'cs.py', 'de.py', 'en.py', 'es.py', 'fr.py', 'he.py',
        'it.py', 'ja.py', 'lt.py', 'pl.py', 'ru.py', 'sq.py', 'uk.py', 'zh.py'
    ]
    
    total_removed = 0
    
    for filename in translation_files:
        filepath = TRANSLATIONS_DIR / filename
        if filepath.exists():
            count, keys = remove_duplicates_from_file(filepath)
            total_removed += count
            if count > 0:
                print(f"  {filename}: Removed {count} duplicates ({', '.join(keys[:3])}{'...' if len(keys) > 3 else ''})")
            else:
                print(f"  {filename}: No duplicates")
        else:
            print(f"  {filename}: NOT FOUND!")
    
    print()
    print(f"Total duplicates removed: {total_removed}")
    print()
    
    print("=" * 60)
    print("ADDING MISSING KEY TO RU.PY")
    print("=" * 60)
    add_not_set_key_to_ru()
    
    print()
    print("Done!")


if __name__ == "__main__":
    main()
