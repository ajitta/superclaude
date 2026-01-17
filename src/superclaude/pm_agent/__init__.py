"""
PM Agent Core Module

Provides core functionality for PM Agent:
- Pre-execution confidence checking
- Post-implementation self-check protocol
- Reflexion error learning pattern
- Token budget management
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
