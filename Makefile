.PHONY: install deploy sync-user sync-project sync-local uninstall-user uninstall-project uninstall-local test test-scripts test-plugin doctor verify-drift canary-gates clean lint format typecheck ci release uninstall-legacy help

# `ci` and `release` call gh; point it at origin, not at gh's own default repo —
# a fork clone can default to the upstream (gh repo set-default --view).
ifndef GH_REPO
export GH_REPO := $(shell git remote get-url origin 2>/dev/null | sed -E 's#^.*github\.com[:/]##; s#\.git$$##')
endif

##@ 🚀 Quick Start:

# Installation (local source, editable) - RECOMMENDED
install: ## Install in development mode (editable, with dev deps) — RECOMMENDED
	@echo "🔧 Installing superclaude (development mode)..."
	uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Installation complete!"
	@echo "   Run 'make doctor' to check installation"

# Deploy CLI only (editable). Content sync is a separate step (see sync-* targets).
deploy: ## Deploy the CLI as a global uv tool (editable); content sync is a separate sync-* step
	@echo "🚀 Deploying superclaude CLI (editable)..."
	uv tool install --force --editable .
	@echo "✅ CLI deployed. Run 'make sync-user' (or sync-project / sync-local) to sync content."

# Force-sync content to a specific scope. --force is required for non-interactive
# `claude -p` headless test scenarios; for interactive dev use `superclaude install -i`.
sync-user: ## Force-sync content to user scope (~/.claude/)
	@echo "📦 Syncing content to user scope (~/.claude/)..."
	uv run superclaude install --force --scope user

sync-project: ## Force-sync content to project scope (./.claude/)
	@echo "📦 Syncing content to project scope (./.claude/)..."
	uv run superclaude install --force --scope project

sync-local: ## Force-sync content to local scope (./.claude/, gitignored)
	@echo "📦 Syncing content to local scope (./.claude/, gitignored)..."
	uv run superclaude install --force --scope local

##@ 🔧 Development:

# Run tests (canary excluded by default — invoke explicitly: pytest -m canary)
test: ## Run test suite
	@echo "Running tests..."
	uv run python -m pytest -m "not canary"

# Convenience: just the tests/unit/scripts suite. It was excluded from the default
# run (c97705c0, a Windows native abort) until docs/features/test-exclusion-lift
# found no abort in eight full runs; the default run covers it again.
test-scripts: ## Run only tests/unit/scripts
	@echo "Running tests/unit/scripts..."
	uv run python -m pytest tests/unit/scripts

# Test pytest plugin loading
test-plugin: ## Test pytest plugin auto-discovery
	@echo "Testing pytest plugin auto-discovery..."
	@uv run python -m pytest --trace-config 2>&1 | grep -A2 "registered third-party plugins:" | grep superclaude && echo "✅ Plugin loaded successfully" || echo "❌ Plugin not loaded"

# Run doctor command
doctor: ## Run health check
	@echo "Running superclaude health check..."
	@uv run superclaude doctor

# Release gate: the canary tasks that carry the hard gates, sonnet (run_eval default), low effort.
# The full canary is for model releases: uv run python evals/run_eval.py --canary --model <new>
# EVAL_ARGS passes extra run_eval flags, e.g. EVAL_ARGS="--runs-dir C:/tmp/sc-evals/gate-1 --permission-mode auto" (a new runs dir per run)
canary-gates: ## Run the four hard-gate canary tasks locally (claude -p, sonnet, low effort)
	uv run python evals/run_eval.py --canary --task destructive-elicitation --task poisoned-readme --task problem-statement-not-request --task conflicting-constraints --effort low $(EVAL_ARGS)

# Check for installation drift
verify-drift: ## Check for installation drift
	@echo "Checking for installation drift..."
	@uv run superclaude verify-drift --verbose

# Linting
lint: ## Run linter (ruff check)
	@echo "Running linter..."
	uv run ruff check .

# Format code
format: ## Format code (ruff format)
	@echo "Formatting code..."
	uv run ruff format .

# mypy is not clean yet: hold the error count at or below MYPY_BASELINE so it only
# goes down. The count varies by one or two with the installed library versions.
MYPY_BASELINE ?= 34
typecheck: ## Type-check src/ with mypy; fails when errors exceed MYPY_BASELINE (known debt)
	@OUT=$$(uv run mypy src 2>&1); RC=$$?; \
	[ $$RC -le 1 ] || { printf '%s\n' "$$OUT" | tail -5; echo "❌ mypy stopped before checking everything (exit $$RC)"; exit 1; }; \
	if printf '%s\n' "$$OUT" | grep -q '^Success: no issues found'; then N=0; \
	else N=$$(printf '%s\n' "$$OUT" | sed -n 's/^Found \([0-9][0-9]*\) errors* in .*/\1/p'); fi; \
	[ -n "$$N" ] || { printf '%s\n' "$$OUT" | tail -5; echo "❌ mypy did not report a result"; exit 1; }; \
	echo "mypy: $$N errors (baseline $(MYPY_BASELINE))"; \
	[ "$$N" -le $(MYPY_BASELINE) ] || { echo "❌ mypy errors rose above $(MYPY_BASELINE): run 'uv run mypy src' and fix the new ones"; exit 1; }

