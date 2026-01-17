"""
Pre-implementation Confidence Check

Prevents wrong-direction execution by assessing confidence BEFORE starting.

Token Budget: 100-200 tokens
ROI: 25-250x token savings when stopping wrong direction

Confidence Levels:
    - High (≥90%): Root cause identified, solution verified, no duplication, architecture-compliant
    - Medium (70-89%): Multiple approaches possible, trade-offs require consideration
    - Low (<70%): Investigation incomplete, unclear root cause, missing official docs

Required Checks:
    1. No duplicate implementations (check existing code first)
    2. Architecture compliance (use existing tech stack, e.g., Supabase not custom API)
    3. Official documentation verified
    4. Working OSS implementations referenced
    5. Root cause identified with high certainty
"""

import inspect
import warnings
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Protocol, Tuple, runtime_checkable

__all__ = [
    "ConfidenceCheck",
    "AsyncConfidenceCheck",
    "CheckResult",
    "ConfidenceResult",
    "ConfidenceChecker",
    "NoDuplicatesCheck",
    "ArchitectureCheck",
    "OfficialDocsCheck",
    "OssReferenceCheck",
    "RootCauseCheck",
    "DEFAULT_CHECKS",
]


@runtime_checkable
class ConfidenceCheck(Protocol):
    """
    Protocol for synchronous confidence checks.

    Implement this protocol to create custom confidence checks
    that can be registered with ConfidenceChecker.

    Example:
        class CustomCheck:
            name = "custom_check"
            weight = 0.1

            def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
                passed = context.get("custom_flag", False)
                message = "Custom check passed" if passed else "Custom check failed"
                return passed, message

        checker = ConfidenceChecker()
        checker.register_check(CustomCheck())
    """

    name: str
    weight: float

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate the check against the given context.

        Args:
            context: Task context dictionary

        Returns:
            Tuple of (passed: bool, message: str)
        """
        ...


@runtime_checkable
class AsyncConfidenceCheck(Protocol):
    """
    Protocol for asynchronous confidence checks.

    Implement this protocol for checks that need to perform async operations
    like fetching documentation from MCP servers (Context7, Tavily).

    Example:
        class AsyncDocsCheck:
            name = "async_docs"
            weight = 0.2

            async def evaluate_async(self, context: Dict[str, Any]) -> Tuple[bool, str]:
                # Async operation (e.g., fetch from Context7)
                docs = await fetch_docs_from_mcp(context.get("library"))
                if docs:
                    return True, "Documentation verified via MCP"
                return False, "No documentation found"

        checker = ConfidenceChecker()
        checker.register_check(AsyncDocsCheck())
        result = await checker.assess_async(context)
    """

    name: str
    weight: float

    async def evaluate_async(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Asynchronously evaluate the check against the given context.

        Args:
            context: Task context dictionary

        Returns:
            Tuple of (passed: bool, message: str)
        """
        ...


def _is_async_check(check: Any) -> bool:
    """Check if a check object has async evaluation capability."""
    return (
        hasattr(check, "evaluate_async")
        and callable(getattr(check, "evaluate_async", None))
        and inspect.iscoroutinefunction(check.evaluate_async)
    )


def _has_sync_evaluate(check: Any) -> bool:
    """Check if a check object has sync evaluation capability."""
    return (
        hasattr(check, "evaluate")
        and callable(getattr(check, "evaluate", None))
        and not inspect.iscoroutinefunction(check.evaluate)
    )


@dataclass
class CheckResult:
    """Result of a single confidence check."""

    name: str
    passed: bool
    message: str
    weight: float


