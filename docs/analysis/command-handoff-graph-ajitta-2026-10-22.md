---
status: complete
revised: 2026-10-22
---

# `/sc:*` 명령 핸드오프 그래프와 구멍

**지금 상태(5b28dd7e 이후):** G1의 Proof 꼬리말, G2, G3의 review → design 핸드오프, G5는 해결됐다. G1의 `Evidence:` 규칙, G3의 체인 기준(D2), G4, G6–G10은 열려 있다. 열린 항목 중 관찰된 실패가 있는 것은 없다. 처리 내용은 끝의 "검토 반영"과 "구현과 측정"에 있다. 아래 판정과 각 절은 d7f04869 시점에 쓴 기록이다.

**판정: 실제로 쓰인 경로는 맞물리고, 구멍은 쓰이지 않은 두 영역에 몰려 있다.** plan 이후의 문서 계약(implement가 `Result:`를 쓰고 reflect가 확인)과 brainstorm → review → plan 관문은 이 저장소에서 실제로 작동했다. 구멍은 roadmap 경로(산출물이 plan 문서 계약을 지키지 못함)와 design의 위치(체인 정의가 두 벌)에 있다. 이 구멍들로 인한 실패는 관찰되지 않았다. 고치기 전에 결정이 두 개 필요하다(아래 "결정 사항"). 이 문서를 검토하면서 심각도를 다시 매기고 사실 오류 셋을 바로잡았다. G5는 roadmap-plan-gate(6d0985c8)에서 이미 해결됐다. 고친 내용과 결정은 끝의 "검토 반영"에 있다.

## 범위와 방법

- 대상: `docs/handoff-graph-audit` @ d7f04869(master와 같음). 분석은 8794fd40에서 시작했고, 그 사이 커밋은 아래 대상 파일을 바꾸지 않았다(`git diff --stat 8794fd40 d7f04869 -- src/superclaude/{commands,core,agents,modes} README.md evals/tasks.yaml` 비어 있음). 모델: Claude Opus.
- 노드: 명령 35개, 에이전트 5개, 모드 7개(`find src/superclaude/<dir> -maxdepth 1 -name '*.md' ! -name README.md`).
- 대조한 다섯 출처:
  1. 각 파일의 `<handoff next="...">` 태그
  2. `RULES_DOCS.md` `<workflow_gates>`의 관문 11개
  3. 명령 본문 flow의 라우팅 문장
  4. README 크기별 체인(`README.md:294-298`)
  5. `/sc:intent --through` 실행 순서(`intent.md:20`)
- 문서 계약: plan·roadmap의 산출물을 implement·test·reflect·task가 요구하는 것과 비교했다.
- status: enum 값마다 쓰는 곳과 읽는 곳을 grep으로 찾고, `docs/features/` 문서의 실제 status를 집계했다.
- 사용 데이터: `05-plan.md`가 있는 기능 15개의 앞 단계 문서, roadmap 산출물, canary probe를 집계했다.
- 도구: 세션 스크래치 스크립트(태그와 관문 추출, 저장소에 넣지 않음), grep, `git log -S`. 테스트는 돌리지 않았다. 문서만 쓴 작업이고 shipped 파일은 고치지 않았다.

## 그래프: 메인 체인

```mermaid
flowchart LR
  intent -->|G| brainstorm
  intent -->|G| plan
  intent -.-> design
  brainstorm -->|G| review_spec[review spec]
  brainstorm -->|G 승인만| design
  review_spec --> plan
  review_spec -.x|태그 없음| design
  design -->|G| plan
  design -->|G 문구 모순| roadmap
  design -.->|관문 없음| implement
  plan -->|G 커밋| implement
  roadmap -->|G| implement
  roadmap -.-> task
  implement -->|G| review_branch[review branch]
  implement -->|G| test
  review_branch --> test
  test -->|G| reflect
  reflect -->|G| done
```

`G`: workflow_gates에 관문이 있는 간선. 점선: 핸드오프 태그에만 있는 간선. `x`: README 체인에는 있는데 태그가 없는 간선. 전체 핸드오프 표는 부록에 있다.

## 구멍

표의 심각도 열은 검토 뒤 상태다. 각 절의 본문은 d7f04869 시점의 기록이다.

