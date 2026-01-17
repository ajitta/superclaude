"""Tests for parallel execution engine."""

import pytest

from superclaude.execution.parallel import (
    ExecutionPlan,
    ParallelExecutor,
    ParallelGroup,
    Task,
    TaskStatus,
    parallel_file_operations,
    should_parallelize,
)


class TestTask:
    """Test Task dataclass."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            id="test1",
            description="Test task",
            execute=lambda: "result",
            depends_on=[],
        )
        assert task.id == "test1"
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None

    def test_can_execute_no_dependencies(self):
        """Task with no dependencies can always execute."""
        task = Task(
            id="test1",
            description="Test task",
            execute=lambda: "result",
            depends_on=[],
        )
        assert task.can_execute(set()) is True
        assert task.can_execute({"other"}) is True

    def test_can_execute_with_dependencies(self):
        """Task with dependencies can only execute when satisfied."""
        task = Task(
            id="test2",
            description="Test task",
            execute=lambda: "result",
            depends_on=["dep1", "dep2"],
        )
        assert task.can_execute(set()) is False
        assert task.can_execute({"dep1"}) is False
        assert task.can_execute({"dep1", "dep2"}) is True
        assert task.can_execute({"dep1", "dep2", "dep3"}) is True


class TestParallelGroup:
    """Test ParallelGroup dataclass."""

    def test_group_repr(self):
        """Test group string representation."""
        tasks = [
            Task(id="t1", description="Task 1", execute=lambda: None, depends_on=[]),
            Task(id="t2", description="Task 2", execute=lambda: None, depends_on=[]),
        ]
        group = ParallelGroup(group_id=0, tasks=tasks, dependencies=set())
        assert "Group 0" in repr(group)
        assert "2 tasks" in repr(group)


class TestExecutionPlan:
    """Test ExecutionPlan dataclass."""

    def test_plan_repr(self):
        """Test plan string representation."""
        plan = ExecutionPlan(
            groups=[],
            total_tasks=5,
            sequential_time_estimate=5.0,
            parallel_time_estimate=2.0,
            speedup=2.5,
        )
        repr_str = repr(plan)
        assert "5" in repr_str
        assert "2.5" in repr_str


class TestParallelExecutor:
    """Test ParallelExecutor class."""

    def test_executor_creation(self):
        """Test executor initialization."""
        executor = ParallelExecutor(max_workers=5)
        assert executor.max_workers == 5

    def test_plan_independent_tasks(self):
        """Test planning independent tasks creates single group."""
        executor = ParallelExecutor()
        tasks = [
            Task(id="t1", description="Task 1", execute=lambda: 1, depends_on=[]),
            Task(id="t2", description="Task 2", execute=lambda: 2, depends_on=[]),
            Task(id="t3", description="Task 3", execute=lambda: 3, depends_on=[]),
        ]
        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 1
        assert len(plan.groups[0].tasks) == 3

    def test_plan_sequential_tasks(self):
        """Test planning sequential tasks creates multiple groups."""
        executor = ParallelExecutor()
        tasks = [
            Task(id="t1", description="Task 1", execute=lambda: 1, depends_on=[]),
            Task(id="t2", description="Task 2", execute=lambda: 2, depends_on=["t1"]),
            Task(id="t3", description="Task 3", execute=lambda: 3, depends_on=["t2"]),
        ]
        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 3
        assert plan.speedup == 1.0  # No parallelization possible

    def test_plan_mixed_dependencies(self):
        """Test planning mixed dependency patterns."""
        executor = ParallelExecutor()
        tasks = [
            Task(id="r1", description="Read 1", execute=lambda: "r1", depends_on=[]),
            Task(id="r2", description="Read 2", execute=lambda: "r2", depends_on=[]),
            Task(
                id="analyze",
                description="Analyze",
                execute=lambda: "analyze",
                depends_on=["r1", "r2"],
            ),
        ]
        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 2
        # First group: r1, r2 (parallel)
        # Second group: analyze (depends on first)

    def test_plan_circular_dependency_raises(self):
        """Test that circular dependencies raise ValueError."""
        executor = ParallelExecutor()
        tasks = [
            Task(id="t1", description="Task 1", execute=lambda: 1, depends_on=["t2"]),
            Task(id="t2", description="Task 2", execute=lambda: 2, depends_on=["t1"]),
        ]

        with pytest.raises(ValueError, match="Circular dependency"):
            executor.plan(tasks)

    def test_execute_simple_tasks(self):
        """Test executing simple independent tasks."""
        executor = ParallelExecutor()
        results_list = []

        tasks = [
            Task(
                id="t1",
                description="Task 1",
                execute=lambda: results_list.append(1) or 1,
                depends_on=[],
            ),
            Task(
                id="t2",
                description="Task 2",
                execute=lambda: results_list.append(2) or 2,
                depends_on=[],
            ),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert len(results) == 2
        assert results["t1"] == 1
        assert results["t2"] == 2

    def test_execute_with_failure(self):
        """Test executing tasks with failures."""
        executor = ParallelExecutor()

        def failing_task():
            raise RuntimeError("Test error")

        tasks = [
            Task(
                id="t1", description="Good task", execute=lambda: "success", depends_on=[]
            ),
            Task(
                id="t2", description="Bad task", execute=failing_task, depends_on=[]
            ),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert results["t1"] == "success"
        assert results["t2"] is None
        assert tasks[1].status == TaskStatus.FAILED
        assert tasks[1].error is not None


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_should_parallelize_below_threshold(self):
        """Test should_parallelize returns False below threshold."""
        assert should_parallelize([1, 2]) is False
        assert should_parallelize([1, 2], threshold=3) is False

    def test_should_parallelize_at_threshold(self):
        """Test should_parallelize returns True at threshold."""
        assert should_parallelize([1, 2, 3]) is True
        assert should_parallelize([1, 2, 3], threshold=3) is True

    def test_should_parallelize_above_threshold(self):
        """Test should_parallelize returns True above threshold."""
        assert should_parallelize([1, 2, 3, 4, 5]) is True
        assert should_parallelize([1, 2, 3, 4, 5], threshold=3) is True

    def test_parallel_file_operations(self):
        """Test parallel_file_operations function."""

        def mock_operation(file: str) -> str:
            return f"processed_{file}"

        files = ["a.txt", "b.txt", "c.txt"]
        results = parallel_file_operations(files, mock_operation)

        assert len(results) == 3
        assert "processed_a.txt" in results
        assert "processed_b.txt" in results
        assert "processed_c.txt" in results


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
