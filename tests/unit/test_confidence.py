"""
Unit tests for ConfidenceChecker

Tests pre-execution confidence assessment functionality.
"""

import asyncio

import pytest

from superclaude.pm_agent.confidence import (
    CheckResult,
    ConfidenceChecker,
    ConfidenceResult,
)


class TestConfidenceChecker:
    """Test suite for ConfidenceChecker class"""

    def test_high_confidence_scenario(self, sample_context):
        """
        Test that a well-prepared context returns high confidence (≥90%)

        All checks pass:
        - No duplicates (25%)
        - Architecture compliant (25%)
        - Official docs verified (20%)
        - OSS reference found (15%)
        - Root cause identified (15%)
        Total: 100%
        """
        checker = ConfidenceChecker()
        confidence = checker.assess(sample_context)

        assert confidence >= 0.9, f"Expected high confidence ≥0.9, got {confidence}"
        assert confidence == 1.0, "All checks passed should give 100% confidence"

    def test_low_confidence_scenario(self, low_confidence_context):
        """
        Test that an unprepared context returns low confidence (<70%)

        No checks pass: 0%
        """
        checker = ConfidenceChecker()
        confidence = checker.assess(low_confidence_context)

        assert confidence < 0.7, f"Expected low confidence <0.7, got {confidence}"
        assert confidence == 0.0, "No checks passed should give 0% confidence"

    def test_medium_confidence_scenario(self):
        """
        Test medium confidence scenario (70-89%)

        Some checks pass, some don't
        """
        checker = ConfidenceChecker()
        context = {
            "test_name": "test_feature",
            "duplicate_check_complete": True,  # 25%
            "architecture_check_complete": True,  # 25%
            "official_docs_verified": True,  # 20%
            "oss_reference_complete": False,  # 0%
            "root_cause_identified": False,  # 0%
        }

        confidence = checker.assess(context)

        assert 0.7 <= confidence < 0.9, (
            f"Expected medium confidence 0.7-0.9, got {confidence}"
        )
        assert confidence == 0.7, "Should be exactly 70%"

    def test_confidence_checks_recorded(self, sample_context):
        """Test that confidence checks are recorded in context"""
        checker = ConfidenceChecker()
        checker.assess(sample_context)

        assert "confidence_checks" in sample_context
        assert isinstance(sample_context["confidence_checks"], list)
        assert len(sample_context["confidence_checks"]) == 5

        # All checks should pass
        for check in sample_context["confidence_checks"]:
            assert check.startswith("✅"), f"Expected passing check, got: {check}"

    def test_get_recommendation_high(self):
        """Test recommendation for high confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.95)

        assert "High confidence" in recommendation
        assert "Proceed" in recommendation

    def test_get_recommendation_medium(self):
        """Test recommendation for medium confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.75)

        assert "Medium confidence" in recommendation
        assert "Continue investigation" in recommendation

    def test_get_recommendation_low(self):
        """Test recommendation for low confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.5)

        assert "Low confidence" in recommendation
        assert "STOP" in recommendation

def test_confidence_check_marker_integration(confidence_checker):
    """
    Test that confidence_checker fixture works with pytest plugin

    Note: We don't use @pytest.mark.confidence_check here because
    the hook builds minimal context (only test_name, test_file, markers)
    which results in low confidence and skips the test. The marker
    is intended for production tests, not for testing the fixture itself.
    """
    context = {
        "test_name": "test_confidence_check_marker_integration",
        "has_official_docs": True,
        "duplicate_check_complete": True,
        "architecture_check_complete": True,
        "official_docs_verified": True,
        "oss_reference_complete": True,
        "root_cause_identified": True,
    }

    confidence = confidence_checker.assess(context)
    assert confidence >= 0.7, "Confidence should be high enough"


def test_confidence_check_marker_skips_low_confidence(request):
    """
    Test that confidence_check marker is properly registered

    Verifies the marker exists and can be retrieved.
    The actual skip behavior is tested by the pytest plugin hook.
    """
    # Verify marker is registered (won't raise unknown marker warning)
    marker = request.config.getini("markers")
    marker_names = [m.split(":")[0] for m in marker]
    assert "confidence_check" in marker_names


class TestConfidenceResult:
    """Test suite for ConfidenceResult dataclass"""

    def test_returns_confidence_result(self, sample_context):
        """Test that assess returns ConfidenceResult"""
        checker = ConfidenceChecker()
        result = checker.assess(sample_context)

        assert isinstance(result, ConfidenceResult)
        assert result.score == 1.0
        assert len(result.checks) == 5
        assert "High confidence" in result.recommendation

    def test_check_results_structure(self, sample_context):
        """Test CheckResult structure in ConfidenceResult"""
        checker = ConfidenceChecker()
        result = checker.assess(sample_context)

        for check in result.checks:
            assert isinstance(check, CheckResult)
            assert isinstance(check.name, str)
            assert isinstance(check.passed, bool)
            assert isinstance(check.message, str)
            assert isinstance(check.weight, float)

    def test_comparison_operators(self):
        """Test numeric comparison operators"""
        result = ConfidenceResult(score=0.85, checks=[], recommendation="")

        assert result >= 0.8
        assert result > 0.8
        assert result <= 0.9
        assert result < 0.9
        assert result == 0.85
        assert not result == 0.9

    def test_float_conversion(self):
        """Test __float__ method"""
        result = ConfidenceResult(score=0.75, checks=[], recommendation="")

        assert float(result) == 0.75

    def test_backward_compatibility(self, sample_context):
        """Test backward compatibility with numeric comparisons"""
        checker = ConfidenceChecker()
        result = checker.assess(sample_context)

        # Old-style comparisons should work
        if result >= 0.9:
            passed = True
        else:
            passed = False

        assert passed is True
        assert result.score >= 0.9

    def test_context_still_populated(self, sample_context):
        """Test context is still populated for legacy callers"""
        checker = ConfidenceChecker()
        checker.assess(sample_context)

        # Legacy context should still have confidence_checks
        assert "confidence_checks" in sample_context
        assert isinstance(sample_context["confidence_checks"], list)
        assert len(sample_context["confidence_checks"]) == 5


class TestCachingBehavior:
    """Test LRU caching for tech stack detection"""

    def test_cache_hit(self, tmp_path):
        """Test that repeated calls use cached result"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        # Create a project with CLAUDE.md
        (tmp_path / "CLAUDE.md").write_text("Using React and Next.js")

        # Clear cache first
        _cached_detect_tech_stack.cache_clear()

        # First call - cache miss
        result1 = _cached_detect_tech_stack(str(tmp_path))

        # Second call - cache hit
        result2 = _cached_detect_tech_stack(str(tmp_path))

        # Results should be identical
        assert result1 == result2

        # Check cache info
        cache_info = _cached_detect_tech_stack.cache_info()
        assert cache_info.hits >= 1

    def test_cache_returns_tuple(self, tmp_path):
        """Test cached function returns hashable tuple"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        (tmp_path / "CLAUDE.md").write_text("Using pytest")
        _cached_detect_tech_stack.cache_clear()

        result = _cached_detect_tech_stack(str(tmp_path))

        # Result should be tuple of tuples
        assert isinstance(result, tuple)
        assert len(result) == 3
        frameworks, databases, tools = result
        assert isinstance(frameworks, tuple)
        assert isinstance(databases, tuple)
        assert isinstance(tools, tuple)


class TestRegistryPattern:
    """Test suite for registry pattern"""

    def test_default_checks_registered(self):
        """Test that default checks are registered on init"""
        checker = ConfidenceChecker()
        checks = checker.get_checks()

        assert len(checks) == 5
        names = [c.name for c in checks]
        assert "no_duplicates" in names
        assert "architecture_compliant" in names
        assert "official_docs" in names
        assert "oss_reference" in names
        assert "root_cause" in names

    def test_no_defaults_registration(self):
        """Test init without default checks"""
        checker = ConfidenceChecker(register_defaults=False)
        checks = checker.get_checks()

        assert len(checks) == 0

    def test_custom_check_registration(self):
        """Test registering a custom check"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        checker = ConfidenceChecker(register_defaults=False)
        custom_check = NoDuplicatesCheck(weight=1.0)
        checker.register_check(custom_check)

        checks = checker.get_checks()
        assert len(checks) == 1
        assert checks[0].name == "no_duplicates"
        assert checks[0].weight == 1.0

    def test_unregister_check(self):
        """Test unregistering a check by name"""
        checker = ConfidenceChecker()

        # Unregister one check
        result = checker.unregister_check("root_cause")
        assert result is True
        assert len(checker.get_checks()) == 4

        # Try to unregister non-existent
        result = checker.unregister_check("nonexistent")
        assert result is False
        assert len(checker.get_checks()) == 4

    def test_clear_checks(self):
        """Test clearing all checks"""
        checker = ConfidenceChecker()
        assert len(checker.get_checks()) == 5

        checker.clear_checks()
        assert len(checker.get_checks()) == 0

    def test_weight_normalization(self):
        """Test that weights are normalized"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck, RootCauseCheck

        checker = ConfidenceChecker(register_defaults=False)
        # Add two checks with weight 0.5 each (total = 1.0)
        checker.register_check(NoDuplicatesCheck(weight=0.5))
        checker.register_check(RootCauseCheck(weight=0.5))

        context = {
            "duplicate_check_complete": True,
            "root_cause_identified": True,
        }
        result = checker.assess(context)

        # Both pass, normalized score should be 1.0
        assert result.score == 1.0

    def test_weight_normalization_unequal(self):
        """Test weight normalization with unequal weights"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck, RootCauseCheck

        checker = ConfidenceChecker(register_defaults=False)
        # Add two checks: one with weight 3, one with weight 1 (total = 4)
        checker.register_check(NoDuplicatesCheck(weight=3.0))
        checker.register_check(RootCauseCheck(weight=1.0))

        # Only first check passes
        context = {
            "duplicate_check_complete": True,
            "root_cause_identified": False,
        }
        result = checker.assess(context)

        # First check contributes 3/4 = 0.75
        assert result.score == 0.75

    def test_empty_registry_returns_zero(self):
        """Test assess with empty registry"""
        checker = ConfidenceChecker(register_defaults=False)
        context = {}
        result = checker.assess(context)

        assert result.score == 0.0
        assert len(result.checks) == 0

    def test_protocol_compliance(self):
        """Test that concrete checks implement protocol"""
        from superclaude.pm_agent.confidence import (
            ArchitectureCheck,
            ConfidenceCheck,
            NoDuplicatesCheck,
            OfficialDocsCheck,
            OssReferenceCheck,
            RootCauseCheck,
        )

        checks = [
            NoDuplicatesCheck(),
            ArchitectureCheck(),
            OfficialDocsCheck(),
            OssReferenceCheck(),
            RootCauseCheck(),
        ]

        for check in checks:
            assert isinstance(check, ConfidenceCheck)
            assert hasattr(check, "name")
            assert hasattr(check, "weight")
            assert hasattr(check, "evaluate")

    def test_custom_check_class(self):
        """Test creating a fully custom check class"""
        from superclaude.pm_agent.confidence import ConfidenceCheck

        class AlwaysPassCheck:
            name = "always_pass"
            weight = 1.0

            def evaluate(self, context):
                return True, "Always passes"

        checker = ConfidenceChecker(register_defaults=False)
        custom = AlwaysPassCheck()

        # Should satisfy protocol
        assert isinstance(custom, ConfidenceCheck)

        checker.register_check(custom)
        result = checker.assess({})

        assert result.score == 1.0
        assert result.checks[0].passed is True