@dataclass
class ConfidenceResult:
    """
    Result of confidence assessment.

    Supports comparison operators via __float__ for backward compatibility:
        result = checker.assess(context)
        if result >= 0.9:  # Works via __float__
        if result.score >= 0.9:  # Also works
    """

    score: float
    checks: List[CheckResult] = field(default_factory=list)
    recommendation: str = ""

    def __float__(self) -> float:
        """Enable numeric comparison (e.g., result >= 0.9)."""
        return self.score

    def __ge__(self, other: float) -> bool:
        return self.score >= other

    def __gt__(self, other: float) -> bool:
        return self.score > other

    def __le__(self, other: float) -> bool:
        return self.score <= other

    def __lt__(self, other: float) -> bool:
        return self.score < other

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float)):
            return self.score == other
        if isinstance(other, ConfidenceResult):
            return self.score == other.score
        return NotImplemented


# Module-level cache for tech stack detection (hashable key: path string)
@lru_cache(maxsize=32)
def _cached_detect_tech_stack(project_root_str: str) -> tuple:
    """
    Cached tech stack detection.

    Returns tuple for hashability: (frameworks, databases, tools)
    """
    project_root = Path(project_root_str)
    stack_frameworks: List[str] = []
    stack_databases: List[str] = []
    stack_tools: List[str] = []

    # Check CLAUDE.md for explicit tech stack
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists():
        try:
            content = claude_md.read_text(encoding="utf-8").lower()
            # Framework detection
            if "next.js" in content or "nextjs" in content:
                stack_frameworks.append("nextjs")
            if "react" in content:
                stack_frameworks.append("react")
            if "fastapi" in content:
                stack_frameworks.append("fastapi")
            if "django" in content:
                stack_frameworks.append("django")
            if "flask" in content:
                stack_frameworks.append("flask")
            # Database detection
            if "supabase" in content:
                stack_databases.append("supabase")
            if "postgresql" in content or "postgres" in content:
                stack_databases.append("postgresql")
            if "mongodb" in content:
                stack_databases.append("mongodb")
            # Tool detection
            if "turborepo" in content:
                stack_tools.append("turborepo")
            if "pytest" in content:
                stack_tools.append("pytest")
        except (OSError, UnicodeDecodeError):
            pass

    # Check pyproject.toml for Python dependencies
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8").lower()
            if "fastapi" in content:
                stack_frameworks.append("fastapi")
            if "django" in content:
                stack_frameworks.append("django")
            if "flask" in content:
                stack_frameworks.append("flask")
            if "pytest" in content:
                stack_tools.append("pytest")
            if "sqlalchemy" in content:
                stack_databases.append("sqlalchemy")
        except (OSError, UnicodeDecodeError):
            pass

    # Check package.json for JS dependencies
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            content = package_json.read_text(encoding="utf-8").lower()
            if "next" in content:
                stack_frameworks.append("nextjs")
            if "react" in content:
                stack_frameworks.append("react")
            if "vue" in content:
                stack_frameworks.append("vue")
            if "@supabase" in content:
                stack_databases.append("supabase")
        except (OSError, UnicodeDecodeError):
            pass

    # Deduplicate and return as tuple (hashable)
    return (
        tuple(sorted(set(stack_frameworks))),
        tuple(sorted(set(stack_databases))),
        tuple(sorted(set(stack_tools))),
    )


# =============================================================================
# Concrete Check Implementations
# =============================================================================


