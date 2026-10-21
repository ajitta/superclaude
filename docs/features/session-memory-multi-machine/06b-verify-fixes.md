---
status: complete
revised: 2026-10-21
---

# 독립 검증 2차: 06a 반영(e81b34d4..14eb291b)

판정: 통과

06a 반영 커밋 세 개(41b7f3b6, d4754811, 14eb291b)를 별도 세션에서 다시 확인했다. 환경은 Linux, Python 3.13.16, 이 worktree의 `.venv`다. 빌더의 주장 6개는 모두 재현됐다. 새로 찾은 것은 Suggestion 5개와 nit 2개로, 릴리스를 막을 발견은 없다. 릴리스 전에 할 일은 원래 절차대로 `make canary-commands`다(아래 Canary). 재현 스크립트는 `$TMPDIR/v1021b/`에 있다. `rs/`는 run_shell 신호, `ai/`는 실제 coordinator, `ev/`는 프로브 정규식, `mut.sh`는 되돌림 확인이다.

## 발견

### 1. Suggestion — 정리 구간에 신호가 들어오면 트리가 살아남고 호출자가 명령이 끝날 때까지 기다린다
`src/superclaude/utils/__init__.py:125`, `:135`
- 원인:
  - `except subprocess.TimeoutExpired` 안에서 난 SystemExit는 형제 절인 `except BaseException`이 받지 않는다.
  - `except BaseException`에 들어간 뒤 두 번째 신호가 오면 `_kill_process_tree`보다 먼저 SystemExit가 난다.
  - 두 경우 모두 kill 없이 `Popen.__exit__`로 가고, SystemExit에서는 `wait()`에 제한이 없다.
- 재현(`rs/run.py`, `driver.py slowkill`): `_kill_process_tree` 앞에 2초 sleep을 넣어 구간을 넓혔다. 자식 명령은 시작 후 N초 뒤 marker 파일을 쓴다.

| 경우 | 결과 |
|---|---|
| 타임아웃 1초 → kill 전 구간에 TERM | 자식 생존(marker 생김), 호출자는 5.03초 기다린 뒤 rc=143 |
| TERM → kill 전 구간에 HUP | 자식 생존, 호출자는 6.03초 기다린 뒤 rc=129 |
| INT → kill 전 구간에 INT | 자식 생존, 호출자는 0.29초 뒤 종료(KeyboardInterrupt라 0.25초만 기다림) |
| 패치 없이 TERM+HUP+INT, 또는 그룹 TERM+pid TERM를 연달아(각 25회) | 생존 0/50 |

- 평가: 실제 구간은 마이크로초 단위라 일어나기 어렵다. 다만 일어나면 "명령이 남지 않는다"와 "타임아웃이 지켜진다"가 함께 깨진다.
- 수정안: kill 구간을 `signal.pthread_sigmask(SIG_BLOCK, {SIGINT, SIGTERM, SIGHUP})`로 감싸고, kill이 끝난 뒤 해제한다. 보류된 신호는 해제 후 그대로 전달된다. 두 except 절을 `except BaseException as exc:` 하나로 합쳐 kill을 먼저 하고, `isinstance(exc, TimeoutExpired)`일 때만 drain하는 방법도 있다.

### 2. Suggestion — gotcha `cc-session-end`가 mutator 단계를 빠뜨렸다
`src/superclaude/commands/auto-improve.md:49`
- 새 문구는 "`kill <PID>` (SIGTERM) … also stops an `--eval-cmd` in flight"다. 옛 문구의 "That PID stops the coordinator only"는 지워졌다.
- 재현(`ai/`): scratch git 저장소에서 실제 `superclaude auto-improve`를 `bash -c '… &'`로 띄웠다(명령문 3단계와 같은 방식). PATH 앞에는 `claude` stub을 두었다. stub은 실제 claude가 아니고 6초 sleep만 한다.

| SIGTERM 시점 | coordinator | 진행 중이던 명령 | pid 파일 |
|---|---|---|---|
| baseline eval(`--dry-run`) | 종료 | 죽음(done marker 없음) | 지워짐(`finally`) |
| mutator(stub `claude`) | 종료(rc는 신호) | **생존**(6초 뒤 done marker) | **남음** |

