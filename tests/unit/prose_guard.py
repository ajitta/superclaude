"""The unit a prose guard over shipped markdown should scope itself to.

Not a test module (``python_files = ["test_*.py"]`` skips it) — a helper the
drift guards import so the *unit derivation* has one definition site.

Guards that read shipped markdown and assert "this document never prescribes X"
kept being written as a filter over ``text.splitlines()``, and the per-line unit
failed in both directions:

* a re-wrap that lands mid-command splits the literal being searched for across
  two lines, so the guard silently matches NOTHING and passes forever;
* an exemption spelled as a substring test over the whole line ("...and
  ``'uv run' not in line``") launders a genuine prescription that merely shares
  a line with the exempting words.

Flattening whitespace first kills the first failure — the guard then sees one
command whatever width the file is wrapped to. Splitting the flattened text into
sentences keeps the second one bounded: an exemption applies to the sentence
that earns it, not to every neighbour that happens to be on the same line.

What stays per-guard is the pattern and any exemption: those genuinely differ
(`tests/unit/test_cli_entrypoints.py` guards the `python -m superclaude.scripts.`
module form, `tests/unit/test_cli_context.py` the `python <path>/<script>.py`
file-path form). Only the unit was ever duplicated, so only the unit is shared.

Caveat worth knowing before relying on it: "sentence" means "run of text between
terminal punctuation", so a markdown table with no `.`/`!`/`?` in it collapses
into ONE unit. A guard whose exemption could then be borrowed from a neighbouring
row has to anchor that exemption on shape, not on the marker turning up anywhere
in the unit.
"""

from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def prose_units(text: str) -> list[str]:
    """``text`` as whitespace-flattened sentences, the unit a guard should scan."""
    return _SENTENCE_BOUNDARY.split(_WHITESPACE.sub(" ", text))
