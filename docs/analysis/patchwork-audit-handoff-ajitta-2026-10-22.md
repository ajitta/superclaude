---
status: complete
revised: 2026-10-22
---

# 누더기 감사: v4.34.2 이후 미출시 작업 (95d5f73b)

**판정: 조건부 통과. Critical 0, Important 2, Suggestion 6.** 출하 문장의 증가분은 대부분 규칙을 싣고 있고, 프로브 측정(design-draft 0/3 → 3/3, Proof 0/6 → 3/3)이 그 근거다. 누더기는 세 곳에 몰려 있다. 라운드마다 괄호를 하나씩 더한 plan 문서 정의(세 벌), 한 라운드에 assert를 하나씩 더한 가드, 되돌린 규칙을 아직 현재형으로 적은 분석 기록이다. 정의는 단계 파일을 빼면서 단계 파일로 일한 작업이 /sc:reflect를 건너뛰는 읽기를 남겼다. 이것이 출하 문장의 유일한 Important다.

## 범위와 실행

- 범위: `git diff v4.34.2 HEAD`(커밋 39개, 34파일, +1692/−31). 라운드별 재검증 없이 최종 상태만 읽었다.
- `uv run pytest -q`: 3866 passed, 3 skipped(exit 0). `make lint`: All checks passed. `make typecheck`: 54 files, no issues.
- 아래 다시 쓰기 A와 가벼운 가드는 `$TMPDIR` 사본(`git archive HEAD`)에 적용해 `test_docs_ssot_guards.py`, `test_command_structure.py`, `test_cross_references.py`를 돌렸다: 1111 passed. 사본의 reflect.md에서 "split plan's phase file"을 지우면 `test_review_reflect_gate_anchors[reflect Plan-Close]`가 red다. 워크트리는 이 보고서 외에 바꾸지 않았다.

### 단계별 길이 (v4.34.2 → 지금, 바이트)

| 위치 | 전 | 후 | 판단 |
|---|---|---|---|
| `roadmap.md:13` Analyze | 190 | 657 | 규칙(소스 순서, discovery 관문, design 비차단). no-op 두 구절 |
| `roadmap.md:17` Validate | 350 | 562 | 규칙(Proof). 뒤 절은 하류 설명 |
| `roadmap.md:18` Document | 367 | 631 | 규칙(design 승인) |
| `reflect.md:19` Plan-Close | 1361 | 1477 | +116 전부 정의 괄호 |
| `test.md:17` Report | 385 | 501 | +116 같은 괄호 |
| `test.md:40` Agent | 335 | 366 | 규칙(경로 전달) |
| `implement.md:19` Integrate | 1635 | 1666 | +31, 규칙 |
| `RULES_DOCS.md:82–87` 관문 4줄 | 650 | 901 | 규칙 + 같은 괄호 |
| 명령 파일 전체: roadmap 4255→5189, reflect 4122→4238, test 3686→3833, implement 5855→5886, review 7763→7774, plan 불변 | | | |

## 발견

**1. Important — plan 문서 정의가 단계 파일로 한 작업을 /sc:reflect 밖으로 보낸다.**
`reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87`이 같은 172바이트 괄호를 싣는다: "a feature folder's `05-plan.md` or another `05<letter>-plan-*.md` plan that is not a split plan's phase file (one its index lists with a checkbox), or a `docs/plans/` plan". 괄호 안에 괄호가 있고, 2차·3차 라운드가 한 절씩 붙인 결과다. 문제는 의미다. `implement.md:13`은 분할 plan의 각 단계 파일을 그 단계가 시작할 때 읽게 한다. 그래서 세션은 단계 파일로 일한다. 그런데 정의는 단계 파일을 plan 문서에서 뺀다. 글자 그대로 읽으면 단계 파일로 한 작업은 "plan 문서로 한 작업"이 아니다. `/sc:test`는 "other work is done here"로 끝내고(`RULES_DOCS.md:87`), Plan-Close는 돌지 않는다. 의도는 "단계 파일은 따로 세는 plan이 아니라 인덱스에 속한다"였다(`reflect.md:19`의 "check its plan (index)"). 관찰된 실패는 없다. 다시 쓰기 A가 의도대로 고친다.

