---
status: draft
revised: 2026-10-22
---

# review-findings-record 04 독립 설계 검증

**판정: 조건부 통과.** 문제 진단, 인용, `--through`와의 관계, 기준선 프로브의 셋업은 대체로 재현된다. 다만 권고 ★B는 지금 문구로 빌드하면 안 된다. 상태 모델에 출구가 없는 경우가 둘 있고, 기록이 없을 때의 의미를 정하지 않아 오늘의 기준선에 없던 잘못 닫기 경로가 생긴다. headless에서 Auto 등급 명령이 커밋하는 문제도 있다. 또 앞선 결정 두 개(약점 4의 "리뷰 기록" 비용, 약점 감사 검증 F12의 "관찰된 실패 먼저")가 B에 불리한데 설계는 이를 인용하지 않는다. 이 검증의 권고는 C(변경 없음)와 프로브 보강이다. 소유자가 관찰된 실패 없이 B를 택한다면 아래 6개 수정을 조건으로 한다.

범위: 7651e477. `claude -p`는 돌리지 않았다. 기준선 transcript가 저장소에 없어 그 내용은 재현하지 못했다.

## 게이트

- `uv run pytest -q`: `3859 passed, 3 skipped, 11 warnings in 137.66s`, exit 0
- `make lint`: `All checks passed!` / `make typecheck`: `Success: no issues found in 54 source files`
- `git diff af910e59 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json src/superclaude/commands`: 0바이트(비어 있음). canary 대상 변경 없음.

## 발견

### 1. [Important] 면제와 Plan-Close 수락에 출구가 없다 (주장 5)

B는 "fixed"를 다음 review round만 쓰게 하고, 사용자의 수락·면제는 reflect가 "사용자가 yes 한 docs 전용 커밋"에 쓰게 한다(04-design.md:72). 조건 (3)(`reflect.md:19`)을 그대로 적용하면 다음과 같다.

- (i) round 1에서 F-1이 open이고, 수정 커밋이 있고, round 2가 없는 경우: 조건 실패. `/sc:review`를 이름으로 대므로 출구가 있다. 그런데 사용자가 재리뷰를 면제하면 출구가 없다. 면제 줄은 적히지만 F-1을 fixed로 적을 주체가 없다. 그래서 계획은 `complete`인데 로그는 "F-1 open"이라고 남는다. 거짓 기록이다. 다음 reflect도 조건 (3) 앞 절("fixed or accepted")을 기록으로 확인할 수 없다.
- (iii) 사용자가 Plan-Close에서 F-2를 수락하고 `complete`에는 no라고 한 경우: 커밋이 생기지 않으므로 수락이 사라진다. 다음 세션에서 다시 묻는다. 비용 1이 B 안에서 다시 생긴다.
- (ii) round 2가 깨끗한 경우, (iv) 분할 계획, (v) 단독 계획은 성립한다. (iv)는 발견 6의 위치 문제가 있다. (vi)은 발견 2에서 다룬다.

설계 수정: reflect가 면제·수락을 `complete`와 따로, 사용자가 동의한 docs 전용 커밋으로 쓰게 한다. 면제 상태를 따로 정의한다. 예: `F-1 fixed in <sha>, re-review waived by user`.

### 2. [Important] 기록이 없을 때의 의미를 정하지 않았다. 새 잘못 닫기 경로가 생긴다 (주장 5 (vi), 주장 3)

B의 reflect 문구 "the plan's `## Review Log` and any review in this session"(04-design.md:72)에서는 로그가 없는 계획이 둘 중 무엇인지 구분할 수 없다. (a) 리뷰를 하지 않은 Medium 작업이다(`RULES_DOCS.md:85` "optional for Medium"). (b) 리뷰는 했는데 기록이 없다. (b)에는 업그레이드 전 계획, 사용자가 발견을 "resolve"하지 않고 끝난 대화형 리뷰(B는 "once the user has resolved the findings"에만 쓴다), 계획을 찾지 못한 리뷰가 들어간다. 로그가 리뷰 기록의 자리로 정해지면, 로그가 없을 때 "발견 없음 → (3) 성립"으로 읽힐 수 있다. 오늘 기준선에서는 근거가 없으면 묻는다. B가 이 동작을 약하게 만든다. 이 경로를 막는 것은 `reflect-plan-close-no-record`뿐인데, 그 채점은 발견 8대로 약하다. 업그레이드 줄(04-design.md:88)만 "묻는다"고 말하고, 그 말은 shipped 문구에 들어가지 않는다.

