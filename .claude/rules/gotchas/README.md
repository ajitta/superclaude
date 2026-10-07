---
paths: [".claude/rules/gotchas/**"]
---

# Project Gotchas Subsystem

Project-specific failure patterns live here. CC load files native.

```
.claude/rules/gotchas/
├── general.md     # No paths: frontmatter → always loaded
└── <domain>.md    # paths: frontmatter → conditional loading
```

- **Format**: `- name: description` (one gotcha per line, same as framework `<gotchas>`)
- **Creation**: `/sc:init` task [h] make `general.md`. Domain files proposed by R19 on first correction.
- **paths: example**: `paths: ["**/models/**"]` → load only on model file work
- **Limits**: 50 lines/file, 100 lines total recommended; one entry ≤ 320 characters (name, symptom, action, SSOT pointer — the story behind it goes to a commit body or docs/, not here). `tests/unit/test_gotcha_budget.py` enforces the entry budget.
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warn on 90-day+ stale.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)