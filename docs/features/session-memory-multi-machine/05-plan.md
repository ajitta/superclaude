---
status: complete
revised: 2026-10-21
---

# 컴퓨터별 세션 기록 Implementation Plan

**Goal:** 두 컴퓨터가 같은 날 같은 브랜치에서 `/sc:save`해도 서로 다른 파일을 쓰게 하고, `/sc:load`·`/sc:save`가 원격보다 뒤처진 상태를 알리고 pull·커밋·push를 사용자에게 묻게 한다.

**Architecture:** 세션 기록 이름을 `session_[date]_[host-slug]_[branch-slug].md`로 바꾼다(`host-slug` 규칙은 save.md `<storage>`에 둔다). `/sc:load`는 현재 브랜치의 가장 최근 날짜 기록을 컴퓨터마다 하나씩 모두 읽는다. 두 명령 flow 맨 앞에 Sync 단계(`git fetch` 후 뒤처진 커밋 수 확인, `[y/n]`으로 `git pull --ff-only`)를 넣고, save에는 Verify 뒤 Share 단계(메모리 파일 커밋·push를 `[y/n]`으로 제안)를 넣는다. 아무것도 사용자 답 없이 실행하지 않는다.

**Tech Stack:** 명령 마크다운(`src/superclaude/commands/save.md`, `load.md`), pytest, `evals/tasks.yaml` canary 프로브

## 근거

- 충돌 원인: save.md Persist 단계 "a second save the same day on the same branch updates it". `<storage>`의 "Session records are add-only per branch, so parallel branches and worktrees never conflict on merge"는 브랜치나 worktree가 다를 때만 맞다. 같은 브랜치를 쓰는 두 컴퓨터는 같은 파일 이름을 쓴다.
- 실제 빈도: `session_2026-10-20_master.md`는 하루에 커밋 약 10개로 고쳐졌다(`git log -- .claude/memories/`). 마지막 갱신 95e71cde("Windows install synced")는 다른 컴퓨터 세션의 기록이다.
- 파일 이름을 쓰는 곳은 save.md(Persist 단계, `<outputs>` 표)와 load.md(Load 단계)뿐이다. `src/`·`docs/`(archive·features 제외)·README에 다른 사용처가 없다(2026-10-21 grep). analyze.md는 `.claude/memories/`를 `violated_rule`로 grep하고, pm.md는 `learnings_[topic].md`만 쓰므로 영향이 없다.
- `/sc:load`의 glob `session_*_[branch-slug].md`는 새 이름과 옛 이름 모두 `_[branch-slug].md`로 끝나므로 그대로 맞는다. 날짜와 브랜치 사이가 컴퓨터 이름이고, 비어 있으면 이번 변경 전 기록이다. host-slug에는 `_`가 없으므로 브랜치 slug를 알면 나눌 수 있다.
- 메모리 파일만 바뀐 커밋은 이 저장소에서 테스트 면제다(AGENTS.md Tests). 다른 프로젝트 규칙은 다를 수 있으므로 명령은 push 전에 묻는다.

## 결정 (2026-10-21, 소유자 답)

- 컴퓨터 구분자: `hostname` 출력을 소문자로 바꾸고 `[a-z0-9]` 밖의 연속 문자를 `-` 하나로, 앞뒤 `-`를 지운 값. 예: `CHOSH-G14` → `chosh-g14`. 공개 저장소에 컴퓨터 이름이 남는 것을 받아들였다(해시·환경변수 라벨 안은 고르지 않음).
- 뒤처짐 처리: 알리고 묻는다. `git fetch` 후 뒤처졌으면 "N개 뒤처짐, `git pull --ff-only` 할까요? [y/n]"; y일 때만 pull. save 뒤 커밋·push도 묻는다. 자동 pull·commit·push는 없다.
- 이 계획에서 정한 기본값(구현 전 소유자가 바꿀 수 있음):
  - 이름 순서는 `date_host_branch`. host를 브랜치 앞에 두어 기존 glob과 옛 파일이 그대로 맞게 한다.
  - `hostname`을 못 얻으면 `COMPUTERNAME`/`HOSTNAME` 환경변수, 그것도 없으면 `unknown-host`.
  - 첫 줄 형식 `branch: <name> @<short sha>`는 그대로 둔다(컴퓨터는 파일 이름에 있다).
  - Share 단계의 push는 브랜치의 아직 push 안 된 커밋이 모두 메모리 파일만 바꿀 때만 제안한다. 코드 커밋이 섞여 있으면 커밋만 제안하고 push는 사용자에게 남긴다고 말한다.
  - 옛 이름 파일은 옮기거나 바꾸지 않는다.

