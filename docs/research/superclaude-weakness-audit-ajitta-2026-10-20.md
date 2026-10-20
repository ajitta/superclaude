---
status: draft
revised: 2026-10-20
---

# 외부 약점 분석·ECC 대조 개선안 감사와 새 개선안

대상은 같은 브랜치의 두 문서다. [superclaude-weakness.md](./superclaude-weakness.md)(약점 6개)와 [superclaude-improvement-compared-ecc.md](./superclaude-improvement-compared-ecc.md)(3단계 완료 상태, 수용 기준 증거표, RED 통일 등)를 master `04a99968`의 소스와 대조했다. 두 문서가 읽은 `stable`(4.32.0)은 `src/`와 `README.md`가 master와 같아서, 이 감사의 인용도 그대로 `stable`에 맞는다.

## 결론

진단은 대체로 맞지만 처방은 과하다. 약점 1·2·3은 소스로 확인된다. 그런데 개선안의 중심인 `implemented → verified → complete` 상태 체계와 수용 기준 증거표는 약점 4(절차 운영 비용)를 스스로 키우고, `/sc:reflect`의 경계(`never overrides completion status`)와 충돌한다. 공통 계약을 둘 위치(`RULES_QUALITY.md`)도 틀렸다. 같은 목표는 이미 있는 장치 세 개만으로 이룰 수 있다. 계획의 `Proof`를 실제로 실행하는 것, 스펙 게이트의 리뷰를 격리하는 것, README의 "hard gate" 표현을 바로잡는 것이다. 외부 분석은 `evals/`의 기존 측정과, 이 저장소가 이미 내린 결정 두 가지(단계별 수동 호출은 의도, 훅은 측정 후에만)를 보지 못했다.

## 1. 약점 분석 평가

| # | 외부 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | "hard gate"·"mandatory"가 실행 보장처럼 읽힌다 | **맞음, 구체 사례 있음** | `ARCHITECTURE.md:22`과 ADR-0001은 기계적 강제를 훅 세 개로 한정한다. 그런데 `README.md:308` 표 머리글은 "Hard gate before next step", `:313`·`:433`은 "`/sc:brainstorm` hard-blocks `/sc:plan`"이라고 쓴다. 실제로는 `plan.md:13` Load 단계의 프로즈 규칙이고, 이 게이트를 재는 eval도 없다(`sdlc-playbook-alignment/03-analysis.md` 개선 8: "brainstorm '확인 없이 진행 금지'는 아직 재지 못한다"). |
| 2 | 명령 사이 계약이 덜 맞물린다 | **맞음, 단 원인 진단 일부 틀림** | `implement.md:19`는 마지막 박스에서 plan과 README `phase:`를 `complete`로 바꾼다. 대표 흐름(`README.md:297-298`)은 그 뒤에 `/sc:test`·`/sc:reflect`를 둔다. Large 흐름에는 구현 후 코드 리뷰가 없고 "End of branch"(`:330`)에만 있다. 외부 분석이 놓친 더 직접적인 틈: plan 푸터의 `## Proof`(`plan.md:60`, "the check that proves done")를 실행하라는 단계가 어디에도 없다. `implement.md:18` Validate는 작업별 verify만 돌린다. Proof를 읽는 것은 사용자가 명시적으로 부르는 `verifier`뿐이다(`test.md:18,40`). |
| 3 | 같은 모델의 해석이 문서를 거치며 강화된다 | **맞음, 지점을 특정할 수 있음** | `brainstorm.md:29`는 스펙 게이트가 필요한 이유를 "독립 리뷰만 잡는 반전"이라고 적는다. 하지만 핸드오프(`:20`)는 `/sc:review --scope spec`만 부르고, 격리 리뷰어는 `--structured`일 때만 뜬다(`review.md:27,41`). 기본 경로에서는 스펙을 쓴 그 컨텍스트가 스펙을 검토한다. 게이트의 근거와 기본 동작이 어긋난다. 위임 결정 감사(`--audit-delegated`)만 패킷 규칙으로 격리된다. |
| 4 | 절차 운영 비용 | **맞음** | `checklist_scaling`(`RULES_QUALITY.md`)과 `verification_ladder`가 규모별 생략을 정하지만, 그 판단은 모델이 한다. 이 지적은 외부 개선안 자체에도 적용된다(§2). |
| 5 | 표면 신호가 의미 판단을 대리한다 | **과장** | 승인 기준은 파일 수만이 아니다. R12는 보안·데이터·파괴적 작업이면 크기와 상관없이 먼저 묻고(`RULES_QUALITY.md` R12), 검증 사다리도 인증·마이그레이션을 Level 4로 올린다. 결정 모드 분류(`brainstorm.md:37-38`)는 오분류가 나도 대부분 `delegated` 쪽으로 기운다. 그 결과는 독립 감사가 한 번 더 도는 것이라 안전한 방향이다. "한국어 선택을 놓친다"는 사례(예: "1번으로")도 감사가 추가될 뿐 누락되지 않는다. 키워드 주입은 실제 한계다. 아래 "놓친 것" 2 참조. |
| 6 | 실제 효과 검증이 부족하다 | **절반만 맞음** | 외부 분석은 `evals/`를 보지 못했다. vanilla와 sc arm을 비교하는 하네스, 릴리스 전 canary 게이트(`make canary-gates`), 측정 결과가 있다. 예를 들어 hurry 프로브는 sc-full 30/30, vanilla 20/30, p = 0.0004였다(`docs/features/pressure-readout/`). 맞는 부분은 측정이 단일 프롬프트 프로브라는 점이다. plan → implement → status로 이어지는 다단계 흐름은 아무도 재지 않았다(유일한 예외는 `implement-checkpoint`). |

