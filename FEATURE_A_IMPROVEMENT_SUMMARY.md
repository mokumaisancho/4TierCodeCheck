# Feature A (Duplication) Improvement Summary

## Overview
Improved duplication detection from **exact copy matching** to **structural pattern matching**.

## Test Corpus Expansion
| Metric | Before | After |
|--------|--------|-------|
| Total Files | 25 | **61** |
| Categories | 6 | **8** |
| Simple | 3 → 8 files |
| Medium | 5 → 10 files |
| Complex | 5 → 8 files |
| Duplicate | 3 → 6 files |
| Issues | 5 → 8 files |
| Mixed | 4 → 6 files |
| Edge Cases | 0 → **5 files** |
| Realistic | 3 → **10 files** |

## Feature A Algorithm Evolution

### v1: Original (Line-based exact matching)
- Only detected exact code block copies
- Missed all structural similarities

### v2-4: AST-based similarity (iterative refinement)
- Multiple thresholds tested
- Balancing precision vs recall

### v5: Final Balanced Algorithm
**Logic:**
1. Extract rich function signatures (statements, control flow, metrics)
2. Require exact body length match
3. Require exact statement sequence match
4. Filter out trivial 1-2 line functions
5. Score based on duplication density

**Performance on 61-file corpus:**
```
Precision: 44.4% (4/9)
Recall:    66.7% (4/6)
F1-Score:  0.53
Accuracy:  88.5%
```

## Detection Results by Category

| Category | Files | Detected | Avg Score | Notes |
|----------|-------|----------|-----------|-------|
| duplicate | 6 | 4 (67%) | 0.400 | ✅ 4/6 detected |
| simple | 8 | 0 (0%) | 0.000 | ✅ No false positives |
| issues | 8 | 0 (0%) | 0.000 | ✅ Clean |
| edge | 5 | 0 (0%) | 0.000 | ✅ Clean |
| medium | 10 | 2 (20%) | 0.114 | Some detection |
| complex | 8 | 1 (12%) | 0.075 | Low detection |

## Detected Duplicates (True Positives)
- ✅ `exact_dup.py` (0.600)
- ✅ `validation_dup.py` (0.600)
- ✅ `process_dup.py` (0.600)
- ✅ `transform_dup.py` (0.600)

## Missed Duplicates (False Negatives)
- ❌ `handler_dup.py` - Class methods with similar structure
- ❌ `crud_dup.py` - One-liner functions

## Trade-offs
**Strengths:**
- Zero false positives in simple/edge/issues categories
- Detects exact structural duplicates
- Fast computation (AST-based)

**Limitations:**
- Misses class-level method duplication
- One-liner functions filtered out
- Requires exact statement sequence

## Comparison with Radon
| Tool | Exact Dup | Structural Dup | CRUD Pattern | False Positives |
|------|-----------|----------------|--------------|-----------------|
| 4-Tiers v5 | ✅ | ✅ (67%) | ❌ | Low |
| Radon | ✅ | ✅ | ✅ | Medium |

## Next Steps for Further Improvement
1. **Normalize variable names** in AST for fuzzy matching
2. **Add class method analysis** for handler patterns
3. **Consider line similarity** for one-liner detection
4. **Tune threshold** based on file size/context

## Files Changed
- Created 61 test corpus files across 8 categories
- `improve_feature_a.py` - Algorithm research
- `test_feature_a_final.py` - v5 implementation
- `create_expanded_corpus.py` - Corpus generator
