# 4-Tiers Code Check System

Heuristic code-health analysis that maps static structure, runtime behavior, and Git history into a shared **"knot"** model.

> Status: **experimental / research prototype**
>
> This repository is best understood as an explainable, multi-perspective analyzer for exploring maintainability risk. It is **not** a replacement for mature tools such as SonarQube, Radon, coverage.py, or CodeScene.

## What is a "knot"?

In this project, a knot is a concentrated maintainability risk signal built from multiple weak indicators:

- repetition / duplication
- contradictory logic
- dead or untested paths
- unresolved TODOs
- unstable runtime behavior
- unhealthy historical change patterns

The main idea is not that any single indicator is novel, but that they can be presented through one shared scoring vocabulary.

## The four tiers

| Tier | Analyzer | File | Input | Purpose |
|------|----------|------|-------|---------|
| 1 | Knot model core | `knot_detector_v3.py` | CSV / temporal text | Original rule-based knot scoring model |
| 2 | Static analysis | `static_code_knot_analyzer.py` | Python source | AST-based maintainability heuristics |
| 3 | Dynamic analysis | `dynamic_code_knot_analyzer.py` | Executed Python module | Runtime tracing with `sys.settrace` |
| 4 | Temporal analysis | `temporal_knot_detector.py` | Git repo | Change-history and refactoring risk heuristics |

## Why this repo may still be useful

- **Explainable:** scores are broken into named features (`A-H`)
- **Multi-angle:** combines static, dynamic, and temporal signals
- **Fast enough for experimentation:** optimized single-file analysis is millisecond-scale
- **Hackable:** plain Python, easy to extend with new heuristics

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Recommended Python: **3.10+**

## Quick start

### 1) Static analysis for one file

```python
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

analyzer = StaticCodeKnotAnalyzer("path/to/file.py")
result = analyzer.analyze()

print(result.knot_score, result.severity, result.refactoring_suggestion)
```

### 2) Batch analysis with automatic sequential/parallel selection

```python
from parallel_batch_analyzer import ParallelBatchAnalyzer

batch = ParallelBatchAnalyzer(max_workers=4)
results = batch.analyze_batch(["a.py", "b.py", "c.py"])

successful = [r for r in results if r["success"]]
```

### 3) Temporal / Git-based scan

```bash
python3 temporal_knot_detector.py /path/to/repo --min-score 0.3
```

### 4) Optimized benchmark

```bash
python3 optimized_knot_analyzer.py
```

## Validation status

Current checks included in this repository:

- unit and smoke tests via `pytest`
- GitHub Actions CI workflow for push / pull request validation
- regression coverage for:
  - static scoring basics
  - edge cases
  - batch analyzer
  - optimized analyzer parallel execution

Run:

```bash
pytest -q
```

## Current limitations

This repository deliberately trades completeness for transparency and speed.

- Heuristics are coarse and may produce false positives / false negatives
- Dynamic analysis uses `sys.settrace`, so runtime overhead is non-trivial
- Temporal analysis is lightweight and does not yet match dedicated hotspot tools
- Scores are useful for ranking and discussion, not for treating as ground truth

## Repository layout

- `knot_detector_v3.py` - original knot scoring core
- `static_code_knot_analyzer.py` - AST-based code analysis
- `dynamic_code_knot_analyzer.py` - runtime tracing
- `temporal_knot_detector.py` - Git/history heuristics
- `parallel_batch_analyzer.py` - auto strategy batch runner
- `optimized_knot_analyzer.py` - cached / faster approximations
- `test_knot_detector.py` - tests
- `unified_analyzer_demo.py` - combined demo

## Suggested positioning on GitHub

If you publish this project, describe it as:

- **experimental**
- **heuristic**
- **research prototype**
- **explainable code health analyzer**

That framing is accurate and sets good expectations.

## Roadmap

- improve branch/path coverage in dynamic analysis
- calibrate scores against real-world labeled code smells
- compare against Radon / Pylint / Sonar-style baselines
- enrich temporal analysis with stronger hotspot metrics
- package CLI entry points more cleanly
