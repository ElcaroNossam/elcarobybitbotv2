#!/usr/bin/env python3
"""
Apply STARK Design System to all CSS and HTML files
Replaces purple/blue colors with red/black/gold theme
"""

import os
import re

# Color replacements: OLD -> NEW
COLOR_REPLACEMENTS = {
    # Purple accents -> Red
    '#6366f1': '#dc2626',
    '#8b5cf6': '#991b1b',
    '#a855f7': '#7f1d1d',
    '#4f46e5': '#b91c1c',
    '#7c3aed': '#dc2626',
    '#818cf8': '#ef4444',
    '#a78bfa': '#f87171',
    
    # Blue accents -> Red/Gold
    '#3b82f6': '#dc2626',
    '#2563eb': '#b91c1c',
    '#1d4ed8': '#991b1b',
    '#60a5fa': '#ef4444',
    '#06b6d4': '#d4a017',  # Cyan -> Gold
    
    # Background adjustments
    '#0a0a0f': '#0a0a0a',
    '#111118': '#111111',
    '#16161f': '#1a1a1a',
    '#1e1e28': '#1f1f1f',
    '#0a0a0c': '#0a0a0a',
    '#111114': '#111111',
    '#1a1a1f': '#1a1a1a',
    '#0d0d0f': '#0a0a0a',
    '#141418': '#141414',
    '#1e1e24': '#1a1a1a',
    '#252530': '#242424',
    '#2a2a35': '#2a2a2a',
    
    # RGBA replacements
    'rgba(99, 102, 241': 'rgba(220, 38, 38',
    'rgba(139, 92, 246': 'rgba(153, 27, 27',
    'rgba(168, 85, 247': 'rgba(127, 29, 29',
    'rgba(79, 70, 229': 'rgba(185, 28, 28',
}

# Gradient replacements
GRADIENT_REPLACEMENTS = [
    # Purple gradients -> Red gradients
    (r'linear-gradient\(135deg,\s*#6366f1\s*0%,\s*#8b5cf6\s*50%,\s*#a855f7\s*100%\)',
     'linear-gradient(135deg, #dc2626 0%, #991b1b 50%, #7f1d1d 100%)'),
    (r'linear-gradient\(135deg,\s*#6366f1\s*0%,\s*#8b5cf6\s*100%\)',
     'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)'),
    (r'linear-gradient\(135deg,\s*#8b5cf6\s*0%,\s*#6366f1\s*100%\)',
     'linear-gradient(135deg, #991b1b 0%, #dc2626 100%)'),
    # Gold gradient
    (r'linear-gradient\(135deg,\s*#f59e0b\s*0%,\s*#fbbf24\s*50%,\s*#f59e0b\s*100%\)',
     'linear-gradient(135deg, #d4a017 0%, #b8860b 50%, #d4a017 100%)'),
]

# Variable name replacements
VAR_REPLACEMENTS = {
    '--accent-primary: #6366f1': '--accent-primary: #dc2626',
    '--accent-secondary: #8b5cf6': '--accent-secondary: #991b1b',
    '--accent-tertiary: #a855f7': '--accent-tertiary: #7f1d1d',
    '--accent: #6366f1': '--accent: #dc2626',
    '--accent-purple: #8b5cf6': '--accent-purple: #dc2626',
    '--accent-blue: #3b82f6': '--accent-blue: #dc2626',
    '--accent-cyan: #06b6d4': '--accent-cyan: #d4a017',
    '--border-accent: #4f46e5': '--border-accent: #dc2626',
}

# Shadow glow replacements
GLOW_REPLACEMENTS = {
    '0 0 40px rgba(99, 102, 241, 0.3)': '0 0 40px rgba(220, 38, 38, 0.4)',
    '0 0 20px rgba(99, 102, 241, 0.3)': '0 0 20px rgba(220, 38, 38, 0.4)',
    '0 8px 24px rgba(99, 102, 241, 0.3)': '0 8px 24px rgba(220, 38, 38, 0.3)',
    '0 8px 40px rgba(99, 102, 241, 0.5)': '0 8px 40px rgba(220, 38, 38, 0.5)',
    '0 12px 32px rgba(99, 102, 241, 0.4)': '0 12px 32px rgba(220, 38, 38, 0.4)',
}


def apply_replacements(content: str) -> str:
    """Apply all color replacements to content"""
    
    # Apply variable replacements first
    for old, new in VAR_REPLACEMENTS.items():
        content = content.replace(old, new)
    
    # Apply glow replacements
    for old, new in GLOW_REPLACEMENTS.items():
        content = content.replace(old, new)
    
    # Apply gradient replacements (regex)
    for pattern, replacement in GRADIENT_REPLACEMENTS:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Apply color replacements
    for old, new in COLOR_REPLACEMENTS.items():
        content = content.replace(old, new)
        content = content.replace(old.upper(), new.upper())
    
    return content


def process_file(filepath: str) -> bool:
    """Process a single file and return True if modified"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        modified = apply_replacements(original)
        
        if modified != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True
        return False
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")
        return False


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_dir = os.path.join(base_dir, 'webapp')
    
    # Files to process
    css_files = []
    html_files = []
    js_files = []
    
    # Find all CSS files
    css_dir = os.path.join(webapp_dir, 'static', 'css')
    if os.path.exists(css_dir):
        for f in os.listdir(css_dir):
            if f.endswith('.css'):
                css_files.append(os.path.join(css_dir, f))
    
    # Find all HTML templates
    templates_dir = os.path.join(webapp_dir, 'templates')
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for f in files:
                if f.endswith('.html'):
                    html_files.append(os.path.join(root, f))
    
    # Find all JS files
    js_dir = os.path.join(webapp_dir, 'static', 'js')
    if os.path.exists(js_dir):
        for f in os.listdir(js_dir):
            if f.endswith('.js'):
                js_files.append(os.path.join(js_dir, f))
    
    print("=" * 60)
    print("STARK Design System - Theme Converter")
    print("=" * 60)
    print(f"\nFound: {len(css_files)} CSS, {len(html_files)} HTML, {len(js_files)} JS files\n")
    
    modified_count = 0
    
    print("Processing CSS files...")
    for f in css_files:
        if process_file(f):
            print(f"  ✓ Modified: {os.path.basename(f)}")
            modified_count += 1
    
    print("\nProcessing HTML templates...")
    for f in html_files:
        if process_file(f):
            print(f"  ✓ Modified: {os.path.basename(f)}")
            modified_count += 1
    
    print("\nProcessing JS files...")
    for f in js_files:
        if process_file(f):
            print(f"  ✓ Modified: {os.path.basename(f)}")
            modified_count += 1
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: Modified {modified_count} files")
    print("=" * 60)
    print("\nSTARK Theme Applied:")
    print("  • Primary: #dc2626 (Iron Man Red)")
    print("  • Secondary: #991b1b (Dark Crimson)")
    print("  • Gold: #d4a017 (Premium Gold)")
    print("  • Background: #0a0a0a (Deep Black)")
    print("  • Card: #141414 (Graphite)")


if __name__ == '__main__':
    main()
