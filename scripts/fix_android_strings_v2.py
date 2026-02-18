#!/usr/bin/env python3
"""Fix ALL @Composable functions that use strings. but don't declare val strings = LocalStrings.current"""

import os
import re

SCREENS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "android", "EnlikoTrading", "app", "src", "main",
    "java", "io", "enliko", "trading", "ui", "screens"
)

IMPORT_LINE = "import io.enliko.trading.util.LocalStrings"
STRINGS_DECL = "    val strings = LocalStrings.current"


def ensure_import(lines):
    """Ensure import line exists."""
    content = "\n".join(lines)
    if IMPORT_LINE in content:
        return lines, False
    last_import = 0
    for i, line in enumerate(lines):
        if line.startswith("import "):
            last_import = i
    lines.insert(last_import + 1, IMPORT_LINE)
    return lines, True


def find_composable_functions(lines):
    """Find all @Composable function start lines and their opening brace line."""
    composables = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("@Composable"):
            # Look for 'fun' declaration after this
            j = i + 1
            while j < len(lines) and j < i + 5:
                if "fun " in lines[j]:
                    # Find the opening brace
                    k = j
                    while k < len(lines):
                        if "{" in lines[k]:
                            composables.append(k)  # line with opening brace
                            break
                        k += 1
                    break
                j += 1
        i += 1
    return composables


def get_function_body_range(lines, brace_line):
    """Get the range of lines for a function body (from opening { to matching })."""
    depth = 0
    start = brace_line
    for i in range(brace_line, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return (start, i)
    return (start, len(lines) - 1)


def function_uses_strings(lines, start, end):
    """Check if function body uses strings. reference."""
    for i in range(start, end + 1):
        if "strings." in lines[i]:
            return True
    return False


def function_has_strings_decl(lines, start, end):
    """Check if function body already has val strings = LocalStrings.current."""
    for i in range(start + 1, min(start + 5, end + 1)):
        if "val strings = LocalStrings.current" in lines[i]:
            return True
    return False


def process_file(filepath):
    """Process a single .kt file."""
    with open(filepath, "r") as f:
        lines = f.read().split("\n")

    if not any("strings." in line for line in lines):
        return False

    modified = False

    # Ensure import
    lines, imp_changed = ensure_import(lines)
    if imp_changed:
        modified = True

    # Find all composable functions
    composable_braces = find_composable_functions(lines)

    # Process in reverse order so line insertions don't shift later indices
    injections = []
    for brace_line in composable_braces:
        start, end = get_function_body_range(lines, brace_line)
        if function_uses_strings(lines, start, end) and not function_has_strings_decl(lines, start, end):
            # Determine indentation
            base_indent = ""
            for ch in lines[brace_line]:
                if ch in " \t":
                    base_indent += ch
                else:
                    break
            inner_indent = base_indent + "    "
            injections.append((brace_line, inner_indent + "val strings = LocalStrings.current"))

    # Apply injections in reverse order
    for brace_line, decl_line in sorted(injections, reverse=True):
        lines.insert(brace_line + 1, decl_line)
        modified = True

    if modified:
        with open(filepath, "w") as f:
            f.write("\n".join(lines))

    return modified


def main():
    fixed = 0
    for root, dirs, files in os.walk(SCREENS_DIR):
        for f in files:
            if not f.endswith(".kt"):
                continue
            filepath = os.path.join(root, f)
            if process_file(filepath):
                relpath = os.path.relpath(filepath, SCREENS_DIR)
                print(f"  FIXED: {relpath}")
                fixed += 1

    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