| # | 심각도 | 실제 사용 | 구멍 |
|---|---|---|---|
| G1 | 부분 해결(9b4ae86e: Proof 꼬리말. `Evidence:` 규칙은 보류) | 미사용 | roadmap 산출물이 plan 문서 계약을 지키지 못한다 |
| G2 | 해결됨(9b4ae86e: 핸드오프에서 task 뺌) | 미사용 | roadmap → task로 넘기면 plan 문서가 갱신되지 않는다 |
| G3 | Low(검토에서 낮춤). review → design 핸드오프는 해결됨(9b4ae86e) | 명령 쪽 체인만 1회 | 체인 정의가 두 벌이고, design의 위치가 다르다 |
| G4 | Low(검토에서 낮춤) | 미사용 | design → implement 간선이 plan을 건너뛴다 |
| G5 | 해결됨(6d0985c8) | 미사용 | roadmap 관문이 "plan과 같은 관문"이라 하지만 규칙이 다르다 |
| G6 | Low | 원인 | plan 이후 구간 밖에서는 핸드오프·관문·README가 서로 맞는지 확인하는 테스트가 없다 |
| G7 | Low | 무관 | status enum의 고아 값, enum 밖 status 11건 |
| G8 | Low | 미확인 | spec-panel이 고립돼 있고 관문을 통과시키지 못한다 |
| G9 | Low | 미확인 | 여러 파일을 바꾸는 명령에 review 간선이 없다 |
| G10 | Low | 무관 | 에이전트·모드 핸드오프가 체인 밖으로 안내한다 |

### G1. roadmap 산출물이 plan 문서 계약을 지키지 못한다

- roadmap은 기능마다 체크 박스와 빈 `Evidence:` 줄을 쓴다(`roadmap.md:17`). `## Proof` 꼬리말은 없다. 플로와 출력 표 어디에도 Proof가 나오지 않는다.
- implement는 마지막 박스를 체크한 뒤 "`## Proof` 꼬리말의 명령을 실행하고 `Result:` 줄을 쓴다"(`implement.md:19`). 실행할 Proof가 없다.
- `Evidence:`는 `implement.md`에 한 번도 나오지 않는다(grep 0건). roadmap이 기대하는 증거 기입을 implement가 하지 않는다.
- reflect Plan-Close 조건 (2)는 Proof `Result:`가 green이거나 사용자가 수락했을 것을 요구한다(`reflect.md:19`). `RULES_DOCS.md:58`도 plan의 `complete` 조건으로 Proof `Result:`를 요구한다.
- 결과: roadmap으로 만든 plan은 실행할 Proof가 없다. implement는 실행할 수 없는 Proof를 `Result:`로 기록하고 사용자 수락으로 인정받게 하므로(`implement.md:19`) `complete`에 이르는 길은 있다. 하지만 roadmap 문서마다 그 수락을 거쳐야 한다. (검토 정정: 처음 판정은 "규칙상 `complete`에 도달할 수 없다"였다.)

### G2. roadmap → task로 넘기면 plan 문서가 갱신되지 않는다

- roadmap 핸드오프에는 `/sc:task`가 있다. task의 flow에는 plan 문서를 입력으로 읽는 단계가 없다.
- task는 증거를 TaskCreate 설명에 남긴다(`task.md` flow 2, 6). 문서의 박스나 `Evidence:`는 건드리지 않는다.
- roadmap 문서는 빈 박스인 채 `draft`에 남는다.
- test → reflect 관문은 "plan 문서로 진행한 작업"에만 적용된다(`test.md:17`). task로 진행한 작업이 여기에 해당하는지 정해져 있지 않다.

### G3. 체인 정의가 두 벌이고, design의 위치가 다르다

| 출처 | 체인 |
|---|---|
| README Large(`README.md:298`, `:303`), `--through`(`intent.md:20`) | brainstorm → review(spec) → **design** → plan |
| brainstorm flow 6·8단계(`brainstorm.md:18`, `:20`), review 핸드오프(`review.md:76`) | brainstorm → review(spec) → plan |
| 관문 `brainstorm -> design`(`RULES_DOCS.md:79`) | brainstorm → design(review 조건 없음). 핸드오프 태그(`brainstorm.md:83`)는 `/sc:review /sc:plan /sc:design /sc:research`로 review가 먼저다(검토 정정) |

