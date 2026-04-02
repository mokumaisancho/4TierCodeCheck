#!/usr/bin/env python3
"""
Code Knot Detector
==================

Applies the knot-explosion-insight model to code analysis:
- Detects refactoring points
- Identifies technical debt accumulation
- Maps code evolution patterns
- Suggests restructuring opportunities

Maps code concepts to knot model:
- Repetitive code → Feature A (regression)
- Similar patterns → Feature B (isomorphism)
- Contradictory logic → Feature C (contradiction)
- Abandoned features → Feature D (expansion stop)
- TODO comments → Feature E (question cutoff)
- Complexity changes → Feature F (emotion trajectory)
"""

import ast
import re
import git
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np


@dataclass
class CodeEvolution:
    """Tracks evolution of a code unit over time."""
    file_path: str
    function_name: Optional[str]
    commits: List[Dict]
    
    # Metrics over time
    complexity_history: List[int] = field(default_factory=list)
    line_count_history: List[int] = field(default_factory=list)
    change_frequency: int = 0
    
    def get_text_sequence(self) -> List[str]:
        """Convert commit messages to text sequence for knot analysis."""
        return [c['message'] for c in self.commits]


@dataclass
class RefactoringOpportunity:
    """Identified refactoring point."""
    location: str
    knot_score: float
    explosion_probability: float
    refactoring_type: str
    suggested_action: str
    confidence: float


