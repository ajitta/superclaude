---
status: draft
revised: 2026-10-04
---

# 플래그 참조 검사 Implementation Plan

**Goal:** 명령 본문이 flow 단계, 섹션, gotcha를 가리키는 참조를 테스트가 검사할 수 있는 형식으로 바꾼다. 아울러 전역 플래그 이름에 자기 값을 주는 명령에 `<flags>` 항목이 없으면 테스트가 잡게 한다. business-panel `<flags>`는 다른 명령 형식에 맞추고 `--focus`를 정의한다.

**Architecture:** `tests/unit/test_command_structure.py`에 검사 네 개를 더한다. (1) 본문에 `step <숫자>`가 없다. (2) "the X step"은 그 명령(`/sc:<name>`이 붙으면 그 명령)의 flow에 있는 `N. X:` 줄로 해석된다. (3) `<flags>`의 section·table·gotcha·pattern·threshold·tools entry 참조가 실제 태그나 항목으로 해석된다. (4) `<syntax>`가 전역 플래그에 `core/FLAGS.md`가 허용하지 않는 값을 주면(값을 받지 않는 전역 플래그에 값을 주는 경우 포함) `<flags>` 항목이 있어야 한다. 명령 마크다운을 이 형식에 맞추고, commands 밖의 번호 참조 2개는 손으로 고친다. hook 코드는 바꾸지 않는다.

**Tech Stack:** pytest, 명령 마크다운

## 근거

- 선행 작업: [command-local-flags 계획](../../plans/command-local-flags-ajitta-2026-10-04.md), 리뷰 후속 커밋 `eafd5e96`.
- 단계 번호 참조가 16개 명령에 29개 있다(`<flags>` 안 23개, 밖 6개). 이 중 review.md:21은 다른 명령(brainstorm)의 단계 번호를 가리킨다. commands 밖에도 2개 있다: `src/superclaude/core/rules/RULES_DOCS.md:67`(brainstorm 6단계)과 `.claude/rules/gotchas/general.md:21`(implement 4단계). flow 순서가 바뀌면 참조가 조용히 틀어지고, 이를 잡는 테스트가 없다.
- "the X step" 형식의 이름 참조는 3개(implement `the Validate step`, save `the Checkpoint step`, troubleshoot `the Test, Fix and Verify steps`)이고 모두 해석된다. 라벨만 쓴 참조도 4개 있다: save.md:16 `per /sc:reflect Misunderstanding-Audit`, review.md:21 `read at Gather`, troubleshoot.md:25 `stop after Confirm`, auto-improve.md:67 `skip Phase 0 confirm`. 이 4개는 테스트가 보지 못한다.
- `<flags>`의 섹션류 참조 26개는 아래 규칙으로 모두 해석된다(2026-10-04 scratchpad 시험 파서). 형식 밖 참조는 3개다: auto-improve `--eval-cmd`의 "(flow step 2, eval-cmd-blast-radius gotcha)", init `--quick`·`--full`의 "the menu". Phase 1이 이 3개를 형식 안으로 옮기므로 Phase 2 시점에는 29개다.
- Phase 2 검사는 대상 이름이 바뀌는 경우만 잡는다. `eafd5e96`에서 고친 troubleshoot의 "per the rule in the command description" 같은 서술형 참조는 형식 밖이라 작성 규칙으로만 막는다.
- spec-panel `--focus`는 전역 이름에 자기 값을 쓰는데도 b6026ba2에서 항목이 빠졌다. 구조 테스트가 전역 이름을 검사에서 빼기 때문이다(`eafd5e96`에서 수정). 같은 검사로 보면 지금은 analyze `--focus`의 `rules`만 걸린다. 값을 받지 않는 전역 플래그에 값을 주는 implement `--plan`은 항목이 있지만, 지우면 어떤 테스트도 실패하지 않고 hook이 전역 `--plan` 지시문을 다시 주입한다(`context_loader.py:883`, `:909`).

## 결정 (2026-10-04 인터뷰)

