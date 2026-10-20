---
status: draft
revised: 2026-10-20
---

# 감사 문서 검증: superclaude-weakness-audit-ajitta-2026-10-20.md

판정: **PASS WITH FIXES** — 진단(약점 1·2·3)과 방향(상태 체계 대신 기존 장치 강화)은 소스로 재현되지만, S1 네 건이 권고를 바꾼다. 결정 모드 오분류의 방향, N4의 격리 범위, N2와 N3의 순서, canary 게이트 대상 여부가 그것이다.

대상: 감사 문서와 외부 두 문서([superclaude-weakness.md](./superclaude-weakness.md), [superclaude-improvement-compared-ecc.md](./superclaude-improvement-compared-ecc.md)). 기준: 브랜치 `docs/superclaude-weakness-research` HEAD `b678776f`. `git diff --quiet origin/stable 04a99968 -- src README.md`가 같음을 반환했고, `origin/stable`의 `pyproject.toml`은 `version = "4.32.0"`이다. 그러니 감사 서두의 "stable과 master의 `src/`·README가 같다"는 맞다. 전체 `uv run pytest`는 이 브랜치에서 `3752 passed, 3 skipped`였다.

## 발견 사항

### S1 — 결론이나 권고를 바꾼다

**F1. "`core/`를 건드리지 않으므로 canary 게이트 대상이 아니다"는 틀렸다 (§5-3, N6 실행 항목)**
- 감사의 주장: N6 "`src/superclaude/core`를 바꾸지 않으므로 canary 릴리스 게이트 대상이 아니다". §5-3 "`core/`는 건드리지 않으므로 canary 게이트 대상이 아니다".
- 근거: N2는 "`RULES_DOCS.md:58`의 plan `complete` 조건에도 같은 조건을 한 구절 덧붙인다"고 적는다. 이 파일은 `src/superclaude/core/rules/RULES_DOCS.md`다. `Makefile:122`은 `git diff --name-only $PREV..HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json`이 비어 있지 않으면 `CANARY_OK=1` 없이는 릴리스를 거부한다. AGENTS.md "Canary before a release"도 같은 규칙이다.
- 수정: §5-3과 N6의 문장을 "N2의 RULES_DOCS 변경 때문에 `make canary-gates`를 돌리고 보고서를 읽은 뒤 `CANARY_OK=1`"로 바꾼다. RULES_DOCS를 건드리지 않는 쪽(N2(a)에서 `implement.md`만 변경)을 택하면 지금 문장이 맞게 된다. 두 길 중 하나를 명시해야 한다.

**F2. 결정 모드 오분류가 "안전한 방향(`delegated`)으로 기운다"는 주장은 성립하지 않는다 (§1 약점 5, 보류 요약) — 주장 (e)**
- 감사의 주장: "오분류가 나도 대부분 `delegated` 쪽으로 기운다. 그 결과는 독립 감사가 한 번 더 도는 것이라 안전한 방향이다." 그리고 "결정 모드 분류 규칙 재작성: 보류".
- 근거: `brainstorm.md:37`의 `confirmed` 조건은 "`a`/`b`/`c` as standalone token, OR ≥2 contiguous words from chosen option label text"다. `review.md:21`은 `confirmed` 행을 재평가하지 않는다("Other rows get no re-evaluation … user-confirmed choices already passed the user's own judgment"). 그러니 `confirmed` 쪽 오분류는 감사를 빼는 방향, 곧 위험한 방향이다. 문자 그대로 적용하면 선택이 아닌 답이 `confirmed`가 되는 반례를 쉽게 만들 수 있다.
  1. "I need a minute to think about this" — 영어 관사 `a`가 독립 토큰이다.
  2. "b looks risky, not sure" — `b`가 독립 토큰이지만 선택이 아니라 우려다.
  3. 선택지 라벨이 "Redis cache"일 때 "whatever you think, Redis cache or in-memory, either is fine" — 연속 두 단어가 일치하지만 실제로는 위임이다.
  4. 반대 방향의 틈도 있다. `RULES_INTERACTION.md`의 기본 라벨은 `[1]–[7]`이다. 사용자가 "1번으로"나 "2"라고 답하면 `confirmed` 조건(문자만)에도 `delegated` 조건(bare yes 등)에도 맞지 않는다. 휴리스틱에는 기본값이 없어서 결과가 정해지지 않는다. "감사가 추가될 뿐 누락되지 않는다"는 보장이 없다.
