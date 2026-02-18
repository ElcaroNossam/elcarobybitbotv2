#!/usr/bin/env python3
"""Final localization audit across all platforms."""
import re
import os
import sys
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def audit_server_translations():
    """Check all 15 server translation files."""
    print("=" * 60)
    print("PHASE 1: SERVER TRANSLATIONS (translations/*.py)")
    print("=" * 60)
    en = importlib.import_module('translations.en').TEXTS
    en_keys = set(en.keys())
    print(f"EN keys: {len(en_keys)}")
    
    langs = ['ru','uk','de','es','fr','it','ja','zh','ar','he','pl','cs','lt','sq']
    issues = []
    for lang in langs:
        mod = importlib.import_module(f'translations.{lang}')
        lk = set(mod.TEXTS.keys())
        missing = en_keys - lk
        extra = lk - en_keys
        status = "✅" if not missing else "❌"
        print(f"  {status} {lang}: {len(lk)} keys, missing {len(missing)}, extra {len(extra)}")
        if missing:
            issues.append((lang, sorted(missing)))
            print(f"     MISSING: {sorted(missing)[:10]}")
    
    # Check for English values that are just copies (untranslated)
    print(f"\n  Checking for untranslated copies (EN value == translated value)...")
    for lang in langs:
        if lang == 'en':
            continue
        mod = importlib.import_module(f'translations.{lang}')
        texts = mod.TEXTS
        copies = 0
        for key in en_keys:
            if key in texts and texts[key] == en[key] and len(en[key]) > 3:
                copies += 1
        if copies > 50:
            print(f"  ⚠️  {lang}: {copies} keys are exact EN copies (may be untranslated)")
    
    return issues


def audit_ios_translations():
    """Check iOS LocalizationManager.swift key coverage."""
    print("\n" + "=" * 60)
    print("PHASE 2: iOS TRANSLATIONS (LocalizationManager.swift)")
    print("=" * 60)
    
    filepath = os.path.join(ROOT, 'ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift')
    if not os.path.exists(filepath):
        print("  ❌ File not found!")
        return []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Parse language blocks
    lang_map = {
        'english': 'en', 'russian': 'ru', 'ukrainian': 'uk',
        'german': 'de', 'spanish': 'es', 'french': 'fr',
        'italian': 'it', 'japanese': 'ja', 'chinese': 'zh',
        'arabic': 'ar', 'hebrew': 'he', 'polish': 'pl',
        'czech': 'cs', 'lithuanian': 'lt', 'albanian': 'sq'
    }
    
    results = {}
    for swift_name, code in lang_map.items():
        # Find .langName: [ and count keys
        pattern = re.compile(rf'\.{swift_name}\s*:\s*\[')
        match = pattern.search(content)
        if match:
            start = match.end()
            depth = 1
            pos = start
            while pos < len(content) and depth > 0:
                if content[pos] == '[':
                    depth += 1
                elif content[pos] == ']':
                    depth -= 1
                pos += 1
            block = content[start:pos-1]
            keys = re.findall(r'"([^"]+)"\s*:', block)
            results[code] = set(keys)
    
    if 'en' not in results:
        print("  ❌ Could not parse English keys!")
        return []
    
    en_keys = results['en']
    print(f"  EN keys: {len(en_keys)}")
    
    issues = []
    for code in ['ru','uk','de','es','fr','it','ja','zh','ar','he','pl','cs','lt','sq']:
        if code not in results:
            print(f"  ❌ {code}: NOT FOUND in file!")
            issues.append((code, list(en_keys)))
            continue
        lang_keys = results[code]
        missing = en_keys - lang_keys
        status = "✅" if not missing else "❌"
        print(f"  {status} {code}: {len(lang_keys)} keys, missing {len(missing)}")
        if missing:
            issues.append((code, sorted(missing)))
            print(f"     MISSING: {sorted(missing)[:8]}...")
    
    return issues


