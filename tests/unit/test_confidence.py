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

    def test_has_official_docs_with_flag(self):
        """Test official docs check with direct flag"""
        checker = ConfidenceChecker()
        context = {"official_docs_verified": True}

        result = checker._has_official_docs(context)

        assert result is True

    def test_no_duplicates_check(self):
        """Test duplicate check validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"duplicate_check_complete": True}
        assert checker._no_duplicates(context_pass) is True

        # Without flag
        context_fail = {"duplicate_check_complete": False}
        assert checker._no_duplicates(context_fail) is False

    def test_architecture_compliance_check(self):
        """Test architecture compliance validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"architecture_check_complete": True}
        assert checker._architecture_compliant(context_pass) is True

        # Without flag
        context_fail = {}
        assert checker._architecture_compliant(context_fail) is False

    def test_oss_reference_check(self):
        """Test OSS reference validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"oss_reference_complete": True}
        assert checker._has_oss_reference(context_pass) is True

        # Without flag
        context_fail = {"oss_reference_complete": False}
        assert checker._has_oss_reference(context_fail) is False

    def test_root_cause_check(self):
        """Test root cause identification validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"root_cause_identified": True}
        assert checker._root_cause_identified(context_pass) is True

        # Without flag
        context_fail = {}
        assert checker._root_cause_identified(context_fail) is False


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