- 수정: 약점 5의 판정을 "과장"에서 "부분적으로 맞음"으로 바꾼다. 보류 대신 최소 수정을 권고한다. 예: "확신이 없으면 `delegated`"를 기본값으로 두고, 단일 문자는 응답 전체이거나 대괄호로 감싸였을 때만 인정한다. `brainstorm.md` 한 줄이면 되고 `core/` 변경은 없다. 아니면 먼저 N6에 판정 프로브를 추가한다(아래 N6).

**F3. N4(a)는 격리 리뷰어에게 `00-intent.md`가 간다고 보장하지 않고, README 체인도 그대로 남긴다 (N4)**
- 감사의 주장: N4(a) "`brainstorm.md:20` 핸드오프가 `--structured`를 안내". 검증 항목으로 "패킷에 `00-intent.md` 원문이 들어가는지 확인한다".
- 근거:
  - `RULES_DELEGATION.md:36` "Sent: the artifact and its acceptance criteria"는 `00-intent.md`를 지목하지 않는다. `user_request_verbatim`(`:30`)은 `/sc:review --scope spec <path>` 호출문일 뿐 원래 의도가 아니다. `review.md:15` Gather 단계는 `00-intent.md`를 메인 루프가 읽는다고만 하고, `review.md:45`(review_lens)도 리뷰어 프롬프트에 "the artifact and its acceptance criteria"만 넣는다. 반면 스펙 안의 "Intent coverage" 표(`brainstorm.md:13`)는 작성자가 의도를 해석한 결과인데, 아티팩트의 일부라서 그대로 넘어간다(`RULES_DELEGATION.md:36`). 기본 상태에서 리뷰어는 작성자의 해석을 받고 원문은 받지 못할 수 있다. 외부 약점 3이 말한 바로 그 경로다.
  - 서브에이전트는 context_loader 주입을 받지 않는다(`RULES_DELEGATION.md:32`). lean 라운드도 "Does `delegate_packet` actually deliver the finding-policy text to native subagents?"를 미해결로 남겼다(`docs/features/lean-round/00-intent.md` Open questions). 패킷 전달은 아직 입증되지 않았다.
  - 사용자가 따라 치는 README 체인(`README.md:298`, `:303`)은 `/sc:review --scope spec`만 적는다. (a)는 brainstorm 출력 문장만 바꾸므로 README 체인을 따르는 사용자는 여전히 같은 컨텍스트에서 리뷰한다.
- 수정: N4의 "검증" 항목을 변경 사항으로 올린다. `review.md`에서 spec 대상 격리 리뷰의 수용 기준을 "feature 폴더의 `00-intent.md` 원문"으로 지목한다(한 구절, `core/` 밖). (a)를 택하면 README `:298`·`:303`·`:313`에도 `--structured`를 넣는다. 아니면 (b) "`--scope spec`이면 격리가 기본"을 택한다. (b)는 README를 고칠 필요가 없어서 실제로는 (b)가 더 작은 변경일 수 있다.

**F4. N2와 N3을 함께 적용하면 외부안이 경고한 "낡은 증거"가 생긴다. 감사는 그 경고를 버렸다 (N2, N3, §2) — 주장 (f)**
- 감사의 주장: N2는 implement의 Integrate 단계에서 `Proof`를 실행하고 `Result:` 줄을 남긴 뒤 `complete`로 바꾼다. N3은 그 **뒤에** `/sc:review --scope branch`를 넣는다. 외부안 §5 "상태 재평가"와 §9 "리뷰 후 코드를 수정했다면 영향받는 검증을 다시 실행"은 따로 평가하지 않고 3단계 상태와 함께 기각했다.
- 근거: N3 순서에서 리뷰 지적으로 코드를 고치면 plan은 이미 `status: complete`이고, `Result:` 줄은 고치기 전 코드의 결과다. `RULES_DOCS.md:31`의 README `phase:`는 "never moves back"이라 되돌릴 수도 없다. 커널 `verification_before_completion`(`RULES.md:26`)이 일반 원칙은 지지만, 기록된 `Result:`를 무효로 만드는 규칙은 없다. `verifier.md:72` `proof-written-ahead`("re-run its commands, never copy its numbers")는 명시적으로 부르는 verifier에만 적용된다.
- 수정: N2의 `Result:` 줄에 Proof를 돌린 커밋 SHA를 적고(`Result: <sha> — <요약>`), "SHA 이후 코드가 바뀌었으면 완료를 주장하기 전에 Proof를 다시 돌린다"는 구절을 같은 문장에 붙인다. 외부안의 재검증 조항 가운데 유효한 부분이 상태 하나를 늘리지 않고 흡수된다.

