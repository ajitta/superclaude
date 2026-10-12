---
status: complete
revised: 2026-10-12
---

# Phase G: 브랜치 단위 세션 기록

Index: [05-plan.md](./05-plan.md). 입력: Phase F 뒤 사용자 질문 "worktree, multi-branch 작업할때 'sc:load'. 'sc:save' 처리". 사용자가 고른 방안: 덮어쓰는 파일을 없애고 세션 기록을 브랜치별로 추가만 한다 (y, 이 브랜치에 적용).

## Decisions

- 원인: `last_session.md`/`next_actions.md`는 매 save가 덮어쓰는 고정 이름이다. 두 브랜치(또는 worktree)가 각각 저장하면 merge마다 내용 충돌, 먼저 merge된 브랜치의 요약을 다른 브랜치의 /sc:load가 읽는다. `session_[date].md`는 같은 날 두 브랜치면 add/add 충돌
- 기록: `.claude/memories/session_[date]_[branch-slug].md` 하나. 첫 줄 `branch: <name> @<short sha>`, 요약, `## Next actions` 체크리스트. 같은 날 같은 브랜치의 두 번째 save는 같은 파일을 갱신
- 브랜치 slug: `git branch --show-current`의 `/` → `-`, detached HEAD → `detached-<short sha>`. 정의는 save `<storage>` 한 곳, load는 포인터, project-manager는 subagent라 save를 받지 않으므로 한 줄로 적는다
- load: `pm_context` + 현재 브랜치의 가장 최근 기록. 없으면 아무 브랜치의 가장 최근 기록을 그 브랜치 기록이라고 알리고 읽는다
- `pm_context.md`: 하나로 둔다. 브랜치가 아닌 프로젝트 상태이고 쓰는 곳이 project-manager 하나
- auto memory: 같은 저장소의 worktree가 한 폴더를 공유한다 (근거: `~/.claude/projects/`에 worktree 전용 폴더가 없고, worktree 세션에서 저장한 `project_authoring-skill.md`가 메인 폴더에 있다). 항목에 브랜치를 적고 `MEMORY.md`는 해당 줄만 Edit
- 예전 이름 fallback은 두지 않는다. `.claude/memories/`는 이 브랜치가 처음 만들었고 아직 merge 전이라 예전 이름의 파일이 있는 사용자가 없다

### Task G1: 브랜치 단위 기록

**Files:** Modify: `tests/unit/test_session_memory_folder.py`, `src/superclaude/commands/save.md`, `src/superclaude/commands/load.md`, `src/superclaude/agents/project-manager.md`

- [x] Step 1: 테스트
  - save가 `.claude/memories/session_[date]_[branch-slug].md`를 쓴다
  - project-manager Session end가 같은 기록을 쓴다
  - load `<flow>` 1단계가 `session_*_[branch-slug].md`를 읽는다
  - save·load·project-manager 어디에도 `last_session`/`next_actions`가 없다
  - load가 이름으로 읽는 키(`pm_context`)는 project-manager Session end가 쓴다 (`PROJECT_MANAGER_ONLY_KEYS` 삭제)
- [x] Step 2: `uv run pytest tests/unit/test_session_memory_folder.py` → 새 테스트 7개 FAIL
- [x] Step 3: save `<flow>` 2·3단계, `<storage>` Branch slug 줄, `<outputs>` session 행; load `<flow>` 1단계; project-manager `:22`, `:71`
- [x] Step 4: Step 2 명령 → 14 passed
- [x] Step 5: 이 레포 `.claude/memories/`의 세 파일을 `session_2026-10-12_feature-serena-removal.md` 하나로 합침, local scope 재동기화

## Risks

- 기록 파일은 브랜치와 날짜만큼 쌓인다. 이력이 목적이라 정리 단계를 두지 않는다
- slug 충돌: `feature/x`와 `feature-x`가 같은 slug. 드물어서 막지 않는다
- 같은 브랜치를 두 기계에서 같은 날 저장하면 같은 파일이 충돌할 수 있다. 같은 브랜치의 일반 파일 편집과 같은 조건
