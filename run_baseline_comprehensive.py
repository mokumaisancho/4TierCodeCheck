#!/usr/bin/env python3
"""
Comprehensive Baseline Comparison Study
=======================================

Fixed conditions, expanded corpus, Spearman correlation.
"""

import sys
import time
import json
import platform
import subprocess
from pathlib import Path
from statistics import mean, stdev

# Add paths
sys.path.insert(0, '/Users/apple/Downloads/Py/4tiersCodeCheck_target')

# System info
SYSTEM_INFO = {
    "python_version": platform.python_version(),
    "platform": platform.platform(),
    "processor": platform.processor() or "Apple Silicon",
    "machine": platform.machine(),
}

print("="*80)
print("COMPREHENSIVE BASELINE COMPARISON STUDY")
print("="*80)
print(f"\nSystem Configuration:")
print(f"  Python: {SYSTEM_INFO['python_version']}")
print(f"  Platform: {SYSTEM_INFO['platform']}")
print(f"  Processor: {SYSTEM_INFO['processor']}")
print(f"  Machine: {SYSTEM_INFO['machine']}")

# Test corpus - expanded to 25 files
TEST_CORPUS = Path('test_corpus_expanded')
test_files = list(TEST_CORPUS.glob('*.py')) if TEST_CORPUS.exists() else []

if not test_files:
    print("\n⚠️  Expanded corpus not found, using basic corpus")
    TEST_CORPUS = Path('test_corpus')
    test_files = list(TEST_CORPUS.glob('*.py'))

print(f"\nTest Corpus: {len(test_files)} files from {TEST_CORPUS}/")

# Imports
from static_code_knot_analyzer import StaticCodeKnotAnalyzer
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

# Warmup - cold cache
print("\n" + "="*80)
print("WARMUP PHASE (Cold → Hot Cache)")
print("="*80)

warmup_file = test_files[0] if test_files else None
if warmup_file:
    print(f"\nWarming up with {warmup_file.name}...")
    
    # Cold run
    start = time.perf_counter()
    analyzer = StaticCodeKnotAnalyzer(str(warmup_file))
    _ = analyzer.analyze()
    cold_time = time.perf_counter() - start
    print(f"  Cold run: {cold_time*1000:.2f} ms")
    
    # Hot runs
    hot_times = []
    for i in range(3):
        start = time.perf_counter()
        analyzer = StaticCodeKnotAnalyzer(str(warmup_file))
        _ = analyzer.analyze()
        hot_times.append(time.perf_counter() - start)
    
    hot_time = mean(hot_times)
    print(f"  Hot run:  {hot_time*1000:.2f} ms (avg of 3)")
    print(f"  Cache effect: {(cold_time/hot_time - 1)*100:.1f}% slower when cold")

# Main analysis
print("\n" + "="*80)
print("MAIN ANALYSIS (Hot Cache)")
print("="*80)

results = []

for i, test_file in enumerate(test_files):
    print(f"\n[{i+1}/{len(test_files)}] {test_file.name}")
    
    code = test_file.read_text()
    
    # 4-Tiers analysis (hot cache - multiple runs)
    times_4tiers = []
    for _ in range(3):
        start = time.perf_counter()
        analyzer = StaticCodeKnotAnalyzer(str(test_file))
        knot_result = analyzer.analyze()
        times_4tiers.append(time.perf_counter() - start)
    
    time_4tiers = mean(times_4tiers) * 1000  # ms
    
    # Radon analysis (hot cache)
    times_radon = []
    for _ in range(3):
        start = time.perf_counter()
        cc_blocks = cc_visit(code)
        max_cc = max((b.complexity for b in cc_blocks), default=0)
        avg_cc = mean([b.complexity for b in cc_blocks]) if cc_blocks else 0
        try:
            mi_score = mi_visit(code, multi=True)
        except:
            mi_score = 0
        raw = analyze(code)
        times_radon.append(time.perf_counter() - start)
    
    time_radon = mean(times_radon) * 1000  # ms
    
    # Store results
    result_data = {
        'file': test_file.name,
        'category': test_file.name.split('_')[0],  # simple, medium, complex, etc.
        'lines': len(code.split('\n')),
        'radon_max_cc': max_cc,
        'radon_avg_cc': avg_cc,
        'radon_mi': mi_score,
        'radon_loc': raw.loc,
        'time_4tiers_ms': time_4tiers,
        'time_radon_ms': time_radon,
    }
    
    if knot_result:
        result_data.update({
            'knot_score': knot_result.knot_score,
            'severity': knot_result.severity,
            'feature_a': knot_result.features['A'],
            'feature_b': knot_result.features['B'],
            'feature_c': knot_result.features['C'],
            'feature_d': knot_result.features['D'],
            'feature_e': knot_result.features['E'],
            'feature_f': knot_result.features['F'],
            'feature_h': knot_result.features['H'],
        })
    
    results.append(result_data)
    print(f"  4-Tiers: {time_4tiers:.2f} ms | Radon: {time_radon:.2f} ms | CC: {max_cc}")

# Statistical analysis
print("\n" + "="*80)
print("STATISTICAL ANALYSIS")
print("="*80)