설계 수정: reflect 문구에 부재 규칙을 넣는다. 로그가 없는데 `git log`나 계획에 리뷰나 수정의 흔적이 있으면 (3)은 확인되지 않은 것으로 보고 묻는다. 리뷰 쪽은 round가 끝날 때 해결 여부와 상관없이 open으로 쓴다(발견 3의 동의 조건 안에서).

### 3. [Important] headless에서 Auto 등급 명령이 커밋한다 (주장 4)

`/sc:review`는 Auto 등급이다(`review.md:2` "Use when asked …"). `.claude/rules/command-authoring.md` Trigger Policy는 "writes committed artifacts by default → on-request"이고, Auto는 "a file written only when the user passes a flag for it … or agrees to it"이다. B의 "a run that cannot ask writes them open"과 "Write it in a docs-only commit"(04-design.md:70)에서는 모델이 스스로 부른 리뷰나 일반 `claude -p "/sc:review"`도 묻지 않고 계획에 써서 커밋한다. 지금의 `<never>` 예외는 "user-approved"다(`review.md:72`). B의 headless 쓰기는 그렇지 않다. `RULES_DOCS.md:77`("do not commit unasked")과도 결이 다르다. `no-unsolicited-fixes`(`review.md:67`)와는 충돌하지 않는다. 로그는 수정이 아니다.

`--through`에서는 문제가 없다. 리뷰 호출은 두 번 그대로이고, 단일 수정 round도 그대로다. Run이 커밋하므로(`intent.md:20`) 작업 트리도 깨끗하다. `through_left_open` 정규식도 로그 줄에 걸리지 않는다.

설계 수정: 일반 실행에서는 사용자가 동의한 경우에만 쓴다. 커밋은 하지 않거나, 동의를 받은 뒤에 한다. 묻지 않고 쓰는 경우는 `--through`의 Run 단계 안으로 한정하고, 그 커밋은 Run이 한다.

### 4. [Important] `<never>` 예외의 새 문구가 기존 예외를 지운다

04-design.md:71은 예외를 "the log entries in the Spec gate and Review Log steps"로 넓힌다고 쓴다. 지금 문구는 "the user-approved log entry and status update in the Spec gate step"(`review.md:72`)이다. 새 문구를 그대로 넣으면 "status update"(`approved-for-plan`)와 "user-approved"가 빠진다. 그러면 Spec gate의 상태 쓰기가 `<never>`와 모순된다. 설계 수정: 바꿀 문장 전체를 적는다. 예: "…; the exceptions are the user-approved log entry and status update in the Spec gate step and the log entry in the Review Log step".

### 5. [Important] B의 파일 목록에 깨지는 테스트가 빠졌다 (주장 1)

`tests/unit/test_docs_ssot_guards.py:586`의 `_GATE_ANCHORS["reflect Plan-Close"]`는 "the review findings and `git log`"를 고정한다. B의 reflect 문구로 바꾸는 것을 모의로 적용해 보면 `anchor kept after B edit: False`가 나온다. `test_review_reflect_gate_anchors[reflect Plan-Close]`가 red가 된다. 설계는 `_GATE_ANCHORS`를 검증 질문(04-design.md:135)으로만 적고, 바뀌는 파일 목록에는 넣지 않았다. 같은 앵커 묶음의 `_SOFTENER`도 새 문구에 적용된다. 설계 수정: B의 변경 파일에 이 테스트를 넣고 새 앵커를 정한다.

### 6. [Important] "`## Proof` 뒤에 만든다"는 footer 계약과 `Result:` 위치를 깬다 (주장 6)

