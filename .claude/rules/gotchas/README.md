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
- **Limits**: 50 lines/file, 100 lines total recommended
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warn on 90-day+ stale.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)