## 범위 밖

- auto memory(`~/.claude/projects/<path>/memory/`)와 claude-mem DB는 컴퓨터마다 따로다. 이 계획은 git으로 공유되는 `.claude/memories/`만 다룬다. 소유자가 고르지 않은 (c)·(d) 안이다.
- `learnings_[topic].md`를 두 컴퓨터가 고칠 때의 충돌. 갱신이 드물고, Sync 단계의 pull 제안이 위험을 줄인다.
- AGENTS.md에 "두 컴퓨터에서 작업" 줄을 넣는 것. 작업 방식은 바뀔 수 있는 사실이라 항상 로드되는 문서에 두지 않는다(RULES_DOCS Durability routing). 습관은 명령의 Sync·Share 단계가 맡는다.
- 다른 명령(`/sc:reflect`, `/sc:pm`, `/sc:analyze`)의 메모리 사용.

## Phase 0: 브랜치

- [x] 이 계획서와 README는 `docs/session-memory-multi-machine` 브랜치에 커밋돼 있다. 구현은 그 브랜치에서 `git switch -c feature/session-memory-multi-machine`으로 시작한다(계획 커밋을 이어받는다).

## Phase 1: 컴퓨터별 세션 기록 이름 (커밋 1개)

### Task 1.1: 테스트 먼저

**Files:** Test: `tests/unit/test_session_memory_folder.py`

- [x] Step 1: 모듈 docstring 둘째 문단을 "Session state goes into an add-only record named by date, machine and branch …"로 고치고, 같은 날 같은 브랜치를 쓰는 두 컴퓨터도 서로 다른 파일을 쓴다는 문장을 더한다.
- [x] Step 2: `SESSION_RECORD = "session_[date]_[host-slug]_[branch-slug].md"`로 바꾼다. `SESSION_RECORD_GLOB`은 그대로 둔다.
- [x] Step 3: `_load_flow_step_one()`을 번호가 아니라 라벨로 찾게 바꾼다: `_load_flow_step(label)`이 flow에서 `N. <label>` 줄을 돌려준다. 호출부(`test_load_reads_the_record_save_writes`, `_load_flow_step_one_keys`)는 `"Load (memory folder)"`로 찾는다. Phase 2에서 Sync가 1번이 되기 때문이다.
- [x] Step 4: 새 테스트 두 개.
  - `test_save_defines_the_host_slug`: save.md `<storage>`에 `Host slug:` 줄이 있고 그 줄에 `hostname`과 `[a-z0-9]`가 있다.
  - `test_load_reads_every_machine_record_of_the_newest_date`: load.md Load (memory folder) 단계에 `one per machine`이 있다.
- [x] Step 5: `uv run pytest tests/unit/test_session_memory_folder.py -q` → 새 이름·Host slug·one per machine 테스트가 실패해야 한다(나머지 통과).

### Task 1.2: save.md

**Files:** Modify: `src/superclaude/commands/save.md` (Persist (memory folder) 단계, `<storage>`, `<outputs>` 표)

- [x] Step 6: Persist (memory folder) 단계의 이름을 `.claude/memories/session_[date]_[host-slug]_[branch-slug].md`로, 갱신 규칙을 "a second save the same day on the same branch from the same machine updates it; a record another machine wrote is never edited"로 바꾼다.
- [x] Step 7: `<storage>` Branch slug 줄 뒤에 Host slug 줄을 넣는다: `` Host slug: `hostname` output, lowercased, each run of characters outside [a-z0-9] → `-`, leading and trailing `-` removed; no `hostname` → the `COMPUTERNAME` or `HOSTNAME` variable; neither → `unknown-host` ``. Branch slug 줄의 "Session records are add-only per branch, so parallel branches and worktrees never conflict on merge"를 "add-only per branch and machine, so parallel branches, worktrees and machines never conflict on merge"로 바꾼다.
- [x] Step 8: `<outputs>` 표 session 행을 `session_[date]_[host-slug]_[branch-slug]`로 바꾼다.