`## Proof`는 계획의 마지막 절, 곧 footer다(`plan.md:55-60`, `RULES_DOCS.md:13`의 index 구성 "…, footer"). `implement.md:19`는 `Result:`를 "under the footer"에 쓴다. 프로브 셋업 `s_result`(`evals/tasks.yaml:670`)는 파일 끝에 덧붙인다. Review Log를 Proof 뒤에 두면 다음 Proof 재실행의 `Result:`가 로그 절 안으로 들어갈 수 있다. "the `## Proof` footer"라는 말도 더는 맞지 않는다. 또 "RULES_DOCS는 이 네 명령에서 로드되지 않는다"(04-design.md:38,78)는 단독 호출에서만 맞다. `context_loader.py:191`의 정규식은 `/sc:intent`에 걸린다. 확인 결과 `/sc:intent --through …` → True, `/sc:review`·`/sc:reflect`·`/sc:implement --plan` → False다. 그래서 `--through` 실행 안에서는 RULES_DOCS:13이 B와 어긋난 채 로드된다. 설계 수정: 로그를 `## Deviations` 뒤, `## Risks` 앞에 둔다. footer 밖이므로 RULES_DOCS:13은 그대로 맞다.

### 7. [Important] 앞선 결정 두 개가 B에 불리한데 인용되지 않았다 (주장 2, 3)

- 약점 4 본문은 비용 목록에 "리뷰 기록"을 이름으로 넣는다(`docs/research/superclaude-weakness-ajitta-2026-10-20.md:32` "계획 체크박스, `Deviations`, 기능 README, 문서 상태, 리뷰 기록을 함께 관리해야 합니다"). 설계는 약점 4를 A의 단점으로만 쓰고 B에는 적용하지 않는다.
- 약점 감사 검증 F12(`…-audit-verify-ajitta-2026-10-20.md:82-84`, `:132`)는 관찰된 실패가 없다는 이유로 N5를 보류했다. 처방은 "먼저 프로브로 실패를 관찰한다"였다. 이 설계는 프로브를 돌렸고, 실패는 관찰되지 않았다. 설계 본문에도 "기준선은 잘못 닫는 실패를 보여 주지 않았다"(04-design.md:58)고 적혀 있다. "근거를 만드는 단계가 없는 조건"은 실패가 아니라 구조에 대한 관찰이다. 세션이 바뀐 뒤 리뷰를 다시 돌린 사례는 `.claude/memories/`와 `insights.jsonl`에서 찾지 못했다.
- 03i 선례(`03i-analysis-commands.md:31,42`)는 정확하다. 다만 그때는 체인이 막혔고, 지금은 막히지 않고 묻는다.

설계 수정: 두 결정을 "지켜야 할 앞선 결정"에 넣는다. B를 택한다면 F12를 넘는 소유자 결정임을 적는다.

### 8. [Important] 기준선 프로브는 "회귀 가드"로 쓰기에 약하다 (주장 7)

단위 테스트는 재현된다. `-k no_record` → `1 passed`. `*closable_verdict`를 빼면 `assert not all(_grade(… "All three conditions hold."))`에서 red, `*plan_not_complete`를 빼면 `"plan written"`에서 red다. `git checkout HEAD -- evals/tasks.yaml`로 복원했고 `git status`는 깨끗하다. dry run 작업 공간(`run_eval.py --canary --task reflect-plan-close-no-record --dry-run`)은 "build ok, no API calls"였다. 그 안에서 `grep -rl 06-review`는 결과가 없다(`.claude/` 설치본과 git 기록 포함). 남는 흔적은 커밋 제목 두 개와 Deviations 한 줄이다.

그런데 채점은 다음 답을 모두 통과시킨다(fixture에서 `_grade`를 직접 실행).

- 빈 답: `[True, True, True, True]`
- "Conditions 1-3 are satisfied. I propose marking the plan complete.": `[True, True, True, True]`

"every run said condition 3 cannot be confirmed"는 채점 결과가 아니라 transcript를 읽은 결과다. 이 저장소에 transcript가 없어 재현할 수 없다. 이 프로브가 막는 것은 파일 쓰기와 "all three conditions hold" 꼴의 말뿐이다. 발견 2의 위험(로그가 없으면 성립으로 읽는다)을 지키는 가드로는 부족하다. 설계 수정(소유자 결정 2): 남긴다면 긍정 check를 더한다. 조건 3이나 리뷰를 다시 요구하는 말을 찾는 `rereview_named` 꼴이 맞고, 이것이 무행동 가드도 된다. 그 전까지는 주석의 "A regression guard"를 "phrase guard"로 낮춘다.

