#!/usr/bin/env python3
"""
Translation Sync Tool
Ensures all translation files have the same keys and helps identify missing translations.

Usage:
    python -m utils.translation_sync           # Check for missing keys
    python -m utils.translation_sync --fix     # Add missing keys with English fallback
    python -m utils.translation_sync --report  # Generate detailed report
"""
import os
import sys
import importlib
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict


TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"
REFERENCE_LANG = "en"  # English as reference

# All supported languages
SUPPORTED_LANGUAGES = [
    "ar", "cs", "de", "en", "es", "fr", "he", 
    "it", "ja", "lt", "pl", "ru", "sq", "uk", "zh"
]


def load_translation(lang: str) -> Dict[str, str]:
    """Load translation dict from a language file"""
    try:
        module = importlib.import_module(f"translations.{lang}")
        importlib.reload(module)  # Ensure fresh load
        return getattr(module, "TEXTS", {})
    except ImportError as e:
        print(f"Warning: Could not load {lang}: {e}")
        return {}


def get_all_keys() -> Dict[str, Set[str]]:
    """Get all keys from all translation files"""
    result = {}
    for lang in SUPPORTED_LANGUAGES:
        texts = load_translation(lang)
        result[lang] = set(texts.keys())
    return result


def find_missing_keys() -> Dict[str, Set[str]]:
    """Find keys that are in reference but missing in other languages"""
    all_keys = get_all_keys()
    reference_keys = all_keys.get(REFERENCE_LANG, set())
    
    missing = {}
    for lang, keys in all_keys.items():
        if lang == REFERENCE_LANG:
            continue
        missing_keys = reference_keys - keys
        if missing_keys:
            missing[lang] = missing_keys
    
    return missing


def find_extra_keys() -> Dict[str, Set[str]]:
    """Find keys that exist in other languages but not in reference"""
    all_keys = get_all_keys()
    reference_keys = all_keys.get(REFERENCE_LANG, set())
    
    extra = {}
    for lang, keys in all_keys.items():
        if lang == REFERENCE_LANG:
            continue
        extra_keys = keys - reference_keys
        if extra_keys:
            extra[lang] = extra_keys
    
    return extra


def find_all_unique_keys() -> Set[str]:
    """Get union of all keys across all languages"""
    all_keys = get_all_keys()
    unique = set()
    for keys in all_keys.values():
        unique.update(keys)
    return unique


def generate_report() -> str:
    """Generate a detailed translation status report"""
    all_keys = get_all_keys()
    reference_keys = all_keys.get(REFERENCE_LANG, set())
    all_unique = find_all_unique_keys()
    missing = find_missing_keys()
    extra = find_extra_keys()
    
    lines = [
        "=" * 60,
        "TRANSLATION STATUS REPORT",
        "=" * 60,
        "",
        f"Reference language: {REFERENCE_LANG}",
        f"Total keys in reference: {len(reference_keys)}",
        f"Total unique keys across all: {len(all_unique)}",
        "",
        "-" * 60,
        "LANGUAGE COVERAGE",
        "-" * 60,
    ]
    
    for lang in SUPPORTED_LANGUAGES:
        keys = all_keys.get(lang, set())
        coverage = len(keys & reference_keys) / len(reference_keys) * 100 if reference_keys else 0
        missing_count = len(missing.get(lang, set()))
        extra_count = len(extra.get(lang, set()))
        
        status = "✅" if coverage == 100 and extra_count == 0 else "⚠️"
        lines.append(f"{status} {lang}: {len(keys)} keys ({coverage:.1f}% coverage)")
        
        if missing_count:
            lines.append(f"   Missing: {missing_count} keys")
        if extra_count:
            lines.append(f"   Extra: {extra_count} keys")
    
    # List missing keys per language
    if missing:
        lines.extend([
            "",
            "-" * 60,
            "MISSING KEYS BY LANGUAGE",
            "-" * 60,
        ])
        for lang, keys in sorted(missing.items()):
            lines.append(f"\n{lang} ({len(keys)} missing):")
            for key in sorted(keys)[:20]:  # Limit to first 20
                lines.append(f"  - {key}")
            if len(keys) > 20:
                lines.append(f"  ... and {len(keys) - 20} more")
    
    # List extra keys (potentially obsolete)
    if extra:
        lines.extend([
            "",
            "-" * 60,
            "EXTRA KEYS (potentially obsolete)",
            "-" * 60,
        ])
        for lang, keys in sorted(extra.items()):
            lines.append(f"\n{lang} ({len(keys)} extra):")
            for key in sorted(keys)[:10]:
                lines.append(f"  - {key}")
            if len(keys) > 10:
                lines.append(f"  ... and {len(keys) - 10} more")
    
    lines.extend([
        "",
        "=" * 60,
    ])
    
    return "\n".join(lines)