## 2. ECC 대조 개선안 평가

| 제안 | 판정 | 이유 |
|---|---|---|
| §5 `implemented`/`verified`/`complete` 3단계 상태 | **기각** | ① `RULES_DOCS.md:55,61` 상태 enum, 마이그레이션 표, `test_plan_checklist.py`, `implement.md` 상태 전이를 모두 고쳐야 한다. ② 상태를 바꾸는 책임을 `/sc:reflect`에 주는데, `reflect.md:45`는 `never overrides completion status`다. `reflect`는 선택 단계이기도 하다. ③ `complete`를 읽는 소비자가 저장소 안에 없다(`grep`: `implement.md`가 쓰기만 하고, 읽는 것은 이 저장소 전용 테스트뿐). 라벨이 이르게 붙는 비용은 사람이 오해하는 정도다. 이를 막는 데는 상태 하나를 늘리지 않고 `complete`의 진입 조건을 강화하면 된다(N2). |
| §7 수용 기준 ID·결과·근거 표 | **기각 (기본값으로는)** | `plan.md` 푸터에 이미 `Proof`(명령과 기대 출력)가 있다. 모든 계획에 4열 표를 요구하면 Small·Medium에 문서 작업이 늘어 약점 4를 키운다. 쓸 만한 부분인 `NOT RUN`·`SKIPPED`를 `PASS`로 치지 않는다는 원칙은 커널 `verification_before_completion`(`RULES.md:26`, "If verification was skipped, say which check and why")에 이미 있다. |
| §6 `reflect --type completion`이 상태 전이 | **기각** | 위 ②와 같다. `reflect`의 역할(`reflect.md:8`: 이미 모은 증거로 판단)은 유지한다. |
| §8 직접 `/sc:implement`에도 RED 통일 | **축소 채택** | `/sc:implement`는 일상적 버그 수정용이 아니다(`implement.md:2`). 대부분의 작업은 커맨드를 거치지 않으므로, 공통 기준은 이미 커널 R20(`RULES.md` `verification_before_completion`, "fix bug → the repro now passes")이 진다. 받을 만한 것은 ECC의 "유효한 RED" 정의 한 구절뿐이다. 실행했고, 의도한 이유로 실패했고, import·설정 오류가 아닐 것(N5). |
| §9 차단 지적 기준 | **기각 (대부분 이미 있음)** | `review.md:18,20` Categorize(Critical = must fix)와 Process 단계(근거 없는 지적은 철회·강등)가 같은 일을 한다. |
| §4.1 대표 흐름에 구현 후 코드 리뷰 | **채택** | N3. |
| §11 공통 계약을 `RULES_QUALITY.md`에 둔다 | **위치가 틀림** | `RULES_QUALITY.md`는 `/sc:` 커맨드나 `--validate`·`--loop`가 있을 때만 주입된다(`context_loader.py:180-183`). 커맨드 없이 "이 버그 고쳐 줘"라고 하면 로드되지 않는다. 항상 로드되는 공통 계약은 이미 커널(`purpose_before_action`, `verification_before_completion`)에 있다. 커널을 늘리면 lean 라운드의 예산 테스트(`TestCoreLiteSplit`)와 부딪힌다. |
| §12 3단계 "필요한 부분만 자동화, 측정 후" | **채택** | 저장소 방침(ADR-0001, `sdlc-playbook-alignment` 개선 8: "측정 전에 훅을 늘리는 것은 과하다")과 같다. N6이 이 측정을 구체화한다. |

## 3. 외부 분석이 놓친 것

