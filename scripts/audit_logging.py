#!/usr/bin/env python3
"""
Full Project Logging Audit
Checks all Python files for proper logging patterns
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Patterns to check
PATTERNS = {
    'bare_except': re.compile(r'^\s*except:\s*$', re.MULTILINE),
    'print_statement': re.compile(r'\bprint\s*\(', re.MULTILINE),
    'logger_exception': re.compile(r'logger\.exception\(', re.MULTILINE),
    'logger_error': re.compile(r'logger\.error\(', re.MULTILINE),
    'logger_warning': re.compile(r'logger\.warning\(', re.MULTILINE),
    'logger_info': re.compile(r'logger\.info\(', re.MULTILINE),
    'logger_debug': re.compile(r'logger\.debug\(', re.MULTILINE),
    'logging_getLogger': re.compile(r'logging\.getLogger\(', re.MULTILINE),
    'todo_comment': re.compile(r'#\s*TODO[:\s]', re.MULTILINE | re.IGNORECASE),
    'fixme_comment': re.compile(r'#\s*FIXME[:\s]', re.MULTILINE | re.IGNORECASE),
    'notimplemented': re.compile(r'NotImplementedError', re.MULTILINE),
    'pass_in_except': re.compile(r'except[^:]*:\s*\n\s*pass\s*$', re.MULTILINE),
}

# Directories to skip
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'ios', 'android', '.idea'}

# Files to skip (scripts with intentional prints)
SKIP_PRINT_CHECK = {
    'run_backend_tests.py',
    'run_backtest_tests.py',
    'check_translations.py',
    'audit_data.py',
    'verify_positions.py',
    'cleanup_positions.py',
    'test_bybit_api.py',
}


def audit_file(filepath: Path) -> Dict[str, List[int]]:
    """Audit a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return {}
    
    results = {}
    for pattern_name, pattern in PATTERNS.items():
        # Skip print check for CLI scripts
        if pattern_name == 'print_statement' and filepath.name in SKIP_PRINT_CHECK:
            continue
            
        matches = list(pattern.finditer(content))
        if matches:
            # Get line numbers
            lines = []
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                lines.append(line_num)
            results[pattern_name] = lines
    
    return results


def main():
    project_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🔍 FULL PROJECT LOGGING AUDIT")
    print("=" * 70)
    
    # Collect all Python files
    py_files = []
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)
    
    print(f"\n📊 Found {len(py_files)} Python files\n")
    
    # Audit statistics
    stats = {
        'files_with_bare_except': [],
        'files_with_print': [],
        'files_with_todo': [],
        'files_with_fixme': [],
        'files_with_notimplemented': [],
        'files_with_pass_in_except': [],
        'files_using_logging': 0,
        'total_logger_calls': 0,
    }
    
    issues = []
    
    for filepath in sorted(py_files):
        rel_path = filepath.relative_to(project_root)
        results = audit_file(filepath)
        
        if not results:
            continue
        
        # Check for issues
        if 'bare_except' in results:
            # Skip tests
            if 'tests/' not in str(rel_path):
                stats['files_with_bare_except'].append((rel_path, results['bare_except']))
                issues.append(f"❌ {rel_path}: bare except at lines {results['bare_except']}")
        
        if 'print_statement' in results and 'tests/' not in str(rel_path) and 'scripts/' not in str(rel_path) and 'migrations/' not in str(rel_path):
            stats['files_with_print'].append((rel_path, len(results['print_statement'])))
        
        if 'todo_comment' in results:
            stats['files_with_todo'].append((rel_path, results['todo_comment']))
        
        if 'fixme_comment' in results:
            stats['files_with_fixme'].append((rel_path, results['fixme_comment']))
        
        if 'notimplemented' in results:
            stats['files_with_notimplemented'].append((rel_path, results['notimplemented']))
        
        if 'pass_in_except' in results:
            if 'tests/' not in str(rel_path):
                stats['files_with_pass_in_except'].append((rel_path, results['pass_in_except']))
        
        # Count logging usage
        if 'logging_getLogger' in results:
            stats['files_using_logging'] += 1
        
        for key in ['logger_exception', 'logger_error', 'logger_warning', 'logger_info', 'logger_debug']:
            if key in results:
                stats['total_logger_calls'] += len(results[key])
    
    # Print results
    print("\n📋 AUDIT RESULTS")
    print("-" * 50)
    
    print(f"\n✅ Files using logging: {stats['files_using_logging']}")
    print(f"✅ Total logger calls: {stats['total_logger_calls']}")
    
    if stats['files_with_bare_except']:
        print(f"\n❌ BARE EXCEPT (production code): {len(stats['files_with_bare_except'])}")
        for path, lines in stats['files_with_bare_except'][:10]:
            print(f"   {path}: lines {lines}")
    else:
        print("\n✅ No bare except in production code")
    
    if stats['files_with_pass_in_except']:
        print(f"\n⚠️ PASS IN EXCEPT: {len(stats['files_with_pass_in_except'])}")
        for path, lines in stats['files_with_pass_in_except'][:5]:
            print(f"   {path}: lines {lines}")
    
    if stats['files_with_print']:
        print(f"\n⚠️ PRINT STATEMENTS (non-script): {len(stats['files_with_print'])}")
        for path, count in stats['files_with_print'][:10]:
            print(f"   {path}: {count} prints")
    
    if stats['files_with_todo']:
        print(f"\nℹ️ TODO comments: {len(stats['files_with_todo'])}")
        for path, lines in stats['files_with_todo'][:10]:
            print(f"   {path}: lines {lines[:5]}{'...' if len(lines) > 5 else ''}")
    
    if stats['files_with_notimplemented']:
        print(f"\n⚠️ NotImplementedError: {len(stats['files_with_notimplemented'])}")
        for path, lines in stats['files_with_notimplemented'][:5]:
            print(f"   {path}: lines {lines}")
    
    print("\n" + "=" * 70)
    
    # Overall assessment
    critical_issues = len(stats['files_with_bare_except'])
    warnings = len(stats['files_with_print']) + len(stats['files_with_pass_in_except'])
    
    if critical_issues == 0 and warnings < 5:
        print("✅ LOGGING AUDIT PASSED - Project is in good shape!")
    elif critical_issues == 0:
        print("⚠️ LOGGING AUDIT: Minor warnings, but no critical issues")
    else:
        print("❌ LOGGING AUDIT: Critical issues found, please fix!")
    
    print("=" * 70)
    
    return 0 if critical_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