def audit_android_translations():
    """Check Android Localization.kt."""
    print("\n" + "=" * 60)
    print("PHASE 3: ANDROID TRANSLATIONS (Localization.kt)")
    print("=" * 60)
    
    filepath = os.path.join(ROOT, 'android/EnlikoTrading/app/src/main/java/io/enliko/trading/util/Localization.kt')
    if not os.path.exists(filepath):
        print("  ❌ File not found!")
        return []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find interface Strings properties
    interface_match = re.search(r'interface Strings \{(.*?)\n\}', content, re.DOTALL)
    if interface_match:
        interface_block = interface_match.group(1)
        props = re.findall(r'val\s+(\w+)', interface_block)
        print(f"  Interface Strings: {len(props)} properties")
    
    # Find each language object
    lang_objects = re.findall(r'object\s+(\w+)\s*:\s*Strings\s*\{', content)
    print(f"  Language objects: {len(lang_objects)}")
    for obj in lang_objects:
        print(f"    {obj}")
    
    # Check for empty strings
    empty_count = len(re.findall(r'override val \w+ = ""', content))
    if empty_count > 0:
        print(f"  ⚠️  {empty_count} properties with empty strings!")
    
    return []


def audit_bot_hardcoded():
    """Find hardcoded Russian/English strings in bot.py."""
    print("\n" + "=" * 60)
    print("PHASE 4: BOT.PY HARDCODED STRINGS")
    print("=" * 60)
    
    filepath = os.path.join(ROOT, 'bot.py')
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # 1. t.get() with Russian fallbacks
    russian_fallbacks = []
    for i, line in enumerate(lines, 1):
        if 't.get(' in line and re.search(r'[а-яА-ЯёЁ]', line):
            russian_fallbacks.append((i, line.strip()[:100]))
    
    print(f"\n  t.get() with Russian fallbacks: {len(russian_fallbacks)}")
    for lineno, text in russian_fallbacks:
        print(f"    L{lineno}: {text}")
    
    # 2. Hardcoded send_message/edit_message with plain strings
    hardcoded_messages = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Only check user-facing messages, skip logger/comments
        if ('send_message' in stripped or 'edit_message_text' in stripped or 'reply_text' in stripped):
            if re.search(r'[а-яА-ЯёЁ]{3,}', stripped) and '#' not in stripped.split('send_message')[0] if 'send_message' in stripped else True:
                if 'logger' not in stripped and not stripped.startswith('#'):
                    hardcoded_messages.append((i, stripped[:120]))
    
    print(f"\n  Hardcoded Cyrillic in messages: {len(hardcoded_messages)}")
    for lineno, text in hardcoded_messages[:15]:
        print(f"    L{lineno}: {text}")
    
    # 3. Hardcoded English strings in await send/edit
    eng_hardcoded = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.search(r'(send_message|edit_message_text|reply_text)\(.*"[A-Z][a-z]{2,}', stripped):
            if 't.get' not in stripped and 'logger' not in stripped and 'callback_data' not in stripped:
                if not stripped.startswith('#') and 'parse_mode' not in stripped:
                    eng_hardcoded.append((i, stripped[:120]))
    
    print(f"\n  Potential hardcoded English messages: {len(eng_hardcoded)}")
    for lineno, text in eng_hardcoded[:15]:
        print(f"    L{lineno}: {text}")
    
    return russian_fallbacks


def audit_ios_hardcoded():
    """Find hardcoded strings in iOS Swift views."""
    print("\n" + "=" * 60)
    print("PHASE 5: iOS HARDCODED STRINGS (Swift Views)")
    print("=" * 60)
    
    ios_dir = os.path.join(ROOT, 'ios/EnlikoTrading/EnlikoTrading/Views')
    if not os.path.exists(ios_dir):
        print("  ❌ Views directory not found!")
        return
    
    total_hardcoded = 0
    for dirpath, _, filenames in os.walk(ios_dir):
        for fn in filenames:
            if not fn.endswith('.swift'):
                continue
            fpath = os.path.join(dirpath, fn)
            with open(fpath, 'r') as f:
                lines = f.readlines()
            
            file_issues = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Text("Something") without .localized
                if re.search(r'Text\(\s*"[A-Z][a-z]', stripped) and '.localized' not in stripped:
                    # Skip comments, imports, @State defaults, NavigationTitle
                    if not stripped.startswith('//') and 'preview' not in stripped.lower():
                        file_issues.append((i, stripped[:100]))
                # Label("Something") without .localized
                if re.search(r'Label\(\s*"[A-Z][a-z]', stripped) and '.localized' not in stripped:
                    if not stripped.startswith('//'):
                        file_issues.append((i, stripped[:100]))
            
            if file_issues:
                rel = os.path.relpath(fpath, ROOT)
                print(f"\n  📄 {rel}: {len(file_issues)} hardcoded strings")
                for lineno, text in file_issues[:5]:
                    print(f"     L{lineno}: {text}")
                if len(file_issues) > 5:
                    print(f"     ... and {len(file_issues) - 5} more")
                total_hardcoded += len(file_issues)
    
    print(f"\n  TOTAL hardcoded iOS strings: {total_hardcoded}")