1. **`Proof`가 쓰이기만 하고 실행되지 않는다.** 완료 판정 신뢰성(외부 우선순위 ①)의 실제 구멍은 상태가 두 개뿐이라는 점이 아니다. 완료 증거를 적어 두는 칸이 이미 있는데, 그 칸을 채우는 단계가 없다는 점이다.
2. **커맨드 밖 작업이 대부분이다.** `implement`·`test`·`plan`은 모두 "on request only"다. 커맨드 문서만 고치는 개선은 커맨드를 부르지 않는 다수의 작업에 닿지 않는다. 그 작업에 닿는 것은 커널뿐이고, 커널은 측정을 거쳐야 바꾼다(lean·reframing-anchoring 라운드의 방침).
3. **이미 내린 결정.** `sdlc-playbook-alignment/03-analysis.md`의 전제 1은 "단계별 수동 호출은 의도"다. 자동 연쇄나 게이트 생략은 제외하고, 사람이 보는 산출물의 질을 높이거나 통과 조건을 결정적으로 확인하는 개선만 받는다. 3단계 상태 체계는 사람이 게이트에서 볼 라벨을 늘린다. 반면 N2는 라벨이 붙는 조건을 결정적으로 만든다.
4. **소유자의 궁극 목적.** `lean-round/00-intent.md`가 인용하는 목적은 "의도를 어떻게 인공지능이 인식하게 만드냐"다. 외부 약점 3이 이 목적과 가장 가깝다. 따라서 N4(스펙 게이트 격리)가 상태 체계보다 우선한다.
5. **문서 규약.** 외부 두 문서에는 `docs/research/`의 이름 규약(`<주제>-<user>-<date>.md`)과 `status`/`revised` 프론트매터가 없다. 병합하려면 이름을 바꾸거나 이 감사 문서의 부록으로 남겨야 한다.

## 4. 새 개선안

우선순위 순이다. 각 항목은 R18 필요성 테스트("없으면 무엇이 깨지는가")를 통과한 것만 남겼다. Small 티어에 새 단계를 얹는 항목은 없다.

### N1. README의 "hard gate" 표현 정정 — 결정 필요 없음

- 깨지는 것: 사용자가 프로즈 게이트를 훅처럼 믿는다(약점 1). ADR-0001과 README가 서로 모순이다.
- 변경: `README.md:308` 표 머리글을 "Required before next step"으로 바꾼다. `:313`·`:433`의 "hard-blocks"는 "the `/sc:plan` Load step stops on a draft spec (model-followed; hooks enforce only the three guards)"처럼 실제 장치를 적는다. 커맨드 안의 "hard gate"(`brainstorm.md:18,29,75`)는 모델에게 주는 강도 표시라서 그대로 둔다.
- 비용: README 몇 줄. `src/` 변경이 없으므로 릴리스는 다음 릴리스에 묶는다.

### N2. 완료 = `Proof` 실행 결과 — ★채택 권고

- 깨지는 것: 모든 박스를 체크하면 `phase: complete`가 붙는데, 계획 스스로 "done을 증명하는 검사"라고 적은 명령은 한 번도 돌지 않았을 수 있다(약점 2, 외부 §3.1).
- 변경: `implement.md` Integrate 단계에 한 문장을 넣는다. plan(인덱스)을 `status: complete`로 바꾸기 전에 푸터 `## Proof`의 명령을 실행하고, 실제 출력 요약을 `Proof` 아래 `Result:` 한 줄로 같은 커밋에 기록한다. 실행할 수 없거나 기대와 다르면 `implementing`에 남기고 이유를 보고한다. `RULES_DOCS.md:58`의 plan `complete` 조건에도 같은 조건을 한 구절 덧붙인다.
- 선택지: (a) ★프로즈 한 문장 + canary 프로브(N6-i). (b) (a) + `test_plan_checklist.py`에 "이후 `complete`가 된 plan은 `Result:` 줄이 있어야 한다" 검사를 추가한다. 이 저장소의 plan만 지키고, 기존 plan은 날짜로 제외한다. (c) 외부안의 3단계 상태 — 기각 권고(§2).
- 상태 enum, `reflect`, README `phase:` 매핑은 바꾸지 않는다.

### N3. 대표 흐름에 구현 후 코드 리뷰 — ★Large는 필수 단계, Medium은 선택

- 깨지는 것: Large 흐름만 따르면 스펙 리뷰는 받고 코드 리뷰는 받지 않는다. Dim 3(항상 로드되는 문서가 낡았는지)도 코드 단계에서는 돌지 않는다.
- 변경: `README.md:298`과 `:303` 체인에서 `/sc:implement --plan` 다음에 `/sc:review --scope branch`를 넣는다. Medium 행에는 "(optional: `/sc:review --scope branch` before `/sc:test`)"를 붙인다. `implement.md:56` handoff를 `/sc:review /sc:test /sc:build`로 바꾼다.
- 선택지: (a) ★위와 같이. (b) Large·Medium 모두 필수. Medium의 의례가 늘어난다. (c) "End of branch" 흐름을 가리키는 한 줄만 둔다.

