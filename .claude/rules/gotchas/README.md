# Project Gotchas Subsystem

Project-specific failure patterns live here. CC loads these files natively.

```
.claude/rules/gotchas/
├── general.md     # No paths: frontmatter → always loaded
└── <domain>.md    # paths: frontmatter → conditional loading
```

- **Format**: `- name: description` (one gotcha per line, same as framework `<gotchas>`)
- **Creation**: `/sc:init` task [h] creates `general.md`. Domain files are proposed by R19 on first correction.
- **paths: example**: `paths: ["**/models/**"]` → loads only when working on model files
- **Limits**: 50 lines per file, 100 lines total recommended
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warns on 90-day+ staleness.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)
