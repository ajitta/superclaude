"""
Task Cleanup Manager

Automatic task lifecycle management for Claude Code 2.1.20+.
Identifies and removes completed, cancelled, or stale tasks
via TaskUpdate delete feature.
"""

import time
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
