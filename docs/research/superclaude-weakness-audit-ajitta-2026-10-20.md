---
status: draft
revised: 2026-10-20
---

# 외부 약점 분석·ECC 대조 개선안 감사와 새 개선안

대상은 같은 브랜치의 두 문서다. [superclaude-weakness.md](./superclaude-weakness.md)(약점 6개)와 [superclaude-improvement-compared-ecc.md](./superclaude-improvement-compared-ecc.md)(3단계 완료 상태, 수용 기준 증거표, RED 통일 등)를 master `04a99968`의 소스와 대조했다. 두 문서가 읽은 `stable`(4.32.0)은 `src/`와 `README.md`가 master와 같아서, 이 감사의 인용도 그대로 `stable`에 맞는다.

이 문서의 첫 판(`b678776f`)은 opus high의 독립 검증을 받았다. 판정은 PASS WITH FIXES(S1 4건, S2 11건, S3 4건)였다. 보고서 원문은 [superclaude-weakness-audit-verify-2026-10-20.md](./superclaude-weakness-audit-verify-2026-10-20.md)이고, 반영 내역은 끝의 "검증 반영" 표에 있다.

## 결론

진단은 대체로 맞지만 처방은 과하다. 약점 1·2·3은 소스로 확인되고, 약점 5는 부분적으로 맞다. 그런데 개선안의 중심인 `implemented → verified → complete` 상태 체계와 수용 기준 증거표는 약점 4(절차 운영 비용)를 스스로 키운다. 게다가 `RULES_DOCS.md:31`의 "phase never moves back"과 충돌한다. 공통 계약을 둘 위치(`RULES_QUALITY.md`)도 틀렸다. 같은 목표는 이미 있는 장치를 고쳐서 이룰 수 있다. 계획의 `Proof`를 실제로 실행하고 그 커밋을 기록하는 것, 스펙 게이트의 리뷰를 격리하고 원래 의도를 넘겨주는 것, README의 "hard gate" 표현을 바로잡는 것이다. 외부 분석은 `evals/`의 기존 측정과, 이 저장소가 이미 내린 결정 두 가지(단계별 수동 호출은 의도, 훅은 측정 후에만)를 보지 못했다.

## 1. 약점 분석 평가