class CodeKnotDetector:
    """
    Detects 'knots' in code that indicate refactoring needs.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path) if (self.repo_path / '.git').exists() else None
        
        # Patterns for code analysis
        self.todo_patterns = [
            r'TODO', r'FIXME', r'HACK', r'XXX', r'BUG',
            r'OPTIMIZE', r'REFACTOR', r'REVIEW'
        ]
        
        self.repetition_patterns = [
            r'copy|duplicate|repeat|similar',
            r'refactor.*again|again.*refactor',
            r'clean.*up|cleanup|tidy'
        ]
        
        self.contradiction_patterns = [
            r'fix.*break|break.*fix',
            r'workaround|temporary.*solution',
            r'inconsistent|mismatch|conflict'
        ]
    
    def analyze_file_evolution(self, file_path: str, 
                               lookback_commits: int = 20) -> CodeEvolution:
        """
        Analyze how a file has evolved over recent commits.
        """
        if not self.repo:
            raise ValueError("Git repository required for evolution analysis")
        
        commits = []
        
        # Get commit history for file
        try:
            file_commits = list(self.repo.iter_commits(
                paths=file_path,
                max_count=lookback_commits
            ))
        except git.GitCommandError:
            return CodeEvolution(file_path=file_path, function_name=None, commits=[])
        
        for commit in reversed(file_commits):  # Oldest first
            commit_info = {
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'date': commit.committed_datetime,
                'author': commit.author.name,
                'stats': self._get_file_stats_at_commit(file_path, commit)
            }
            commits.append(commit_info)
        
        return CodeEvolution(
            file_path=file_path,
            function_name=None,
            commits=commits
        )
    
    def _get_file_stats_at_commit(self, file_path: str, commit) -> Dict:
        """Get file statistics at a specific commit."""
        try:
            blob = commit.tree / file_path
            content = blob.data_stream.read().decode('utf-8', errors='ignore')
            
            lines = content.split('\n')
            
            return {
                'line_count': len(lines),
                'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                'todo_count': sum(1 for l in lines if any(
                    re.search(p, l, re.I) for p in self.todo_patterns
                )),
                'complexity': self._estimate_complexity(content)
            }
        except:
            return {'line_count': 0, 'code_lines': 0, 'todo_count': 0, 'complexity': 0}
    
    def _estimate_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity from code."""
        complexity = 1
        
        # Count control structures
        complexity += len(re.findall(r'\bif\b', content))
        complexity += len(re.findall(r'\belif\b', content))
        complexity += len(re.findall(r'\bfor\b', content))
        complexity += len(re.findall(r'\bwhile\b', content))
        complexity += len(re.findall(r'\bexcept\b', content))
        complexity += len(re.findall(r'\band\b|\bor\b', content))
        
        return complexity
    
    def calculate_code_knot_features(self, evolution: CodeEvolution) -> Dict[str, float]:
        """
        Calculate knot features from code evolution.
        
        Maps to knot model:
        A: Regression - repeated similar changes
        B: Isomorphism - same patterns in commits
        C: Contradiction - fix/revert cycles
        D: Expansion stop - abandoned features
        E: Question cutoff - TODOs not resolved
        F: Complexity trajectory
        """
        if len(evolution.commits) < 3:
            return {k: 0.0 for k in ['A', 'B', 'C', 'D', 'E', 'F']}
        
        messages = [c['message'] for c in evolution.commits]
        stats = [c['stats'] for c in evolution.commits if c['stats']]
        
        # A: Regression - repeated keywords in commits
        A = self._calculate_commit_repetition(messages)
        
        # B: Isomorphism - similar commit structures
        B = self._calculate_commit_similarity(messages)
        
        # C: Contradiction - fix/break cycles
        C = self._calculate_fix_contradictions(messages)
        
        # D: Expansion stop - decreasing activity
        D = self._calculate_abandonment(stats)
        
        # E: Question cutoff - TODOs accumulating
        E = self._calculate_todo_accumulation(stats)
        
        # F: Complexity volatility
        F = self._calculate_complexity_volatility(stats)
        
        return {
            'A': min(A, 1.0),
            'B': min(B, 1.0),
            'C': min(C, 1.0),
            'D': min(D, 1.0),
            'E': min(E, 1.0),
            'F': min(F, 1.0)
        }
    
    def _calculate_commit_repetition(self, messages: List[str]) -> float:
        """Calculate how much commits repeat similar themes."""
        if len(messages) < 2:
            return 0.0
        
        # Extract keywords from messages
        keywords = []
        for msg in messages:
            words = set(re.findall(r'\b\w{4,}\b', msg.lower()))
            keywords.append(words)
        
        # Calculate overlap between consecutive commits
        overlaps = []
        for i in range(1, len(keywords)):
            if keywords[i-1]:
                overlap = len(keywords[i] & keywords[i-1]) / len(keywords[i-1])
                overlaps.append(overlap)
        
        return np.mean(overlaps) if overlaps else 0.0
    
    def _calculate_commit_similarity(self, messages: List[str]) -> float:
        """Calculate structural similarity of commits."""
        if len(messages) < 2:
            return 0.0
        
        # Check for similar prefixes (e.g., "fix:", "refactor:")
        prefixes = [re.match(r'(\w+)[\s:]', msg) for msg in messages]
        prefixes = [p.group(1).lower() for p in prefixes if p]
        
        if not prefixes:
            return 0.0
        
        # Count most common prefix
        from collections import Counter
        most_common = Counter(prefixes).most_common(1)[0][1]
        
        return most_common / len(prefixes)
    
    def _calculate_fix_contradictions(self, messages: List[str]) -> float:
        """Calculate fix/break contradiction cycles."""
        contradictions = 0
        
        for i in range(1, len(messages)):
            prev = messages[i-1].lower()
            curr = messages[i].lower()
            
            # Check for fix followed by break/fix again
            if 'fix' in prev and ('break' in curr or 'fix' in curr):
                contradictions += 1
            
            # Check for revert
            if 'revert' in curr:
                contradictions += 1
        
        return contradictions / max(len(messages) - 1, 1)
    
    def _calculate_abandonment(self, stats: List[Dict]) -> float:
        """Calculate if file is being abandoned."""
        if len(stats) < 3:
            return 0.0
        
        # Check for decreasing line count then plateau
        lines = [s.get('line_count', 0) for s in stats]
        
        if len(lines) >= 3:
            # Recent commits have fewer changes
            recent_avg = np.mean(lines[-3:])
            earlier_avg = np.mean(lines[:-3]) if len(lines) > 3 else recent_avg
            
            if recent_avg < earlier_avg * 0.8:
                return 0.7  # Likely being deprecated
        
        return 0.0
    
    def _calculate_todo_accumulation(self, stats: List[Dict]) -> float:
        """Calculate TODO accumulation (questions not resolved)."""
        if len(stats) < 2:
            return 0.0
        
        todos = [s.get('todo_count', 0) for s in stats]
        
        # Check if TODOs are increasing
        if todos[-1] > todos[0]:
            return min((todos[-1] - todos[0]) / max(todos[0], 1), 1.0)
        
        return 0.0
    
    def _calculate_complexity_volatility(self, stats: List[Dict]) -> float:
        """Calculate complexity volatility."""
        if len(stats) < 2:
            return 0.0
        
        complexities = [s.get('complexity', 0) for s in stats]
        
        if len(complexities) >= 2:
            changes = [abs(complexities[i] - complexities[i-1]) 
                      for i in range(1, len(complexities))]
            return min(np.mean(changes) / 10, 1.0)
        
        return 0.0
    
    def detect_refactoring_opportunities(self, 
                                         file_pattern: str = "*.py",
                                         min_knot_score: float = 0.5) -> List[RefactoringOpportunity]:
        """
        Scan repository for refactoring opportunities.
        """
        opportunities = []
        
        # Find all matching files
        files = list(self.repo_path.rglob(file_pattern))
        
        print(f"Analyzing {len(files)} files...")
        
        for file_path in files:
            try:
                # Get relative path from repo root
                rel_path = file_path.relative_to(self.repo_path)
                
                # Analyze evolution
                evolution = self.analyze_file_evolution(str(rel_path))
                
                if len(evolution.commits) < 3:
                    continue
                
                # Calculate features
                features = self.calculate_code_knot_features(evolution)
                
                # Calculate knot score
                knot_score = np.mean([
                    features['A'], features['B'], features['C'],
                    features['D'], features['E']
                ])
                
                if knot_score >= min_knot_score:
                    # Determine refactoring type
                    ref_type, suggestion = self._classify_refactoring_need(features)
                    
                    opportunity = RefactoringOpportunity(
                        location=str(rel_path),
                        knot_score=knot_score,
                        explosion_probability=min(knot_score * 1.2, 1.0),
                        refactoring_type=ref_type,
                        suggested_action=suggestion,
                        confidence=min(knot_score + 0.2, 1.0)
                    )
                    
                    opportunities.append(opportunity)
                    
            except Exception as e:
                continue
        
        # Sort by knot score
        opportunities.sort(key=lambda x: x.knot_score, reverse=True)
        
        return opportunities
    
    def _classify_refactoring_need(self, features: Dict[str, float]) -> Tuple[str, str]:
        """Classify the type of refactoring needed."""
        
        # Find dominant feature
        max_feature = max(features, key=features.get)
        
        if max_feature == 'A' and features['A'] > 0.6:
            return (
                "Extract Method/Class",
                "High repetition detected. Extract common patterns into reusable functions."
            )
        
        elif max_feature == 'B' and features['B'] > 0.6:
            return (
                "Pattern Standardization",
                "Similar structures throughout. Consider template method or strategy pattern."
            )
        
        elif max_feature == 'C' and features['C'] > 0.6:
            return (
                "Stabilize Logic",
                "Contradictory changes detected. Refactor to single source of truth."
            )
        
        elif max_feature == 'D' and features['D'] > 0.6:
            return (
                "Deprecate or Revive",
                "File may be abandoned. Decide to fully deprecate or actively maintain."
            )
        
        elif max_feature == 'E' and features['E'] > 0.6:
            return (
                "TODO Resolution",
                f"High TODO accumulation ({features['E']:.0%}). Schedule cleanup sprint."
            )
        
        elif max_feature == 'F' and features['F'] > 0.6:
            return (
                "Complexity Reduction",
                "Unstable complexity. Apply simplification patterns."
            )
        
        else:
            return (
                "General Refactoring",
                "Multiple indicators suggest refactoring would improve maintainability."
            )
    
    def generate_refactoring_report(self, opportunities: List[RefactoringOpportunity]) -> str:
        """Generate a refactoring report."""
        
        report = []
        report.append("=" * 80)
        report.append("CODE KNOT DETECTION - REFACTORING REPORT")
        report.append("=" * 80)
        report.append(f"\nRepository: {self.repo_path}")
        report.append(f"Opportunities Found: {len(opportunities)}")
        report.append(f"High Priority (K > 0.7): {len([o for o in opportunities if o.knot_score > 0.7])}")
        
        # Group by refactoring type
        by_type = defaultdict(list)
        for opp in opportunities:
            by_type[opp.refactoring_type].append(opp)
        
        for ref_type, opps in sorted(by_type.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True):
            report.append(f"\n{'=' * 80}")
            report.append(f"{ref_type.upper()} ({len(opps)} files)")
            report.append("=" * 80)
            
            for opp in opps[:10]:  # Top 10 per category
                report.append(f"\n📁 {opp.location}")
                report.append(f"   Knot Score: {opp.knot_score:.2f}")
                report.append(f"   Confidence: {opp.confidence:.0%}")
                report.append(f"   Suggestion: {opp.suggested_action}")
        
        report.append("\n" + "=" * 80)
        report.append("RECOMMENDED ACTIONS")
        report.append("=" * 80)
        
        # Priority queue
        high_priority = [o for o in opportunities if o.knot_score > 0.7]
        medium_priority = [o for o in opportunities if 0.5 <= o.knot_score <= 0.7]
        
        report.append(f"\n🔴 High Priority ({len(high_priority)} files):")
        report.append("   Address these first - high knot density detected")
        
        report.append(f"\n🟡 Medium Priority ({len(medium_priority)} files):")
        report.append("   Schedule for upcoming sprints")
        
        return "\n".join(report)