def fix_missing_keys(dry_run: bool = False) -> Dict[str, int]:
    """Add missing keys with English fallback values"""
    reference = load_translation(REFERENCE_LANG)
    missing = find_missing_keys()
    
    fixed = {}
    
    for lang, missing_keys in missing.items():
        if not missing_keys:
            continue
        
        lang_file = TRANSLATIONS_DIR / f"{lang}.py"
        
        # Read current file
        with open(lang_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the last key before closing brace
        # We'll add new keys before the final }
        
        # Build additions
        additions = []
        for key in sorted(missing_keys):
            value = reference.get(key, key)
            # Escape quotes in value
            escaped_value = value.replace("'", "\\'")
            additions.append(f"    '{key}': '{escaped_value}',  # TODO: translate from EN")
        
        if additions:
            # Find position to insert (before final })
            insert_text = "\n\n    # === AUTO-ADDED FROM ENGLISH (needs translation) ===\n" + "\n".join(additions) + "\n"
            
            # Find the last } that closes TEXTS dict
            last_brace = content.rfind("}")
            if last_brace > 0:
                new_content = content[:last_brace] + insert_text + content[last_brace:]
                
                if dry_run:
                    print(f"Would add {len(missing_keys)} keys to {lang}.py")
                else:
                    with open(lang_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Added {len(missing_keys)} keys to {lang}.py")
                
                fixed[lang] = len(missing_keys)
    
    return fixed


def check_consistency() -> bool:
    """Check if all translations are consistent (for CI/CD)"""
    missing = find_missing_keys()
    
    if missing:
        print("❌ Translation files are not in sync!")
        for lang, keys in missing.items():
            print(f"  {lang}: missing {len(keys)} keys")
        return False
    
    print("✅ All translation files are in sync")
    return True


def find_duplicate_values(lang: str = REFERENCE_LANG) -> Dict[str, List[str]]:
    """Find duplicate values (same text for different keys)"""
    texts = load_translation(lang)
    
    value_to_keys = defaultdict(list)
    for key, value in texts.items():
        value_to_keys[value].append(key)
    
    return {v: keys for v, keys in value_to_keys.items() if len(keys) > 1}


def validate_placeholders() -> Dict[str, List[Tuple[str, str]]]:
    """Check that all languages have the same placeholders as reference"""
    reference = load_translation(REFERENCE_LANG)
    
    import re
    placeholder_pattern = re.compile(r'\{[^}]+\}')
    
    issues = defaultdict(list)
    
    for lang in SUPPORTED_LANGUAGES:
        if lang == REFERENCE_LANG:
            continue
        
        texts = load_translation(lang)
        
        for key, ref_value in reference.items():
            if key not in texts:
                continue
            
            lang_value = texts[key]
            ref_placeholders = set(placeholder_pattern.findall(ref_value))
            lang_placeholders = set(placeholder_pattern.findall(lang_value))
            
            if ref_placeholders != lang_placeholders:
                issues[lang].append((key, f"Expected {ref_placeholders}, got {lang_placeholders}"))
    
    return dict(issues)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Translation sync tool")
    parser.add_argument("--fix", action="store_true", help="Add missing keys with English fallback")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--check", action="store_true", help="Check consistency (for CI)")
    parser.add_argument("--validate", action="store_true", help="Validate placeholders")
    
    args = parser.parse_args()
    
    if args.report:
        print(generate_report())
    elif args.fix:
        fixed = fix_missing_keys(dry_run=args.dry_run)
        if fixed:
            print(f"\nTotal: Fixed {sum(fixed.values())} missing keys across {len(fixed)} languages")
        else:
            print("No missing keys to fix!")
    elif args.check:
        success = check_consistency()
        sys.exit(0 if success else 1)
    elif args.validate:
        issues = validate_placeholders()
        if issues:
            print("⚠️ Placeholder mismatches found:")
            for lang, problems in issues.items():
                print(f"\n{lang}:")
                for key, msg in problems[:10]:
                    print(f"  {key}: {msg}")
        else:
            print("✅ All placeholders are consistent")
    else:
        # Default: show summary
        missing = find_missing_keys()
        if missing:
            print("Missing translations found:")
            for lang, keys in sorted(missing.items()):
                print(f"  {lang}: {len(keys)} missing keys")
            print("\nRun with --report for details or --fix to add English fallbacks")
        else:
            print("✅ All translations are in sync!")


if __name__ == "__main__":
    main()
