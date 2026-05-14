"""Allow ``python -m superclaude.scripts.parallel_ab`` to invoke the CLI."""

from .cli import main

raise SystemExit(main())
