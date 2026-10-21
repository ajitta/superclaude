---
status: complete
revised: 2026-10-21
---

# 독립 리뷰와 반영 (2026-10-21)

- 대상: master에 병합된 범위 cd7b4358..9b625e2b (`src/`, `tests/`, `evals/`, `CHANGELOG.md`).
- 리뷰어: `self-review` 에이전트. 받은 것은 소유자 요청 원문, 결정, 수용 기준, diff였다. 작성자 판정(`Result:`, Deviations, 커밋 설명의 통과 주장)은 프롬프트에 넣지 않았다. 리뷰어는 실행 도구가 없어 테스트를 돌리지 않았다.
- 결과: Critical 0, Important 6, Suggestion 9, nit 2. 반영 브랜치는 `fix/session-memory-review`.
- 검증: 인용된 줄은 모두 다시 읽어 확인했다. I-3은 이 컴퓨터 PowerShell에서 재현했다. 따옴표 없는 `@{u}`는 "해시 리터럴의 키 뒤에 '=' 연산자가 없습니다"로 파싱부터 실패하고, `'@{u}'`는 git의 정상 오류("no upstream configured")를 낸다.

## 반영

| ID | 내용 | 반영 |
|---|---|---|
| I-1 | Share의 커밋이 이미 stage된 다른 파일까지 담을 수 있다 | `git add -- <files>` 후 `git commit -m … -- <files>`로 고정. 테스트: `-- <files>`, "only those files" |
| I-2 | Share가 Checkpoint·Validate·Session Goal보다 앞에 있다 | Share를 마지막(9) 단계로. 테스트: 최상위 마지막 단계가 Share |
| I-3 | PowerShell에서 `@{u}`가 파싱 오류 → "no upstream"처럼 보이고 Sync를 건너뜀 | load Sync와 save Share의 모든 `@{u}`를 따옴표로. 테스트: 따옴표 없는 `@{u}` 금지 |
| I-3b | save Sync가 가리키는 load 단계가 문맥에 없을 수 있다 | 설치 경로 `commands/sc/load.md`를 적고, 문맥에 없으면 Read. 테스트 |
| I-4 | fetch가 자격 증명 프롬프트에서 멈출 수 있다 | `GIT_TERMINAL_PROMPT=0`(PowerShell 표기 포함), `-c credential.interactive=never`. 테스트 |
| I-5 | "다른 컴퓨터 기록은 고치지 않음"을 지키는 테스트가 없다 | 단위 테스트로 문장을 고정. headless에서는 `.claude/` Write가 거부되므로 프로브 검사는 셸로 쓴 경우만 잡는다고 tasks.yaml 주석에 적음 |
| I-6 | load 프로브가 옛 내용에서도 통과하고, 기록과 컴퓨터를 짝지어 말하는지 보지 않는다. upstream이 있는 Sync 경로를 아무 프로브도 돌리지 않는다 | `otherbox`가 자기 표지(`OTHER-TASK-9083`) 근처에 나와야 통과. 새 프로브 `cmd-load-sync-behind`: origin이 한 커밋 앞섬 → fetch, behind를 말함, pull 없음, HEAD 그대로 |
| S-1, S-2 | 브랜치 slug에 `_`가 있으면 컴퓨터·브랜치를 잘못 읽음. fallback도 파일 이름에서 브랜치를 읽음 | 기록의 `branch:` 첫 줄로 브랜치를 확인하고 fallback도 그 줄을 따른다. 테스트 |
| S-3 | detached HEAD나 upstream 없음에서 Share가 커밋·push를 제안 | detached HEAD → 커밋 제안 없음. push는 upstream이 있고 뒤처지지 않았을 때만 |
| S-4 | 갈라진 브랜치에서 pull이 멈출 때 안내가 없고, save가 거절될 push를 제안 | `git pull --rebase`를 이름만 알려 준다(실행하지 않음). 뒤처졌으면 push 제안 없음 |
| S-5 | "push 안 된 커밋이 메모리 파일만"을 셀 명령이 없음(병합 커밋은 `log --name-only`에 파일이 안 나옴) | `git diff --name-only '@{u}'...HEAD` |
| S-6 | Share 테스트가 약함 | `[y/n]` 두 번, "only those files", `-- <files>` 검사 |
| N-1 | `<tools>` Bash 줄이 쓰는 명령을 다 적지 않음 | `hostname`, 읽기 전용 git(branch, rev-parse, rev-list, diff) 추가 |
| N-2 | CHANGELOG: "두 번째 push 충돌"은 부정확, "현재 브랜치" 빠짐 | "두 번째 push는 거절되고 pull에서 병합 충돌", "현재 브랜치의", 커밋 범위와 비밀번호 묻는 원격 문구 추가 |

## 반영하지 않음 (계획 Risks로)

- S-7: 같은 hostname을 쓰는 두 컴퓨터(`localhost`, 같은 PC의 WSL과 Windows가 각자 체크아웃할 때, 한 컴퓨터의 두 clone), 다시 만들 때마다 hostname이 바뀌는 컨테이너, 네트워크에 따라 `hostname`이 바뀌는 macOS. 소유자가 "hostname 그대로"를 골랐고, 다른 라벨은 고르지 않은 안이다.
- S-8: "가장 최근 날짜"만 읽으므로 어제 다른 컴퓨터가 남긴 Next actions는 오늘 기록이 있으면 안 보인다. 시간대가 다르면 더하다. 수용 기준대로다.
- S-9: `.claude/`를 gitignore한 프로젝트, pre-commit hook이나 서명 프롬프트, commitlint와 맞지 않는 `docs:` 접두사. 커밋은 `[y/n]`을 거치므로 실패해도 사용자가 본다.

