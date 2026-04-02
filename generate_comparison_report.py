#!/usr/bin/env python3
"""Generate comprehensive comparison report from results."""

import json
from collections import defaultdict
import statistics

with open('comparison_61files_results.json') as f:
    results = json.load(f)

print("="*80)
print("COMPREHENSIVE TOOL COMPARISON REPORT - 61 FILES")
print("="*80)

# Overall statistics
print("\n📊 OVERALL STATISTICS")
print("-"*80)

# 4-Tiers stats
tiers_scores = [r['tiers_4']['knot_score'] for r in results]
tiers_times = [r['tiers_4']['time_ms'] for r in results]

# Radon stats
radon_cc = [r['radon']['max_cc'] for r in results]
radon_times = [r['radon']['time_ms'] for r in results]

# Pylint stats
pylint_issues = [r['pylint']['issues'] for r in results]
pylint_times = [r['pylint']['time_ms'] for r in results]

# Feature A v5 stats
fa_v5_scores = [r['feature_a_v5']['score'] for r in results]
fa_v5_times = [r['feature_a_v5']['time_ms'] for r in results]

print(f"{'Metric':<30} {'4-Tiers':>12} {'Radon':>12} {'Pylint':>12} {'FeatA-v5':>12}")
print("-"*80)
print(f"{'Mean Score/CC/Issues':<30} {statistics.mean(tiers_scores):>12.3f} {statistics.mean(radon_cc):>12.1f} {statistics.mean(pylint_issues):>12.1f} {statistics.mean(fa_v5_scores):>12.3f}")
print(f"{'Median Score/CC/Issues':<30} {statistics.median(tiers_scores):>12.3f} {statistics.median(radon_cc):>12.1f} {statistics.median(pylint_issues):>12.1f} {statistics.median(fa_v5_scores):>12.3f}")
print(f"{'Max Score/CC/Issues':<30} {max(tiers_scores):>12.3f} {max(radon_cc):>12.1f} {max(pylint_issues):>12.1f} {max(fa_v5_scores):>12.3f}")
print(f"{'Files with Issues (>0)':<30} {sum(1 for s in tiers_scores if s > 0.15):>12} {sum(1 for c in radon_cc if c > 5):>12} {sum(1 for i in pylint_issues if i > 0):>12} {sum(1 for s in fa_v5_scores if s > 0.25):>12}")
print(f"{'Total Time (ms)':<30} {sum(tiers_times):>12.2f} {sum(radon_times):>12.2f} {sum(pylint_times):>12.2f} {sum(fa_v5_times):>12.2f}")
print(f"{'Mean Time (ms)':<30} {statistics.mean(tiers_times):>12.3f} {statistics.mean(radon_times):>12.3f} {statistics.mean(pylint_times):>12.3f} {statistics.mean(fa_v5_times):>12.3f}")

# Category analysis
print("\n\n📁 RESULTS BY CATEGORY")
print("-"*80)
print(f"{'Category':<15} {'Files':>6} {'4-Tiers':>10} {'Radon':>10} {'Pylint':>10} {'FeatA-v5':>10}")
print("-"*80)

categories = ['simple', 'medium', 'complex', 'duplicate', 'issues', 'mixed', 'edge', 'realistic']
for cat in categories:
    cat_results = [r for r in results if r['category'] == cat]
    if not cat_results:
        continue
    
    tiers_avg = statistics.mean([r['tiers_4']['knot_score'] for r in cat_results])
    radon_avg = statistics.mean([r['radon']['max_cc'] for r in cat_results])
    pylint_avg = statistics.mean([r['pylint']['issues'] for r in cat_results])
    fav5_avg = statistics.mean([r['feature_a_v5']['score'] for r in cat_results])
    
    print(f"{cat:<15} {len(cat_results):>6} {tiers_avg:>10.3f} {radon_avg:>10.1f} {pylint_avg:>10.1f} {fav5_avg:>10.3f}")

# Duplicate category detailed analysis
print("\n\n🔍 DUPLICATE CATEGORY DETAILED ANALYSIS")
print("-"*80)
print(f"{'File':<30} {'4-Tiers':>10} {'Radon CC':>10} {'Pylint':>10} {'FeatA-v5':>10} {'Detected':>10}")
print("-"*80)