class DependencyMapKnotAnalyzer:
    """
    Analyze dependency maps for knot patterns.
    
    Useful for:
    - Microservice architecture analysis
    - Module dependency graphs
    - Package coupling detection
    """
    
    def __init__(self, dependency_graph: Dict):
        """
        Args:
            dependency_graph: {module: [dependencies]}
        """
        self.graph = dependency_graph
        self.reverse_graph = self._build_reverse_graph()
    
    def _build_reverse_graph(self) -> Dict:
        """Build reverse dependency graph."""
        reverse = defaultdict(list)
        for module, deps in self.graph.items():
            for dep in deps:
                reverse[dep].append(module)
        return dict(reverse)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies (strong knots)."""
        cycles = []
        visited = set()
        
        def dfs(node, path):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in self.graph.get(node, []):
                dfs(dep, path)
            
            path.pop()
        
        for node in self.graph:
            dfs(node, [])
        
        return cycles
    
    def calculate_knot_metrics(self) -> Dict[str, float]:
        """
        Calculate knot-like metrics for dependency graph.
        """
        metrics = {}
        
        # A: Repetitive dependencies (same imports everywhere)
        all_deps = [dep for deps in self.graph.values() for dep in deps]
        dep_counts = {}
        for dep in all_deps:
            dep_counts[dep] = dep_counts.get(dep, 0) + 1
        
        # Most common dependencies (potential over-coupling)
        common_deps = {k: v for k, v in dep_counts.items() if v > len(self.graph) * 0.5}
        metrics['repetitive_coupling'] = len(common_deps) / max(len(dep_counts), 1)
        
        # B: Isomorphism - similar dependency patterns
        dep_sets = [set(deps) for deps in self.graph.values()]
        if len(dep_sets) > 1:
            similarities = []
            for i in range(len(dep_sets)):
                for j in range(i+1, len(dep_sets)):
                    if dep_sets[i]:
                        sim = len(dep_sets[i] & dep_sets[j]) / len(dep_sets[i])
                        similarities.append(sim)
            
            metrics['isomorphic_modules'] = np.mean(similarities) if similarities else 0.0
        else:
            metrics['isomorphic_modules'] = 0.0
        
        # C: Contradictions - bidirectional dependencies
        bidirectional = 0
        for module, deps in self.graph.items():
            for dep in deps:
                if module in self.graph.get(dep, []):
                    bidirectional += 1
        
        metrics['bidirectional_coupling'] = bidirectional / max(len(all_deps), 1)
        
        # D: Abandoned modules (no incoming or outgoing)
        total_modules = set(self.graph.keys()) | set(self.reverse_graph.keys())
        isolated = [m for m in total_modules 
                   if not self.graph.get(m) and not self.reverse_graph.get(m)]
        
        metrics['abandoned_modules'] = len(isolated) / max(len(total_modules), 1)
        
        # E: Questionable dependencies (too many deps)
        excessive_deps = [m for m, deps in self.graph.items() if len(deps) > 10]
        metrics['excessive_dependencies'] = len(excessive_deps) / max(len(self.graph), 1)
        
        return metrics
    
    def identify_refactoring_targets(self) -> List[Dict]:
        """Identify modules that need refactoring based on knot metrics."""
        
        metrics = self.calculate_knot_metrics()
        targets = []
        
        # High coupling modules
        for module, deps in self.graph.items():
            score = 0.0
            reasons = []
            
            # Too many dependencies
            if len(deps) > 10:
                score += 0.3
                reasons.append(f"High outbound coupling ({len(deps)} deps)")
            
            # Too many modules depend on this
            dependents = len(self.reverse_graph.get(module, []))
            if dependents > 10:
                score += 0.3
                reasons.append(f"High inbound coupling ({dependents} dependents)")
            
            # Circular dependencies
            cycles = self.detect_circular_dependencies()
            in_cycles = any(module in cycle for cycle in cycles)
            if in_cycles:
                score += 0.4
                reasons.append("Part of circular dependency")
            
            if score > 0.5:
                targets.append({
                    'module': module,
                    'knot_score': score,
                    'reasons': reasons,
                    'suggestion': self._suggest_decoupling(module, deps, dependents)
                })
        
        return sorted(targets, key=lambda x: x['knot_score'], reverse=True)
    
    def _suggest_decoupling(self, module: str, deps: List[str], dependents: int) -> str:
        """Suggest decoupling strategy."""
        
        if len(deps) > 10 and dependents > 10:
            return "Apply Dependency Inversion Principle. Extract interfaces."
        elif len(deps) > 10:
            return "Reduce outbound dependencies. Apply Facade pattern."
        elif dependents > 10:
            return "Too many dependents. Consider splitting module."
        else:
            return "Review coupling. Apply dependency injection."


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect code knots for refactoring")
    parser.add_argument("repo", help="Path to git repository")
    parser.add_argument("--pattern", default="*.py", help="File pattern to analyze")
    parser.add_argument("--min-score", type=float, default=0.5, help="Minimum knot score")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    print(f"🔍 Analyzing {args.repo} for code knots...")
    
    detector = CodeKnotDetector(args.repo)
    opportunities = detector.detect_refactoring_opportunities(
        file_pattern=args.pattern,
        min_knot_score=args.min_score
    )
    
    report = detector.generate_refactoring_report(opportunities)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print("\n" + report)
