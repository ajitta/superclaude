---
status: draft
revised: 2026-10-21
---

# review·reflect가 빠진 원인과 후속 작업

2026-10-21 session-memory-multi-machine 작업에서 두 단계가 빠졌다. 반영한 수정 커밋은 다시 리뷰하지 않았고, `/sc:reflect`는 한 번도 돌지 않았다. 소유자가 원인을 물었고, 이 문서는 원인과 근거, 새 브랜치에서 할 후속 작업을 적는다. 후속 작업은 아직 하지 않았다.

## 무엇이 빠졌나

- reflect: 기능 전체에 대해 `/sc:reflect`를 돌리지 않았다.
- review:
  - 첫 병합(9b625e2b)은 리뷰 없이 master에 들어갔다. 소유자가 버전 범프를 멈추게 한 뒤에야 `self-review` 에이전트로 병합 범위를 리뷰했다([06-review](../features/session-memory-multi-machine/06-review.md)). `/sc:review --scope branch` 명령이 아니라 에이전트를 직접 불렀다.
  - 리뷰 발견을 반영한 수정 커밋 ec090829는 shipped 명령 본문을 크게 바꿨다(Share를 마지막 단계로, 새 git 명령, 새 프로브). 그런데 다시 리뷰하지 않고 Proof(테스트·canary)로 바로 갔다.

## 원인과 근거

1. README와 RULES_DOCS의 단계가 서로 다르다.
   - README 작업 크기 표: Medium은 `/sc:plan` → `/sc:implement --plan` → `/sc:test` → `/sc:reflect`이고 branch review는 선택이다. Large는 `/sc:review --scope branch`와 `/sc:reflect`를 모두 포함한다(`README.md:297-298`).
   - RULES_DOCS `workflow_gates`는 `/sc:implement -> /sc:review --scope branch (Large; optional for Medium) | /sc:test`와 `/sc:test -> done`에서 끝난다(`src/superclaude/core/rules/RULES_DOCS.md:85-86`). reflect는 게이트에 없다.
   - 세션에 주입되는 것은 RULES_DOCS뿐이고 README는 문맥에 없다. 그래서 "끝났다"의 기준에 reflect가 들어오지 않았다.
   - 이 변경은 파일 약 8개(save.md, load.md, 테스트 2개, tasks.yaml, CHANGELOG, 문서)라 Medium이고, README 기준으로는 reflect가 필요했다.
2. 명령 handoff도 reflect를 가리키지 않는다. `implement.md:56`은 `next="/sc:review /sc:test /sc:build"`, `test.md:73`은 `next="/sc:troubleshoot /sc:implement"`다.
3. `/sc:reflect` 설명은 "Use when asked whether a task is truly done"이라, 묻지 않으면 모델이 시작하지 않는다.
4. 계획을 명령 없이 손으로 실행했다. `/sc:implement --plan`·`/sc:test`·`/sc:reflect`를 쓰지 않고 pytest와 canary를 직접 돌렸다. 그래서 명령 본문의 단계와 handoff가 작동할 기회가 없었다.
5. 직접 쓴 계획이 재리뷰를 빼먹었다. Phase 4 상자는 "발견을 반영한 커밋 뒤 Proof 1–3을 다시 돌린다"로, 리뷰 → 반영 → Proof만 정했다. 반영한 수정을 다시 보는 단계는 없다. `workflow_gates`도 반영 뒤 재리뷰를 요구하지 않는다.
6. 같은 날 기록한 피드백 메모리 `release-needs-complete-plan`(auto memory)도 리뷰 게이트를 한 번 통과하면 된다고 적었다. 같은 빈틈이다.

## 후속 작업

### A. session-memory 기능 마무리 (기존 브랜치 `fix/session-memory-review`)

- 상태:
  - 리뷰 반영 커밋은 ec090829, 리뷰 기록은 fbd7aaa6. 둘 다 master에 병합되지 않았고 push도 안 됐다.
  - 이 브랜치에서 전체 suite 3786 passed / 12 skipped, ruff·mypy clean.
  - `make canary-commands`는 네 프로브가 모두 통과했다: cmd-delegated-load 1/1, cmd-load-other-host 3/3, cmd-load-sync-behind 4/4, cmd-save-host-record 3/3. 보고서는 `C:/sc-evals/smm-review/report.md`(이 컴퓨터).
  - 계획은 `status: implementing`이다. Phase 4 리뷰 상자와 `Result:`는 아직 고치지 않았다.
- [ ] ec090829 독립 재리뷰.
  - 리뷰어에게는 06-review.md의 I-1–I-6, S-1–S-6, N-1–N-2를 수용 기준으로 준다. 각 항목은 결함과 그것이 없어졌음을 보이는 검사로 적고, 고쳤다는 주장은 넣지 않는다(RULES_DELEGATION `delegate_packet`).
  - S-7–S-9는 고치지 않기로 한 결정으로만 전한다.
- [ ] `/sc:reflect`로 기능 전체(cd7b4358..브랜치 끝)를 본다.
- [ ] 발견을 반영하고 Proof를 다시 돈다. 그 뒤 계획 `Result:`, `status: complete`, README `phase: complete`. 그다음 master 병합과 push.
- [ ] 릴리스 여부는 소유자가 정한다. 낡은 범프 브랜치 `chore/version-4.34.2`(로컬, 리뷰 반영 전)는 지우고 다시 만든다.

### B. 규칙과 문서 맞추기 (새 브랜치, 예: `fix/review-reflect-gates`)

결정이 필요하다. ★는 추천.

- reflect를 어디에 둘지:
  - ★(a) RULES_DOCS `workflow_gates`에 `/sc:test -> /sc:reflect (Medium, Large)` 같은 게이트를 넣어 README 표와 맞춘다.
  - (b) `/sc:test`·`/sc:implement` handoff에 `/sc:reflect`를 더한다.
  - (c) README 표에서 reflect를 선택 단계로 내린다.
- 반영 뒤 재리뷰: `workflow_gates`에 "리뷰 뒤 shipped 내용을 바꾼 수정은 다시 리뷰한다"는 줄을 넣을지 정한다. 넣는다면 `/sc:review`의 재리뷰가 이전 발견을 수용 기준으로 받는다는 점도 같이 적는다.
- `core/`가 바뀌면 다음 릴리스는 `make canary-gates`가 필요하다(AGENTS.md). 이 실패를 막는 canary 프로브를 `evals/tasks.yaml`에 더할지도 정한다(AGENTS.md: 행동 실패를 기록한 gotcha·insight에는 프로브를 더한다).

### C. 메모리 고치기

- [ ] auto memory `release-needs-complete-plan`에 "반영한 수정은 다시 리뷰한다, reflect는 체인의 단계다"를 더한다. B의 결정이 나오면 그 규칙을 가리키게 한다.

## 확인 방법

- A: 재리뷰와 reflect 기록이 feature 폴더에 있고, 계획 `Result:`가 마지막 코드 커밋과 그 출력을 적는다.
- B: `workflow_gates`(또는 handoff)와 README 표가 reflect와 재리뷰에 대해 같은 말을 한다. 관련 테스트(`tests/unit/test_cross_references.py`, `tests/unit/test_command_structure.py`)와 전체 suite가 통과한다.
