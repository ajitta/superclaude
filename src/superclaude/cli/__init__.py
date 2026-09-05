"""
SuperClaude CLI

Commands:
    - superclaude doctor                   # Check installation health
    - superclaude version                  # Show version
    - superclaude hook <name>              # Run one hook script (hooks.json form)

The console script enters through ``entry.py``, which dispatches ``hook`` ahead
of the click application in ``main.py`` (why: ``hook_dispatch.py``). Nothing is
imported here so that path stays free of it; ``superclaude.cli.main`` names the
submodule.
"""