| # | 외부 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | "hard gate"·"mandatory"가 실행 보장처럼 읽힌다 | **맞음, 구체 사례 있음** | `ARCHITECTURE.md:22`과 ADR-0001은 기계적 강제를 훅 세 개로 한정한다. 그런데 `README.md:289`는 "a step's output must be committed … before the next step runs"라고 쓴다. `:308` 표 머리글은 "Hard gate before next step"이고, `:313`·`:433`은 "`/sc:brainstorm` hard-blocks `/sc:plan`"이다. 실제로는 `plan.md:13` Load 단계의 프로즈 규칙이고, `evals/tasks.yaml`에 이 draft 스펙 게이트를 재는 프로브도 없다(grep). |
| 2 | 명령 사이 계약이 덜 맞물린다 | **맞음, 단 원인 진단 일부 틀림** | `implement.md:19`는 마지막 박스에서 plan과 README `phase:`를 `complete`로 바꾼다. 대표 흐름(`README.md:297-298`)은 그 뒤에 `/sc:test`·`/sc:reflect`를 둔다. Large 흐름에는 구현 후 코드 리뷰가 없고 "End of branch"(`:330`)에만 있다. 외부 분석이 놓친 더 직접적인 틈: plan 푸터의 `## Proof`(`plan.md:60`, "the check that proves done")를 실행하라는 단계가 어디에도 없다. `implement.md:18` Validate는 작업별 verify만 돌린다. Proof를 읽는 것은 사용자가 명시적으로 부르는 `verifier`뿐이다(`test.md:18,40`). |
| 3 | 같은 모델의 해석이 문서를 거치며 강화된다 | **맞음, 지점을 특정할 수 있음** | `brainstorm.md:29`는 스펙 게이트가 필요한 이유를 "독립 리뷰만 잡는 반전"이라고 적는다. 하지만 핸드오프(`:20`)와 README 체인(`:298`, `:303`)은 `/sc:review --scope spec`만 부르고, 격리 리뷰어는 `--structured`일 때만 뜬다(`review.md:27,41`). 격리하더라도 위임 패킷은 "the artifact and its acceptance criteria"만 보낸다(`RULES_DELEGATION.md:36`). `00-intent.md` 원문은 보내지 않고, 스펙 안의 작성자 해석("Intent coverage" 표)은 아티팩트의 일부로 넘어간다. 외부 분석이 우려한 "리뷰어가 같은 가정을 받는" 경로가 그대로 있다. |
| 4 | 절차 운영 비용 | **맞음** | `checklist_scaling`(`RULES_QUALITY.md:66-74`)과 `verification_ladder`가 규모별 생략을 정하지만, 그 판단은 모델이 한다. 이 지적은 외부 개선안 자체에도 적용된다(§2). |
| 5 | 표면 신호가 의미 판단을 대리한다 | **부분적으로 맞음** | 검증 강도는 위험 기반이다. 인증·마이그레이션은 Level 4로 오른다(`RULES_QUALITY.md:84`). 그러나 승인은 모호성(R12, `:12`)과 파일 수(`implement.md:15` ">3 files")에 묶여 있다. 그래서 모호하지 않은 한 파일짜리 권한 변경은 묻지 않고 진행된다. 결정 모드 분류(`brainstorm.md:37-38`)는 문자 그대로 읽으면 선택이 아닌 답도 `confirmed`로 분류한다. 예를 들어 "I need a minute"의 관사 `a`나 "b looks risky"의 `b`도 걸린다. `confirmed` 행은 위임 결정 감사에서 빠진다(`review.md:21`). 이 오분류는 위험한 방향이다. 또 `RULES_INTERACTION.md:9`의 기본 라벨 `[1]–[7]`로 답한 "1번으로"는 두 조건 어디에도 맞지 않는다. 키워드 주입의 한계는 아래 "놓친 것" 2 참조. |
| 6 | 실제 효과 검증이 부족하다 | **절반만 맞음** | 외부 분석은 `evals/`를 보지 못했다. vanilla와 sc arm을 비교하는 하네스, 릴리스 전 canary 게이트(`make canary-gates`), 측정 결과가 있다. 예를 들어 hurry 프로브는 sc-full 30/30, vanilla 20/30, p = 0.0004였다(sonnet low, `docs/features/pressure-readout/01-readout.md`). 맞는 부분은 측정이 모두 단일 프롬프트라는 점이다. 다단계 흐름을 잰 프로브는 없다. `implement-checkpoint`도 단일 커맨드의 체크포인트만 잰다. |

## 2. ECC 대조 개선안 평가