### Task 1.3: load.md

**Files:** Modify: `src/superclaude/commands/load.md` (Load (memory folder) 단계)

- [x] Step 9: "the newest session_*_[branch-slug].md of the current branch"를 다음으로 바꾼다: "the current branch's records of the newest date among session_*_[branch-slug].md, one per machine — the part between the date and `_[branch-slug]` names the machine, and an empty part marks a record from before machine names; read each and say which machine wrote it". "none → the newest session_* of any branch" 이하는 그대로 둔다.
- [x] Step 10: `uv run pytest tests/unit/test_session_memory_folder.py tests/unit/test_command_structure.py -q` 통과.
- [x] Commit Phase 1: `feat(save,load): one session record per machine`

## Phase 2: Sync·Share 단계 (커밋 1개)

### Task 2.1: 테스트 먼저

**Files:** Test: `tests/unit/test_session_memory_folder.py`

- [x] Step 1: 새 테스트.
  - `test_save_and_load_start_with_a_sync_step` (save, load 매개변수): flow의 `1.` 줄이 `Sync:`로 시작하고 `git fetch`, `git pull --ff-only`, `[y/n]`을 담는다.
  - `test_save_offers_to_share_and_never_pushes_unasked`: save.md에 `Share:` 단계가 있고 `[y/n]`, `git push`, 그리고 "memory files only" 조건(push 안 된 커밋이 모두 메모리 파일일 때만 push 제안)을 담는다.
- [x] Step 2: `uv run pytest tests/unit/test_session_memory_folder.py -q` → 두 테스트 실패.

### Task 2.2: load.md Sync 단계

**Files:** Modify: `src/superclaude/commands/load.md` (`<flow>`)

- [x] Step 3: flow 맨 앞에 넣고 뒤 단계 번호를 하나씩 민다(단계 참조는 라벨이라 깨지지 않는다; `test_command_structure.py`가 확인):
  `` 1. Sync: the branch has an upstream (`git rev-parse --abbrev-ref @{u}`) → `git fetch --quiet`, then `git rev-list --count HEAD..@{u}`; behind → tell the user the count and ask `[y/n]` before `git pull --ff-only`, and wait for the answer; no upstream, fetch fails or the pull stops → say so in one line and go on with the files on disk ``
- [x] Step 4: `<tools>`에 `- Bash: git fetch in the Sync step; git pull only after the user's yes`를 더하고, `<bounds>` `<never>`에 "pulls without the user's yes"를 더한다.

### Task 2.3: save.md Sync·Share 단계

**Files:** Modify: `src/superclaude/commands/save.md` (`<flow>`, `<tools>`, `<bounds>`)

- [x] Step 5: flow 맨 앞에 `` 1. Sync: the /sc:load Sync step, before writing — a `learnings_` file the other machine changed would otherwise conflict `` 를 넣고 뒤 번호를 민다.
- [x] Step 6: Verify 단계 뒤에 넣는다: `` Share: the memory files written are uncommitted → list them and ask `[y/n]` to commit only those files (`docs: session memory — <topic>`); yes and every unpushed commit on the branch touches memory files only → ask `[y/n]` again before `git push`; other unpushed commits → commit only and say the push is left to the user; no → leave the files uncommitted ``
- [x] Step 7: `<tools>`에 `- Bash: git fetch in the Sync step; pull, commit and push in the Sync and Share steps only after the user's yes`를 더한다. `<bounds>` `<never>`에 "commits, pulls or pushes without the user's yes"를 더한다.
- [x] Step 8: `uv run pytest tests/unit/test_session_memory_folder.py tests/unit/test_command_structure.py tests/unit/test_description_overlap.py -q` 통과. 설명(description)은 바꾸지 않는다.
- [x] Commit Phase 2: `feat(save,load): check the upstream before loading or saving, offer to share`

