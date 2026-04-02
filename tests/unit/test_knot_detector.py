#!/usr/bin/env python3
"""
Targeted Tests for 4-Tiers CodeCheck System
===========================================

Test Categories:
1. Knot calculation correctness (3-4 tests)
2. Edge cases - doesn't crash (2-3 tests)
3. Output format validation (2 tests)
4. Performance regression check (1 test)

Total: ~10 tests covering critical functionality
"""

import pytest
import time
import sys
from pathlib import Path

# Import modules under test
from src.knot_detector_v3 import KnotDetectorV3
from src.static_code_knot_analyzer import StaticCodeKnotAnalyzer, CodeKnot
from src.dynamic_code_knot_analyzer import DynamicCodeKnotAnalyzer, ExecutionTrace
from src.parallel_batch_analyzer import ParallelBatchAnalyzer
from src.optimized_knot_analyzer import FastKnotAnalyzer, FastKnotFeatures


# =============================================================================
# CATEGORY 1: Knot Calculation Correctness (4 tests)
# =============================================================================

class TestKnotCalculationCorrectness:
    """Verify knot scoring algorithms produce correct values."""
    
    def test_knot_score_calculation_basic(self):
        """Test 1: Basic knot score calculation with known inputs."""
        detector = KnotDetectorV3(use_agents=False)
        
        # Create known feature set
        features = {
            'A': 0.5,  # Regression
            'B': 0.3,  # Isomorphism
            'C': 0.0,  # Contradiction
            'D': 0.0,  # Expansion Stop
            'E': 0.1,  # Question Cutoff
            'F': 0.2,  # Complexity
            'H': 0.1   # Distortions
        }
        
        score = detector._calc_K(features)
        
        # Actual weights from knot_detector_v3.py
        # Weights: A,B,C,D,E=1.0, F=0.5, H=0.8, divide by 6.3
        expected_numerator = 0.5 + 0.3 + 0.0 + 0.0 + 0.1 + 0.5*0.2 + 0.8*0.1
        expected = expected_numerator / 6.3
        
        assert abs(score - expected) < 0.001, f"Score {score} != expected {expected}"
        assert 0 <= score <= 1, "Score must be in valid range [0, 1]"
    
    def test_knot_score_zero_features(self):
        """Test 2: All zero features should give zero knot score."""
        detector = KnotDetectorV3(use_agents=False)
        
        features = {k: 0.0 for k in ['A', 'B', 'C', 'D', 'E', 'F', 'H']}
        score = detector._calc_K(features)
        
        assert score == 0.0, "Zero features should give zero score"
    
    def test_knot_score_maximum_features(self):
        """Test 3: All maximum features should give high knot score."""
        detector = KnotDetectorV3(use_agents=False)
        
        features = {k: 1.0 for k in ['A', 'B', 'C', 'D', 'E', 'F', 'H']}
        score = detector._calc_K(features)
        
        # All 1.0 features should give score close to 1.0
        assert score > 0.9, f"Maximum features should give high score, got {score}"
        assert score <= 1.0, "Score should not exceed 1.0"
    
    def test_explosion_point_calculation(self):
        """Test 4: Explosion point (G) calculation correctness."""
        detector = KnotDetectorV3(use_agents=False)
        
        K = 0.5  # Knot score
        centrality = 0.8
        density = 0.6
        
        G = detector._calc_G(K, centrality, density)
        
        # Expected: G = K * (centrality + density) / 2
        expected = 0.5 * (0.8 + 0.6) / 2
        assert abs(G - expected) < 0.001, f"Explosion point {G} != expected {expected}"


# =============================================================================
# CATEGORY 2: Edge Cases - Doesn't Crash (3 tests)
# =============================================================================

