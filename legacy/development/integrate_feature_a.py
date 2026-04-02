#!/usr/bin/env python3
"""Integrate improved Feature A into static_code_knot_analyzer.py"""

print("="*70)
print("Feature A Integration Script")
print("="*70)

improved_calculation = '''
    def calculate_feature_a(self, tree: ast.AST, metrics: Dict[str, Any]) -> float:
        """Calculate Feature A: Regression/Duplication density (IMPROVED)."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if len(functions) < 2:
            return 0.0
        
        sigs = [self._extract_function_signature(f) for f in functions]
        duplicate_pairs = 0
        max_similarity = 0.0
        
        for i, sig1 in enumerate(sigs):
            for sig2 in sigs[i+1:]:
                sim = self._calculate_signature_similarity(sig1, sig2)
                if sim >= 0.85:
                    duplicate_pairs += 1
                    max_similarity = max(max_similarity, sim)
        
        if duplicate_pairs == 0:
            return 0.0
        
        import math
        score = (1 - math.exp(-0.4 * duplicate_pairs)) * (0.4 + 0.6 * max_similarity)
        return min(score, 1.0)
    
    def _extract_function_signature(self, node):
        stmt_types = tuple(type(s).__name__ for s in node.body)
        return {
            'params': len(node.args.args),
            'body_len': len(node.body),
            'stmts': stmt_types,
            'ifs': sum(1 for n in ast.walk(node) if isinstance(n, ast.If)),
            'loops': sum(1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))),
            'tries': sum(1 for n in ast.walk(node) if isinstance(n, ast.Try)),
            'lines': getattr(node, 'end_lineno', 10) - node.lineno,
        }
    
    def _calculate_signature_similarity(self, sig1, sig2):
        weights = {'params': 0.1, 'body_len': 0.1, 'stmts': 0.35, 'ifs': 0.15, 'loops': 0.15, 'tries': 0.15}
        score = 0
        if sig1['stmts'] == sig2['stmts']:
            score += weights['stmts']
        elif len(sig1['stmts']) == len(sig2['stmts']):
            common = sum(1 for a, b in zip(sig1['stmts'], sig2['stmts']) if a == b)
            score += weights['stmts'] * (common / len(sig1['stmts'])) * 0.5
        for key in ['params', 'body_len', 'ifs', 'loops', 'tries']:
            if sig1[key] == sig2[key]:
                score += weights[key]
        return score
'''

print("\n✅ Improved Feature A calculation prepared")
print(f"   - Detects structural duplicates (not just exact copies)")
print(f"   - Uses statement sequence matching")
print(f"   - High threshold (0.85) to reduce false positives")

print("\n" + "="*70)