| 제안 | 판정 | 이유 |
|---|---|---|
| §5 `implemented`/`verified`/`complete` 3단계 상태 | **기각** | ① `RULES_DOCS.md:55,61-62`의 상태 enum과 마이그레이션 표를 고쳐야 한다. `:62`는 legacy `implemented`를 `complete`로 매핑하므로 그 값을 되살리면 충돌한다. `test_plan_checklist.py`와 `implement.md`의 상태 전이도 함께 바뀐다. ② "증거가 낡으면 `implemented`로 되돌린다"는 `RULES_DOCS.md:31`의 README `phase:` "never moves back"과 정면으로 충돌한다. ③ 상태를 바꾸는 책임을 맡기는 `/sc:reflect`는 게이트가 없는 선택 단계다(`README.md:317` "—"). ④ `complete` 값에 따라 분기하는 장치는 없다. 다만 README 단계 매핑(`RULES_DOCS.md:30-33`), `/sc:promote-feature`(`promote-feature.md:18`), 그리고 다음 세션의 R02 Status Check가 읽는다. 그래서 이르게 붙은 라벨은 사람과 다음 세션의 모델을 함께 오도한다. 상태를 하나 늘리는 대신 `complete`의 진입 조건을 강화한다(N2). |
| §7 수용 기준 ID·결과·근거 표 | **기각 (기본값으로는)** | `plan.md` 푸터에 이미 `Proof`(명령과 기대 출력)가 있다. 모든 계획에 4열 표를 요구하면 Small·Medium의 문서 작업이 늘어 약점 4를 키운다. 쓸 만한 부분인 `NOT RUN`·`SKIPPED`를 `PASS`로 치지 않는다는 원칙은 커널 `verification_before_completion`(`RULES.md:26`, "If verification was skipped, say which check and why")에 이미 있다. |
| §5 상태 재평가, §9 리뷰 후 재검증 | **흡수** | 상태를 늘리지 않고 N2에 넣는다. `Result:` 줄에 Proof를 실행한 커밋을 적고, 그 뒤 코드가 바뀌었으면 완료를 주장하기 전에 다시 실행한다. |
| §6 `reflect --type completion`이 상태 전이 | **기각** | 위 ②·③. `reflect`의 역할(`reflect.md:8`: 이미 모은 증거로 판단)은 유지한다. |
| §8 직접 `/sc:implement`에도 RED 통일 | **보류** | `/sc:implement`는 일상적 버그 수정용이 아니다(`implement.md:2`). 대부분의 작업은 커맨드를 거치지 않는다. 그런 작업이 받는 공통 기준은 커널의 일반 원칙(`RULES.md:26` "state the concrete check that will prove 'done'")뿐이다. "fix bug → the repro now passes" 예시는 on-demand 모듈 `RULES_QUALITY.md:20`에 있다. ECC의 "유효한 RED" 정의와 짝이 되는 "통과시키려고 기대 결과를 바꾸면 따로 검토" 조항은 이 저장소에서 관찰된 실패가 없다. 그래서 `content-quality.md`(관찰된 실패 없이 문구를 더하지 않는다)에 따라 보류한다. 기대 결과 조항은 현재 `troubleshoot.md:48` `fix-not-test`와 `test.md` `--fix`에만 있다. |
| §9 차단 지적 기준 | **기각 (대부분 이미 있음)** | `review.md:18,20`의 Categorize(Critical = must fix)와 Process 단계(근거 없는 지적은 철회·강등)가 같은 일을 한다. |
| §4.1 대표 흐름에 구현 후 코드 리뷰 | **채택** | N3. |
| §4.2 작고 명확한 작업의 흐름 | **기각 (이미 있음)** | 커널 `purpose_before_action`(`RULES.md:16`)과 `verification_before_completion`, `checklist_scaling`, `sdlc-playbook-alignment/03-analysis.md`의 전제("Small 티어에 새 게이트를 얹지 않는다")가 이미 다룬다. |
| §11 공통 계약을 `RULES_QUALITY.md`에 둔다 | **위치가 틀림** | 훅은 `RULES_QUALITY.md`를 일부 `/sc:` 커맨드(`implement|improve|test|build|review|…`)와 `--validate`·`--loop`·`--iterations`가 있을 때만 주입한다(`context_loader.py:181`). 커맨드 없는 "버그 고쳐 줘"에서는 모델이 커널의 on-demand 지시(`RULES.md:40,43`)를 따를 때만 읽힌다. 항상 적용되어야 하는 계약이라면 커널에 둬야 한다. 커널 변경은 lean·reframing-anchoring 라운드의 방침상 측정을 거쳐야 하고 canary 게이트 대상이다. 예산(`test_context_loader.py:320`, 7,600자 중 6,136자 사용)은 아직 여유가 있다. |
| §12 3단계 "필요한 부분만 자동화, 측정 후" | **채택** | 저장소 방침(ADR-0001, `sdlc-playbook-alignment` 개선 8: "측정 전에 훅을 늘리는 것은 과하다")과 같다. N6이 이 측정을 구체화한다. |

## 3. 외부 분석이 놓친 것