### S2 — 사실이나 인용이 틀렸지만 결론은 그대로다

**F5. "`complete`를 읽는 소비자가 없다"는 과하다 — 주장 (a)**
- 감사의 주장: "`implement.md`가 쓰기만 하고, 읽는 것은 이 저장소 전용 테스트뿐".
- 근거: 동작을 막는 리더는 없다는 점은 맞다. `grep -rn "status:" src/superclaude`에서 `complete` 값을 분기 조건으로 쓰는 커맨드·훅·스크립트는 없었다. `session_init.py:169`의 `status`는 PR 상태다. `load.md`·`save.md`·`pm.md`·`roadmap.md`·`context_loader.py`도 이 값을 읽지 않는다. 다만 읽는 쪽은 있다.
  - `RULES_DOCS.md:30-33`: feature 경로에 문서를 쓰는 모든 커맨드는 README `phase:`를 갱신한다. 이때 "furthest stage, never moves back"을 지키려면 현재 값을 읽어야 한다.
  - `promote-feature.md:18`: "phase: <furthest stage among the moved docs, per the RULES_DOCS phase mapping>"은 plan의 `status: complete`를 읽어 `phase: complete`를 정한다.
  - 다음 세션의 모델: R02 Status Check(`RULES_QUALITY.md:9`, "confirm the work is not already done")가 feature 폴더를 grep하면 `phase: complete`를 "이미 끝남"의 증거로 볼 수 있다. 비용은 "사람이 오해하는 정도"를 넘어 모델의 판단에도 미친다.
- 수정: 이유 ③을 "값에 따라 분기하는 장치는 없지만 README 단계 매핑, `/sc:promote-feature`, 이후 세션의 상태 확인이 읽는다"로 고친다. 기각 결론은 유지한다. 오히려 더 강한 이유가 하나 있다. 외부안 §5의 "`implemented`로 되돌린다"는 `RULES_DOCS.md:31` "it never moves back"과 정면으로 충돌한다. 감사는 이 점을 쓰지 않았다.

**F6. "`RULES_QUALITY.md`는 커맨드 없는 '버그 고쳐 줘'에서 로드되지 않는다"는 반만 맞다 — 주장 (c)**
- 근거:
  - 훅 주입 조건(`context_loader.py:181`)은 `/sc:(implement|improve|test|build|review|cleanup|troubleshoot|analyze|task|reflect|git)|--validate|--loop\b|--iterations`다. 모든 `/sc:` 커맨드가 아니다(`plan`·`brainstorm`·`design`은 빠진다). `--iterations`가 하나 더 있다. 다른 주입 경로는 없다. `COMPOSITE_FLAGS`(`:205-215`)는 MCP만, `_EXECUTION_DIRECTIVES`(`:863-909`)는 인라인 지시만 낸다. 그러니 기계적 주입에 대한 감사의 주장은 맞다.
  - 하지만 커널이 모델에게 직접 읽으라고 지시한다. `RULES.md:40` "When a module's domain is in play and it is not in context, Read it", `:43` "Load when: implement / test / review / build / debug work". 그리고 세션 캐시(`check_triggers`, `:658-670`) 때문에 세션 안에서 한 번 주입되면 다시 주입하지 않는다. 컴팩션 전까지는 컨텍스트에 남는다.
- 수정: "기계적으로는 주입되지 않고, 커널의 on-demand 지시를 모델이 따를 때만 읽힌다"로 고친다. "커널에 둬야 항상 적용된다"는 결론은 유지된다.

**F7. 커널 예산 테스트와 "부딪힌다"는 과장이다**
- 근거: `tests/unit/test_context_loader.py:320` `KERNEL_CHAR_BUDGET = 7600`. 현재 `RULES.md`는 6,136바이트라 약 1,460자 여유가 있다. 한 구절은 테스트를 깨지 않는다. 이 테스트의 출처도 lean 라운드가 아니라 "Phase 2-1 core-lite split"(`:317-318`)이다. 실제 제약은 lean·reframing-anchoring 라운드의 "커널은 측정 후 변경" 방침이다.
- 수정: "커널 변경은 측정을 거쳐야 하고(lean 라운드 방침) canary 게이트 대상"으로 바꾼다.

