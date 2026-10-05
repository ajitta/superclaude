## Summary

<!-- What changes and why. If installed users must act on upgrade (hooks, flags, env vars, CLI commands), say what. -->

## Verification

<!-- Commands you ran and what they printed, e.g. `uv run pytest` → N passed. -->

## Checklist

- [ ] Targets `master`, never `stable` (only `make release` moves `stable`)
- [ ] Commit messages start with `feat:`, `fix:`, `docs:`, `refactor:`, `test:` or `chore:`
- [ ] `uv run pytest` exits 0 (markdown is tested too, so a docs-only change needs it)
- [ ] `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` pass
- [ ] Agent, command and mode changes follow the authoring rules in `.claude/rules/`
- [ ] No secrets or machine-specific paths committed