**2. Important — 분석 기록이 되돌린 규칙을 현재형으로 적는다.**
`docs/analysis/command-handoff-graph-ajitta-2026-10-22.md`:
- `:280`(2차 4번 행) "Plan-Close는 '폴더의 다른 plan 문서가 모두 `complete`일 때'만 README를 `complete`로 바꾼다", `:289`(3차 1번 행) "Plan-Close는 'other plan documents with task boxes …'일 때 README를 바꾼다 … 둘 다 가드에 넣었다". 둘 다 4차(95d5f73b)에서 되돌렸다. 지금 `reflect.md:19`과 `RULES_DOCS.md:33`은 "plan (index) `status: complete` → complete"다.
- `:267`(1차 행) "정의에 'a roadmap's `05<letter>-plan-workflow.md`'를 넣었다. 가드는 세 곳이 그 이름을 적는지 본다". 2차에서 역할 정의로 바뀌었고 그 가드는 없다.
- `:292`(3차 4번 행) "'whose path it is passed'를 넣고". 4차에서 "pass it that path"로 바뀌었다.
- `:8` 상단 "지금 상태(5b28dd7e 이후)"는 그 뒤 네 라운드(역할 정의, README 규칙 도입과 되돌림)를 말하지 않는다. 처음 읽는 사람은 표를 위에서 읽다가 `:299`에 가서야 되돌림을 안다.
- 파일 크기 28,715바이트로 RULES_DOCS Size 목표(25,000)를 넘었다. 2·3·4차 추가가 모두 목표를 넘은 뒤의 추가다.
`roadmap-plan-gate-ajitta-2026-10-22.md`는 문제없다. 좁힌 내용을 변경 절에 표시했다.

**3. Suggestion — 가드가 라운드마다 assert 하나씩 자랐다.**
`tests/unit/test_docs_ssot_guards.py:686–718`의 한 테스트에 assert 12개(정의 루프 셋 포함). 문장 통째 고정("End the doc with a `## Proof` footer that names the command", 172바이트 정의 구절 ×3), 되돌린 문구가 다시 오지 않는지 보는 부정 고정(`:711` `"with task boxes" not in rules`), 리뷰 이력 주석(`:709` "round 4")이 섞였다. 같은 파일에 이미 앵커 기반 장치 `_GATE_ANCHORS`(`:525`)가 있고 `test.md`·`reflect.md`·RULES_DOCS 관문을 읽는데, 이 테스트는 그 옆에서 같은 텍스트를 따로 읽는다. `_handoff`(`:678`)는 `:750`의 정규식을 한 번 더 쓴다. 정의 문구를 한 단어 바꾸면 세 assert가 함께 깨진다. 아래 "가벼운 가드"가 대안이다.

**4. Suggestion — CHANGELOG `[Unreleased]` Changed 두 번째 항목이 961바이트에 변경 다섯을 담는다.**
`CHANGELOG.md:14`: Proof 꼬리말, implement로만 핸드오프, review → design, `05a-plan-….md`가 plan 문서, README 첫 박스. 사용자 동작으로 쓰였고 되돌린 규칙은 적지 않아 사실은 맞다. 다만 "counts as a plan document"는 내부 용어이고, 한 문단이라 무엇이 바뀌었는지 훑어볼 수 없다. `:15` 기여자 줄은 같은 범위에서 더한 프로브 `reflect-plan-close-no-record`(9bf0bdac)를 빠뜨렸다. 다시 쓰기 C.

