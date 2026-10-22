---
status: complete
revised: 2026-10-22
---

# review·reflect가 빠진 원인과 후속 작업

2026-10-21 session-memory-multi-machine 작업에서 두 단계가 빠졌다. 반영한 수정 커밋은 다시 리뷰하지 않았고, `/sc:reflect`는 한 번도 돌지 않았다. 소유자가 원인을 물었고, 이 문서는 원인과 근거, 새 브랜치에서 할 후속 작업을 적는다. 후속 작업의 진행은 각 항목에 적었다.

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

### A. session-memory 기능 마무리 — 완료 (2026-10-21, master 085a6cab)

- [x] ec090829 독립 재리뷰. 4차까지 돌았다. 반영 커밋은 28d92471, 51d61fa4, b13591f4이고, 기록은 [06-review](../features/session-memory-multi-machine/06-review.md) 2–4차에 있다. 리뷰어에게는 이전 발견을 결함과 확인 방법으로만 주고, 고쳤다는 주장은 넣지 않았다. S-7–S-9는 결정으로만 전했다.
- [x] `/sc:reflect`로 기능 전체를 봤다. 판정은 "재리뷰 전에는 끝나지 않음"이었다. 계획 Deviations에 적었다.
- [x] 발견 반영과 Proof: b13591f4에서 전체 suite 3786 passed, 병합 직전 7bae5106에서 3787 passed. canary는 네 프로브가 모두 통과했다(`C:/sc-evals/smm-final2/report.md`, 이 컴퓨터). 계획은 `status: complete`, README는 `phase: complete`. master에 병합하고 push했다(085a6cab). 브랜치 `fix/session-memory-review`는 원격과 로컬에서 지웠다.
- [x] 낡은 범프 브랜치 `chore/version-4.34.2`는 지웠다.
- [ ] 릴리스: 소유자가 보류했다(2026-10-21 "release는 아직"). 할 때는 범프 브랜치를 새로 만들고, `CANARY_OK=1 make release` 뒤 두 컴퓨터에서 설치를 맞추고 두 컴퓨터로 확인한다(feature README `릴리스 뒤`). B를 같은 릴리스에 묶으면 canary를 한 번만 돌린다.

### B. 규칙과 문서 맞추기 — 결정됨 (2026-10-21), 완료: [review-reflect-gates](../features/review-reflect-gates/README.md)

소유자는 ★(a), 재리뷰 줄, canary 프로브를 골랐다. RULES_DOCS가 `/sc:test`에서 로드되지 않는 것(`context_loader.py:191`)을 확인한 뒤 `test.md` handoff의 (b)도 더했다. handoff만으로는 `/sc:test` 세션의 답이 바뀌지 않아(0/3), 소유자가 `test.md` Report 단계 한 줄을 더 골랐다(3/3). 리뷰 1차 뒤에는 `/sc:intent --through`가 한 번의 수정 round를 유지하는 예외를 게이트에 두기로 했다. 릴리스는 보류한다. 아래는 결정 전 선택지다. ★는 추천이었다.

- reflect를 어디에 둘지:
  - ★(a) RULES_DOCS `workflow_gates`에 `/sc:test -> /sc:reflect (Medium, Large)` 같은 게이트를 넣어 README 표와 맞춘다.
  - (b) `/sc:test`·`/sc:implement` handoff에 `/sc:reflect`를 더한다.
  - (c) README 표에서 reflect를 선택 단계로 내린다.
- 반영 뒤 재리뷰: `workflow_gates`에 "리뷰 뒤 shipped 내용을 바꾼 수정은 다시 리뷰한다"는 줄을 넣을지 정한다. 넣는다면 `/sc:review`의 재리뷰가 이전 발견을 수용 기준으로 받는다는 점도 같이 적는다.
- `core/`가 바뀌면 다음 릴리스는 `make canary-gates`가 필요하다(AGENTS.md). 이 실패를 막는 canary 프로브를 `evals/tasks.yaml`에 더할지도 정한다(AGENTS.md: 행동 실패를 기록한 gotcha·insight에는 프로브를 더한다).

### C. 메모리 고치기

- [x] auto memory `release-needs-complete-plan`에 "반영한 수정은 다시 리뷰한다, reflect는 체인의 단계다"를 더했다(2026-10-21). B의 결정이 나오면 그 규칙을 가리키게 한다.

### D. 계획 `complete`와 reflect의 순서 — 완료 (v4.34.2): [plan-complete-order](../features/plan-complete-order/README.md), 확정안 B′

`/sc:implement` Integrate 단계는 Proof가 통과하면 계획을 `status: complete`, feature README를 `phase: complete`로 만든다. 체인에서는 그 뒤에 `/sc:test`와 `/sc:reflect`가 온다. 그래서 reflect 전에 feature가 `complete`로 보인다. B 이전의 `/sc:test -> done`에서도 같았다(review-reflect-gates 리뷰 1차 I-5). `implement.md`, RULES_DOCS의 계획 status 규칙, `workflow_gates`가 `complete`의 위치에 대해 같은 말을 하게 할지는 소유자가 정한다.

재리뷰도 같은 순서 문제를 가진다(review-reflect-gates 06b 발견 5). 녹색 Proof가 `complete`를 정한 뒤에 리뷰 수정의 다음 round가 온다. 2차 round가 Critical을 찾아도 계획을 `implementing`으로 되돌리는 경로는 "a red re-run"뿐이다. `test-reflect-gate-complete` 프로브가 이 상태(파일은 complete, 일은 아직)를 잰다. D를 정할 때 그 프로브의 check도 함께 본다.