여기서 두 증상이 나온다.

- **review → design 핸드오프가 없다.** README Large 체인의 바로 다음 단계인데 review 태그는 `plan implement test troubleshoot`뿐이다. `--through`는 순서를 직접 정하므로 영향이 없고, 단계를 손으로 밟는 사용자만 안내를 받지 못한다.
- **design 전에 discovery 리뷰를 거쳤는지 아무도 확인하지 않는다.** 강제되는 리뷰 관문은 "/sc:plan으로 넘기기 전"(`RULES_DOCS.md:80`, `brainstorm.md:29`) 하나다. design Analyze는 `01-discovery.md`를 읽지만 status를 보지 않는다(`design.md:13`). draft spec 위에 design을 쓰면 plan Load에서 멈추고(`plan.md:13`), 그때 리뷰가 결정을 뒤집으면 design을 다시 써야 한다.

실제로 쓰인 것은 명령 쪽 체인이다(사용 데이터 참조). README Large 체인 그대로 진행한 기능은 없다.

### G4. design → implement 간선이 plan을 건너뛴다

design 핸드오프에 `/sc:implement`가 있고(`design.md:62`) 관문은 없다. 이 경로로 가면 다음이 함께 빠진다.

- Areas of concern을 해결하는 시점: "before /sc:plan"(`design.md:18`)
- design 승인: plan Save가 처리한다(`plan.md:18`)
- `05-plan` 문서: 그래서 `implement --plan`을 쓸 수 없다
- reflect Plan-Close: test → reflect 관문은 plan 문서로 진행한 작업에만 적용된다

`intent → design`(`intent.md:18`)도 관문이 없지만, 관문이 그 뒤에 이어지므로 영향은 더 작다.

### G5. roadmap 관문이 "plan과 같은 관문"이라 하지만 규칙이 다르다

**해결됨**: [roadmap-plan-gate](./roadmap-plan-gate-ajitta-2026-10-22.md)(6d0985c8)에서 처리했다. roadmap은 plan의 소스 순서와 관문을 그대로 적용하고, 소스인 design을 승인한다. `RULES_DOCS.md:82`도 고쳤다. probe 3개로 쟀다(`roadmap-design-draft` 0/3 → 3/3). 아래는 d7f04869 시점의 기록이다. "frontmatter 없는 PRD" 행은 구멍이 아니다. PRD는 discovery spec이 아니고, plan의 `--from <PRD>`도 같다.

| | `/sc:plan` | `/sc:roadmap` |
|---|---|---|
| 검사 대상 | `01-discovery`(source가 design이어도 검사) | source spec만 |
| draft `04-design` | 통과시키고 Save에서 `approved-for-plan`으로 바꿈 | 문구상 정지, `/sc:review --scope spec`으로 안내 |
| frontmatter 없는 PRD | 해당 없음 | 관문이 작동하지 않음 |

- 연혁:
  - plan Load가 discovery 전용이 됨: fb2f7422(10-15)
  - roadmap 관문 추가, "as /sc:plan already did": 67215cd7(10-18)
  - plan이 design 승인을 맡음: 97cbac42(10-20). roadmap은 따라가지 않았다
- 관문 문구 `/sc:design -> /sc:roadmap: Alternative path when input is a PRD/feature doc rather than a design spec`(`RULES_DOCS.md:82`)은 design 다음 단계라면서 입력은 design spec이 아니라고 해 스스로 모순된다.
- 문구를 그대로 따르면 roadmap 경로에서만 design이 격리된 리뷰를 강제로 받는다. 이때 Dim 2 렌즈는 spec용(requirement coverage)이고 design용(architectural soundness)이 아니다(`review.md:16`). Spec gate는 design 문서에 없는 Self-Review Iteration Log 섹션에 기록을 남긴다(`review.md:22`).

### G6. 일치 여부를 확인하는 테스트가 없다

`test_cross_references.py`는 핸드오프 대상 파일이 존재하는지만 본다. 핸드오프와 관문, 핸드오프와 본문의 금지 문장, 핸드오프와 README 체인이 서로 맞는지는 아무것도 확인하지 않는다. G3과 G5가 생겨 그대로 남은 이유다.