**F8. R20 인용 위치가 틀렸고, 그래서 감사 자신의 논리가 약해진다**
- 감사의 주장(§2 §8 행): "커널 R20(`RULES.md` `verification_before_completion`, "fix bug → the repro now passes")".
- 근거: 그 예시는 `RULES_QUALITY.md:20`에 있다. 이 파일은 on-demand 모듈이다. `RULES.md:26`에는 "Before non-trivial work, state the concrete check that will prove 'done'"이라는 일반 문장만 있다. 커맨드 없는 작업에서는 그 예시가 보장되지 않는다(F6).
- 수정: 인용을 `RULES_QUALITY.md:20`으로 고치고, "커널은 일반 원칙만 진다"고 적는다.

**F9. 약점 1 행의 eval 인용이 다른 게이트를 가리킨다**
- 감사의 주장: "이 게이트를 재는 eval도 없다(`sdlc-playbook-alignment/03-analysis.md` 개선 8: "brainstorm '확인 없이 진행 금지'는 아직 재지 못한다")".
- 근거: 개선 8의 문구(`03-analysis.md:50`)는 brainstorm Approve 단계("no proceed without confirm", `brainstorm.md:17`)를 말한다. `/sc:plan` Load 단계의 draft 스펙 정지(`plan.md:13`)가 아니다. 다만 결론은 독립적으로 맞다. `grep -n "draft\|approved-for-plan" evals/tasks.yaml`에서 스펙 게이트 프로브는 없다.
- 수정: 근거를 "`evals/tasks.yaml`에 draft 스펙 게이트 프로브가 없다(grep)"로 바꾼다.

**F10. R12의 "보안이면 크기와 상관없이 먼저 묻는다"는 조건을 빠뜨렸다 (약점 5)**
- 근거: `RULES_QUALITY.md:12` R12는 "ambiguous request (2+ valid interpretations)"일 때만 적용되는 분기다. 모호하지 않은 한 파일짜리 권한 변경은 R12로 묻지 않는다. `/sc:implement` Checkpoint도 ">3 files"만 본다(`implement.md:15`). 크기와 무관하게 강화되는 것은 검증이다(`RULES_QUALITY.md:84` Level 4 승격, `:72` domain overrides). 승인이 아니다.
- 수정: "검증 강도는 위험 기반이지만, 승인은 모호성과 파일 수에 묶여 있다"로 고친다. 외부 약점 5의 "한 파일의 권한 수정" 예는 승인 측면에서 유효하다. F2와 합치면 약점 5는 "부분적으로 맞음"이다.

**F11. 외부안에서 유효한데 언급 없이 빠진 항목 — 주장 (f)**
- "통과시키려고 기대 결과를 바꿨다면 수용 기준에 맞는지 따로 검토"(외부 §8): 현재는 `troubleshoot.md:48` `fix-not-test`와 `test.md:26` `--fix`에만 있다. plan 경유 TDD(`plan.md:49-51`)와 `/sc:implement`에는 없다. 감사는 N5에서 RED 쪽 정의만 받고, 짝이 되는 GREEN 쪽 조항은 다루지 않았다.
- 소규모 작업 흐름(외부 §4.2): 감사 표에 행이 없다. 실제로는 커널 `purpose_before_action`(`RULES.md:16`), `verification_before_completion`, `checklist_scaling`(`RULES_QUALITY.md:66-74`), `03-analysis.md` 전제 3이 이미 다룬다. "이미 있음"으로 기각하는 행을 추가하면 된다.
- 수정: §2 표에 두 행을 추가한다. 앞의 것은 N5와 같은 처분을 받는다(관찰된 실패가 생기면 추가).

**F12. N5는 저장소의 콘텐츠 규칙과 충돌한다**
- 근거: 감사 스스로 "근거가 ECC 문헌뿐이고 이 저장소에서 관찰된 사고는 없다"고 적는다. `.claude/rules/content-quality.md` Improvement Workflow 1은 "Observe a real failure … before adding or rewording"이다. Anti-Patterns는 "'Improved' wording with no observed failure behind it → Revert"다.
- 수정: N5를 브랜치에서 빼고 보류 목록으로 옮긴다. 아니면 먼저 프로브로 실패를 관찰한다.

**F13. 외부 문서의 "문서 규약 위반" 중 프론트매터 부분은 틀렸다 (§3-5)**
- 근거: `RULES_DOCS.md:59` "Standalone research/+analysis/: optional {status, revised}". 이름 규약(`:23`, `<slug>-<username>-YYYY-MM-DD`)만 맞다. 지금 상태로 전체 테스트도 통과한다.
- 수정: "이름 규약만 어긋난다. 프론트매터는 선택이다"로 고친다.