def pearson_corr(x, y):
    """Calculate Pearson correlation."""
    n = len(x)
    if n < 2:
        return 0
    mx, my = mean(x), mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    denx = sum((xi - mx) ** 2 for xi in x) ** 0.5
    deny = sum((yi - my) ** 2 for yi in y) ** 0.5
    return num / (denx * deny) if denx * deny > 0 else 0

def spearman_corr(x, y):
    """Calculate Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0
    
    # Rank the data
    x_rank = [sorted(x).index(v) + 1 for v in x]
    y_rank = [sorted(y).index(v) + 1 for v in y]
    
    # Pearson on ranks
    return pearson_corr(x_rank, y_rank)

# Extract data for correlation
knot_scores = [r['knot_score'] for r in results if 'knot_score' in r]
feature_f = [r['feature_f'] for r in results if 'feature_f' in r]
radon_cc = [r['radon_max_cc'] for r in results]

# Performance
print("\n1. Performance (Hot Cache):")
print("-" * 50)
times_4t = [r['time_4tiers_ms'] for r in results]
times_rd = [r['time_radon_ms'] for r in results]

print(f"4-Tiers:  {mean(times_4t):.2f} ± {stdev(times_4t):.2f} ms")
print(f"Radon:    {mean(times_rd):.2f} ± {stdev(times_rd):.2f} ms")
print(f"Ratio:    4-Tiers is {mean(times_rd)/mean(times_4t):.2f}x relative to Radon")

# Correlations
print("\n2. Complexity Correlations:")
print("-" * 50)

if len(feature_f) == len(radon_cc) and len(feature_f) > 1:
    p_f_cc = pearson_corr(feature_f, radon_cc)
    s_f_cc = spearman_corr(feature_f, radon_cc)
    
    print(f"Feature F vs Radon Max CC:")
    print(f"  Pearson:  {p_f_cc:.3f}")
    print(f"  Spearman: {s_f_cc:.3f}")
    
    if abs(p_f_cc) > 0.7:
        print(f"  ✅ Strong correlation")
    elif abs(p_f_cc) > 0.4:
        print(f"  ⚠️  Moderate correlation")
    else:
        print(f"  ❌ Weak correlation")

# Detection agreement by category
print("\n3. Detection by Category:")
print("-" * 50)
print(f"{'Category':<15} {'Files':<8} {'Avg Knot':<10} {'Avg CC':<10} {'Agreement'}")
print("-" * 60)

categories = {}
for r in results:
    cat = r['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(r)

for cat, items in sorted(categories.items()):
    avg_knot = mean([i.get('knot_score', 0) for i in items])
    avg_cc = mean([i['radon_max_cc'] for i in items])
    
    # Agreement check
    agrees = 0
    for i in items:
        knot_high = i.get('knot_score', 0) > 0.15
        cc_high = i['radon_max_cc'] > 5
        if knot_high == cc_high:
            agrees += 1
    
    agreement = f"{agrees}/{len(items)}"
    print(f"{cat:<15} {len(items):<8} {avg_knot:.3f}      {avg_cc:.1f}       {agreement}")

# Feature H detection examples
print("\n4. Feature H (Distortions) Detection Examples:")
print("-" * 50)

high_h_files = [(r['file'], r['feature_h'], r['radon_max_cc']) 
                for r in results if r.get('feature_h', 0) > 0.5]

if high_h_files:
    print("Files with high Feature H scores:")
    for fname, h_score, cc in high_h_files:
        print(f"  {fname}: H={h_score:.2f}, CC={cc}")
        print(f"    → Anti-patterns detected (deep nesting, long functions, etc.)")
else:
    print("No files with very high Feature H (>0.5)")
    # Show top 3
    top_h = sorted([(r['file'], r.get('feature_h', 0), r['radon_max_cc']) 
                    for r in results], key=lambda x: x[1], reverse=True)[:3]
    print("Top 3 by Feature H:")
    for fname, h_score, cc in top_h:
        print(f"  {fname}: H={h_score:.2f}, CC={cc}")

# Summary statistics
print("\n5. Summary Statistics:")
print("-" * 50)
print(f"Total files analyzed: {len(results)}")
print(f"Files with knots (score > 0.15): {sum(1 for r in results if r.get('knot_score', 0) > 0.15)}")
print(f"Files with high complexity (CC > 5): {sum(1 for r in results if r['radon_max_cc'] > 5)}")
print(f"Average lines per file: {mean([r['lines'] for r in results]):.0f}")

# Save results
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

output = {
    'system_info': SYSTEM_INFO,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'test_corpus': str(TEST_CORPUS),
    'file_count': len(results),
    'summary': {
        'performance': {
            '4tiers_mean_ms': mean(times_4t),
            '4tiers_std_ms': stdev(times_4t),
            'radon_mean_ms': mean(times_rd),
            'radon_std_ms': stdev(times_rd),
        },
        'correlations': {
            'pearson_f_cc': p_f_cc if 'p_f_cc' in dir() else None,
            'spearman_f_cc': s_f_cc if 's_f_cc' in dir() else None,
        }
    },
    'results': results
}

with open('baseline_comprehensive_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Results saved to: baseline_comprehensive_results.json")

print("\n" + "="*80)
print("STUDY COMPLETE")
print("="*80)
