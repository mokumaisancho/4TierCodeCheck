#!/usr/bin/env python3
"""
Full Tool Comparison on 61-File Corpus
======================================
Compare 4-Tiers, Radon, and Pylint on expanded corpus.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from collections import defaultdict

# Import 4-Tiers
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

# Import Feature A v5
import ast
import math

class FeatureAV5:
    def _extract_signature(self, node):
        stmt_types = tuple(type(s).__name__ for s in node.body)
        return_count = sum(1 for s in node.body if isinstance(s, ast.Return))
        assign_count = sum(1 for s in node.body if isinstance(s, ast.Assign))
        if_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
        loop_count = sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)))
        
        return {
            'params': len(node.args.args),
            'body_len': len(node.body),
            'stmts': stmt_types,
            'returns': return_count,
            'assigns': assign_count,
            'ifs': if_count,
            'loops': loop_count,
            'lines': getattr(node, 'end_lineno', 10) - node.lineno,
        }
    
    def _is_likely_duplicate(self, sig1, sig2):
        if sig1['body_len'] != sig2['body_len']:
            return False, 0.0
        if sig1['stmts'] != sig2['stmts']:
            return False, 0.0
        if sig1['body_len'] <= 1:
            return False, 0.0
        confidence = 1.0 if sig1['params'] == sig2['params'] else 0.9
        return True, confidence
    
    def calculate(self, code):
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
        num_dups = len(duplicates)
        avg_conf = sum(duplicates) / len(duplicates)
        if num_dups >= 3:
            score = 0.7 + 0.3 * avg_conf
        elif num_dups == 2:
            score = 0.5 + 0.3 * avg_conf
        else:
            score = 0.3 + 0.3 * avg_conf
        return min(score, 1.0)


def run_radon(filepath):
    """Run radon cc command."""
    try:
        start = time.perf_counter()
        result = subprocess.run(
            ['radon', 'cc', '-s', '-a', str(filepath)],
            capture_output=True, text=True, timeout=10
        )
        elapsed = time.perf_counter() - start
        output = result.stdout
        
        # Parse complexity
        avg_cc = 0.0
        max_cc = 0.0
        blocks = []
        
        for line in output.split('\n'):
            if '|' in line and not line.strip().startswith('F'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    try:
                        rank = parts[2]
                        cc = int(parts[3]) if parts[3].isdigit() else 0
                        blocks.append(cc)
                        max_cc = max(max_cc, cc)
                    except:
                        pass
        
        if blocks:
            avg_cc = sum(blocks) / len(blocks)
        
        return {'avg_cc': avg_cc, 'max_cc': max_cc, 'time_ms': elapsed * 1000}
    except Exception as e:
        return {'avg_cc': 0, 'max_cc': 0, 'time_ms': 0, 'error': str(e)}


def run_pylint(filepath):
    """Run pylint command."""
    try:
        start = time.perf_counter()
        result = subprocess.run(
            ['pylint', str(filepath), '--disable=all', '--enable=R,C,W,E', '--score=n'],
            capture_output=True, text=True, timeout=15
        )
        elapsed = time.perf_counter() - start
        
        output = result.stdout + result.stderr
        
        # Parse issues
        issue_count = 0
        error_count = 0
        warning_count = 0
        
        for line in output.split('\n'):
            if ':' in line and any(c in line for c in ['E', 'W', 'C', 'R']):
                if line.strip().startswith('E'):
                    error_count += 1
                    issue_count += 1
                elif line.strip().startswith('W'):
                    warning_count += 1
                    issue_count += 1
                elif line.strip().startswith('C') or line.strip().startswith('R'):
                    issue_count += 1
        
        return {
            'issues': issue_count,
            'errors': error_count,
            'warnings': warning_count,
            'time_ms': elapsed * 1000
        }
    except Exception as e:
        return {'issues': 0, 'errors': 0, 'warnings': 0, 'time_ms': 0, 'error': str(e)}


def run_4tiers(filepath):
    """Run 4-Tiers analyzer."""
    try:
        start = time.perf_counter()
        analyzer = StaticCodeKnotAnalyzer(str(filepath))
        knot = analyzer.analyze()
        elapsed = time.perf_counter() - start
        
        return {
            'knot_score': knot.knot_score if hasattr(knot, 'knot_score') else 0,
            'features': knot.features if hasattr(knot, 'features') else {},
            'time_ms': elapsed * 1000
        }
    except Exception as e:
        return {'knot_score': 0, 'features': {}, 'time_ms': 0, 'error': str(e)}


def run_feature_a_v5(filepath):
    """Run Feature A v5."""
    try:
        with open(filepath) as f:
            code = f.read()
        
        start = time.perf_counter()
        v5 = FeatureAV5()
        score = v5.calculate(code)
        elapsed = time.perf_counter() - start
        
        return {'score': score, 'time_ms': elapsed * 1000}
    except Exception as e:
        return {'score': 0, 'time_ms': 0, 'error': str(e)}


def main():
    corpus_dir = Path('test_corpus')
    categories = ['simple', 'medium', 'complex', 'duplicate', 'issues', 'mixed', 'edge', 'realistic']
    
    results = []
    
    print("="*80)
    print("FULL TOOL COMPARISON - 61 File Corpus")
    print("="*80)
    print("\nRunning analysis...\n")
    
    total_files = 0
    
    for cat in categories:
        cat_dir = corpus_dir / cat
        if not cat_dir.exists():
            continue
        
        for pyfile in sorted(cat_dir.glob('*.py')):
            total_files += 1
            print(f"[{total_files:3d}/61] {cat}/{pyfile.name:30s}", end='', flush=True)
            
            result = {
                'file': pyfile.name,
                'category': cat,
                'path': str(pyfile)
            }
            
            # Run tools
            result['tiers_4'] = run_4tiers(pyfile)
            result['radon'] = run_radon(pyfile)
            result['pylint'] = run_pylint(pyfile)
            result['feature_a_v5'] = run_feature_a_v5(pyfile)
            
            results.append(result)
            
            # Quick summary
            ks = result['tiers_4'].get('knot_score', 0)
            cc = result['radon'].get('max_cc', 0)
            pl = result['pylint'].get('issues', 0)
            fav = result['feature_a_v5'].get('score', 0)
            print(f" | 4T:{ks:.2f} R:{cc:.0f} P:{pl} A5:{fav:.2f}")
    
    # Save results
    with open('comparison_61files_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Analyzed {len(results)} files")
    print(f"📁 Results saved to comparison_61files_results.json")
    
    return results


if __name__ == '__main__':
    results = main()
