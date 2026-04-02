# Tool Comparison Report: 4-Tiers vs Radon vs Pylint

**Date:** April 2, 2026  
**Test Corpus:** 25 Python files (expanded corpus)  
**Method:** Hot cache, 3-run average per file

---

## Executive Summary

| Metric | 4-Tiers | Radon | Pylint |
|--------|---------|-------|--------|
| **Avg Time** | 1.02 ms | 1.15 ms | 299.71 ms |
| **Files Flagged** | 9/25 (36%) | 17/25 (68%) | 0/25 (0%) |
| **Speed Ranking** | 🥇 Fastest | 🥈 Close | 🥉 Slow |
| **Detection Style** | Structural knots | Complexity metrics | Style/Syntax |

---

## Detailed Results by File

### Complex Files (High Complexity Expected)

| File | 4-Tiers Score | Radon CC | Pylint | Agreement |
|------|---------------|----------|--------|-----------|
| complex_algorithm.py | 0.284 ⚠️ | 19 ⚠️ | OK | ⚠️ 2/3 |
| complex_nested.py | 0.284 ⚠️ | 19 ⚠️ | OK | ⚠️ 2/3 |
| complex_parser.py | 0.284 ⚠️ | 19 ⚠️ | OK | ⚠️ 2/3 |
| complex_recursion.py | 0.284 ⚠️ | 19 ⚠️ | OK | ⚠️ 2/3 |
| complex_state_machine.py | 0.284 ⚠️ | 19 ⚠️ | OK | ⚠️ 2/3 |

**Finding:** Both 4-Tiers and Radon correctly identified all 5 complex files. Pylint (with `--errors-only`) found no errors.

### Duplication Files (Similar Code Patterns)

| File | 4-Tiers Score | Radon CC | Pylint | Agreement |
|------|---------------|----------|--------|-----------|
| duplicate_api_calls.py | 0.119 | 4 ⚠️ | OK | ⚠️ 1/3 |
| duplicate_logging.py | 0.119 | 4 ⚠️ | OK | ⚠️ 1/3 |
| duplicate_validation.py | 0.119 | 4 ⚠️ | OK | ⚠️ 1/3 |

**Finding:** Only Radon flagged these (low complexity). 4-Tiers did NOT detect the similar-but-not-identical code patterns. **Known limitation.**

### Issues Files (Specific Code Problems)

| File | 4-Tiers Score | Radon CC | Pylint | Agreement |
|------|---------------|----------|--------|-----------|
| issues_complexity_spike.py | 0.284 ⚠️ | 6 ⚠️ | OK | ⚠️ 2/3 |
| issues_dead_code.py | 0.269 ⚠️ | 2 | OK | ⚠️ 1/3 |
| issues_long_function.py | 0.119 | 1 | OK | ⚠️ 1/3 |
| issues_many_params.py | 0.284 ⚠️ | 1 | OK | ⚠️ 1/3 |
| issues_todo.py | 0.254 ⚠️ | 2 | OK | ⚠️ 1/3 |

**Finding:** 4-Tiers uniquely detected:
- Dead code (Feature D)
- Too many parameters (Feature H)
- TODO comments (Feature E)

### Simple Files (Low Complexity Baseline)

| File | 4-Tiers Score | Radon CC | Pylint | Agreement |
|------|---------------|----------|--------|-----------|
| simple_dicts.py | 0.114 | 2 ✅ | OK | ✅ None |
| simple_io.py | 0.114 | 2 ✅ | OK | ✅ None |
| simple_lists.py | 0.114 | 2 ✅ | OK | ✅ None |
| simple_math.py | 0.114 | 2 ✅ | OK | ✅ None |
| simple_strings.py | 0.114 | 2 ✅ | OK | ✅ None |

**Finding:** All tools correctly passed simple files as clean.

---

## Performance Comparison

### Raw Speed

```
4-Tiers:  ████ 1.02 ms
Radon:    █████ 1.15 ms  
Pylint:   ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 299.71 ms
```

### Speedup Factors

- 4-Tiers is **1.13x faster** than Radon
- 4-Tiers is **292.7x faster** than Pylint

---

## Detection Agreement Analysis

### Agreement Matrix

| Files | Count | Description |
|-------|-------|-------------|
| All 3 flag | 0 | No consensus on high-priority issues |
| 2 of 3 flag | 6 | Partial agreement (mostly 4-Tiers + Radon) |
| 1 of 3 flags | 14 | Tool-specific detection |
| None flag | 5 | Clean files (all agree) |

### Unique Detections by Tool

**4-Tiers Only (3 files):**
- `issues_dead_code.py` - Detected unreachable code (Feature D)
- `issues_many_params.py` - Detected anti-pattern (Feature H)
- `issues_todo.py` - Detected TODO/FIXME comments (Feature E)

**Radon Only (11 files):**
- All `duplicate_*.py` files - Detected similar patterns via complexity
- All `medium_*.py` files - Complexity threshold exceeded
- `mixed_*.py` files - Maintainability Index < 60

**Pylint Only (0 files):**
- With `--errors-only`, found no unique issues
- Would find more with full rule set (but much slower)

---

## Tool-Specific Strengths

### 4-Tiers ✅

**Strengths:**
- Fastest performance
- Detects anti-patterns (Feature H)
- Detects TODOs (Feature E)
- Detects dead code (Feature D)
- 8-dimensional analysis
- Severity classification

**Weaknesses:**
- Misses duplication (Feature A needs improvement)
- No raw metrics (LOC, SLOC)
- No maintainability index

### Radon ✅

**Strengths:**
- Industry-standard complexity metrics
- Maintainability Index
- Raw code metrics
- Detects all complexity issues
- Fast performance (close to 4-Tiers)

**Weaknesses:**
- No anti-pattern detection
- No TODO detection
- No dead code detection
- Single-dimension analysis

### Pylint ✅

**Strengths:**
- Comprehensive rule set (when not using `--errors-only`)
- Style enforcement
- Error detection
- Well-established

**Weaknesses:**
- Extremely slow (292x slower)
- With `--errors-only`, finds very little
- High false positive rate (with full rules)

---

## Recommendations

### Use 4-Tiers For:
- Quick health checks (fastest)
- Anti-pattern detection
- TODO/FIXME tracking
- Dead code identification
- Multi-dimensional analysis

### Use Radon For:
- Complexity metrics
- Maintainability Index
- Raw code statistics
- Industry-standard reporting

### Use Pylint For:
- Style enforcement
- Comprehensive linting (if speed not critical)
- CI/CD gates (nightly, not per-commit)

### Combined Workflow:
```bash
# Fast pre-commit check
4-tiers analyze

# Detailed analysis
radon cc -a -nc .

# Style check (nightly)
pylint src/
```

---

## Correlation with Radon

| Feature vs Radon Metric | Expected | Actual | Status |
|------------------------|----------|--------|--------|
| Knot Score vs CC | Medium | Low | ⚠️ Review |
| Feature F vs CC | High | Low | ⚠️ Needs calibration |

**Note:** Feature F (Complexity Trajectory) showed weak correlation with Radon CC in this expanded corpus. May need threshold adjustment.

---

## Conclusion

4-Tiers CodeCheck offers:
1. **Speed**: Fastest tool (1.02 ms avg)
2. **Unique detections**: Anti-patterns, TODOs, dead code
3. **Multi-dimensional**: 8 features vs single metrics
4. **Trade-off**: Misses some complexity (Radon better), misses style (Pylint better)

**Best use case:** Fast structural health assessment combined with Radon for complexity metrics.

---

*Report generated: April 2, 2026*  
*Raw data: tool_comparison_results.json*
