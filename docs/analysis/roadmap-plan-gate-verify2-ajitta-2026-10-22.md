---
status: complete
revised: 2026-10-22
---

# roadmap-plan-gate 독립 검증 2차

대상: `verify/roadmap-plan-gate-2` e03e1889. 1차 발견을 수락 기준으로 삼았고, 반영 표는 믿지 않고 항목마다 다시 확인했다.

**판정: 통과**

1차의 Important(G1)를 포함한 다섯 항목이 모두 해결됐다. 이제 roadmap.md, plan.md, RULES_DOCS workflow_gates, README, CHANGELOG가 관문을 같은 내용으로 적는다. 남은 것은 제안 셋이며 모두 문구 정리 수준이다.

## 게이트 실행

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3864 passed, 3 skipped, exit 0 |
| `make lint` / `make typecheck` / `ruff format --check src tests` | All checks passed! / no issues in 54 files / 223 files already formatted |
| `git diff v4.34.2 HEAD --stat -- core hooks.json commands` | `core/rules/RULES_DOCS.md`, `commands/roadmap.md`(각 2줄) |
| `evals/changed_command_probes.py` | 세 roadmap 프로브 |

카나리: `core/`와 `roadmap.md`가 바뀌었으므로 릴리스 전에 `make canary-gates`와 `make canary-commands`(세 roadmap 프로브)가 필요하다. 둘 다 운영자가 e03e1889에서 돌리고 있어 여기서는 실행하지 않았다.

## G1–G5

| 항목 | 판정 | 근거 |
|---|---|---|
| G1 RULES_DOCS workflow_gates | 해결 | `RULES_DOCS.md:81`이 Areas of concern을 넘기는 자리로 "the /sc:plan Load step or the /sc:roadmap Analyze step"을 적는다. `roadmap.md:13`의 질문과 `plan.md:13`의 질문에 맞는다. `:82`는 더 이상 "rather than a design spec"이라고 적지 않고 "from the design or from a PRD/feature doc"이라고 적는다. 그래서 roadmap.md(design을 소스로 받아 승인함)와 README `:692`, `design.md:62` handoff(`/sc:plan /sc:implement /sc:roadmap`)와 모순되지 않는다. 다른 gate 줄과도 충돌이 없다. 다만 PRD 입력에 "same gate"가 걸리는 것처럼 읽힐 여지는 남았다(제안 1) |
| G2 소스 순서와 승인 범위 | 해결 | `roadmap.md:13`의 순서(넘겨받은 문서 → `04-design.md` → `01-discovery.md` → 설명)는 `plan.md:13`과 같다. 승인 대상은 `:18` "the design doc that is the Analyze step's source"다. 경우별 확인: (a) `01-discovery.md`(approved)를 넘기면 소스가 discovery라 옆의 draft design은 draft로 남는다. (b) feature 이름을 넘기면 소스가 `04-design.md`라 승인되고, `01-discovery.md`가 draft면 discovery 관문이 먼저 멈춘다. (c) PRD 경로를 넘기면 design이 소스가 아니어서 승인되는 design이 없다. discovery 관문은 여전히 "Whatever the source"로 소스와 무관하게 걸리고, 열거된 두 경우(소스 문서, feature 폴더의 `01-discovery.md`)도 그대로라 새로 빠지는 경우는 없다. 설명 fallback은 예시 `'user auth system'`과 맞는다. error-path 예시는 입력이 아예 없는 경우다 |
| G3 새 `.py` | 해결 | `tasks.yaml:572` `file_absent_glob '**/*.py'`, `exclude_baseline: true`. `run_eval.py:510-518`은 workspace 전체를 glob하고 `git ls-tree HEAD`를 뺀다(fixture의 `report.py`는 baseline). `:636`에 같은 형태의 선례가 있다. 테스트는 `report.py`를 복원한 뒤 green을 확인하고, `export_csv.py`를 만들면 red가 되는지 확인한다(`test_eval_harness.py:1480-1485`) |
| G4 check별 변이 | 해결 | 세 작업의 check 14개를 하나씩 지웠다(YAML을 로드해 alias를 펼친 뒤 다시 dump). `pytest … -k roadmap`이 14번 모두 red였다(각 1 failed, 2 passed). 대조군(변이 없이 다시 dump한 파일)은 3 passed다. 복원은 `git checkout HEAD -- evals/tasks.yaml`로 했고, 복원 후 status는 깨끗하다 |
| G5 README | 해결 | `README.md:313`의 "the `/sc:plan` and `/sc:roadmap` gates stop on a discovery spec still `status: draft`, which only this review clears"는 `plan.md:13`, `roadmap.md:13`, 그리고 `brainstorm.md:31`(review만 `approved-for-plan`을 설정)과 맞는다. `:461`의 "`/sc:plan` stops on a draft discovery spec"도 맞다. `README.md`와 `docs/index.html`을 grep해 보니 옛 문구("draft spec", "Load step stops")로 관문을 적은 곳은 없다. `index.html`에는 관문 서술이 없다 |

