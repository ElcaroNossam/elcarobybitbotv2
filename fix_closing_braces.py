#!/usr/bin/env python3
"""Add closing braces to computed property dictionaries"""

filepath = '/Users/elcarosam/project/elcarobybitbotv2/ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Line numbers where static var declarations start (0-indexed: 187, 885, 1530, etc.)
dict_starts = [188, 886, 1531, 1637, 1734, 1831, 1928, 2025, 2122, 2219, 2316, 2413, 2510, 2607, 2704]

# Find closing brackets for each dictionary
# The pattern is: the line before next static var or class end that has just "    ]"

# Next dictionary starts at these lines, last one ends at class end
dict_ends = []
for i, start in enumerate(dict_starts):
    if i < len(dict_starts) - 1:
        next_start = dict_starts[i + 1]
        # Find ] before next_start
        for j in range(next_start - 1, start, -1):
            if lines[j-1].strip() == ']':
                dict_ends.append(j)
                break
    else:
        # Last dictionary - find ] before class end }
        for j in range(len(lines) - 1, start, -1):
            if lines[j-1].strip() == ']':
                dict_ends.append(j)
                break

print(f"Found dictionary ends at lines: {dict_ends}")

# Replace ] with ] } at these lines (from end to not mess up line numbers)
for line_num in reversed(dict_ends):
    idx = line_num - 1  # Convert to 0-indexed
    if lines[idx].strip() == ']':
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        lines[idx] = ' ' * indent + '] }\n'
        print(f"Fixed line {line_num}: ] -> ] }}")

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Done!")
