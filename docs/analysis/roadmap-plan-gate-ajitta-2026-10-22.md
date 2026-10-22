---
status: complete
revised: 2026-10-22
---

# `/sc:roadmap`의 리뷰 관문을 `/sc:plan`과 맞춘다

`/sc:roadmap`의 Analyze 단계는 "the same review gate /sc:plan applies"라고 적었다. 그런데 내용이 달랐다. plan은 draft discovery spec이면 멈추고(design이 있어도 멈춘다), design은 통과시킨 뒤 Save에서 `approved-for-plan`으로 바꾼다(97cbac42). roadmap은 넘겨받은 파일 하나만 검사했다. 그래서 draft design에서 멈추고 `/sc:review --scope spec`으로 보냈고, 옆에 있는 draft discovery spec은 보지 않았다. 67215cd7(10-18)이 "as /sc:plan already did"라며 관문을 들였는데, 97cbac42(10-20)는 plan만 바꿨다.

소유자 결정(2026-10-22): 안 A. roadmap이 plan의 관문을 그대로 적용하고, 프로브를 함께 둔다. design 이후 독립 리뷰를 명령에 넣는 안(B)은 다루지 않는다. 관문 문장을 지우는 안(C)은 채택하지 않았다. roadmap 세션에는 `plan.md`가 로드되지 않고, roadmap → implement 경로에는 다른 관문이 없기 때문이다. 릴리스는 소유자가 보류했다. 다음 릴리스에 함께 나간다.

## 변경

- `src/superclaude/commands/roadmap.md`:
  - Analyze 단계: 어떤 입력이든 draft discovery spec이면 멈춘다(입력 문서, 또는 `04-design.md`가 있어도 feature 폴더의 `01-discovery.md`). design은 `draft`라는 이유로 멈추지 않는다. 해결되지 않은 Areas of concern이 있으면 그렇다고 말하고 진행할지 묻는다.
  - Document 단계: Analyze 단계가 읽은 design을 같은 저장에서 `approved-for-plan`으로 바꾼다(독립 검증 반영에서 "소스인 design"으로 좁혔고, 소스 순서도 더했다).
- 프로브 `roadmap-draft-spec-gate`, `roadmap-design-discovery-draft`, `roadmap-design-draft`(`evals/tasks.yaml`, fixture `evals/fixtures/roadmap-design-gate`)와 채점 테스트. 측정 전에 커밋했다(a9e01360).

## 측정

Linux, sonnet, sc-full, 각 3회. 커밋 a9e01360(변경 전)과 de4e6cb3(변경 후)에서 돌렸다.

| 프로브 | 변경 전 | 변경 후 |
|---|---|---|
| `roadmap-draft-spec-gate` | 3/3 | 3/3 |
| `roadmap-design-discovery-draft` | 3/3 | 3/3 |
| `roadmap-design-draft` | 0/3 | 3/3 |

- 변경 전 `roadmap-design-draft`의 세 run은 모두 "04-design.md is still `status: draft`"라며 멈췄다. 그리고 `/sc:review --scope spec 04-design.md`를 권했다. 분석이 문구에서 읽은 동작이 실제로 그랬다.
- 변경 전 `roadmap-design-discovery-draft`는 결과는 맞았지만 이유가 달랐다. draft design 때문에 멈췄고, discovery spec은 언급하지 않았다. 변경 후 세 run은 draft discovery spec을 이유로 들었고, design은 "draft라도 막지 않는다"고 했다.
- 변경 후 `roadmap-design-draft`의 세 run은 모두 `05-plan.md`를 썼다. design을 `approved-for-plan`으로 바꾸고 `revised`를 올렸으며, README `phase: planning`과 Documents를 갱신했다. 코드는 바꾸지 않았다.
- `roadmap-draft-spec-gate`는 변경 전에도 통과한 회귀 가드다.

## 독립 검증 반영

[독립 검증](./roadmap-plan-gate-verify-ajitta-2026-10-22.md)(opus high)의 판정은 조건부 통과였다. Important는 1개였다.

| 발견 | 처리 |
|---|---|
| 1 Important: `RULES_DOCS.md` workflow_gates가 roadmap을 "design spec이 아닌 입력"용으로 적고, Areas of concern을 넘기는 자리를 plan Load로만 적음 | `/sc:design -> /sc:roadmap`을 "Alternative to /sc:plan for a phased workflow, from the design or from a PRD/feature doc; the same gate as /sc:design -> /sc:plan"으로 고쳤다. `/sc:design -> /sc:plan`에는 "or the /sc:roadmap Analyze step"을 더했다. `core/`가 바뀌었으므로 릴리스 때 `make canary-gates`가 필요하다 |
| 2 입력 해석 순서가 없어 승인 대상이 plan보다 넓음 | Analyze에 plan Load와 같은 순서를 두었다. 넘겨받은 문서, 없으면 feature 폴더의 `04-design.md`(fallback `01-discovery.md`), 없으면 사용자 설명이다. 승인 대상은 "the design doc that is the Analyze step's source"로 좁혔다 |
| 3 새 `.py` 파일을 놓침 | `roadmap-design-draft`에 `file_absent_glob '**/*.py'`(`exclude_baseline`)를 더했다. 테스트에 새 파일 변이를 넣었다 |
| 4 "roadmap 문서 작성" check가 테스트로 지켜지지 않음 | "design은 승인됐지만 roadmap 문서는 없음 → 실패" 단언을 더했다. 그 check를 지우는 변이와 새 `.py` check를 지우는 변이가 각각 red임을 확인했다 |
| 5 Areas of concern 분기 프로브 없음 | 하지 않는다. plan에도 같은 프로브가 없고, 관찰된 실패가 없다 |
| 이 브랜치 밖: README가 plan 관문을 "draft spec"으로 적음 | 같은 관문이라 이 브랜치에서 고쳤다(README `/sc:review` 행과 Tightened Workflow Gates 줄: "discovery spec") |
| 이 브랜치 밖: `RULES_DOCS.md:81` "Design spec committed"를 확인하는 단계 없음 | 기존 상태라 두었다 |

2차 독립 검증([verify2](./roadmap-plan-gate-verify2-ajitta-2026-10-22.md))은 통과였다(Critical·Important 없음). 1차 발견 다섯이 모두 해결됐다. check 14개를 하나씩 지우는 변이를 하면 14개 모두 red였다. 남은 제안 셋은 다시 round를 돌리지 않고 처리했다.

- `RULES_DOCS.md:82`: "the same gate"를 design 입력에만 붙였다.
- 이 문서의 변경 절에 좁힌 내용을 표시했다.
- 소스가 approved discovery이고 옆에 draft design이 있는 경우의 프로브는 두지 않는다. 관찰된 실패가 없고, plan에도 대응 프로브가 없다.

e03e1889에서 돌린 측정:

- roadmap 프로브 3개 × 3회: 9/9 통과
- `make canary-gates`: hard-gate check 7개 모두 통과

그 뒤 바뀐 것은 `RULES_DOCS.md:82`의 절 순서뿐이다.

남긴 것(이 브랜치 밖): `plan.md` Save의 "the design doc the Load step read"도 "source"로 좁히면 같은 틈이 plan에서도 닫힌다. 이 일은 `plan.md`를 다음에 건드리는 round에서 한다.
