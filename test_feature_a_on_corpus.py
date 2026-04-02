#!/usr/bin/env python3
"""Test Feature A on expanded corpus - v2 with adjusted threshold."""

import os
import ast
import math
from pathlib import Path

class FeatureATester:
    def __init__(self):
        self.results = []
    
    def _extract_signature(self, node):
        stmt_types = tuple(type(s).__name__ for s in node.body)
        return {
            'name': node.name,
            'params': len(node.args.args),
            'body_len': len(node.body),
            'stmts': stmt_types,
            'ifs': sum(1 for n in ast.walk(node) if isinstance(n, ast.If)),
            'loops': sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))),
            'tries': sum(1 for n in ast.walk(node) if isinstance(n, ast.Try)),
            'lines': getattr(node, 'end_lineno', 10) - node.lineno,
        }
    
    def _calculate_similarity(self, sig1, sig2):
        """Calculate similarity with more weight on statement patterns."""
        weights = {'params': 0.1, 'body_len': 0.1, 'stmts': 0.45, 'ifs': 0.12, 'loops': 0.12, 'tries': 0.11}
        score = 0
        
        # Statement sequence - most important
        if sig1['stmts'] == sig2['stmts']:
            score += weights['stmts']
        elif len(sig1['stmts']) == len(sig2['stmts']) and len(sig1['stmts']) > 0:
            common = sum(1 for a, b in zip(sig1['stmts'], sig2['stmts']) if a == b)
            match_ratio = common / len(sig1['stmts'])
            score += weights['stmts'] * match_ratio * 0.7
        
        # Other attributes
        for key in ['params', 'body_len', 'ifs', 'loops', 'tries']:
            if sig1[key] == sig2[key]:
                score += weights[key]
        
        return score
    
    def calculate_feature_a(self, code):
        try:
            tree = ast.parse(code)
        except:
            return 0.0
        
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if len(functions) < 2:
            return 0.0
        
        sigs = [self._extract_signature(f) for f in functions]
        duplicate_pairs = 0
        max_similarity = 0.0
        pair_details = []
        
        for i, sig1 in enumerate(sigs):
            for sig2 in sigs[i+1:]:
                sim = self._calculate_similarity(sig1, sig2)
                if sim >= 0.80:  # Slightly lower threshold but with stricter scoring
                    duplicate_pairs += 1
                    max_similarity = max(max_similarity, sim)
                    pair_details.append((sig1['name'], sig2['name'], sim))
        
        if duplicate_pairs == 0:
            return 0.0
        
        # Require at least 2 duplicate pairs OR very high similarity for single pair
        if duplicate_pairs == 1 and max_similarity < 0.95:
            return max_similarity * 0.2  # Significantly reduce single pair score
        
        # More aggressive scoring for multiple pairs
        score = (1 - math.exp(-0.6 * duplicate_pairs)) * (0.3 + 0.7 * max_similarity)
        return min(score, 1.0)
    
    def test_file(self, filepath, expected_category):
        with open(filepath) as f:
            code = f.read()
        
        score = self.calculate_feature_a(code)
        return {
            'file': filepath.name,
            'category': expected_category,
            'score': score,
            'detected': score > 0.25
        }
    
    def run_all(self, corpus_dir):
        categories = ['simple', 'medium', 'complex', 'duplicate', 'issues', 'mixed', 'edge', 'realistic']
        
        for cat in categories:
            cat_dir = Path(corpus_dir) / cat
            if not cat_dir.exists():
                continue
            
            for pyfile in cat_dir.glob('*.py'):
                result = self.test_file(pyfile, cat)
                self.results.append(result)
        
        return self.results
    
    def analyze(self):
        # By category
        print("\n📊 Feature A Detection by Category (v2):")
        print("-" * 60)
        print(f"{'Category':<15} {'Files':>6} {'Detected':>10} {'Avg Score':>12}")
        print("-" * 60)
        
        categories = set(r['category'] for r in self.results)
        for cat in sorted(categories):
            cat_results = [r for r in self.results if r['category'] == cat]
            files = len(cat_results)
            detected = sum(1 for r in cat_results if r['detected'])
            avg_score = sum(r['score'] for r in cat_results) / files if files else 0
            
            marker = "👍" if cat == 'duplicate' and detected >= 3 else ""
            print(f"{cat:<15} {files:>6} {detected:>10} {avg_score:>11.3f} {marker}")
        
        print("-" * 60)
        
        # Duplicates detection analysis
        print("\n🔍 Duplicate Category Analysis:")
        dup_results = [r for r in self.results if r['category'] == 'duplicate']
        for r in sorted(dup_results, key=lambda x: -x['score']):
            status = "✅" if r['detected'] else "❌"
            print(f"  {status} {r['file']:<25} Score: {r['score']:.3f}")
        
        # False positive analysis
        print("\n🚨 False Positive Check:")
        for cat in ['simple', 'medium']:
            cat_results = [r for r in self.results if r['category'] == cat and r['detected']]
            if cat_results:
                print(f"  {cat} category:")
                for r in cat_results:
                    print(f"    ⚠️  {r['file']:<25} Score: {r['score']:.3f}")
            else:
                print(f"  ✅ {cat}: No false positives")
        
        # Summary stats
        print("\n📈 Summary Statistics:")
        dup_detected = sum(1 for r in self.results if r['category'] == 'duplicate' and r['detected'])
        non_dup_detected = sum(1 for r in self.results if r['category'] != 'duplicate' and r['detected'])
        non_dup_total = sum(1 for r in self.results if r['category'] != 'duplicate')
        
        print(f"  True Positives: {dup_detected}/6 ({dup_detected/6*100:.0f}%) in duplicate category")
        print(f"  False Positives: {non_dup_detected}/{non_dup_total} ({non_dup_detected/non_dup_total*100:.1f}%) in other categories")


if __name__ == '__main__':
    print("="*70)
    print("Feature A Detection Test - v2 (Adjusted Thresholds)")
    print("="*70)
    
    tester = FeatureATester()
    tester.run_all('test_corpus')
    tester.analyze()
    
    print("\n" + "="*70)
