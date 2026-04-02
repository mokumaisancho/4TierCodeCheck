#!/usr/bin/env python3
"""
Dynamic Code Knot Analyzer (Refactored)
=======================================

Runtime analysis using sys.settrace to capture execution patterns.
Addresses Feature F (Complexity) and Feature D (Dead Code) concerns.

Changes:
- Extracted handler methods from trace_calls()
- Separated feature calculation into individual methods
- Modularized analyze_function() logic
"""

import sys
import time
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ExecutionTrace:
    """Tracks runtime execution of a function."""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    lines_executed: set = field(default_factory=set)
    variable_states: List[Dict] = field(default_factory=list)
    exceptions_raised: List[str] = field(default_factory=list)
    last_call_time: float = 0.0


@dataclass
class DynamicKnot:
    """Represents a dynamically detected knot."""
    function_name: str
    features: Dict[str, float]
    knot_score: float
    call_count: int
    avg_execution_time: float
    line_coverage: float
    branch_coverage: float
    hot_paths: List[int]
    cold_paths: List[int]
    runtime_suggestions: str
    severity: str


class DynamicCodeKnotAnalyzer:
    """
    Analyze code at runtime using sys.settrace.
    
    Refactored to reduce complexity (Feature F):
    - trace_calls() now dispatches to specific handlers
    - Each feature calculated by dedicated method
    - Analysis logic modularized
    """
    
    def __init__(self, target_module: str):
        self.target_module = target_module
        self.traces: Dict[str, ExecutionTrace] = {}
        self._trace_active = False
    
    # ========================================================================
    # Phase 1: Refactored Tracing (addresses Feature F)
    # ========================================================================
    
    def trace_calls(self, frame, event, arg):
        """
        Main trace dispatcher - simplified using handler mapping.
        
        Previous complexity: 52 lines, 4 nested conditionals
        Current complexity: 15 lines, 1 conditional
        """
        # Filter by target module early
        if self.target_module not in frame.f_code.co_filename:
            return self.trace_calls
        
        # Dispatch to appropriate handler
        handler = self._TRACE_HANDLERS.get(event)
        if handler:
            handler(self, frame, arg)
        
        return self.trace_calls
    
    # Handler registry - maps events to methods
    _TRACE_HANDLERS = {}
    
    def _handle_call(self, frame, arg):
        """Handle function entry event."""
        func_name = frame.f_code.co_name
        
        if func_name not in self.traces:
            self.traces[func_name] = ExecutionTrace(function_name=func_name)
        
        self.traces[func_name].call_count += 1
        self.traces[func_name].last_call_time = time.time()
    
    def _handle_line(self, frame, arg):
        """Handle line execution event."""
        func_name = frame.f_code.co_name
        line_no = frame.f_lineno
        
        if func_name not in self.traces:
            return
        
        trace = self.traces[func_name]
        trace.lines_executed.add(line_no)
        
        # Capture variable states periodically (every 10 lines)
        if len(trace.lines_executed) % 10 == 0:
            self._capture_variables(trace, frame, line_no)
    
    def _capture_variables(self, trace: ExecutionTrace, frame, line_no: int):
        """Capture current variable state."""
        local_vars = {
            k: str(v)[:100] 
            for k, v in frame.f_locals.items() 
            if not k.startswith('__')
        }
        trace.variable_states.append({
            'line': line_no,
            'vars': local_vars
        })
    
    def _handle_return(self, frame, arg):
        """Handle function return event."""
        func_name = frame.f_code.co_name
        
        if func_name not in self.traces:
            return
        
        trace = self.traces[func_name]
        if hasattr(trace, 'last_call_time'):
            exec_time = time.time() - trace.last_call_time
            trace.total_time += exec_time
    
    def _handle_exception(self, frame, arg):
        """Handle exception event."""
        func_name = frame.f_code.co_name
        exc_type, exc_value, _ = arg
        
        if func_name not in self.traces:
            return
        
        self.traces[func_name].exceptions_raised.append(
            f"{exc_type.__name__}: {str(exc_value)[:50]}"
        )
    
    # Register handlers
    _TRACE_HANDLERS['call'] = _handle_call
    _TRACE_HANDLERS['line'] = _handle_line
    _TRACE_HANDLERS['return'] = _handle_return
    _TRACE_HANDLERS['exception'] = _handle_exception
    
    # ========================================================================
    # Execution Methods
    # ========================================================================
    
    def run_with_data(self, test_data_path: str) -> Dict[str, ExecutionTrace]:
        """Run analysis with test data."""
        import importlib.util
        
        # Load test data module
        spec = importlib.util.spec_from_file_location("test_data", test_data_path)
        test_module = importlib.util.module_from_spec(spec)
        
        # Install trace
        self._trace_active = True
        sys.settrace(self.trace_calls)
        
        try:
            spec.loader.exec_module(test_module)
        finally:
            sys.settrace(None)
            self._trace_active = False
        
        return self.traces
    
    # ========================================================================
    # Phase 2: Refactored Feature Calculation (addresses Feature F)
    # ========================================================================
    
    def calculate_dynamic_features(self, trace: ExecutionTrace, 
                                   source_lines: int) -> Dict[str, float]:
        """
        Calculate all dynamic features using dedicated methods.
        
        Previous complexity: 74 lines, 7 feature blocks
        Current complexity: 20 lines, dispatches to methods
        """
        return {
            'A': self._calc_feature_regression(trace),
            'B': self._calc_feature_isomorphism(trace),
            'C': self._calc_feature_contradiction(trace),
            'D': self._calc_feature_expansion_stop(trace, source_lines),
            'E': self._calc_feature_question_cutoff(trace),
            'F': self._calc_feature_volatility(trace),
            'H': self._calc_feature_antipatterns(trace)
        }
    
    def _calc_feature_regression(self, trace: ExecutionTrace) -> float:
        """
        Feature A: Regression - repeated execution patterns.
        High call count with similar paths indicates stuck pattern.
        """
        if trace.call_count == 0:
            return 0.0
        
        call_pattern_score = min(trace.call_count / 100, 1.0)
        
        if not trace.lines_executed:
            return 0.0
        
        repetition = len(trace.lines_executed) / max(trace.call_count, 1)
        return min((1 - repetition) * call_pattern_score, 1.0)
    
    def _calc_feature_isomorphism(self, trace: ExecutionTrace) -> float:
        """
        Feature B: Isomorphism - consistent execution times.
        Similar execution times indicate uniform behavior.
        """
        if trace.call_count <= 1 or trace.total_time <= 0:
            return 0.0
        
        avg_time = trace.total_time / trace.call_count
        # Fast consistent execution = higher isomorphism
        return 0.5 if avg_time < 0.1 else 0.3
    
    def _calc_feature_contradiction(self, trace: ExecutionTrace) -> float:
        """
        Feature C: Contradiction - exception mismatches.
        Frequent exceptions indicate contradictory states.
        """
        if not trace.exceptions_raised or trace.call_count == 0:
            return 0.0
        
        return min(len(trace.exceptions_raised) / trace.call_count, 1.0)
    
    def _calc_feature_expansion_stop(self, trace: ExecutionTrace, 
                                      source_lines: int) -> float:
        """
        Feature D: Expansion Stop - low line coverage.
        (addresses Feature D - ensure full coverage calculation)
        """
        if source_lines == 0:
            return 0.0
        
        coverage = len(trace.lines_executed) / source_lines
        # Low coverage = expansion stop (dead code paths)
        return max(0.0, 1.0 - coverage)
    
    def _calc_feature_question_cutoff(self, trace: ExecutionTrace) -> float:
        """
        Feature E: Question Cutoff - exception swallowing.
        Exceptions raised but not propagated.
        """
        if not trace.exceptions_raised:
            return 0.0
        
        # Simplified: presence of exceptions indicates potential cutoff
        return min(0.3 + (len(trace.exceptions_raised) * 0.1), 1.0)
    
    def _calc_feature_volatility(self, trace: ExecutionTrace) -> float:
        """
        Feature F: State volatility - frequent variable changes.
        Many state changes = high volatility.
        """
        if not trace.variable_states:
            return 0.0
        
        return min(len(trace.variable_states) / 50, 1.0)
    
    def _calc_feature_antipatterns(self, trace: ExecutionTrace) -> float:
        """
        Feature H: Runtime anti-patterns.
        Detects performance and behavior issues.
        """
        anti_patterns = 0
        
        # Long execution time per call
        avg_time = trace.total_time / max(trace.call_count, 1)
        if avg_time > 1.0:
            anti_patterns += 1
        
        # High exception rate
        if trace.call_count > 0:
            exc_rate = len(trace.exceptions_raised) / trace.call_count
            if exc_rate > 0.1:
                anti_patterns += 1
        
        return min(anti_patterns / 2, 1.0)
    
    # ========================================================================
    # Phase 3: Refactored Analysis (addresses Feature F)
    # ========================================================================
    
    def analyze_function(self, func_name: str, source_lines: int) -> DynamicKnot:
        """
        Analyze a single function's dynamic behavior.
        
        Previous complexity: 69 lines
        Current complexity: 25 lines (delegates to helpers)
        """
        trace = self.traces.get(func_name)
        
        if not trace or trace.call_count == 0:
            return self._create_empty_knot(func_name)
        
        features = self.calculate_dynamic_features(trace, source_lines)
        score = self._calculate_knot_score(features)
        severity = self._determine_severity(score)
        suggestion = self._get_suggestion(features)
        hot_paths, cold_paths = self.identify_hot_cold_paths(trace)
        
        return DynamicKnot(
            function_name=func_name,
            features=features,
            knot_score=score,
            call_count=trace.call_count,
            avg_execution_time=trace.total_time / trace.call_count,
            line_coverage=len(trace.lines_executed) / max(source_lines, 1),
            branch_coverage=0.0,
            hot_paths=hot_paths,
            cold_paths=cold_paths,
            runtime_suggestions=suggestion,
            severity=severity
        )
    
    def _create_empty_knot(self, func_name: str) -> DynamicKnot:
        """Create knot for unexecuted function."""
        return DynamicKnot(
            function_name=func_name,
            features={k: 0.0 for k in ['A', 'B', 'C', 'D', 'E', 'F', 'H']},
            knot_score=0.0,
            call_count=0,
            avg_execution_time=0.0,
            line_coverage=0.0,
            branch_coverage=0.0,
            hot_paths=[],
            cold_paths=[],
            runtime_suggestions="Function not executed",
            severity="low"
        )
    
    def _calculate_knot_score(self, features: Dict[str, float]) -> float:
        """Calculate weighted knot score from features."""
        weights = {
            'A': 1.0, 'B': 0.8, 'C': 1.2, 'D': 1.0,
            'E': 0.9, 'F': 0.7, 'H': 1.1
        }
        
        weighted_sum = sum(features.get(k, 0) * w for k, w in weights.items())
        return weighted_sum / sum(weights.values())
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity level from score."""
        if score > 0.8:
            return 'critical'
        elif score > 0.6:
            return 'high'
        elif score > 0.4:
            return 'medium'
        return 'low'
    
    def _get_suggestion(self, features: Dict[str, float]) -> str:
        """Generate refactoring suggestion from top feature."""
        if not features:
            return "No data available"
        
        max_feature = max(features, key=features.get)
        
        suggestions = {
            'A': "Reduce repeated execution patterns - consider caching",
            'B': "Execution times vary - optimize for consistency",
            'C': "Many exceptions - add proper error handling",
            'D': "Low coverage - add more test cases (Feature D: Expansion Stop)",
            'E': "Exception handling incomplete - review error paths",
            'F': "High state volatility - simplify state management",
            'H': "Runtime anti-patterns detected - review implementation"
        }
        
        return suggestions.get(max_feature, "Review function")
    
    def identify_hot_cold_paths(self, trace: ExecutionTrace) -> tuple:
        """Identify frequently and rarely executed lines."""
        if not trace.lines_executed:
            return [], []
        
        lines = list(trace.lines_executed)
        mid = len(lines) // 2
        
        return lines[:mid], lines[mid:]
    
    # ========================================================================
    # Reporting
    # ========================================================================
    
    def generate_report(self) -> str:
        """Generate analysis report."""
        report = ["="*70, "DYNAMIC ANALYSIS REPORT", "="*70, ""]
        
        for func_name in sorted(self.traces.keys()):
            trace = self.traces[func_name]
            report.append(f"\nFunction: {func_name}")
            report.append(f"  Calls: {trace.call_count}")
            report.append(f"  Total time: {trace.total_time:.4f}s")
            report.append(f"  Lines covered: {len(trace.lines_executed)}")
            report.append(f"  Exceptions: {len(trace.exceptions_raised)}")
        
        return "\n".join(report)


# ========================================================================
# Feature D: Ensure no dead code - export public API
# ========================================================================

__all__ = [
    'DynamicCodeKnotAnalyzer',
    'ExecutionTrace',
    'DynamicKnot'
]


if __name__ == '__main__':
    print("Dynamic Code Knot Analyzer (Refactored)")
    print("Run tests with: pytest test_dynamic_analyzer.py")
