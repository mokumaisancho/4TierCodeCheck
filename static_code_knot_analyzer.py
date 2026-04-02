#!/usr/bin/env python3
"""
Static Code Knot Analyzer
=========================

Detects "knots" in code structure by analyzing source code directly (no git history).
Bridges FRT's static analysis with the Knot model's conceptual framework.

Maps code structure to knot features:
- A (Regression): Repeated code patterns (duplication)
- B (Isomorphism): Similar control structures
- C (Contradiction): Contradictory logic paths
- D (Expansion Stop): Dead code / unreachable paths
- E (Question Cutoff): TODOs/HACKs not addressed
- F (Complexity Trajectory): Complexity spikes
- H (Distortions): Code smells / anti-patterns

Unlike FRT's shortest path weights, this uses the Knot model's psychological 
framework applied to code structure.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import math


@dataclass
class CodeKnot:
    """Represents a detected knot in code structure."""
    location: str  # file:function or file:class.method
    features: Dict[str, float]  # A-H scores
    knot_score: float
    complexity: int
    lines_of_code: int
    refactoring_suggestion: str
    severity: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class FunctionMetrics:
    """Metrics for a single function/method."""
    name: str
    line_start: int
    line_end: int
    complexity: int  # Cyclomatic complexity
    lines: int
    parameters: int
    returns: int
    nested_depth: int  # Maximum nesting depth
    
    # Knot features
    duplicated_blocks: List[str] = field(default_factory=list)
    similar_functions: List[str] = field(default_factory=list)
    contradictory_paths: List[str] = field(default_factory=list)
    dead_code_lines: List[int] = field(default_factory=list)
    todo_comments: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)


class StaticCodeKnotAnalyzer:
    """
    Analyze code structure for knot patterns (no git history needed).
    
    Simulates reading code like a developer would, detecting:
    - Complexity accumulation
    - Pattern repetition
    - Logic contradictions
    - Abandoned code
    """
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text()
        self.lines = self.content.split('\n')
        self.tree = self._parse_ast()
        
        # Collect all functions/methods
        self.functions: List[FunctionMetrics] = []
        self._extract_functions()
    
    def _parse_ast(self) -> ast.AST:
        """Parse Python file into AST."""
        try:
            return ast.parse(self.content)
        except SyntaxError as e:
            # Return empty module on syntax error
            return ast.Module(body=[], type_ignores=[])
    
    def _extract_functions(self):
        """Extract all function/method definitions with metrics."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics = self._analyze_function(node)
                self.functions.append(metrics)
    
    def _analyze_function(self, node: ast.FunctionDef) -> FunctionMetrics:
        """Analyze a single function for metrics."""
        
        # Basic metrics
        name = node.name
        line_start = node.lineno
        line_end = node.end_lineno or line_start
        lines = line_end - line_start + 1
        
        # Complexity analysis
        complexity = self._calculate_complexity(node)
        
        # Nesting depth
        nested_depth = self._calculate_nesting_depth(node)
        
        # Parameters
        parameters = len(node.args.args) + len(node.args.kwonlyargs)
        
        # Return statements
        returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
        
        metrics = FunctionMetrics(
            name=name,
            line_start=line_start,
            line_end=line_end,
            complexity=complexity,
            lines=lines,
            parameters=parameters,
            returns=returns,
            nested_depth=nested_depth
        )
        
        # Analyze for knot patterns
        self._detect_duplication(node, metrics)
        self._detect_contradictions(node, metrics)
        self._detect_dead_code(node, metrics)
        self._detect_todos(metrics)
        self._detect_anti_patterns(node, metrics)
        
        return metrics
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, 
                                  ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, 
                                  ast.Try, ast.With, ast.FunctionDef)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _detect_duplication(self, node: ast.FunctionDef, metrics: FunctionMetrics):
        """Detect duplicated code blocks within function."""
        # Look for repeated statement patterns
        body_strs = [ast.dump(stmt) for stmt in node.body]
        
        duplicates = []
        seen = {}
        for i, stmt_str in enumerate(body_strs):
            if stmt_str in seen:
                duplicates.append((seen[stmt_str], i))
            else:
                seen[stmt_str] = i
        
        if duplicates:
            metrics.duplicated_blocks = [
                f"Lines {metrics.line_start + d[0]} and {metrics.line_start + d[1]}"
                for d in duplicates[:3]  # Limit to first 3
            ]
    
    def _detect_contradictions(self, node: ast.FunctionDef, metrics: FunctionMetrics):
        """Detect contradictory logic paths."""
        contradictions = []
        
        # Look for if/else with same condition
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check for contradictory conditions in nested ifs
                condition_str = ast.dump(child.test)
                
                # Look for negation in else branch
                if child.orelse and isinstance(child.orelse[0], ast.If):
                    else_condition = ast.dump(child.orelse[0].test)
                    
                    # Simple check: if x / if not x
                    if 'Not' in else_condition and condition_str.replace('Not', '') in else_condition:
                        contradictions.append(f"Contradictory conditions at line {child.lineno}")
        
        metrics.contradictory_paths = contradictions[:3]
    
    def _detect_dead_code(self, node: ast.FunctionDef, metrics: FunctionMetrics):
        """Detect unreachable code."""
        dead_lines = []
        
        # Look for code after return
        found_return = False
        for stmt in node.body:
            if found_return:
                dead_lines.append(stmt.lineno)
            if isinstance(stmt, ast.Return):
                found_return = True
        
        # Look for raise followed by code
        found_raise = False
        for stmt in node.body:
            if found_raise:
                dead_lines.append(stmt.lineno)
            if isinstance(stmt, ast.Raise):
                found_raise = True
        
        metrics.dead_code_lines = list(set(dead_lines))[:5]  # Unique, limit to 5
    
    def _detect_todos(self, metrics: FunctionMetrics):
        """Detect TODO/FIXME comments in function."""
        todos = []
        
        for i, line in enumerate(self.lines[metrics.line_start-1:metrics.line_end], 
                                  start=metrics.line_start):
            if re.search(r'#.*\b(TODO|FIXME|HACK|XXX|BUG)\b', line, re.I):
                todos.append(f"Line {i}: {line.strip()[:50]}")
        
        metrics.todo_comments = todos[:5]
    
    def _detect_anti_patterns(self, node: ast.FunctionDef, metrics: FunctionMetrics):
        """Detect code smells and anti-patterns."""
        anti_patterns = []
        
        # Long function
        if metrics.lines > 50:
            anti_patterns.append("Long function (>50 lines)")
        
        # Too many parameters
        if metrics.parameters > 5:
            anti_patterns.append("Too many parameters (>5)")
        
        # High complexity
        if metrics.complexity > 10:
            anti_patterns.append("High cyclomatic complexity (>10)")
        
        # Deep nesting
        if metrics.nested_depth > 3:
            anti_patterns.append("Deep nesting (>3 levels)")
        
        # God function (too many responsibilities)
        if metrics.lines > 100:
            anti_patterns.append("God function (>100 lines)")
        
        # Check for exception swallowing
        for child in ast.walk(node):
            if isinstance(child, ast.ExceptHandler):
                if not child.body or isinstance(child.body[0], ast.Pass):
                    anti_patterns.append(f"Exception swallowing at line {child.lineno}")
        
        metrics.anti_patterns = anti_patterns[:5]
    
    def calculate_knot_features(self) -> Dict[str, float]:
        """
        Calculate knot features from static code analysis.
        
        Maps to psychological knot model:
        A: Regression (repetition) - duplicated code
        B: Isomorphism - similar structures
        C: Contradiction - contradictory logic
        D: Expansion stop - dead code
        E: Question cutoff - TODOs
        F: Complexity trajectory - complexity distribution
        H: Distortions - anti-patterns
        """
        
        if not self.functions:
            return {k: 0.0 for k in ['A', 'B', 'C', 'D', 'E', 'F', 'H']}
        
        total_functions = len(self.functions)
        
        # A: Regression - code duplication
        funcs_with_duplication = sum(1 for f in self.functions if f.duplicated_blocks)
        A = funcs_with_duplication / total_functions
        
        # B: Isomorphism - similar complexity patterns
        complexities = [f.complexity for f in self.functions]
        if complexities:
            complexity_variance = max(complexities) - min(complexities)
            B = 1.0 - min(complexity_variance / 20, 1.0)  # Low variance = high isomorphism
        else:
            B = 0.0
        
        # C: Contradiction - contradictory logic paths
        funcs_with_contradictions = sum(1 for f in self.functions if f.contradictory_paths)
        C = funcs_with_contradictions / total_functions
        
        # D: Expansion stop - dead code
        funcs_with_dead_code = sum(1 for f in self.functions if f.dead_code_lines)
        D = funcs_with_dead_code / total_functions
        
        # E: Question cutoff - TODOs
        funcs_with_todos = sum(1 for f in self.functions if f.todo_comments)
        E = funcs_with_todos / total_functions
        
        # F: Complexity trajectory (volatility)
        if len(complexities) > 1:
            mean_complexity = sum(complexities) / len(complexities)
            variance = sum((c - mean_complexity) ** 2 for c in complexities) / len(complexities)
            F = min(variance / 50, 1.0)  # Normalize
        else:
            F = 0.0
        
        # H: Distortions (anti-patterns)
        funcs_with_antipatterns = sum(1 for f in self.functions if f.anti_patterns)
        H = funcs_with_antipatterns / total_functions
        
        return {
            'A': min(A, 1.0),
            'B': min(B, 1.0),
            'C': min(C, 1.0),
            'D': min(D, 1.0),
            'E': min(E, 1.0),
            'F': min(F, 1.0),
            'H': min(H, 1.0)
        }
    
    def calculate_knot_score(self, features: Dict[str, float]) -> float:
        """Calculate overall knot score."""
        # Weighted average emphasizing contradictions and distortions
        score = (
            features['A'] * 1.0 +
            features['B'] * 0.8 +
            features['C'] * 1.2 +  # Contradictions are serious
            features['D'] * 1.0 +
            features['E'] * 0.9 +
            features['F'] * 0.7 +
            features['H'] * 1.1    # Anti-patterns matter
        ) / 6.7
        
        return min(score, 1.0)
    
    def get_refactoring_suggestion(self, features: Dict[str, float]) -> str:
        """Get refactoring suggestion based on dominant features."""
        
        max_feature = max(features, key=features.get)
        
        suggestions = {
            'A': "Extract duplicated code into shared functions",
            'B': "Standardize similar function structures",
            'C': "Resolve contradictory logic paths",
            'D': "Remove dead code",
            'E': "Address TODO/FIXME comments",
            'F': "Reduce complexity volatility - simplify complex functions",
            'H': "Fix anti-patterns: break down long functions"
        }
        
        return suggestions.get(max_feature, "General refactoring recommended")
    
    def analyze(self) -> CodeKnot:
        """Run complete analysis."""
        features = self.calculate_knot_features()
        knot_score = self.calculate_knot_score(features)
        
        # Calculate severity
        if knot_score > 0.8:
            severity = 'critical'
        elif knot_score > 0.6:
            severity = 'high'
        elif knot_score > 0.4:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Total complexity
        total_complexity = sum(f.complexity for f in self.functions)
        total_lines = sum(f.lines for f in self.functions)
        
        return CodeKnot(
            location=str(self.file_path),
            features=features,
            knot_score=knot_score,
            complexity=total_complexity,
            lines_of_code=total_lines,
            refactoring_suggestion=self.get_refactoring_suggestion(features),
            severity=severity
        )
    
    def get_detailed_report(self) -> str:
        """Generate detailed analysis report."""
        knot = self.analyze()
        
        report = []
        report.append("=" * 70)
        report.append(f"STATIC CODE KNOT ANALYSIS: {self.file_path.name}")
        report.append("=" * 70)
        
        report.append(f"\n📊 Overall Metrics:")
        report.append(f"   Functions: {len(self.functions)}")
        report.append(f"   Total Lines: {knot.lines_of_code}")
        report.append(f"   Total Complexity: {knot.complexity}")
        report.append(f"   Avg Complexity: {knot.complexity / max(len(self.functions), 1):.1f}")
        
        report.append(f"\n🎯 Knot Score: {knot.knot_score:.2f} ({knot.severity.upper()})")
        
        report.append(f"\n📋 Knot Features:")
        feature_names = {
            'A': 'Regression (Duplication)',
            'B': 'Isomorphism (Similarity)',
            'C': 'Contradiction',
            'D': 'Expansion Stop (Dead Code)',
            'E': 'Question Cutoff (TODOs)',
            'F': 'Complexity Trajectory',
            'H': 'Distortions (Anti-patterns)'
        }
        
        for feature, score in sorted(knot.features.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20)
            report.append(f"   {feature} ({feature_names[feature]}): {score:.2f} {bar}")
        
        report.append(f"\n💡 Primary Suggestion:")
        report.append(f"   {knot.refactoring_suggestion}")
        
        # Detailed function analysis
        report.append(f"\n🔍 Function Details:")
        for func in sorted(self.functions, key=lambda f: f.complexity, reverse=True)[:5]:
            report.append(f"\n   {func.name}():")
            report.append(f"      Lines: {func.lines}, Complexity: {func.complexity}, Depth: {func.nested_depth}")
            
            if func.duplicated_blocks:
                report.append(f"      ⚠️  Duplication: {len(func.duplicated_blocks)} blocks")
            if func.contradictory_paths:
                report.append(f"      ⚠️  Contradictions: {len(func.contradictory_paths)}")
            if func.dead_code_lines:
                report.append(f"      ⚠️  Dead code: {len(func.dead_code_lines)} lines")
            if func.todo_comments:
                report.append(f"      📝 TODOs: {len(func.todo_comments)}")
            if func.anti_patterns:
                report.append(f"      🔴 Anti-patterns: {', '.join(func.anti_patterns[:3])}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


class MultiFileKnotAnalyzer:
    """Analyze multiple files for codebase-wide knot patterns."""
    
    def __init__(self, directory: str, pattern: str = "*.py"):
        self.directory = Path(directory)
        self.pattern = pattern
        self.file_knots: List[CodeKnot] = []
    
    def analyze_all(self) -> List[CodeKnot]:
        """Analyze all matching files."""
        files = list(self.directory.rglob(self.pattern))
        
        print(f"🔍 Analyzing {len(files)} files...")
        
        for file_path in files:
            try:
                analyzer = StaticCodeKnotAnalyzer(str(file_path))
                knot = analyzer.analyze()
                
                if knot.knot_score > 0.3:  # Only report significant knots
                    self.file_knots.append(knot)
                    
            except Exception as e:
                continue
        
        # Sort by knot score
        self.file_knots.sort(key=lambda k: k.knot_score, reverse=True)
        
        return self.file_knots
    
    def generate_summary_report(self) -> str:
        """Generate summary report for all files."""
        if not self.file_knots:
            return "No significant code knots detected! ✅"
        
        report = []
        report.append("=" * 70)
        report.append("CODEBASE-WIDE KNOT ANALYSIS")
        report.append("=" * 70)
        
        report.append(f"\n📊 Summary:")
        report.append(f"   Files with knots: {len(self.file_knots)}")
        
        critical = len([k for k in self.file_knots if k.severity == 'critical'])
        high = len([k for k in self.file_knots if k.severity == 'high'])
        medium = len([k for k in self.file_knots if k.severity == 'medium'])
        
        report.append(f"   Critical: {critical}, High: {high}, Medium: {medium}")
        
        avg_score = sum(k.knot_score for k in self.file_knots) / len(self.file_knots)
        report.append(f"   Average knot score: {avg_score:.2f}")
        
        report.append(f"\n🔥 Top 10 Files by Knot Score:")
        for i, knot in enumerate(self.file_knots[:10], 1):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[knot.severity]
            report.append(f"\n{i}. {emoji} {knot.location}")
            report.append(f"   Score: {knot.knot_score:.2f} | Complexity: {knot.complexity}")
            report.append(f"   Top issue: {knot.refactoring_suggestion[:60]}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Static Code Knot Analyzer - Detect code complexity without git history"
    )
    parser.add_argument("path", help="Python file or directory to analyze")
    parser.add_argument("--pattern", default="*.py", help="File pattern for directory analysis")
    parser.add_argument("--min-score", type=float, default=0.3, 
                       help="Minimum knot score to report")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        # Single file analysis
        print(f"🔍 Analyzing {path}...")
        analyzer = StaticCodeKnotAnalyzer(str(path))
        print(analyzer.get_detailed_report())
        
    elif path.is_dir():
        # Multi-file analysis
        analyzer = MultiFileKnotAnalyzer(str(path), args.pattern)
        knots = analyzer.analyze_all()
        print(analyzer.generate_summary_report())
        
    else:
        print(f"Error: {path} not found")
