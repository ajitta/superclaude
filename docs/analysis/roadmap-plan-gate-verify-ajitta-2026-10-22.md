---
status: complete
revised: 2026-10-22
---

# roadmap-plan-gate 독립 검증

대상: `verify/roadmap-plan-gate` 55d8762b (master 8ed42256 기준 3커밋). 측정 수치(변경 전 3/3, 3/3, 0/3 → 변경 후 3/3, 3/3, 3/3)는 실행 기록이 저장소에 없어 주장으로만 다뤘다.

**판정: 조건부 통과**

roadmap의 Analyze·Document 단계는 이제 plan의 Load·Save 단계 관문을 문장 단위로 그대로 적는다. roadmap 세션에 plan.md가 없어도 동작이 성립하고, CHANGELOG도 그 내용과 맞는다. 다만 `RULES_DOCS.md`의 `/sc:design -> /sc:roadmap` 관문 줄은 아직 roadmap을 "design spec이 아닌 입력"용 경로로 적고 있어 새 문구와 어긋난다(1번). 나머지는 가드 범위의 제안이다.

## 게이트 실행

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3864 passed, 3 skipped, exit 0 (166 s) |
| `make lint` | All checks passed! |
| `make typecheck` | Success: no issues found in 54 source files |
| `ruff format --check src tests` | 223 files already formatted |
| `pytest tests/unit/test_eval_harness.py -k roadmap` | 3 passed |
| `evals/changed_command_probes.py` (기준 태그 v4.34.2) | `--task roadmap-draft-spec-gate --task roadmap-design-discovery-draft --task roadmap-design-draft` |
| `run_eval.py --canary --task …(3개) --dry-run` | 세 작업 공간 모두 build ok. 커밋 1개(`baseline`), 태그 `baseline`, status 깨끗. 상태: spec-gate는 01 `draft`·04 없음, discovery-draft는 01 `draft`·04 `draft`, design-draft는 01 `approved-for-plan`·04 `draft`. 설치된 `.claude/commands/sc/roadmap.md`에 새 문구("Whatever the source") 있음 |

## 1번 질문: plan과 roadmap 조항 대조

| 조항 | plan.md | roadmap.md | 일치 |
|---|---|---|---|
| draft discovery spec → 멈춤, `/sc:review --scope spec` | :13 (--from 문서 또는 `01-discovery.md`, `04-design.md`가 있어도) | :13 (입력 문서 또는 `01-discovery.md`, 같은 조건) | 예 |
| draft design은 멈추지 않음 | 명시 없음(Save가 draft design을 승인하므로 함의) | :13 명시 | 예(roadmap 쪽이 더 명확) |
| 미해결 Areas of concern → 알리고 진행 여부 질문 | :13 | :13 | 예 |
| 읽은 design을 `approved-for-plan`으로, `revised` 갱신, 같은 저장 | :18 | :18 | 예 |
| 넘어간 concern은 Areas of concern에 남김 | :18 | :18 | 예 |
| 입력 해석 순서(--from → `04-design.md` → `01-discovery.md`) | :13 | 없음 | 아니오(2번) |
| `00-intent.md` 읽기 | :13 | 없음 | 관문 밖 |

roadmap 문구는 plan.md에 기대지 않는다. "the same review gate /sc:plan applies"는 이제 설명 꼬리표일 뿐이고, 동작은 roadmap.md 안에 다 있다. `/sc:roadmap`은 `context_loader.py:191` 트리거로 `RULES_DOCS.md`를 받는다.

## 발견 사항

