# Log

## 2026-08-31

- **Update**: Migrated the whole bundle v0.1 → v0.2 (`timestamp` → `generated`, root `okf_version: "0.2"`), via okf-validate --migrate.
- **Update**: Re-synced 37 agent/command concept descriptions (and their index entries) from current source frontmatter — the bundle predated the trigger-damping pass, so many descriptions claimed natural-language auto-triggers the source now forbids.
- **Update**: Token Efficiency mode concept rewritten from symbol-compression to the current selective-omission design.
- **Update**: Verbalized Sampling mode concept gained `sources` (paper + in-repo re-verification doc) and an evidence-limits note; the mode itself was evidence-corrected in source the same day.
- **Update**: Root index — removed the empty Skills section left by the skills-layer deletion (910eabd; 5 skill concepts went with it), corrected Modes count 8 → 9 (Verbalized Sampling added) and MCP count 6 → 4 (Sequential and Context7 docs dropped earlier in source, 0a37af8/4aea453 — recorded late).

## 2026-07-05

- **Creation**: Initialized OKF v0.1 bundle from src/superclaude — 86 concepts across 6 sections (agents, commands, modes, skills, mcp, core) plus architecture overview.
- **Creation**: Each concept carries a `resource` pointer to its source markdown; bundle-absolute cross-links wire progressive-disclosure navigation.
- **Update**: Root index cross-links back to `src/superclaude/ARCHITECTURE.md` and the section READMEs; those docs add a reciprocal pointer to this bundle (bidirectional doc integration).
