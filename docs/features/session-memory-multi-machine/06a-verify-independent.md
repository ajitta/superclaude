---
status: complete
revised: 2026-10-21
---

# 독립 검증: v4.34.1..4fd32d90

판정: 조건부 통과

별도 머신(Linux aarch64, Python 3.13.16, git 2.43.0, `/bin/sh`=dash 0.5.12)에서 별도 세션으로 재현했다. 게이트는 모두 통과하고, 수정마다 그것을 지키는 테스트가 있다. 릴리스 전에 1·2·4·5번(Important)을 고치거나, 알려진 한계로 CHANGELOG에 적어야 한다. 재현 스크립트는 `$TMPDIR/v1021/`(`rs/` run_shell, `git*/` git 시퀀스, `ev/` 프로브)에 있다.

## 발견

### 1. Important — run_shell이 호출자의 프로세스 그룹을 떠나 인터럽트되면 명령 트리가 살아남는다
`src/superclaude/utils/__init__.py:100`, `:113`
- 재현(`rs/scenario.sh`): `setsid python driver.py`로 호출자를 띄운다. driver는 옛 `subprocess.run` 또는 `run_shell`로 `python child.py && echo done`(4초 뒤 marker 파일을 쓴다)을 실행한다. 1초 뒤 driver에 신호를 보내고 marker로 생존을 판정했다.

| 신호 → 대상 | 옛 run | run_shell |
|---|---|---|
| INT → 그룹(터미널 Ctrl-C) | 죽음 | **생존** |
| TERM / KILL / HUP → 그룹 | 죽음 | **생존** |
| INT → pid(KeyboardInterrupt) | 손자 생존(shell만 kill) | **트리 전체 생존** |
| TERM → pid | 생존 | 생존 |

- 원인 1: `start_new_session=True`라서 그룹에 보낸 신호가 명령에 닿지 않는다.
- 원인 2: `subprocess.run`의 `except: process.kill(); raise` 같은 정리 코드가 없다. KeyboardInterrupt 때 `Popen.__exit__`는 0.25초만 기다리고 돌아간다.
- 반대 증거: 이 세션의 Bash 작업을 TaskStop으로 멈추자 `setsid`로 새 세션에 있던 손자까지 죽었다. Claude Code는 ppid 트리를 따라 죽이므로 CC 안의 훅 경로에서는 이 누수가 나지 않을 가능성이 높다. 훅 타임아웃 때 같은 방식인지는 확인하지 못했다.
- 영향: 터미널에서 돌린 `superclaude auto-improve`를 Ctrl-C로 멈추거나, 그룹 신호를 쓰는 감독자(`timeout`, 셸 job control)를 쓰면 eval/smoke 명령이 남는다.
- 수정안:
  - `except BaseException:`에서 `_kill_process_tree(proc.pid)`를 호출하고 다시 raise한다(`run()`과 같은 계약).
  - 훅과 coordinator에 SIGTERM/SIGHUP 핸들러를 두어 `SystemExit`로 바꾼다.
  - driver에 SIGINT를 보내는 테스트를 추가한다.

### 2. Important — test_runner_hook의 120초는 hooks.json 타임아웃 120초와 같아서, 트리 kill이 CC 안에서는 거의 실행되지 않는다
`src/superclaude/scripts/test_runner_hook.py:215`, `src/superclaude/hooks/hooks.json:127`
- CC의 타이머는 훅 시작 시점부터 돈다. `run_shell`의 타이머는 Python 기동과 테스트 명령 탐지가 끝난 뒤에야 시작하므로 CC가 항상 먼저 끊는다.
- CHANGELOG Fixed는 "test_runner_hook(120 s) … now kill every process"라고 쓰지만, 그 경로에서는 CC의 kill 방식이 결과를 정한다. 두 값이 같은 것은 v4.34.1부터였지만, 이번 수정의 효과가 이 조건에 달려 있다.
- 수정안: `run_shell(..., timeout=110)`로 줄이거나 hooks.json을 150으로 늘린다. 두 값의 관계를 테스트로 고정한다.

### 3. Suggestion — run_shell docstring과 테스트 docstring이 POSIX에서 옛 동작을 틀리게 적었다
`src/superclaude/utils/__init__.py:94`, `tests/unit/test_run_shell.py:5`
- 두 docstring은 "on POSIX whenever the shell forks"에도 `run`이 자식을 기다렸다고 쓴다.
- 실측(`rs/old_vs_new.py`): POSIX의 `run()`은 `kill()` 뒤 `wait()`만 하므로 0.50초에 돌아왔고, 자식은 살아남았다(exec 형태, fork 형태, `sh -c` 중첩 모두). Ubuntu dash는 단순 명령도 exec하지 않고 fork한다.
- 이 점은 CHANGELOG가 맞고 docstring이 틀렸다. 수정안: "POSIX: run은 돌아오지만 자식이 백그라운드에 남는다"로 고친다.

