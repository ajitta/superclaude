---
status: complete
revised: 2026-10-22
---

# 누더기 감사: v4.34.1 이후 미릴리스 작업

**판정: 부분적으로 누더기.** 기능 설계(기계별 세션 기록, 재리뷰 게이트, reflect에서 닫는 계획)는 일관되고 loading 제약에 맞게 나뉘어 있다. 그러나 `implement.md` Integrate, `load.md` Load, CHANGELOG, `_GATE_PHRASES`는 검증 round마다 덧붙인 흔적이 그대로 남았다. 그중 하나는 실제 모순이다(reflect가 `/sc:test`로 보내지만 `/sc:test`는 `Result:`를 고치지 않는다).

## 범위와 방법

- 대상: `audit/patchwork` @ 0bf95173(`feature/plan-complete-order` head), `git diff v4.34.1 HEAD`(63 files, 81 commits). 모델: Claude Opus, effort high.
- 읽은 것: 바뀐 shipped 단계 전부(v4.34.1과 나란히), README·CHANGELOG, `_GATE_PHRASES` 블록, `test_eval_harness.py`·`tasks.yaml`의 새 블록, `run_eval.py`, `run_shell`, `test_runner_hook.py`, 세 feature 폴더의 README·설계·검증 표, 분석 문서, gotchas, insights.
- loading: `context_loader.py:191`. RULES_DOCS는 `/sc:intent`, `/sc:plan`, `/sc:save` 등에서 로드되고 `/sc:implement`, `/sc:test`, `/sc:review`, `/sc:reflect`에서는 로드되지 않는다. `core/RULES.md`는 항상 로드된다.
- 기준선: `uv run pytest` 3863 passed, 3 skipped(exit 0), `make lint` 통과, `make typecheck` 통과.
- 재작성안은 `$TMPDIR` 복사본(`git archive HEAD`)에 적용해 `tests/unit`을 돌렸다(아래 "재작성안 검증"). 저장소 파일은 이 보고서 말고 고치지 않았다.

## 바뀐 shipped 단계

| 단계 | v4.34.1 → HEAD (자) | 담은 규칙 | 같은 규칙의 다른 사본 (loading상 필요?) |
|---|---|---|---|
| `implement.md:19` Integrate | 1565 → 2020 | Proof·`Result:`, `complete` 안 씀, 되돌림, 재리뷰 | "`complete`는 reflect에서": 이 단계 안 3번(1번 필요), RULES_DOCS 2번(1번 필요), reflect(필요) |
| `review.md:20` Process | 210 → 688 | 재리뷰, 멈춤 규칙, `--through` 예외 | "no claim that they are fixed"는 `RULES.md:10`(항상 로드)와 중복(불필요) |
| `test.md:17` Report | 37 → 382 | 계획 작업은 reflect 전 미완료, 재리뷰 지목 | RULES_DOCS `/sc:test ->` 게이트(test에서 미로드라 필요) |
| `reflect.md:19` Plan-Close | 0 → 866 | 세 조건, 사용자 yes, 제안 | RULES_DOCS 2곳, implement(필요) |
| `intent.md:20,22` Run·Report | 943 → 958, 486 → 515 | `--through`는 `complete`를 쓰지 않음 | 없음. 최소 변경 |
| RULES_DOCS `:58` Plan docs | 457 → 549 | 작성자 표기 | `:88` reflect 게이트와 같은 말(불필요) |
| RULES_DOCS `:86–88` 게이트 | 73 → 1052 (3줄) | 재리뷰·멈춤·`--through`·reflect | 멈춤 규칙 사본은 `/sc:review`에서 미로드(불필요) |
| `load.md:13` Sync | 0 → 814 | fetch, 뒤처짐 수, pull 전 질문 | `save.md:13`이 가리킨다(한 정의, 좋음) |
| `load.md:14` Load | 344 → 962 | `branch:` 줄로 거르기, 기계별 최신 | `save.md` `<storage>` slug |
| `save.md` Sync·Persist·Share·Host slug | 0·355·0·0 → 337·437·628·206 | 동기화 위임, 기계별 이름, 공유 | 없음 |
| `auto-improve.md:49` gotcha | 393 → 676 | 종료 신호별 생존 | CHANGELOG Fixed |

