"""
PM Agent Pytest Patterns

Reusable testing patterns exposed as pytest fixtures via superclaude's pytest plugin.
These run during `uv run pytest`, NOT during Claude Code sessions.

The Claude Code agent definition is in agents/project-manager.md (separate system).

Patterns:
- ConfidenceChecker: Pre-execution gate with pluggable checks
- SelfCheckProtocol: Post-implementation validation
- ReflexionPattern: Cross-session error learning (JSONL)
- TokenBudgetManager: Token allocation by complexity
"""

from .confidence import (
    # Concrete checks (for custom registration)
    ArchitectureCheck,
    # Protocols
    AsyncConfidenceCheck,
    # Result types
    CheckResult,
    ConfidenceCheck,
    ConfidenceChecker,
    ConfidenceResult,
    NoDuplicatesCheck,
    OfficialDocsCheck,
    OssReferenceCheck,
    RootCauseCheck,
)
from .reflexion import ReflexionPattern
from .self_check import SelfCheckProtocol
from .token_budget import TokenBudgetManager

__all__ = [
    # Protocols
    "AsyncConfidenceCheck",
    "ConfidenceCheck",
    # Core
    "CheckResult",
    "ConfidenceChecker",
    "ConfidenceResult",
    # Concrete checks
    "ArchitectureCheck",
    "NoDuplicatesCheck",
    "OfficialDocsCheck",
    "OssReferenceCheck",
    "RootCauseCheck",
    # Other patterns
    "ReflexionPattern",
    "SelfCheckProtocol",
    "TokenBudgetManager",
]