**F14. "다단계 흐름을 잰 유일한 예외는 `implement-checkpoint`"는 틀렸다 (약점 6)**
- 근거: `evals/tasks.yaml:415-450`의 `implement-checkpoint`는 단일 프롬프트(`/sc:implement rename …`)가 첫 편집 전에 멈추는지를 잰다. 다단계 흐름이 아니다.
- 수정: "다단계 흐름을 잰 프로브는 없다. `implement-checkpoint`는 단일 커맨드 체크포인트만 잰다"로 고친다.

**F15. N6 프로브 설계가 그대로는 잘못 채점된다**
- 근거:
  - (i) `implement-proof-fail`: Proof가 범위 안의 코드 결함 때문에 실패하면 올바르게 행동하는 모델은 코드를 고쳐 Proof를 통과시키고 `complete`로 바꾼다. 그러면 "status가 complete가 아님" 채점에서 실패 판정을 받는다. 픽스처는 plan 범위 밖이면서 수정이 금지된 원인으로 실패해야 한다(예: plan의 `forbidden_changes` 파일, 없는 외부 서비스).
  - 기본 `max_turns: 12`(`tasks.yaml:20`)는 여러 작업짜리 plan에 부족할 수 있다.
  - "arm당 10회"는 맞지 않는다. vanilla에는 `/sc:implement`가 없고, `sc-candidate`는 커널 `RULES.md`만 바꾼다(`evals/README.md:13`). N2 전후 비교는 sc-full을 두 커밋에서 각각 돌려야 한다.
  - 채점 자체는 지원되는 checker로 가능하다. frontmatter 파싱은 `cmd_ok`, Proof 실패 보고는 `output_regex`, plan 파일 부재는 `file_absent_glob`이다(`run_eval.py:462-513`).
- 수정: 위 세 가지를 N6에 명시한다.

### S3 — 표현

**F16.** N4(b)의 "`command-local-flags` 테스트"는 존재하지 않는다(`grep -rn "command-local" tests` 결과 0건). 해당 테스트는 `tests/unit/test_command_structure.py`다(`.claude/rules/command-authoring.md:113`).

**F17.** 이유 ①의 "`RULES_DOCS.md:55,61`"에 `:62`(마이그레이션 표)를 더해야 한다. `:62`가 legacy `implemented → complete`로 매핑하므로, `implemented`를 상태로 되살리면 기존 매핑과 충돌한다. 구체적인 근거로 쓸 만하다.

**F18.** N1의 범위에 `README.md:289` "a step's output must be committed (or explicitly approved) before the next step runs"도 넣는 편이 맞다. 같은 강도 과장이다.

**F19.** 이유 ②의 "`reflect.md:45` never overrides completion status"는 외부안이 바꾸자고 하는 바로 그 경계라서 순환 논증에 가깝다. 실제로 힘이 있는 근거는 "`reflect`는 게이트가 없는 단계"(`README.md:317` "—")와 F5의 "never moves back" 충돌이다.

## 주장 (a)–(g) 검증표

| 주장 | 결과 | 요지 |
|---|---|---|
| (a) `complete`의 리더 없음 | **부분 유지** | 분기하는 리더는 없다. README 단계 매핑(`RULES_DOCS.md:30-33`), `promote-feature.md:18`, 이후 세션의 R02는 읽는다 (F5) |
| (b) 기본 경로에서 Proof를 실행하는 단계 없음 | **유지** | `Proof` 참조는 `plan.md:16,60`(작성), `verifier.md`, `test.md:18,40`(명시 호출)뿐이다. implement·reflect·task·build·커널 어디에도 없다 |
| (c) 일반 프롬프트에서 RULES_QUALITY 미로드 | **부분 유지** | 훅 주입은 없다. 커널 `RULES.md:40,43`이 Read를 지시하고, 세션 캐시가 유지된다. 트리거는 `/sc:` 일부와 `--iterations` (F6) |
| (d) 기본 스펙 리뷰는 같은 컨텍스트, `brainstorm.md:29` 근거와 어긋남 | **유지** | `review.md:27,41`. README 체인도 `--structured`가 없다. 격리돼도 `00-intent.md` 전달은 보장되지 않는다 (F3) |
| (e) 오분류는 `delegated`(안전) 쪽 | **불성립** | 관사 `a`와 라벨 단어 일치로 `confirmed` 오분류가 생기고, 그러면 감사가 빠진다. 숫자 라벨 응답은 분류되지 않는다 (F2) |
| (f) 3단계 상태·증거표·RULES_QUALITY 위치 기각의 공정성 | **결론 유지, 근거와 누락 보완 필요** | 기각 자체는 타당하다(더 강한 근거: never-moves-back). 다만 수정 후 재검증과 기대값 변경 검토를 근거 없이 버렸다 (F4, F11) |
| (g) hurry 30/30 vs 20/30, p = 0.0004 | **유지** | `pressure-readout/01-readout.md:17-20`, `README.md:17`, `02-verify.md:88`(p = 0.000399). 단서: sonnet low effort이고, batch A는 p = 0.105였으며, 셀 확장과 ceiling은 batch A를 본 뒤 정했다(`02-verify.md:49`, `00-prereg.md:63`) |

