#!/usr/bin/env python3
"""
Update WebApp HTML templates with unified CSS/JS imports.
Adds components.css, animations.css, and dynamic.js to all templates.
"""

import os
import re
from pathlib import Path

TEMPLATES_DIR = Path("/Users/elcarosam/project/elcarobybitbotv2/webapp/templates")

# CSS imports to add (after base.css or in head)
NEW_CSS_IMPORTS = """
    <!-- Unified Components & Animations -->
    <link rel="stylesheet" href="/static/css/components.css">
    <link rel="stylesheet" href="/static/css/animations.css">
"""

# JS import to add (before closing </body>)
NEW_JS_IMPORT = """
    <!-- Dynamic Effects -->
    <script src="/static/js/dynamic.js"></script>
"""

def update_css_imports(content: str) -> str:
    """Add CSS imports if not already present."""
    if 'components.css' in content:
        return content  # Already has imports
    
    # Try to insert after base.css
    if '/static/css/base.css' in content:
        content = re.sub(
            r'(<link[^>]*href="/static/css/base\.css"[^>]*>)',
            r'\1' + NEW_CSS_IMPORTS,
            content
        )
        return content
    
    # Try to insert before </head>
    if '</head>' in content:
        content = content.replace('</head>', NEW_CSS_IMPORTS + '</head>')
    
    return content

def update_js_imports(content: str) -> str:
    """Add JS import if not already present."""
    if 'dynamic.js' in content:
        return content  # Already has import
    
    # Insert before </body>
    if '</body>' in content:
        content = content.replace('</body>', NEW_JS_IMPORT + '</body>')
    
    return content

def add_scroll_reveal_classes(content: str) -> str:
    """Add scroll-reveal class to key elements."""
    # Add to section elements
    content = re.sub(
        r'<section([^>]*)class="([^"]*)"',
        r'<section\1class="\2 scroll-reveal"',
        content
    )
    
    # Add to feature cards
    content = re.sub(
        r'class="feature-card([^"]*)"',
        r'class="feature-card\1 scroll-reveal"',
        content
    )
    
    # Add to stat cards
    content = re.sub(
        r'class="stat-card([^"]*)"',
        lambda m: f'class="stat-card{m.group(1)} scroll-reveal"' if 'scroll-reveal' not in m.group(0) else m.group(0),
        content
    )
    
    return content

def add_hover_effects(content: str) -> str:
    """Add hover effect classes to interactive elements."""
    # Add hover-lift to cards without it
    content = re.sub(
        r'class="([^"]*card[^"]*)"',
        lambda m: f'class="{m.group(1)} hover-lift"' if 'hover-' not in m.group(1) else m.group(0),
        content
    )
    
    return content

def process_template(filepath: Path) -> bool:
    """Process a single template file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Update imports
        content = update_css_imports(content)
        content = update_js_imports(content)
        
        # Add animation classes
        content = add_scroll_reveal_classes(content)
        content = add_hover_effects(content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("🎨 Updating WebApp Templates with Unified CSS/JS")
    print("=" * 50)
    
    updated = 0
    skipped = 0
    errors = 0
    
    # Skip backup files
    skip_patterns = ['_backup', '_old', '_copy']
    
    for filepath in sorted(TEMPLATES_DIR.glob('*.html')):
        name = filepath.name
        
        # Skip backup files
        if any(p in name for p in skip_patterns):
            print(f"⏭️  Skipping backup: {name}")
            skipped += 1
            continue
        
        print(f"📄 Processing: {name}")
        if process_template(filepath):
            print(f"   ✅ Updated")
            updated += 1
        else:
            print(f"   ⏭️  No changes needed")
            skipped += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Updated: {updated}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print("🎉 Done!")

if __name__ == "__main__":
    main()
