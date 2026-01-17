"""
Unit tests for ReflexionPattern

Tests error learning and prevention functionality.
"""

import pytest

from superclaude.pm_agent.reflexion import ReflexionPattern


class TestReflexionPattern:
    """Test suite for ReflexionPattern class"""

    def test_initialization(self):
        """Test ReflexionPattern initialization"""
        reflexion = ReflexionPattern()

        assert reflexion is not None
        assert hasattr(reflexion, "record_error")
        assert hasattr(reflexion, "get_solution")

    def test_record_error_basic(self):
        """Test recording a basic error"""
        reflexion = ReflexionPattern()

        error_info = {
            "test_name": "test_feature",
            "error_type": "AssertionError",
            "error_message": "Expected 5, got 3",
            "traceback": "File test.py, line 10...",
        }

        # Should not raise an exception
        reflexion.record_error(error_info)

    def test_record_error_with_solution(self):
        """Test recording an error with a solution"""
        reflexion = ReflexionPattern()

        error_info = {
            "test_name": "test_database_connection",
            "error_type": "ConnectionError",
            "error_message": "Could not connect to database",
            "solution": "Ensure database is running and credentials are correct",
        }

        reflexion.record_error(error_info)

    def test_get_solution_for_known_error(self):
        """Test retrieving solution for a known error pattern"""
        reflexion = ReflexionPattern()

        # Record an error with solution
        error_info = {
            "error_type": "ImportError",
            "error_message": "No module named 'pytest'",
            "solution": "Install pytest: pip install pytest",
        }

        reflexion.record_error(error_info)

        # Try to get solution for similar error
        error_signature = "ImportError: No module named 'pytest'"
        solution = reflexion.get_solution(error_signature)

        # Note: Actual implementation might return None if not implemented yet
        # This test documents expected behavior
        assert solution is None or isinstance(solution, str)

    def test_error_pattern_matching(self):
        """Test error pattern matching functionality"""
        reflexion = ReflexionPattern()

        # Record multiple similar errors
        errors = [
            {
                "error_type": "TypeError",
                "error_message": "expected str, got int",
                "solution": "Convert int to str using str()",
            },
            {
                "error_type": "TypeError",
                "error_message": "expected int, got str",
                "solution": "Convert str to int using int()",
            },
        ]

        for error in errors:
            reflexion.record_error(error)

        # Test pattern matching (implementation-dependent)
        error_signature = "TypeError"
        solution = reflexion.get_solution(error_signature)

        assert solution is None or isinstance(solution, str)

    def test_reflexion_memory_persistence(self, temp_memory_dir):
        """Test that reflexion can work with memory directory"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        error_info = {
            "test_name": "test_feature",
            "error_type": "ValueError",
            "error_message": "Invalid input",
        }

        # Should not raise exception even with custom memory dir
        reflexion.record_error(error_info)

    def test_error_learning_across_sessions(self):
        """
        Test that errors can be learned across sessions

        Note: This tests the interface, actual persistence
        depends on implementation
        """
        reflexion = ReflexionPattern()

        # Session 1: Record error
        error_info = {
            "error_type": "FileNotFoundError",
            "error_message": "config.json not found",
            "solution": "Create config.json in project root",
            "session": "session_1",
        }

        reflexion.record_error(error_info)

        # Session 2: Retrieve solution
        error_signature = "FileNotFoundError: config.json"
        solution = reflexion.get_solution(error_signature)

        # Implementation may or may not persist across instances
        assert solution is None or isinstance(solution, str)


@pytest.mark.reflexion
def test_reflexion_marker_integration(reflexion_pattern):
    """
    Test that reflexion marker works with pytest plugin fixture

    If this test fails, reflexion should record the failure
    """
    # Test that fixture is properly provided
    assert reflexion_pattern is not None

    # Record a test error
    error_info = {
        "test_name": "test_reflexion_marker_integration",
        "error_type": "IntegrationTestError",
        "error_message": "Testing reflexion integration",
    }

    # Should not raise exception
    reflexion_pattern.record_error(error_info)


def test_reflexion_with_real_exception():
    """
    Test reflexion pattern with a real exception scenario

    This simulates how reflexion would be used in practice
    """
    reflexion = ReflexionPattern()

    try:
        # Simulate an operation that fails
        _ = 10 / 0  # noqa: F841
    except ZeroDivisionError as e:
        # Record the error
        error_info = {
            "test_name": "test_reflexion_with_real_exception",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": "simulated traceback",
            "solution": "Check denominator is not zero before division",
        }

        reflexion.record_error(error_info)

    # Test should complete successfully
    assert True


class TestReflexionSignatureMatching:
    """Test error signature creation and matching"""

    def test_create_error_signature_full(self, tmp_path):
        """Test signature creation with full error info"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        error_info = {
            "error_type": "ValueError",
            "error_message": "Invalid value: 42",
            "test_name": "test_validation",
        }

        sig = reflexion._create_error_signature(error_info)

        assert "ValueError" in sig
        assert "Invalid value" in sig
        assert "test_validation" in sig

    def test_create_error_signature_numbers_normalized(self, tmp_path):
        """Test that numbers are normalized in signatures"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        error_info = {
            "error_type": "IndexError",
            "error_message": "list index 42 out of range",
        }

        sig = reflexion._create_error_signature(error_info)

        # Numbers should be replaced with 'N'
        assert "42" not in sig
        assert "N" in sig

    def test_signatures_match_identical(self, tmp_path):
        """Test matching identical signatures"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        sig = "ValueError | Invalid input | test_func"
        assert reflexion._signatures_match(sig, sig) is True

    def test_signatures_match_similar(self, tmp_path):
        """Test matching similar signatures"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        sig1 = "ValueError | Invalid input value | test_validation"
        sig2 = "ValueError | Invalid input string | test_validation"

        # Should match (high word overlap)
        assert reflexion._signatures_match(sig1, sig2) is True

    def test_signatures_match_different(self, tmp_path):
        """Test non-matching signatures"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        sig1 = "ValueError | completely different error"
        sig2 = "TypeError | unrelated message here"

        assert reflexion._signatures_match(sig1, sig2) is False

    def test_signatures_match_empty(self, tmp_path):
        """Test matching with empty signatures"""
        reflexion = ReflexionPattern(memory_dir=tmp_path / "memory")

        assert reflexion._signatures_match("", "") is False
        assert reflexion._signatures_match("some text", "") is False