## N1–N6 처분

| 항목 | 처분 | 이유 |
|---|---|---|
| N1 README "hard gate" 정정 | **유지** | ADR-0001·`ARCHITECTURE.md:22`과 README `:308`·`:313`·`:433`의 모순이 소스로 확인된다. README 문구를 고정하는 테스트도 없다(grep 0건). `:289`도 범위에 넣는다(F18) |
| N2 완료 = Proof 실행 결과 | **변경** | 방향은 맞다(주장 (b) 유지). `Result:`에 커밋 SHA를 적고 이후 코드가 바뀌면 다시 돌린다(F4). RULES_DOCS를 고치면 canary 게이트 대상이다(F1). Proof를 실행할 수 없는 plan은 `implementing`에 영구히 남는다는 결과를 명시한다 |
| N3 구현 후 코드 리뷰 | **유지** | `README.md:297-298,303,330`으로 확인된다. `03-analysis.md` 전제 1(수동 호출)·전제 3(Small에 게이트 없음)과 맞는다. N2의 SHA 규칙과 짝을 지어야 한다 |
| N4 스펙 게이트 격리 | **변경** | 격리만으로는 원문 의도가 가지 않는다. `review.md`에서 `00-intent.md` 원문을 수용 기준으로 지목한다. (a)라면 README 체인도 고치고, (b)가 더 작을 수 있다(F3) |
| N5 유효한 RED | **보류(브랜치에서 제외)** | 관찰된 실패가 없어 `content-quality.md`와 충돌한다(F12). 기대값 변경 조항(F11)과 함께 실패 관찰 후 다시 본다 |
| N6 다단계 측정 | **변경** | 채점은 지원되는 checker로 가능하다. (i) 픽스처 실패 원인을 범위 밖으로 두고, `max_turns`를 올리고, 커밋 전후 sc-full 비교로 설계를 고친다. canary 문장도 고친다(F1, F15). 결정 모드 판정 프로브(iii)를 추가할 것을 권한다. 예: 스펙에 `a`가 포함된 비선택 응답을 둔 fixture에서 `mode` 값을 `cmd_ok`로 검사(F2) |

## 이 산출물 밖에서 본 것

- 외부 문서와 감사 모두 `RULES_DOCS.md:31`의 "phase never moves back"을 보지 않았다. 외부안의 상태 되돌림과 감사의 N2·N3 순서 모두에 걸리는 제약이다.
- `verifier.md:3` description의 "(the /sc:test → done gate, which requires test pass evidence)"도 프로즈 게이트를 "gate"로 부른다. N1과 같은 계열이지만 모델에게 주는 문구라 그대로 둘 수 있다. 판단이 필요하다.
- `RULES_INTERACTION.md`는 "/sc:brainstorm이 `[a]/[b]/[c]` 라벨을 정의한다"고 적지만, `brainstorm.md`에는 메뉴 라벨 정의가 없고 `<decision_modes>` 휴리스틱에만 문자 라벨이 나온다. 그래서 숫자 라벨로 질문하면 F2-4의 미분류가 생긴다. 한쪽 문구를 맞추는 것이 F2의 최소 수정에 포함될 수 있다.
- 서브에이전트로 가는 지침 전달(패킷, finding_policy)은 lean 라운드에서 미입증으로 남아 있다. N4는 격리의 효과를 잴 프로브 없이 비용만 늘릴 수 있다. N6에 "격리 리뷰어가 `00-intent.md`와 스펙의 반전을 잡는가" 프로브를 함께 두는 것을 검토한다.
- 전체 테스트는 현재 브랜치에서 녹색이다(`3752 passed, 3 skipped in 77.07s`). 외부 두 문서의 이름 규약 위반은 테스트에 걸리지 않는다.
