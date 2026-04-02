#!/usr/bin/env python3
"""
Parallel Batch Analyzer
=======================

Automatically optimizes batch processing with intelligent parallelization.

Features:
- Auto-detects optimal worker count
- Groups files by size for efficient chunking
- Falls back to sequential for small batches
- Uses spawn-safe multiprocessing
"""

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List, Dict, Callable, Any, Tuple
import time
import math


def _build_success_result(path: str, knot) -> Dict[str, Any]:
    """Create a consistent success payload for both sequential and parallel paths."""
    return {
        'success': True,
        'path': path,
        'knot': knot,
        'knots': knot,  # Backwards-compatible alias used by demo/tests
        'score': knot.knot_score,
        'severity': knot.severity,
    }


def _build_error_result(path: str, error: Exception | str) -> Dict[str, Any]:
    """Create a consistent error payload."""
    return {
        'success': False,
        'path': path,
        'error': str(error),
    }


def _analyze_single(args: Tuple[str, int]):
    """Worker function - must be picklable."""
    from src.static_code_knot_analyzer import StaticCodeKnotAnalyzer
    path, index = args
    try:
        analyzer = StaticCodeKnotAnalyzer(path)
        knot = analyzer.analyze()
        return (index, _build_success_result(path, knot))
    except Exception as e:
        return (index, _build_error_result(path, e))


class ParallelBatchAnalyzer:
    """
    Intelligent batch analyzer with automatic parallelization.
    
    Automatically selects optimal strategy:
    - Sequential: < 50 files or < 5 workers beneficial
    - ProcessPool: Large batches with significant compute per file
    """
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self._stats = {}
    
    def _estimate_file_complexity(self, path: str) -> float:
        """Estimate analysis complexity based on file size."""
        try:
            lines = len(Path(path).read_text().split('\n'))
            # Complexity is roughly O(n) with some fixed overhead
            return max(1.0, lines / 100.0)
        except:
            return 1.0
    
    def _should_use_parallel(self, files: List[str]) -> tuple:
        """
        Determine if parallel processing is beneficial.
        
        Returns:
            (use_parallel: bool, optimal_workers: int)
        """
        n_files = len(files)
        
        # Small batches - sequential is faster (avoids spawn overhead)
        if n_files < 20:
            return False, 1
        
        # Estimate total work
        total_complexity = sum(self._estimate_file_complexity(f) for f in files)
        avg_complexity = total_complexity / n_files
        
        # Very simple files - sequential may be faster
        if avg_complexity < 2.0 and n_files < 50:
            return False, 1
        
        # Calculate optimal workers
        # Rule of thumb: workers = min(cores, ceil(total_work / unit_work))
        # where unit_work is the work that benefits from parallelization
        unit_work = 5.0  # complexity units per worker
        optimal = min(self.max_workers, max(2, math.ceil(total_complexity / unit_work)))
        
        # Diminishing returns after 6 workers for this workload
        optimal = min(optimal, 6)
        
        return True, optimal
    
    def analyze_batch(self, files: List[str], progress_callback: Callable = None) -> List[Dict]:
        """
        Analyze a batch of files with automatic parallelization.
        
        Args:
            files: List of file paths
            progress_callback: Called with (completed, total) for progress updates
            
        Returns:
            List of analysis results
        """
        use_parallel, workers = self._should_use_parallel(files)
        
        self._stats = {
            'files': len(files),
            'parallel': use_parallel,
            'workers': workers,
            'start_time': time.perf_counter()
        }
        
        if not use_parallel:
            # Sequential processing
            results = []
            for i, path in enumerate(files):
                from src.static_code_knot_analyzer import StaticCodeKnotAnalyzer
                try:
                    analyzer = StaticCodeKnotAnalyzer(path)
                    knot = analyzer.analyze()
                    results.append(_build_success_result(path, knot))
                except Exception as e:
                    results.append(_build_error_result(path, e))
                
                if progress_callback:
                    progress_callback(i + 1, len(files))
        else:
            # Parallel processing
            context = mp.get_context('spawn')
            indexed_files = [(f, i) for i, f in enumerate(files)]
            results = [None] * len(files)
            
            with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
                completed = 0
                for index, result in executor.map(_analyze_single, indexed_files):
                    results[index] = result
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, len(files))
        
        self._stats['elapsed'] = time.perf_counter() - self._stats['start_time']
        self._stats['throughput'] = len(files) / self._stats['elapsed']
        self._stats['successful'] = sum(1 for r in results if r.get('success'))
        self._stats['failed'] = len(files) - self._stats['successful']
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics from last analysis."""
        return self._stats.copy()


def demo():
    """Demonstrate parallel batch analyzer."""
    print("="*80)
    print("PARALLEL BATCH ANALYZER DEMO")
    print("="*80)
    
    # Create test files
    code_small = "def f():\n    return 1\n" * 20
    code_medium = "class C:\n    def m(self):\n        if True:\n            return 1\n" * 50
    code_large = "class C:\n    def m(self, x):\n        if x > 0:\n            if x % 2:\n                return x * 2\n        return 0\n" * 200
    
    test_scenarios = [
        ("Tiny (10 small)", ["/tmp/small_{}.py".format(i) for i in range(10)]),
        ("Small (50 mixed)", 
         ["/tmp/small_{}.py".format(i) for i in range(30)] +
         ["/tmp/med_{}.py".format(i) for i in range(20)]),
        ("Medium (100 mixed)",
         ["/tmp/small_{}.py".format(i) for i in range(60)] +
         ["/tmp/med_{}.py".format(i) for i in range(35)] +
         ["/tmp/large_{}.py".format(i) for i in range(5)]),
    ]
    
    for name, files in test_scenarios:
        print(f"\n{name}: {len(files)} files")
        
        # Create files
        for i, f in enumerate(files):
            if 'small' in f:
                Path(f).write_text(code_small)
            elif 'med' in f:
                Path(f).write_text(code_medium)
            else:
                Path(f).write_text(code_large)
        
        # Analyze
        analyzer = ParallelBatchAnalyzer()
        results = analyzer.analyze_batch(files)
        stats = analyzer.get_stats()
        
        print(f"  Strategy: {'Parallel' if stats['parallel'] else 'Sequential'}")
        print(f"  Workers: {stats['workers']}")
        print(f"  Time: {stats['elapsed']*1000:.2f} ms")
        print(f"  Throughput: {stats['throughput']:.1f} files/sec")
        print(f"  Results: {sum(1 for r in results if r.get('success'))} successful")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    demo()