검토 정정: plan 이후 구간에는 가드가 있다. `test_docs_ssot_guards.py`의 `_GATE_ANCHORS`는 RULES_DOCS 관문, test·review·implement·reflect·intent 단계, README 행이 같은 규칙을 적는지 본다. 같은 파일은 `test.md` 핸드오프의 첫 항목이 `/sc:reflect`인지도 본다. 판정의 "실제로 쓰인 경로는 맞물린다"는 이 가드 덕분이다. 가드가 없는 곳은 그 구간 밖이다.

### G7. status enum의 고아 값과 enum 밖 status

- `review`는 enum에 있지만(`RULES_DOCS.md:61`) 쓰는 곳도 읽는 곳도 grep으로 찾지 못했다.
- `docs/features/`에 enum 밖 status가 11건 있다(`frozen` 4, `approved` 3, 기타 4). `approved` 3건은 10-19에 쓴 `00-intent.md`인데, 규칙상 값은 `approved-for-plan`이다(`RULES_DOCS.md:56`).
- enum을 강제하는 테스트가 없다.
- intent 관문은 "커밋됨"만 요구하므로 기능 영향은 없어 보인다.

### G8. spec-panel이 고립돼 있다

어느 명령의 핸드오프도 spec-panel을 가리키지 않는다. spec-panel은 spec의 status와 Iteration Log를 건드리지 않는다. 그런데 핸드오프는 design과 implement로 이어진다. spec 리뷰 대신 spec-panel을 쓰면 관문을 통과하지 못한 채 다음 단계 안내를 받는다.

### G9. 여러 파일을 바꾸는 명령에 review 간선이 없다

improve(`test analyze`), cleanup(`test build`), `troubleshoot --fix`(`improve implement`)가 해당한다. implement에는 review 간선이 있다.

### G10. 에이전트·모드 핸드오프가 체인 밖으로 안내한다

- `self-review` 에이전트의 핸드오프는 `/sc:improve /sc:test /sc:reflect`인데, 이 에이전트는 `/sc:review`가 spec 리뷰어로 띄운다(`review.md:45`).
- `MODE_Brainstorming`의 핸드오프에는 `/sc:implement`가 있다.
- 둘 다 제안일 뿐이다.

## 구멍이 아닌 것

- **들어오는 간선이 없는 명령 13개**: spec-panel(G8)을 빼면 진입점이다. help, init, intent, pm, agent, git, explain, estimate, insight, select-tool, business-panel, promote-feature. promote-feature는 cleanup이 "알리기만 하고 옮기지 않는다"고 의도적으로 정해 둔 경우다.
- **태그 안의 `--status`, `[command]`**: 템플릿 표기다. `test_cross_references.py:24`가 제외한다.
- **review → review(수정 후 재리뷰)**: 태그에는 없지만 Process 단계(`review.md:20`)가 다룬다.
- **plan status `draft → implementing`**: implement Integrate가 쓴다(`implement.md:19`).
- **명령 간 단계 참조 6개**: `/sc:reflect` Plan-Close, `/sc:brainstorm` Decision-mode tag·Self-review, `/sc:review` Process, `/sc:plan` Load, `/sc:load` Sync. 모두 해당 flow에 존재한다.
- **실패 분기**: test·review → troubleshoot 같은 경로는 관문이 필요 없다.

## 사용 데이터

| 경로 | 이 저장소에서의 사용 |
|---|---|
| `05-plan.md`가 있는 기능 15개 | 앞 단계 문서 없음 12 · discovery만 1 · design만 2 · 둘 다 0 |
| brainstorm → review → plan | 1회. `serena-removal`(05-plan 10-12): discovery `approved-for-plan`, Iteration Log 1건. 관문 정상 작동 |
| plan 이후 계약 | 15개 중 `complete` 11(박스를 다 채움 10, 박스 없음 1) · `implementing` 2 · `draft` 1 · `approved-for-plan` 1 |
| roadmap 산출물(`*-plan-workflow*`, `docs/plans/*-workflow-*`, `Evidence:` 줄) | 0건 |
| roadmap을 다루는 canary probe | d7f04869 시점 0개. 지금은 3개(roadmap-plan-gate) |
| README 크기별 체인 | Small·Medium·Large 어디에도 roadmap 없음 |