dup_results = [r for r in results if r['category'] == 'duplicate']
for r in sorted(dup_results, key=lambda x: x['file']):
    ks = r['tiers_4']['knot_score']
    cc = r['radon']['max_cc']
    pl = r['pylint']['issues']
    fav = r['feature_a_v5']['score']
    detected = "✅" if fav > 0.25 else "❌"
    print(f"{r['file']:<30} {ks:>10.3f} {cc:>10.0f} {pl:>10} {fav:>10.3f} {detected:>10}")

# Feature A detection analysis
print("\n\n📈 FEATURE A DETECTION ANALYSIS")
print("-"*80)

# Count detections by category
print("\nDetection Count by Category (threshold: >0.25):")
for cat in categories:
    cat_results = [r for r in results if r['category'] == cat]
    detected = sum(1 for r in cat_results if r['feature_a_v5']['score'] > 0.25)
    print(f"  {cat:<15}: {detected}/{len(cat_results)} files ({detected/len(cat_results)*100:.0f}%)")

# Issues category analysis
print("\n\n⚠️  ISSUES CATEGORY DETAILED ANALYSIS")
print("-"*80)
print(f"{'File':<30} {'4-Tiers':>10} {'Radon CC':>10} {'Pylint':>10} {'FeatA-v5':>10}")
print("-"*80)

issue_results = [r for r in results if r['category'] == 'issues']
for r in sorted(issue_results, key=lambda x: x['file']):
    ks = r['tiers_4']['knot_score']
    cc = r['radon']['max_cc']
    pl = r['pylint']['issues']
    fav = r['feature_a_v5']['score']
    print(f"{r['file']:<30} {ks:>10.3f} {cc:>10.0f} {pl:>10} {fav:>10.3f}")

# Performance comparison
print("\n\n⚡ PERFORMANCE COMPARISON")
print("-"*80)

# Calculate speedup ratios
tiers_total = sum(tiers_times)
radon_total = sum(radon_times)
pylint_total = sum(pylint_times)
fav5_total = sum(fa_v5_times)

print(f"Total execution time (61 files):")
print(f"  4-Tiers:   {tiers_total:>10.2f} ms")
print(f"  Radon:     {radon_total:>10.2f} ms")
print(f"  Pylint:    {pylint_total:>10.2f} ms")
print(f"  FeatureA:  {fav5_total:>10.2f} ms")

print(f"\nSpeedup vs Pylint:")
if pylint_total > 0:
    print(f"  4-Tiers is {pylint_total/tiers_total:.1f}x faster than Pylint")
    print(f"  Radon is {pylint_total/radon_total:.1f}x faster than Pylint")
    print(f"  FeatureA is {pylint_total/fav5_total:.1f}x faster than Pylint")

# Key insights
print("\n\n💡 KEY INSIGHTS")
print("-"*80)

# Feature A detection quality
dup_detected = sum(1 for r in dup_results if r['feature_a_v5']['score'] > 0.25)
non_dup_detected = sum(1 for r in results if r['category'] != 'duplicate' and r['feature_a_v5']['score'] > 0.25)
non_dup_total = sum(1 for r in results if r['category'] != 'duplicate')

print(f"1. Feature A v5 Duplication Detection:")
print(f"   - True Positives: {dup_detected}/{len(dup_results)} ({dup_detected/len(dup_results)*100:.0f}%)")
print(f"   - False Positives: {non_dup_detected}/{non_dup_total} ({non_dup_detected/non_dup_total*100:.1f}%)")

# 4-Tiers unique capabilities
has_todos = sum(1 for r in results if 'E' in r['tiers_4'].get('features', {}) and r['tiers_4']['features'].get('E', 0) > 0)
print(f"\n2. 4-Tiers Unique Detections:")
print(f"   - Files with TODOs detected: {has_todos}")

# Complexity correlation
print(f"\n3. Complexity Comparison:")
high_complexity_4t = sum(1 for r in results if r['tiers_4']['knot_score'] > 0.25)
high_complexity_radon = sum(1 for r in results if r['radon']['max_cc'] > 5)
print(f"   - 4-Tiers flagged: {high_complexity_4t} files as high-complexity")
print(f"   - Radon flagged: {high_complexity_radon} files as high-complexity (CC>5)")

print("\n" + "="*80)
print("END OF REPORT")
print("="*80)
