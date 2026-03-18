"""
SuperClaude pytest plugin

Auto-loaded when superclaude is installed.
Provides auto-markers for test directory conventions.

Entry point registered in pyproject.toml:
    [project.entry-points.pytest11]
    superclaude = "superclaude.pytest_plugin"
"""

import pytest


def pytest_configure(config):
    """Register SuperClaude custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "hallucination: Hallucination detection tests")
    config.addinivalue_line("markers", "performance: Performance benchmark tests")


def pytest_report_header(config):
    """Add SuperClaude version to pytest header."""
    from . import __version__

    return f"SuperClaude: {__version__}"


def pytest_collection_modifyitems(config, items):
    """
    Auto-add markers based on test file location.

    - tests/unit/ → 'unit' marker
    - tests/integration/ → 'integration' marker
    - *hallucination* in path → 'hallucination' marker
    - *performance* or *benchmark* in path → 'performance' marker
    """
    for item in items:
        test_path = str(item.fspath)
        normalized_path = test_path.replace("\\", "/")

        if "/unit/" in normalized_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in normalized_path:
            item.add_marker(pytest.mark.integration)

        if "hallucination" in test_path:
            item.add_marker(pytest.mark.hallucination)
        elif "performance" in test_path or "benchmark" in test_path:
            item.add_marker(pytest.mark.performance)
