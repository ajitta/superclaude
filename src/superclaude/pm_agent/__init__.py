"""
PM Agent Core Module

Provides core functionality for PM Agent:
- Pre-execution confidence checking
- Post-implementation self-check protocol
- Reflexion error learning pattern
- Token budget management
"""

from .confidence import (
    # Protocol
    ConfidenceCheck,
    # Result types
    CheckResult,
    ConfidenceChecker,
    ConfidenceResult,
    # Concrete checks (for custom registration)
    ArchitectureCheck,
    NoDuplicatesCheck,
    OfficialDocsCheck,
    OssReferenceCheck,
    RootCauseCheck,
)
from .reflexion import ReflexionPattern
from .self_check import SelfCheckProtocol

__all__ = [
    # Protocol
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
]