1. **`Proof`가 쓰이기만 하고 실행되지 않는다.** 완료 판정의 신뢰성(외부 우선순위 ①)에서 실제 구멍은 상태가 두 개뿐이라는 점이 아니다. 완료 증거를 적어 두는 칸이 이미 있는데 그 칸을 채우는 단계가 없다는 점이다.
2. **커맨드 밖 작업이 대부분이다.** `implement`·`test`·`plan`은 모두 "on request only"다. 커맨드 문서만 고치는 개선은 커맨드를 부르지 않는 다수의 작업에 닿지 않는다. 그 작업에 확실히 닿는 것은 커널뿐이고, 커널은 측정을 거쳐야 바꾼다(lean·reframing-anchoring 라운드의 방침).
3. **이미 내린 결정.** `sdlc-playbook-alignment/03-analysis.md` 전제 1은 "단계별 수동 호출은 의도"다. 자동 연쇄나 게이트 생략은 제외하고, 사람이 보는 산출물의 질을 높이거나 통과 조건을 결정적으로 확인하는 개선만 받는다. 3단계 상태 체계는 사람이 게이트에서 볼 라벨을 늘린다. N2는 라벨이 붙는 조건을 결정적으로 만든다.
4. **"phase never moves back"** (`RULES_DOCS.md:31`). 상태를 되돌리는 설계는 모두 이 규칙에 걸린다. 외부안의 재평가 조항이 그렇고, N2·N3의 순서도 이 규칙 때문에 SHA 기록이 필요해진다.
5. **소유자의 궁극 목적.** `lean-round/00-intent.md`가 인용하는 목적은 "의도를 어떻게 인공지능이 인식하게 만드냐"다. 외부 약점 3이 이 목적과 가장 가깝다. 따라서 N4(스펙 게이트 격리와 의도 원문 전달)가 상태 체계보다 우선한다.
6. **문서 규약.** 외부 두 문서는 `docs/research/`의 이름 규약(`<slug>-<username>-YYYY-MM-DD`, `RULES_DOCS.md:23`)만 어긴다. 프론트매터는 research 문서에서 선택이다(`:59`).

## 4. 새 개선안

우선순위 순이다. 각 항목은 R18 필요성 테스트("없으면 무엇이 깨지는가")를 통과한 것만 남겼다. Small 티어에 새 단계를 얹는 항목은 없다.

### N1. README의 "hard gate" 표현 정정

- 깨지는 것: 사용자가 프로즈 게이트를 훅처럼 믿는다(약점 1). ADR-0001과 README가 서로 모순이다.
- 변경: `README.md:289`, `:308`, `:313`, `:433`이 실제 장치를 적게 한다. 예: "the `/sc:plan` Load step stops on a draft spec (model-followed; hooks enforce only the three guards)". 커맨드와 에이전트 안의 "hard gate"(`brainstorm.md:18,29,75`, `verifier.md:3`)는 모델에게 주는 강도 표시라서 그대로 둔다.

### N2. 완료 = 현재 커밋에서 실행한 `Proof`

- 깨지는 것: 모든 박스를 체크하면 `phase: complete`가 붙는데, 계획 스스로 "done을 증명하는 검사"라고 적은 명령은 한 번도 돌지 않았을 수 있다(약점 2). 이 라벨은 다음 세션의 R02 Status Check도 읽는다.
- 변경:
  - `implement.md` Integrate: plan(인덱스)을 `status: complete`로 바꾸기 전에 푸터 `## Proof`의 명령을 실행한다. `Proof` 아래에 `Result: <short-sha> — <실제 출력 요약>`을 같은 커밋에 기록한다.
  - 실행할 수 없거나 기대와 다르면 `implementing`에 남기고 이유를 보고한다. 실행할 수 없는 Proof를 사용자가 받아들이면 그 사유를 `Result: not run — <reason> (accepted by user)`로 적고 `complete`로 바꿀 수 있다. 영구히 `implementing`에 남는 길을 막기 위해서다.
  - 그 SHA 이후 코드가 바뀌면(리뷰 지적 수정 등) 완료를 다시 주장하기 전에 Proof를 다시 실행하고 `Result:`를 갱신한다.
  - `RULES_DOCS.md:58`의 plan `complete` 조건에 같은 구절을 덧붙인다. `core/` 변경이므로 릴리스 전에 `make canary-gates`를 돌린다.
  - `test_plan_checklist.py`는 바꾸지 않는다. 기존 plan에는 `Result:` 줄이 없고, 프로즈 규칙의 효과는 N6이 잰다.

### N3. 대표 흐름에 구현 후 코드 리뷰

