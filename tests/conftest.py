"""
Pytest configuration for V3 tests.
"""

import pytest
import sys
import os

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def pytest_configure(config):
    """Register custom markers for gates."""
    config.addinivalue_line("markers", "gate1: Feature Extraction Tests (Must Pass)")
    config.addinivalue_line("markers", "gate2: Core Function Tests (Must Pass)")
    config.addinivalue_line("markers", "gate3: Integration Tests (Must Pass)")
    config.addinivalue_line("markers", "gate4: Performance Tests (Must Pass)")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Add markers to test items based on class."""
    for item in items:
        # Ensure all tests have proper markers
        if "TestFeatureExtraction" in item.nodeid:
            item.add_marker(pytest.mark.gate1)
        elif "TestCoreFunctions" in item.nodeid:
            item.add_marker(pytest.mark.gate2)
        elif "TestIntegration" in item.nodeid:
            item.add_marker(pytest.mark.gate3)
        elif "TestPerformance" in item.nodeid:
            item.add_marker(pytest.mark.gate4)