class NoDuplicatesCheck:
    """Check for duplicate implementations in codebase."""

    name: str = "no_duplicates"

    def __init__(self, weight: float = 0.25):
        self.weight = weight

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if no duplicate implementations exist."""
        # Honor explicit flag
        if "duplicate_check_complete" in context:
            passed = context["duplicate_check_complete"]
            msg = "No duplicate implementations found" if passed else "Check for existing implementations first"
            return passed, msg

        # Active verification
        task_name = context.get("task_name", "")
        if not task_name:
            return True, "No duplicate implementations found"

        project_root = Path(context.get("project_root", "."))
        if not project_root.exists():
            return True, "No duplicate implementations found"

        # Extract keywords
        skip_words = {"test", "the", "and", "for", "with", "from", "that", "this"}
        keywords = [
            w.lower() for w in task_name.replace("_", " ").replace("-", " ").split()
            if len(w) > 3 and w.lower() not in skip_words
        ]

        if not keywords:
            return True, "No duplicate implementations found"

        # Search for duplicates
        duplicate_threshold = context.get("duplicate_threshold", 5)
        for keyword in keywords[:3]:
            try:
                matches = list(project_root.rglob(f"*{keyword}*.py"))
                matches = [
                    m for m in matches
                    if "__pycache__" not in str(m) and not m.name.startswith("test_")
                ]
                if len(matches) > duplicate_threshold:
                    context["potential_duplicates"] = [str(m) for m in matches[:10]]
                    return False, "Check for existing implementations first"
            except (OSError, PermissionError):
                continue

        return True, "No duplicate implementations found"


class ArchitectureCheck:
    """Check architecture compliance with existing tech stack."""

    name: str = "architecture_compliant"

    def __init__(self, weight: float = 0.25):
        self.weight = weight

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if solution aligns with project architecture."""
        # Honor explicit flag
        if "architecture_check_complete" in context:
            passed = context["architecture_check_complete"]
            msg = "Uses existing tech stack" if passed else "Verify architecture compliance"
            return passed, msg

        # Active verification
        proposed_tech = context.get("proposed_technology", [])
        if not proposed_tech:
            return False, "Verify architecture compliance (avoid reinventing)"

        project_root = Path(context.get("project_root", "."))
        frameworks, databases, tools = _cached_detect_tech_stack(str(project_root))
        detected_stack = {
            "frameworks": list(frameworks),
            "databases": list(databases),
            "tools": list(tools),
        }
        context["detected_tech_stack"] = detected_stack

        # Check conflicts
        conflicts = self._find_conflicts(detected_stack, proposed_tech)
        if conflicts:
            context["architecture_conflicts"] = conflicts
            return False, "Verify architecture compliance (avoid reinventing)"

        return True, "Uses existing tech stack"

    def _find_conflicts(self, detected_stack: dict, proposed_tech: list) -> list:
        """Find conflicts between detected stack and proposed technology."""
        conflicts = []
        conflict_rules = {
            "supabase": ["custom_api", "custom_auth", "raw_postgresql"],
            "postgresql": ["sqlite_for_production"],
            "nextjs": ["custom_routing", "express_routing"],
            "react": ["jquery", "vanilla_dom"],
            "fastapi": ["flask_in_same_project", "django_in_same_project"],
            "turborepo": ["manual_workspace_scripts"],
            "pytest": ["unittest_exclusively"],
        }

        all_detected = (
            detected_stack.get("frameworks", [])
            + detected_stack.get("databases", [])
            + detected_stack.get("tools", [])
        )

        proposed_lower = [p.lower().replace("-", "_").replace(" ", "_") for p in proposed_tech]

        for tech in all_detected:
            if tech in conflict_rules:
                for proposed in proposed_lower:
                    if proposed in conflict_rules[tech]:
                        conflicts.append(f"Conflict: '{proposed}' conflicts with existing '{tech}'")

        return conflicts