- flow는 번호 목록을 유지한다. 번호를 빼는 실익이 아직 없다. 이 계획의 라벨 정규식과 작성 규칙은 이 결정을 전제로 한다.
- 단계 참조는 이름으로 쓰고 테스트로 검사한다. 이름이 없는 단계에는 이름만 붙이고 문장은 그대로 둔다(prompt 1–7, auto-improve 1·4).
- 테스트 범위: `<flags>`와 본문 전체의 단계 참조, `<flags>`의 섹션류 참조.
- 전역 플래그 값 목록 비교 테스트를 둔다. analyze `--focus`에 항목을 추가한다.
- business-panel: `<flags>` 형식을 다른 명령과 맞춘다. `--focus`는 `--experts`가 없을 때만 전문가를 고르고, `--experts`나 `--all-experts`가 있으면 무시한다.

## 범위 밖

- `<flags>` 밖의 섹션 참조와 파일 경로 참조(`modes/RESEARCH_CONFIG.md` 등).
- 아래 형식에서 벗어난 참조. 테스트는 이를 찾지 못하므로 command-authoring.md 규칙으로만 막는다.
- commands 밖 파일의 단계 참조 검사. 지금 있는 2개는 Task 1.3에서 손으로 고치고, 테스트는 commands만 본다.
- 값 없이 전역 이름에 자기 뜻을 주는 경우(reflect `--validate`)의 항목 검사. Phase 3는 `<syntax>`가 값을 줄 때만 본다.
- 참조되지 않는 flow 단계의 이름(prompt·auto-improve 외 단계 이름 의무화).
- agents·modes 본문, hook 코드.

## Phase 0: 브랜치

- [x] master에서 `git switch -c docs/flag-pointer-checks`. 이 계획서와 README(untracked)는 Phase 1 커밋에 넣는다.

## Phase 1: 단계 참조를 이름으로 (커밋 1개)

### Task 1.1: 단계 참조 테스트

**Files:** Test: `tests/unit/test_command_structure.py` (새 클래스 `TestCommandStepRefs`)