class TestRootCauseActiveVerification:
    """Test active verification for _root_cause_identified"""

    def test_specific_root_cause_with_evidence_passes(self):
        """Root cause with 5+ words and evidence should pass"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "Null pointer exception in UserService.getUser() due to missing null check",
            "evidence": ["stack trace line 42", "reproduction steps documented"],
        }
        assert checker._root_cause_identified(context) is True

    def test_short_root_cause_fails(self):
        """Root cause with fewer than 5 words should fail"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "Bug in code",
            "evidence": ["some evidence"],
        }
        assert checker._root_cause_identified(context) is False

    def test_vague_root_cause_fails(self):
        """Root cause with vague terms should fail"""
        checker = ConfidenceChecker()
        vague_examples = [
            "Maybe the authentication service is failing somewhere",
            "The error probably comes from the database connection",
            "It might be a race condition in the async handler",
            "Unknown issue causing the timeout in production",
            "Possibly a memory leak in the worker process",
        ]
        for vague_cause in vague_examples:
            context = {
                "root_cause": vague_cause,
                "evidence": ["some evidence"],
            }
            assert checker._root_cause_identified(context) is False, f"Should fail for: {vague_cause}"

    def test_no_evidence_fails(self):
        """Root cause without evidence should fail"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "Database connection timeout due to connection pool exhaustion",
            "evidence": [],
        }
        assert checker._root_cause_identified(context) is False

    def test_flag_overrides_heuristic(self):
        """Explicit flag should override heuristic check"""
        checker = ConfidenceChecker()
        # Flag True overrides bad heuristics
        context = {
            "root_cause_identified": True,
            "root_cause": "Bug",  # Would fail heuristic
            "evidence": [],
        }
        assert checker._root_cause_identified(context) is True

        # Flag False overrides good heuristics
        context = {
            "root_cause_identified": False,
            "root_cause": "Null pointer exception in UserService due to missing check",
            "evidence": ["stack trace"],
        }
        assert checker._root_cause_identified(context) is False


class TestNoDuplicatesActiveVerification:
    """Test active verification for _no_duplicates"""

    def test_no_task_name_passes(self, tmp_path):
        """No task name means nothing to check, should pass"""
        checker = ConfidenceChecker()
        context = {"project_root": str(tmp_path)}
        assert checker._no_duplicates(context) is True

    def test_no_matches_passes(self, tmp_path):
        """No matching files should pass"""
        checker = ConfidenceChecker()
        # Create a file that won't match
        (tmp_path / "unrelated.py").write_text("# nothing here")
        context = {
            "task_name": "implement_unique_feature",
            "project_root": str(tmp_path),
        }
        assert checker._no_duplicates(context) is True

    def test_many_matches_fails(self, tmp_path):
        """Many matching files should fail (potential duplicates)"""
        checker = ConfidenceChecker()
        # Create many files matching "user" keyword
        for i in range(10):
            (tmp_path / f"user_handler_{i}.py").write_text(f"# handler {i}")

        context = {
            "task_name": "implement_user_management",
            "project_root": str(tmp_path),
            "duplicate_threshold": 5,
        }
        assert checker._no_duplicates(context) is False
        assert "potential_duplicates" in context

    def test_threshold_configurable(self, tmp_path):
        """Duplicate threshold should be configurable"""
        checker = ConfidenceChecker()
        # Create 3 matching files
        for i in range(3):
            (tmp_path / f"auth_{i}.py").write_text(f"# auth {i}")

        # Should pass with high threshold
        context = {
            "task_name": "implement_auth_feature",
            "project_root": str(tmp_path),
            "duplicate_threshold": 10,
        }
        assert checker._no_duplicates(context) is True

        # Should fail with low threshold
        context["duplicate_threshold"] = 2
        assert checker._no_duplicates(context) is False

    def test_excludes_test_files(self, tmp_path):
        """Test files should be excluded from duplicate check"""
        checker = ConfidenceChecker()
        # Create test files (should be ignored)
        for i in range(10):
            (tmp_path / f"test_feature_{i}.py").write_text(f"# test {i}")

        context = {
            "task_name": "implement_feature",
            "project_root": str(tmp_path),
            "duplicate_threshold": 5,
        }
        assert checker._no_duplicates(context) is True

    def test_flag_overrides_search(self, tmp_path):
        """Explicit flag should override filesystem search"""
        checker = ConfidenceChecker()
        # Create many duplicates
        for i in range(10):
            (tmp_path / f"handler_{i}.py").write_text(f"# handler {i}")

        context = {
            "duplicate_check_complete": True,  # Override
            "task_name": "implement_handler",
            "project_root": str(tmp_path),
        }
        assert checker._no_duplicates(context) is True


class TestArchitectureCompliantActiveVerification:
    """Test active verification for _architecture_compliant"""

    def test_no_proposed_tech_fails(self):
        """No proposed technology should fail (backward compat)"""
        checker = ConfidenceChecker()
        context = {"project_root": "."}
        assert checker._architecture_compliant(context) is False

    def test_compatible_tech_passes(self, tmp_path):
        """Proposed tech compatible with stack should pass"""
        checker = ConfidenceChecker()
        # Create CLAUDE.md with React
        (tmp_path / "CLAUDE.md").write_text("# Project\nUsing React and Next.js")

        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["react_components", "nextjs_api"],
        }
        assert checker._architecture_compliant(context) is True
        assert "detected_tech_stack" in context

    def test_conflicting_tech_fails(self, tmp_path):
        """Proposed tech conflicting with stack should fail"""
        checker = ConfidenceChecker()
        # Create CLAUDE.md with React
        (tmp_path / "CLAUDE.md").write_text("# Project\nUsing React for frontend")

        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["jquery", "vanilla_dom"],
        }
        assert checker._architecture_compliant(context) is False
        assert "architecture_conflicts" in context
        assert len(context["architecture_conflicts"]) > 0

    def test_supabase_conflict_detection(self, tmp_path):
        """Should detect conflicts with Supabase projects"""
        checker = ConfidenceChecker()
        (tmp_path / "CLAUDE.md").write_text("# Project\nUsing Supabase for backend")

        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["custom_api", "custom_auth"],
        }
        assert checker._architecture_compliant(context) is False
        conflicts = context.get("architecture_conflicts", [])
        assert any("custom_api" in c for c in conflicts)

    def test_detects_from_pyproject(self, tmp_path):
        """Should detect tech stack from pyproject.toml"""
        checker = ConfidenceChecker()
        (tmp_path / "pyproject.toml").write_text(
            '[project]\ndependencies = ["fastapi", "pytest"]'
        )

        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["compatible_middleware"],
        }
        result = checker._architecture_compliant(context)
        assert result is True
        stack = context.get("detected_tech_stack", {})
        assert "fastapi" in stack.get("frameworks", [])

    def test_detects_from_package_json(self, tmp_path):
        """Should detect tech stack from package.json"""
        checker = ConfidenceChecker()
        (tmp_path / "package.json").write_text(
            '{"dependencies": {"next": "14.0.0", "react": "18.0.0"}}'
        )

        context = {
            "project_root": str(tmp_path),
            "proposed_technology": ["server_components"],
        }
        result = checker._architecture_compliant(context)
        assert result is True
        stack = context.get("detected_tech_stack", {})
        assert "nextjs" in stack.get("frameworks", [])

    def test_flag_overrides_detection(self, tmp_path):
        """Explicit flag should override detection"""
        checker = ConfidenceChecker()
        (tmp_path / "CLAUDE.md").write_text("Using React")

        context = {
            "architecture_check_complete": True,
            "project_root": str(tmp_path),
            "proposed_technology": ["jquery"],  # Would conflict
        }
        assert checker._architecture_compliant(context) is True


class TestOssReferenceActiveVerification:
    """Test active verification for _has_oss_reference"""

    def test_valid_github_reference_passes(self):
        """Valid GitHub reference should pass"""
        checker = ConfidenceChecker()
        context = {
            "oss_references": [
                {"url": "https://github.com/tiangolo/fastapi", "source": "Context7"}
            ]
        }
        assert checker._has_oss_reference(context) is True
        assert "validated_oss_references" in context

    def test_multiple_reputable_sources_pass(self):
        """Multiple reputable sources should pass"""
        checker = ConfidenceChecker()
        context = {
            "oss_references": [
                {"url": "https://stackoverflow.com/questions/12345"},
                {"url": "https://docs.python.org/3/library/asyncio.html"},
                {"url": "https://reactjs.org/docs/hooks-intro.html"},
            ]
        }
        assert checker._has_oss_reference(context) is True

    def test_cached_pattern_passes(self, tmp_path):
        """Cached pattern file should pass"""
        checker = ConfidenceChecker()
        patterns_dir = tmp_path / "docs" / "patterns"
        patterns_dir.mkdir(parents=True)
        (patterns_dir / "authentication.md").write_text("# Auth patterns")

        context = {
            "project_root": str(tmp_path),
            "task_type": "authentication",
        }
        assert checker._has_oss_reference(context) is True
        assert "cached_pattern_source" in context

    def test_known_pattern_database_match(self):
        """Known OSS pattern should match from database"""
        checker = ConfidenceChecker()
        test_cases = [
            ("implement_jwt_auth", "jwt"),
            ("add_user_login", "login"),
            ("create_api_endpoint", "api"),
            ("write_unit_tests", "test"),
            ("add_form_validation", "form"),
            ("add_cache_layer", "cache"),  # "cache" must be substring
        ]
        for task_name, expected_keyword in test_cases:
            context = {"task_name": task_name}
            result = checker._has_oss_reference(context)
            assert result is True, f"Should match pattern for: {task_name}"
            assert "matched_oss_pattern" in context
            pattern = context["matched_oss_pattern"]
            assert "references" in pattern

    def test_no_reference_fails(self):
        """No OSS reference should fail"""
        checker = ConfidenceChecker()
        context = {
            "task_name": "implement_xyz_unique_feature",
            "project_root": ".",
        }
        assert checker._has_oss_reference(context) is False

    def test_flag_overrides_verification(self):
        """Explicit flag should override verification"""
        checker = ConfidenceChecker()
        context = {
            "oss_reference_complete": True,
            "task_name": "unique_feature",  # Would fail
        }
        assert checker._has_oss_reference(context) is True

    def test_home_claude_patterns_checked(self, tmp_path, monkeypatch):
        """Should check ~/.claude/patterns for cached patterns"""
        checker = ConfidenceChecker()
        # Mock Path.home() to return tmp_path
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        patterns_dir = tmp_path / ".claude" / "patterns"
        patterns_dir.mkdir(parents=True)
        (patterns_dir / "custom_pattern.md").write_text("# Custom")

        context = {
            "project_root": str(tmp_path / "project"),
            "task_type": "custom_pattern",
        }
        assert checker._has_oss_reference(context) is True


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