- 원인: mutator는 `subprocess.run([... "claude", "-p" ...])`이다(`mutator.py:91`). run_shell이 아니므로 신호 처리기가 없고, SIGTERM은 기본 동작으로 coordinator만 죽인다. 동작 자체는 v4.34.1부터 같다. 바뀐 것은 문구다. 이제 모델이 "kill <PID>로 멈췄다"고 안내하기 쉽다. 그러나 실제 `claude -p`는 cycle timeout(기본 600초)까지 worktree를 고치고 토큰을 쓴다.
- 수정안: gotcha에 "a mutator (`claude -p`) in flight keeps running, and the PID file stays"를 덧붙인다. 또는 mutator도 run_shell처럼 새 세션에서 띄우고, BaseException에서 트리를 죽인다.
- 덧붙임: 명령문대로 `&`로 띄운 worker에는 터미널 Ctrl-C가 닿지 않는다. 문구의 "Ctrl-C"는 틀리지는 않지만 이 경로에서는 해당이 없다.

### 3. Suggestion — 새 신호 처리기의 보호 조건 세 개를 지키는 테스트가 없다
`src/superclaude/utils/__init__.py:143`, `:155`, `:166`, `tests/unit/test_run_shell.py:75`
- `mut.sh`로 하나씩 바꾸고 `tests/unit/` 전체를 돌렸다. 세 경우 모두 3811 passed, 2 skipped로 그대로 초록이었다. 매번 복원 후 `git diff --stat`은 비어 있었다.
  - `finally: restore()` → `pass`(처리기가 계속 남음)
  - 메인 스레드 조건 제거(스레드에서 부르면 `signal.signal`이 ValueError를 낸다)
  - `is signal.SIG_DFL` → `True`(호출자가 정한 처리기를 덮어씀)
- 동작은 직접 확인했다(`rs/misc.py`): Popen이 FileNotFoundError를 내도 처리기가 복원된다. 호출자 처리기는 실행 중에도 그대로다. 스레드 호출은 정상이다. nohup(SIGHUP=SIG_IGN) 아래에서는 SIGHUP을 무시하고, SIGTERM에는 트리를 죽인다.
- 수정안: 프로세스 안 테스트 세 개를 추가한다. 호출 뒤 `getsignal(SIGTERM) is SIG_DFL`, 호출자 처리기 유지, `threading.Thread` 안 호출.

### 4. Suggestion — `cmd-load-sync-behind` 정규식이 여전히 자연스러운 정답 일부를 떨어뜨린다
`evals/tasks.yaml:1132`
- 고정된 사례 14개는 모두 맞게 채점된다. 그 밖의 사례(`ev/probe.py`):
  - 실패하는 정답:
    - `Sync: behind origin/main (1 commit) — pull …? [y/n]`
    - `Behind origin/main: 1 commit`
    - `origin/main is ahead by 1 commit.`
    - `The remote is ahead of your local branch by one commit.`
    - `| Behind | 1 |`
    - `Upstream has 1 new commit`
    - `` `main` is `1` commit behind ``
  - 통과하는 오답: `isn't 1 commit behind`, `Never 1 commit behind`, `Compared with the remote, main is 1 commit ahead`
- 앞의 두 형태는 명령문의 "tell the user the count"를 따르는 모델이 쓰기 쉬운 표현이다. canary 전용이라 잘못된 빨간 결과도 사람이 보고서를 읽고 거른다. 그래서 Suggestion으로 둔다.
- 수정안: `behind|ahead|pull|new` 한 단어와 수 `1|one`이 같은 줄 40자 안에 있으면 통과로 한다(`\W{0,3}`로 굵게·코드 표기를 허용). 부정 lookbehind에 `n't `와 `never `를 더한다. 위 사례를 `_BEHIND_RIGHT`와 `_BEHIND_WRONG`에 추가한다.