### N4. 스펙 게이트 리뷰를 격리 리뷰어로 — ★채택 권고

- 깨지는 것: 스펙 게이트가 존재하는 이유는 "승인된 스펙에도 남는 반전을 독립 리뷰가 잡는다"(`brainstorm.md:29`)인데, 기본 호출은 같은 컨텍스트의 자기 검토다(약점 3). 소유자의 궁극 목적(의도 인식)에 가장 직접 닿는 틈이다.
- 변경: 선택지 (a) ★`brainstorm.md:20` 핸드오프가 `/sc:review --scope spec --structured <path>`를 안내한다. 사용자는 여전히 `--structured` 없이 부를 수 있다. (b) `review.md`에서 `--scope spec`이면 격리 리뷰를 기본으로 한다. 플래그 의미가 바뀌어서 `command-local-flags` 테스트를 다시 봐야 한다. (c) 유지하고 `brainstorm.md:29`의 근거 문장을 "독립"에서 "별도 단계"로 낮춘다.
- 비용: 스펙 리뷰마다 서브에이전트가 한 번 돈다. Large 흐름에서만 발생한다.
- 검증: 격리 리뷰어가 받는 패킷에 `00-intent.md` 원문이 들어가는지 확인한다(`RULES_DELEGATION.md` `<delegate_packet>`). 원문이 빠지면 외부 분석의 우려대로 같은 가정만 받는다.

### N5. "유효한 RED" 한 구절 — 낮은 우선순위

- 깨지는 것: import 오류나 픽스처 누락으로 실패한 테스트를 RED로 치면, 구현 뒤의 GREEN은 아무것도 증명하지 못한다.
- 변경: `plan.md:49` "Step 2: Verify it fails" → "Step 2: Run it and see it fail for the reason it tests (not an import or setup error)". `test.md`의 TDD 패턴에도 같은 구절을 넣는다. 커널과 직접 `/sc:implement`에는 넣지 않는다.
- 근거가 ECC 문헌뿐이고 이 저장소에서 관찰된 사고는 없다. ★N2와 같은 커밋에 묶되, 소유자가 원하지 않으면 뺀다.

### N6. 다단계 흐름 측정 — ★N1·N2와 함께

외부 약점 6에 대한 구체적 답이다. 규칙을 더하는 대신 실패를 재는 프로브를 `evals/tasks.yaml`에 둘 추가한다(AGENTS.md: 행동 실패는 canary 프로브로).

- (i) `implement-proof-fail`: fixture plan의 박스는 모두 처리할 수 있지만 `Proof` 명령은 실패한다. 프롬프트는 `/sc:implement --plan <path>`. 채점은 plan의 `status`가 `complete`가 아니고, 출력에 Proof 실패가 보고되는 것이다. N2 전후로 각각 돌려 효과를 본다.
- (ii) `plan-draft-spec-gate`: `status: draft`인 discovery 스펙을 두고 `/sc:plan --from <spec>`을 부른다. 채점은 plan 파일이 생기지 않고 `/sc:review --scope spec` 안내가 나오는 것이다. README가 "hard-blocks"라고 부르던 게이트를 처음으로 잰다. 결과가 붉으면 그때 훅으로 옮길지 정한다(ADR-0001, `sdlc-playbook-alignment` 개선 8의 방침).
- 실행: sonnet low, arm당 10회, 사전 등록 후. `src/superclaude/core`를 바꾸지 않으므로 canary 릴리스 게이트 대상이 아니다.

### 보류·기각 요약

- 3단계 상태, 수용 기준 표, `reflect` 상태 전이: 기각(§2).
- 결정 모드 분류 규칙 재작성: 보류. 오분류가 감사를 늘리는 쪽이다. 한국어 사례에서 `confirmed`를 놓치는 일이 반복 관찰되면 그때 예시를 추가한다.
- 상태 검사 훅: 보류. N6이 붉게 나올 때만 다시 본다.

## 5. 다음 단계

1. N1·N2(a)·N3(a)·N4(a)·N5·N6을 `feature/completion-proof` 한 브랜치로 묶는다. 커맨드 파일 변경은 `.claude/rules/command-authoring.md`의 테스트를 따르고, 통합 시점에 전체 `uv run pytest`를 돌린다.
2. N6 프로브는 N2 반영 전에 먼저 한 번 돌려 기준선을 남긴다.
3. 커맨드가 바뀌므로 CHANGELOG `[Unreleased]`에 적고 패치 릴리스를 한다. `core/`는 건드리지 않으므로 canary 게이트 대상이 아니다.
4. 외부 두 문서는 이 브랜치에 원문 그대로 두고, 병합할 때 이름 규약에 맞춘다(§3-5).
