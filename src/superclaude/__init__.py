"""
SuperClaude Framework

AI-enhanced development framework for Claude Code.
Provides pytest plugin for enhanced testing and optional skills system.
"""

__version__ = "4.2.1+ajitta"
__author__ = "NomenAK, Mithun Gowda B"

# Expose main components
from .pm_agent.confidence import CheckResult, ConfidenceChecker, ConfidenceResult
from .pm_agent.reflexion import ReflexionPattern
from .pm_agent.self_check import SelfCheckProtocol

__all__ = [
    "CheckResult",
    "ConfidenceChecker",
    "ConfidenceResult",
    "ReflexionPattern",
    "SelfCheckProtocol",
    "__version__",
]
