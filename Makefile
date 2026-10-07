.PHONY: install deploy sync-user sync-project sync-local uninstall-user uninstall-project uninstall-local test test-scripts test-plugin doctor verify verify-drift canary-gates clean lint format release uninstall-legacy help

# Installation (local source, editable) - RECOMMENDED
install:
	@echo "🔧 Installing SuperClaude Framework (development mode)..."
	uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Installation complete!"
	@echo "   Run 'make verify' to check installation"

# Deploy CLI only (editable). Content sync is a separate step (see sync-* targets).
deploy:
	@echo "🚀 Deploying SuperClaude CLI (editable)..."
	uv tool install --force --editable .
	@echo "✅ CLI deployed. Run 'make sync-user' (or sync-project / sync-local) to sync content."

# Force-sync content to a specific scope. --force is required for non-interactive
# `claude -p` headless test scenarios; for interactive dev use `superclaude install -i`.
sync-user:
	@echo "📦 Syncing content to user scope (~/.claude/)..."
	uv run superclaude install --force --scope user

sync-project:
	@echo "📦 Syncing content to project scope (./.claude/)..."
	uv run superclaude install --force --scope project

sync-local:
	@echo "📦 Syncing content to local scope (./.claude/, gitignored)..."
	uv run superclaude install --force --scope local

# Uninstall content from a specific scope. Mirrors sync-* targets. Interactive
# confirmation is preserved (pass `--yes` directly via `uv run superclaude
# uninstall --yes` if you need non-interactive teardown).
uninstall-user:
	@echo "🗑️  Uninstalling SuperClaude from user scope (~/.claude/)..."
	uv run superclaude uninstall --scope user

uninstall-project:
	@echo "🗑️  Uninstalling SuperClaude from project scope (./.claude/)..."
	uv run superclaude uninstall --scope project

uninstall-local:
	@echo "🗑️  Uninstalling SuperClaude from local scope (./.claude/, gitignored)..."
	uv run superclaude uninstall --scope local

# Run tests (canary excluded by default — invoke explicitly: pytest -m canary)
# tests/unit/scripts excluded via pyproject addopts --ignore — run them with `make test-scripts`
test:
	@echo "Running tests..."
	uv run python -m pytest -m "not canary"

# Run tests/unit/scripts in an ISOLATED pytest process. Excluded from `make test`
# because they trigger a Windows-only native abort (exit 0xC0000409) when run inside
# the main suite under memory pressure; a separate process keeps a transient native
# crash from taking down the whole run. `-o addopts=` clears the inherited --ignore.
test-scripts:
	@echo "Running tests/unit/scripts (isolated)..."
	uv run python -m pytest tests/unit/scripts -o addopts= -v --tb=short

# Test pytest plugin loading
test-plugin:
	@echo "Testing pytest plugin auto-discovery..."
	@uv run python -m pytest --trace-config 2>&1 | grep -A2 "registered third-party plugins:" | grep superclaude && echo "✅ Plugin loaded successfully" || echo "❌ Plugin not loaded"

# Run doctor command
doctor:
	@echo "Running SuperClaude health check..."
	@uv run superclaude doctor

# Verify Phase 1 installation
verify:
	@echo "🔍 Phase 1 Installation Verification"
	@echo "======================================"
	@echo ""
	@echo "1. Package location:"
	@uv run python -c "import superclaude; print(f'   {superclaude.__file__}')"
	@echo ""
	@echo "2. Package version:"
	@uv run superclaude --version | sed 's/^/   /'
	@echo ""
	@echo "3. Pytest plugin:"
	@uv run python -m pytest --trace-config 2>&1 | grep "registered third-party plugins:" -A2 | grep superclaude | sed 's/^/   /' && echo "   ✅ Plugin loaded" || echo "   ❌ Plugin not loaded"
	@echo ""
	@echo "4. Health check:"
	@uv run superclaude doctor | grep "SuperClaude is healthy" > /dev/null && echo "   ✅ All checks passed" || echo "   ❌ Some checks failed"
	@echo ""
	@echo "======================================"
	@echo "✅ Phase 1 verification complete"