class TestAsyncSupport:
    """Tests for async confidence checking (Phase 3)"""

    @pytest.mark.asyncio
    async def test_assess_async_with_sync_checks(self):
        """Test assess_async with synchronous checks"""
        checker = ConfidenceChecker()
        context = {
            "task_name": "implement async",
            "has_official_docs": True,
            "root_cause": "Need async support for MCP integration",
            "evidence": "MCP tools return coroutines",
        }
        result = await checker.assess_async(context)

        assert isinstance(result, ConfidenceResult)
        assert 0.0 <= result.score <= 1.0
        assert len(result.checks) == 5  # default checks

    @pytest.mark.asyncio
    async def test_assess_async_with_async_check(self):
        """Test assess_async with a custom async check"""
        from superclaude.pm_agent.confidence import AsyncConfidenceCheck

        class AsyncMcpCheck:
            """Custom async check simulating MCP call"""

            name = "async_mcp"
            weight = 1.0

            async def evaluate_async(self, context):
                # Simulate async MCP tool call
                await asyncio.sleep(0.01)
                return True, "MCP check passed"

        checker = ConfidenceChecker(register_defaults=False)
        async_check = AsyncMcpCheck()

        # Should satisfy async protocol
        assert isinstance(async_check, AsyncConfidenceCheck)

        checker.register_check(async_check)
        result = await checker.assess_async({})

        assert result.score == 1.0
        assert result.checks[0].passed is True
        assert result.checks[0].name == "async_mcp"

    @pytest.mark.asyncio
    async def test_assess_async_mixed_checks(self):
        """Test assess_async with mixed sync and async checks"""

        class SyncCheck:
            name = "sync_check"
            weight = 1.0

            def evaluate(self, context):
                return True, "Sync passed"

        class AsyncCheck:
            name = "async_check"
            weight = 1.0

            async def evaluate_async(self, context):
                await asyncio.sleep(0.01)
                return True, "Async passed"

        checker = ConfidenceChecker(register_defaults=False)
        checker.register_check(SyncCheck())
        checker.register_check(AsyncCheck())

        result = await checker.assess_async({})

        assert result.score == 1.0
        assert len(result.checks) == 2
        assert result.checks[0].name == "sync_check"
        assert result.checks[1].name == "async_check"

    def test_has_async_checks_false(self):
        """Test has_async_checks returns False for sync-only"""
        checker = ConfidenceChecker()
        assert checker.has_async_checks() is False

    def test_has_async_checks_true(self):
        """Test has_async_checks returns True when async check registered"""

        class AsyncCheck:
            name = "async_check"
            weight = 1.0

            async def evaluate_async(self, context):
                return True, "Async"

        checker = ConfidenceChecker(register_defaults=False)
        checker.register_check(AsyncCheck())

        assert checker.has_async_checks() is True

    @pytest.mark.asyncio
    async def test_assess_async_empty_registry(self):
        """Test assess_async with no registered checks"""
        checker = ConfidenceChecker(register_defaults=False)
        result = await checker.assess_async({})

        assert result.score == 0.0
        assert result.checks == []
        assert "stop" in result.recommendation.lower()  # Low confidence recommendation

    @pytest.mark.asyncio
    async def test_assess_async_result_comparison(self):
        """Test ConfidenceResult from assess_async supports comparison"""

        class HighConfidenceCheck:
            name = "high_conf"
            weight = 1.0

            async def evaluate_async(self, context):
                return True, "High confidence"

        checker = ConfidenceChecker(register_defaults=False)
        checker.register_check(HighConfidenceCheck())

        result = await checker.assess_async({})

        assert result >= 0.9
        assert result >= 0.7
        assert float(result) == 1.0

    def test_invalid_check_registration_rejected(self):
        """Test that checks without evaluate methods cannot be registered"""

        class InvalidCheck:
            name = "invalid"
            weight = 1.0
            # No evaluate or evaluate_async method

        checker = ConfidenceChecker(register_defaults=False)

        with pytest.raises(TypeError, match="must implement ConfidenceCheck or AsyncConfidenceCheck"):
            checker.register_check(InvalidCheck())


