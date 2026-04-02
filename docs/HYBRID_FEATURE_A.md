# Hybrid Feature A Implementation

## Overview

Implemented a **hybrid duplication detection system** that combines:
1. **Exact duplicate detection** (existing) - Line-based within functions
2. **Near-duplicate detection** (v5) - AST-based structural matching
3. **Conservative synthesis** - Weighted combination for final score

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID FEATURE A                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐                         │
│  │   A_exact    │      │    A_near    │                         │
│  │  (existing)  │      │    (v5)      │                         │
│  ├──────────────┤      ├──────────────┤                         │
│  │ Line-based   │      │ AST-based    │                         │
│  │ within func  │      │ cross-func   │                         │
│  │ Reliable     │      │ Structural   │                         │
│  │ Low FP       │      │ Catches sim  │                         │
│  └──────┬───────┘      └──────┬───────┘                         │
│         │                     │                                 │
│         └──────────┬──────────┘                                 │
│                    ▼                                            │
│         ┌──────────────────┐                                    │
│         │   A_combined     │                                    │
│         │ = max(A_exact,   │                                    │
│         │    0.7 * A_near) │                                    │
│         └──────────────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Details

### A_exact (Existing)
```python
# Detects line-level duplicates within function body
body_strs = [ast.dump(stmt) for stmt in node.body]
# Compares AST dump strings to find exact matches
```

**Characteristics:**
- Line-level granularity
- Within-function scope
- High precision
- Misses structural similarities across functions

### A_near (v5 - New)
```python
# Extracts function signatures
signature = {
    'params': len(node.args.args),
    'body_len': len(node.body),
    'stmts': tuple(type(s).__name__ for s in node.body),
    'ifs': ..., 'loops': ..., 'tries': ...
}

# Matches functions with:
# - Same body length
# - Same statement sequence
# - Body length > 1 (filters trivial functions)
```

**Characteristics:**
- Function-level granularity
- Cross-function scope
- Structural pattern matching
- 66.7% recall on duplicate corpus

### A_combined (Conservative Synthesis)
```python
A_combined = max(A_exact, 0.7 * A_near)
```

**Rationale:**
- Exact matches are more reliable → full weight (1.0)
- Near matches need validation → reduced weight (0.7)
- Conservative approach avoids over-flagging
- Uses max() to ensure exact matches aren't diluted

## API Changes

### CodeKnot Dataclass
```python
@dataclass
class CodeKnot:
    # ... existing fields ...
    feature_a_breakdown: Dict[str, float] = field(default_factory=dict)
    # Contains: {'A_exact': x, 'A_near': y, 'A_combined': z}
```

### New Methods
```python
def calculate_feature_a_hybrid(self) -> Dict[str, float]:
    """Calculate all three A variants."""
    
def _calculate_near_duplicate_score(self) -> float:
    """v5 near-duplicate detection algorithm."""
    
def _extract_function_signature_v5(self, node) -> dict:
    """Extract signature for structural comparison."""
    
def _is_near_duplicate(self, sig1, sig2) -> Tuple[bool, float]:
    """Check if two signatures indicate near-duplicates."""
```

## Report Format

```
📋 Knot Features:
   A (Regression (Duplication)): 0.42 ████████
   B (Isomorphism (Similarity)): 1.00 ████████████████████
   ...

   📊 Feature A Breakdown:
      A_exact (exact dup):    0.00
      A_near (structural):    0.60
      A_combined (weighted):  0.42 = max(0.0, 0.7×0.6)
```

## Test Results

### Duplicate Category (6 files)
| File | A_exact | A_near | A_combined | Status |
|------|---------|--------|------------|--------|
| exact_dup.py | 0.0 | 0.6 | **0.42** | ✅ |
| process_dup.py | 0.0 | 0.6 | **0.42** | ✅ |
| transform_dup.py | 0.0 | 0.6 | **0.42** | ✅ |
| validation_dup.py | 0.0 | 0.6 | **0.42** | ✅ |
| crud_dup.py | 0.0 | 0.0 | 0.00 | ❌ (1-liner) |
| handler_dup.py | 0.0 | 0.0 | 0.00 | ❌ (class methods) |

**Detection Rate: 4/6 (66.7%)**

### Simple Category (8 files)
All files: A_exact=0, A_near=0, A_combined=0

**False Positive Rate: 0%** ✅

## Benefits

1. **Transparency**: All three values reported separately
2. **Backward Compatible**: Existing A_exact preserved
3. **Extensible**: Easy to adjust weights or add new detectors
4. **Debuggable**: Can see which detector triggered
5. **Conservative**: Weighted synthesis reduces false positives

## Usage

```python
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

analyzer = StaticCodeKnotAnalyzer('myfile.py')
knot = analyzer.analyze()

# Access combined score (used in overall knot score)
print(knot.features['A'])  # A_combined

# Access breakdown
print(knot.feature_a_breakdown['A_exact'])    # Exact duplicates
print(knot.feature_a_breakdown['A_near'])     # Near duplicates
print(knot.feature_a_breakdown['A_combined']) # Weighted synthesis

# Detailed report shows all three
print(analyzer.get_detailed_report())
```

## Future Improvements

1. **Class method detection**: Handle handler_dup.py case
2. **One-liner patterns**: Special handling for CRUD patterns
3. **Configurable weights**: Allow users to adjust 0.7 factor
4. **Token-based matching**: More flexible than AST statements
5. **Cross-file detection**: Currently limited to single file
