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
  - Document 단계: Analyze 단계가 읽은 design을 같은 저장에서 `approved-for-plan`으로 바꾼다.
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
