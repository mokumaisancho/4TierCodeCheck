#!/usr/bin/env python3
"""
Feature A (Duplication) Detection v4 - Production Ready
======================================================
"""

import ast
import hashlib
import math
from typing import List, Dict, Tuple
from collections import defaultdict


def is_constant(node):
    return isinstance(node, ast.Constant)


class DuplicationDetector:
    """Multi-level duplication detection for Feature A."""
    
    def find_structural_duplicates(self, code: str) -> List[Tuple[str, str, float]]:
        """Find functions with similar structure."""
        try:
            tree = ast.parse(code)
        except:
            return []
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                sig = self._extract_signature(node)
                functions.append((node.name, sig))
        
        duplicates = []
        for i, (name1, sig1) in enumerate(functions):
            for name2, sig2 in functions[i+1:]:
                sim = self._calculate_structure_similarity(sig1, sig2)
                if sim >= 0.85:  # High threshold to reduce false positives
                    duplicates.append((name1, name2, sim))
        
        return duplicates
    
    def _extract_signature(self, node: ast.FunctionDef) -> Dict:
        """Extract detailed function signature."""
        # Get statement types in order
        stmt_types = []
        for stmt in node.body:
            stmt_types.append(type(stmt).__name__)
        
        return {
            'params': len(node.args.args),
            'body_len': len(node.body),
            'stmts': tuple(stmt_types),  # Sequence matters
            'ifs': sum(1 for n in ast.walk(node) if isinstance(n, ast.If)),
            'loops': sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))),
            'tries': sum(1 for n in ast.walk(node) if isinstance(n, ast.Try)),
            'returns': sum(1 for n in ast.walk(node) if isinstance(n, ast.Return)),
            'calls': sum(1 for n in ast.walk(node) if isinstance(n, ast.Call)),
            'lines': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 10,
            'struct_hash': self._structure_hash(node),
        }
    
    def _structure_hash(self, node: ast.FunctionDef) -> str:
        """Create hash of control flow structure."""
        parts = []
        for stmt in node.body:
            parts.append(type(stmt).__name__)
            for child in ast.walk(stmt):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                    parts.append(type(child).__name__)
        return hashlib.md5("|".join(parts).encode()).hexdigest()[:16]
    
    def _calculate_structure_similarity(self, sig1: Dict, sig2: Dict) -> float:
        """Calculate similarity with statement sequence matching."""
        # Exact structural match
        if sig1['struct_hash'] == sig2['struct_hash']:
            return 1.0
        
        weights = {
            'params': 0.1, 'body_len': 0.1, 'stmts': 0.3,
            'ifs': 0.15, 'loops': 0.15, 'tries': 0.1
        }
        
        score = 0
        
        # Statement sequence similarity (order matters!)
        stmts1, stmts2 = sig1['stmts'], sig2['stmts']
        if stmts1 == stmts2:
            score += weights['stmts']
        elif len(stmts1) == len(stmts2):
            # Same length, check for reordering
            common = sum(1 for a, b in zip(stmts1, stmts2) if a == b)
            score += weights['stmts'] * (common / len(stmts1)) * 0.5
        
        # Parameter count
        if sig1['params'] == sig2['params']:
            score += weights['params']
        
        # Body length
        if sig1['body_len'] == sig2['body_len']:
            score += weights['body_len']
        
        # Control flow structures
        for key in ['ifs', 'loops', 'tries']:
            if sig1[key] == sig2[key]:
                score += weights[key]
        
        return score
    
    def calculate_feature_a(self, code: str) -> float:
        """Calculate improved Feature A score."""
        structural = self.find_structural_duplicates(code)
        
        if not structural:
            return 0.0
        
        # Score based on count and severity
        # More duplicates = higher score, capped at 1.0
        dup_count = len(structural)
        max_sim = max(sim for _, _, sim in structural)
        
        # Formula: saturation curve
        score = (1 - math.exp(-0.5 * dup_count)) * (0.5 + 0.5 * max_sim)
        return min(score, 1.0)


def test():
    """Test Feature A improvement."""
    detector = DuplicationDetector()
    
    tests = [
        # (name, code, expected_min, expected_max)
        ("Duplicate validations", '''
def validate_user(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True

def validate_product(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True
''', 0.5, 1.0),
        
        ("Different functions", '''
def add(x, y):
    return x + y

def multiply(a, b):
    return a * b

def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
''', 0.0, 0.4),
        
        ("Exact duplicates", '''
def process_a(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result

def process_b(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result
''', 0.5, 1.0),
    ]
    
    print("="*70)
    print("Feature A (Duplication) Detection Test v4")
    print("="*70)
    
    all_passed = True
    for name, code, min_exp, max_exp in tests:
        score = detector.calculate_feature_a(code)
        dups = detector.find_structural_duplicates(code)
        
        passed = min_exp <= score <= max_exp
        status = "✅" if passed else "❌"
        
        print(f"\n{status} {name}")
        print(f"   Score: {score:.3f} (expected: {min_exp:.1f}-{max_exp:.1f})")
        print(f"   Duplicates found: {len(dups)}")
        
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    print("✅ ALL PASSED" if all_passed else "❌ SOME FAILED")
    print("="*70)
    
    return all_passed


if __name__ == '__main__':
    test()
