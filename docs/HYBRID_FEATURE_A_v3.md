# Hybrid Feature A v3 - With Class Method Detection

## Overview

Enhanced duplication detection that now includes **class method cross-reference detection**.

## Architecture v3

```
┌──────────────────────────────────────────────────────────────────────┐
│                    HYBRID FEATURE A v3                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│  │   A_exact       │    │  A_near_func    │    │  A_near_method  │   │
│  │  (existing)     │    │   (v5)          │    │   (v3 NEW)      │   │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤   │
│  │ Within-function │    │ Cross-function  │    │ Cross-class     │   │
│  │ Line-based      │    │ Any name        │    │ Same name       │   │
│  │ body_len > 1    │    │ body_len > 1    │    │ body_len >= 1   │   │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │
│           │                      │                      │            │
│           └──────────────────────┼──────────────────────┘            │
│                                  ▼                                    │
│                        ┌─────────────────┐                           │
│                        │    A_near       │                           │
│                        │  = max(func,    │                           │
│                        │        method)  │                           │
│                        └────────┬────────┘                           │
│                                 │                                     │
│                                 ▼                                     │
│                      ┌─────────────────────┐                         │
│                      │    A_combined       │                         │
│                      │ = max(A_exact,      │                         │
│                      │    0.7 × A_near)    │                         │
│                      └─────────────────────┘                         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## New in v3: Class Method Detection

### Algorithm

```python
def is_method_duplicate(sig1, sig2):
    """
    Detects cross-class method duplication.
    Requirements:
    1. Same method name (e.g., "get", "create")
    2. Same body structure
    3. Same statement sequence
    4. For 1-liners: same number of function calls
    """
```

### Example Detection

```python
# handler_dup.py - NOW DETECTED ✅
class UserHandler:
    def get(self, id): return db.get_user(id)
    def create(self, data): return db.create_user(data)

class ProductHandler:
    def get(self, id): return db.get_product(id)      # ← DETECTED
    def create(self, data): return db.create_product(data)  # ← DETECTED
```

**Detected pairs:**
- `UserHandler.get` ↔ `ProductHandler.get`
- `UserHandler.create` ↔ `ProductHandler.create`

## Detection Results (61-file corpus)

### Duplicate Category (6 files)

| File | A_exact | A_near | A_combined | Status |
|------|---------|--------|------------|--------|
| exact_dup.py | 0.00 | 0.60 | **0.42** | ✅ |
| handler_dup.py | 0.00 | **0.77** | **0.54** | ✅ NEW! |
| process_dup.py | 0.00 | 0.60 | **0.42** | ✅ |
| transform_dup.py | 0.00 | 0.60 | **0.42** | ✅ |
| validation_dup.py | 0.00 | 0.60 | **0.42** | ✅ |
| crud_dup.py | 0.00 | 0.00 | 0.00 | ❌ (1-liner) |

**Recall: 5/6 (83%)** ↑ from 67%

### False Positive Check

| Category | Detected | Total | Rate |
|----------|----------|-------|------|
| simple | 0 | 8 | **0%** ✅ |
| issues | 0 | 8 | **0%** ✅ |
| edge | 0 | 5 | **0%** ✅ |

**Precision: 5/5 (100%)** on clean categories

## Implementation Details

### Method Signature Extraction

```python
signature = {
    'name': 'get',
    'class': 'UserHandler',
    'is_method': True,
    'params': 2,      # self + id
    'body_len': 1,    # single return
    'stmts': ('Return',),
    'calls': 1,       # one function call
    ...
}
```

### Matching Criteria

| Aspect | Function Dup | Method Dup |
|--------|--------------|------------|
| Scope | Cross-function | Cross-class |
| Name requirement | Any name | Same name |
| Body length | > 1 | ≥ 1 |
| Statement match | Required | Required |
| Extra checks | None | Call count (for 1-liners) |

## Benefits of v3

1. **Higher Recall**: 83% vs 67% (detected handler pattern)
2. **Maintains Precision**: 0% false positives in simple/issues/edge
3. **Real-world Relevance**: Handler/CRUD patterns common in production
4. **Transparent**: Reports show function vs method detection separately

## Known Limitations

1. **crud_dup.py** (1-liner functions): Not detected by design
   - Would require lowering body_len threshold
   - Risk of false positives in simple category
   
2. **Method name must match**: `get_user` vs `fetch_user` won't match
   - Semantic similarity not implemented (future work)

## Report Format

```
📊 Feature A Breakdown:
   A_exact (exact dup):    0.00
   A_near (structural):    0.77   ← includes class method detection
   A_combined (weighted):  0.54 = max(0.0, 0.7×0.77)
```

## Usage

```python
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

analyzer = StaticCodeKnotAnalyzer('myfile.py')
knot = analyzer.analyze()

# Now detects both function and class method duplication
print(knot.feature_a_breakdown['A_near'])  # 0.77 for handler_dup.py
```

## Success Metrics Achieved

| Metric | Target | Achieved |
|--------|--------|----------|
| Recall | >75% | **83%** ✅ |
| Precision | >50% | **100%** ✅ |
| FP (simple) | 0% | **0%** ✅ |
| FP (issues) | 0% | **0%** ✅ |

## Next Steps (Future)

1. **Semantic method matching**: `get_user` ↔ `fetch_user`
2. **1-liner function support**: Optional mode with stricter guards
3. **Cross-file detection**: Currently single-file only