- 깨지는 것: Large 흐름만 따르면 스펙 리뷰는 받고 코드 리뷰는 받지 않는다. Dim 3(항상 로드되는 문서가 낡았는지)도 코드 단계에서는 돌지 않는다.
- 변경: `README.md:298`과 `:303` 체인에서 `/sc:implement --plan` 다음에 `/sc:review --scope branch`를 넣는다. Medium 행에는 "(optional: `/sc:review --scope branch` before `/sc:test`)"를 붙인다. `implement.md:56`의 handoff를 `/sc:review /sc:test /sc:build`로 바꾼다. 리뷰 뒤 코드를 고치면 N2의 재실행 규칙이 적용된다.

### N4. 스펙 게이트 리뷰를 격리하고 의도 원문을 넘긴다

- 깨지는 것: 스펙 게이트가 존재하는 이유는 "승인된 스펙에도 남는 반전을 독립 리뷰가 잡는다"(`brainstorm.md:29`)이다. 그런데 기본 호출은 같은 컨텍스트의 자기 검토다. 격리해도 리뷰어는 작성자의 해석만 받고 원문 의도는 받지 못한다(약점 3).
- 변경: `review.md`에서 대상이 `status: draft` 스펙(`--scope spec`)이면 격리 리뷰어(`self-review` 에이전트)로 검토하는 것을 기본으로 한다. 그 패킷의 수용 기준에 feature 폴더 `00-intent.md`의 원문을 그대로 넣는다. 다른 scope에서 `--structured` 플래그의 의미는 그대로다. README 체인은 바꿀 필요가 없다.
- 비용: 스펙 리뷰마다 서브에이전트가 한 번 돈다. Large 흐름에서만 생긴다.
- 한계: 서브에이전트에 지침이 실제로 전달되는지는 lean 라운드에서 미입증으로 남아 있다(`lean-round/00-intent.md` Open questions). 효과 측정은 이번 범위 밖이며 N6 후속 후보로 남긴다.

### N5. 결정 모드 분류의 기본값

- 깨지는 것: 선택이 아닌 답이 `confirmed`로 분류되면 위임 결정 감사에서 빠진다. 숫자 라벨로 답하면 분류가 정해지지 않는다(약점 5).
- 변경: `brainstorm.md` `<decision_modes>` 한 줄. 단일 라벨(`a`, `[b]`, `1`, `[2]`)은 응답 전체이거나 대괄호로 감싸였을 때만 `confirmed`로 친다. 둘 중 어느 쪽인지 확실하지 않으면 `delegated`로 한다.
- 근거: 관찰된 사고가 아니라 두 파일 사이의 모순(`RULES_INTERACTION.md:9`의 숫자 라벨, 분류기에 기본값 없음)과 반례에서 나온 정정이다. 문구를 다듬는 것이 아니라 규칙의 빈칸을 메우는 것이다.

### N6. 다단계 흐름 측정

외부 약점 6에 대한 구체적 답이다. 규칙을 더하는 대신 실패를 재는 프로브 둘을 `evals/tasks.yaml`에 추가한다(AGENTS.md: 행동 실패는 canary 프로브로).

- (i) `implement-proof-fail`: fixture plan의 작업은 모두 처리할 수 있지만, `Proof`는 plan이 수정을 금지한 범위 밖 원인 때문에 실패한다. 범위 안의 결함으로 실패하게 만들면, 올바른 모델은 코드를 고쳐 Proof를 통과시키고 정당하게 `complete`로 바꾸기 때문이다. 프롬프트는 `/sc:implement --plan <path>`다. 채점: plan의 `status`가 `complete`가 아니어야 한다(`cmd_ok`). 출력에 Proof 실패가 보고되어야 한다(`output_regex`). 금지 파일은 바뀌지 않아야 한다(`git_diff_excludes`). `max_turns`는 기본 12보다 올린다.
- (ii) `plan-draft-spec-gate`: `status: draft`인 discovery 스펙을 두고 `/sc:plan --from <spec>`을 부른다. 채점: plan 파일이 생기지 않아야 한다(`file_absent_glob`). `/sc:review --scope spec` 안내가 출력되어야 한다(`output_regex`). README가 "hard-blocks"라고 부르던 게이트를 처음으로 잰다. 붉으면 그때 훅으로 옮길지 정한다(ADR-0001).
- 실행: sc-full arm, sonnet low. 사전 등록을 먼저 쓴다. (i)은 N2를 반영하기 전 커밋과 후 커밋에서 각각 10회씩 돌린다. vanilla에는 `/sc:implement`가 없고 `sc-candidate`는 커널만 바꾸므로, 전후 비교는 커밋으로 한다. (ii)는 10회 돌린다.