**5. Suggestion — roadmap Analyze·Validate에 결과를 바꾸지 않는 절이 있다.**
`roadmap.md:13` "Parse it and understand the requirements"는 모델이 어차피 하는 일이다. "the same review gate /sc:plan applies"는 plan.md가 로드되지 않는 세션에서 내용 없는 포인터다. 원래 버그(67215cd7)가 바로 이 주장만 있고 내용이 달랐던 것이다. 지금은 내용이 같으니 해는 없다. `roadmap.md:17` "; /sc:implement --plan runs it after the last box and records `Result:`, as for a /sc:plan plan"은 하류 명령의 동작을 설명한다. 측정은 이 문장까지 포함해 3/3이었으므로 줄이면 canary를 다시 돌려야 한다. 다시 쓰기 D(보류 권장).

**6. Suggestion — 테스트 docstring이 CHANGELOG와 어긋난다.**
`tests/unit/test_insight_writer.py:1824` "every hook goes through build_parser". 등록된 훅은 모두 `*-from-hook`이고(`hooks.json:35,47,59,149`), `insight_writer.py:849–880`이 `build_parser` 전에 처리한다. CHANGELOG `:19` "The insight hooks were not affected"가 맞다. docstring을 "`superclaude insight` goes through build_parser"로 고친다.

**7. Suggestion — review 핸드오프가 다섯 개다.**
`review.md:76` `next="/sc:plan /sc:design /sc:implement /sc:test /sc:troubleshoot"`. command-authoring.md는 "2-3 natural next commands"라고 한다. 원래 넷이었고 강제하는 테스트는 없다. /sc:design 추가는 소유자 결정이다.

**8. Suggestion — plan Save와 roadmap Document의 승인 대상 문구가 다르다.**
`plan.md` Save는 "the design doc the Load step read", `roadmap.md:18`은 "A design doc that is the Analyze step's source"다. roadmap-plan-gate 기록 끝에 "plan.md를 다음에 건드릴 때"로 대기 중이다. 두 명령이 "같은 관문"이라는 주장의 유일한 남은 틈이다.

## 다시 쓰기

### A. plan 문서 정의 (세 곳, 발견 1)

`reflect.md:19`, `test.md:17`, `RULES_DOCS.md:87`의 괄호 안을 각각 아래로 바꾼다. 172 → 183바이트. 역할 기준 정의와 인덱스 체크박스 기준은 그대로 두고, 단계 파일을 "제외"에서 "인덱스로 센다"로 바꾼다. `_SOFTENER` 단어는 없다.

```text
전: a feature folder's `05-plan.md` or another `05<letter>-plan-*.md` plan that is not a split plan's phase file (one its index lists with a checkbox), or a `docs/plans/` plan
후: a feature folder's `05-plan.md` or another `05<letter>-plan-*.md` plan, or a `docs/plans/` plan; a split plan's phase file, one its index lists with a checkbox, stands for that index
```

`reflect.md` Plan-Close의 "check its plan (index)", `implement.md`의 "the plan's (index's) last box"와 그대로 맞물린다. README 규칙(plan (index) `complete` → README `complete`)은 건드리지 않는다.

### B. handoff-graph 기록 (발견 2)

본문은 이력이므로 고쳐 쓰지 않는다. 상단 `:8`을 아래로 바꾸고, 행 네 개 끝에 표시만 단다.

```text
**지금 상태(95d5f73b):** G1의 Proof 꼬리말, G2, G3의 review → design 핸드오프, G5는 해결됐다. plan 문서는 역할로 정의한다(05 슬롯의 plan, 분할 plan의 단계 파일은 제외). README `phase:`는 plan (index) 하나가 `complete`가 되면 `complete`가 된다. 2·3차에서 들인 "폴더의 다른 plan이 모두 끝나야" 규칙은 4차에서 되돌렸다. G1의 `Evidence:` 규칙, G3의 체인 기준(D2), G4, G6–G10은 열려 있다. 아래 표의 각 행은 그 라운드 시점의 처리이며, 뒤 라운드가 바꾼 행은 표시했다.
```

