#!/usr/bin/env python3
"""Fix Android 'Unresolved reference: strings' by injecting val strings = LocalStrings.current"""

import os
import re

SCREENS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "android", "EnlikoTrading", "app", "src", "main",
    "java", "io", "enliko", "trading", "ui", "screens"
)

IMPORT_LINE = "import io.enliko.trading.util.LocalStrings"
STRINGS_DECL = "    val strings = LocalStrings.current"

# Files that need fixing (from build error analysis)
TARGET_FILES = [
    "NotificationSettingsScreen.kt",
    "ApiKeysScreen.kt",
    "StrategySettingsScreen.kt",
    "RiskSettingsScreen.kt",
    "LeverageSettingsScreen.kt",
    "TradingSettingsScreen.kt",
    "ExchangeSettingsScreen.kt",
    "HyperLiquidScreen.kt",
    "ScreenerScreen.kt",
    "LinkEmailScreen.kt",
    "StrategiesScreen.kt",
    "AdminScreen.kt",
    "PositionsScreen.kt",
    "MarketHubScreen.kt",
    "OrderbookScreen.kt",
    "AdvancedTradingScreen.kt",
    "ManualTradingScreen.kt",
    "StatsScreen.kt",
    "SpotTradingScreen.kt",
    "LoginScreen.kt",
    "AlertsScreen.kt",
    "TradeHistoryScreen.kt",
    "WalletScreen.kt",
]


def find_file(filename):
    """Find a .kt file recursively in SCREENS_DIR."""
    for root, dirs, files in os.walk(SCREENS_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None


def add_import(content):
    """Add import line if missing."""
    if IMPORT_LINE in content:
        return content, False
    lines = content.split("\n")
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("import "):
            last_import_idx = i
    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, IMPORT_LINE)
    else:
        # No imports? Add after package line
        for i, line in enumerate(lines):
            if line.startswith("package "):
                lines.insert(i + 1, "")
                lines.insert(i + 2, IMPORT_LINE)
                break
    return "\n".join(lines), True


def inject_strings_declaration(content):
    """Inject val strings = LocalStrings.current into all @Composable functions that need it."""
    if "strings." not in content:
        return content, False

    # Already has it everywhere needed
    if "LocalStrings.current" in content:
        # Check if ALL composable funs that use strings. have the declaration
        # For simplicity, we'll check if the declaration exists at all
        return content, False

    lines = content.split("\n")
    new_lines = []
    modified = False
    i = 0

    while i < len(lines):
        new_lines.append(lines[i])

        # Detect @Composable annotation
        stripped = lines[i].strip()
        if stripped == "@Composable":
            # Look ahead for the fun declaration and its opening brace
            j = i + 1
            fun_lines = []
            found_brace = False

            while j < len(lines):
                fun_lines.append(lines[j])
                new_lines.append(lines[j])

                if "{" in lines[j]:
                    found_brace = True
                    # Check if body uses strings.
                    # Look ahead in the function body to see if strings. is used
                    body_text = ""
                    brace_depth = 0
                    for k in range(j, min(j + 200, len(lines))):
                        for ch in lines[k]:
                            if ch == "{":
                                brace_depth += 1
                            elif ch == "}":
                                brace_depth -= 1
                        body_text += lines[k] + "\n"
                        if brace_depth <= 0 and k > j:
                            break

                    if "strings." in body_text and "val strings = LocalStrings.current" not in body_text:
                        # Inject after the opening brace
                        new_lines.append(STRINGS_DECL)
                        modified = True

                    i = j
                    break

                j += 1

            if not found_brace:
                i = max(i, j - 1) if fun_lines else i

        i += 1

    return "\n".join(new_lines), modified


def fix_file(filepath):
    """Fix a single file."""
    with open(filepath, "r") as f:
        content = f.read()

    if "strings." not in content:
        return False

    original = content
    changed = False

    # Step 1: Add import
    content, imp_changed = add_import(content)
    if imp_changed:
        changed = True

    # Step 2: Inject strings declaration into composable functions
    content, inj_changed = inject_strings_declaration(content)
    if inj_changed:
        changed = True

    if changed:
        with open(filepath, "w") as f:
            f.write(content)

    return changed


def main():
    fixed_count = 0
    not_found = []

    for filename in TARGET_FILES:
        filepath = find_file(filename)
        if not filepath:
            not_found.append(filename)
            continue

        result = fix_file(filepath)
        if result:
            print(f"  FIXED: {filename}")
            fixed_count += 1
        else:
            print(f"  SKIP (already ok or no strings.): {filename}")

    if not_found:
        print(f"\n  NOT FOUND: {not_found}")

    # Also scan ALL .kt files for any we missed
    print("\n--- Scanning ALL screen files ---")
    for root, dirs, files in os.walk(SCREENS_DIR):
        for f in files:
            if not f.endswith(".kt") or f in TARGET_FILES:
                continue
            filepath = os.path.join(root, f)
            with open(filepath, "r") as fh:
                content = fh.read()
            if "strings." in content and "LocalStrings.current" not in content:
                result = fix_file(filepath)
                if result:
                    print(f"  EXTRA FIXED: {f}")
                    fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()