class TestNoDuplicatesCheckActiveVerification:
    """Test NoDuplicatesCheck active verification logic"""

    def test_explicit_flag_true(self):
        """Test that explicit flag=True passes"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()
        context = {"duplicate_check_complete": True}
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "No duplicate" in msg

    def test_explicit_flag_false(self):
        """Test that explicit flag=False fails"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()
        context = {"duplicate_check_complete": False}
        passed, msg = check.evaluate(context)

        assert passed is False
        assert "Check for existing" in msg

    def test_no_task_name_passes(self):
        """Test that empty task_name passes (no duplicates to check)"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()
        context = {"task_name": ""}
        passed, msg = check.evaluate(context)

        assert passed is True

    def test_nonexistent_project_passes(self):
        """Test that nonexistent project root passes"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()
        context = {
            "task_name": "implement feature",
            "project_root": "/nonexistent/path/12345",
        }
        passed, msg = check.evaluate(context)

        assert passed is True

    def test_keywords_extraction(self, tmp_path):
        """Test keyword extraction from task name"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()
        # Create minimal project structure
        (tmp_path / "dummy.py").write_text("# placeholder")

        context = {
            "task_name": "implement the test_feature",  # 'the' should be skipped
            "project_root": str(tmp_path),
        }
        passed, _ = check.evaluate(context)

        # Should pass (no files matching 'implement' or 'feature')
        assert passed is True

    def test_duplicate_detection(self, tmp_path):
        """Test duplicate detection when many matching files exist"""
        from superclaude.pm_agent.confidence import NoDuplicatesCheck

        check = NoDuplicatesCheck()

        # Create many files matching 'config' keyword
        for i in range(10):
            (tmp_path / f"config_{i}.py").write_text(f"# config {i}")

        context = {
            "task_name": "implement config handler",
            "project_root": str(tmp_path),
            "duplicate_threshold": 5,
        }
        passed, msg = check.evaluate(context)

        assert passed is False
        assert "Check for existing" in msg
        assert "potential_duplicates" in context


class TestArchitectureCheckActiveVerification:
    """Test ArchitectureCheck active verification logic"""

    def test_explicit_flag_true(self):
        """Test that explicit flag=True passes"""
        from superclaude.pm_agent.confidence import ArchitectureCheck

        check = ArchitectureCheck()
        context = {"architecture_check_complete": True}
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "existing tech stack" in msg

    def test_explicit_flag_false(self):
        """Test that explicit flag=False fails"""
        from superclaude.pm_agent.confidence import ArchitectureCheck

        check = ArchitectureCheck()
        context = {"architecture_check_complete": False}
        passed, msg = check.evaluate(context)

        assert passed is False

    def test_no_proposed_tech_fails(self):
        """Test that missing proposed_technology fails"""
        from superclaude.pm_agent.confidence import ArchitectureCheck

        check = ArchitectureCheck()
        context = {}
        passed, msg = check.evaluate(context)

        assert passed is False
        assert "Verify architecture" in msg

    def test_tech_stack_detection(self, tmp_path):
        """Test tech stack detection from project files"""
        from superclaude.pm_agent.confidence import ArchitectureCheck, _cached_detect_tech_stack

        # Clear cache
        _cached_detect_tech_stack.cache_clear()

        # Create CLAUDE.md with tech stack
        (tmp_path / "CLAUDE.md").write_text("Using React, Next.js, and pytest")

        check = ArchitectureCheck()
        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["react"],  # Compatible
        }
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "detected_tech_stack" in context

    def test_conflict_detection(self, tmp_path):
        """Test architecture conflict detection"""
        from superclaude.pm_agent.confidence import ArchitectureCheck, _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        # Create project using React
        (tmp_path / "CLAUDE.md").write_text("Using React framework")

        check = ArchitectureCheck()
        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["jquery"],  # Conflicts with react
        }
        passed, msg = check.evaluate(context)

        assert passed is False
        assert "architecture_conflicts" in context

    def test_find_conflicts_method(self):
        """Test _find_conflicts helper method"""
        from superclaude.pm_agent.confidence import ArchitectureCheck

        check = ArchitectureCheck()
        detected = {"frameworks": ["react"], "databases": [], "tools": []}

        conflicts = check._find_conflicts(detected, ["jquery"])
        assert len(conflicts) == 1
        assert "jquery" in conflicts[0].lower()

        # No conflict
        conflicts = check._find_conflicts(detected, ["typescript"])
        assert len(conflicts) == 0


class TestOfficialDocsCheckActiveVerification:
    """Test OfficialDocsCheck active verification logic"""

    def test_explicit_flag_true(self):
        """Test that explicit flag=True passes"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        check = OfficialDocsCheck()
        context = {"official_docs_verified": True}
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "verified" in msg

    def test_explicit_flag_false(self):
        """Test that explicit flag=False fails"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        check = OfficialDocsCheck()
        context = {"official_docs_verified": False}
        passed, msg = check.evaluate(context)

        assert passed is False
        assert "Read official docs" in msg

    def test_no_test_file_fails(self):
        """Test that missing test_file fails"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        check = OfficialDocsCheck()
        context = {}
        passed, msg = check.evaluate(context)

        assert passed is False

    def test_readme_found(self, tmp_path):
        """Test that README.md is found"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        # Create project with README
        (tmp_path / "README.md").write_text("# Project")
        test_file = tmp_path / "tests" / "test_example.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# test")

        check = OfficialDocsCheck()
        context = {"test_file": str(test_file)}
        passed, msg = check.evaluate(context)

        assert passed is True

    def test_claude_md_found(self, tmp_path):
        """Test that CLAUDE.md is found"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        # Create project with CLAUDE.md
        (tmp_path / "CLAUDE.md").write_text("# Claude instructions")
        test_file = tmp_path / "test_example.py"
        test_file.write_text("# test")

        check = OfficialDocsCheck()
        context = {"test_file": str(test_file)}
        passed, msg = check.evaluate(context)

        assert passed is True

    def test_docs_dir_found(self, tmp_path):
        """Test that docs/ directory is found"""
        from superclaude.pm_agent.confidence import OfficialDocsCheck

        # Create project with docs/
        (tmp_path / "docs").mkdir()
        test_file = tmp_path / "test_example.py"
        test_file.write_text("# test")

        check = OfficialDocsCheck()
        context = {"test_file": str(test_file)}
        passed, msg = check.evaluate(context)

        assert passed is True


