"""
Post-implementation Self-Check Protocol

Hallucination prevention through evidence-based validation.

Token Budget: 200-2,500 tokens (complexity-dependent)
Detection Rate: 94% (Reflexion benchmark)

The Four Questions:
1. Are all tests passing?
2. Are all requirements met?
3. No assumptions without verification?
4. Is there evidence?

Claude Code 2.1.20 Integration:
- Task auto-cleanup via TaskUpdate delete feature
- Stale task detection and automatic removal
"""

from typing import Any, Dict, List, Tuple


class TaskCleanupManager:
    """
    Automatic task cleanup manager.

    Integrates with Claude Code 2.1.20's TaskUpdate delete feature
    to automatically remove completed, cancelled, or stale tasks.

    Usage:
        manager = TaskCleanupManager()
        cleaned = manager.cleanup_tasks(tasks)
        print(f"Cleaned {len(cleaned)} stale tasks")
    """

    # Task states that should be auto-cleaned
    CLEANABLE_STATES = ["completed", "cancelled", "stale", "blocked"]

    # Maximum age (in hours) before a pending task becomes stale
    STALE_THRESHOLD_HOURS = 24

    def __init__(self, auto_delete: bool = True):
        """
        Initialize TaskCleanupManager.

        Args:
            auto_delete: If True, automatically delete stale tasks.
                        If False, only identify them for review.
        """
        self.auto_delete = auto_delete

    def identify_stale_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify tasks that should be cleaned up.

        Args:
            tasks: List of task dictionaries with 'id', 'status', 'created_at' etc.

        Returns:
            List of stale tasks that should be removed
        """
        import time

        stale_tasks = []
        current_time = time.time()

        for task in tasks:
            status = task.get("status", "").lower()

            # Immediately cleanable states
            if status in self.CLEANABLE_STATES:
                stale_tasks.append(task)
                continue

            # Check for age-based staleness
            created_at = task.get("created_at", 0)
            if created_at:
                age_hours = (current_time - created_at) / 3600
                if age_hours > self.STALE_THRESHOLD_HOURS and status == "pending":
                    task["stale_reason"] = f"Pending for {age_hours:.1f} hours"
                    stale_tasks.append(task)

        return stale_tasks

    def cleanup_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Clean up stale tasks.

        Args:
            tasks: List of task dictionaries

        Returns:
            Tuple of (deleted_task_ids, remaining_tasks)
        """
        stale = self.identify_stale_tasks(tasks)
        stale_ids = {t.get("id") for t in stale if t.get("id")}

        deleted_ids = []
        remaining = []

        for task in tasks:
            task_id = task.get("id")
            if task_id in stale_ids:
                if self.auto_delete:
                    if task_id is not None:
                        deleted_ids.append(str(task_id))
                else:
                    # Mark for review but keep
                    task["marked_for_cleanup"] = True
                    remaining.append(task)
            else:
                remaining.append(task)

        return deleted_ids, remaining

    def generate_cleanup_report(
        self, deleted_ids: List[str], stale_tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a cleanup report.

        Args:
            deleted_ids: List of deleted task IDs
            stale_tasks: List of stale task dictionaries

        Returns:
            Formatted cleanup report string
        """
        if not deleted_ids and not stale_tasks:
            return "No stale tasks found."

        lines = ["Task Cleanup Report", "=" * 40]

        if deleted_ids:
            lines.append(f"\nAuto-deleted {len(deleted_ids)} tasks:")
            for task_id in deleted_ids:
                lines.append(f"  - {task_id}")

        if stale_tasks:
            lines.append(f"\nStale tasks identified: {len(stale_tasks)}")
            for task in stale_tasks:
                reason = task.get("stale_reason", task.get("status", "unknown"))
                lines.append(f"  - {task.get('id', 'unknown')}: {reason}")

        return "\n".join(lines)


class SelfCheckProtocol:
    """
    Post-implementation validation

    Mandatory Questions (The Four Questions):
        1. Are all tests passing?
           → Run tests → Show ACTUAL results
           → IF any fail: NOT complete

        2. Are all requirements met?
           → Compare implementation vs requirements
           → List: ✅ Done, ❌ Missing

        3. No assumptions without verification?
           → Review: Assumptions verified?
           → Check: Official docs consulted?

        4. Is there evidence?
           → Test results (actual output)
           → Code changes (file list)
           → Validation (lint, typecheck)

    Usage:
        protocol = SelfCheckProtocol()
        passed, issues = protocol.validate(implementation)

        if passed:
            print("✅ Implementation complete with evidence")
        else:
            print("❌ Issues detected:")
            for issue in issues:
                print(f"  - {issue}")
    """

    # 7 Red Flags for Hallucination Detection
    HALLUCINATION_RED_FLAGS = [
        "tests pass",  # without showing output
        "everything works",  # without evidence
        "implementation complete",  # with failing tests
        # Skipping error messages
        # Ignoring warnings
        # Hiding failures
        # "probably works" statements
    ]

    def validate(self, implementation: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Run self-check validation

        Args:
            implementation: Implementation details dict containing:
                - tests_passed (bool): Whether tests passed
                - test_output (str): Actual test output
                - requirements (List[str]): List of requirements
                - requirements_met (List[str]): List of met requirements
                - assumptions (List[str]): List of assumptions made
                - assumptions_verified (List[str]): List of verified assumptions
                - evidence (Dict): Evidence dict with test_results, code_changes, validation

        Returns:
            Tuple of (passed: bool, issues: List[str])
        """
        issues = []

        # Question 1: Tests passing?
        if not self._check_tests_passing(implementation):
            issues.append("❌ Tests not passing - implementation incomplete")

        # Question 2: Requirements met?
        unmet = self._check_requirements_met(implementation)
        if unmet:
            issues.append(f"❌ Requirements not fully met: {', '.join(unmet)}")

        # Question 3: Assumptions verified?
        unverified = self._check_assumptions_verified(implementation)
        if unverified:
            issues.append(f"❌ Unverified assumptions: {', '.join(unverified)}")

        # Question 4: Evidence provided?
        missing_evidence = self._check_evidence_exists(implementation)
        if missing_evidence:
            issues.append(f"❌ Missing evidence: {', '.join(missing_evidence)}")

        # Additional: Check for hallucination red flags
        hallucinations = self._detect_hallucinations(implementation)
        if hallucinations:
            issues.extend([f"🚨 Hallucination detected: {h}" for h in hallucinations])

        return len(issues) == 0, issues

    def _check_tests_passing(self, impl: Dict[str, Any]) -> bool:
        """
        Verify all tests pass WITH EVIDENCE

        Must have:
        - tests_passed = True
        - test_output (actual results, not just claim)
        """
        if not impl.get("tests_passed", False):
            return False

        # Require actual test output (anti-hallucination)
        test_output = impl.get("test_output", "")
        if not test_output:
            return False

        # Check for passing indicators in output
        passing_indicators = ["passed", "OK", "✓", "✅"]
        return any(indicator in test_output for indicator in passing_indicators)

    def _check_requirements_met(self, impl: Dict[str, Any]) -> List[str]:
        """
        Verify all requirements satisfied

        Returns:
            List of unmet requirements (empty if all met)
        """
        requirements = impl.get("requirements", [])
        requirements_met = set(impl.get("requirements_met", []))

        unmet = []
        for req in requirements:
            if req not in requirements_met:
                unmet.append(req)

        return unmet

    def _check_assumptions_verified(self, impl: Dict[str, Any]) -> List[str]:
        """
        Verify assumptions checked against official docs

        Returns:
            List of unverified assumptions (empty if all verified)
        """
        assumptions = impl.get("assumptions", [])
        assumptions_verified = set(impl.get("assumptions_verified", []))

        unverified = []
        for assumption in assumptions:
            if assumption not in assumptions_verified:
                unverified.append(assumption)

        return unverified

    def _check_evidence_exists(self, impl: Dict[str, Any]) -> List[str]:
        """
        Verify evidence provided (test results, code changes, validation)

        Returns:
            List of missing evidence types (empty if all present)
        """
        evidence = impl.get("evidence", {})
        missing = []

        # Evidence requirement 1: Test Results
        if not evidence.get("test_results"):
            missing.append("test_results")

        # Evidence requirement 2: Code Changes
        if not evidence.get("code_changes"):
            missing.append("code_changes")

        # Evidence requirement 3: Validation (lint, typecheck, build)
        if not evidence.get("validation"):
            missing.append("validation")

        return missing

    def _detect_hallucinations(self, impl: Dict[str, Any]) -> List[str]:
        """
        Detect hallucination red flags

        7 Red Flags:
        1. "Tests pass" without showing output
        2. "Everything works" without evidence
        3. "Implementation complete" with failing tests
        4. Skipping error messages
        5. Ignoring warnings
        6. Hiding failures
        7. "Probably works" statements

        Returns:
            List of detected hallucination patterns
        """
        detected = []

        # Red Flag 1: "Tests pass" without output
        if impl.get("tests_passed") and not impl.get("test_output"):
            detected.append("Claims tests pass without showing output")

        # Red Flag 2: "Everything works" without evidence
        if impl.get("status") == "complete" and not impl.get("evidence"):
            detected.append("Claims completion without evidence")

        # Red Flag 3: "Complete" with failing tests
        if impl.get("status") == "complete" and not impl.get("tests_passed"):
            detected.append("Claims completion despite failing tests")

        # Red Flag 4-6: Check for ignored errors/warnings
        errors = impl.get("errors", [])
        warnings = impl.get("warnings", [])
        if (errors or warnings) and impl.get("status") == "complete":
            detected.append("Ignored errors/warnings")

        # Red Flag 7: Uncertainty language
        description = impl.get("description", "").lower()
        uncertainty_words = ["probably", "maybe", "should work", "might work"]
        if any(word in description for word in uncertainty_words):
            detected.append(f"Uncertainty language detected: {description}")

        return detected

    def format_report(self, passed: bool, issues: List[str]) -> str:
        """
        Format validation report

        Args:
            passed: Whether validation passed
            issues: List of issues detected

        Returns:
            str: Formatted report
        """
        if passed:
            return "✅ Self-Check PASSED - Implementation complete with evidence"

        report = ["❌ Self-Check FAILED - Issues detected:\n"]
        for issue in issues:
            report.append(f"  {issue}")

        return "\n".join(report)

    def check_and_cleanup_tasks(
        self, tasks: List[Dict[str, Any]], auto_delete: bool = True
    ) -> Tuple[List[str], List[Dict[str, Any]], str]:
        """
        Check for stale tasks and automatically clean them up.

        Integrates with Claude Code 2.1.20's TaskUpdate delete feature.

        Args:
            tasks: List of task dictionaries
            auto_delete: If True, automatically delete stale tasks

        Returns:
            Tuple of (deleted_ids, remaining_tasks, report)
        """
        manager = TaskCleanupManager(auto_delete=auto_delete)
        deleted_ids, remaining = manager.cleanup_tasks(tasks)
        stale = manager.identify_stale_tasks(tasks)
        report = manager.generate_cleanup_report(deleted_ids, stale)

        return deleted_ids, remaining, report