1. **Important: `RULES_DOCS.md` workflow_gates가 새 roadmap 입력과 어긋난다.**
   근거: `src/superclaude/core/rules/RULES_DOCS.md:82` `/sc:design -> /sc:roadmap: Alternative path when input is a PRD/feature doc rather than a design spec`. 이제 `roadmap.md:13`은 design 문서(`04-design.md`, `docs/specs/*-design-*.md`)를 입력으로 이름 붙이고, `:18`에서 그 design을 승인한다. 프로브 두 개도 `04-design.md`를 roadmap 입력으로 쓴다. 또 `RULES_DOCS.md:81`은 Areas of concern을 넘기는 자리를 "the /sc:plan Load step"으로만 적는다. roadmap Analyze 단계가 같은 질문을 하게 된 것은 반영되지 않았다. 이 파일은 roadmap 세션에 로드되므로, 서로 다른 두 문장이 같은 컨텍스트에 들어간다. 변경 후 3/3 run에서 실제 혼동은 관찰되지 않았다고 기록돼 있다. 82행 자체는 이 브랜치 전부터 있었지만, 이 브랜치가 design 입력을 명시하면서 모순이 드러났다.
   수정: 82행을 예컨대 `/sc:design -> /sc:roadmap: Alternative to /sc:plan for a phased workflow; same gate as /sc:design -> /sc:plan, with Areas of concern built past at the /sc:roadmap Analyze step`로 바꾼다. 81행의 "at the /sc:plan Load step" 뒤에 "or the /sc:roadmap Analyze step"을 덧붙인다. CHANGELOG 항목은 그대로 둬도 된다.

2. **Suggestion: roadmap에는 입력 해석 순서가 없다. 그래서 "the design doc the Analyze step read"의 범위가 plan보다 넓다.**
   근거: `plan.md:13`은 Load가 읽는 source를 정한다. 그래서 `--from 01-discovery.md`이면 design을 읽지 않고, Save는 design을 승인하지 않는다. `roadmap.md:13`은 "Parse PRD"뿐이다. 예를 들어 `/sc:roadmap docs/features/x/01-discovery.md`(approved)를 받고 맥락 파악용으로 옆의 draft `04-design.md`를 읽은 run은 `:18`에 따라 그 design을 승인할 수 있다. plan이라면 승인하지 않는 경우다. feature 이름만 받았을 때 design을 읽어야 하는지도 정해져 있지 않다. 관찰된 실패는 없다.
   수정: Analyze 앞부분에 plan과 같은 순서를 둔다. 인자로 받은 문서, 없으면 feature 폴더의 `04-design.md`(fallback `01-discovery.md`)이다. 승인 대상은 "the design doc that is the Analyze step's source"로 좁힌다.

3. **Suggestion: `roadmap-design-draft`의 "코드 변경 없음" 검사는 새 .py 파일을 놓친다.**
   근거: dry-run 작업 공간에서 `echo x=1 > export_csv.py; git diff --quiet baseline -- '*.py'` → exit 0. `src/w.py`도 exit 0이다. 저장소의 기존 관례는 `evals/tasks.yaml:634-635`처럼 `no_py_change`와 `no_new_py`(`file_absent_glob '**/*.py'`, `exclude_baseline: true`)를 짝으로 둔다. roadmap 프로브(`tasks.yaml:571`)에는 앞의 것만 있다.
   수정: `- {type: file_absent_glob, tag: scope, pattern: '**/*.py', exclude_baseline: true}`를 추가하고, 테스트에 새 .py 파일을 만드는 변이를 넣는다.

4. **Suggestion: 채점 테스트가 `roadmap-design-draft`의 "roadmap 문서 작성" 검사를 지키지 않는다.**
   근거: 검사 하나씩 제거 변이 14회(앵커를 풀어 각 작업에서 독립적으로 제거) 중 13회는 테스트가 red가 됐다. `roadmap-design-draft`의 첫 검사(`tag: success`, `05*.md` 또는 `docs/plans/*.md` 존재)를 지운 경우만 `3 passed`였다. `tests/unit/test_eval_harness.py:1463`의 "nothing written passed" 단언은 design이 아직 draft라서 실패하는 것이지, roadmap이 없어서 실패하는 것이 아니다. 프로브 자체는 옳다.
   수정: 테스트에 "design만 `approved-for-plan`, roadmap 문서 없음 → `not all(...)`" 단언을 추가한다.

5. **Suggestion: Areas of concern 질문 분기와 `revised` 갱신을 재는 프로브가 없다.**
   근거: 픽스처 `04-design.md`의 Areas of concern은 `none`이다. 어떤 검사도 `revised`를 보지 않는다. plan 쪽에도 해당 프로브가 없다(`tasks.yaml`에서 `Areas of concern` 검색 시 roadmap 주석 한 곳뿐).
   수정: 미해결 concern이 있는 변형 픽스처로, 질문 없이 roadmap을 쓰면 실패하는 프로브를 둔다. 선택 사항이다.

