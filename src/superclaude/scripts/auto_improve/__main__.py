"""Allow ``python -m superclaude.scripts.auto_improve`` to invoke the CLI."""

from .cli import main

raise SystemExit(main())
