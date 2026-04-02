#!/usr/bin/env python3
"""
Comprehensive Tool Comparison: 4-Tiers vs Radon vs Pylint
==========================================================

Analyzes all 25 test files with all three tools for direct comparison.
"""

import sys
import time
import json
from pathlib import Path
from statistics import mean
import subprocess

sys.path.insert(0, '/Users/apple/Downloads/Py/4tiersCodeCheck_target')

from static_code_knot_analyzer import StaticCodeKnotAnalyzer
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

print("="*100)
print("TOOL COMPARISON: 4-Tiers vs Radon vs Pylint")
print("="*100)

# Test corpus
TEST_CORPUS = Path('test_corpus_expanded')
test_files = sorted(TEST_CORPUS.glob('*.py'))

print(f"\nAnalyzing {len(test_files)} files...\n")

# Header
header = f"{'File':<30} {'4-Tiers':<12} {'Radon':<12} {'Pylint':<10} {'Match':<8}"
print(header)
print("="*100)

results = []

for i, test_file in enumerate(test_files, 1):
    code = test_file.read_text()
    fname = test_file.name[:28]  # Truncate for display
    
    # 4-Tiers
    start = time.perf_counter()
    analyzer = StaticCodeKnotAnalyzer(str(test_file))
    knot_result = analyzer.analyze()
    time_4t = (time.perf_counter() - start) * 1000
    
    knot_score = knot_result.knot_score if knot_result else 0.0
    severity = knot_result.severity if knot_result else 'none'
    top_feature = max(knot_result.features.items(), key=lambda x: x[1])[0] if knot_result else '-'
    
    # Radon
    start = time.perf_counter()
    cc_blocks = cc_visit(code)
    max_cc = max((b.complexity for b in cc_blocks), default=0)
    try:
        mi_score = mi_visit(code, multi=True)
    except:
        mi_score = 0
    raw = analyze(code)
    time_radon = (time.perf_counter() - start) * 1000
    
    # Pylint (run once per file)
    start = time.perf_counter()
    try:
        result = subprocess.run(
            ['python3', '-m', 'pylint', str(test_file), '--errors-only', '-sn', '-r=n'],
            capture_output=True,
            text=True,
            timeout=30
        )
        pylint_issues = result.stdout.count('\n') if result.stdout else 0
        pylint_rating = 'OK' if pylint_issues == 0 else f'{pylint_issues} issues'
    except Exception as e:
        pylint_issues = -1
        pylint_rating = 'ERROR'
    time_pylint = (time.perf_counter() - start) * 1000
    
    # Agreement check
    # High complexity indicators:
    tiers_high = knot_score > 0.15 or severity in ['medium', 'high', 'critical']
    radon_high = max_cc > 5 or mi_score < 60
    pylint_high = pylint_issues > 0
    
    # Count how many tools flagged it
    flags = sum([tiers_high, radon_high, pylint_high])
    if flags == 3:
        match = "✅ ALL"
    elif flags == 2:
        match = "⚠️ 2/3"
    elif flags == 1:
        match = "⚠️ 1/3"
    else:
        match = "✅ None"
    
    # Print row
    print(f"{fname:<30} {knot_score:.3f}      {max_cc:>3} (MI{mi_score:.0f})  {pylint_rating:<10} {match}")
    
    results.append({
        'file': test_file.name,
        'category': test_file.name.split('_')[0],
        'lines': len(code.split('\n')),
        '4tiers': {
            'knot_score': knot_score,
            'severity': severity,
            'top_feature': top_feature,
            'time_ms': time_4t
        },
        'radon': {
            'max_cc': max_cc,
            'mi': mi_score,
            'loc': raw.loc,
            'time_ms': time_radon
        },
        'pylint': {
            'issues': pylint_issues,
            'time_ms': time_pylint
        },
        'agreement': {
            'tiers_flagged': tiers_high,
            'radon_flagged': radon_high,
            'pylint_flagged': pylint_high,
            'flags_count': flags
        }
    })