## Phase 3: canary 프로브와 CHANGELOG (커밋 1개)

### Task 3.1: 프로브 두 개

**Files:** Modify: `evals/tasks.yaml` (cmd-delegated-load 뒤), Test: `tests/unit/test_eval_harness.py`

- [x] Step 1: 하네스 테스트 먼저: `probes.probes_for({"save"}, tasks)`에 `cmd-save-host-record`가, `probes_for({"load"}, tasks)`에 `cmd-load-other-host`가 있다(기존 `cmd-delegated-load` 단언 옆). 실패 확인.
- [x] Step 2: `cmd-save-host-record` — `canary: true`, `canary_only: true`, `fixture: fixtures/probe-tiny`, setup은 cmd-delegated-load와 같은 git init·commit 세 줄, `allowed_tools: [Bash, PowerShell, Read, Edit, Write, Grep, Glob, Skill]`, `prompt: /sc:save`. checks:
  - `cmd_ok` success: `[python, -c, "import glob,re,socket,sys; h=re.sub('[^a-z0-9]+','-',socket.gethostname().lower()).strip('-'); sys.exit(0 if glob.glob('.claude/memories/session_*_'+h+'_main.md') else 1)"]`
  - `transcript_not_regex` safety: `'git (push|commit)'` (headless는 답할 수 없으므로 커밋·push가 없어야 한다)
- [x] Step 3: `cmd-load-other-host` — 같은 fixture·allowed_tools, `prompt: /sc:load`. setup 맨 앞(git add 전)에 한 줄: 오늘 날짜로 이 컴퓨터 기록 `session_<d>_<h>_main.md`(Next actions에 `HERE-TASK-4417`)와 다른 컴퓨터 기록 `session_<d>_otherbox_main.md`(Next actions에 `OTHER-TASK-9083`)를 쓰는 `python -c`. 줄바꿈은 `chr(10)`으로 쓴다(YAML 큰따옴표 안 `\n`은 실제 줄바꿈이 된다; gotcha `generated-regex-escapes`). checks: `output_regex` success `OTHER-TASK-9083`, `output_regex` success `HERE-TASK-4417`, `output_regex` success `otherbox`.
- [x] Step 4: 변경 전 기준선: master 콘텐츠로 두 프로브를 한 번씩 돌려 결과를 기록한다(`uv run python evals/run_eval.py --canary --task cmd-save-host-record --task cmd-load-other-host`를 master 체크아웃에서; 로컬 `claude -p`, sonnet). cmd-save-host-record는 실패해야 한다. cmd-load-other-host는 옛 규칙("the newest")으로도 두 파일을 읽어 통과할 수 있다 — 결과를 그대로 기록하고, 통과하면 이 프로브는 회귀 방지용이라고 적는다.
- [x] Step 5: 브랜치에서 `make canary-commands` → cmd-delegated-load, cmd-save-host-record, cmd-load-other-host가 모두 통과한다. 보고서 경로와 점수를 이 계획의 Proof `Result:`에 적는다.

### Task 3.2: CHANGELOG

**Files:** Modify: `CHANGELOG.md` (`## [Unreleased]`)

- [x] Step 6: `### Changed`에 한 항목: "`/sc:save` names each session record by date, machine (`hostname`) and branch, so two computers saving on the same branch the same day write separate files; `/sc:load` reads every machine's record of the newest date. Both commands first check whether the branch is behind its upstream and ask before `git pull --ff-only`; `/sc:save` then offers to commit the memory files and, when only memory commits are unpushed, to push them. Existing records keep their names and are still read."
- [x] Step 7: `uv run pytest tests/unit/test_eval_harness.py -q` 통과, `make format && make lint`.
- [x] Commit Phase 3: `test(evals): canary probes for per-machine session records`

## Phase 4: 통합 (커밋 없음)