- [x] Step 1: 테스트를 쓴다. 블록 추출은 기존 `md_helpers.extract_xml_content`를 쓴다.
  - `_flow_labels(content) -> set[str]`: `<flow>` 블록에서 `re.M`으로 `^\s*\d+(?:\.\d+)?\.\s+(.+?):` 줄의 첫 `:` 앞을 이름으로 잡는다. 괄호 부분(`\s*\(.*?\)`)을 지우고 소문자로 바꾼다. `Load (Serena)`는 `load`, `2.5. Misunderstanding-Audit:`은 `misunderstanding-audit`가 된다.
  - `test_no_numbered_step_refs`: `re.findall(r"\bsteps? \d+", content)`가 비어 있어야 한다. 소문자만 본다(plan.md `<templates>`의 `Step 1:`은 대상이 아님).
  - `test_named_step_refs_resolve`: `` \b[Tt]he (?:(/sc:[a-z][\w-]*) )?([A-Z`][^.;:()|\n]*?) steps?\b ``에 맞는 참조마다 이름을 `\s*,\s*(?:and\s+)?|\s+and\s+`로 나눈다. `/sc:<name>`이 붙으면 `COMMANDS_DIR / f"{name}.md"`가 있어야 하고(assert), 없으면 자기 자신이 대상이다. 각 이름(소문자)이 대상의 `_flow_labels`에 있어야 한다. 소문자로 시작하는 문구(git의 "the operation step by step")는 대상이 아니다.
- [x] Step 2: `uv run pytest tests/unit/test_command_structure.py -k StepRefs -q`. `test_no_numbered_step_refs`가 16개 명령에서 실패하고, `test_named_step_refs_resolve`는 통과해야 한다(기존 3개).

### Task 1.2: flow 이름과 명령 안 참조 교체

**Files:** Modify: `src/superclaude/commands/` 아래 18개 명령

- [x] Step 3: 이름이 없는 단계 앞에 이름을 붙인다. 문장은 그대로 둔다.
  - prompt.md flow: `Capture:` `Resolve:` `Diagnose:` `Apply:` `Rewrite:` `Report:` `Emit:` (1–7)
  - auto-improve.md flow: 1 `Parse:`, 4 `Print:`
- [x] Step 4: 참조를 바꾼다. "바꾸기 전" 문구가 한 파일에 여러 번 나오면(init·insight·promote-feature·prompt) 모두 바꾼다. review.md:21은 매우 긴 줄이라 Grep content 모드에서 안 보일 수 있다(`grep-longline-blindspot`). Read로 확인하고 Edit로 고친다.

| 위치 | 바꾸기 전 | 바꾼 뒤 |
|---|---|---|
| analyze:23 | runs flow step 5 | runs the Report step |
| auto-improve:23 | ` (flow step 2, eval-cmd-blast-radius gotcha)` (앞 공백 포함) | `; see the Phase 0 confirm step and the eval-cmd-blast-radius gotcha` |
| auto-improve:24 | required by flow step 1 | required by the Parse step |
| auto-improve:30 | the status branch in flow step 5 | the `` `--status` `` branch step |
| auto-improve:67 | skip Phase 0 confirm, | skip the Phase 0 confirm step, |
| brainstorm:25 | set in flow step 2 (Analyze) | set in the Analyze step |
| brainstorm:31 | from step 5 forbidden | from the Approve step forbidden |
| brainstorm:40 | handoff (step 8) | handoff (the Handoff step) |
| build:23 | runs flow step 4 (Optimize) | runs the Optimize step |
| cleanup:21 | and flow step 3 | and the Execute step |
| explain:21 | that flow step 2 otherwise infers | that the Assess step otherwise infers |
| implement:56 | checkpoint (flow step 3) | checkpoint (the Checkpoint step) |
| init:22-23 | defined in flow step 3 and the menu | defined in the Select step and the menu section |
| insight:23-25 | defined in flow step 6 | defined in the Read modes step |
| insight:26 | defined in flow step 7 | defined in the Review mode step |
| load:25 | the structure flow step 4 always reports | the structure the Discover step always reports |
| plan:22 | read in flow step 1 | read in the Load step |
| pm:22 | the strategy flow step 2 otherwise picks | the strategy the Strategy step otherwise picks |
| promote-feature:24-25 | defined in flow step 3 | defined in the Confirm step |
| prompt:24-25 | resolved in flow step 2 | resolved in the Resolve step |
| review:21 | (per /sc:brainstorm step 7 heuristic) | (per the /sc:brainstorm Decision-mode tag step heuristic) |
| review:21 | already read at Gather | already read in the Gather step |
| review:27 | per flow step 8 | per the Delegated-decision audit step |
| review:43 | re-eval (step 8) | re-eval (the Delegated-decision audit step) |
| save:16 | per /sc:reflect Misunderstanding-Audit | per the /sc:reflect Misunderstanding-Audit step |
| task:23 | the execution order flow step 3 otherwise picks | the execution order the Strategy step otherwise picks |
| task:74 | checkpoint (flow step 4) | checkpoint (the Checkpoint step) |
| troubleshoot:25 | stop after Confirm | stop after the Confirm step |

auto-improve:30 칸의 이중 백틱은 표 안의 마크다운 표기다. 파일에는 `--status`를 백틱 한 쌍으로 감싸 쓴다.

### Task 1.3: commands 밖 참조

**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md`, `.claude/rules/gotchas/general.md`

- [x] Step 5: 두 줄을 바꾼다. 테스트 대상은 아니다.
  - RULES_DOCS.md:67 `see brainstorm.md flow step 6` → `see the /sc:brainstorm Self-review step`
  - general.md:21 `(implement.md flow step 4, "mark tasks done as go")` → `(the /sc:implement Execute step, "mark tasks done as go")`

### Task 1.4: 작성 규칙

**Files:** Modify: `.claude/rules/command-authoring.md` (XML Rules)

- [x] Step 6: XML Rules를 세 군데 고친다.
  - `<flow>` 줄을 `` - `<flow>` — ≥2 numbered steps in execution order; a step that anything points at starts with `N. Label:` ``로 바꾼다.
  - 그 아래에 새 줄을 넣는다: `` - Step pointers — anywhere in the body, point at a flow step as `the <Label> step`, or `the /sc:<name> <Label> step` for another command's flow, never by number. `test_command_structure.py` rejects `step <N>` and resolves each such label; a bare label (`after Confirm`) goes unchecked. ``
  - `<flags>` 줄의 "gets a line pointing to that section by topic, not a restatement"를 "gets a line pointing to it (a flow step by its label, a section by topic), not a restatement"로 바꾼다. flow 단계를 가리키는 방법이 파일 안에서 하나가 되게 하기 위해서다.
- [x] Step 7: `uv run pytest tests/unit/test_command_structure.py -q` 통과, 이어서 `uv run pytest` exit 0.
- [x] Step 8: `make format && make lint` 후 커밋: `docs(commands): point at flow steps by label, not number`
- [x] Step 9: 이름 검사가 고장을 잡는지 일부러 깨 보고 되돌린다. brainstorm.md의 `5. Approve:`를 `5. Approval:`로, `7. Decision-mode tag:`를 `7. Decision mode tag:`로 바꾸면 brainstorm(같은 명령 참조)과 review(다른 명령 참조)가 실패해야 한다. 확인 후 `git checkout -- src/superclaude/commands/brainstorm.md`.

## Phase 2: `<flags>` 섹션 참조 검사 (커밋 1개)

### Task 2.1: 참조 해석 테스트

**Files:** Test: `tests/unit/test_command_structure.py` (새 클래스 `TestCommandFlagPointers`)

- [x] Step 1: `test_flags_pointers_resolve`를 쓴다. `<flags>` 블록에서 `` \bthe ([\w`/ -]+?) (section|table|gotcha|pattern|threshold|entry in (?:the )?tools(?: section)?)\b ``를 찾는다. 대상 이름은 잡힌 문구의 마지막 ` the ` 뒤다("the four modes in the modes section" → `modes`). 키는 이름을 소문자로 바꾸고 `-`와 공백을 `_`로 바꾼 것이다. 본문의 태그는 `re.M`으로 `^\s*<([a-z][\w-]*)[\s>]`에 맞는 줄 머리 태그다(`note=` 같은 속성은 허용하고, 문장 안의 `<focus>` 같은 자리표시자는 뺀다).

| 종류 | 해석 |
|---|---|
| section, table | 키와 같은 태그가 있거나, 키가 어떤 태그로 시작함 (`depth profiles` → `<depth>`, `expertise adaptation` → `<expertise_adapt>`) |
| threshold | `<{키}_threshold>` 태그가 있음 |
| gotcha | `<gotchas>`에 `- {이름}:` 항목이 있음 |
| pattern | `<patterns>`에 `{이름}`으로 시작하는 항목이 있음 |
| entry in tools | `<tools>`에 `- {이름}:` 항목이 있음 |

- [x] Step 2: 지금 내용으로는 통과해야 한다(29개). 테스트가 고장을 잡는지 일부러 깨 보고 되돌린다. plan.md:75의 gotcha 항목 `- phase-vs-pr:`만 `- phase-vs-prx:`로 바꾸고(:25의 참조는 그대로), spec-panel.md의 `<focus_areas>`와 `</focus_areas>`를 `<areas>`와 `</areas>`로 바꾸면 두 명령이 실패해야 한다. 확인 후 `git checkout -- src/superclaude/commands/plan.md src/superclaude/commands/spec-panel.md`.

### Task 2.2: 작성 규칙

- [x] Step 3: command-authoring.md의 `<flags>` 줄은 마침표 없이 `5-line plan)`으로 끝난다. 그 뒤에 마침표와 공백을 넣고 이어서 더한다: `` A pointer takes one of these forms, which `test_command_structure.py` resolves: `the <Label> step` (see Step pointers), `the <topic> section|table`, `the <name> gotcha`, `the <name> pattern`, `the <topic> threshold`, `the <Tool> entry in the tools section`; a pointer in any other form goes unchecked. ``
- [x] Step 4: `uv run pytest` exit 0, `make format && make lint`, 커밋: `test(commands): resolve section and gotcha pointers in <flags>`

## Phase 3: 전역 플래그에 자기 값 (커밋 1개)

### Task 3.1: 값 목록 비교 테스트

**Files:** Test: `tests/unit/test_command_structure.py` (`TestCommandFlagsAreDefined`에 추가)

- [x] Step 1: `test_global_flag_with_own_values_is_defined`를 쓴다.
  - `COMMANDS_DIR.parent / "core" / "FLAGS.md"`에서 `re.M`으로 `^(--[\w-]+(?:\|--[\w-]+)*)(?: \[([^\]]*)\])?:` 줄을 읽는다. `|`로 나눈 이름마다 허용 값을 정한다. 대괄호가 없으면 값을 받지 않는다(빈 집합). `[a|b]`이면 그 값들이다. `[n]`처럼 `|`가 없는 자리표시자는 자유 값이라 검사하지 않는다(spec-panel `--iterations N`). 파싱 결과에 `focus`, `scope`, `plan`이 있는지 assert해서, FLAGS.md 형식이 바뀌어 아무것도 못 읽는 경우 테스트가 그냥 통과하지 않게 한다.
  - `<syntax>`에서 `--{name}(?![\w-])(?:[ \t]+(?!\[?-)\[?([^\]\s]+))?`로 값을 잡고(뒤따르는 `[--flag]`나 다음 줄은 값으로 보지 않는다) `"<>`를 벗겨 `|`로 나눈다. 값이 없으면(`[--delegate]`) 건너뛴다. 허용되지 않는 값이 하나라도 있으면 `flag_entries(content)`에 그 이름이 있어야 한다.
- [x] Step 2: 실행하면 analyze만 `{'rules'}`로 실패해야 한다(auto-improve·review `--scope`, business-panel·spec-panel `--focus`, implement `--plan`은 항목이 있음). 값이 없는 전역 플래그 분기도 확인한다. implement.md의 `- --plan <path>:` 항목을 지우면 implement도 실패해야 한다. 확인 후 `git checkout -- src/superclaude/commands/implement.md`.

### Task 3.2: analyze 항목과 규칙

- [x] Step 3: analyze.md `<flags>` 첫 줄에 넣는다: `- --focus perf|security|quality|arch|a11y|testing|rules: the global --focus domains, plus rules, which runs the rules analysis section.` 이 줄은 Phase 2 테스트로 `<rules_analysis>`에 해석된다. 이제 hook은 `/sc:analyze`에서 `--focus`를 선언된 플래그로 본다. `--focus`는 전역 지시문이 없고 `VALID_FLAGS`에 있으므로 동작은 같다.
- [x] Step 4: command-authoring.md `<flags>` 줄의 기존 문장 "A global name the command gives its own meaning is defined here too"를 `` A global name the command gives its own meaning is defined here too (`test_command_structure.py` catches a `<syntax>` value core/FLAGS.md does not allow, including any value for a global that takes none; a redefinition without a value, such as reflect's `--validate`, goes unchecked) ``로 바꾼다. 뒤의 ", and inside this command ..."는 그대로 둔다. 새 문장은 만들지 않는다.
- [x] Step 5: `uv run pytest` exit 0, `make format && make lint`, 커밋: `test(commands): require an entry when a global flag takes its own values`

## Phase 4: business-panel `<flags>` (커밋 1개)

**Files:** Modify: `src/superclaude/commands/business-panel.md` (`<flags>` 블록)

- [x] Step 1: 블록을 아래로 바꾼다. 들여쓰기는 2칸, 값 표기는 `<syntax>`(`--experts "names"`, `--focus domain`)와 같게 한다. 예시 도메인은 `core/BUSINESS_SYMBOLS.md`의 도메인 표에 있는 것만 쓴다.

```
  <flags>
  - --experts "names": panel members by surname from the experts section, e.g. "porter,christensen,meadows".
  - --mode discussion|debate|socratic|adaptive: one of the four modes in the modes section.
  - --focus domain: business domain (e.g. strategy, risk) that picks the 2-3 experts the Analyze step applies; ignored when --experts or --all-experts is given; unrelated to the global --focus.
  - --all-experts: include all 9 experts in the experts section.
  - --synthesis-only: skip per-expert detail and show only the synthesis.
  - --structured: use the business symbol system (core/BUSINESS_SYMBOLS.md).
  </flags>
```

- [x] Step 2: `uv run pytest tests/unit/test_command_structure.py -q` 통과(Phase 1이 `the Analyze step`, Phase 2가 experts·modes 섹션을 해석). 이어서 `uv run pytest` exit 0.
- [x] Step 3: `make format && make lint`, 커밋: `docs(business-panel): define --focus and align <flags> with other commands`

## Phase 5: 동기화와 병합 (커밋 1개)

- [ ] Step 1: `superclaude doctor --scope local`로 확인한 뒤 `superclaude install --force --scope local`. 이어서 `diff -rq src/superclaude/commands .claude/commands/sc`에서 `__init__.py`, `__pycache__`, `README.md` 외의 차이가 없고, `diff -q src/superclaude/core/rules/RULES_DOCS.md .claude/superclaude/core/rules/RULES_DOCS.md`도 같아야 한다. user scope는 동기화하지 않는다(`sync-scope-creates`).
- [ ] Step 2: 이 계획서를 `status: complete`로, README `phase:`를 `complete`로 바꾸고 날짜(`revised:`, `updated:`)를 그날로 맞춘다. Step 1–2의 체크박스도 이 커밋에서 체크한다. 이전 단계 체크박스는 단계마다 이미 체크되어 있어야 한다(`plan-checklist-vs-status`). 커밋: `docs(plans): mark flag-pointer-checks plan complete`
- 병합(체크박스 없음, 계획서가 병합 전에 완료 상태로 커밋되므로): `git checkout master && git merge --no-ff docs/flag-pointer-checks -m "Merge docs/flag-pointer-checks: check flow-step and <flags> pointers"`를 한 명령으로 실행한다(`editable-tool-branch-switch`). push 후 master CI를 확인한다.

## 위험

- section·table의 앞쪽 일치는 다른 섹션을 같은 것으로 볼 수 있다(키 `flowchart`가 `<flow>`로 해석됨 같은 경우). 지금 참조 중 앞쪽 일치가 필요한 것은 `depth profiles`, `expertise adaptation` 둘뿐이고 잘못 해석되는 경우는 없다.
- 형식 밖 참조는 검사되지 않는다. 작성 규칙에 형식을 적어 두는 것이 유일한 방어다.
- flow 단계 이름을 바꾸면 이제 테스트가 실패한다. 의도한 동작이며, flow를 고치는 사람이 참조도 같이 고치게 된다.
- 나중에 flow를 번호 없는 형식으로 바꾸면 `_flow_labels` 정규식과 `<flow>` 작성 규칙을 함께 바꿔야 한다.
- commands 밖 참조는 테스트가 보지 않으므로 다시 번호로 쓰여도 잡히지 않는다.
- 새 `.py` 파일이 없으므로 `codex-module-count-drift`에는 영향이 없다.

## 완료 기준

- `uv run pytest` exit 0, `make lint` 통과
- `TestCommandStepRefs` 2개, `TestCommandFlagPointers` 1개, `test_global_flag_with_own_values_is_defined`가 명령마다 통과
- 일부러 깬 세 곳(Phase 1 Step 9, Phase 2 Step 2, Phase 3 Step 2)이 예상한 명령에서 실패했다가 되돌린 뒤 통과
- `.claude/rules/command-authoring.md`의 바뀐 `<flow>`·`<flags>` 줄이 문장으로 읽히고, flow 단계를 가리키는 방법이 한 가지로만 적혀 있음
- 명령 파일과 RULES_DOCS.md가 local 설치본과 원본 사이에 차이 없음, master CI 통과
