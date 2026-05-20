---
status: complete
revised: 2026-05-20
---

# `scripts/` Dead-Code Audit

Audit of repo-root `scripts/` to classify each file as wired (auto-invoked), manual-only (orphan), or dead/broken. Evidence = reference search across `Makefile`, `*.toml`, `.github/**`, and `scripts/**` (excluding each file's own docstring as a self-reference).

No code changed — findings recorded only.

## Verdict

| File | External reference | Verdict |
|---|---|---|
| `build_superclaude_plugin.py` | `Makefile:115` (`make build-plugin`) | **Wired** — but spec `docs/specs/superclaude-plugin-discovery-ajitta-2026-05-05.md` marks it "scaffold exists; needs activation". Confirm it actually builds before relying. |
| `uninstall_legacy.sh` | `Makefile:188` | **Alive** — invoked by a make target. |
| `publish.sh` | README only | **Broken** — `publish.sh:19` sets `BUILD_SCRIPT="$SCRIPT_DIR/build_and_upload.py"`, but that file does not exist. Publish chain fails. |
| `build_and_upload.py` | README + `publish.sh:19` | **Missing** — referenced by README and `publish.sh`, file absent from `scripts/`. Phantom reference. |
| `ab_test_workflows.py` | self-docstring only | **Orphan** — manual-run only, no Makefile/CI/cross-script wiring. |
| `analyze_workflow_metrics.py` | self-docstring only | **Orphan** — manual-run only. |
| `compare_token_usage.py` | self-docstring only | **Orphan** — manual-run only. |
| `validate_instructions.py` | self-docstring only | **Orphan** — manual-run only. |
| `cleanup.sh` | self only (`cleanup.sh:100` points at broken `publish.sh`) | **Orphan** — and references the broken publish chain. |

## Key findings

- **Zero CI references.** Grep of `.github/**` for any of these script names returned nothing. `scripts/README.md` claims `.github/workflows/publish-pypi.yml` automates publishing — that claim is **stale** (no such workflow references these scripts).
- **README is stale.** `scripts/README.md` documents only `publish.sh` + `build_and_upload.py`. `build_and_upload.py` no longer exists. The 5 orphan scripts are not mentioned at all.
- **Two genuinely dead:** `publish.sh` (broken) + `build_and_upload.py` (absent). The PyPI publish chain does not work as documented.
- **Five orphans are not dead, just unwired:** workflow A/B + token-analysis + instruction-validation utilities. They run if invoked manually; otherwise dormant.

## Decision

Leave as-is. Documentation only — no cleanup, no deletion, no fix performed. This file is the record.

## Note (out of scope)

`~/.claude/scripts/update-tools.ps1` (manual updater for serena + tavily-cli) is a personal user-scope script outside this repo — unrelated to repo `scripts/`. Not part of this audit.