### 9. [Suggestion] 작은 안 하나가 설명 없이 빠졌다 (주장 9)

분석 E의 후보 (b) `Review: <sha> — round 2, Critical 0, Important 0; accepted: F-3`(`review-reflect-gate-gap-ajitta-2026-10-21.md:70`)는 설계에서 절 형태 B로 바뀌었다. 한 줄 형태를 따로 비교하지 않았다. 쓰는 주체의 문제(발견 3)는 같고, 크기와 절 위치 문제(발견 6)는 더 작다. `/sc:implement` Deviations는 고친 발견만 남기고 open 발견과 수락은 남기지 않아 맞지 않는다. `--through` Report에만 기록하는 안은 일반 실행을 덮지 못한다.

### 10. [Suggestion] 저장소 관행 서술이 반만 맞다

04-design.md:37은 "리뷰 기록은 `06x-verify-*.md`로 남는다"고 한다. 실제로는 손으로 쓴 `06-review.md`도 있다(`docs/features/review-reflect-gates/06-review.md`, `session-memory-multi-machine/06-review.md`). 계획이 리뷰 round를 체크된 task로 기록하고 그 파일에 링크한 예도 있다(`review-reflect-gates/05-plan.md:187-190`). 그러니 fixture의 `06-review.md`는 "사용자가 갖지 않는 상태"(04-design.md:36)가 아니라 소유자가 손으로 만드는 상태다. reflect는 그런 파일을 읽고, 기존 프로브 네 개가 그것을 잰다. C가 이미 동작한다는 근거다.

### 11. [Suggestion] B 문구의 범위

"when the reviewed work ran from a plan document"는 `--scope plan`으로 계획 자체를 리뷰하는 경우에도 맞는다. 그러면 계획 문서에 대한 발견이 조건 (3)에 들어간다. "fixed는 다음 round만 쓴다"는 규칙 때문에 그 발견은 open으로 남는다. 범위를 `pr|diff|file|branch`로 한정한다. 또 `test.md`는 "문구 그대로 Review Log에서 마지막 round를 찾는다"(04-design.md:75)고 했지만, `test.md:17`은 계획 파일을 읽으라고 하지 않는다. 이 동작은 확인되지 않은 가정이다.

### 12. [Suggestion] 인용과 주석

- `superclaude-weakness-audit-ajitta-2026-10-20.md:33`: 증거표 기각은 `:32`다. `:33`은 `Result:`로 흡수한 행이다. `:14,32,33`으로 고친다.
- "proposal-audit의 구분"(04-design.md:58)은 저장소 밖의 skill 참조다. 저장소만으로는 확인할 수 없다. 경로를 적거나 문장을 뺀다.
- 프로브 주석(`evals/tasks.yaml:730-738`)의 "only the commit subject `fix: apply review F-1`": `feat: CSV export; review round 1` 제목도 리뷰가 있었음을 보여 준다(dry run의 `git log`). "the commit subjects"로 고친다.

## 인용 점검 (주장 8)

`sed -n`/`grep -n`으로 맞는 것: `reflect.md:19`, `review.md:18,22,31-37,67,72`, `agents/self-review.md:5,36`, `implement.md:19`, `intent.md:20,22`, `test.md:17`, `RULES_DOCS.md:19,30,58,86,88`, `context_loader.py:181,191`, `evals/tasks.yaml:514-728`, `03i:31,42`, weakness-audit `:14`. 어긋난 것: weakness-audit `:33`(발견 12). 범위 밖이라 확인하지 못한 것: proposal-audit.

## 주장별 재현

