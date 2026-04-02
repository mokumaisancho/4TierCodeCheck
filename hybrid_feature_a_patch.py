"""
Hybrid Feature A Implementation
To be integrated into static_code_knot_analyzer.py
"""

HYBRID_FEATURE_A_CODE = '''
    def calculate_feature_a_hybrid(self) -> Dict[str, float]:
        """
        Calculate hybrid Feature A: exact + near-duplicate detection.
        
        Returns:
            {
                'A_exact': exact duplicate score (existing),
                'A_near': near-duplicate score (v5),
                'A_combined': conservative synthesis
            }
        """
        import ast
        import math
        
        # A_exact: Existing exact duplicate detection
        total_functions = len(self.functions)
        if total_functions == 0:
            return {'A_exact': 0.0, 'A_near': 0.0, 'A_combined': 0.0}
        
        funcs_with_duplication = sum(1 for f in self.functions if f.duplicated_blocks)
        A_exact = funcs_with_duplication / total_functions
        
        # A_near: v5 near-duplicate detection
        A_near = self._calculate_near_duplicate_score()
        
        # A_combined: Conservative synthesis
        # Prefer exact matches, weight near matches at 70%
        A_combined = max(A_exact, 0.7 * A_near)
        
        return {
            'A_exact': round(A_exact, 3),
            'A_near': round(A_near, 3),
            'A_combined': round(A_combined, 3)
        }
    
    def _extract_function_signature_v5(self, node) -> dict:
        """Extract function signature for near-duplicate detection."""
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
    
    def _is_near_duplicate(self, sig1: dict, sig2: dict) -> tuple:
        """Check if two functions are near-duplicates."""
        # Require same body length
        if sig1['body_len'] != sig2['body_len']:
            return False, 0.0
        
        # Require same statement sequence
        if sig1['stmts'] != sig2['stmts']:
            return False, 0.0
        
        # Filter out trivial functions
        if sig1['body_len'] <= 1:
            return False, 0.0
        
        # Calculate confidence
        confidence = 1.0
        if sig1['params'] != sig2['params']:
            confidence = 0.9
        
        return True, confidence
    
    def _calculate_near_duplicate_score(self) -> float:
        """Calculate near-duplicate score using v5 algorithm."""
        try:
            tree = ast.parse(self.content)
        except:
            return 0.0
        
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if len(functions) < 2:
            return 0.0
        
        sigs = [self._extract_function_signature_v5(f) for f in functions]
        duplicates = []
        
        for i, sig1 in enumerate(sigs):
            for sig2 in sigs[i+1:]:
                is_dup, conf = self._is_near_duplicate(sig1, sig2)
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
'''

print("Hybrid Feature A code prepared")
print(f"Length: {len(HYBRID_FEATURE_A_CODE)} characters")