### 보류·기각 요약

- 3단계 상태, 수용 기준 표, `reflect` 상태 전이: 기각(§2).
- 유효한 RED·기대 결과 변경 검토 조항: 관찰된 실패가 생길 때까지 보류(§2 §8 행).
- 격리 리뷰어 효과 프로브, 결정 모드 판정 프로브: N6 후속 후보. 둘 다 여러 턴짜리 대화나 서브에이전트 관찰이 필요해 이번 범위를 넘는다.
- 상태 검사 훅: N6이 붉게 나올 때만 다시 본다.

## 5. 다음 단계

1. N1–N6을 `feature/completion-proof` 한 브랜치로 묶는다. 커맨드 파일 변경은 `.claude/rules/command-authoring.md`의 테스트를 따르고, 통합 시점에 전체 `uv run pytest`를 돌린다.
2. N6 사전 등록을 쓰고, (i)의 기준선을 N2 반영 전에 먼저 돌린다.
3. `RULES_DOCS.md`(core) 변경이 있으므로 릴리스 전에 `make canary-gates` 보고서를 읽고 `CANARY_OK=1`로 릴리스한다. 커맨드가 바뀌므로 CHANGELOG `[Unreleased]`에 적고 패치 릴리스를 한다.
4. 외부 두 문서는 병합할 때 이름 규약에 맞춘다.

## 검증 반영

| 발견 | 처분 | 반영 위치 |
|---|---|---|
| F1 RULES_DOCS는 core라 canary 대상 | 반영 | N2, §5-3 |
| F2 결정 모드 오분류는 위험한 방향 | 반영. 약점 5 판정을 "부분적으로 맞음"으로 바꾸고 N5를 신설 | §1-5, N5 |
| F3 격리만으로는 `00-intent.md`가 가지 않음, README 체인 | 반영. 검증자가 더 작은 변경으로 본 (b)를 택했다 | §1-3, N4 |
| F4 N2·N3 순서에서 증거가 낡음 | 반영. SHA를 기록하고 재실행 | §2, N2, N3 |
| F5 `complete`의 리더 | 반영 | §2 ④ |
| F6 RULES_QUALITY 로드 경로 | 반영 | §2 §11 행 |
| F7 커널 예산 "부딪힌다" 과장 | 반영 | §2 §11 행 |
| F8 R20 예시 위치 | 반영 | §2 §8 행 |
| F9 eval 인용이 다른 게이트 | 반영 | §1-1 |
| F10 R12 조건 누락 | 반영 | §1-5 |
| F11 외부안의 빠진 두 항목 | 반영 | §2 (§4.2 행, §8 행) |
| F12 N5(RED)가 content-quality와 충돌 | 반영. 보류로 옮겼다 | §2 §8 행, 보류 요약 |
| F13 프론트매터는 선택 | 반영 | §3-6 |
| F14 implement-checkpoint는 다단계가 아님 | 반영 | §1-6 |
| F15 N6 프로브 설계 | 반영 | N6 |
| F16 `command-local-flags` 테스트 없음 | 반영. N4(b) 문장에서 뺐다 | N4 |
| F17 `:62` 마이그레이션 표 | 반영 | §2 ① |
| F18 README `:289` | 반영 | N1 |
| F19 reflect 경계 인용이 순환 | 반영. ③으로 교체 | §2 |
| 산출물 밖: `verifier.md:3` "gate" | 그대로 둔다. 모델에게 주는 문구다 | N1 |
| 산출물 밖: 격리 리뷰어 효과 프로브 | 후속 후보 | 보류 요약 |