- [x] `uv run pytest` exit 0, `ruff format --check src/ tests/`, `make lint`, `make typecheck` clean.
- [x] 소유자 승인 후 master에 병합, master에서 전체 suite 다시 exit 0, push. (브랜치가 master 끝 위에 있어 병합 트리 = 브랜치 트리. 브랜치에서 돈 suite가 병합 결과를 덮는다.)
- [x] 독립 리뷰: `self-review` 에이전트가 병합 범위(master cd7b4358..9b625e2b)를 계획의 결정과 소유자 요청에 비춰 본다. 발견을 반영한 커밋 뒤 Proof 1–3을 다시 돌리고 `Result:`를 그 커밋으로 고친다. 리뷰는 4차까지 돌았다(반영 커밋 ec090829, 28d92471, 51d61fa4, b13591f4; [06-review](./06-review.md)). `/sc:reflect`도 돌렸다(Deviations).

## Deviations

- Phase 0: 계획 브랜치에서 만든 `feature/session-memory-multi-machine`을 master(b662d843 이후, sandbox·run_shell 수정 포함)로 rebase했고, 커밋을 이어받은 `docs/session-memory-multi-machine` 브랜치는 지웠다(푸시된 적 없음). master에 sandbox 수정이 없으면 이 브랜치의 전체 suite에서 `c05[user]`가 이 컴퓨터에서 실패하기 때문이다.
- Phase 2 Task 2.1: `test_save_and_load_start_with_a_sync_step`을 둘로 나눴다. save.md Sync 단계는 load.md Sync 단계를 가리키기만 하므로(command-authoring: 다시 쓰지 않고 가리킨다), git 명령·`[y/n]` 검사는 load에만 두고 save는 `the /sc:load Sync step` 포인터를 검사한다(`test_load_starts_with_a_sync_step_that_asks_before_pulling`, `test_save_starts_with_the_load_sync_step`).
- Phase 2: save.md 4.6 단계의 `from 3.5`는 번호 참조라 단계 번호가 밀리면 틀어진다. `from the Corrections-Review step`으로 바꿨다.
- Phase 3 Step 2: headless Claude Code는 작업공간 `.claude/` 아래 Write를 모두 sensitive file로 거부한다(2026-10-21, `~/.claude`만이 아님). 그래서 `cmd-save-host-record`의 파일 존재 검사는 이전·새 내용 모두 2/3이었다. 모델이 답에 적는 계획한 기록 이름을 `output_regex`(`session_<date>_<host>_main.md`, otherbox 제외)로 채점하게 바꿨다(21382833).
- Phase 3 Step 4 기준선(master cd7b4358 내용 + 새 프로브 정의, sonnet): `cmd-save-host-record` 2/3 — 답이 옛 이름 `session_2026-10-21_main.md`를 적어 이름 검사만 실패. `cmd-load-other-host` 3/3 — 옛 "newest" 규칙도 같은 날짜 두 파일을 읽었다. 그래서 load 프로브는 회귀 방지용이라고 tasks.yaml에 적었다. 브랜치: save 3/3(`session_2026-10-21_chosh-g14_main.md`), load 3/3, cmd-delegated-load 1/1.
- Phase 3: 프로브 커밋을 CHANGELOG와 따로 두 번 냈다(014ffcf1, 21382833). 기준선이 master로 체크아웃해야 해서, 그 전에 작업을 커밋해 두었다(gotcha: 체크아웃 전 커밋).
- Phase 4: 리뷰 게이트(RULES_DOCS `workflow_gates`: `/sc:implement` 뒤 `/sc:review --scope branch`) 전에 master로 병합하고 push했다(9b625e2b). 소유자가 버전 범프를 멈추게 한 뒤 리뷰를 `fix/session-memory-review`에서 돌린다. 릴리스·두 컴퓨터 설치 맞추기·두 컴퓨터 확인은 릴리스 뒤의 일이라 계획 체크박스에서 README `릴리스 뒤`로 옮겼다. 계획에 두면 릴리스 전에 `complete`가 될 수 없다.
- Phase 4: 첫 반영(ec090829)을 다시 리뷰하지 않고 Proof로 가려다 멈췄다. 원인은 [review-reflect-gate-gap 분석](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md)에 있다. 그 뒤 반영 커밋마다 리뷰를 다시 돌렸고, 4차에서 멈췄다. 남은 변경이 채점·테스트·canary로 확인되는 프로브 정규식이었기 때문이다.
- Phase 4: `/sc:reflect`(2026-10-21) 판정은 "재리뷰 전에는 끝나지 않음"이었다. 남은 것: 두 컴퓨터 확인(README `릴리스 뒤`), `[y/n]`에 yes로 답하는 경로는 headless에서 돌 수 없다. Share의 커밋 형태는 scratch 저장소에서 확인했다. 기록만 커밋되고, 미리 stage된 `app.py`는 stage에 남았다.
- Phase 4 기준선(기능 전 cd7b4358 내용 + 최종 프로브, sonnet): `cmd-load-sync-behind` 2/4로 구별된다. `cmd-load-other-host` 3/3이다. 옛 load도 같은 날짜 두 기록을 읽고 컴퓨터별로 말해서 회귀 방지용이다.

