# 4-Tiers Code Check System

Psychological knot-explosion-insight detection applied to code analysis.

## Four Tiers

| Tier | Analyzer | File | Purpose |
|------|----------|------|---------|
| 1 | Structure | `knot_detector_v3.py` | File Relationship Tree (FRT) |
| 2 | Static | `static_code_knot_analyzer.py` | AST-based analysis |
| 3 | Dynamic | `dynamic_code_knot_analyzer.py` | Runtime trace analysis |
| 4 | Temporal | `temporal_knot_detector.py` | Git history evolution |

## Optimal Strategy Feature

`parallel_batch_analyzer.py` includes intelligent auto-selection:

```python
analyzer = ParallelBatchAnalyzer()
results = analyzer.analyze_batch(files)  # Auto selects sequential vs parallel
```

- Small batches (< 20 files) → Sequential
- Large/complex batches → ProcessPool with 4-6 workers
- 2-3x speedup for large codebases

## Quick Start

```python
from static_code_knot_analyzer import StaticCodeKnotAnalyzer
from parallel_batch_analyzer import ParallelBatchAnalyzer

# Single file
analyzer = StaticCodeKnotAnalyzer('path/to/file.py')
knots = analyzer.analyze()

# Batch with auto-optimization
batch = ParallelBatchAnalyzer()
results = batch.analyze_batch(['file1.py', 'file2.py', ...])
```

## Files

- `knot_detector_v3.py` (487 lines) - Core 8-feature detection
- `static_code_knot_analyzer.py` (549 lines) - AST static analysis
- `dynamic_code_knot_analyzer.py` (440 lines) - Runtime analysis
- `temporal_knot_detector.py` (634 lines) - Temporal/git analysis
- `optimized_knot_analyzer.py` (392 lines) - Caching & performance
- `parallel_batch_analyzer.py` (197 lines) - **Auto strategy selection**
- `unified_analyzer_demo.py` (115 lines) - Demo all 4 tiers

## Performance

- Single file: ~6.69 ms
- Throughput: 149-350 files/sec (sequential vs parallel)
- Large codebase (10k files): ~28 seconds (parallel)