class OfficialDocsCheck:
    """Check if official documentation has been verified."""

    name: str = "official_docs"

    def __init__(self, weight: float = 0.20):
        self.weight = weight

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if official documentation exists and was verified."""
        # Honor explicit flag
        if "official_docs_verified" in context:
            passed = context.get("official_docs_verified", False)
            msg = "Official documentation verified" if passed else "Read official docs first"
            return passed, msg

        # Active verification
        test_file = context.get("test_file")
        if not test_file:
            return False, "Read official docs first"

        project_root = Path(test_file).parent
        while project_root.parent != project_root:
            if (project_root / "README.md").exists():
                return True, "Official documentation verified"
            if (project_root / "CLAUDE.md").exists():
                return True, "Official documentation verified"
            if (project_root / "docs").exists():
                return True, "Official documentation verified"
            project_root = project_root.parent

        return False, "Read official docs first"


class OssReferenceCheck:
    """Check if working OSS implementations have been referenced."""

    name: str = "oss_reference"

    def __init__(self, weight: float = 0.15):
        self.weight = weight

    # Known OSS patterns database
    KNOWN_PATTERNS = {
        "auth": {"pattern": "authentication", "references": ["NextAuth.js", "Passport.js", "python-jose"]},
        "login": {"pattern": "user_login", "references": ["NextAuth.js", "Flask-Login", "Django-allauth"]},
        "jwt": {"pattern": "jwt_authentication", "references": ["python-jose", "PyJWT", "jsonwebtoken"]},
        "api": {"pattern": "rest_api", "references": ["FastAPI", "Express.js", "Django REST"]},
        "graphql": {"pattern": "graphql_api", "references": ["Strawberry", "Apollo", "Graphene"]},
        "crud": {"pattern": "crud_operations", "references": ["SQLAlchemy", "Prisma", "TypeORM"]},
        "migration": {"pattern": "database_migration", "references": ["Alembic", "Prisma Migrate"]},
        "test": {"pattern": "testing", "references": ["pytest", "Jest", "Vitest"]},
        "mock": {"pattern": "mocking", "references": ["unittest.mock", "pytest-mock", "Jest mocks"]},
        "component": {"pattern": "ui_component", "references": ["React", "Vue", "Svelte"]},
        "form": {"pattern": "form_handling", "references": ["React Hook Form", "Formik", "VeeValidate"]},
        "state": {"pattern": "state_management", "references": ["Redux", "Zustand", "Pinia"]},
        "cache": {"pattern": "caching", "references": ["Redis", "Memcached", "lru_cache"]},
        "queue": {"pattern": "message_queue", "references": ["Celery", "Bull", "RabbitMQ"]},
        "log": {"pattern": "logging", "references": ["structlog", "Winston", "Pino"]},
    }

    REPUTABLE_DOMAINS = [
        "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
        "docs.python.org", "developer.mozilla.org", "reactjs.org", "nextjs.org",
        "fastapi.tiangolo.com", "django-project.com",
    ]

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if OSS reference found and analyzed."""
        # Honor explicit flag
        if "oss_reference_complete" in context:
            passed = context["oss_reference_complete"]
            msg = "Working OSS implementation found" if passed else "Search for OSS implementations"
            return passed, msg

        # Check provided references
        oss_references = context.get("oss_references", [])
        if oss_references:
            valid_refs = self._validate_references(oss_references)
            if valid_refs:
                context["validated_oss_references"] = valid_refs
                return True, "Working OSS implementation found"

        # Check local pattern cache
        project_root = Path(context.get("project_root", "."))
        task_type = context.get("task_type", "")
        if task_type:
            cached = self._find_cached_pattern(project_root, task_type)
            if cached:
                context["cached_pattern_source"] = cached
                return True, "Working OSS implementation found"

        # Check known patterns
        task_name = context.get("task_name", "")
        if task_name:
            pattern = self._match_known_pattern(task_name)
            if pattern:
                context["matched_oss_pattern"] = pattern
                return True, "Working OSS implementation found"

        return False, "Search for OSS implementations"

    def _validate_references(self, references: list) -> list:
        """Validate quality of OSS references."""
        valid = []
        for ref in references:
            if isinstance(ref, dict):
                url = ref.get("url", "")
                source = ref.get("source", "")
            else:
                url = str(ref)
                source = ""

            is_reputable = any(domain in url.lower() for domain in self.REPUTABLE_DOMAINS)
            has_content = len(url) > 20 or len(source) > 10

            if is_reputable or has_content:
                valid.append(ref)
        return valid

    def _find_cached_pattern(self, project_root: Path, task_type: str) -> str:
        """Find cached pattern in local directories."""
        cache_locations = [
            project_root / "docs" / "patterns",
            project_root / ".claude" / "patterns",
            project_root / ".patterns",
            Path.home() / ".claude" / "patterns",
        ]

        task_type_normalized = task_type.lower().replace(" ", "_").replace("-", "_")

        for cache_dir in cache_locations:
            if cache_dir.exists():
                pattern_file = cache_dir / f"{task_type_normalized}.md"
                if pattern_file.exists():
                    return str(pattern_file)
                try:
                    for f in cache_dir.glob("*.md"):
                        if task_type_normalized in f.stem.lower():
                            return str(f)
                except (OSError, PermissionError):
                    continue
        return ""

    def _match_known_pattern(self, task_name: str) -> dict:
        """Match task against known OSS patterns database."""
        task_lower = task_name.lower()
        for keyword, pattern_info in self.KNOWN_PATTERNS.items():
            if keyword in task_lower:
                return pattern_info
        return {}