행 표시: `:267` 끝에 "(2차에서 역할 정의로 바뀜)", `:280`과 `:289` 끝에 "(4차에서 되돌림)", `:292` 끝에 "(4차에서 'pass it that path'로 바뀜)". 크기는 분할하지 않는다. 이 수정은 수백 바이트이고 문서는 닫혔다(`status: complete`).

### C. CHANGELOG `[Unreleased]` Changed (발견 4)

`:13`은 그대로 두고 `:14–15`를 아래로 바꾼다.

```markdown
- A roadmap written by `/sc:roadmap` now ends with a `## Proof` footer: the command that proves the workflow done and its expected output, as in a `/sc:plan` plan. `/sc:implement --plan` runs it after the last box and records the `Result:` line that `/sc:reflect` checks before the plan can be marked `complete`.
- `/sc:roadmap` now hands off to `/sc:implement` only; `/sc:task` does not read the roadmap document. `/sc:review` also suggests `/sc:design`, the step after a spec review in the Large chain.
- A second plan in a feature folder (`05a-plan-….md`, such as a roadmap written beside an existing plan) now goes through `/sc:reflect` and Plan-Close like `05-plan.md`. A split plan's phase files still belong to their index.
- The first checked box no longer moves a README that is already `complete` back to `implementing`.
- For contributors: new canary probes `roadmap-draft-spec-gate`, `roadmap-design-discovery-draft`, `roadmap-design-draft` (which also requires the Proof footer) and `reflect-plan-close-no-record`.
```

### D. roadmap Analyze·Validate (발견 5, 보류 권장)

```text
1. Analyze: Read the source: the PRD or doc passed in; else the feature folder's `04-design.md` (fallback `01-discovery.md`); else the user's description. A discovery spec still `status: draft` — the source, or the folder's `01-discovery.md` even beside a `04-design.md` — stops it: point to `/sc:review --scope spec <path>`, the same review gate /sc:plan applies. A design doc (`04-design.md`, or a `docs/specs/*-design-*.md`) does not stop it for being `draft`; one with unresolved "Areas of concern" → say so and ask whether to build the workflow anyway
```

657 → 565바이트. 관문 포인터는 소유자 결정의 흔적이라 남겼다. Validate의 Proof 절은 "End the doc with a `## Proof` footer that names the command proving the whole workflow done and its expected output, the one /sc:implement --plan runs after the last box." (562 → 521바이트).

## 가벼운 가드 (발견 3)

`test_roadmap_and_review_handoffs_follow_the_chain`(`:686–718`)을 아래로 바꾸고, 정의 앵커는 기존 `_GATE_ANCHORS`로 옮긴다. 앵커는 지금 문장과 다시 쓰기 A 둘 다에서 통과한다. 위 사본 실행에서 확인했다. 부정 고정과 라운드 주석은 없앤다. README 규칙은 긍정 고정 하나로 지킨다.

```python
# _GATE_ANCHORS: append to the existing lists
#   "gates":              "`05<letter>-plan-*.md`", "split plan's phase file",
#                         "/sc:roadmap -> /sc:implement --plan",
#   "test Report":        "`05<letter>-plan-*.md`", "split plan's phase file",
#   "reflect Plan-Close": "`05<letter>-plan-*.md`", "split plan's phase file",
#   "implement Integrate": "when it is not already further",


def test_roadmap_and_review_handoffs_follow_the_chain():
    """A roadmap is a 05-slot plan: it ends with the Proof /sc:implement --plan
    runs and hands off to /sc:implement only. Spec review hands off to
    /sc:design. The plan-document definition is in _GATE_ANCHORS."""
    assert "`## Proof` footer" in _read(_SRC / "commands" / "roadmap.md")
    assert _handoff("roadmap") == ["/sc:implement"]
    assert "/sc:design" in _handoff("review")
    assert "the plan doc the work ran from" in _read(_SRC / "commands" / "test.md")
    rules = _read(_SRC / "core" / "rules" / "RULES_DOCS.md")
    assert "| plan (index) `status: complete` → complete" in rules