print("="*100)

# Summary statistics
print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)

# Performance
times_4t = [r['4tiers']['time_ms'] for r in results]
times_radon = [r['radon']['time_ms'] for r in results]
times_pylint = [r['pylint']['time_ms'] for r in results]

print("\n1. Performance (Average per file):")
print(f"   4-Tiers:  {mean(times_4t):.2f} ms")
print(f"   Radon:    {mean(times_radon):.2f} ms")
print(f"   Pylint:   {mean(times_pylint):.2f} ms")
print(f"   ")
print(f"   Ratio: 4-Tiers is {mean(times_radon)/mean(times_4t):.2f}x vs Radon, {mean(times_pylint)/mean(times_4t):.1f}x vs Pylint")

# Detection counts
print("\n2. Files Flagged by Each Tool:")
flagged_tiers = sum(1 for r in results if r['agreement']['tiers_flagged'])
flagged_radon = sum(1 for r in results if r['agreement']['radon_flagged'])
flagged_pylint = sum(1 for r in results if r['agreement']['pylint_flagged'])

print(f"   4-Tiers:  {flagged_tiers}/{len(results)} ({flagged_tiers/len(results)*100:.0f}%)")
print(f"   Radon:    {flagged_radon}/{len(results)} ({flagged_radon/len(results)*100:.0f}%)")
print(f"   Pylint:   {flagged_pylint}/{len(results)} ({flagged_pylint/len(results)*100:.0f}%)")

# Agreement
print("\n3. Agreement Between Tools:")
all_agree = sum(1 for r in results if r['agreement']['flags_count'] == 3)
two_agree = sum(1 for r in results if r['agreement']['flags_count'] == 2)
one_agree = sum(1 for r in results if r['agreement']['flags_count'] == 1)
none_agree = sum(1 for r in results if r['agreement']['flags_count'] == 0)

print(f"   All 3 flag:     {all_agree} files")
print(f"   2 of 3 flag:    {two_agree} files")
print(f"   1 of 3 flags:   {one_agree} files")
print(f"   None flag:      {none_agree} files")

# By category
print("\n4. Detection by Category:")
categories = {}
for r in results:
    cat = r['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(r)

print(f"   {'Category':<15} {'Files':<8} {'4-Tiers':<10} {'Radon':<10} {'Pylint':<10}")
print(f"   {'-'*60}")
for cat in sorted(categories.keys()):
    items = categories[cat]
    t = sum(1 for i in items if i['agreement']['tiers_flagged'])
    r = sum(1 for i in items if i['agreement']['radon_flagged'])
    p = sum(1 for i in items if i['agreement']['pylint_flagged'])
    print(f"   {cat:<15} {len(items):<8} {t}/{len(items):<8} {r}/{len(items):<8} {p}/{len(items)}")

# Unique detections
print("\n5. Unique Detections (only that tool flagged):")
only_tiers = [r['file'] for r in results if r['agreement']['tiers_flagged'] and not r['agreement']['radon_flagged'] and not r['agreement']['pylint_flagged']]
only_radon = [r['file'] for r in results if r['agreement']['radon_flagged'] and not r['agreement']['tiers_flagged'] and not r['agreement']['pylint_flagged']]
only_pylint = [r['file'] for r in results if r['agreement']['pylint_flagged'] and not r['agreement']['tiers_flagged'] and not r['agreement']['radon_flagged']]

print(f"   Only 4-Tiers:   {len(only_tiers)} files")
for f in only_tiers[:3]:
    print(f"     - {f}")
if len(only_tiers) > 3:
    print(f"     ... and {len(only_tiers)-3} more")

print(f"   Only Radon:     {len(only_radon)} files")
for f in only_radon[:3]:
    print(f"     - {f}")

print(f"   Only Pylint:    {len(only_pylint)} files")
for f in only_pylint[:3]:
    print(f"     - {f}")

# Save results
with open('tool_comparison_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Detailed results saved to: tool_comparison_results.json")
print("="*100)
