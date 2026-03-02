"""
Unit tests for TokenBudgetManager

Tests token budget allocation and management functionality.
"""

import pytest

from superclaude.pm_agent.token_budget import TokenBudgetManager


class TestTokenBudgetManager:
    """Test suite for TokenBudgetManager class"""

    def test_simple_complexity(self):
        """Test token budget for simple tasks (typo fixes)"""
        manager = TokenBudgetManager(complexity="simple")

        assert manager.limit == 200
        assert manager.complexity == "simple"

    def test_medium_complexity(self):
        """Test token budget for medium tasks (bug fixes)"""
        manager = TokenBudgetManager(complexity="medium")

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_complex_complexity(self):
        """Test token budget for complex tasks (features)"""
        manager = TokenBudgetManager(complexity="complex")

        assert manager.limit == 2500
        assert manager.complexity == "complex"

    def test_default_complexity(self):
        """Test default complexity is medium"""
        manager = TokenBudgetManager()

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_invalid_complexity_defaults_to_medium(self):
        """Test that invalid complexity defaults to medium"""
        manager = TokenBudgetManager(complexity="invalid")

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_token_usage_tracking(self):
        """Test token usage tracking if implemented"""
        manager = TokenBudgetManager(complexity="simple")

        # Check if usage tracking is available
        if hasattr(manager, "used"):
            assert manager.used == 0

        if hasattr(manager, "remaining"):
            assert manager.remaining == manager.limit

    def test_budget_allocation_strategy(self):
        """Test token budget allocation strategy"""
        # Simple tasks should have smallest budget
        simple = TokenBudgetManager(complexity="simple")

        # Medium tasks should have moderate budget
        medium = TokenBudgetManager(complexity="medium")

        # Complex tasks should have largest budget
        complex_task = TokenBudgetManager(complexity="complex")

        assert simple.limit < medium.limit < complex_task.limit

    def test_complexity_examples(self):
        """Test that complexity levels match documented examples"""
        # Simple: typo fix (200 tokens)
        simple = TokenBudgetManager(complexity="simple")
        assert simple.limit == 200

        # Medium: bug fix, small feature (1,000 tokens)
        medium = TokenBudgetManager(complexity="medium")
        assert medium.limit == 1000

        # Complex: feature implementation (2,500 tokens)
        complex_task = TokenBudgetManager(complexity="complex")
        assert complex_task.limit == 2500


@pytest.mark.complexity("simple")
def test_complexity_marker_simple(token_budget):
    """
    Test that complexity marker works with pytest plugin fixture

    This test should have a simple (200 token) budget
    """
    assert token_budget.limit == 200
    assert token_budget.complexity == "simple"


@pytest.mark.complexity("medium")
def test_complexity_marker_medium(token_budget):
    """
    Test that complexity marker works with medium budget

    This test should have a medium (1000 token) budget
    """
    assert token_budget.limit == 1000
    assert token_budget.complexity == "medium"


@pytest.mark.complexity("complex")
def test_complexity_marker_complex(token_budget):
    """
    Test that complexity marker works with complex budget

    This test should have a complex (2500 token) budget
    """
    assert token_budget.limit == 2500
    assert token_budget.complexity == "complex"


def test_token_budget_no_marker(token_budget):
    """
    Test that token_budget fixture defaults to medium without marker

    Tests without complexity marker should get medium budget
    """
    assert token_budget.limit == 1000
    assert token_budget.complexity == "medium"


class TestTokenBudgetLevels:
    """Test suite for token budget levels and marker extraction"""

    def test_budget_simple_level(self):
        """
        Test simple complexity returns 200 tokens

        Simple tasks (typo fixes, trivial changes) should
        have the smallest token budget of 200.
        """
        manager = TokenBudgetManager(complexity="simple")

        assert manager.limit == 200, f"Expected 200 tokens for simple, got {manager.limit}"
        assert manager.complexity == "simple"
        assert manager.used == 0
        assert manager.remaining == 200

    def test_budget_medium_level(self):
        """
        Test medium complexity returns 1000 tokens

        Medium tasks (bug fixes, small features) should
        have a moderate token budget of 1000.
        """
        manager = TokenBudgetManager(complexity="medium")

        assert manager.limit == 1000, f"Expected 1000 tokens for medium, got {manager.limit}"
        assert manager.complexity == "medium"
        assert manager.used == 0
        assert manager.remaining == 1000

    def test_budget_complex_level(self):
        """
        Test complex complexity returns 2500 tokens

        Complex tasks (large features, refactoring) should
        have the largest token budget of 2500.
        """
        manager = TokenBudgetManager(complexity="complex")

        assert manager.limit == 2500, f"Expected 2500 tokens for complex, got {manager.limit}"
        assert manager.complexity == "complex"
        assert manager.used == 0
        assert manager.remaining == 2500

    def test_marker_extraction(self, request):
        """
        Test pytest marker extraction for complexity level

        Verifies the complexity marker is registered and can
        be retrieved from pytest configuration, which is how
        the token_budget fixture determines complexity level.
        """
        markers = request.config.getini("markers")
        marker_names = [m.split(":")[0] for m in markers]

        assert "complexity" in marker_names, (
            "complexity marker should be registered in pyproject.toml"
        )

        # Verify the marker accepts a level argument by checking
        # the LIMITS dict covers all documented levels
        expected_levels = {"simple", "medium", "complex"}
        assert set(TokenBudgetManager.LIMITS.keys()) == expected_levels