```

assert 12 → 5개(앵커 8개는 기존 parametrize에 들어가 위치별로 실패를 보고한다). `:750`도 `_handoff("test")[0]`로 바꿀 수 있지만 이 범위 밖이다.

## 유지 목록 (정당한 반복)

- **정의가 `test.md`·`reflect.md`에 한 벌씩**: `context_loader.py:191`은 RULES_DOCS를 plan·roadmap·design 등에만 주입하고, `:181`의 test·reflect·implement에는 주입하지 않는다. 두 명령은 정의를 직접 들고 있어야 한다. RULES_DOCS 관문 줄은 plan·roadmap 세션의 SSOT다.
- **roadmap Analyze가 plan Load 관문을 다시 적음**: roadmap 세션에 `plan.md`는 로드되지 않는다(소유자 결정 A). "does not stop it for being `draft`"는 측정된 실패(0/3)를 막는 부정문이다.
- **implement의 "when it is not already further"(+31B)**: RULES_DOCS의 "never moves back"이 implement 세션에 로드되지 않는다.
- **-OO 대응 세 곳**(`insight_writer.py:779`, `run_eval.py:688`, 테스트 두 곳): 각 한 줄 주석, 비례에 맞다.
- **run_eval runs-dir 거부**(`run_eval.py:768–780`): 증거 덮어쓰기를 막는 단일 검사와 테스트 하나.
- **tasks.yaml 측정 주석**(`:512`, `:824`): v4.34.2에 이미 같은 관용이 24곳 있다. 프로브가 왜 있는지를 알려 준다.
- **Proof 채점기의 백틱 휴리스틱**(`tasks.yaml:591`): 백틱 하나면 통과하는 한계는 기록에 적혀 있고, 기록의 2차 처리가 "정규식으로 가를 수 없으니 더 조이지 않는다"고 정했다. 새 lint 인프라 금지와도 맞다.
- **README 두 줄 수정**: "discovery spec"으로 좁힌 것은 출하 문장과 맞다.

## 소유자 결정

1. 다시 쓰기 A(정의, 단계 파일은 인덱스로 센다)를 적용할지. ★ 적용한다. `fix/*` 브랜치에서 세 파일과 가드를 한 커밋에. `core/`가 바뀌므로 릴리스 전 `make canary-gates`와 `make canary-commands`.
2. 가드를 앵커로 가볍게 바꿀지. ★ 1과 같은 커밋에서 바꾼다. A를 하면 지금 가드의 정의 고정 세 줄이 어차피 깨진다.
3. 분석 기록 B(상단 줄 + 행 표시)를 할지, 본문을 다시 쓸지. ★ B만 한다. 이력은 남기고 현재 상태만 바르게 한다. 크기 분할은 하지 않는다.
4. CHANGELOG C를 적용할지. ★ 적용한다. 릴리스 노트는 사용자가 읽는 첫 표면이다.
5. roadmap D(no-op 절 삭제)를 지금 할지. ★ 보류한다. 얻는 것은 133바이트이고, 측정된 문장을 바꾸므로 canary를 다시 돌려야 한다. 다음에 `roadmap.md`를 건드릴 때 함께 한다.
6. `test_insight_writer.py:1824` docstring을 고칠지. ★ 고친다. 1과 같은 커밋이면 충분하다.
7. review 핸드오프 다섯 개를 줄일지. ★ 그대로 둔다. /sc:design은 소유자 결정이고, 나머지 넷 중 뺄 근거가 관찰되지 않았다.
8. plan.md Save의 "source" 좁히기(발견 8). ★ 대기 목록대로 다음 `plan.md` 수정 때 한다.
