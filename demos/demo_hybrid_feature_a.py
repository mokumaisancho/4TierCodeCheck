#!/usr/bin/env python3
"""
Demonstrate Hybrid Feature A Implementation
============================================
Shows A_exact, A_near, and A_combined for different file types.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.static_code_knot_analyzer import StaticCodeKnotAnalyzer

def analyze_file(filepath):
    """Analyze a file and return Feature A breakdown."""
    try:
        analyzer = StaticCodeKnotAnalyzer(str(filepath))
        knot = analyzer.analyze()
        return {
            'file': filepath.name,
            'category': filepath.parent.name,
            'knot_score': knot.knot_score,
            'A_combined': knot.features['A'],
            'A_exact': knot.feature_a_breakdown.get('A_exact', 0),
            'A_near': knot.feature_a_breakdown.get('A_near', 0),
        }
    except Exception as e:
        return {
            'file': filepath.name,
            'category': filepath.parent.name,
            'error': str(e)
        }

def main():
    print("="*80)
    print("HYBRID FEATURE A DEMONSTRATION")
    print("="*80)
    print("\nA_exact:    Exact duplicate detection (line-based within functions)")
    print("A_near:     Near-duplicate detection (AST-based structural matching)")
    print("A_combined: Conservative synthesis = max(A_exact, 0.7 * A_near)")
    print("="*80)
    
    test_files = [
        # Simple files (should have low scores)
        'test_corpus/simple/calc.py',
        'test_corpus/simple/greet.py',
        
        # Duplicate files (should have high A_near)
        'test_corpus/duplicate/validation_dup.py',
        'test_corpus/duplicate/process_dup.py',
        'test_corpus/duplicate/exact_dup.py',
        'test_corpus/duplicate/crud_dup.py',
        
        # Issues files (should have low A)
        'test_corpus/issues/deep_nesting.py',
        'test_corpus/issues/high_complexity.py',
        
        # Realistic files
        'test_corpus/realistic/api_routes.py',
        'test_corpus/realistic/validation.py',
    ]
    
    results = []
    for filepath in test_files:
        path = Path(filepath)
        if path.exists():
            result = analyze_file(path)
            results.append(result)
    
    # Display results
    print("\n📊 RESULTS:")
    print("-"*80)
    print(f"{'File':<35} {'Category':<12} {'A_exact':>8} {'A_near':>8} {'A_combined':>10}")
    print("-"*80)
    
    for r in results:
        if 'error' in r:
            print(f"{r['file']:<35} ERROR: {r['error']}")
        else:
            marker = "👀" if r['A_combined'] > 0.3 else ""
            print(f"{r['file']:<35} {r['category']:<12} {r['A_exact']:>8.3f} {r['A_near']:>8.3f} {r['A_combined']:>10.3f} {marker}")
    
    print("-"*80)
    
    # Summary
    print("\n📈 SUMMARY:")
    dup_results = [r for r in results if r.get('category') == 'duplicate']
    simple_results = [r for r in results if r.get('category') == 'simple']
    
    if dup_results:
        avg_a_combined = sum(r['A_combined'] for r in dup_results) / len(dup_results)
        print(f"   Duplicate files avg A_combined: {avg_a_combined:.3f} (expected: high)")
    
    if simple_results:
        avg_a_combined = sum(r['A_combined'] for r in simple_results) / len(simple_results)
        print(f"   Simple files avg A_combined: {avg_a_combined:.3f} (expected: low)")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("  • A_exact catches line-level duplicates within functions")
    print("  • A_near catches structural similarities across functions")
    print("  • A_combined uses conservative weighting (70% for near)")
    print("  • Both values reported separately for transparency")
    print("="*80)

if __name__ == '__main__':
    main()