## 결정 사항

| 결정 | 선택지 |
|---|---|
| D1. roadmap(G1, G2, G5) | ① roadmap 템플릿에 `## Proof` 꼬리말을 넣고 증거 규칙을 implement에 맞춘다. 관문은 plan Load와 같게 하고, 핸드오프에서 task를 뺀다. 크기 S–M<br>② 원인 제거: 한 번도 쓰이지 않은 roadmap을 plan의 옵션으로 흡수하거나 폐기한다. fork 사용자 메모리가 허용하는 것은 "문서화된 CLI 명령을 README와 함께 제거"이고, 슬래시 명령에도 적용되는지는 소유자가 확인해야 한다. 검토 추가: 같은 흡수안은 이미 reframing-anchoring `04b-ponytail-content-structure-2.md` #13에서 제안됐다. lean-round B4(67215cd7, `docs/features/lean-round/04-batches.md:47`)는 흡수 대신 roadmap에 draft 정지를 넣는 쪽을 택했다. 다시 연다면 그 결정과 무엇이 달라졌는지(사용 0건)를 적어야 한다 |
| D2. 체인 기준(G3, G4) | ① README와 `--through`를 따른다. brainstorm·review flow와 review 핸드오프에 design을 넣고, design Analyze에 discovery status 검사를 넣는다. design 핸드오프에서 implement를 뺀다<br>② 실제로 쓰인 명령 쪽 체인을 따른다. README Large에서 design을 "선택"으로 표기하고, `brainstorm -> design` 관문에 리뷰 조건을 넣는다 |

어느 쪽을 골라도 G6의 일치 확인 테스트를 같은 변경에 넣어야 같은 어긋남이 다시 생기지 않는다. G7–G10은 D1·D2와 독립적이며, 관찰된 실패가 없으므로 다음에 해당 파일을 고칠 때 함께 처리해도 된다.

## 남은 불확실성

- 같은 파일 안의 "the X step" 참조는 확인하지 못했다.
- 슬래시 명령 파일을 지웠을 때 설치 프로그램이 기존 설치본의 파일을 지우는지는 확인하지 않았다(D1 ②에 필요하다).
- G7의 "`review` 0건"은 정규식 grep 결과라, 표기 방식이 다른 언급은 놓쳤을 수 있다.
- 모든 구멍은 문구를 읽어 판단했다. 모델이 실제로 그렇게 행동하는지는 canary로 돌려 보지 않았다.

## 부록: 명령 핸드오프 표

d7f04869 시점의 표다. 그 뒤 roadmap은 `implement`만 남았고, review에는 `design`이 더해졌다(9b4ae86e).

| 명령 | `next` | 명령 | `next` |
|---|---|---|---|
| agent | implement research | load | analyze index-repo task |
| analyze | plan improve cleanup implement | plan | implement brainstorm |
| auto-improve | auto-improve --status review | pm | implement task research |
| brainstorm | review plan design research | promote-feature | cleanup design plan |
| build | test troubleshoot | recommend | analyze implement design troubleshoot |
| business-panel | brainstorm design | reflect | improve troubleshoot |
| cleanup | test build | research | design implement brainstorm |
| design | plan implement roadmap | review | plan implement test troubleshoot |
| document | implement improve | roadmap | implement task |
| estimate | roadmap implement | save | load reflect |
| explain | implement improve document | select-tool | implement analyze |
| git | test build | spec-panel | design implement |
| help | recommend [command] | task | test implement |
| implement | review test build | test | reflect troubleshoot implement |
| improve | test analyze | troubleshoot | improve implement |
| index-repo | analyze index | init | load implement test |
| index | implement improve | insight | save analyze |
| intent | brainstorm plan design | | |

관문 11개(`RULES_DOCS.md:78-88`):

```
intent → brainstorm | plan
brainstorm → design
brainstorm → review
design → plan
design → roadmap
plan → implement
roadmap → implement
implement → review | test
review → (수정) → review
test → reflect | done
reflect → done
```

## 검토 반영

