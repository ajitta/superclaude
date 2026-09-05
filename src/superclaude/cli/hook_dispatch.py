"""``superclaude hook <name>`` — the entry point every hooks.json command runs.

hooks.json used to register ``{{PYTHON_BIN}} {{SCRIPTS_PATH}}/<script>.py`` and
the installer baked both halves into absolute paths: the interpreter running the
installer, and a copy of the script under ``<base>/superclaude/scripts/``. Both
halves named one machine, so a project-scope ``.claude/settings.json`` — the
file the scope exists to share — was rewritten by every teammate's install.
The console script carries its own interpreter and its own copy of the package,
so a registration reduced to ``superclaude hook <name>`` has no machine-specific
byte in it: the committed file is identical for everyone.

Startup cost is the constraint on how this module is reached. Measured
2026-09-05: ``import superclaude.cli.main`` is ~40ms (click + yaml) against
~20ms for a hook script run directly, and hook processes fire three times per
Bash tool call. ``cli/entry.py`` therefore dispatches ``hook`` here BEFORE
importing the click application, and this module imports nothing from
``superclaude.cli.main``. Keep it that way: an import of click, yaml, or the
click group from here silently doubles the cost of every hook.

The registry is an allowlist, not an ``importlib`` of whatever name arrives. A
name that is not in it exits 1 with the name in stderr: loud, and the script
does not run, but NOT exit 2, the code that blocks the tool call on PreToolUse
and Stop. The same path fires when a committed project-scope settings.json
names a hook newer than the teammate's installed package (settings travel with
the repo, the package does not), and a typo and a version skew are
indistinguishable here. Exit 2 would lock every Bash/Read/Edit/Write of that
teammate's session behind an upgrade they have not made yet; exit 1 leaves the
new hook absent and everything else working. Decided 2026-09-05.
"""

from __future__ import annotations

import importlib
import sys

# Hook name -> (module, forwards argv). The name is the script's module stem so
# `grep <name>` finds the registration, the script and the tests together.
#
# Only insight_writer takes arguments: its hooks.json registrations name a
# subcommand (`harvest-from-hook`, `request-from-hook`, ...) and its own
# argparse parser reads them, the same way `superclaude insight` forwards. Every
# other script reads stdin and nothing else, and a stray argument on one of
# those is a hooks.json typo — refused rather than ignored.
HOOKS: dict[str, tuple[str, bool]] = {
    "context_loader": ("superclaude.scripts.context_loader", False),
    "context_reset": ("superclaude.scripts.context_reset", False),
    "destructive_guard": ("superclaude.scripts.destructive_guard", False),
    "file_size_guard": ("superclaude.scripts.file_size_guard", False),
    "insight_writer": ("superclaude.scripts.insight_writer", True),
    "loop_guard": ("superclaude.scripts.loop_guard", False),
    "memory_staleness": ("superclaude.scripts.memory_staleness", False),
    "prettier_hook": ("superclaude.scripts.prettier_hook", False),
    "session_init": ("superclaude.scripts.session_init", False),
    "test_runner_hook": ("superclaude.scripts.test_runner_hook", False),
}


def usage() -> str:
    names = "\n".join(f"  {name}" for name in sorted(HOOKS))
    return (
        "usage: superclaude hook <name> [args...]\n\n"
        "Run one SuperClaude hook script. This is what every command in\n"
        "hooks.json / settings.json invokes; stdin, stdout and the exit code\n"
        "are the script's own.\n\n"
        f"hooks:\n{names}\n"
    )


def run_hook(argv: list[str]) -> int:
    """Run the hook named by ``argv[0]``; return the process exit code.

    A script's ``main()`` keeps its own contract: ``None`` means 0, an int is
    returned as-is, and a ``SystemExit`` raised inside propagates untouched,
    exactly as under ``python <script>.py``. (The shipped guards block by
    printing ``{"decision": "block"}`` and exiting 0; the SystemExit path is
    argparse's exit 2 in insight_writer and any future script that exits.)
    """
    if not argv:
        sys.stderr.write(usage())
        return 2
    if argv[0] in ("-h", "--help"):
        sys.stdout.write(usage())
        return 0

    name, rest = argv[0], argv[1:]
    spec = HOOKS.get(name)
    if spec is None:
        # 1, not 2: see the module docstring. A bare `superclaude hook` above
        # keeps the usage-error 2 — no hooks.json registration is nameless.
        sys.stderr.write(f"superclaude hook: unknown hook {name!r}\n\n{usage()}")
        return 1

    module_name, forwards_argv = spec
    module = importlib.import_module(module_name)
    if forwards_argv:
        rc = module.main(rest, prog=f"superclaude hook {name}")
    else:
        if rest:
            sys.stderr.write(
                f"superclaude hook {name}: takes no arguments "
                f"(got {' '.join(rest)!r})\n"
            )
            return 1
        rc = module.main()
    return 0 if rc is None else int(rc)