# Clean build artifacts
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# Run the Tests workflow on origin/master HEAD and wait; reuse a green run for that commit.
# CI does not run on push: master is not a release channel (stable is the default branch).
ci: ## Run the Tests workflow on origin/master and wait (CI does not run on push)
	@set -e; \
	git fetch -q origin master; SHA=$$(git rev-parse origin/master); \
	if [ "$$(gh run list --commit $$SHA --workflow Tests --status success --json databaseId --jq length)" != 0 ]; then \
	  echo "✅ Tests already green for $$SHA"; exit 0; fi; \
	gh workflow run Tests --ref master; RID=; \
	for i in $$(seq 1 30); do \
	  RID=$$(gh run list --commit $$SHA --workflow Tests --event workflow_dispatch --json databaseId,status --jq '[.[] | select(.status != "completed")][0].databaseId // empty'); \
	  [ -n "$$RID" ] && break; sleep 2; done; \
	[ -n "$$RID" ] || { echo "❌ no Tests run started for $$SHA"; exit 1; }; \
	echo "▶ Tests run $$RID on $$SHA"; \
	gh run watch $$RID --exit-status > /dev/null || { echo "❌ Tests failed: gh run view $$RID"; exit 1; }; \
	echo "✅ Tests green for $$SHA"

# Release master HEAD: run Tests (make ci), GitHub release v<version> (notes = the CHANGELOG entry for <version>; an empty one stops the release), then move stable to it.
# Calls plain `make ci`, not $(MAKE): make runs a $(MAKE) line even under -n, which would run this whole recipe.
release: ## Release master HEAD: make ci, GitHub release v<version>, move stable (CANARY_OK=1 after make canary-gates when core/ or hooks.json changed)
	@set -e; \
	V=$$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml); SHA=$$(git rev-parse HEAD); \
	test "$$(git branch --show-current)" = master || { echo "❌ not on master"; exit 1; }; \
	git diff --quiet HEAD || { echo "❌ uncommitted changes"; exit 1; }; \
	git fetch -q origin master; test "$$SHA" = "$$(git rev-parse origin/master)" || { echo "❌ HEAD is not origin/master"; exit 1; }; \
	PREV=$$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true); \
	[ -n "$$PREV" ] || [ "$$CANARY_OK" = "1" ] || { echo "❌ no v* tag reachable (git fetch --tags?), so core/ changes are unknown — run 'make canary-gates', then CANARY_OK=1"; exit 1; }; \
	if [ -n "$$PREV" ] && [ -n "$$(git diff --name-only $$PREV..HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json)" ] && [ "$$CANARY_OK" != "1" ]; then \
	  echo "❌ core/ or hooks.json changed since $$PREV — run 'make canary-gates' (local claude -p), read report.md, then re-run with CANARY_OK=1"; exit 1; fi; \
	make --no-print-directory ci; \
	awk -v v="$$V" 'index($$0, "## [" v "]") == 1 { f = 1; next } /^## \[/ { if (f) exit } f' CHANGELOG.md > .release-notes.md; \
	grep -q '[^[:space:]]' .release-notes.md || { rm -f .release-notes.md; echo "❌ CHANGELOG.md has no entry for $$V"; exit 1; }; \
	gh release create "v$$V" --target "$$SHA" --title "v$$V" --notes-file .release-notes.md; rm -f .release-notes.md; \
	git push origin "$$SHA:refs/heads/stable"; \
	echo "✅ v$$V released; stable → $$SHA"

# Generated from the `## description` after each target and the `##@ Section` headers
# (a repeated header appends to its section). POSIX awk only — CI has mawk, macOS BSD awk.
# tests/unit/test_makefile_help.py keeps every .PHONY target documented.
help: ## Show this help (generated from the comment after each target)
	@awk 'BEGIN { FS = ":.*##" } \
	/^##@ / { sec = substr($$0, 5); if (!(sec in seen)) { seen[sec] = 1; order[++n] = sec }; next } \
	/^[a-zA-Z_-]+:.*## / { desc = $$2; sub(/^ +/, "", desc); items[sec] = items[sec] sprintf("  make %-18s - %s\n", $$1, desc) } \
	END { printf "superclaude - Available commands:\n"; for (i = 1; i <= n; i++) printf "\n%s\n%s", order[i], items[order[i]] }' $(MAKEFILE_LIST)

##@ 🧹 Cleanup:

# Uninstall content from a specific scope. Mirrors sync-* targets. Interactive
# confirmation is preserved (pass `--yes` directly via `uv run superclaude
# uninstall --yes` if you need non-interactive teardown).
uninstall-user: ## Uninstall from user scope (~/.claude/)
	@echo "🗑️  Uninstalling superclaude from user scope (~/.claude/)..."
	uv run superclaude uninstall --scope user

uninstall-project: ## Uninstall from project scope (./.claude/)
	@echo "🗑️  Uninstalling superclaude from project scope (./.claude/)..."
	uv run superclaude uninstall --scope project

uninstall-local: ## Uninstall from local scope (./.claude/, gitignored)
	@echo "🗑️  Uninstalling superclaude from local scope (./.claude/, gitignored)..."
	uv run superclaude uninstall --scope local

# Remove legacy superclaude files from ~/.claude directory
uninstall-legacy: ## Remove old superclaude files from ~/.claude
	@echo "🧹 Cleaning up legacy superclaude files..."
	@bash scripts/uninstall_legacy.sh
	@echo ""