이 문서를 받은 뒤 master e69cfbe6에서 주장을 다시 확인했다. 확인한 것은 사용 데이터, 상태 집계, enum 밖 status, 핸드오프 표, G1의 핵심이고, 모두 재현됐다. 다음을 바로잡았다.

- 사실 정정 셋: G1의 "`complete`에 도달할 수 없다"(수락 경로가 있다), G3의 brainstorm 핸드오프 태그(review가 먼저다), G6의 "아무것도 확인하지 않는다"(plan 이후 구간에는 `_GATE_ANCHORS`가 있다).
- G5는 이 문서를 쓰는 사이 master에서 해결됐다(6d0985c8).
- 심각도: 관찰된 실패가 없으므로 Important는 두 파일이 어긋나는 G1·G2에만 남긴다. G3은 draft spec 위의 design을 plan Load가 나중에 막는다. G4의 implement는 plan 없이 쓰는 정상 경로다. 그래서 둘 다 Low로 낮췄다.
- D1 ②에 앞선 결정(04b #13, lean-round B4)을 인용했다.

소유자 결정(2026-10-22, 권고대로):

- D1 ①을 가장 작은 범위로 한다. roadmap 산출물에 plan과 같은 `## Proof` 꼬리말을 넣고, 핸드오프에서 `/sc:task`를 뺀다. 관문은 이미 맞췄다(G5).
- D2는 `/sc:review` 핸드오프에 `/sc:design`을 더하는 것만 한다. design Analyze의 discovery status 검사는 관찰된 실패가 없어 보류한다.
- G6은 범용 일치 테스트를 만들지 않는다. 이번에 고치는 간선만 기존 가드 방식으로 지킨다.
- G7–G10은 해당 파일을 다음에 고칠 때 함께 처리한다.

## 구현과 측정

- `roadmap.md` Validate 단계에 `## Proof` 꼬리말을 넣었다. 꼬리말은 워크플로 전체가 끝났음을 보이는 명령과 기대 출력을 적고, `/sc:implement --plan`이 마지막 상자 뒤에 실행해 `Result:`를 남긴다. 핸드오프는 `/sc:implement`만 남겼다. `review.md` 핸드오프에는 `/sc:design`을 더했다. 가드는 `test_docs_ssot_guards.py::test_roadmap_and_review_handoffs_follow_the_chain`이다. 수정을 되돌리면 이 가드가 red가 되는 것을 확인했다.
- probe `roadmap-design-draft`에 check 하나를 더했다. roadmap 문서에 명령을 적은 `## Proof` 꼬리말이 있어야 한다. 측정 전에 커밋했다(c4afeca3).
  - 변경 전: 저장된 run 6개(de4e6cb3·e03e1889, roadmap.md는 같음)를 다시 채점하니 0/6이었다. 그중 4개는 `## Proof`와 빈 `Result:`만 쓰고 명령은 적지 않았다.
  - 변경 후(9b4ae86e, Linux, sonnet, 3회): roadmap 프로브 3개 모두 9/9 통과. Proof 꼬리말은 3/3에서 명령과 기대 출력을 적었다.
  - 남은 관찰: 한 run은 꼬리말 끝에 빈 `Result:` 자리표시를 남겼다. `/sc:implement`가 Proof를 실행한 뒤 이 줄을 다시 쓰므로 문구를 더하지는 않는다.
- 릴리스 때: v4.34.2 이후 `roadmap.md`, `review.md`, `reflect.md`, `test.md`와 `core/rules/RULES_DOCS.md`가 바뀌었다. 그래서 `make canary-commands`(review를 다루는 `--through` probe 포함)와 `make canary-gates`가 둘 다 필요하다.

## 독립 검증 반영

[독립 검증](./command-handoff-graph-verify-ajitta-2026-10-22.md)(opus high)의 판정은 조건부 통과였다. Important는 1개였다.

| 발견 | 처리 |
|---|---|
| 1 Important: 이 문서가 고친 증상을 열린 구멍으로 적음 | 맨 위에 현재 상태를 적었다. 구멍 표의 G1·G2·G3 상태를 고치고, 각 절과 부록이 d7f04869 시점 기록임을 표시했다 |
| 2 roadmap `Evidence:` 규칙을 지키게 하는 곳 없음 | 소유자가 가장 작은 범위를 고르며 보류한 부분이라 두었다. G1은 "부분 해결"로 남긴다 |
| 3 `RULES_DOCS.md:84`가 `--plan`과 "committed"를 말하지 않음 | `/sc:roadmap -> /sc:implement --plan: Roadmap document committed; implementation proceeds per its task list and ends with its Proof footer`로 고쳤다 |
| 4 probe check가 관대함 | ` ``` ` 펜스 블록 안의 제목을 무시하고, `Result:` 줄은 명령으로 치지 않게 고쳤다. 저장된 run을 다시 채점하니 변경 전 0/6, 변경 후 3/3으로 그대로였다. 테스트 사례 둘을 더했다. 남은 한계(2차 검증 반영으로 정정): 내용과 상관없이 펜스 블록을 명령으로 친다(기대 출력만 담은 ` ```text ` 블록도 통과). `~~~` 펜스 안의 제목, 그리고 들여쓴 펜스나 목록 안 펜스(`- ```md`) 안의 제목은 무시하지 않는다. 줄 첫 칸에서 여는 ` ``` ` 펜스만 본다(4차 검증 반영). `## Proof`가 마지막 절인지 보지 않는다. 백틱으로 감싼 자리표시(`` `<command>` ``)는 통과한다. `## Proof:`, `### Proof`, `## Proof footer` 제목은 실패한다. 절 안에 백틱이 하나라도 있으면 통과한다(자리표시나 파일 이름만 있어도). `Result:`로 시작하는 줄만 빼므로 `**Result:**`나 `- Result:` 줄은 명령으로 친다(3차 검증 반영). 명령과 출력을 정규식으로 가를 수 없으므로 더 조이지 않는다. 변경 후 세 run의 꼬리말은 사람이 직접 읽어 명령과 기대 출력이 있음을 확인했다 |
| 이 브랜치 밖, Important 후보: roadmap이 plan 옆에 쓰는 `05<letter>-plan-workflow.md`가 Plan-Close 대상 정의에 없어 `implementing`에서 나갈 길이 없음 | 같은 계약이라 이 브랜치에서 고쳤다. `reflect.md` Plan-Close, `test.md` Report, `RULES_DOCS.md` reflect 관문의 정의에 "a roadmap's `05<letter>-plan-workflow.md`"를 넣었다. 가드는 세 곳이 그 이름을 적는지 본다 |
| 이 브랜치 밖: 릴리스에 `canary-gates`도 필요 | 위 "릴리스 때" 줄을 고쳤다 |

## 2차 독립 검증 반영

[2차 검증](./command-handoff-graph-verify2-ajitta-2026-10-22.md)의 판정은 조건부 통과였다. Important는 1개였고, 바로 위 적용 표의 거짓 문장이다.

| 발견 | 처리 |
|---|---|
| 1 Important: 적용 표가 "끝 탭도 이제 인식한다"고 적고 남은 한계를 덜 적음(옛 check도 탭과 CRLF를 통과시켰다) | 그 문장을 지우고, 남은 한계를 다섯 가지로 적었다(위 표 4번 행) |
| 2 probe check의 남은 관대함 | 더 조이지 않는다. 펜스 블록 안이 명령인지 출력인지는 정규식으로 가를 수 없다. 단어 목록을 늘리면 누더기가 된다. 변경 후 run은 사람이 직접 읽었다 |
| 3 분할 plan 단계 이름(`workflow`)과 roadmap 이름이 겹침 | 정의를 이름이 아니라 역할로 바꿨다: "a feature folder's `05-plan.md` or another `05<letter>-plan-*.md` plan that is not a split plan's phase file"(`reflect.md` Plan-Close, `test.md` Report, `RULES_DOCS.md` reflect 관문) |
| 이 브랜치 밖, Important 후보: 다른 독립 plan `05<letter>-plan-<distinguisher>.md`도 정의에 없음 | 같은 문장으로 해결된다(`command-local-flags/05a-plan-pointer-checks.md`, `plugin-install/05a-plan-release-channel.md` 같은 파일) |
| 4 한 폴더에 plan이 둘이면 README `phase:`가 먼저 끝난 plan에서 `complete`가 됨 | Plan-Close는 "폴더의 다른 plan 문서가 모두 `complete`일 때"만 README를 `complete`로 바꾼다. RULES_DOCS phase 매핑도 "every plan (index) in the folder"로 고쳤다 |
| 5 `test.md` verifier 항목이 `05-plan.md`로만 적음 | "the plan doc the work ran from"으로 바꿨다 |

## 3차 독립 검증 반영

[3차 검증](./command-handoff-graph-verify3-ajitta-2026-10-22.md)의 판정은 조건부 통과였다. Important는 1개였다.

| 발견 | 처리 |
|---|---|
| 1 Important: README `complete` 조건이 끝내 `complete`가 될 수 없는 plan 문서까지 셈. 예: 박스가 없는 부속 파일 `runtime-behavior-audit/05a-plan-trigger-tiers.md`, `deprecated` plan, `archive/` | `reflect.md` Plan-Close는 "other plan documents with task boxes are all `complete` or `deprecated`"일 때 README를 바꾼다. RULES_DOCS 매핑은 "every plan (index) with task boxes in the folder (`archive/` aside) at `status: complete` or `deprecated`"이다. 둘 다 가드에 넣었다 |
| 2 단계 파일과 별도 plan을 가르는 기준이 정의에 없음 | 정의 세 곳에 "(one its index lists with a checkbox)"를 붙였다 |
| 3 probe check 한계 목록이 다 적지 못함 | 적용 표 4번 행에 더했다. 고치지는 않는다(G2) |
| 4 verifier 항목을 지키는 가드가 없고, 경로를 넘기라는 말이 없음 | "whose path it is passed"를 넣고 가드에 더했다 |
| 이 브랜치 밖: implement 첫 박스가 README를 `implementing`으로 되돌릴 수 있음 | "when it is not already further"를 붙였다. 같은 README phase 규칙이라 이 브랜치에서 고쳤다 |

## 4차 독립 검증 반영

[4차 검증](./command-handoff-graph-verify4-ajitta-2026-10-22.md)의 판정은 조건부 통과였다. Important는 1개였다. plan이 닫힌 뒤 남은 plan을 버리거나 `archive/`로 옮기면 README를 `complete`로 쓰는 단계가 없었다.

처리: 2차 제안 4에서 들인 "폴더의 다른 plan이 모두 끝나야 README `complete`" 규칙을 되돌렸다. 이 규칙은 3차와 4차에서 매번 새 막다른 상태를 만들었다(박스 없는 부속 파일, 닫은 뒤의 `deprecated`와 `archive/`). 그 상태들을 막으려면 어떤 명령도 맡지 않는 수명 주기(버리기, 옮기기, 다시 확인하기)가 필요하다. 원래 매핑은 "README `phase:` = 폴더가 도달한 가장 먼 단계"이고, plan 하나가 끝나면 그 단계에 도달한 것이다. 이 정의와 맞고 막다른 상태도 없다. 그래서 `reflect.md` Plan-Close와 RULES_DOCS 매핑을 원래 문장("plan (index) `status: complete` → complete")으로 돌렸다. 가드는 원래 문장을 고정하고 "with task boxes"가 다시 들어오지 않는지 본다. 2차 제안 4(다른 plan이 진행 중인데 README는 끝난 것처럼 보임)는 받지 않는다. phase가 "도달한 가장 먼 단계"라는 정의대로 동작하는 것이다. 각 plan의 `status:`가 진행 상황을 보여 준다.

| 발견 | 처리 |
|---|---|
| 1 Important: 닫은 뒤 버린 plan 때문에 README가 막힘 | 위와 같이 규칙을 되돌려 원인을 없앴다 |
| 2 reflect에 "(`archive/` aside)"가 없음 | 규칙을 되돌렸으므로 해당 없다 |
| 3 probe 한계에 들여쓴 펜스가 빠짐 | 적용 표 4번 행에 더했다 |
| 4 `test.md` verifier 문장이 꼬임 | "(its Proof section and task list; pass it that path), and reports …"로 고치고 가드 구절을 바꿨다 |

남는 것: plan 문서 정의(역할과 인덱스 체크박스 기준), verifier 경로, implement 첫 박스의 "when it is not already further"는 그대로다.