## 발견

### Important

**1. reflect가 `/sc:test`로 보내지만 `Result:`를 고치는 쪽이 없다 (모순, 표지 10).** `reflect.md:19` "A code commit after the `Result:` sha → send the work to /sc:test first". `/sc:test`(`test.md:17`)는 `Result:`를 쓰지 않는다. `Result:`를 다시 쓰는 규칙은 `implement.md:19` "A later code change ... re-runs the Proof and updates `Result:`"뿐이고, 그 문장은 `/sc:implement`에서만 로드된다. 리뷰 수정을 `/sc:review` 세션에서 했다면 `/sc:test` → `/sc:reflect`를 돌아도 조건 (2)가 계속 실패한다. CHANGELOG `:17`("sends you to `/sc:test` first")도 같은 말을 사용자에게 한다. 출처인 04 표 6행은 누가 `Result:`를 다시 쓰는지 정하지 않았다. 수정: reflect가 Proof를 돌리지 않는다는 결정은 지키고, 보낼 곳을 `Result:`의 주인(`/sc:implement --plan`)으로 바꾼다(재작성안 2). `/sc:test`가 `Result:`를 쓰게 하는 안은 test가 docs를 건드리지 않는다는 프로브 의도와 부딪혀 권하지 않는다. 소유자 확인이 필요하다.

**2. `implement.md:19` Integrate: 한 단계 안에서 같은 규칙 세 번, 옛 뜻이 남은 동사 (표지 1, 2).**
- "the index records its Proof when its last box is checked (below) and reaches `status: complete` only at the /sc:reflect Plan-Close step", "it moves to `complete` with the plan (index), at the /sc:reflect Plan-Close step", "The plan stays `implementing`: /sc:implement never sets it `complete`; the user does, ..." 셋이 같은 규칙이다. B′ 반영 때 문장을 바꾸지 않고 덧붙였다.
- "A red or unrunnable run ... keeps `status: implementing`": B′ 뒤에는 녹색이어도 `implementing`이므로 빨강만의 규칙이 아니다.
- "it closes only on the user's acceptance": B′ 전에는 "acceptance → `complete`"였다. 지금은 acceptance가 Plan-Close 조건 (1)을 채울 뿐이다. "closes"가 남아 모델이 수용 = `complete`로 읽을 수 있다.
- 수정: 재작성안 1(2020 → 1561자, 규칙 수는 같다). `_GATE_PHRASES` implement 3행을 바꿔야 한다.

**3. CHANGELOG [Unreleased]가 개발 기록처럼 읽히고 같은 이야기를 두 번 한다 (표지 9).** `:15`(1077자)는 멈춤 규칙과 `--through` 예외를 전부 옮기고 "The workflow gates say the same"로 끝난다. `:17`(882자)은 같은 주제(계획 작업은 언제 끝나는가)를 다른 각도에서 다시 말한다. 기여자 항목 `:16`(803자)·`:19`(503자)은 check 내부(assertion-rewrite cache, `-B`, `-O`, `--assert=plain`)를 적는다. 사용자는 "무엇이 바뀌었고 무엇을 해야 하나"만 필요하다. 수정: `:15`와 `:17`을 한 항목으로 합친다.

> - Work run from a plan document is done only after `/sc:reflect`, not when its Proof or tests pass. `/sc:implement` records the Proof in a `Result:` line and leaves the plan `implementing`; `/sc:test` says the work still needs `/sc:reflect`; `/sc:reflect`'s new Plan-Close step proposes marking the plan and feature `complete` once every box is checked, the `Result:` line is green and current, and no review fix is waiting, and writes it only on your yes. A fix to a Critical or Important review finding now gets another `/sc:review` round, until a round finds none or you accept them. `/sc:intent --through` keeps one fix round and leaves marking the plan complete to you.

