# Feature F & D Improvement Plan

## Current Status (from Assessment)

| Feature | Score | Status | File |
|---------|-------|--------|------|
| **F** (Complexity Trajectory) | **1.327** | ⚠️ Moderate | dynamic_code_knot_analyzer.py |
| **D** (Expansion Stop) | **0.000** | ✅ Good | All files |

---

## Feature F: Complexity Trajectory (Volatility)

### Problem Analysis

The `dynamic_code_knot_analyzer.py` has elevated complexity due to:

1. **`trace_calls()`** - 52 lines, 5 nested if/elif blocks
2. **`calculate_dynamic_features()`** - 74 lines, 7 feature calculations with conditionals  
3. **`analyze_function()`** - 69 lines, severity logic + suggestion mapping

### Root Cause
The functions are doing too much - violating Single Responsibility Principle.

### Solution: Refactor into Smaller Functions

#### Before (Complex):
```python
def trace_calls(self, frame, event, arg):
    # 52 lines handling call/line/return/exception
    # High cyclomatic complexity (4+ branches)
```

#### After (Simplified):
```python
def trace_calls(self, frame, event, arg):
    """Main trace dispatcher."""
    if self.target_module not in frame.f_code.co_filename:
        return self.trace_calls
    
    handlers = {
        'call': self._handle_call,
        'line': self._handle_line,
        'return': self._handle_return,
        'exception': self._handle_exception
    }
    
    handler = handlers.get(event)
    if handler:
        handler(frame, arg)
    
    return self.trace_calls

def _handle_call(self, frame, arg):
    """Handle function entry - 10 lines"""
    ...

def _handle_line(self, frame, arg):
    """Handle line execution - 12 lines"""
    ...

def _handle_return(self, frame, arg):
    """Handle function return - 8 lines"""
    ...

def _handle_exception(self, frame, arg):
    """Handle exception - 8 lines"""
    ...
```

**Impact:**
- Each function < 15 lines
- Cyclomatic complexity: 4 → 1 per function
- Easier to test individually
- Better maintainability

---

## Feature D: Expansion Stop (Dead Code)

### Current Status: ✅ GOOD (0.000)

No dead code detected. Let's keep it that way.

### Prevention Measures

1. **Add Coverage Testing**
   ```python
   # Ensure all feature calculation paths are tested
   def test_all_features_calculated():
       # Test A, B, C, D, E, F, H all have values
   ```

2. **Add `__all__` exports**
   ```python
   __all__ = [
       'DynamicCodeKnotAnalyzer',
       'ExecutionTrace',
       'DynamicKnot'
   ]
   ```

3. **Remove unused imports**
   ```bash
   # Run autoflake to check
   autoflake --remove-unused-variables --remove-all-unused-imports dynamic_code_knot_analyzer.py
   ```

---

## Implementation Plan

### Phase 1: Refactor trace_calls (30 min)
- [ ] Extract `_handle_call()`
- [ ] Extract `_handle_line()`
- [ ] Extract `_handle_return()`
- [ ] Extract `_handle_exception()`
- [ ] Update main `trace_calls()` to use dispatcher pattern

### Phase 2: Refactor calculate_dynamic_features (45 min)
- [ ] Extract `_calc_feature_A()` (Regression)
- [ ] Extract `_calc_feature_B()` (Isomorphism)
- [ ] Extract `_calc_feature_C()` (Contradiction)
- [ ] Extract `_calc_feature_D()` (Expansion Stop)
- [ ] Extract `_calc_feature_E()` (Question Cutoff)
- [ ] Extract `_calc_feature_F()` (State Volatility)
- [ ] Extract `_calc_feature_H()` (Anti-patterns)
- [ ] Update main function to call individual calculators

### Phase 3: Refactor analyze_function (30 min)
- [ ] Extract `_calculate_knot_score()`
- [ ] Extract `_determine_severity()`
- [ ] Extract `_get_suggestion()`
- [ ] Simplify main function to orchestrate these

### Phase 4: Verify Improvements (15 min)
- [ ] Run assessment again
- [ ] Verify Feature F decreases
- [ ] Verify Feature D stays at 0
- [ ] Ensure all tests still pass

**Total Time: ~2 hours**

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Feature F | 1.327 | < 1.0 |
| Feature D | 0.000 | 0.000 |
| Max function length | 74 lines | < 20 lines |
| Testability | Hard | Easy |

---

## Alternative: Document Instead

If refactoring is not desired, document the complexity as **intentional**:

```python
def trace_calls(self, frame, event, arg):
    """
    Trace function for sys.settrace.
    
    NOTE: Complexity is inherent to tracing requirements.
    Each event type (call/line/return/exception) requires 
    different handling. Refactoring would add indirection
    without improving clarity.
    
    Complexity: ~8 (acceptable for trace handler)
    """
```

This acknowledges the complexity without "fixing" it (since it may not be broken).

---

## Recommendation

**Go with Phase 1 only** (trace_calls refactor):
- High impact (biggest complexity reduction)
- Low risk (straightforward extraction)
- ~30 min work

Skip Phases 2-3 if time is limited - the complexity there is more acceptable (feature calculation naturally has branches).

---

*Created: April 2, 2026*
*Target: dynamic_code_knot_analyzer.py*
