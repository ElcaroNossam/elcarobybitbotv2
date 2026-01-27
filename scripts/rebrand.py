#!/usr/bin/env python3
"""
Rebrand Script
Updates app name across all platforms when APP_NAME env is changed

Usage:
    # Check current branding
    python scripts/rebrand.py --check
    
    # Preview changes (dry run)
    python scripts/rebrand.py --preview NewName
    
    # Apply changes
    python scripts/rebrand.py --apply NewName
"""
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

# Files that contain hardcoded app name references
REBRAND_TARGETS = [
    # Environment files
    ('.env.example', 'APP_NAME=', 'env'),
    
    # iOS
    ('ios/EnlikoTrading/App/Config.swift', 'appName', 'swift'),
    
    # Android
    ('android/EnlikoTrading/app/build.gradle.kts', 'APP_NAME', 'gradle'),
    
    # Python config
    ('config/settings.py', 'APP_NAME', 'python'),
    ('core/branding.py', 'APP_NAME', 'python'),
]

# Translation files (need special handling for welcome text)
TRANSLATION_FILES = [
    f'translations/{lang}.py' 
    for lang in ['ar', 'cs', 'de', 'en', 'es', 'fr', 'he', 'it', 'ja', 'lt', 'pl', 'ru', 'sq', 'uk', 'zh']
]

# HTML templates
HTML_TEMPLATES = [
    'webapp/templates/landing.html',
    'webapp/templates/terminal.html',
    'webapp/templates/admin/dashboard.html',
    'webapp/templates/strategy_settings.html',
]


def find_app_name_occurrences(current_name: str = "Enliko") -> List[Tuple[str, int, str]]:
    """Find all occurrences of app name in the project"""
    occurrences = []
    
    # Search in Python files
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
        
        for file in files:
            if file.endswith(('.py', '.swift', '.kt', '.html', '.js', '.kts', '.env')):
                filepath = Path(root) / file
                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.split('\n'), 1):
                        if current_name in line:
                            rel_path = filepath.relative_to(PROJECT_ROOT)
                            occurrences.append((str(rel_path), i, line.strip()[:80]))
                except Exception:
                    pass
    
    return occurrences


def preview_rebrand(old_name: str, new_name: str):
    """Show what would change"""
    occurrences = find_app_name_occurrences(old_name)
    
    print(f"\n📋 Preview: Rebrand from '{old_name}' to '{new_name}'")
    print(f"   Found {len(occurrences)} occurrences:\n")
    
    # Group by file
    by_file = {}
    for path, line, text in occurrences:
        if path not in by_file:
            by_file[path] = []
        by_file[path].append((line, text))
    
    for path, lines in sorted(by_file.items()):
        print(f"   {path}:")
        for line, text in lines[:3]:
            new_text = text.replace(old_name, new_name)
            print(f"      L{line}: {text[:50]} → {new_text[:50]}")
        if len(lines) > 3:
            print(f"      ... and {len(lines) - 3} more")
        print()
    
    return len(occurrences)


def update_env_file(new_name: str):
    """Update .env.example with new app name"""
    env_file = PROJECT_ROOT / '.env.example'
    if env_file.exists():
        content = env_file.read_text()
        content = re.sub(r'APP_NAME=\w+', f'APP_NAME={new_name}', content)
        env_file.write_text(content)
        print(f"   ✅ Updated .env.example")


def apply_rebrand(old_name: str, new_name: str):
    """Apply the rebrand"""
    print(f"\n🔧 Applying rebrand: '{old_name}' → '{new_name}'")
    
    updated_count = 0
    
    # Update .env.example
    update_env_file(new_name)
    updated_count += 1
    
    # Update translation files
    for trans_file in TRANSLATION_FILES:
        filepath = PROJECT_ROOT / trans_file
        if filepath.exists():
            content = filepath.read_text()
            if old_name in content:
                new_content = content.replace(old_name, new_name)
                filepath.write_text(new_content)
                updated_count += 1
                print(f"   ✅ Updated {trans_file}")
    
    # Update HTML templates
    for html_file in HTML_TEMPLATES:
        filepath = PROJECT_ROOT / html_file
        if filepath.exists():
            content = filepath.read_text()
            if old_name in content:
                new_content = content.replace(old_name, new_name)
                filepath.write_text(new_content)
                updated_count += 1
                print(f"   ✅ Updated {html_file}")
    
    print(f"\n✅ Rebrand complete! Updated {updated_count} files.")
    print(f"\n⚠️  IMPORTANT: After rebranding, you must:")
    print(f"   1. Update APP_NAME in .env file")
    print(f"   2. Rebuild iOS: cd ios/EnlikoTrading && xcodebuild")
    print(f"   3. Rebuild Android: cd android/EnlikoTrading && ./gradlew assembleDebug")
    print(f"   4. Restart the bot: sudo systemctl restart elcaro-bot")


def check_current_branding():
    """Check current branding status"""
    print("\n📊 CURRENT BRANDING STATUS")
    print("=" * 50)
    
    # Check .env.example
    env_file = PROJECT_ROOT / '.env.example'
    if env_file.exists():
        content = env_file.read_text()
        match = re.search(r'APP_NAME=(\w+)', content)
        if match:
            print(f"   .env.example: APP_NAME={match.group(1)}")
    
    # Check iOS Config.swift
    ios_config = PROJECT_ROOT / 'ios/EnlikoTrading/App/Config.swift'
    if ios_config.exists():
        content = ios_config.read_text()
        match = re.search(r'environment\["APP_NAME"\] \?\? "(\w+)"', content)
        if match:
            print(f"   iOS Config.swift: default={match.group(1)}")
    
    # Check Android build.gradle.kts
    android_gradle = PROJECT_ROOT / 'android/EnlikoTrading/app/build.gradle.kts'
    if android_gradle.exists():
        content = android_gradle.read_text()
        match = re.search(r'System\.getenv\("APP_NAME"\) \?: "(\w+)"', content)
        if match:
            print(f"   Android build.gradle.kts: default={match.group(1)}")
    
    # Check Python branding
    branding_file = PROJECT_ROOT / 'core/branding.py'
    if branding_file.exists():
        content = branding_file.read_text()
        match = re.search(r'os\.getenv\("APP_NAME", "(\w+)"\)', content)
        if match:
            print(f"   core/branding.py: default={match.group(1)}")
    
    # Count occurrences
    occurrences = find_app_name_occurrences("Enliko")
    print(f"\n   Total 'Enliko' occurrences: {len(occurrences)}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Rebrand the app')
    parser.add_argument('--check', action='store_true', help='Check current branding')
    parser.add_argument('--preview', type=str, help='Preview rebrand to new name')
    parser.add_argument('--apply', type=str, help='Apply rebrand to new name')
    parser.add_argument('--from', dest='old_name', type=str, default='Enliko', 
                        help='Current app name (default: Enliko)')
    
    args = parser.parse_args()
    
    if args.check:
        check_current_branding()
    elif args.preview:
        preview_rebrand(args.old_name, args.preview)
    elif args.apply:
        apply_rebrand(args.old_name, args.apply)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