기여자 항목 둘은 프로브 이름과 "limits: `evals/tasks.yaml` comments" 한 줄로 줄인다. 테스트 영향 없음.

### Suggestion

**4. `_GATE_PHRASES`가 문장 23개를 통째로 고정한다 (표지 5).** `test_docs_ssot_guards.py:529–627`. 규칙을 하나도 빼지 않은 재작성안 1–4를 적용하자 13개가 실패했다. 06a/06b mutation(D4, D5, D8, D10, D16, D17)을 막으려고 구절을 문장으로 키운 결과인데, 그 mutation은 "삭제"와 "may/optionally로 약화" 두 부류다. 짧은 anchor와 약화어 검사로 둘 다 잡힌다("테스트 가드 제안"). 주석 `:515–517` "in the same words"는 틀렸다("changes"/"changed", review만의 "with no claim ..."). `/sc:reflect`도 빠져 있다.

**5. RULES_DOCS 안의 중복 (표지 1).** `:58` "(... the status is set on the user's yes to the /sc:reflect Plan-Close proposal)"와 `:88` "the plan (index) reaches `complete` here, on the user's yes ..."는 같은 파일 안에서 같은 말이다. `:86`의 멈춤 규칙 전문은 rounds가 실제로 도는 `/sc:review`에서 로드되지 않는다. 그 사본을 읽는 곳(`/sc:plan`, `/sc:intent`)에서는 쓸 일이 없다. 수정: 재작성안 3(멈춤 규칙은 `/sc:review` Process를 가리킨다).

**6. `review.md:20`이 항상 로드되는 규칙을 다시 적는다 (표지 1).** "which gets the earlier findings as acceptance criteria with no claim that they are fixed"는 `RULES.md:10` Intent Propagation과 같다. RULES.md는 항상 로드되므로 이름만 대면 된다. "(a `/sc:intent --through` run keeps its single fix round)"는 남긴다(그대로 둘 것 3). 수정: 재작성안 4.

**7. `load.md:14` Load: 괄호 안의 이유 설명이 규칙보다 길다 (표지 2, 3).** "(one Grep `^branch:` over that glob, without reading the records whole; a record's `branch:` header is its first line, so a later line starting `branch:` does not count; a branch slug may hold `_`, so the filename alone can misread machine and branch)". `load.md:13` Sync의 "(PowerShell reads a bare one as a hashtable)", "(a bare `GIT_TERMINAL_PROMPT=0;` before it is not exported in bash)"는 이유다. 이유는 `test_session_memory_folder.py:98,105` 주석에 이미 있고, 모델에게는 명령이면 된다. 수정: 재작성안 5. 기존 session-memory 테스트는 모두 통과한다.

**8. `reflect-plan-close`의 성공 check가 거의 측정하지 못한다 (표지 7).** `tasks.yaml:681` `(?i)\bcomplete\b`. "The plan is not complete"도 통과하고, 계획에 `status:`를 말하는 답은 대개 이 단어를 쓴다. 수정: 제안 형태를 본다. `'(?i)\b(mark|set|close)\w*\b[^.\n]{0,60}\bcomplete\b[^.\n]*\?|\bcomplete\b[^.\n]{0,40}\?'`. `test_reflect_plan_close_writes_nothing_headless`의 `bad`에 "The plan is not complete yet."를 더한다.

**9. 채점 테스트 데이터가 문구 목록이다 (표지 6).** `test_eval_harness.py:1316–1388`의 `_RG_REREVIEW` 29개, `_RG_FAILS` 22개, `_RG_HEDGED` 5개. 정규식은 세 규칙으로 설계했지만(`tasks.yaml:540–565` 주석), 테스트는 round마다 탈출 문구를 하나씩 더했다. `_RG_KNOWN_MISSES`(`:1350`)는 정규식이 좋아지면 테스트가 깨지게 만든다. 수정: 규칙마다 통과 2개, 실패 2개(약 15개)만 남긴다. 나머지와 known misses는 05a 측정 문서에만 둔다.