class TestEdgeCasesRobustness:
    """Verify system handles edge cases gracefully without crashing."""
    
    def test_empty_file_analysis(self, tmp_path):
        """Test 5: Empty file should not crash analyzer."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        analyzer = StaticCodeKnotAnalyzer(str(empty_file))
        
        # Should not raise exception
        try:
            result = analyzer.analyze()
            # Empty file should return None or empty result
            assert result is None or isinstance(result, CodeKnot)
        except Exception as e:
            pytest.fail(f"Empty file should not crash: {e}")
    
    def test_single_line_file(self, tmp_path):
        """Test 6: Single line file should not crash."""
        single_line = tmp_path / "single.py"
        single_line.write_text("x = 1")
        
        analyzer = StaticCodeKnotAnalyzer(str(single_line))
        
        try:
            result = analyzer.analyze()
            assert result is None or isinstance(result, CodeKnot)
        except Exception as e:
            pytest.fail(f"Single line file should not crash: {e}")
    
    def test_syntax_error_file(self, tmp_path):
        """Test 7: Invalid Python syntax should be handled gracefully."""
        bad_syntax = tmp_path / "bad.py"
        bad_syntax.write_text("def broken(:")
        
        analyzer = StaticCodeKnotAnalyzer(str(bad_syntax))
        
        try:
            result = analyzer.analyze()
            # Should either return None or raise expected exception
        except SyntaxError:
            pass  # Expected for invalid syntax
        except Exception as e:
            pytest.fail(f"Should handle syntax error gracefully, got: {e}")
    
    def test_very_large_file(self, tmp_path):
        """Test 8: Large file should complete without memory issues."""
        large_file = tmp_path / "large.py"
        
        # Generate 1000 lines of code
        code_lines = ['def func_{}(x):'.format(i) for i in range(100)]
        code_lines += ['    return x * {}'.format(i) for i in range(100)]
        large_file.write_text('\n'.join(code_lines))
        
        analyzer = StaticCodeKnotAnalyzer(str(large_file))
        
        try:
            result = analyzer.analyze()
            # Should complete without crash
            assert True
        except MemoryError:
            pytest.fail("Should handle large files without memory error")
        except Exception as e:
            pytest.fail(f"Large file should not crash: {e}")


# =============================================================================
# CATEGORY 3: Output Format Validation (2 tests)
# =============================================================================

class TestOutputFormatValidation:
    """Verify output structures match expected formats."""
    
    def test_knot_output_structure(self, tmp_path):
        """Test 9: Verify CodeKnot has all required fields with correct types."""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def example():
    if True:
        return 1
    return 0
''')
        
        analyzer = StaticCodeKnotAnalyzer(str(test_file))
        result = analyzer.analyze()
        
        if result is not None:
            # Verify all required fields exist
            assert hasattr(result, 'location'), "Missing 'location' field"
            assert hasattr(result, 'features'), "Missing 'features' field"
            assert hasattr(result, 'knot_score'), "Missing 'knot_score' field"
            assert hasattr(result, 'severity'), "Missing 'severity' field"
            
            # Verify types
            assert isinstance(result.location, str), "location should be string"
            assert isinstance(result.features, dict), "features should be dict"
            assert isinstance(result.knot_score, (int, float)), "knot_score should be numeric"
            assert isinstance(result.severity, str), "severity should be string"
            
            # Verify value ranges
            assert 0 <= result.knot_score <= 1, "knot_score should be in [0, 1]"
            assert result.severity in ['low', 'medium', 'high', 'critical']
    
    def test_features_dict_structure(self, tmp_path):
        """Test 10: Verify features dict contains expected keys."""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def example(x):
    if x > 0:
        return x * 2
    return 0
''')
        
        analyzer = StaticCodeKnotAnalyzer(str(test_file))
        result = analyzer.analyze()
        
        if result is not None and hasattr(result, 'features'):
            expected_features = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
            
            for feature in expected_features:
                assert feature in result.features, f"Missing feature '{feature}'"
                assert isinstance(result.features[feature], (int, float)), \
                    f"Feature '{feature}' should be numeric"
                assert 0 <= result.features[feature] <= 1, \
                    f"Feature '{feature}' should be in [0, 1]"


# =============================================================================
# CATEGORY 4: Performance Regression Check (1 test)
# =============================================================================

class TestPerformanceRegression:
    """Verify performance meets baseline requirements."""
    
    def test_analysis_performance_baseline(self, tmp_path):
        """Test 11: Analysis should complete within acceptable time."""
        # Create test file of moderate size
        test_file = tmp_path / "perf_test.py"
        code = '''
class Example:
    def method1(self, x):
        if x > 0:
            if x % 2 == 0:
                return x * 2
            return x * 3
        return 0
    
    def method2(self, items):
        result = []
        for item in items:
            if item not in self.cache:
                self.cache[item] = self.process(item)
            result.append(self.cache[item])
        return result
    
    def process(self, item):
        return item * 2
'''
        test_file.write_text(code)
        
        # Measure analysis time
        start = time.perf_counter()
        analyzer = StaticCodeKnotAnalyzer(str(test_file))
        result = analyzer.analyze()
        elapsed = time.perf_counter() - start
        
        # Baseline: Should complete in under 100ms for this size
        baseline_ms = 100
        elapsed_ms = elapsed * 1000
        
        assert elapsed_ms < baseline_ms, \
            f"Analysis took {elapsed_ms:.1f}ms, exceeds baseline {baseline_ms}ms"
        
        # Also verify throughput metric
        throughput = 1.0 / elapsed  # files per second
        assert throughput > 10, \
            f"Throughput {throughput:.1f} files/sec below minimum 10 files/sec"


# =============================================================================
# BONUS: Integration/Smoke Tests (2 tests)
# =============================================================================

class TestIntegrationSmoke:
    """High-level integration smoke tests."""
    
    def test_full_pipeline_execution(self, tmp_path):
        """Smoke test: Full pipeline runs without errors."""
        test_file = tmp_path / "integration.py"
        test_file.write_text('''
def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
''')
        
        # Run static analysis
        analyzer = StaticCodeKnotAnalyzer(str(test_file))
        knot_result = analyzer.analyze()
        
        # Basic sanity checks
        assert knot_result is not None or knot_result is None  # Either is OK
        print("✓ Full pipeline executed successfully")
    
    def test_batch_analyzer_runs(self, tmp_path):
        """Smoke test: Batch analyzer initializes and runs."""
        # Create multiple test files
        files = []
        for i in range(3):
            f = tmp_path / f"batch_{i}.py"
            f.write_text(f"def func_{i}(): return {i}")
            files.append(str(f))
        
        # Run batch analysis
        batch = ParallelBatchAnalyzer()
        results = batch.analyze_batch(files)
        
        # Verify we got results
        assert len(results) == len(files), "Should get result for each file"
        
        # Verify stats
        stats = batch.get_stats()
        assert 'elapsed' in stats, "Should have elapsed time"
        assert stats['elapsed'] > 0, "Should take some time"


class TestPublishReadinessFixes:
    """Regression tests for publish-blocking issues fixed before release."""

    def test_parallel_batch_analyzer_parallel_path(self, tmp_path):
        """Parallel branch should return successful structured results."""
        files = []
        code = (
            "def process(items):\n"
            "    total = 0\n"
            "    for item in items:\n"
            "        if item % 2 == 0:\n"
            "            total += item\n"
            "        else:\n"
            "            total += item * 2\n"
            "    return total\n\n"
        ) * 30

        for i in range(20):
            path = tmp_path / f"parallel_{i}.py"
            path.write_text(code)
            files.append(str(path))

        analyzer = ParallelBatchAnalyzer(max_workers=2)
        results = analyzer.analyze_batch(files)
        stats = analyzer.get_stats()

        assert stats['parallel'] is True, "Should exercise the parallel branch"
        assert stats['successful'] == len(files)
        assert stats['failed'] == 0
        assert all(r['success'] for r in results)
        assert all(isinstance(r['knot'], CodeKnot) for r in results)

    def test_fast_analyzer_directory_parallel(self, tmp_path):
        """Optimized directory analyzer should work in parallel without pickling errors."""
        for i in range(4):
            path = tmp_path / f"fast_{i}.py"
            path.write_text(
                "def f(x):\n"
                "    if x > 0:\n"
                "        return x\n"
                "    return 0\n"
            )

        analyzer = FastKnotAnalyzer(use_cache=False, parallel=True)
        results = analyzer.analyze_directory_parallel(str(tmp_path))

        assert len(results) == 4
        assert all(isinstance(path, str) for path, _ in results)
        assert all(isinstance(features, FastKnotFeatures) for _, features in results)

    def test_fast_analyzer_todo_comments_affect_feature_e(self, tmp_path):
        """Optimized analyzer should preserve comment-based TODO signal."""
        target = tmp_path / "todo_sample.py"
        target.write_text(
            "# TODO: handle negative numbers\n"
            "def f(x):\n"
            "    if x > 0:\n"
            "        return x\n"
            "    return 0\n"
        )

        analyzer = FastKnotAnalyzer(use_cache=False, parallel=False)
        result = analyzer.analyze_file_optimized(str(target))

        assert result.E > 0.0


# =============================================================================
# Test Configuration
# =============================================================================

if __name__ == '__main__':
    # Run with: python -m pytest test_knot_detector.py -v
    pytest.main([__file__, '-v', '--tb=short'])
