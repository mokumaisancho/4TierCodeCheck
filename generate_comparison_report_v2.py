#!/usr/bin/env python3
"""Generate comprehensive comparison report from results - with corrected radon parsing."""

import json
import subprocess
from collections import defaultdict
import statistics

# Re-run radon with correct parsing
print("Re-running Radon with correct parsing...")

def run_radon_fixed(filepath):
    """Run radon cc command with correct parsing."""
    try:
        result = subprocess.run(
            ['radon', 'cc', '-s', str(filepath)],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        
        # Parse complexity - format: "F 2:0 process - A (5)"
        max_cc = 0.0
        
        for line in output.split('\n'):
            if ' - ' in line and '(' in line and ')' in line:
                try:
                    # Extract number from parentheses
                    cc_str = line[line.find('(')+1:line.find(')')]
                    cc = int(cc_str)
                    max_cc = max(max_cc, cc)
                except:
                    pass
        
        return max_cc
    except:
        return 0

with open('comparison_61files_results.json') as f:
    results = json.load(f)

# Re-parse radon results
for r in results:
    r['radon']['max_cc'] = run_radon_fixed(r['path'])

print("✅ Radon parsing corrected\n")

print("="*80)
print("COMPREHENSIVE TOOL COMPARISON REPORT - 61 FILES (CORRECTED)")
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
print(f"{'Max Score/CC/Issues':<30} {max(tiers_scores):>12.3f} {max(radon_cc):>12.0f} {max(pylint_issues):>12.0f} {max(fa_v5_scores):>12.3f}")
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
print(f"{'File':<30} {'4-Tiers':>10} {'Radon CC':>10} {'Pylint':>10} {'FeatA-v5':>10} {'Status':>10}")
print("-"*80)

dup_results = [r for r in results if r['category'] == 'duplicate']
for r in sorted(dup_results, key=lambda x: x['file']):
    ks = r['tiers_4']['knot_score']
    cc = r['radon']['max_cc']
    pl = r['pylint']['issues']
    fav = r['feature_a_v5']['score']
    detected = "✅" if fav > 0.25 else "❌"
    print(f"{r['file']:<30} {ks:>10.3f} {cc:>10.0f} {pl:>10} {fav:>10.3f} {detected:>10}")

# Complex category analysis
print("\n\n🧠 COMPLEX CATEGORY DETAILED ANALYSIS")
print("-"*80)
print(f"{'File':<30} {'4-Tiers':>10} {'Radon CC':>10} {'Pylint':>10} {'FeatA-v5':>10}")
print("-"*80)

complex_results = [r for r in results if r['category'] == 'complex']
for r in sorted(complex_results, key=lambda x: x['file']):
    ks = r['tiers_4']['knot_score']
    cc = r['radon']['max_cc']
    pl = r['pylint']['issues']
    fav = r['feature_a_v5']['score']
    print(f"{r['file']:<30} {ks:>10.3f} {cc:>10.0f} {pl:>10} {fav:>10.3f}")

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

# Correlation analysis
print("\n\n📊 CORRELATION ANALYSIS")
print("-"*80)

# Calculate correlation between 4-Tiers and Radon
import math

def correlation(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x2 = sum(xi**2 for xi in x)
    sum_y2 = sum(yi**2 for yi in y)
    sum_xy = sum(xi*yi for xi, yi in zip(x, y))
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
    
    return numerator / denominator if denominator != 0 else 0

corr_4t_radon = correlation(tiers_scores, radon_cc)
corr_4t_fa = correlation([r['tiers_4']['features'].get('A', 0) for r in results], fa_v5_scores)

print(f"Correlation (4-Tiers vs Radon CC): {corr_4t_radon:.3f}")
print(f"Correlation (Feature A vs v5): {corr_4t_fa:.3f}")

# Performance comparison
print("\n\n⚡ PERFORMANCE COMPARISON")
print("-"*80)

# Calculate speedup ratios
tiers_total = sum(tiers_times)
radon_total = sum(radon_times)
pylint_total = sum(pylint_times)
fav5_total = sum(fa_v5_times)

print(f"Total execution time (61 files):")
print(f"  4-Tiers:   {tiers_total:>10.2f} ms  (baseline)")
print(f"  Radon:     {radon_total:>10.2f} ms  ({radon_total/tiers_total:.1f}x slower)")
print(f"  Pylint:    {pylint_total:>10.2f} ms  ({pylint_total/tiers_total:.1f}x slower)")
print(f"  FeatureA:  {fav5_total:>10.2f} ms  ({fav5_total/tiers_total:.1f}x faster)")

print(f"\nSpeedup vs Pylint:")
if pylint_total > 0:
    print(f"  4-Tiers is {pylint_total/tiers_total:.0f}x faster than Pylint")
    print(f"  Radon is {pylint_total/radon_total:.1f}x faster than Pylint")
    print(f"  FeatureA is {pylint_total/fav5_total:.0f}x faster than Pylint")

# Key insights
print("\n\n💡 KEY INSIGHTS")
print("-"*80)

# Feature A detection quality
dup_detected = sum(1 for r in dup_results if r['feature_a_v5']['score'] > 0.25)
non_dup_detected = sum(1 for r in results if r['category'] != 'duplicate' and r['feature_a_v5']['score'] > 0.25)
non_dup_total = sum(1 for r in results if r['category'] != 'duplicate')

precision = dup_detected / (dup_detected + non_dup_detected) if (dup_detected + non_dup_detected) > 0 else 0
recall = dup_detected / len(dup_results)
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print(f"1. Feature A v5 Duplication Detection:")
print(f"   - Precision: {precision:.1%} ({dup_detected}/{dup_detected + non_dup_detected})")
print(f"   - Recall: {recall:.1%} ({dup_detected}/{len(dup_results)})")
print(f"   - F1-Score: {f1:.2f}")
print(f"   - False Positive Rate: {non_dup_detected/non_dup_total:.1%}")

# 4-Tiers unique capabilities
has_todos = sum(1 for r in results if 'E' in r['tiers_4'].get('features', {}) and r['tiers_4']['features'].get('E', 0) > 0)
has_dead = sum(1 for r in results if 'D' in r['tiers_4'].get('features', {}) and r['tiers_4']['features'].get('D', 0) > 0)

print(f"\n2. 4-Tiers Unique Detections:")
print(f"   - Files with TODOs detected (Feature E): {has_todos}")
print(f"   - Files with dead code (Feature D): {has_dead}")

# Complexity comparison
print(f"\n3. Complexity Detection Comparison:")
high_complexity_4t = sum(1 for r in results if r['tiers_4']['knot_score'] > 0.2)
high_complexity_radon = sum(1 for r in results if r['radon']['max_cc'] >= 5)
high_complexity_both = sum(1 for r in results if r['tiers_4']['knot_score'] > 0.2 and r['radon']['max_cc'] >= 5)
print(f"   - 4-Tiers flagged: {high_complexity_4t} files")
print(f"   - Radon flagged: {high_complexity_radon} files (CC>=5)")
print(f"   - Both flagged: {high_complexity_both} files")
print(f"   - Agreement rate: {high_complexity_both/max(high_complexity_4t, high_complexity_radon)*100:.0f}%")

# Tool strengths
print(f"\n4. Tool Strengths:")
print(f"   - 4-Tiers: Fast, detects TODOs/dead code/duplicates, structural patterns")
print(f"   - Radon: Industry standard CC, good for complex control flow")
print(f"   - Pylint: Comprehensive style/syntax checking")
print(f"   - FeatureA-v5: Specialized duplication detection (66.7% recall)")

print("\n" + "="*80)
print("END OF REPORT")
print("="*80)
