"""
SuperClaude CLI

Commands:
    - superclaude doctor                   # Check installation health
    - superclaude version                  # Show version
    - superclaude hook <name>              # Run one hook script (hooks.json form)

The console script enters through ``entry.py``, which dispatches ``hook``
before the click application in ``main.py`` is imported (the click import
alone costs more than a whole hook run). Nothing is imported here so that the
fast path stays free of it; ``superclaude.cli.main`` names the submodule.
"""
