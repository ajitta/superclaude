---
status: complete
revised: 2026-10-13
---

# Phase F: 저장소 쪽 변경 (C6)

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C6 표. `xml-prose-format.md`, `content-quality.md`는 변경 없음 (D10).

수를 복사하지 않는다 (gotcha `stale-number-copies`): 문서에는 "skills"라는 이름만 넣고 개수는 02 §1을 가리킨다.

### Task F1: `skill-authoring.md`

**Files:** Create: `.claude/rules/skill-authoring.md`

- [x] Step 1: frontmatter `paths: ["src/superclaude/skills/**", ".claude/rules/skill-authoring.md"]` (`command-authoring.md:1-3`과 같은 형식, gotcha `paths-frontmatter-format`)
- [x] Step 2: 내용 (C6 첫 행)
  - SuperClaude가 배포하는 스킬: 이름 `sc-` 접두어(공유 `.claude/skills/`에서 충돌 방지), 사이드 이펙트·메타 스킬은 `disable-model-invocation: true`, CC 전용 frontmatter 허용
  - references는 사용자 프로젝트 독자용으로 독립 작성, 이 저장소 rules를 링크·import하지 않음 (D10, `install-tree-boundary`)
  - references의 원본은 각 파일 `sources`의 외부 문서. 이 저장소 rules(`content-quality.md`, `xml-prose-format.md` 등)는 원본이 아니므로 rules를 바꿔도 references를 따라 바꾸지 않는다 (D20). 생성 결과의 기준은 설치된 각 프로젝트의 관례 (D19)
  - `/sc:prompt`에 모델을 넣으면 `quality.md` Model differences 행도 갱신 (`tests/unit/test_sc_author_skill.py`가 red로 알림)
  - `fields.yaml`이 검사기 데이터라는 점: 필드를 바꾸면 `uv run pytest tests/unit/test_author_check.py`
  - 구조 테스트 위치: `tests/unit/test_sc_author_skill.py`, `tests/unit/test_author_check.py`

### Task F2: 작은 문구 갱신

**Files:** Modify: `.claude/rules/schemas.yaml`, `.claude/rules/agent-authoring.md:112`, `AGENTS.md` Architecture

- [x] Step 3: `schemas.yaml`의 `forbidden_command_fields` 위에 한 줄 주석: "SuperClaude policy for its own commands; the fields Claude Code supports per type are in `src/superclaude/skills/sc-author/references/fields.yaml`"
- [x] Step 4: `agent-authoring.md:112` "SuperClaude ships no skills of its own — names refer to skills installed in `~/.claude/skills/` or `.claude/skills/`." → "SuperClaude's only skill, `sc-author`, sets `disable-model-invocation: true`, so it cannot be preloaded; names refer to skills installed in `~/.claude/skills/` or `.claude/skills/`."
- [x] Step 5: `AGENTS.md` Architecture 첫 문단 "(commands, agents, modes, output styles, MCP docs, core config)" → "(commands, agents, skills, modes, output styles, MCP docs, core config)"

### Task F3: 아키텍처 문서

**Files:** Modify: `src/superclaude/ARCHITECTURE.md` (`## Directory Roles` `:23`, Content Delivery 표 `:121-125`, Authoring Rules 표 `:149-157`), `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` §3 `### skills/` (`:124-132`)

- [x] Step 6: ARCHITECTURE Directory Roles에 `skills/` 항목: 사용자가 호출하는 스킬 디렉터리, 디렉터리 단위 설치. 다른 항목의 형식을 따른다
- [x] Step 7: Content Delivery 표 CC-native 행 `agents/, commands/, output-styles/` → `agents/, commands/, output-styles/, skills/`, 트리거 열에 `/sc-author` 추가
- [x] Step 8: Authoring Rules 표 행 `| skills/ | .claude/rules/skill-authoring.md | tests/unit/test_sc_author_skill.py |`
- [x] Step 9: 02 §3 `### skills/` 절을 현재 상태로: 역할(사용자 호출 전용 스킬, 참고 파일 묶음), 전달(`skills` 디렉터리 컴포넌트, 디렉터리 단위 copytree, 공유 대상이라 배포 이름만 제거), 위험(`fields.yaml` 두 사본 어긋남 → verify-drift, 공유 디렉터리 삭제 범위), 검증 초점(`test_install_skills_component.py`, `test_sc_author_skill.py`, 자기 검사)

### Task F4: README

**Files:** Modify: `README.md`

- [x] Step 10: `grep -n "^## \|/sc:" README.md`로 명령 소개 위치를 찾아 그 근처에 `/sc-author` 짧은 절: 무엇을 하나(형식 맞춤 + no-op 제거 + 검사), 명시 호출만, `--md`/`--xml`, `superclaude author-check <path>` 단독 사용 예 한 줄. 설치 결과 설명에 `.claude/skills/sc-author/` 한 줄
- [x] Step 11: README에 다른 컴포넌트 수가 적혀 있으면 그 줄은 건드리지 않는다 (범위 밖. 이미 02 §1을 가리키는지만 확인하고 아니면 최종 보고에 언급)

### Task F5: 검증과 커밋

- [x] Step 12: `git grep -n "ships no skills" -- src/ .claude/rules/` → 출력 없음
- [x] Step 13: `make format && make lint && uv run pytest` → 모두 exit 0 (문서 구조·교차 참조 테스트 포함)
- [x] Step 14: 커밋 `docs: document the sc-author skill and the skills component`

## Deviations

- ARCHITECTURE: Directory Roles 절 외에 맨 위 Framework Taxonomy 표에도 `skills/` 행 추가 (같은 문서의 콘텐츠 유형 목록이 둘이라 둘 다 맞춤)
- README: "All Commands" 목록 끝에 `### ✍️ Authoring (skill)` 절 (Step 10). Step 11: README "At a glance" 표(`37`, `24`, `8`, `3`)와 본문 "37 slash commands"는 02 §1을 가리키지 않고 숫자를 직접 적고 있음 — 범위 밖이라 건드리지 않음, 최종 보고에 언급