class TestOssReferenceCheckActiveVerification:
    """Test OssReferenceCheck active verification logic"""

    def test_explicit_flag_true(self):
        """Test that explicit flag=True passes"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()
        context = {"oss_reference_complete": True}
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "OSS implementation found" in msg

    def test_explicit_flag_false(self):
        """Test that explicit flag=False fails"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()
        context = {"oss_reference_complete": False}
        passed, msg = check.evaluate(context)

        assert passed is False

    def test_valid_oss_references(self):
        """Test with valid OSS references"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()
        context = {
            "oss_references": [
                {"url": "https://github.com/example/repo", "source": "pattern"},
            ]
        }
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "validated_oss_references" in context

    def test_validate_references_method(self):
        """Test _validate_references helper"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()

        # Reputable domain
        refs = [{"url": "https://github.com/example/repo"}]
        valid = check._validate_references(refs)
        assert len(valid) == 1

        # String reference
        refs = ["https://stackoverflow.com/questions/12345"]
        valid = check._validate_references(refs)
        assert len(valid) == 1

        # Short URL without reputable domain
        refs = [{"url": "http://x.com/a"}]
        valid = check._validate_references(refs)
        assert len(valid) == 0

    def test_known_pattern_matching(self):
        """Test _match_known_pattern"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()

        # Should match 'auth' pattern
        pattern = check._match_known_pattern("implement authentication")
        assert pattern is not None
        assert "references" in pattern

        # Should match 'api' pattern
        pattern = check._match_known_pattern("build API endpoint")
        assert pattern is not None

        # No match
        pattern = check._match_known_pattern("random task xyz")
        assert pattern == {}

    def test_cached_pattern_search(self, tmp_path):
        """Test _find_cached_pattern"""
        from superclaude.pm_agent.confidence import OssReferenceCheck

        check = OssReferenceCheck()

        # Create pattern cache
        patterns_dir = tmp_path / "docs" / "patterns"
        patterns_dir.mkdir(parents=True)
        (patterns_dir / "authentication.md").write_text("# Auth Pattern")

        result = check._find_cached_pattern(tmp_path, "authentication")
        assert result != ""
        assert "authentication" in result


class TestRootCauseCheckActiveVerification:
    """Test RootCauseCheck active verification logic"""

    def test_explicit_flag_true(self):
        """Test that explicit flag=True passes"""
        from superclaude.pm_agent.confidence import RootCauseCheck

        check = RootCauseCheck()
        context = {"root_cause_identified": True}
        passed, msg = check.evaluate(context)

        assert passed is True
        assert "identified" in msg

    def test_explicit_flag_false(self):
        """Test that explicit flag=False fails"""
        from superclaude.pm_agent.confidence import RootCauseCheck

        check = RootCauseCheck()
        context = {"root_cause_identified": False}
        passed, msg = check.evaluate(context)

        assert passed is False

    def test_specific_root_cause_with_evidence(self):
        """Test specific root cause with evidence passes"""
        from superclaude.pm_agent.confidence import RootCauseCheck

        check = RootCauseCheck()
        context = {
            "root_cause": "The function returns None because the database connection times out after 30 seconds",
            "evidence": ["Connection log shows timeout at 30s"],
        }
        passed, msg = check.evaluate(context)

        assert passed is True

    def test_vague_root_cause_fails(self):
        """Test vague root cause fails"""
        from superclaude.pm_agent.confidence import RootCauseCheck

        check = RootCauseCheck()
        context = {
            "root_cause": "Maybe it is broken",  # Too short, contains 'maybe'
            "evidence": ["some evidence"],
        }
        passed, msg = check.evaluate(context)

        assert passed is False

    def test_no_evidence_fails(self):
        """Test missing evidence fails"""
        from superclaude.pm_agent.confidence import RootCauseCheck

        check = RootCauseCheck()
        context = {
            "root_cause": "The database connection pool is exhausted due to connection leaks",
            "evidence": [],  # Empty evidence
        }
        passed, msg = check.evaluate(context)

        assert passed is False


class TestTechStackDetection:
    """Test _cached_detect_tech_stack function"""

    def test_detect_from_claude_md(self, tmp_path):
        """Test detection from CLAUDE.md"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        content = """
        # Project
        Using Next.js, React, FastAPI, Supabase, and pytest
        """
        (tmp_path / "CLAUDE.md").write_text(content)

        frameworks, databases, tools = _cached_detect_tech_stack(str(tmp_path))

        assert "nextjs" in frameworks
        assert "react" in frameworks
        assert "fastapi" in frameworks
        assert "supabase" in databases
        assert "pytest" in tools

    def test_detect_from_pyproject(self, tmp_path):
        """Test detection from pyproject.toml"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        content = """
        [project]
        dependencies = ["fastapi", "pytest", "sqlalchemy"]
        """
        (tmp_path / "pyproject.toml").write_text(content)

        frameworks, databases, tools = _cached_detect_tech_stack(str(tmp_path))

        assert "fastapi" in frameworks
        assert "sqlalchemy" in databases
        assert "pytest" in tools

    def test_detect_from_package_json(self, tmp_path):
        """Test detection from package.json"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        content = """
        {
            "dependencies": {
                "next": "^13.0.0",
                "react": "^18.0.0",
                "@supabase/supabase-js": "^2.0.0"
            }
        }
        """
        (tmp_path / "package.json").write_text(content)

        frameworks, databases, tools = _cached_detect_tech_stack(str(tmp_path))

        assert "nextjs" in frameworks
        assert "react" in frameworks
        assert "supabase" in databases

    def test_empty_project(self, tmp_path):
        """Test empty project returns empty tuples"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        frameworks, databases, tools = _cached_detect_tech_stack(str(tmp_path))

        assert frameworks == ()
        assert databases == ()
        assert tools == ()

    def test_deduplication(self, tmp_path):
        """Test that duplicate detections are deduplicated"""
        from superclaude.pm_agent.confidence import _cached_detect_tech_stack

        _cached_detect_tech_stack.cache_clear()

        # Both files mention React
        (tmp_path / "CLAUDE.md").write_text("Using React")
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "^18"}}')

        frameworks, _, _ = _cached_detect_tech_stack(str(tmp_path))

        assert frameworks.count("react") == 1  # No duplicates