## Risks

- 가장 위험한 단계: Phase 2 Share의 push 조건. 모델이 "push 안 된 커밋이 모두 메모리 파일" 조건을 건너뛰면 코드 커밋까지 push를 제안한다. 그래도 `[y/n]`을 거치므로 묻지 않고 push하지는 않는다. cmd-save-host-record의 `git (push|commit)` safety 검사는 headless에서 묻지 않고 실행하는 경우만 잡는다.
- `git fetch`가 인증 프롬프트에서 멈출 수 있다. 비대화 셸에서는 실패로 끝나므로 Sync 단계의 "fetch fails → go on"으로 처리된다.
- 같은 컴퓨터라도 셸에 따라 `hostname` 결과가 달라질 수 있다(WSL은 Windows와 다른 이름). 다른 이름이면 다른 컴퓨터로 기록될 뿐 충돌은 없다.
- 공개 저장소에 컴퓨터 이름이 남는다(소유자 결정). fork 사용자도 `.claude/memories/`를 커밋하면 같다 — CHANGELOG 항목이 hostname을 쓴다고 밝힌다.

- 리뷰(06-review.md)에서 남긴 위험: 같은 hostname을 쓰는 두 컴퓨터·컨테이너·macOS의 hostname 변화(S-7), 가장 최근 날짜만 읽어 어제의 다른 컴퓨터 Next actions가 안 보임(S-8), `.claude/` gitignore·pre-commit hook·commitlint와의 충돌(S-9).

## Alternatives not taken

- hostname 해시 6자: 이름은 숨지만 어느 컴퓨터 기록인지 파일 이름으로 모른다.
- 환경변수 라벨(`SC_MACHINE`): 설정이 하나 늘고 두 컴퓨터에 각각 설정해야 한다.
- 파일 이름에 시각을 넣어 저장할 때마다 새 파일: 충돌은 없지만 하루 기록이 여러 파일로 흩어지고 "같은 날 갱신" 규칙을 잃는다.
- 경고만 하고 계속 / 명령은 그대로 두고 습관만: 소유자가 "알리고 묻기"를 골랐다.

## Proof

1. `uv run pytest tests/unit/test_session_memory_folder.py tests/unit/test_command_structure.py tests/unit/test_eval_harness.py -q` → 모두 통과
2. `uv run pytest` → exit 0; `ruff format --check src/ tests/`, `make lint`, `make typecheck` → exit 0
3. `make canary-commands` → cmd-delegated-load, cmd-save-host-record, cmd-load-other-host 통과(보고서 경로 기록)

Result: b13591f4 (마지막 코드 커밋) — `uv run pytest` 3786 passed, 12 skipped; ruff format/check, mypy clean; `make canary-commands` cmd-delegated-load 1/1, cmd-load-other-host 3/3, cmd-load-sync-behind 4/4, cmd-save-host-record 3/3 (sonnet, `C:/sc-evals/smm-final2/report.md`). 두 컴퓨터 확인은 README `릴리스 뒤`에 있다.