| 주장 | 결과 | 근거 |
|---|---|---|
| 1 읽는 쪽·쓰는 쪽 목록 완전 | 부분 | 계획의 절 구조를 파싱하는 코드는 없다(`test_plan_checklist.py`는 체크박스와 status만, verifier는 Proof·Deviations만, cleanup `--type docs`는 frontmatter와 Documents만, promote-feature는 파일 이동만 다룬다). 빠진 것: `_GATE_ANCHORS` 앵커(발견 5), footer 계약(발견 6), Trigger Policy(발견 3), 손으로 쓴 `06-review.md`(발견 10) |
| 2 앞선 결정 분석 | 부분 | 03i와 약점 감사 인용은 맞다. 약점 4 본문과 F12/N5가 빠졌다(발견 7) |
| 3 content-quality 요건 통과 | 재현 안 됨 | 관찰된 실패가 없다. F12 선례(발견 7) |
| 4 headless 쓰기와 `--through` | 부분 | `--through`는 충돌 없음. 일반 headless 실행은 Auto 등급 정책과 충돌(발견 3) |
| 5 상태 모델 | 재현 안 됨 | (i)+면제, (iii), (vi)(발견 1, 2) |
| 6 RULES_DOCS 변경 불필요 | 부분 | 네 명령의 트리거는 맞다. `--through`에서는 로드된다. :13 footer(발견 6). :58과 README 행은 어긋나지 않는다 |
| 7 기준선 프로브와 테스트 | 재현(채점은 약함) | 1 passed, 변이 둘 다 red, 흔적 없음. 빈 답도 통과(발견 8) |
| 8 `file:line` | 대체로 | `:33` 하나가 어긋남 |
| 9 더 작은 안 | 빠짐 | `Review:` 한 줄 안(발견 9). C가 이미 동작함(발견 10) |

## 권고

**C(shipped 변경 없음)와 프로브 보강.** 이유는 넷이다.

1. 기준선은 잘못 닫는 실패를 보여 주지 않았다. F12 선례와 content-quality Improvement Workflow 1을 따르면 문구를 더할 근거가 없다.
2. 비용 1–2는 실제 사례가 아니라 추론에서 나왔다. 소유자는 이미 손으로 `06-review.md`를 쓰고, reflect는 그것을 읽는다.
3. B는 리뷰 계약을 바꾼다. Auto 명령이 커밋하게 되고, `<never>` 예외가 넓어지고, 상태 모델에 구멍이 셋 생긴다. 고칠 수는 있지만 문구가 늘고, 약점 4가 말한 리뷰 기록 운영 비용이 생긴다.
4. 프로브 보강은 측정 장치를 고치는 일이라 "관찰된 실패" 요건 없이 할 수 있다. `no-record`에 긍정 check를 더하면, 이후 B를 다시 열 때의 기준선이 된다.

A가 B보다 낫지 않다는 설계의 판단(단독 계획, README 규칙 중복)에 동의한다.

소유자가 세션 간 근거를 지금 원한다면(F12를 넘는 결정이다), 조건부 B′: (a) 로그를 Deviations 뒤, Risks 앞에 둔다. (b) 일반 실행에서는 사용자가 동의할 때만 쓰고, 묻지 않는 쓰기는 `--through` Run 안으로 한정한다. (c) reflect가 수락·면제를 `complete`와 따로, 동의를 받은 커밋으로 쓴다. 면제 상태를 정의한다. (d) 기록이 없을 때의 규칙을 문구에 넣는다. (e) 범위를 코드 리뷰로 한정한다. (f) `_GATE_ANCHORS`를 함께 바꾸고 `<never>` 문장 전체를 다시 쓴다. 한 줄 `Review:` 형태도 함께 견준다.

### 소유자가 정할 것

1. 관찰된 실패 없이 진행할지: ★C(변경 없음, 프로브 보강) / B′(위 6개 조건) / B′의 한 줄 `Review:` 형태
2. `reflect-plan-close-no-record`: ★긍정 check를 더해 가드로 남긴다 / phrase guard로 표시만 고친다 / 지운다
3. B′를 고른다면 일반 실행의 쓰기: ★사용자 동의 시에만 / headless에서도 쓴다(이 경우 Auto 등급 정책의 예외를 command-authoring.md에 적어야 한다)

## 이 브랜치 밖

- `evals/run_eval.py` dry run은 runs-dir에 같은 작업 공간이 이미 있으면 `FileExistsError` traceback으로 끝난다(`except (RuntimeError, subprocess.TimeoutExpired)`가 잡지 못한다). 공유 scratch에 남아 있던 디렉터리에서 실제로 그랬다.
- `reflect-plan-close-review-due`에서는 기록이 있는데도 잘못 닫은 실행이 관찰됐다(`plan-complete-order/06e-verify-round6.md:167`). 읽는 쪽의 문제라 B도 C도 해결하지 않는다.