## 3번 질문: 하류 영향(발견 없음)

- roadmap이 design을 승인한 뒤 `/sc:plan`을 실행하면, Load는 승인된 design을 읽는다. Save의 "draft → approved-for-plan"은 해당 사항이 없어 아무것도 바꾸지 않는다. 같은 상태를 두 쓰기 주체가 반대로 뒤집는 경로는 없다(둘 다 같은 방향, 멱등). `existing-plan` gotcha(`plan.md:77`)는 roadmap이 쓴 `05-plan.md`를 발견한다.
- roadmap 자신의 출력은 `status: draft`로 시작하고(`roadmap.md:17`), `complete` 규칙(`RULES_DOCS.md` Plan docs)과 `/sc:implement` 쪽 문구는 바뀌지 않았다. `RULES_DOCS.md:13`은 05 슬롯을 plan·roadmap 공용으로 이미 적는다.
- 탈출로: draft discovery로 멈춤 → `/sc:review --scope spec`이 `approved-for-plan`으로 바꿈(`review.md:22`) → 다시 실행. concern으로 거절 → `/sc:design`에서 해소. 빠져나갈 수 없는 상태는 없다.

## 5번 질문: CHANGELOG

`CHANGELOG.md:13-14`는 출하 문구와 맞는다. draft discovery는 design 옆에 있어도 멈추고, draft design은 승인되며, concern 질문이 같다. 사용자 관점 서술이고, 97cbac42 항목과 같은 형식이며, 기여자 줄을 따로 뒀다. "a review meant for discovery specs"는 저자의 해석이다. `review.md:22` Spec gate는 "a `status: draft` spec" 전반에 적용되지만, design용 `--scope design`(`review.md:54`)이 따로 있으므로 과장은 아니다. 출시된 이력 항목(`CHANGELOG.md:301`, "as /sc:plan already did")은 수정하지 않았고, 수정 대상도 아니다.

## roadmap 관문을 적는 곳

| 위치 | 내용 | 새 roadmap 문구와 |
|---|---|---|
| `commands/roadmap.md:13,18` | 관문 본문 | 기준 |
| `commands/plan.md:13,18` | 같은 관문(plan) | 일치(입력 해석 순서만 차이, 2번) |
| `core/rules/RULES_DOCS.md:81` | design→plan, concern은 "/sc:plan Load step"에서 넘김 | 부분 불일치(1번) |
| `core/rules/RULES_DOCS.md:82` | design→roadmap: "PRD/feature doc rather than a design spec" | 불일치(1번) |
| `core/rules/RULES_DOCS.md:84` | roadmap→implement: "Roadmap tasks defined" | 일치 |
| `core/rules/RULES_DOCS.md:13,18` | 05 슬롯 = plan, roadmap | 일치 |
| `commands/design.md:62` | handoff에 `/sc:roadmap` | 일치 |
| `commands/brainstorm.md:18,20,75` | discovery는 review 후 `/sc:plan` | 일치(roadmap 언급 없음) |
| `commands/review.md:22` | Spec gate가 `approved-for-plan` 설정 | 일치 |
| `README.md:692`, `commands/README.md:43`, `help.md:50`, `recommend.md:36` | "PRD or feature doc" 등 한 줄 설명 | 일치(관문 미언급) |
| `docs/index.html` | roadmap 관문 언급 없음 | 해당 없음 |
| `CHANGELOG.md:13` (Unreleased) | 이번 항목 | 일치 |
| `CHANGELOG.md:301` (출시됨) | 이전 동작 기록 | 이력, 수정 대상 아님 |

## 이 브랜치 밖

- `README.md:313`과 `:461`은 "`/sc:plan` Load step stops on a spec still `status: draft`"라고 적는다. plan은 draft design에서 멈추지 않으므로(97cbac42 이후) "discovery spec"이 정확하다. roadmap과는 무관한 기존 부정확성이다.
- `RULES_DOCS.md:81`의 "Design spec committed" 전제는 plan과 roadmap 어느 쪽 흐름에도 확인 단계가 없다. 기존 상태이며 이번 변경과 무관하다.
