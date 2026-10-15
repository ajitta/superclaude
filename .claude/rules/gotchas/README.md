---
paths: [".claude/rules/gotchas/**"]
---

# Project Gotchas Subsystem

Project-specific failure patterns live here. Claude Code loads these files natively: a file without `paths:` loads every session, a file with `paths:` loads when a matching file is touched.

```
.claude/rules/gotchas/
├── general.md     # No paths: frontmatter → always loaded
└── <domain>.md    # paths: frontmatter → conditional loading
```

- **Format**: `- name: description` (one gotcha per line, same as framework `<gotchas>`)
- **Creation**: `/sc:init` task [h] creates `general.md`. Domain files are proposed by [R19 Project Gotcha Capture] on first correction.
- **paths: example**: `paths: ["**/models/**"]` → loads only when working on model files
- **Limits**: 50 lines/file, 100 lines total recommended; one entry ≤ 320 characters (name, symptom, action, SSOT pointer — the story behind it goes to a commit body or docs/, not here). `tests/unit/test_gotcha_budget.py` enforces the entry budget.
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warns at 90+ days. Adding an entry does not bump the date; only a full pass over the file does.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)