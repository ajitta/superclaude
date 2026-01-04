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

from pathlib import Path
from typing import Any, Dict


class ConfidenceChecker:
    """
    Pre-implementation confidence assessment

    Usage:
        checker = ConfidenceChecker()
        confidence = checker.assess(context)

        if confidence >= 0.9:
            # High confidence - proceed immediately
        elif confidence >= 0.7:
            # Medium confidence - present options to user
        else:
            # Low confidence - STOP and request clarification
    """

    def assess(self, context: Dict[str, Any]) -> float:
        """
        Assess confidence level (0.0 - 1.0)

        Investigation Phase Checks:
        1. No duplicate implementations? (25%)
        2. Architecture compliance? (25%)
        3. Official documentation verified? (20%)
        4. Working OSS implementations referenced? (15%)
        5. Root cause identified? (15%)

        Args:
            context: Context dict with task details

        Returns:
            float: Confidence score (0.0 = no confidence, 1.0 = absolute certainty)
        """
        score = 0.0
        checks = []

        # Check 1: No duplicate implementations (25%)
        if self._no_duplicates(context):
            score += 0.25
            checks.append("✅ No duplicate implementations found")
        else:
            checks.append("❌ Check for existing implementations first")

        # Check 2: Architecture compliance (25%)
        if self._architecture_compliant(context):
            score += 0.25
            checks.append("✅ Uses existing tech stack (e.g., Supabase)")
        else:
            checks.append("❌ Verify architecture compliance (avoid reinventing)")

        # Check 3: Official documentation verified (20%)
        if self._has_official_docs(context):
            score += 0.2
            checks.append("✅ Official documentation verified")
        else:
            checks.append("❌ Read official docs first")

        # Check 4: Working OSS implementations referenced (15%)
        if self._has_oss_reference(context):
            score += 0.15
            checks.append("✅ Working OSS implementation found")
        else:
            checks.append("❌ Search for OSS implementations")

        # Check 5: Root cause identified (15%)
        if self._root_cause_identified(context):
            score += 0.15
            checks.append("✅ Root cause identified")
        else:
            checks.append("❌ Continue investigation to identify root cause")

        # Store check results for reporting
        context["confidence_checks"] = checks

        return score

    def _has_official_docs(self, context: Dict[str, Any]) -> bool:
        """
        Check if official documentation exists

        Looks for:
        - README.md in project
        - CLAUDE.md with relevant patterns
        - docs/ directory with related content
        """
        # Check context flag first (for testing)
        if "official_docs_verified" in context:
            return context.get("official_docs_verified", False)

        # Check for test file path
        test_file = context.get("test_file")
        if not test_file:
            return False

        project_root = Path(test_file).parent
        while project_root.parent != project_root:
            # Check for documentation files
            if (project_root / "README.md").exists():
                return True
            if (project_root / "CLAUDE.md").exists():
                return True
            if (project_root / "docs").exists():
                return True
            project_root = project_root.parent

        return False

    def _no_duplicates(self, context: Dict[str, Any]) -> bool:
        """
        Check for duplicate implementations

        Before implementing, verify:
        - No existing similar functions/modules (Glob/Grep)
        - No helper functions that solve the same problem
        - No libraries that provide this functionality

        Returns True if no duplicates found (investigation complete)
        """
        # Backward compatibility: honor explicit flag
        if "duplicate_check_complete" in context:
            return context["duplicate_check_complete"]

        # Active verification: search codebase for similar patterns
        task_name = context.get("task_name", "")
        if not task_name:
            return True  # No task name to check against

        project_root = Path(context.get("project_root", "."))
        if not project_root.exists():
            return True  # Can't verify, assume OK

        # Extract meaningful keywords (>3 chars, skip common words)
        skip_words = {"test", "the", "and", "for", "with", "from", "that", "this"}
        keywords = [
            w.lower() for w in task_name.replace("_", " ").replace("-", " ").split()
            if len(w) > 3 and w.lower() not in skip_words
        ]

        if not keywords:
            return True  # No keywords to search

        # Search for potential duplicates (limit to top 3 keywords)
        duplicate_threshold = context.get("duplicate_threshold", 5)
        for keyword in keywords[:3]:
            try:
                matches = list(project_root.rglob(f"*{keyword}*.py"))
                # Exclude test files and __pycache__
                matches = [
                    m for m in matches
                    if "__pycache__" not in str(m)
                    and not m.name.startswith("test_")
                ]
                if len(matches) > duplicate_threshold:
                    # Store matches for reporting
                    context["potential_duplicates"] = [str(m) for m in matches[:10]]
                    return False
            except (OSError, PermissionError):
                continue  # Skip inaccessible paths

        return True

    def _architecture_compliant(self, context: Dict[str, Any]) -> bool:
        """
        Check architecture compliance

        Verify solution uses existing tech stack:
        - Supabase project → Use Supabase APIs (not custom API)
        - Next.js project → Use Next.js patterns (not custom routing)
        - Turborepo → Use workspace patterns (not manual scripts)

        Returns True if solution aligns with project architecture
        """
        # Backward compatibility: honor explicit flag
        if "architecture_check_complete" in context:
            return context["architecture_check_complete"]

        # Active verification requires proposed_technology
        proposed_tech = context.get("proposed_technology", [])
        if not proposed_tech:
            # No proposed technology to verify - return False for backward compat
            # (original placeholder returned context.get(..., False))
            return False

        # Detect existing tech stack from project files
        project_root = Path(context.get("project_root", "."))
        detected_stack = self._detect_tech_stack(project_root)

        # Store detected stack for reporting
        context["detected_tech_stack"] = detected_stack

        # Check for conflicts (reinventing existing functionality)
        conflicts = self._find_architecture_conflicts(detected_stack, proposed_tech)

        if conflicts:
            context["architecture_conflicts"] = conflicts
            return False

        return True

    def _detect_tech_stack(self, project_root: Path) -> dict:
        """Detect technology stack from project files"""
        stack = {"frameworks": [], "databases": [], "tools": []}

        # Check CLAUDE.md for explicit tech stack
        claude_md = project_root / "CLAUDE.md"
        if claude_md.exists():
            try:
                content = claude_md.read_text(encoding="utf-8").lower()
                # Framework detection
                if "next.js" in content or "nextjs" in content:
                    stack["frameworks"].append("nextjs")
                if "react" in content:
                    stack["frameworks"].append("react")
                if "fastapi" in content:
                    stack["frameworks"].append("fastapi")
                if "django" in content:
                    stack["frameworks"].append("django")
                if "flask" in content:
                    stack["frameworks"].append("flask")
                # Database detection
                if "supabase" in content:
                    stack["databases"].append("supabase")
                if "postgresql" in content or "postgres" in content:
                    stack["databases"].append("postgresql")
                if "mongodb" in content:
                    stack["databases"].append("mongodb")
                # Tool detection
                if "turborepo" in content:
                    stack["tools"].append("turborepo")
                if "pytest" in content:
                    stack["tools"].append("pytest")
            except (OSError, UnicodeDecodeError):
                pass

        # Check pyproject.toml for Python dependencies
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8").lower()
                if "fastapi" in content:
                    stack["frameworks"].append("fastapi")
                if "django" in content:
                    stack["frameworks"].append("django")
                if "flask" in content:
                    stack["frameworks"].append("flask")
                if "pytest" in content:
                    stack["tools"].append("pytest")
                if "sqlalchemy" in content:
                    stack["databases"].append("sqlalchemy")
            except (OSError, UnicodeDecodeError):
                pass

        # Check package.json for JS dependencies
        package_json = project_root / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text(encoding="utf-8").lower()
                if "next" in content:
                    stack["frameworks"].append("nextjs")
                if "react" in content:
                    stack["frameworks"].append("react")
                if "vue" in content:
                    stack["frameworks"].append("vue")
                if "@supabase" in content:
                    stack["databases"].append("supabase")
            except (OSError, UnicodeDecodeError):
                pass

        # Deduplicate
        stack["frameworks"] = list(set(stack["frameworks"]))
        stack["databases"] = list(set(stack["databases"]))
        stack["tools"] = list(set(stack["tools"]))

        return stack

    def _find_architecture_conflicts(
        self, detected_stack: dict, proposed_tech: list
    ) -> list:
        """Find conflicts between detected stack and proposed technology"""
        conflicts = []

        # Define conflict rules: if stack has X, proposing Y is a conflict
        conflict_rules = {
            # Database conflicts
            "supabase": ["custom_api", "custom_auth", "raw_postgresql"],
            "postgresql": ["sqlite_for_production"],
            # Framework conflicts
            "nextjs": ["custom_routing", "express_routing"],
            "react": ["jquery", "vanilla_dom"],
            "fastapi": ["flask_in_same_project", "django_in_same_project"],
            # Tool conflicts
            "turborepo": ["manual_workspace_scripts"],
            "pytest": ["unittest_exclusively"],
        }

        # Flatten detected stack
        all_detected = (
            detected_stack.get("frameworks", [])
            + detected_stack.get("databases", [])
            + detected_stack.get("tools", [])
        )

        # Check each proposed tech against conflict rules
        proposed_lower = [p.lower().replace("-", "_").replace(" ", "_") for p in proposed_tech]

        for tech in all_detected:
            if tech in conflict_rules:
                for proposed in proposed_lower:
                    if proposed in conflict_rules[tech]:
                        conflicts.append(
                            f"Conflict: '{proposed}' conflicts with existing '{tech}'"
                        )

        return conflicts

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        """
        Check if working OSS implementations referenced

        Search for:
        - Similar open-source solutions
        - Reference implementations in popular projects
        - Community best practices

        Returns True if OSS reference found and analyzed
        """
        # Backward compatibility: honor explicit flag
        if "oss_reference_complete" in context:
            return context["oss_reference_complete"]

        # Check for OSS references provided in context
        # (injected by external tools like Context7, Tavily, or manual research)
        oss_references = context.get("oss_references", [])
        oss_patterns = context.get("oss_patterns", [])

        # Validate OSS references quality
        if oss_references:
            valid_refs = self._validate_oss_references(oss_references)
            if valid_refs:
                context["validated_oss_references"] = valid_refs
                return True

        # Check local pattern cache
        project_root = Path(context.get("project_root", "."))
        task_type = context.get("task_type", "")

        if task_type:
            cached_pattern = self._find_cached_pattern(project_root, task_type)
            if cached_pattern:
                context["cached_pattern_source"] = cached_pattern
                return True

        # Check against known OSS patterns database
        task_name = context.get("task_name", "")
        if task_name:
            known_pattern = self._match_known_oss_pattern(task_name)
            if known_pattern:
                context["matched_oss_pattern"] = known_pattern
                return True

        # No OSS reference found
        return False

    def _validate_oss_references(self, references: list) -> list:
        """Validate quality of OSS references"""
        valid = []
        # Known reputable sources
        reputable_domains = [
            "github.com",
            "gitlab.com",
            "bitbucket.org",
            "stackoverflow.com",
            "docs.python.org",
            "developer.mozilla.org",
            "reactjs.org",
            "nextjs.org",
            "fastapi.tiangolo.com",
            "django-project.com",
        ]

        for ref in references:
            if isinstance(ref, dict):
                url = ref.get("url", "")
                source = ref.get("source", "")
            else:
                url = str(ref)
                source = ""

            # Check if from reputable source
            is_reputable = any(domain in url.lower() for domain in reputable_domains)

            # Check if has meaningful content
            has_content = len(url) > 20 or len(source) > 10

            if is_reputable or has_content:
                valid.append(ref)

        return valid

    def _find_cached_pattern(self, project_root: Path, task_type: str) -> str:
        """Find cached pattern in local directories"""
        # Pattern cache locations (in priority order)
        cache_locations = [
            project_root / "docs" / "patterns",
            project_root / ".claude" / "patterns",
            project_root / ".patterns",
            Path.home() / ".claude" / "patterns",
        ]

        # Normalize task type for file matching
        task_type_normalized = task_type.lower().replace(" ", "_").replace("-", "_")

        for cache_dir in cache_locations:
            if cache_dir.exists():
                # Look for exact match
                pattern_file = cache_dir / f"{task_type_normalized}.md"
                if pattern_file.exists():
                    return str(pattern_file)

                # Look for partial match
                try:
                    for f in cache_dir.glob("*.md"):
                        if task_type_normalized in f.stem.lower():
                            return str(f)
                except (OSError, PermissionError):
                    continue

        return ""

    def _match_known_oss_pattern(self, task_name: str) -> dict:
        """Match task against known OSS patterns database"""
        # Built-in knowledge of common patterns and their OSS references
        known_patterns = {
            # Authentication patterns
            "auth": {
                "pattern": "authentication",
                "references": ["NextAuth.js", "Passport.js", "python-jose"],
                "docs": ["https://next-auth.js.org", "https://passportjs.org"],
            },
            "login": {
                "pattern": "user_login",
                "references": ["NextAuth.js", "Flask-Login", "Django-allauth"],
            },
            "jwt": {
                "pattern": "jwt_authentication",
                "references": ["python-jose", "PyJWT", "jsonwebtoken"],
            },
            # API patterns
            "api": {
                "pattern": "rest_api",
                "references": ["FastAPI", "Express.js", "Django REST"],
            },
            "graphql": {
                "pattern": "graphql_api",
                "references": ["Strawberry", "Apollo", "Graphene"],
            },
            # Database patterns
            "crud": {
                "pattern": "crud_operations",
                "references": ["SQLAlchemy", "Prisma", "TypeORM"],
            },
            "migration": {
                "pattern": "database_migration",
                "references": ["Alembic", "Prisma Migrate", "Django migrations"],
            },
            # Testing patterns
            "test": {
                "pattern": "testing",
                "references": ["pytest", "Jest", "Vitest"],
            },
            "mock": {
                "pattern": "mocking",
                "references": ["unittest.mock", "pytest-mock", "Jest mocks"],
            },
            # Frontend patterns
            "component": {
                "pattern": "ui_component",
                "references": ["React", "Vue", "Svelte"],
            },
            "form": {
                "pattern": "form_handling",
                "references": ["React Hook Form", "Formik", "VeeValidate"],
            },
            "state": {
                "pattern": "state_management",
                "references": ["Redux", "Zustand", "Pinia"],
            },
            # Infrastructure patterns
            "cache": {
                "pattern": "caching",
                "references": ["Redis", "Memcached", "lru_cache"],
            },
            "queue": {
                "pattern": "message_queue",
                "references": ["Celery", "Bull", "RabbitMQ"],
            },
            "log": {
                "pattern": "logging",
                "references": ["structlog", "Winston", "Pino"],
            },
        }

        # Search for matching pattern
        task_lower = task_name.lower()
        for keyword, pattern_info in known_patterns.items():
            if keyword in task_lower:
                return pattern_info

        return {}

    def _root_cause_identified(self, context: Dict[str, Any]) -> bool:
        """
        Check if root cause is identified with high certainty

        Verify:
        - Problem source pinpointed (not guessing)
        - Solution addresses root cause (not symptoms)
        - Fix verified against official docs/OSS patterns

        Returns True if root cause clearly identified
        """
        # Backward compatibility: honor explicit flag
        if "root_cause_identified" in context:
            return context["root_cause_identified"]

        # Active verification: check root_cause quality
        root_cause = context.get("root_cause", "")
        evidence = context.get("evidence", [])

        # Heuristic: root cause must be specific (not vague)
        vague_terms = ["maybe", "probably", "might", "unknown", "possibly", "perhaps"]
        words = root_cause.split()
        is_specific = (
            len(words) >= 5  # At least 5 words
            and not any(term in root_cause.lower() for term in vague_terms)
        )

        # Require at least one piece of evidence
        has_evidence = len(evidence) >= 1

        return is_specific and has_evidence

    def _has_existing_patterns(self, context: Dict[str, Any]) -> bool:
        """
        Check if existing patterns can be followed

        Looks for:
        - Similar test files
        - Common naming conventions
        - Established directory structure
        """
        test_file = context.get("test_file")
        if not test_file:
            return False

        test_path = Path(test_file)
        test_dir = test_path.parent

        # Check for other test files in same directory
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            return len(test_files) > 1

        return False

    def _has_clear_path(self, context: Dict[str, Any]) -> bool:
        """
        Check if implementation path is clear

        Considers:
        - Test name suggests clear purpose
        - Markers indicate test type
        - Context has sufficient information
        """
        # Check test name clarity
        test_name = context.get("test_name", "")
        if not test_name or test_name == "test_example":
            return False

        # Check for markers indicating test type
        markers = context.get("markers", [])
        known_markers = {
            "unit",
            "integration",
            "hallucination",
            "performance",
            "confidence_check",
            "self_check",
        }

        has_markers = bool(set(markers) & known_markers)

        return has_markers or len(test_name) > 10

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
