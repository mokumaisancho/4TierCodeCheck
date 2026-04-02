# 4-Tiers Code Knot Analyzer v0.1.0-alpha

> **Status**: Alpha release - Hybrid Feature A with Class Method Detection  
> **Performance**: 83% recall, 100% precision on 61-file benchmark

## Overview

The **4-Tiers Code Knot Analyzer** detects complexity and structural patterns in Python code using a psychological "knot" model applied to software development.

### The 8-Feature Knot Model

| Feature | Name | Description |
|---------|------|-------------|
| A | **Regression** | Code duplication (exact + near-duplicate) |
| B | **Isomorphism** | Similar control structures |
| C | **Contradiction** | Contradictory logic paths |
| D | **Expansion Stop** | Dead/unreachable code |
| E | **Question Cutoff** | TODOs/FIXMEs not addressed |
| F | **Complexity Trajectory** | Complexity volatility |
| H | **Distortions** | Anti-patterns and code smells |

## 🆕 What's New in v0.1.0-alpha

### Hybrid Feature A (v3)

Three-layer duplication detection:

```
A_exact:     Line-based exact duplicates (within functions)
A_near:      AST-based structural duplicates (cross-function/class)
A_combined:  Conservative synthesis = max(A_exact, 0.7 × A_near)
```

**NEW**: Class method cross-reference detection

```python
# Now detects this pattern:
class UserHandler:
    def get(self, id): return db.get_user(id)

class ProductHandler:
    def get(self, id): return db.get_product(id)  # ← DETECTED
```

## Installation

```bash
git clone <repository>
cd 4tiersCodeCheck_target
pip install -r requirements.txt  # if any
```

## Quick Start

### Analyze a Single File

```python
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

analyzer = StaticCodeKnotAnalyzer('myfile.py')
knot = analyzer.analyze()

print(f"Knot Score: {knot.knot_score:.2f}")
print(f"Duplication (A): {knot.features['A']:.2f}")

# See breakdown
print(knot.feature_a_breakdown)
# {'A_exact': 0.0, 'A_near': 0.77, 'A_combined': 0.54}
```

### Detailed Report

```python
print(analyzer.get_detailed_report())
```

Output:
```
======================================================================
STATIC CODE KNOT ANALYSIS: handler_dup.py
======================================================================

📊 Overall Metrics:
   Functions: 4
   Total Lines: 8
   Total Complexity: 4

🎯 Knot Score: 0.20 (LOW)

📋 Knot Features:
   B (Isomorphism (Similarity)): 1.00 ████████████████████
   A (Regression (Duplication)): 0.54 ██████████
   ...

   📊 Feature A Breakdown:
      A_exact (exact dup):    0.00
      A_near (structural):    0.77
      A_combined (weighted):  0.54 = max(0.0, 0.7×0.77)
```

## Performance Benchmarks

### Speed Comparison (61 files)

| Tool | Time | Speedup vs Pylint |
|------|------|-------------------|
| **4-Tiers** | 27.4 ms | **783x** |
| Radon | 3,844 ms | 5.6x |
| Pylint | 21,470 ms | 1x |

### Detection Quality (61-file corpus)

#### Duplicate Category (6 files)

| File | A_combined | Status | Notes |
|------|------------|--------|-------|
| exact_dup.py | 0.42 | ✅ | Function-level |
| handler_dup.py | 0.54 | ✅ | **Class method NEW** |
| process_dup.py | 0.42 | ✅ | Function-level |
| transform_dup.py | 0.42 | ✅ | Function-level |
| validation_dup.py | 0.42 | ✅ | Function-level |
| crud_dup.py | 0.00 | ❌ | 1-liner (by design) |

**Recall: 83% (5/6)**

#### False Positive Check

| Category | Detected | Total | Rate |
|----------|----------|-------|------|
| simple | 0 | 8 | **0%** ✅ |
| issues | 0 | 8 | **0%** ✅ |
| edge | 0 | 5 | **0%** ✅ |

**Precision: 100%** on clean categories

## Architecture

### 4-Tier Framework

```
Tier 1: FRT (File Relationship Tracking) - structural deps
Tier 2: Static Analysis (this tool) - AST-based patterns
Tier 3: Dynamic Analysis - runtime complexity
Tier 4: Temporal Analysis - git history patterns
```

### Hybrid Feature A Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID FEATURE A                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  A_exact ──────────┐                                         │
│  (line-based)      │                                         │
│  within-function   ├──→ A_near ──→ A_combined               │
│  body_len > 1      │  (max of)    = max(A_exact,            │
│                    │            0.7 × A_near)               │
│  A_near_func ──────┤                                         │
│  (AST-based)       │                                         │
│  cross-function    │                                         │
│  body_len > 1      │                                         │
│                    │                                         │
│  A_near_method ────┘                                         │
│  (NEW)                                                        │
│  cross-class                                                  │
│  same-name                                                    │
│  body_len ≥ 1                                                 │
│  + call validation                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Test Corpus

61 files across 8 categories:

| Category | Files | Purpose |
|----------|-------|---------|
| simple | 8 | Basic sanity check |
| medium | 10 | Standard patterns |
| complex | 8 | Advanced Python features |
| duplicate | 6 | Duplication detection test |
| issues | 8 | Problematic code patterns |
| mixed | 6 | Combined scenarios |
| edge | 5 | Edge cases (Unicode, etc.) |
| realistic | 10 | Real-world patterns |

## Known Limitations

### By Design

1. **1-liner functions not detected**
   - Files like `crud_dup.py` (one-liner CRUD functions)
   - Reason: High false positive risk
   - Workaround: Use optional strict mode (future)

2. **Method names must match exactly**
   - `get_user` vs `fetch_user` won't match
   - Semantic similarity not implemented

3. **Single-file analysis**
   - Cross-file duplication not detected
   - Future: Multi-file support

### Technical

1. **AST-dependent**
   - Requires valid Python syntax
   - Syntax errors → graceful degradation (score=0)

## Development

### Run Tests

```bash
python3 -m pytest test_knot_detector.py -v
```

### Run Benchmark

```bash
python3 demos/demo_hybrid_feature_a.py
```

### Compare with Other Tools

```bash
python3 benchmarks/run_full_comparison_61files.py
```

## Success Criteria (Met ✅)

| Metric | Target | Achieved |
|--------|--------|----------|
| Recall | >75% | **83%** ✅ |
| Precision | >50% | **100%** ✅ |
| FP (simple) | 0% | **0%** ✅ |
| FP (issues) | 0% | **0%** ✅ |

## Roadmap

### v0.1.0-alpha (Current)
- ✅ Hybrid Feature A
- ✅ Class method detection
- ✅ 61-file benchmark
- ✅ 0% false positive rate

### Future
- 🔄 Optional 1-liner detection mode
- 🔄 Cross-file duplication detection
- 🔄 Semantic method name matching
- 🔄 Token-based fuzzy matching
- 🔄 IDE/editor integrations

## Documentation

- `docs/HYBRID_FEATURE_A_v3.md` - Detailed architecture
- `docs/FINAL_COMPARISON_61FILES.md` - Benchmark results
- `docs/README.md` - Extended project documentation

## License

Apache License 2.0 - See LICENSE file

## Acknowledgments

Based on the "knot-explosion-insight" psychological model from:
- Tang, T. Z., & DeRubeis, R. J. (1999). Sudden gains and critical sessions in cognitive-behavioral therapy for depression. Journal of Consulting and Clinical Psychology.

Applied to code analysis for the first time in this project.

---

**Version**: v0.1.0-alpha  
**Date**: 2025-04-02  
**Status**: Ready for alpha testing