### E. 리뷰 발견과 그 수락의 기록 위치 — 설계 중: [review-findings-record](../features/review-findings-record/README.md)

소유자 결정(2026-10-22): 새 세션에서 설계안 round로 시작한다. 그 round에서는 `src/`를 바꾸지 않는다.

문제. `/sc:reflect` Plan-Close의 조건 (3)은 "every Critical or Important review finding is fixed or accepted by the user, and every fix to one that changed reviewed code or shipped content has had a /sc:review round after it, or the user waived that round"다(`reflect.md` 3.6). 판단하려면 네 가지가 필요하다. 리뷰가 낸 발견과 그 등급, 각 발견이 고쳐졌는지, 사용자가 고치지 않고 수락했는지, 수정의 재리뷰를 사용자가 면제했는지. 그런데 `/sc:review`는 파일을 쓰지 않는다(`review.md` `<outputs>`는 대화 안의 요약·조치·근거뿐이고, `<tools>`에 Write가 없다). 같은 세션에서는 대화에 남지만, `/sc:load`로 이어 가거나 다른 컴퓨터에서 이어 가면 사라진다. 그러면 reflect는 근거 없이 조건이 성립한다고 보거나, 판단하지 못해 계획이 `implementing`에 머문다. 수락과 면제도 마찬가지다. Proof의 수락은 `Result: … (accepted by user)`로 계획에 남지만, 리뷰 발견에는 그런 자리가 없다. 프로브가 쓰는 `06-review.md`(`evals/fixtures/test-reflect-gate`)는 fixture가 만든 파일이다. 이 저장소의 리뷰 기록(`06x-verify-*.md`)도 검증자에게 그렇게 쓰라고 시켰기 때문에 있다. 근거: [plan-complete-order 06e](../features/plan-complete-order/06e-verify-round6.md) "이 브랜치 밖"과 발견 2, [06h](../features/plan-complete-order/06h-verify-round9.md).

후보(설계에서 다시 잰다).

- (a) feature 폴더 작업이면 `/sc:review`가 `06-review.md`를 쓴다. round마다 절을 두고, 발견의 등급과 fixed / accepted / waived 상태를 적는다. 읽기 전용 명령의 계약이 바뀐다. 문서 규칙(RULES_DOCS 번호 문서, README Documents)과는 가장 자연스럽다.
- (b) `Result:` 줄처럼 계획에 리뷰 줄을 남긴다(예: `Review: <sha> — round 2, Critical 0, Important 0; accepted: F-3`). 변경이 작고 계획 하나만 보면 된다. 누가 쓰는지(review, implement, 사용자)를 정해야 한다.
- (c) 지금대로 두고, 기록이 없으면 Plan-Close가 조건 (3)을 사용자에게 묻는다. 가장 작지만 매번 질문이 생긴다.

새 세션에서 할 일(`superclaude-maintenance-round` skill → `references/proposal-audit.md` "Own design proposal for a follow-up item"):

1. `git fetch` 뒤 master에서 `docs/review-findings-record` 브랜치를 만든다. 설계 문서는 브랜치에 둔다(gotcha `plan-docs-on-branch`).
2. 이 정보의 reader와 writer를 전부 찾는다: `reflect.md` 3.6, `implement.md` Integrate(재리뷰 문장), `review.md` Process와 `<outputs>`, `test.md` Report, `intent.md` Run·Report(`--through`는 명령이 쓰는 것을 커밋한다), RULES_DOCS 문서 규칙과 `workflow_gates`, `self-review` agent의 `<finding_policy>`, 프로브(`reflect-plan-close*`, `test-reflect-gate*`, `intent-through-*`)와 그 fixture, `_GATE_ANCHORS`.
3. 앞선 결정을 이유별로 다시 잰다. `review.md`가 파일을 쓰지 않는 이유가 어디에 정해져 있는지(git log, docs/features의 리뷰 관련 결정), 10-20 약점 감사(`docs/research/superclaude-weakness-audit-ajitta-2026-10-20.md`), completion-proof의 `Result:` 선례, plan-complete-order 04·04a.
4. `docs/features/review-findings-record/04-design.md`(status: draft)에 안 A·B·C를 쓴다. 안마다 바뀌는 파일, `--through`와의 관계, 프로브, 릴리스 범주를 적는다. README(`phase: design`)도 만든다.
5. 설계안을 독립 검증한다(별도 worktree, headless `claude -p --model opus --effort high`, 한국어 보고서 `04a-design-verify.md`).
6. 소유자에게 결정 하나를 ★안과 함께 묻는다. 그 뒤 계획·빌드·리뷰 round·누더기 감사·병합 순서는 plan-complete-order와 같다. 릴리스는 소유자가 정한다.

## 확인 방법

- A: 재리뷰와 reflect 기록이 feature 폴더에 있고, 계획 `Result:`가 마지막 코드 커밋과 그 출력을 적는다.
- B: `workflow_gates`(또는 handoff)와 README 표가 reflect와 재리뷰에 대해 같은 말을 한다. 관련 테스트(`tests/unit/test_cross_references.py`, `tests/unit/test_command_structure.py`)와 전체 suite가 통과한다.