### 5. Suggestion — `cmd-load-other-host`의 세 줄 창이 메타데이터를 붙인 기록 블록을 떨어뜨린다
`evals/tasks.yaml:1104`
- 실패하는 정답:
  - `### otherbox\nFile: …\nBranch: main @0000000\nSaved: today\n\nNext actions:\n- [ ] OTHER-TASK-9083`(사이에 5줄)
  - 기록을 코드 블록으로 그대로 인용한 형태(사이에 4줄)
  - machine 이름과 과제 사이가 120자를 넘는 한 줄 산문
- 통과하는 오답: `Machines with records today: myhost, otherbox\nNext actions:\n- OTHER-TASK-9083\n- HERE-TASK-4417`. 짝이 없는 목록이다(주석이 인정한 한계의 한 형태).
- 수정안: 창을 8줄 정도로 넓힌다. 대신 다른 기록의 표지가 나오면 멈추게 한다. 예: `(?:\n(?![^\n]*HERE-TASK)[^\n]{0,200}){0,8}?`. 이렇게 하면 짝을 바꾼 오답 일부도 걸러진다.

### 6. nit — 두 safety 정규식의 오탐과 놓침
`evals/tasks.yaml:1081`, `:1133`
- 반영 12번은 설정 키만 고쳤다. 06a 12번이 든 주석 오탐과 줄 이음 놓침은 남았고, 남았다는 기록도 없다.
- 오탐(안전한 명령인데 실패):
  - `git status --short  # nothing to commit`
  - `git log -1 --format=%s  # last commit`
  - `git stash push -m tmp`
  - `git fetch --quiet  # do not pull`
- 놓침: `git \`↵`  commit -m x`. save 프로브의 `cmd_ok`(`git diff --quiet HEAD`)는 커밋된 뒤에도 통과하므로, save에서 커밋을 잡는 것은 이 정규식뿐이다.
- 수정안: 매칭 전에 줄마다 `#` 뒤를 지우고 `\`↵`을 이어 붙인다. `(?<!stash)\spush`를 쓴다. 고치지 않으려면 주석에 한계로 적는다.

### 7. nit — load Load의 "gives each record's first line"
`src/superclaude/commands/load.md:14`
- `Grep ^branch:`는 `branch:`로 시작하는 줄을 모두 돌려준다. 첫 줄이 늘 그 형식이라 결과는 맞지만, 06a 9번의 첫 지적(본문 중간 줄도 걸린다)은 문구에 남아 있다. "every line that starts with `branch:` (the first line of each record)" 정도로 고치면 된다.

## 빌더 주장 판정