### 4. Important — 프로브 `cmd-load-other-host`의 짝짓기 정규식이 자연스러운 정답을 떨어뜨린다
`evals/tasks.yaml:1100`
- `(?:\n\s*){0,2}[^\n]{0,120}` 구조라서 과제 토큰은 machine 이름이 있는 줄 바로 다음의 비어 있지 않은 줄에 있어야 한다.
- 재현(`ev/regex_probe.py`): 다음 두 답은 실패한다. 기록에 `## Next actions`가 있으니 모델이 그대로 옮기기 쉬운 형태다.
  - `### otherbox (…)\n**Next actions:**\n- [ ] OTHER-TASK-9083`
  - `**otherbox** record\nbranch: main @0000000\n- [ ] OTHER-TASK-9083`
- 같은 줄, 제목+빈 줄+체크리스트, 표 형태는 통과한다. 짝을 바꾼 오답이 통과하는 것은 주석에 적힌 대로다.
- 수정안: `(?:\n[^\n]{0,120}){0,3}`처럼 중간 줄을 몇 줄 허용한다.

### 5. Important — 프로브 `cmd-load-sync-behind`의 결과 정규식이 흔한 정답 형식을 떨어뜨린다
`evals/tasks.yaml:1125`
- 실패하는 정답: `**1** commit behind`, `behind … by **1**`, `origin/main is 1 commit ahead`, `Behind: 1`
- 통과하는 오답: `not 1 commit behind`
- canary가 실제 회귀 없이 빨간색이 될 수 있다(06-review는 9개 사례로 채점했다고 하지만, 강조 표기된 숫자는 사례에 없었다).
- 수정안: 숫자 앞뒤 `\**`를 허용하고, `ahead`·`Behind:` 형태를 추가한다.

### 6. Suggestion — load Sync의 bash 표기 `GIT_TERMINAL_PROMPT=0`은 별도 문장으로 쓰면 효과가 없다
`src/superclaude/commands/load.md:13`
- 재현(`git5/`, 401을 돌려주는 로컬 HTTP 서버, pty, 전역 설정 차단):
  - 접두 형태 `GIT_TERMINAL_PROMPT=0 git … fetch` → "terminal prompts disabled"로 바로 실패한다.
  - 별도 문장 `GIT_TERMINAL_PROMPT=0; git … fetch` → export되지 않아 `Username for …` 프롬프트가 뜬다.
  - tty가 없으면(CC Bash 도구 형태) 어느 쪽이든 바로 실패한다.
- 수정안: 명령 전체를 `GIT_TERMINAL_PROMPT=0 git -c credential.interactive=never fetch --quiet`로 적는다. CHANGELOG가 인정한 SSH 대기는 `GIT_SSH_COMMAND="ssh -o BatchMode=yes"`로 막을 수 있다.

### 7. Suggestion — save Share의 조건 순서와 revert 근거
`src/superclaude/commands/save.md:23`, `tests/unit/test_session_memory_folder.py:145`
- 순서: detached HEAD와 merge/cherry-pick/revert 진행 중이라는 전제 조건이 `[y/n]` 질문 뒤에 적혀 있다. 글자 그대로 따르면 먼저 묻고 나서 거절하게 된다. 전제를 맨 앞에 두는 편이 낫다.
- revert 근거(`git2/`):
  - 테스트 주석은 "Git refuses a partial commit during a merge, cherry-pick or revert"라고 쓴다.
  - git 2.43은 merge와 cherry-pick에서만 거절한다("cannot do a partial commit during a …").
  - 충돌 난 revert 중에는 `git commit -m r -- r.md`가 exit 0으로 성공하고, `REVERT_HEAD`를 조용히 지운다(충돌 `UU`는 남는다).
  - 그래서 명령문의 revert 제외는 맞고 오히려 꼭 필요하다. 테스트 주석만 고치면 된다.
- rebase가 충돌로 멈춘 상태는 HEAD가 detached라서 기존 조건에 걸린다(`git branch --show-current`가 빈 값).

