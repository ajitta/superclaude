"""Self-extension prototype.

Detects repeated command patterns in a session and suggests
creating new skills via Anthropic's skill-creator.

This is an experimental/prototype module (Phase 4 / Sprint 7).
User approval is always required — no auto-generation.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass
class CommandPattern:
    """A detected repeated command sequence."""

    commands: list[str]
    frequency: int
    description: str = ""


@dataclass
class SkillSuggestion:
    """A suggested skill based on detected patterns."""

    name: str
    description: str
    trigger_phrases: list[str]
    detected_patterns: list[CommandPattern]
    confidence: float  # 0.0 to 1.0


class PatternDetector:
    """Detects repeated command sequences in session history.

    Looks for sequences of 2+ commands that appear 2+ times
    in the session, suggesting they could be automated as a skill.
    """

    def __init__(self, min_sequence_length: int = 2, min_frequency: int = 2) -> None:
        self._min_seq = min_sequence_length
        self._min_freq = min_frequency
        self._history: list[str] = []

    def record(self, command: str) -> None:
        """Record a command executed in the session."""
        self._history.append(command.strip())

    def detect(self) -> list[CommandPattern]:
        """Find repeated command sequences in history."""
        if len(self._history) < self._min_seq * self._min_freq:
            return []

        patterns: list[CommandPattern] = []

        # Check subsequences of various lengths
        for seq_len in range(self._min_seq, min(len(self._history) // 2 + 1, 6)):
            ngrams: Counter[tuple[str, ...]] = Counter()
            for i in range(len(self._history) - seq_len + 1):
                gram = tuple(self._history[i : i + seq_len])
                ngrams[gram] += 1

            for gram, count in ngrams.most_common():
                if count >= self._min_freq:
                    patterns.append(
                        CommandPattern(
                            commands=list(gram),
                            frequency=count,
                            description=f"{seq_len}-step sequence repeated {count} times",
                        )
                    )

        # Deduplicate: remove subsequences of longer patterns
        filtered = _remove_subsequences(patterns)
        return sorted(filtered, key=lambda p: (-len(p.commands), -p.frequency))


def _remove_subsequences(patterns: list[CommandPattern]) -> list[CommandPattern]:
    """Remove patterns that are subsequences of longer ones."""
    result: list[CommandPattern] = []
    sorted_patterns = sorted(patterns, key=lambda p: -len(p.commands))

    for p in sorted_patterns:
        is_sub = False
        for existing in result:
            if len(p.commands) < len(existing.commands):
                # Check if p.commands is a contiguous subsequence of existing.commands
                existing_str = " | ".join(existing.commands)
                p_str = " | ".join(p.commands)
                if p_str in existing_str:
                    is_sub = True
                    break
        if not is_sub:
            result.append(p)

    return result


class SkillSuggester:
    """Converts detected patterns into skill creation suggestions."""

    def suggest(self, patterns: list[CommandPattern]) -> list[SkillSuggestion]:
        """Generate skill suggestions from detected patterns.

        Returns suggestions sorted by confidence (highest first).
        """
        suggestions: list[SkillSuggestion] = []

        for pattern in patterns:
            name = _generate_name(pattern)
            description = _generate_description(pattern)
            triggers = _generate_triggers(pattern)

            confidence = min(1.0, (pattern.frequency - 1) * 0.2 + len(pattern.commands) * 0.15)

            suggestions.append(
                SkillSuggestion(
                    name=name,
                    description=description,
                    trigger_phrases=triggers,
                    detected_patterns=[pattern],
                    confidence=confidence,
                )
            )

        return sorted(suggestions, key=lambda s: -s.confidence)

    def format_for_skill_creator(self, suggestion: SkillSuggestion) -> str:
        """Format a suggestion as input for Anthropic's skill-creator.

        Returns a human-readable prompt that can be passed to skill-creator.
        """
        commands_str = "\n".join(f"  {i+1}. {cmd}" for i, cmd in enumerate(suggestion.detected_patterns[0].commands))
        triggers_str = ", ".join(f'"{t}"' for t in suggestion.trigger_phrases)

        return (
            f"Create a skill named '{suggestion.name}' that automates this workflow:\n\n"
            f"Steps:\n{commands_str}\n\n"
            f"Description: {suggestion.description}\n"
            f"Trigger phrases: {triggers_str}\n"
            f"Confidence: {suggestion.confidence:.0%}\n"
        )


def _generate_name(pattern: CommandPattern) -> str:
    """Generate a skill name from a command pattern."""
    # Extract key verbs/nouns from commands
    words: list[str] = []
    for cmd in pattern.commands[:3]:
        parts = cmd.lower().split()
        for part in parts[:2]:
            cleaned = part.strip("/-_.")
            if cleaned and len(cleaned) > 2 and cleaned not in ("the", "and", "for"):
                words.append(cleaned)
                break

    if words:
        return "sc-" + "-".join(words[:3])
    return f"sc-pattern-{hash(tuple(pattern.commands)) % 10000}"


def _generate_description(pattern: CommandPattern) -> str:
    """Generate a description from a command pattern."""
    step_count = len(pattern.commands)
    return f"Automates a {step_count}-step workflow detected {pattern.frequency} times in session"


def _generate_triggers(pattern: CommandPattern) -> list[str]:
    """Generate trigger phrases from a command pattern."""
    triggers: list[str] = []

    # Use first and last command as trigger context
    if pattern.commands:
        first = pattern.commands[0].lower().strip("/")
        triggers.append(first)

    if len(pattern.commands) > 1:
        last = pattern.commands[-1].lower().strip("/")
        if last not in triggers:
            triggers.append(last)

    return triggers