**10. 테스트 helper 중복과 죽은 코드 (표지 6).** `_probe_checks`(`:1810`)는 이미 있는 `TASKS`를 두고 YAML을 다시 읽는다. `import yaml`·`import re`가 함수 안에서 6번 반복되는데 둘 다 모듈 상단(`:10`, `:16`)에 이미 있다. `:1217`의 `footer =`는 `:1219`가 바로 덮어쓰는 죽은 대입이다. step 줄 찾기는 `test_docs_ssot_guards._gate_texts`(`:630`)와 `test_session_memory_folder._flow_step`(`:190`) 두 곳에 있다. 수정: `TASKS`를 쓰고, step 찾기 helper를 하나로 합친다(`tests/unit/_doc_steps.py`).

**11. shipped·테스트 주석의 검증 이력 (표지 4).** `test_eval_harness.py:1823` "(06a-verify-independent.md #4, #5, #12)"는 발견 ID다. 문서 경로면 충분하다. shipped 본문에는 round 언급이 없다.

**12. `auto-improve.md:49` cc-session-end (표지 2).** 393 → 676자. 끝 괄호의 "a killed worker can leave the pid file behind"는 앞 문장 "a hard-killed worker leaves it stale"의 반복이다. 수정: 그 절을 지운다.

**13. 기록 문서 (표지 8).**
- 분석 문서 `:40` "B. ... 결정됨, 진행"인데 review-reflect-gates는 `phase: complete`다. "완료"로 고친다.
- `plan-complete-order/README.md:12`는 고치기 전 동작을 현재형으로 적는다("`/sc:implement`는 ... `complete`로 바꾼다"). 병합 뒤 거짓이 되므로 과거형으로 쓴다.
- `review-reflect-gates/05-plan.md`는 24,420 B로 목표 25,000 B의 98%다. 400자가 넘는 `Result:` 줄의 측정 목록은 05a로 옮긴다.

## 재작성안

소유자 결정(feature README, 04 B′ 표)의 규칙은 모두 남겼다.

### 1. `implement.md` 7. Integrate (2020 → 1561)

```
  7. Integrate: docs and test recommendations; report any blockers hit. With --plan, record every departure from the plan under a "Deviations" heading in the plan doc, in the same commit as the code, and check a box only when the code backs it (a task dropped by decision becomes `- [x] ~~task~~` with its reason under Deviations). The first checked box sets the plan (index) to `status: implementing` and, in a feature folder, the README `phase:` to `implementing`. With a split plan, a phase's Deviations go in its phase file, and a phase file whose boxes are all checked gets `status: complete` and its box in the index checked. When the plan's (index's) last box is checked: commit the last code change, run the command in its `## Proof` footer on that clean HEAD, then in a docs-only commit write under the footer `Result: <that HEAD's short sha> — <actual output, one line>`. A red or unrunnable run is recorded the same way and reported; it counts only once the user accepts it, recorded as `Result: <sha> — <what failed or why not run> (accepted by user)`. Every later code change re-runs the Proof and rewrites `Result:`. /sc:implement never sets the plan (index) or the README `complete`: the user does, at the /sc:reflect Plan-Close step. A red re-run, or a Critical or Important finding in a `complete` plan's work, sets it back to `implementing`; the README `phase:` never moves back. A fix to a Critical or Important review finding that changes reviewed code or shipped content goes back to /sc:review for another round, even when its Proof is green