### 8. Suggestion — save Sync의 "installed sibling commands/sc/load.md"는 어느 scope인지 정하지 않는다
`src/superclaude/commands/save.md:13`
- 모델은 자기 명령 파일의 경로를 모른다. user, project, local 중 어디를 읽을지 추측해야 한다.
- 수정안: `~/.claude/commands/sc/load.md` 또는 `.claude/commands/sc/load.md`를 함께 적거나, Sync 단계 한 줄을 save에 그대로 둔다.

### 9. nit — load Load 단계의 문구
`src/superclaude/commands/load.md:14`
- "one Grep `^branch:` … reads only the first lines"는 사실이 아니다. Grep은 본문 중간의 `branch:`로 시작하는 줄도 찾는다.
- "read every one of the newest date, one per machine"는 "기계마다 가장 최근 기록"으로 잘못 읽힐 수 있다. 실제 규칙은 "가장 최근 날짜의 기록만"이다.
- host/branch 분리 규칙 자체는 맞다. host slug에는 `_`가 들어갈 수 없고 날짜 형식이 고정이므로, `branch:` 필터로 slug가 확정되면 앞뒤를 잘라 machine 부분이 하나로 정해진다. 옛 형식은 그 부분이 빈 값이 된다. `main`과 `fix_main`, `box_main`(옛 형식)과 `box`+`main`(새 형식)을 손으로 대조했다.

### 10. Suggestion — master에 끊어진 링크
`docs/features/session-memory-multi-machine/05-plan.md:140`, `06-review.md:40`
- `../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md`는 master에 없다. 머지되지 않은 `docs/review-reflect-gate-gap` 브랜치에만 있다(`git log --all`).
- 테스트는 이를 잡지 못한다. 수정안: 그 브랜치를 머지하거나 링크를 브랜치 이름으로 바꾼다.

### 11. nit — CHANGELOG Fixed가 과장하거나 빠뜨린 것
`CHANGELOG.md:18`
- 과장: "kill every process the command started"는 사실보다 넓다. `setsid`로 세션을 떠난 자손은 살아남고, 호출은 timeout+5초에 돌아온다(실측 6.01초, 코드 주석이 의도한 동작).
- 누락: 명령이 이제 별도 세션에서 돈다는 점(1번)을 적지 않았다.