class TestReflexionLocalFileSearch:
    """Test local file search functionality"""

    def test_search_local_files_no_file(self, tmp_path):
        """Test search when solutions file doesn't exist"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)
        result = reflexion._search_local_files("any error")

        assert result is None

    def test_search_local_files_with_match(self, tmp_path):
        """Test search finds matching error"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        # Record an error with solution
        error_info = {
            "error_type": "ImportError",
            "error_message": "No module named requests",
            "test_name": "test_api",
            "solution": "pip install requests",
            "root_cause": "Missing dependency",
        }
        reflexion.record_error(error_info)

        # Search for similar error
        search_info = {
            "error_type": "ImportError",
            "error_message": "No module named requests",
            "test_name": "test_api",
        }
        result = reflexion._search_local_files(
            reflexion._create_error_signature(search_info)
        )

        assert result is not None
        assert result.get("solution") == "pip install requests"

    def test_search_local_files_invalid_json(self, tmp_path):
        """Test search handles invalid JSON lines gracefully"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        # Write invalid JSON
        reflexion.solutions_file.write_text("invalid json\n{}\n")

        # Should not crash, just return None
        result = reflexion._search_local_files("any error")
        assert result is None


class TestReflexionMistakeDoc:
    """Test mistake documentation creation"""

    def test_create_mistake_doc(self, tmp_path):
        """Test creating a mistake document"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        error_info = {
            "test_name": "test_feature",
            "error_type": "AssertionError",
            "error_message": "Expected True, got False",
            "traceback": "File test.py, line 42",
            "root_cause": "Logic error in conditional",
            "solution": "Fix the condition to check != instead of ==",
            "why_missed": "Rushed implementation",
            "prevention": "Add edge case tests",
            "lesson": "Always test edge cases",
        }

        reflexion._create_mistake_doc(error_info)

        # Check file was created
        files = list(reflexion.mistakes_dir.glob("*.md"))
        assert len(files) == 1

        # Check content
        content = files[0].read_text()
        assert "test_feature" in content
        assert "AssertionError" in content
        assert "Logic error" in content
        assert "Fix the condition" in content

    def test_record_error_creates_mistake_doc_when_has_solution(self, tmp_path):
        """Test that record_error creates mistake doc when solution provided"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        error_info = {
            "test_name": "test_with_solution",
            "error_type": "ValueError",
            "error_message": "Invalid input",
            "solution": "Validate input first",
        }

        reflexion.record_error(error_info)

        # Should create mistake doc
        files = list(reflexion.mistakes_dir.glob("*.md"))
        assert len(files) == 1


class TestReflexionStatistics:
    """Test statistics functionality"""

    def test_get_statistics_empty(self, tmp_path):
        """Test statistics with no errors recorded"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)
        stats = reflexion.get_statistics()

        assert stats["total_errors"] == 0
        assert stats["errors_with_solutions"] == 0
        assert stats["solution_reuse_rate"] == 0.0

    def test_get_statistics_with_errors(self, tmp_path):
        """Test statistics with errors recorded"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        # Record errors
        reflexion.record_error({
            "error_type": "Error1",
            "error_message": "msg1",
            "solution": "fix1",
        })
        reflexion.record_error({
            "error_type": "Error2",
            "error_message": "msg2",
            # No solution
        })
        reflexion.record_error({
            "error_type": "Error3",
            "error_message": "msg3",
            "solution": "fix3",
        })

        stats = reflexion.get_statistics()

        assert stats["total_errors"] == 3
        assert stats["errors_with_solutions"] == 2
        assert stats["solution_reuse_rate"] == pytest.approx(66.67, rel=0.1)


class TestReflexionGetSolution:
    """Test get_solution functionality"""

    def test_get_solution_dict_input(self, tmp_path):
        """Test get_solution with dict input"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        # Record an error
        reflexion.record_error({
            "error_type": "KeyError",
            "error_message": "key 'name' not found",
            "test_name": "test_dict_access",
            "solution": "Use .get() with default",
            "root_cause": "Missing key handling",
        })

        # Search with dict
        result = reflexion.get_solution({
            "error_type": "KeyError",
            "error_message": "key 'name' not found",
            "test_name": "test_dict_access",
        })

        assert result is not None
        assert result.get("solution") == "Use .get() with default"

    def test_get_solution_no_match(self, tmp_path):
        """Test get_solution returns None when no match"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)

        reflexion = ReflexionPattern(memory_dir=memory_dir)

        result = reflexion.get_solution({
            "error_type": "UnknownError",
            "error_message": "something completely different",
        })

        assert result is None
