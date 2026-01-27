#!/usr/bin/env python3
"""
Translation Sync Checker
Verifies all 15 languages have consistent keys
"""
import os
import sys
import importlib.util

def main():
    translation_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
    languages = ['ar', 'cs', 'de', 'en', 'es', 'fr', 'he', 'it', 'ja', 'lt', 'pl', 'ru', 'sq', 'uk', 'zh']

    all_keys = {}
    all_texts = {}
    
    print("=" * 60)
    print("📊 TRANSLATION SYNC REPORT")
    print("=" * 60)
    
    for lang in languages:
        filepath = os.path.join(translation_dir, f'{lang}.py')
        if not os.path.exists(filepath):
            print(f"❌ {lang}: FILE NOT FOUND")
            continue
            
        spec = importlib.util.spec_from_file_location(lang, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        all_keys[lang] = set(module.TEXTS.keys())
        all_texts[lang] = module.TEXTS
        print(f"  {lang}: {len(module.TEXTS)} keys")

    # Find reference (English)
    en_keys = all_keys.get('en', set())
    print(f"\n📊 Reference (EN): {len(en_keys)} keys")

    # Check for missing keys
    print("\n🔍 SYNC STATUS:")
    print("-" * 40)
    
    all_synced = True
    for lang in languages:
        if lang == 'en':
            continue
        if lang not in all_keys:
            print(f"  ❌ {lang}: FILE MISSING")
            all_synced = False
            continue
            
        missing = en_keys - all_keys[lang]
        extra = all_keys[lang] - en_keys
        
        if missing or extra:
            all_synced = False
            if missing:
                print(f"  ⚠️ {lang}: MISSING {len(missing)} keys")
                for key in sorted(missing)[:10]:
                    print(f"      - {key}")
                if len(missing) > 10:
                    print(f"      ... and {len(missing) - 10} more")
            if extra:
                print(f"  ℹ️ {lang}: EXTRA {len(extra)} keys")
                for key in sorted(extra)[:5]:
                    print(f"      + {key}")
        else:
            print(f"  ✅ {lang}: OK ({len(all_keys[lang])} keys)")

    print("\n" + "=" * 60)
    if all_synced:
        print("✅ ALL LANGUAGES SYNCHRONIZED!")
    else:
        print("⚠️ SOME LANGUAGES NEED SYNC")
    print("=" * 60)
    
    # Count Lyxen mentions
    print("\n📛 APP NAME 'Lyxen' mentions by language:")
    print("-" * 40)
    for lang in languages:
        if lang not in all_texts:
            continue
        lyxen_count = 0
        for key, value in all_texts[lang].items():
            if isinstance(value, str) and 'Lyxen' in value:
                lyxen_count += 1
        print(f"  {lang}: {lyxen_count} mentions")
    
    return 0 if all_synced else 1

if __name__ == "__main__":
    sys.exit(main())
