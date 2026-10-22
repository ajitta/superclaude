---
status: complete
revised: 2026-10-22
---

# `/sc:*` 명령 핸드오프 그래프와 구멍

**판정: 실제로 쓰인 경로는 맞물리고, 구멍은 쓰이지 않은 두 영역에 몰려 있다.** plan 이후의 문서 계약(implement가 `Result:`를 쓰고 reflect가 확인)과 brainstorm → review → plan 관문은 이 저장소에서 실제로 작동했다. 구멍은 roadmap 경로(산출물이 plan 문서 계약을 지키지 못함)와 design의 위치(체인 정의가 두 벌)에 있다. 이 구멍들로 인한 실패는 관찰되지 않았다. 고치기 전에 결정이 두 개 필요하다(아래 "결정 사항").

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

| # | 심각도 | 실제 사용 | 구멍 |
|---|---|---|---|
| G1 | Important | 미사용 | roadmap 산출물이 plan 문서 계약을 지키지 못한다 |
| G2 | Important | 미사용 | roadmap → task로 넘기면 plan 문서가 갱신되지 않는다 |
| G3 | Important | 명령 쪽 체인만 1회 | 체인 정의가 두 벌이고, design의 위치가 다르다 |
| G4 | Important | 미사용 | design → implement 간선이 plan을 건너뛴다 |
| G5 | Medium | 미사용 | roadmap 관문이 "plan과 같은 관문"이라 하지만 규칙이 다르다 |
| G6 | Low | 원인 | 핸드오프·관문·README가 서로 맞는지 확인하는 테스트가 없다 |
| G7 | Low | 무관 | status enum의 고아 값, enum 밖 status 11건 |
| G8 | Low | 미확인 | spec-panel이 고립돼 있고 관문을 통과시키지 못한다 |
| G9 | Low | 미확인 | 여러 파일을 바꾸는 명령에 review 간선이 없다 |
| G10 | Low | 무관 | 에이전트·모드 핸드오프가 체인 밖으로 안내한다 |

### G1. roadmap 산출물이 plan 문서 계약을 지키지 못한다

- roadmap은 기능마다 체크 박스와 빈 `Evidence:` 줄을 쓴다(`roadmap.md:17`). `## Proof` 꼬리말은 없다. 플로와 출력 표 어디에도 Proof가 나오지 않는다.
- implement는 마지막 박스를 체크한 뒤 "`## Proof` 꼬리말의 명령을 실행하고 `Result:` 줄을 쓴다"(`implement.md:19`). 실행할 Proof가 없다.
- `Evidence:`는 `implement.md`에 한 번도 나오지 않는다(grep 0건). roadmap이 기대하는 증거 기입을 implement가 하지 않는다.
- reflect Plan-Close 조건 (2)는 Proof `Result:`가 green이거나 사용자가 수락했을 것을 요구한다(`reflect.md:19`). `RULES_DOCS.md:58`도 plan의 `complete` 조건으로 Proof `Result:`를 요구한다.
- 결과: roadmap으로 만든 plan은 규칙상 `complete`에 도달할 수 없다.

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
| brainstorm 핸드오프 태그(`brainstorm.md:83`), 관문 `brainstorm -> design`(`RULES_DOCS.md:79`) | brainstorm → design(review 언급 없음) |

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
| roadmap을 다루는 canary probe | 0개(`evals/tasks.yaml`에 `roadmap`은 주석 2줄뿐) |
| README 크기별 체인 | Small·Medium·Large 어디에도 roadmap 없음 |

## 결정 사항

| 결정 | 선택지 |
|---|---|
| D1. roadmap(G1, G2, G5) | ① roadmap 템플릿에 `## Proof` 꼬리말을 넣고 증거 규칙을 implement에 맞춘다. 관문은 plan Load와 같게 하고, 핸드오프에서 task를 뺀다. 크기 S–M<br>② 원인 제거: 한 번도 쓰이지 않은 roadmap을 plan의 옵션으로 흡수하거나 폐기한다. fork 사용자 메모리가 허용하는 것은 "문서화된 CLI 명령을 README와 함께 제거"이고, 슬래시 명령에도 적용되는지는 소유자가 확인해야 한다 |
| D2. 체인 기준(G3, G4) | ① README와 `--through`를 따른다. brainstorm·review flow와 review 핸드오프에 design을 넣고, design Analyze에 discovery status 검사를 넣는다. design 핸드오프에서 implement를 뺀다<br>② 실제로 쓰인 명령 쪽 체인을 따른다. README Large에서 design을 "선택"으로 표기하고, `brainstorm -> design` 관문에 리뷰 조건을 넣는다 |

어느 쪽을 골라도 G6의 일치 확인 테스트를 같은 변경에 넣어야 같은 어긋남이 다시 생기지 않는다. G7–G10은 D1·D2와 독립적이며, 관찰된 실패가 없으므로 다음에 해당 파일을 고칠 때 함께 처리해도 된다.

## 남은 불확실성

- 같은 파일 안의 "the X step" 참조는 확인하지 못했다.
- 슬래시 명령 파일을 지웠을 때 설치 프로그램이 기존 설치본의 파일을 지우는지는 확인하지 않았다(D1 ②에 필요하다).
- G7의 "`review` 0건"은 정규식 grep 결과라, 표기 방식이 다른 언급은 놓쳤을 수 있다.
- 모든 구멍은 문구를 읽어 판단했다. 모델이 실제로 그렇게 행동하는지는 canary로 돌려 보지 않았다.

## 부록: 명령 핸드오프 표

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