## 관문 서술 위치 대조

| 위치 | 내용 | 일치 |
|---|---|---|
| `plan.md:13`, `:18` | 소스 순서, draft discovery면 멈춤, concern 질문, Load가 읽은 design 승인 | 기준 |
| `roadmap.md:13`, `:18` | 같은 순서와 멈춤, draft design은 멈추지 않음, 소스인 design 승인 | 예(승인 문구만 다름, 이 브랜치 밖 참고) |
| `RULES_DOCS.md:81-82` | concern을 넘기는 자리 둘, roadmap은 같은 gate | 예(제안 1) |
| `README.md:313`, `:461` | discovery spec 관문 | 예 |
| `CHANGELOG.md:13-14` | 아래 참고 | 예 |
| `brainstorm.md:18`, `:75`, `RULES_DOCS.md:80` | review는 `/sc:plan` 전에 필수 | 모순 없음(roadmap은 이름이 없음, 이 브랜치 밖 참고) |
| `tasks.yaml:508-513` 주석 | 소스든 옆이든 멈춤, "the design it built on" 승인 | 예 |

CHANGELOG `[Unreleased]`는 G2 이후에도 정확하다. "the roadmap builds on it and moves it to `approved-for-plan`"에서 "it"은 roadmap이 바탕으로 삼은 design, 곧 소스다. 옆에 있기만 한 design을 승인한다고 적은 곳은 없다.

## 새 발견

1. **Suggestion** — `RULES_DOCS.md:82`: "from the design or from a PRD/feature doc; the same gate as /sc:design -> /sc:plan"을 PRD 입력에도 그 gate("Design spec committed …")가 걸린다고 읽을 수 있다. 화살표가 `/sc:design ->`이라 범위가 정해지고, roadmap.md에 PRD 예시가 있으니 모순까지는 아니다. 수정: "from the design (the same gate as /sc:design -> /sc:plan) or from a PRD/feature doc".
2. **Suggestion** — `docs/analysis/roadmap-plan-gate-ajitta-2026-10-22.md:16`(변경 절)은 아직 "Analyze 단계가 읽은 design"을 승인한다고 적고, 소스 순서는 적지 않는다. 55d8762b 당시 상태를 기록한 것이고 좁힌 내용은 같은 문서의 반영 표에 있으므로 거짓 기록은 아니다. 다만 변경 절만 읽으면 현재 동작으로 오해할 수 있다. 수정: 그 줄 끝에 "(독립 검증 반영에서 '소스인 design'으로 좁힘)"을 덧붙인다.
3. **Suggestion** — `roadmap-design-draft` 프로브는 소스가 design인 경우(G2 (b))만 잰다. (a), 즉 approved discovery를 넘기고 옆에 draft design이 있으면 design이 draft로 남는 경우는 프로브도 단위 테스트도 없다. 관찰된 실패가 없고 plan에도 대응 프로브가 없으므로 지금은 두어도 된다.

Critical과 Important는 없다.

## 이 브랜치 밖

- `plan.md:18`은 "the design doc the Load step read"이고 `roadmap.md:18`은 "that is the Analyze step's source"다. 소스 순서가 같아서 동작은 같지만, plan 세션이 맥락 확인용으로 옆의 design을 읽으면 plan 쪽 문구로는 그 design도 승인 대상이 된다. 두 문구를 "source"로 맞추면 1차 G2와 같은 틈이 plan에서도 닫힌다.
- `brainstorm.md:18`, `:75`와 `RULES_DOCS.md:80`은 review를 "/sc:plan 전"에만 필수로 적는다. roadmap은 스스로 멈추므로 출구 없는 상태는 생기지 않는다. 다만 brainstorm이 roadmap으로 넘기는 경로를 금지하는 문구는 없다.