def audit_android_hardcoded():
    """Find hardcoded strings in Android Compose screens."""
    print("\n" + "=" * 60)
    print("PHASE 6: ANDROID HARDCODED STRINGS (Compose)")
    print("=" * 60)
    
    android_screens = os.path.join(ROOT, 'android/EnlikoTrading/app/src/main/java/io/enliko/trading/ui/screens')
    if not os.path.exists(android_screens):
        print("  ❌ Screens directory not found!")
        return
    
    total_hardcoded = 0
    for dirpath, _, filenames in os.walk(android_screens):
        for fn in filenames:
            if not fn.endswith('.kt'):
                continue
            fpath = os.path.join(dirpath, fn)
            with open(fpath, 'r') as f:
                lines = f.readlines()
            
            file_issues = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Text("Something") - hardcoded
                if re.search(r'Text\(\s*"[A-Z][a-z]', stripped):
                    if 'strings.' not in stripped and 'LocalStrings' not in stripped:
                        if not stripped.startswith('//'):
                            file_issues.append((i, stripped[:100]))
                # text = "Something" in composable params
                if re.search(r'text\s*=\s*"[A-Z][a-z]', stripped):
                    if 'strings.' not in stripped:
                        if not stripped.startswith('//'):
                            file_issues.append((i, stripped[:100]))
            
            if file_issues:
                rel = os.path.relpath(fpath, ROOT)
                print(f"\n  📄 {rel}: {len(file_issues)} hardcoded strings")
                for lineno, text in file_issues[:5]:
                    print(f"     L{lineno}: {text}")
                if len(file_issues) > 5:
                    print(f"     ... and {len(file_issues) - 5} more")
                total_hardcoded += len(file_issues)
    
    print(f"\n  TOTAL hardcoded Android strings: {total_hardcoded}")


def audit_webapp():
    """Check webapp templates for hardcoded strings."""
    print("\n" + "=" * 60)
    print("PHASE 7: WEBAPP TEMPLATES")
    print("=" * 60)
    
    templates_dir = os.path.join(ROOT, 'webapp/templates')
    if not os.path.exists(templates_dir):
        print("  ❌ Templates directory not found!")
        return
    
    # Check for i18n system
    i18n_path = os.path.join(ROOT, 'webapp/static/i18n')
    if os.path.exists(i18n_path):
        for fn in os.listdir(i18n_path):
            if fn.endswith('.js') or fn.endswith('.json'):
                fpath = os.path.join(i18n_path, fn)
                with open(fpath, 'r') as f:
                    content = f.read()
                keys = re.findall(r'"([^"]+)":', content)
                print(f"  i18n file '{fn}': ~{len(keys)} keys")
    
    # Count templates and data-i18n usage
    template_count = 0
    i18n_templates = 0
    for fn in os.listdir(templates_dir):
        if fn.endswith('.html'):
            template_count += 1
            fpath = os.path.join(templates_dir, fn)
            with open(fpath, 'r') as f:
                content = f.read()
            if 'data-i18n' in content or 'i18n' in content:
                i18n_templates += 1
    
    print(f"  Total templates: {template_count}")
    print(f"  Templates with i18n: {i18n_templates}")
    print(f"  Templates without i18n: {template_count - i18n_templates}")


if __name__ == '__main__':
    print("🔍 ENLIKO PLATFORM — FINAL LOCALIZATION AUDIT")
    print("=" * 60)
    
    server_issues = audit_server_translations()
    ios_issues = audit_ios_translations()
    android_issues = audit_android_translations()
    bot_issues = audit_bot_hardcoded()
    audit_ios_hardcoded()
    audit_android_hardcoded()
    audit_webapp()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  Server: {'✅ Clean' if not server_issues else f'❌ {len(server_issues)} langs with missing keys'}")
    print(f"  iOS: {'✅ Clean' if not ios_issues else f'❌ {len(ios_issues)} langs with missing keys'}")
    print(f"  Bot.py Russian fallbacks: {len(bot_issues)} found")
