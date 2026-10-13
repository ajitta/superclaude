---
status: draft
revised: 2026-10-13
---

# Phase G: 효과·명시 호출 프로브

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C7 "효과", "명시 호출" 행. 리뷰 I5: 비교는 `sc-full` arm 안에서 평문 vs `/sc-author`.

전제:
- 로컬 `claude -p` (구독 OAuth, API 키 없음). Fable로 돌리지 않는다 (AGENTS.md: headless Fable은 사용 크레딧 과금)
- Claude Code 세션 안에서 실행하면 `--runs-dir`를 `~/.claude` 밖의 새 디렉터리로 (AGENTS.md Canary 항목)
- `run_eval.py:164`가 작업 공간마다 `superclaude install --force --scope project`를 돌리므로 C 이후 `sc-full` arm에는 스킬이 설치된다. 실행 전 `uv run python -c "import superclaude; print(superclaude.__file__)"`이 이 worktree를 가리키는지 확인 (gotcha `venv-inherited-by-worktree`)
- 픽스처는 저장소 밖 임시 작업 공간으로 복사된다 (gotcha `probe-observer-effect`)

### Task G1: 픽스처와 과제

**Files:** Create: `evals/fixtures/sc-author/README.md`, `evals/fixtures/sc-author/migrations/001_init.sql` | Modify: `evals/tasks.yaml` (`implement-checkpoint` 뒤)

- [ ] Step 1: 픽스처: 작은 프로젝트 하나 (README에 "SQL migrations live in `migrations/`" 한 줄, SQL 파일 하나). `.claude/`는 넣지 않음 (arm이 설치)
- [ ] Step 2: 과제 두 개. 둘 다 `canary: true`, `canary_only: true` (선례 `implement-checkpoint`: 기본 4-arm 행렬에서 빠지고 `--canary`에서 `sc-full`로만 돈다, `run_eval.py:669-674`)
  - 공통: `fixture: fixtures/sc-author`, 다른 과제와 같은 git `setup`, `allowed_tools: [Bash, PowerShell, Read, Edit, Write, Grep, Glob, Skill]`, `max_turns: 20`
  - `sc-author-skill`: prompt `/sc-author agent a subagent at .claude/agents/sql-migration-reviewer.md that reviews SQL migrations in migrations/ for destructive statements`
  - `sc-author-plain`: prompt `Create a subagent at .claude/agents/sql-migration-reviewer.md that reviews SQL migrations in migrations/ for destructive statements.`
  - checks (둘 다)
    - `{type: file_exists_glob, tag: success, pattern: '.claude/agents/sql-migration-reviewer.md'}`
    - `{type: cmd_ok, tag: success, cmd: [superclaude, author-check, .claude/agents/sql-migration-reviewer.md]}` — `sc-author-skill`은 통과해야 하고, `sc-author-plain`은 측정값 (차이가 스킬에서 나오는지)
  - checks (`sc-author-skill`만): `{type: transcript_regex, tag: verification, pattern: 'author-check'}` — 스킬의 Check 단계가 실제로 돌았는지 (`transcript_regex`는 Bash·PowerShell 명령 입력만 봄, `run_eval.py:380-392`)
  - checks (`sc-author-plain`만): `{type: transcript_not_regex, tag: scope, pattern: 'author-check'}` — 평문 요청에서 스킬이 발동하지 않음 (C7 "명시 호출", D4)
  - `gate:`는 붙이지 않는다 (`tests/unit/test_eval_harness.py:183` 하드 게이트 집합 고정)
  - 헤드리스에서 승인 턴이 없으므로 스킬의 "diff → 승인 후 쓰기"에서 멈출 수 있다. 첫 실행에서 파일이 안 생기면 prompt 끝에 `Approved: write the file without asking.`를 붙이고 이 변경을 `## Deviations`에 기록 (`implement-checkpoint` 주석의 headless 승인 설명 참고)
- [ ] Step 3: `uv run pytest tests/unit/test_eval_harness.py -v` → PASS (`test_every_fixture_dir_exists`, `test_all_check_types_implemented`)
- [ ] Step 4: `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain --dry-run` → 작업 공간 두 개 생성, `.claude/skills/sc-author/SKILL.md` 존재

### Task G2: 실행과 기록

- [ ] Step 5: `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain --runs-dir <새 디렉터리>` (sonnet, 기본 effort). 한 번 실행
- [ ] Step 6: 아래 Results에 기록: 과제별 check 결과, `author-check` 출력의 error·warning 수, turns·duration
- [ ] Step 7: 판정
  - 성공 조건: `sc-author-skill`의 `cmd_ok`·`transcript_regex` 통과, `sc-author-plain`의 `transcript_not_regex` 통과
  - `sc-author-skill`이 실패 → 원인을 transcript에서 찾는다 (스킬 미확장 → `allowed_tools`·prompt 형식, 승인 대기 → Step 2 마지막 줄, 검사기 error 반복 → 3회 상한 동작 확인). 원인과 수정은 `## Deviations`
  - `sc-author-plain`도 `cmd_ok` 통과 → 효과 주장이 이 프로브로는 증명되지 않음. 숨기지 않고 Results에 그대로 쓰고 최종 보고에 올린다
- [ ] Step 8: `make format && make lint && uv run pytest` → 모두 exit 0
- [ ] Step 9: 커밋 `test(evals): add sc-author effect and explicit-invocation probes` (Results 포함)

## Results

(Phase G 실행 후 채움)
