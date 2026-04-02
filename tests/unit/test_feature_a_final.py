#!/usr/bin/env python3
"""Feature A v5 - Balanced approach with proper filtering."""

import ast
import math
from pathlib import Path

class FeatureAFinal:
    def __init__(self):
        self.results = []
    
    def _extract_signature(self, node):
        """Extract rich function signature."""
        stmt_types = tuple(type(s).__name__ for s in node.body)
        
        # Count different statement types
        return_count = sum(1 for s in node.body if isinstance(s, ast.Return))
        assign_count = sum(1 for s in node.body if isinstance(s, ast.Assign))
        expr_count = sum(1 for s in node.body if isinstance(s, ast.Expr))
        
        # Control flow depth
        if_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
        loop_count = sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)))
        
        return {
            'name': node.name,
            'params': len(node.args.args),
            'body_len': len(node.body),
            'stmts': stmt_types,
            'returns': return_count,
            'assigns': assign_count,
            'exprs': expr_count,
            'ifs': if_count,
            'loops': loop_count,
            'lines': getattr(node, 'end_lineno', 10) - node.lineno,
        }
    
    def _is_likely_duplicate(self, sig1, sig2):
        """
        Determine if two functions are likely duplicates.
        Returns (is_duplicate, confidence)
        """
        # Must have same body structure
        if sig1['body_len'] != sig2['body_len']:
            return False, 0.0
        
        # Require same statement sequence
        if sig1['stmts'] != sig2['stmts']:
            return False, 0.0
        
        # Require reasonable body length (not trivial 1-2 liners)
        if sig1['body_len'] <= 1:
            return False, 0.0
        
        # All checks pass = likely duplicate
        confidence = 1.0
        
        # Bonus: same parameter count
        if sig1['params'] == sig2['params']:
            confidence = 1.0
        else:
            confidence = 0.9
        
        return True, confidence
    
    def calculate_feature_a(self, code):
        try:
            tree = ast.parse(code)
        except:
            return 0.0
        
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if len(functions) < 2:
            return 0.0
        
        sigs = [self._extract_signature(f) for f in functions]
        
        duplicates = []
        for i, sig1 in enumerate(sigs):
            for sig2 in sigs[i+1:]:
                is_dup, conf = self._is_likely_duplicate(sig1, sig2)
                if is_dup:
                    duplicates.append(conf)
        
        if not duplicates:
            return 0.0
        
        # Score based on duplication density
        num_dups = len(duplicates)
        avg_conf = sum(duplicates) / len(duplicates)
        
        # Formula: more duplicates = higher score
        if num_dups >= 3:
            score = 0.7 + 0.3 * avg_conf
        elif num_dups == 2:
            score = 0.5 + 0.3 * avg_conf
        else:
            score = 0.3 + 0.3 * avg_conf
        
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
        print("\n📊 Feature A v5 - Final Balanced Version:")
        print("-" * 60)
        print(f"{'Category':<15} {'Files':>6} {'Detected':>10} {'Avg Score':>12}")
        print("-" * 60)
        
        categories = set(r['category'] for r in self.results)
        for cat in sorted(categories):
            cat_results = [r for r in self.results if r['category'] == cat]
            files = len(cat_results)
            detected = sum(1 for r in cat_results if r['detected'])
            avg_score = sum(r['score'] for r in cat_results) / files if files else 0
            
            marker = "👍" if cat == 'duplicate' and detected >= 4 else ""
            print(f"{cat:<15} {files:>6} {detected:>10} {avg_score:>11.3f} {marker}")
        
        print("-" * 60)
        
        # Duplicates analysis
        print("\n🔍 Duplicate Category (should detect most):")
        dup_results = [r for r in self.results if r['category'] == 'duplicate']
        for r in sorted(dup_results, key=lambda x: -x['score']):
            status = "✅" if r['detected'] else "❌"
            print(f"  {status} {r['file']:<25} Score: {r['score']:.3f}")
        
        # Simple category (should NOT detect)
        print("\n🎯 Simple Category (should NOT detect):")
        simple_results = [r for r in self.results if r['category'] == 'simple']
        for r in sorted(simple_results, key=lambda x: -x['score']):
            status = "✅" if not r['detected'] else "⚠️"
            print(f"  {status} {r['file']:<25} Score: {r['score']:.3f}")
        
        # Stats
        print("\n📈 Final Performance Metrics:")
        dup_results = [r for r in self.results if r['category'] == 'duplicate']
        non_dup_results = [r for r in self.results if r['category'] != 'duplicate']
        
        tp = sum(1 for r in dup_results if r['detected'])
        fn = sum(1 for r in dup_results if not r['detected'])
        fp = sum(1 for r in non_dup_results if r['detected'])
        tn = sum(1 for r in non_dup_results if not r['detected'])
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"  Precision: {precision:.1%} ({tp}/{tp+fp})")
        print(f"  Recall:    {recall:.1%} ({tp}/{tp+fn})")
        print(f"  F1-Score:  {f1:.2f}")
        print(f"  Accuracy:  {(tp+tn)/(tp+tn+fp+fn):.1%}")


if __name__ == '__main__':
    print("="*70)
    print("Feature A Detection - v5 (Final Balanced)")
    print("="*70)
    
    tester = FeatureAFinal()
    tester.run_all('test_corpus')
    tester.analyze()
    
    print("\n" + "="*70)
