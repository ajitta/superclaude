---
status: implemented
revised: 2026-04-08
spec: docs/specs/living-gotchas-architecture-discovery-ajitta-2026-04-08.md
---

# Living Gotchas Architecture — Implementation Plan

**Goal:** SuperClaude에 프로젝트별 gotchas 레이어(Layer 2)를 추가하여, 관찰된 실패가 `.claude/rules/gotchas/`에 축적되고 CC 네이티브 `paths:` 조건부 로딩으로 관련 gotchas만 자동 적용되게 한다.

**Architecture:** CC가 `.claude/rules/` 서브디렉토리를 재귀 스캔하는 네이티브 메커니즘을 활용. 4개 markdown 파일 수정 + 1개 파일 생성으로 구현 — Python 코드 변경 없음. 새 R19 규칙으로 교정 시 gotcha 캡처를 자동 제안.

**Tech Stack:** Markdown only (commands, rules, CLAUDE.md). No Python, no hooks, no new skills.

---

### Task 1: R19 신규 규칙 — Project Gotcha Capture

**Files:** Modify: `src/superclaude/core/RULES.md` (R18 뒤에 추가)

R14는 현재 그대로 유지 (correction → personal memory). 새 R19가 project gotcha 캡처를 담당 (Single Responsibility).

- [ ] R18 뒤에 R19 추가:

```
[R19] Project Gotcha Capture 🟡: when user corrects a project-specific pattern (files, packages, conventions — not personal style), propose adding to `.claude/rules/gotchas/<domain>.md` (format: `name: description`). Create file with `paths:` frontmatter if absent. User approval required. Ambiguous → prefer project (team-shareable). Skip if already in framework `<gotchas>`.
```

- [ ] examples 테이블에 R19 예시 추가:

```
| User corrects: "이 프로젝트에선 pytest-django 써야 해" | Saves only to auto memory | Proposes: "gotchas/testing.md에 추가할까요?" + saves to auto memory | Project Gotcha Capture 🟡 |
| User corrects: "응답 좀 더 짧게" | Proposes gotcha file addition | Saves to auto memory only (personal preference, no project reference) | Correction Capture 🟡 |
```

- [ ] Verify: `uv run pytest tests/unit/ -k "test_rules or test_content" -v` — 기존 테스트 통과 확인

---

### Task 2: /sc:init 메뉴에 gotchas 초기화 태스크 추가

**Files:** Modify: `src/superclaude/commands/init.md:22-70`

- [ ] `<menu>` 섹션에 task [h] 추가 (line 37 뒤):

```
    [h] Project gotchas setup          — .claude/rules/gotchas/general.md       (no deps)
```

- [ ] `--full` preset 업데이트:

```
  Presets: --quick (a,b) | --full (a,b,c,d,e,f,g,h)
```

- [ ] `<dependency_graph>` Batch 1에 [h] 추가:

```
  Batch 1 (parallel):  [a] [c] [e] [f] [h]     — no dependencies
```

- [ ] `<task_outputs>` 테이블에 추가:

```
  | h | general.md | .claude/rules/gotchas/ |
```

- [ ] `<safety_rules>`에 추가:

```
  - Gotchas init (h): create .claude/rules/gotchas/ directory + general.md only if not exists. Idempotent — skip if gotchas/ already present. Template content from spec (4-line comment header, no frontmatter).
```

- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -v` — init.md 구조 테스트 통과 확인

---

### Task 3: /sc:reflect에 gotchas gardening 추가

**Files:** Modify: `src/superclaude/commands/reflect.md`

- [ ] `<flow>` 섹션의 step 4 뒤에 gotchas gardening step 추가:

```
    4.5. Gotchas-Gardening: If `.claude/rules/gotchas/` exists, check: (a) files with `# Last reviewed:` older than 90 days → warn, (b) `paths:` glob patterns that match zero files in current project → warn stale pattern, (c) gotcha entries referencing identifiers not found in codebase → warn potential staleness.
```

- [ ] `<patterns>` 섹션에 추가:

```
    - Gotchas: staleness check → paths: validation → content relevance → prune recommendation
```

- [ ] Verify: `uv run pytest tests/unit/test_command_structure.py -v` — reflect.md 구조 테스트 통과 확인

---

### Task 4: CLAUDE.md에 Project Gotchas 컨벤션 문서화

**Files:** Modify: `CLAUDE.md` (프로젝트 루트, `## Architecture` 섹션과 `## Git Workflow` 섹션 사이)

- [ ] 아래 내용을 `## Architecture` 섹션 뒤, `## Git Workflow` 앞에 삽입. 구현 시 CLAUDE.md를 직접 읽고 정확한 삽입 위치 확인 후 Edit:

```
### Project Gotchas

Project-specific failure patterns live in `.claude/rules/gotchas/`. CC loads these natively.

    .claude/rules/gotchas/
    ├── general.md              # No paths: → always loaded
    └── <domain>.md             # paths: frontmatter → conditional loading

- **Format**: `- name: description` (one gotcha per line, same as framework `<gotchas>`)
- **Creation**: `/sc:init` task [h] creates `general.md`. Domain files are proposed by R19 on first correction.
- **paths: example**: `paths: ["**/models/**"]` → loads only when working on model files
- **Limits**: 50 lines per file, 100 lines total recommended
- **Gardening**: `# Last reviewed: YYYY-MM-DD` at top. `/sc:reflect` warns on 90-day+ staleness.
- **Layer priority**: Project gotcha (Layer 2) > Personal preference (Layer 3)
```

Note: 디렉토리 트리는 4-space indent 코드블록으로 표현 (트리플 백틱 중첩 방지).

- [ ] Verify: CLAUDE.md가 정상 로딩되는지 확인 (새 세션에서 gotchas 컨벤션이 보이는지)

---

### Task 5: SuperClaude 자체 프로젝트에 gotchas/general.md 시범 생성

**Files:** Create: `.claude/rules/gotchas/general.md`

- [ ] 디렉토리 + 파일 생성:

```markdown
# Project Gotchas — General
# Last reviewed: 2026-04-08
# Claude가 실수할 때마다 여기에 한 줄씩 추가됩니다.
# 기존에 알려진 프로젝트 트랩이 있으면 직접 추가 가능 (R19 자동 캡처와 병행).
```

- [ ] git에 커밋 대상으로 포함 (다른 `.claude/rules/` 파일과 동일 취급). 이것은 SuperClaude 프로젝트 자체의 gotchas이며, 프레임워크 배포물이 아님.
- [ ] Verify: 새 CC 세션에서 이 파일 내용이 로딩되는지 확인 (system prompt에 포함 여부)

---

### Task 6: 전체 테스트 + 검증

**Files:** None (verification only)

- [ ] `uv run pytest tests/unit/ -v` — 전체 유닛 테스트 통과
- [ ] 기존 테스트 baseline과 비교 (변경 전후 pass count 동일)
- [ ] 새 세션에서 `.claude/rules/gotchas/general.md`가 CC에 의해 로딩되는지 확인
- [ ] 교정 시나리오 수동 테스트: Claude에게 의도적으로 잘못된 패턴 사용하게 한 후 교정 → R14가 gotcha 추가 제안하는지 확인

---

## Execution Order

```
Task 1 (R19)       ─┐
Task 2 (init)       ─┤
Task 3 (reflect)    ─┤── 모두 병렬 가능 (독립적)
Task 4 (CLAUDE.md)  ─┤
Task 5 (general.md) ─┘
        │
Task 6 (전체 검증) ── 모든 Task 완료 후
```