## 2차: 반영 커밋 ec090829 재리뷰

- 왜: 첫 반영이 shipped 명령 본문을 크게 바꿨는데 다시 리뷰하지 않았다. 원인은 [review-reflect-gate-gap 분석](../../analysis/review-reflect-gate-gap-ajitta-2026-10-21.md)에 있다.
- 방식: 같은 `self-review` 에이전트를 새로 띄웠다. 1차 발견 I-1–I-6, S-1–S-6, N-1–N-2를 수용 기준 C1–C11로 넘겼다(결함과 확인 방법만, 고쳤다는 주장 없이). S-7–S-9는 "고치지 않기로 함"으로만 넘겼다.
- 결과: C1, C2, C4, C5, C6, C8 PASS. C3, C7, C9, C10, C11 PARTIAL. 발견 F1–F14(Important 5, Suggestion 8, nit 1).
- 검증: F1은 이 컴퓨터 PowerShell에서 재현했다. `'@{u}'...HEAD`는 인자 둘로 갈라져 git 사용법 오류(exit 129)가 나고, `'@{u}...HEAD'`는 exit 0이다. F3은 셋업을 고친 뒤 확인했다. fetch 전 behind 0, fetch 후 1이다.
- 반영 커밋: 28d92471.

| ID | 내용 | 반영 |
|---|---|---|
| F1 | Share의 `'@{u}'...HEAD`가 PowerShell에서 깨짐 | `'@{u}...HEAD'` |
| F2 | 따옴표 검사가 `HEAD..@{u}`와 `'@{u}'...HEAD`를 놓침 | 모든 `@{u}`가 작은따옴표 인자 하나 안에 있어야 함 |
| F3 | 셋업의 push가 추적 ref를 이미 올려, fetch 없이도 behind가 보임 | push 뒤 `git update-ref refs/remotes/origin/main baseline` |
| F4 | load 프로브가 파일 이름 `_otherbox_main`만으로 통과 | 그 형태를 빼고 같은 줄에서 짝지어야 통과 |
| F5 | `-- <files>` 검사가 `git add`만으로 통과 | pathspec이 `git commit`에 붙어 있어야 함 |
| F6 | `branch:` 줄 검사가 한 곳만 남아도 통과 | 본 경로와 fallback 둘 다, 그리고 날짜 고르기보다 먼저 |
| F7 | SSH 프롬프트는 막지 못함 | 명령은 그대로 둔다(`GIT_SSH_COMMAND`는 사용자의 `core.sshCommand`를 덮는다). CHANGELOG를 HTTPS로 좁히고 SSH 예외를 적음 |
| F8 | `<tools>`에서 status·add·branch가 빠짐 | 추가 |
| F9 | 병합 중에는 부분 커밋이 실패 | merge in progress → 커밋 제안 없음 |
| F10 | CHANGELOG "up to date"가 부정확 | "not behind its upstream", detached HEAD·병합·diverged 문구 |
| F11 | 날짜를 먼저 고르면 다른 브랜치 파일이 현재 브랜치 기록을 가림 | `branch:` 줄로 먼저 거르고 날짜를 고름 |
| F12 | `behind` 정규식이 "not behind"에도 맞음 | 개수 `1`과 함께 |
| F13 | `git -c … pull/commit`이 금지 정규식을 빠져나감 | `git -c <key>=<value> <verb>` 형태도 잡는 정규식 |
| F14 | 프롬프트 끄기 토큰 검사가 한쪽 형태만 봐도 통과 | 두 형태와 `credential.interactive=never`를 각각 검사 |

## 3차: 28d92471 범위 재확인

- 같은 리뷰어에게 F1–F14를 수용 기준으로 다시 맡겼다. 11개는 없어졌고, F4·F7·F9는 작아졌다. 28d92471에서 새 결함 N1–N4가 나왔다.
- 반영:
  - F9: 커밋 제안 없음을 병합만이 아니라 cherry-pick·revert 진행 중으로 넓혔다(git이 부분 커밋을 거부한다).
  - F7: CHANGELOG에 SSH의 낯선 host key 확인도 셸 시간 초과까지 기다릴 수 있다고 적었다.
  - N1: load 프로브가 머리줄 아래 다음 줄에 짝을 둔 올바른 답도 통과하게 했다(한 줄바꿈 허용, 대소문자 무시).
  - N2: behind 검사가 "one"과 점이 든 경로를 받게 했다.
  - N3: 브랜치를 거를 때 `^branch:`를 Grep으로 한 번에 읽어 기록 전체를 Read하지 않게 했다.
  - N4: "which machine wrote each"로 단수·복수를 맞췄다.
- 남긴 한계: 정규식 프로브는 같은 창 안에서 짝이 뒤바뀐 답과 올바른 답을 구별하지 못한다(F4 나머지). tasks.yaml 주석에 적었다.