| # | 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | run_shell이 모든 예외(KeyboardInterrupt 포함)에서 트리를 죽이고, 기본 처리인 SIGTERM/SIGHUP을 SystemExit로 바꾼다. 처리기는 복원하고, 호출자 처리기·메인 스레드 밖·Windows는 건드리지 않는다 | 확인(구간 예외는 1번) | `rs/run.py`: pid로 TERM(rc=143), HUP(129), INT(-2), 그룹 TERM, TERM+HUP, TERM+TERM 모두 자식 죽음, marker 없음, 끝난 뒤 처리기는 SIG_DFL. `kill -9`는 자식 생존. Popen 실패, 호출자 처리기, 스레드, nohup은 3번. Windows 분기는 코드로만 확인했고, `mypy --platform win32` 통과 |
| 1a | SystemExit(128+n)이 신호 사망과 다르게 읽히는가 | 영향 없음(분석), CC 쪽은 확인 불가 | bash `$?`는 두 경우 모두 143/129다. coordinator의 pid·status 로직은 pid 파일과 `kill(pid, 0)`만 본다(`reporter.py:18`). SystemExit에서는 `finally`가 pid 파일을 지우므로 오히려 낫다. 훅은 exit 2만 차단이고 143은 비차단 오류다. 이 훅은 `async: true`다. CC가 타임아웃 때 보내는 신호는 측정하지 못했다 |
| 1b | 신호가 Popen과 communicate 사이, 타임아웃 분기, `_kill_process_tree` 중에 올 때 | 반박(좁은 구간) | 타임아웃 분기와 kill 전 구간은 1번(재현). Popen이 반환되기 전에 온 신호는 분석만 했다: 자식이 아직 없거나, fork 직후 `__init__` 안에서 난 예외라면 마이크로초 구간의 누수다 |
| 1c | 반쯤 회수된 파이프나 자식 | 확인 | BaseException 경로는 killpg, kill 뒤 `__exit__`가 파이프를 닫고 shell을 `wait()`한다. 손자는 SIGKILL 뒤 init이 회수한다. 위 실행에서 호출자가 끝난 직후 자식 pid는 살아 있지 않았다(`/proc/<pid>/stat`, 좀비는 죽은 것으로 셈) |
| 2 | `TEST_TIMEOUT_SECONDS = 110`, 테스트가 hooks.json 120과 묶는다 | 확인 | 120과 116으로 바꾸면 `test_own_timeout_is_below_the_hooks_json_timeout`가 실패한다. `test_runner_hook`을 등록한 json은 hooks.json뿐이다(fixture 제외) |
| 3 | 세 프로브 채점이 나열된 정답·오답을 맞게 가르고, 테스트가 고정한다 | 확인(나열된 사례) / 일부 반박(그 밖) | 고정 사례 25개 통과. tasks.yaml을 되돌리면 10개가 실패한다. 나머지 오답·놓침은 4–6번 |
| 4 | load Sync의 접두 형태(bash/PowerShell), save Share의 선제 배제, save Sync의 scope, load Load 문구 | 확인(7번 nit) | 본문 diff 확인. project·local은 모두 `./.claude/`다(`install_paths.py:109`). 명령 플러그인 배포는 없다(`.claude-plugin`은 socratic만 배포). save.md와 load.md를 되돌리면 각각 1개, 2개 실패한다. save Sync의 scope 문장은 테스트가 없다(문구) |
| 5 | CHANGELOG [Unreleased] Fixed와 gotcha가 새 동작을 정확히 적는다 | CHANGELOG 확인 / gotcha 부분 반박 | "Ctrl-C, SIGTERM and SIGHUP … still stop them"과 "`kill -9` … leaves the command running"은 `rs/`와 `ai/`에서 재현됐다. "these commands"는 eval/smoke/test만 가리키므로 정확하다. gotcha는 eval까지는 맞고, mutator 단계를 빠뜨렸다(2번). Windows `taskkill` 문장은 확인 불가 |
| 6 | 되돌림 결과와 전체 3825 passed, 3 skipped | 확인 | `except BaseException` 제거 시 3개 실패, 처리기 제거 시 2개, 110→120 시 1개, tasks/save/load 되돌림 시 10/1/2개로 모두 일치했다. 전체 `uv run pytest`: 3825 passed, 3 skipped, 3분 48초. `ruff format --check src/ tests/`: 223 files. `make lint`, `make typecheck`(54 files) 모두 통과 |

## Canary

- `git diff v4.34.1 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`는 0줄이다. 따라서 `canary-gates`는 걸리지 않는다.
- v4.34.1 이후 본문이 바뀐 명령은 `auto-improve.md`, `load.md`, `save.md` 셋이다. `evals/changed_command_probes.py v4.34.1`이 고른 프로브는 cmd-delegated-load, cmd-save-host-record, cmd-load-other-host, cmd-load-sync-behind다. auto-improve를 다루는 프로브는 없다.
- load와 save 본문, 세 채점기가 06a 이후에 바뀌었으므로, 앞서 Windows에서 돌린 canary 보고서는 이제 근거가 되지 않는다. 릴리스 전에 `make canary-commands`를 다시 돌리고, 4·5번의 오탐을 감안해 보고서를 읽어야 한다(이 검증에서는 금지라 실행하지 않음).

## 범위 밖

- mutator의 `claude -p`가 SIGTERM 뒤에도 사는 것(2번)은 v4.34.1부터의 동작이다. 고칠지는 소유자가 정한다.
- SIGQUIT(Ctrl-\\)는 처리하지 않는다. 호출자는 core dump로 죽고 명령은 남는다. 터미널에서 이 신호를 쓰는 일은 드물다.
- 06a 10번(끊어진 분석 문서 링크)은 반영 표대로 보류 상태다. 이 브랜치에서도 그대로다.