### 12. nit — 프로브의 transcript 금지 정규식과 save 프로브의 host
`evals/tasks.yaml:1078`, `:1063`
- `\s(commit|push)\b`의 오탐: `# nothing to commit` 주석, `git config --get commit.gpgsign`, `pull.rebase`.
- 놓침: 줄 이음(`git \`↵`commit`).
- `cmd-save-host-record`는 실제 hostname을 확인하지 못하므로 `laptop`, `host-slug` 같은 임의 slug도 통과한다. 하네스에 동적 정규식이 없어 생긴 한계이니 주석에 적어 두면 된다.

### 13. Suggestion — POSIX에서 호출자들의 동작 테스트가 없다
`tests/unit/scripts/auto_improve/test_eval_runner.py:59`
- 호출자 세 파일을 v4.34.1로 되돌리면 테스트 7개가 빨개진다. 다만 mock 대상인 `run_shell` 이름이 사라져서이지 동작 때문이 아니다.
- `wall_seconds < 10`은 Linux의 옛 코드에서도 통과한다(실측 1 passed). POSIX에서 동작을 지키는 테스트는 `test_run_shell.py` 하나뿐이다. 받아들일 수는 있지만, 필요하면 호출자 테스트에 marker 생존 검사를 추가한다.

## 빌더 주장 판정

| 주장 | 판정 | 근거 |
|---|---|---|
| 전체 스위트 green, ruff/mypy clean | 확인(Linux) / 확인 불가(Windows 숫자) | `uv run pytest`: 3796 passed, 3 skipped, exit 0, 1분 51초. `ruff format --check src/ tests/`: 223 files 이미 정리됨. `make lint`, `ruff check src/ tests/`, `make typecheck`(54 files) 모두 통과. 05-plan의 3786과 메모리의 3787은 같은 코드(`b13591f4..HEAD`에 tests/src/evals 변경 없음)의 숫자인데 서로 다르다. Linux 합계 3799 = 3787+12. |
| 타임아웃 시 트리 전체를 죽이고 바로 돌아온다 | 확인(Linux) | 0.5초 타임아웃에 0.50초 만에 돌아왔고, exec/fork/중첩 셋 다 생존 0개(옛 코드는 3개 생존). 부분 출력은 `exc.stdout`에 담긴다. |
| 그 밖에는 `subprocess.run`과 같다 | 반박 | 차이 넷: (a) 새 세션이라 그룹 신호와 Ctrl-C가 닿지 않는다(1번). (b) 타임아웃이 아닌 예외에서 kill하지 않는다. (c) Windows에서 `exc.stdout`을 채우지 않는다(`run`은 두 번째 communicate로 채운다. 호출자는 쓰지 않음). (d) 떨어져 나간 자손이 있으면 최대 5초 더 걸린다. `raise exc`는 TimeoutExpired 계약(cmd, timeout)을 지킨다. 타임아웃 경로의 `Popen.__exit__`는 shell만 기다리므로 멈추지 않는다(실측). |
| CHANGELOG: POSIX에서 옛 코드는 돌아왔지만 명령이 남았다 | 확인 | 위 비교. dash는 단순 명령에도 fork하므로 Ubuntu에서는 항상 남았다. Windows 쪽 문장은 확인 불가. |
| Share: 그 파일들만 커밋하고, 다른 staged 파일은 staged로 남는다 | 확인 | `git1`: 커밋에 기록 1개만 들어갔고, `A  unrelated.txt`(staged)와 ` M a.txt`가 그대로 남았다. |
| Share: detached/merge/cherry-pick/revert에서는 제안하지 않는다 | 확인(문구) | merge와 cherry-pick은 git이 거절한다. revert는 git이 받아들이고 상태를 깨므로 제외가 필요하다(7번). |
| Share: 뒤처지지 않았을 때만, 그리고 diff가 메모리 파일뿐일 때만 push를 제안한다 | 확인 | 메모리 파일만 바뀐 경우 `'@{u}...HEAD'`는 기록 1개를 나열했다. 갈라진 경우 behind=1이고 diff는 `a.txt`를 나열했다. upstream이 없으면 exit 128이라 "commit only"로 간다. bash에서는 따옴표 없는 형태와 일부만 따옴표 친 형태도 동작한다. |
| Sync의 fetch가 자격 증명 프롬프트에서 멈추지 않는다 | 확인(접두 형태) | 6번. `-c credential.interactive=never`는 GCM용이라 Linux에서는 효과를 관찰할 수 없다. |
| `rev-list --count 'HEAD..@{u}'`가 behind 수를 준다 | 확인 | fetch 전 0, fetch 후 1. 갈라진 경우 `pull --ff-only`는 exit 128("Not possible to fast-forward")이다. |
| Load 단계의 host/branch 분리, 옛 형식 읽기 | 확인(분석) | 9번. 모델로 실행하지는 않았다(금지). |
| PowerShell: `'@{u}'`, `$env:GIT_TERMINAL_PROMPT=0` | 확인 불가 | 이 머신에 pwsh가 없다. 문서화된 파싱 규칙과는 맞는다. 일부만 따옴표 친 `HEAD..'@{u}'`도 테스트를 통과하지만, PowerShell은 맨 단어 뒤에 붙은 문자열을 인자 하나로 합치므로 문제없다. |
| 수정을 되돌리면 테스트가 실패한다 | 확인 | 아래 표. 13번의 한계가 있다. |
| canary-commands 4개 통과 | 확인 불가 | 보고서가 Windows 경로(`C:/sc-evals/smm-final2/`)에 있다. 이 검증에서는 실행 금지. 대신 세 프로브의 setup은 scratch에서 모두 성공했다. `cmd-load-sync-behind`는 fetch 전 0, 후 1이고 `cmd_ok`는 모두 0이었다. |

되돌림 결과(복원 후 매번 `git status --short` 0줄):

| 되돌린 것 | 빨개진 테스트 |
|---|---|
| `_kill_process_tree` 호출 → `pass` | `test_timeout_stops_the_command_tree` |
| 호출자 3개 → v4.34.1 | 7개(mock 이름 때문) |
| `project = tmp_path / "project"` | `test_sandbox_walk_stops_at_the_fake_home[user]`(user만, docstring대로) |
| save/load → v4.34.1 | 11개 |
| 커밋의 pathspec 제거 | share 테스트 |
| 따옴표 없는 `@{u}...HEAD` | `quoted[save-share]` |
| `credential.interactive` 제거 | sync 테스트 |
| Share를 Checkpoint 앞으로 | `share_runs_after…` |
| 프로브 3개 삭제 | `test_changed_command_probes…` |
| 일부만 따옴표 친 `HEAD..'@{u}'` | 통과(무해) |

## Canary 게이트

- `git diff v4.34.1 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`는 0줄이다. 따라서 `canary-gates` 게이트는 걸리지 않는다.
- `src/superclaude/commands/{load,save}.md`가 바뀌었으므로 `make release`는 command 게이트(Makefile:129)에서 멈춘다. `make canary-commands`로 cmd-delegated-load, cmd-load-other-host, cmd-load-sync-behind, cmd-save-host-record를 돌리고 보고서를 읽은 뒤 `CANARY_OK=1`로 다시 실행해야 한다. README `릴리스 뒤`의 설명과 일치한다.
- 4·5번 정규식을 고치면 canary를 다시 돌려야 한다.

## 범위 밖

- 빌더의 마지막 저장(4fd32d90)도 옛 이름(`session_2026-10-21_master.md`)을 썼다. 설치본이 아직 v4.34.1이기 때문이다. 두 컴퓨터 모두 `install --force`를 하기 전까지는 같은 파일 충돌이 계속된다(README 체크리스트 2번).
- 이 머신의 `$TMPDIR`도 실제 home 아래에 있다. pytest의 `tmp_path`가 실제 `~/.claude` 위쪽 경로에 놓이는 Windows와 같은 구조다. 이번 sandbox 수정과 decoy 테스트가 이 상황을 막는다. 실제 `~/.claude/superclaude`는 이 머신에 없어서 옛 배치로도 c05는 통과했고, decoy 테스트만 실패했다.
- `gh repo set-default`는 `ajitta/superclaude`로 정상이다.
- auto-improve.md의 shipped gotcha `cc-session-end`("an `--eval-cmd` already in flight breaks away")는 1번의 PID 단독 kill 결과와 일치한다. 이번 변경으로 그룹 kill로도 멈출 수 없게 되었다.

## 반영 (`fix/verify-1021`, 2026-10-21)

| # | 반영 |
|---|---|
| 1 | `run_shell`: 타임아웃이 아닌 예외(KeyboardInterrupt 포함)에서도 트리를 죽이고 다시 raise. 명령이 도는 동안 기본 처리기인 SIGTERM·SIGHUP을 SystemExit로 바꿔 같은 경로를 탄다(메인 스레드, POSIX, 호출자가 정한 처리기는 그대로). 테스트: 호출자 그룹에 SIGINT·SIGTERM·SIGHUP |
| 2 | `TEST_TIMEOUT_SECONDS = 110`. hooks.json 타임아웃보다 5초 이상 작아야 한다는 테스트 |
| 3 | 두 docstring을 실측대로(Windows는 기다림, POSIX는 돌아오고 명령이 남음) |
| 4 | 짝짓기 정규식이 사이에 세 줄까지 허용 |
| 5 | 굵은 숫자, `Behind: 1`, `origin … is 1 commit ahead` 통과, `not 1 commit behind`·`11 commits behind` 실패 |
| 6 | 변수를 fetch 명령 앞에 붙인 형태로 적고, 따로 쓴 `GIT_TERMINAL_PROMPT=0;`은 export되지 않는다고 적음. SSH `BatchMode`는 넣지 않음(소유자 결정 F7: `GIT_SSH_COMMAND`가 `core.sshCommand`를 덮음) |
| 7 | Share가 detached HEAD·merge·cherry-pick·revert를 질문보다 먼저 거른다. 테스트 주석을 git 2.43 동작대로 |
| 8 | `~/.claude/`(user) 또는 프로젝트 `.claude/`(project·local) 중 이 save.md와 같은 곳 |
| 9 | "각 기록의 첫 줄", "가장 최근 날짜를 가진 기록, 그보다 오래된 컴퓨터 기록은 읽지 않음" |
| 10 | 보류: 분석 문서가 든 `fix/review-reflect-gates`가 master에 들어올 때 해결된다 |
| 11 | CHANGELOG Fixed를 고치고 새 세션 동작·`kill -9` 한계·110 s를 한 항목으로 적음. auto-improve gotcha `cc-session-end`도 같은 사실로 |
| 12 | `commit.gpgsign`·`pull.rebase` 같은 설정 키는 금지 정규식에 걸리지 않음. 임의 host slug 통과는 주석에 적음. 세 프로브 채점 사례를 `test_eval_harness.py`에 고정 |
| 13 | 반영하지 않음: POSIX 동작은 `test_run_shell.py`(타임아웃 + 신호 3종)가 지킨다 |

되돌림 확인: `except BaseException` 제거 → 신호 테스트 3개 실패, 신호 처리기 제거 → SIGTERM·SIGHUP 2개 실패, 110 → 120 → 타임아웃 간격 테스트 실패, tasks.yaml·save.md·load.md를 반영 전으로 → 각각 10·1·2개 실패. 전체 suite 3825 passed, 3 skipped(Linux).