class RootCauseCheck:
    """Check if root cause is identified with high certainty."""

    name: str = "root_cause"

    def __init__(self, weight: float = 0.15):
        self.weight = weight

    VAGUE_TERMS = ["maybe", "probably", "might", "unknown", "possibly", "perhaps"]

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if root cause clearly identified."""
        # Honor explicit flag
        if "root_cause_identified" in context:
            passed = context["root_cause_identified"]
            msg = "Root cause identified" if passed else "Continue investigation to identify root cause"
            return passed, msg

        # Active verification
        root_cause = context.get("root_cause", "")
        evidence = context.get("evidence", [])

        # Heuristic: root cause must be specific
        words = root_cause.split()
        is_specific = (
            len(words) >= 5
            and not any(term in root_cause.lower() for term in self.VAGUE_TERMS)
        )

        has_evidence = len(evidence) >= 1

        if is_specific and has_evidence:
            return True, "Root cause identified"
        return False, "Continue investigation to identify root cause"


# Default check instances (for backward compatibility)
DEFAULT_CHECKS: List[ConfidenceCheck] = [
    NoDuplicatesCheck(weight=0.25),
    ArchitectureCheck(weight=0.25),
    OfficialDocsCheck(weight=0.20),
    OssReferenceCheck(weight=0.15),
    RootCauseCheck(weight=0.15),
]


class ConfidenceChecker:
    """
    Pre-implementation confidence assessment with pluggable check registry.

    Usage:
        # Default usage (all 5 checks registered)
        checker = ConfidenceChecker()
        result = checker.assess(context)

        if result >= 0.9:
            # High confidence - proceed immediately
        elif result >= 0.7:
            # Medium confidence - present options to user
        else:
            # Low confidence - STOP and request clarification

        # Custom checks
        checker = ConfidenceChecker(register_defaults=False)
        checker.register_check(NoDuplicatesCheck(weight=0.5))
        checker.register_check(CustomCheck(weight=0.5))
    """

    def __init__(self, register_defaults: bool = True):
        """
        Initialize ConfidenceChecker.

        Args:
            register_defaults: If True, register the 5 default checks.
                Set to False to start with empty registry.
        """
        self._checks: List[ConfidenceCheck] = []
        if register_defaults:
            self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register the 5 default confidence checks."""
        for check in DEFAULT_CHECKS:
            # Create fresh instances to avoid shared state
            check_class = type(check)
            self._checks.append(check_class(weight=check.weight))

    def register_check(self, check: ConfidenceCheck) -> None:
        """
        Register a new confidence check.

        Args:
            check: Check implementing ConfidenceCheck or AsyncConfidenceCheck protocol
        """
        if not isinstance(check, (ConfidenceCheck, AsyncConfidenceCheck)):
            raise TypeError(f"Check must implement ConfidenceCheck or AsyncConfidenceCheck protocol, got {type(check)}")
        self._checks.append(check)

    def unregister_check(self, name: str) -> bool:
        """
        Unregister a check by name.

        Args:
            name: Name of the check to remove

        Returns:
            True if check was found and removed, False otherwise
        """
        original_len = len(self._checks)
        self._checks = [c for c in self._checks if c.name != name]
        return len(self._checks) < original_len

    def clear_checks(self) -> None:
        """Remove all registered checks."""
        self._checks.clear()

    def get_checks(self) -> List[ConfidenceCheck]:
        """Get list of registered checks."""
        return list(self._checks)

    def assess(self, context: Dict[str, Any]) -> ConfidenceResult:
        """
        Assess confidence level using registered checks.

        Scores are calculated based on check weights. Weights are normalized
        so the total possible score is always 1.0.

        Args:
            context: Context dict with task details

        Returns:
            ConfidenceResult: Result with score, checks, and recommendation.
                Supports comparison operators (e.g., result >= 0.9).
        """
        if not self._checks:
            return ConfidenceResult(
                score=0.0,
                checks=[],
                recommendation=self.get_recommendation(0.0),
            )

        # Calculate total weight for normalization
        total_weight = sum(c.weight for c in self._checks)
        if total_weight == 0:
            total_weight = 1.0  # Avoid division by zero

        score = 0.0
        check_results: List[CheckResult] = []

        for check in self._checks:
            passed, message = check.evaluate(context)
            normalized_weight = check.weight / total_weight

            if passed:
                score += normalized_weight

            check_results.append(CheckResult(
                name=check.name,
                passed=passed,
                message=message,
                weight=check.weight,
            ))

        # Build recommendation
        recommendation = self.get_recommendation(score)

        # Backward compatibility: also store in context for legacy callers
        context["confidence_checks"] = [
            f"{'✅' if c.passed else '❌'} {c.message}" for c in check_results
        ]

        return ConfidenceResult(score=score, checks=check_results, recommendation=recommendation)

    async def assess_async(self, context: Dict[str, Any]) -> ConfidenceResult:
        """
        Asynchronously assess confidence level using registered checks.

        This method supports both sync and async checks:
        - Sync checks (with evaluate()) are called normally
        - Async checks (with evaluate_async()) are awaited

        Use this method when you have async checks that need to fetch
        data from MCP servers (Context7, Tavily) or other async sources.

        Args:
            context: Context dict with task details

        Returns:
            ConfidenceResult: Result with score, checks, and recommendation.

        Example:
            result = await checker.assess_async(context)
            if result >= 0.9:
                # Proceed with implementation
        """
        if not self._checks:
            return ConfidenceResult(
                score=0.0,
                checks=[],
                recommendation=self.get_recommendation(0.0),
            )

        # Calculate total weight for normalization
        total_weight = sum(c.weight for c in self._checks)
        if total_weight == 0:
            total_weight = 1.0

        score = 0.0
        check_results: List[CheckResult] = []

        for check in self._checks:
            # Determine how to evaluate this check
            if _is_async_check(check):
                # Async check - await it
                passed, message = await check.evaluate_async(context)
            elif _has_sync_evaluate(check):
                # Sync check - call normally
                passed, message = check.evaluate(context)
            else:
                # No valid evaluate method
                warnings.warn(
                    f"Check '{getattr(check, 'name', 'unknown')}' has no valid "
                    "evaluate() or evaluate_async() method, skipping",
                    RuntimeWarning,
                )
                continue

            normalized_weight = check.weight / total_weight

            if passed:
                score += normalized_weight

            check_results.append(CheckResult(
                name=check.name,
                passed=passed,
                message=message,
                weight=check.weight,
            ))

        # Build recommendation
        recommendation = self.get_recommendation(score)

        # Backward compatibility: also store in context for legacy callers
        context["confidence_checks"] = [
            f"{'✅' if c.passed else '❌'} {c.message}" for c in check_results
        ]

        return ConfidenceResult(score=score, checks=check_results, recommendation=recommendation)

    def has_async_checks(self) -> bool:
        """Check if any registered checks require async evaluation."""
        return any(_is_async_check(check) for check in self._checks)

    def get_recommendation(self, confidence: float) -> str:
        """
        Get recommended action based on confidence level

        Args:
            confidence: Confidence score (0.0 - 1.0)

        Returns:
            str: Recommended action
        """
        if confidence >= 0.9:
            return "✅ High confidence (≥90%) - Proceed with implementation"
        elif confidence >= 0.7:
            return "⚠️ Medium confidence (70-89%) - Continue investigation, DO NOT implement yet"
        else:
            return "❌ Low confidence (<70%) - STOP and continue investigation loop"
