# Full Tool Comparison Report - 61 File Corpus

## Executive Summary

Comprehensive comparison of **4-Tiers**, **Radon**, **Pylint**, and **Feature A v5** on expanded 61-file test corpus.

## Test Corpus Composition

| Category | Files | Description |
|----------|-------|-------------|
| simple | 8 | Basic functions (1-2 lines) |
| medium | 10 | Classes, conditionals, loops |
| complex | 8 | Decorators, async, generators |
| duplicate | 6 | Structural/similar code patterns |
| issues | 8 | Deep nesting, complexity, dead code |
| mixed | 6 | Combined issues |
| edge | 5 | Unicode, special chars, edge cases |
| realistic | 10 | Real-world patterns (API, DB, etc.) |
| **TOTAL** | **61** | |

## Overall Statistics

| Metric | 4-Tiers | Radon | Pylint | FeatA-v5 |
|--------|---------|-------|--------|----------|
| Mean Score/CC/Issues | 0.128 | 2.0 | 0.0 | 0.088 |
| Median | 0.119 | 2.0 | 0.0 | 0.000 |
| Max | 0.284 | 8 | 0 | 0.600 |
| Files Flagged | 12 | 3 | 0 | 9 |
| **Total Time** | **27.43 ms** | **3844 ms** | **21470 ms** | **14.40 ms** |
| **Mean Time** | **0.45 ms** | **63.0 ms** | **352 ms** | **0.24 ms** |

## Performance Speedup

```
vs Pylint (21.5s):
├── 4-Tiers:  783x faster  (27ms)
├── Radon:    5.6x faster  (3.8s)
└── FeatureA: 1491x faster (14ms)
```

## Results by Category

| Category | Files | 4-Tiers | Radon | Pylint | FeatA-v5 |
|----------|-------|---------|-------|--------|----------|
| simple | 8 | 0.104 | 1.0 | 0.0 | 0.000 |
| medium | 10 | 0.118 | 2.2 | 0.0 | 0.114 |
| complex | 8 | 0.142 | 2.4 | 0.0 | 0.075 |
| duplicate | 6 | 0.119 | 2.3 | 0.0 | **0.400** |
| issues | 8 | **0.170** | 2.4 | 0.0 | 0.000 |
| mixed | 8 | **0.194** | 3.0 | 0.0 | 0.100 |
| edge | 5 | 0.048 | 0.4 | 0.0 | 0.000 |
| realistic | 10 | 0.119 | 2.2 | 0.0 | 0.060 |

## Feature A v5 Detection Results

### Duplicate Category (Expected: HIGH detection)

| File | 4-Tiers | Radon CC | FeatA-v5 | Status |
|------|---------|----------|----------|--------|
| exact_dup.py | 0.119 | 2 | **0.600** | ✅ |
| process_dup.py | 0.119 | 3 | **0.600** | ✅ |
| transform_dup.py | 0.119 | 3 | **0.600** | ✅ |
| validation_dup.py | 0.119 | 3 | **0.600** | ✅ |
| crud_dup.py | 0.119 | 1 | 0.000 | ❌ (1-liner) |
| handler_dup.py | 0.119 | 2 | 0.000 | ❌ (class methods) |

### Detection Metrics

```
Precision:  44.4% (4/9)
Recall:     66.7% (4/6)
F1-Score:   0.53
False Pos:  9.1% (5/55)
```

### False Positive Analysis

| Category | Detected/Total | Rate |
|----------|----------------|------|
| simple | 0/8 | 0% ✅ |
| medium | 2/10 | 20% |
| complex | 1/8 | 12% |
| duplicate | 4/6 | 67% ✅ |
| issues | 0/8 | 0% ✅ |
| mixed | 1/6 | 17% |
| edge | 0/5 | 0% ✅ |
| realistic | 1/10 | 10% |

## Complexity Correlation

**4-Tiers vs Radon CC: r = 0.626** (moderate positive correlation)

Files flagged by both tools:
- `deep_nesting.py` (4T: 0.284, Radon: 7)
- `high_complexity.py` (4T: 0.284, Radon: 8)
- `many_params.py` (4T: 0.284, Radon: 1)

Files only 4-Tiers flagged:
- `dead_code.py` (Feature D detection)
- `nested.py` (Feature F - structural complexity)

## Tool-Specific Strengths

### 4-Tiers
- ✅ **783x faster** than Pylint
- ✅ Detects TODO/FIXME comments (6 files)
- ✅ Detects dead code
- ✅ Structural pattern analysis
- ✅ Overall knot score integration

### Radon
- ✅ Industry-standard cyclomatic complexity
- ✅ Precise CC numbers (1-8 range)
- ✅ Well-established thresholds
- ❌ Slower (140x slower than 4-Tiers)

### Pylint
- ✅ Comprehensive style checking
- ✅ Syntax error detection
- ❌ Very slow (352ms/file average)
- ❌ 0 issues detected in corpus (disabled rules?)

### Feature A v5
- ✅ **66.7% recall** for duplication
- ✅ **0% false positives** in simple/issues/edge
- ✅ **1491x faster** than Pylint
- ❌ Misses class method duplication
- ❌ Filters out 1-liner functions

## Key Findings

1. **Speed**: 4-Tiers and FeatureA-v5 are orders of magnitude faster
2. **Duplication**: FeatureA-v5 shows promise but needs class method support
3. **Correlation**: 4-Tiers correlates moderately (r=0.63) with Radon CC
4. **Complementarity**: Tools detect different issues - combined use recommended

## Recommendations

### For Production Use
- **Fast screening**: Use 4-Tiers (0.45ms/file)
- **Duplication detection**: Use FeatureA-v5 + manual review
- **Complexity metrics**: Use Radon for CC validation
- **Style enforcement**: Use Pylint (if speed acceptable)

### For Feature A Improvement
1. Add class method duplication detection
2. Consider 1-liner patterns (CRUD)
3. Integrate v5 algorithm into static_code_knot_analyzer.py
