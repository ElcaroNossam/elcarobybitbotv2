#!/usr/bin/env python3
"""Fix static let to computed properties in LocalizationManager.swift"""

import re

filepath = '/Users/elcarosam/project/elcarobybitbotv2/ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'

with open(filepath, 'r') as f:
    content = f.read()

# Count replacements
count = 0

# Replace: static let xxxTranslations: [String: String] = [
# With:    static var xxxTranslations: [String: String] { return [
def replace_decl(match):
    global count
    count += 1
    name = match.group(1)
    return f'static var {name}: [String: String] {{ return ['

content = re.sub(
    r'static let (\w+Translations): \[String: String\] = \[',
    replace_decl,
    content
)

print(f"Replaced {count} translation dictionary declarations")

# Now we need to add closing } after each ] that ends a dictionary
# The dictionaries end with a line that has just "    ]" (4 spaces + ])
# followed by empty line or next static var

# Find positions of all "static var ...Translations" 
positions = [m.start() for m in re.finditer(r'static var \w+Translations:', content)]
positions.append(len(content))  # Add end of file

# For each dictionary, find its closing ] and add }
result_parts = []
last_end = 0

for i, pos in enumerate(positions[:-1]):
    next_pos = positions[i + 1]
    chunk = content[last_end:next_pos]
    
    # Find the last ] before next dictionary that closes this one
    # Pattern: find "    ]" followed by newline(s) before next static var
    # Replace it with "    ] }"
    
    # Find the ] that closes the dictionary (it's the one before next static var)
    # We look for the pattern: "]" at end of chunk (possibly with whitespace/newlines)
    chunk = re.sub(r'\]\s*$', '] }', chunk.rstrip()) + '\n\n'
    
    result_parts.append(chunk)
    last_end = next_pos

# Add remaining content after last dictionary
result_parts.append(content[positions[-2]:])

# Actually, simpler approach - just find each ] that ends a translation dict
# The pattern is: ] followed by newlines and then "static var" or end of class

# Let's try different approach - find all ] that are followed by "static var" or "}"
content = re.sub(r'\]\s*\n(\s*static var \w+Translations:)', r'] }\n\n\1', content)

# Also close the last dictionary (before end of class)
content = re.sub(r'\]\s*\n(\s*}\s*$)', r'] }\n\1', content)

with open(filepath, 'w') as f:
    f.write(content)

print("Done! File updated.")