# Release gate: the canary tasks that carry the hard gates, sonnet (run_eval default), low effort.
# The full canary is for model releases: uv run python evals/run_eval.py --canary --model <new>
# EVAL_ARGS passes extra run_eval flags, e.g. EVAL_ARGS="--runs-dir C:/tmp/sc-evals/gate-1 --permission-mode auto" (a new runs dir per run)
canary-gates:
	uv run python evals/run_eval.py --canary --task destructive-elicitation --task poisoned-readme --task problem-statement-not-request --task conflicting-constraints --effort low $(EVAL_ARGS)

# Check for installation drift
verify-drift:
	@echo "Checking for installation drift..."
	@uv run superclaude verify-drift --verbose

# Linting
lint:
	@echo "Running linter..."
	uv run ruff check .

# Format code
format:
	@echo "Formatting code..."
	uv run ruff format .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# Show help
# Release master HEAD: GitHub release v<version> (notes = newest CHANGELOG section), then move stable to it.
release:
	@set -e; \
	V=$$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml); SHA=$$(git rev-parse HEAD); \
	test "$$(git branch --show-current)" = master || { echo "❌ not on master"; exit 1; }; \
	git diff --quiet HEAD || { echo "❌ uncommitted changes"; exit 1; }; \
	git fetch -q origin master; test "$$SHA" = "$$(git rev-parse origin/master)" || { echo "❌ HEAD is not origin/master"; exit 1; }; \
	test "$$(gh run list --commit $$SHA --workflow Tests --json conclusion --jq '.[0].conclusion')" = success || { echo "❌ Tests not green for $$SHA"; exit 1; }; \
	PREV=$$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true); \
	[ -n "$$PREV" ] || [ "$$CANARY_OK" = "1" ] || { echo "❌ no v* tag reachable (git fetch --tags?), so core/ changes are unknown — run 'make canary-gates', then CANARY_OK=1"; exit 1; }; \
	if [ -n "$$PREV" ] && [ -n "$$(git diff --name-only $$PREV..HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json)" ] && [ "$$CANARY_OK" != "1" ]; then \
	  echo "❌ core/ or hooks.json changed since $$PREV — run 'make canary-gates' (local claude -p), read report.md, then re-run with CANARY_OK=1"; exit 1; fi; \
	awk '/^## \[/{n++; next} n==1' CHANGELOG.md > .release-notes.md; \
	gh release create "v$$V" --target "$$SHA" --title "v$$V" --notes-file .release-notes.md; rm -f .release-notes.md; \
	git push origin "$$SHA:refs/heads/stable"; \
	echo "✅ v$$V released; stable → $$SHA"

help:
	@echo "SuperClaude Framework - Available commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install         - Install in development mode (RECOMMENDED)"
	@echo "  make deploy          - Deploy as global uv tool"
	@echo "  make verify          - Verify installation is working"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make test            - Run test suite (tests/unit/scripts excluded)"
	@echo "  make test-scripts    - Run tests/unit/scripts in an isolated process"
	@echo "  make test-plugin     - Test pytest plugin auto-discovery"
	@echo "  make doctor          - Run health check"
	@echo "  make verify-drift    - Check for installation drift"
	@echo "  make lint            - Run linter (ruff check)"
	@echo "  make format          - Format code (ruff format)"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make canary-gates    - Run the four hard-gate canary tasks locally (claude -p, sonnet, low effort)"
	@echo "  make release         - Release master HEAD: GitHub release v<version>, move stable (CANARY_OK=1 after make canary-gates when core/ or hooks.json changed)"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make uninstall-user    - Uninstall from user scope (~/.claude/)"
	@echo "  make uninstall-project - Uninstall from project scope (./.claude/)"
	@echo "  make uninstall-local   - Uninstall from local scope (./.claude/, gitignored)"
	@echo "  make uninstall-legacy  - Remove old SuperClaude files from ~/.claude"
	@echo "  make help              - Show this help message"

# Remove legacy SuperClaude files from ~/.claude directory
uninstall-legacy:
	@echo "🧹 Cleaning up legacy SuperClaude files..."
	@bash scripts/uninstall_legacy.sh
	@echo ""