```

"`status: complete` with an open box is a defect"는 phase 파일 문장("whose boxes are all checked")과 `test_plan_checklist.py`가 맡는다.

### 2. `reflect.md` 3.6. Plan-Close (866 → 841, 발견 1 해결)

```
    3.6. Plan-Close: when the work ran from a plan document (a feature folder's `05-plan.md` or a `docs/plans/` plan) whose plan (index) is `status: implementing`, check from the plan file and `git log`, without re-running the Proof: (1) every task box is checked; (2) the `## Proof` footer's `Result:` line is green or marked accepted by the user, and names the last commit that changed code; (3) no fix to a Critical or Important review finding waits for another review round. All three hold → propose one docs-only commit that sets the plan `status: complete` and the feature README `phase: complete`, and write it only when the user says yes. Otherwise name each failing condition and leave the plan `implementing`; a code commit after the `Result:` sha needs the Proof re-run and `Result:` rewritten (/sc:implement --plan) before Plan-Close
```

옛 (1)의 "Result: 존재"와 (2)의 "그 뒤 코드 커밋 없음"은 같은 것을 두 번 잰다. 새 (2) 하나로 합치고 상자를 (1)로 뺐다. 세 조건이라는 결정(04a #5)은 그대로다.

### 3. RULES_DOCS `:86–88` 게이트 (1052 → 835)

`:58` Plan docs는 괄호만 "(/sc:implement writes the line; the user sets `complete` at the /sc:reflect Plan-Close step, below)"로 바꾼다.

```
    /sc:review -> fix -> /sc:review: a fix to a Critical or Important review finding that changes reviewed code or shipped content gets another review round, with the earlier findings as acceptance criteria (RULES.md Intent Propagation); rounds stop as the /sc:review Process step says. A `/sc:intent --through` run keeps its single fix round; its /sc:test step names the fix left unreviewed
    /sc:test -> /sc:reflect | done: Test pass evidence required (actual output, not claims). Work run from a plan document (a feature folder's `05-plan.md` or a `docs/plans/` plan) goes to /sc:reflect; other work is done here
    /sc:reflect -> done: every gap /sc:reflect names is fixed (a fix to reviewed code or shipped content goes back to review, above) or accepted by the user; the plan (index) becomes `complete` here, on the user's yes to Plan-Close
```

### 4. `review.md` 7. Process (688 → 612)

```
  7. Process: classify each finding as a change request, a concern or a question; verify it against the source of truth (file:line, test output) and withdraw or downgrade any finding the evidence does not support. A fix to a Critical or Important finding that changes reviewed code or shipped content comes back for another round, packed as RULES.md Intent Propagation says. Rounds stop when one finds no Critical or Important finding, or when the user accepts the open findings or waives the re-review; leftover Suggestions are reported, not reviewed again. A `/sc:intent --through` run keeps its single fix round
```

### 5. `load.md` 2. Load (memory folder) (962 → 704)

Sync(`:13`)는 이유 괄호 둘("PowerShell reads a bare one as a hashtable", "a bare `GIT_TERMINAL_PROMPT=0;` ... bash")만 지우고 "keep each `'@{u}'` argument in single quotes in either shell"로 바꾼다(814 → 667).

```
  2. Load (memory folder): Glob .claude/memories/*.md → Read learnings_corrections when present (corrections /sc:save keeps there while auto memory is off). Then one Grep `^branch:` over session_*_[branch-slug].md keeps the records whose `branch:` line names the current branch (the first line; a slug may hold `_`, so the filename alone can misread machine and branch). Read every kept record that has the newest date, one per machine, and say which machine wrote each: the part between the date and `_[branch-slug]`, empty in records from before machine names (slugs per /sc:save <storage>). None → the newest session_* of any branch, reported as the branch its `branch:` line names; folder absent → skip
```

### 재작성안 검증

복사본에 1–5(Sync·Plan docs 포함)를 적용하고 `tests/unit` 실행: 3834 passed, 15 failed. 13개는 `test_review_reflect_gate_wording`(implement 3, reflect 1, review 3, gates 5, rules 1)이다. 2개(`test_cli_context`, `test_no_fixture_file_is_git_ignored`)는 복사본이 git 저장소가 아니어서 실패했다. `test_session_memory_folder.py`, `test_plan_checklist.py`, 체인 검사는 통과했다. 함께 바꿀 것: `_GATE_PHRASES` 13행(또는 아래 가드). 프로브 채점은 그대로다. 릴리스 전 `make canary-commands`는 다시 돌린다.

## 테스트 가드 제안

`_GATE_PHRASES`와 `test_review_reflect_gate_wording`을 바꾼다. `_gate_texts()`와 체인 검사는 그대로 둔다.

```python
# The words that carry each rule; rewording passes, deleting or softening fails.
_GATE_ANCHORS = {
    "gates": ["/sc:review -> fix -> /sc:review", "Critical or Important",
              "shipped content", "acceptance criteria", "single fix round",
              "/sc:test -> /sc:reflect", "goes to /sc:reflect",
              "/sc:reflect -> done", "Plan-Close"],
    "rules": ["Plan-Close"],
    "test Report": ["not done until /sc:reflect", "Critical or Important",
                    "another review", "/sc:reflect does not replace"],
    "review Process": ["Critical or Important", "comes back for another round",
                       "no Critical or Important finding", "Suggestions",
                       "single fix round"],
    "implement Integrate": ["never sets", "Plan-Close", "back to `implementing`",
                            "back to /sc:review", "even when its Proof is green"],
    "reflect Plan-Close": ["every task box is checked",
                           "last commit that changed code",
                           "another review round", "only when the user says yes"],
    "intent Run": ["Plan-Close → propose, write nothing"],
    "intent Report": ["setting the plan `complete`"],
    "README implement row": ["stays `implementing`"],
    "README review row": ["Critical and Important", "reviewed again"],
    "README reflect row": ["done only after this", "which you confirm"],
}
_SOFTENER = re.compile(r"\b(may|might|optionally|if needed|consider)\b", re.I)


@pytest.mark.parametrize("where", sorted(_GATE_ANCHORS))
def test_review_reflect_gate_anchors(where):
    """Each place that carries the review-reflect gates keeps its rule
    (docs/features/review-reflect-gates, plan-complete-order)."""
    text = _gate_texts()[where]
    missing = [a for a in _GATE_ANCHORS[where] if a not in text]
    assert not missing, f"{where} lost {missing}"
    if where != "rules":
        assert not _SOFTENER.search(text), where
```

측정: HEAD와 재작성 복사본에서 11/11 통과. 재작성 복사본에 mutation 14개를 넣었다. D1, D3, D4, D5, D8, D9, D10, D16, D17, "even when its Proof is green" 삭제, "never sets"→"sets", "write it only when the user says yes"→"write it", reflect 조건 (3) 삭제의 13개가 red다. 나머지 D6(handoff 순서)은 기존 체인 검사가 잡는다. 약 100줄이 30줄이 된다.

## 그대로 둘 것

1. **"plan document (...)" 정의 세 사본**(`test.md`, `reflect.md`, RULES_DOCS): 함께 로드되지 않는다. 문구도 같다.
2. **`implement`·`test`·`review`의 재리뷰 구절**: RULES_DOCS가 거기서 로드되지 않고, 소유자 결정이다.
3. **`review.md`의 `--through` 예외**: `--through`에서는 `intent.md`("once")와 `review.md`(다시 round)가 함께 보이므로 우선순위가 필요하다.
4. **`test.md` "which /sc:reflect does not replace"**: "reflect가 재리뷰를 대신한다"는 부류의 오해를 막는다.
5. **`intent.md` 두 줄 변경**: 최소이고 B′ 결정(04a #2) 그대로다.
6. **`save.md` Sync의 설치 경로 괄호**: `/sc:save`는 `/sc:load` 없이도 돈다. CLI 설치라 `commands/sc/` 경로가 맞고, 한 정의를 가리키는 방식이 맞다.
7. **`save.md` Share의 조건들**: 절마다 실제 git 실패(부분 commit 거절, revert 상태 소실)를 막고 근거가 테스트 주석에 있다.
8. **`test-reflect-gate-complete`**: B′ 뒤에는 SC가 만들지 않는 상태지만 옛 설치·손으로 쓴 값을 재려고 남기기로 했다(04a #8).
9. **`utils.run_shell`**: 길지만 덧댐이 아니다. Windows pipe, POSIX 세션, 신호를 각각 다루고 `test_run_shell.py`가 잰다.
10. **`rereview_named` 정규식**: 세 규칙이고 한계(53–83%)를 적는다. 고칠 것은 테스트 데이터다(발견 9).
11. **gotchas 추가와 `tests.md` 분리**: 반복된 실수 하나에 한 줄, 형식대로다.
