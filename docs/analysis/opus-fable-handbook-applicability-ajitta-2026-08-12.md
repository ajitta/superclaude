---
status: draft
revised: 2026-08-12
---

# Opus / Fable Agent Handbook — 적용 가능성 및 적용 방안

`docs/codex/opus-fable-agent-handbook/`(커밋 `81b62cc`)을 `src/superclaude` 콘텐츠 프레임워크에 적용할 수 있는지, 적용한다면 무엇을 어떤 순서로 적용할지에 대한 판정.

## 판정 요약

**부분 채택.** 핸드북 6개 문서에서 SuperClaude에 실제로 새로 더할 것은 5건이고, 그중 저비용·즉시 실행 가능한 것은 3건이다. 나머지는 네 부류로 나뉜다 — 이미 있음, 이미 더 강한 근거로 처리됨, 이 저장소 소관이 아님, 채택하면 최근 병합된 작업을 되돌림.

**신뢰도**: 중복·소관 판정은 높음(파일 대조로 직접 확인 가능). 신규 5건의 가치 순서는 중간(측정되지 않음).

결정적 사실 하나가 이 판정을 지배한다. 핸드북이 `[Heuristic]`으로 등급한 모델별 조정 지침을 **Anthropic이 이미 1차 문서로 공개했고, 이 저장소는 그 1차 문서를 근거로 정렬 작업을 이미 완료·병합했다**(`docs/features/opus5-fable5-alignment/`, 커밋 `c75fcd8`…`7cb858a`). 핸드북의 해당 장은 신규 정보가 아니라 더 약한 근거의 재진술이며, 일부는 1차 문서와 방향이 반대다.

---

## 1. 핸드북 사실 주장 재검증 (2026-08-12, 이 세션)

핸드북 README와 §0이 `[Confirmed]`로 등급한 모델 사실을 Anthropic 원문에 대조했다.

| 주장 | 결과 | 근거 |
|---|---|---|
| Opus 5 · 2026-07-24 출시 · `claude-opus-5` · $5/$25 | 일치 | [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5) |
| Opus 5는 exploit 개발에서 Mythos 5에 뒤짐 (취약점 식별은 대등) | 일치 | 동일 문서. 원문: "Mythos 5 and Opus 5 identify vulnerabilities with similar success, Opus 5's score on the development of exploits is far behind" |
| Fable 5 · 2026-06-09 출시 · `claude-fable-5` · $10/$50 | 일치 | [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) |
| Fable 5 = Mythos 5와 동일 기반 모델, 차이는 안전장치 | 일치 | 동일 문서. Mythos 5는 Glasswing 파트너 한정 |
| 고위험 요청 시 Opus 4.8 폴백 | 일치 | [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5). 원문: "the request will instead be sent to Opus 4.8" |
| 2026-06-12 접근 중단 → 07-01 재배포, 원인은 수출통제 | 일치 | 동일 문서. 계기는 Amazon 연구진의 안전장치 우회 시연 |

**사실 층은 통과했다.** 날조된 출처나 과장된 등급은 발견되지 않았다.

### 다만 등급 체계에 반대 방향의 결함이 있다

핸드북 README는 "부재 주장은 검색 도달 범위에 의존하므로 `[Confirmed]` 등급을 받을 수 없다"고 스스로 경고한다. 같은 논리가 반대로도 적용되는데, 핸드북은 그쪽을 놓쳤다.

핸드북은 §11·§13·§17에서 모델별 프롬프트 조정을 일관되게 `[Heuristic]`으로 등급하고 "A/B eval 전에는 배포하지 말라"고 지시한다. 그런데 Anthropic은 이 조정을 1차 문서로 이미 공개했다. 이 세션에서 원문 확인:

> "Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions … remove them" — [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

> "Claude Opus 5 delegates to subagents more readily than prior models." — 동일 문서

핸드북 §11의 "Opus 5: fewer prompt-level verification loops", §13의 2×2 검증 계획은 **이미 답이 공개된 질문에 eval 예산을 쓰라는 지시**가 된다. 등급 오류의 방향만 README의 정정 이력(C1)과 반대일 뿐, 원인은 같다 — 검색 도달 범위를 지식 상태로 착각.

---

## 2. 결정적 맥락: 정렬 작업이 이미 병합됐다

`docs/features/opus5-fable5-alignment/`는 핸드북보다 **먼저** 저장소에 들어왔고 이미 master에 병합됐다.

| 항목 | 정렬 작업 | 핸드북 |
|---|---|---|
| 근거 | Anthropic 1차 프롬프팅 문서 5종 | 대화 세션 재편집 + 엔지니어링 블로그 |
| 검증 | 6인 감사 → 적대적 verifier, 49건 중 43건 생존, 6건 기각 | 자체 정독 + URL 12건 대조 |
| 실측 | canary 10과제 ($2.51), 3개 모델 교차 프로브, master 대조 베이스라인 | 없음 |
| 반증 기록 | CS1의 refusal 위험이 **재현되지 않았음**을 문서에 명시 | 해당 없음 |
| 적용 | 5개 커밋 병합 (`3c03f18`, `7d4c4f2`, `7f32958`, `0ee0e5a`, `313d171`) | 미적용 |

핸드북이 권고하는 항목 중 상당수는 이 작업이 **이미 실행했다**:

- 핸드북 §10 "'think step by step', 'verify three times'는 eval 없으면 제외" → CS3에서 `self-review` 자동 트리거 제거, `commands/agent.md`의 verifier subagent 제거로 실행됨. 근거는 휴리스틱이 아니라 1차 문서.
- 핸드북 §12 "역할 문구만 길게 쓰기 금지" → CS7 트리거 위생으로 실행됨.
- 핸드북 04 §2 "Prompt = policy, Harness = mechanism" → `ARCHITECTURE.md`의 **Enforcement Boundary** 절이 이미 동일 명제를 저장소 아키텍처 원칙으로 선언. "hook 3개 외 전부 model-followed prose"라고 명시.
- 핸드북 03 §12 "제거해도 결과가 같은 문장은 삭제" → `.claude/rules/content-quality.md`의 **deletion test**가 동일 규칙. 이쪽이 더 정교하다(duplication / sediment / no-op 3분류).

핸드북을 지금 적용 소스로 삼으면 **정렬 작업의 근거 등급을 1차 문서에서 세션 휴리스틱으로 강등**시킨다.

---

## 3. 항목별 적용 가능성

### 3.1 이미 있음 — 조치 불필요

| 핸드북 | SuperClaude 대응 |
|---|---|
| 01 §3 최소 고신호 토큰 | `content-quality.md` 4기준, `docs/prompt-guidelines.md` |
| 01 §7 Uncertainty Policy (조사/가정/명시/에스컬레이션) | `RULES_QUALITY.md` R12(가역성 분기) + R13(의도 검증) |
| 01 §8 Success Criteria | R20 (`--loop` 수렴 판정에 연결됨) |
| 01 §9 Evidence: completion claim ≠ 실제 상태 | R15 + `<verification_ladder>` 5단계 (핸드북보다 세분) |
| 01 §5 Priorities | `RULES.md` `<priority_system>`: Safety > Scope > Restraint > Quality > Speed |
| 01 §12 prompt로 보안 강제 금지 | `ARCHITECTURE.md` Enforcement Boundary + `destructive_guard.py` 2티어 |
| 03 §4 Prompt eval / Outcome eval 분리 | `evals/`는 outcome, `tests/unit/test_*_structure.py`는 spec — 이미 분리 |
| 03 §11 Regression 4-arm 비교 | `evals/` vanilla / sc-full / sc-core-lite / sc-command-only |
| 04 §7 Compaction 보존/폐기 | `commands/save.md` `<compaction_strategy>` |
| 04 §8 Checkpoint | `MODE_Task_Management.md` Checkpoint-Disciplined + `/sc:save --checkpoint` |
| 04 §10 Delegate if / Don't delegate if | `RULES_DELEGATION.md` `<sub_agent_decision>` — 핸드북보다 구체적이고 **모델 조건부**(Opus 5 댐핑)까지 반영 |
| 04 §11 병렬 agent는 worktree 분리 | 동일 절의 Worktree-parallel + `EnterWorktree` |
| 05 §8 Approval fatigue | `destructive_guard.py`의 warn 티어(`permissionDecision: "ask"`) |

### 3.2 이 저장소 소관 아님 — 기각

핸드북 04장의 절반과 05장의 절반은 **에이전트 런타임**을 대상으로 쓰였다. SuperClaude는 런타임을 소유하지 않는다 — Claude Code가 소유한다. `ARCHITECTURE.md`가 이미 이 경계를 명문화했다.

기각 대상: Permissions engine(04 §13), Budget/Retry/Idempotency(§14), Observability(§15), Recovery/Cancellation(§16), Reference repository layout(§18), Credential isolation(05 §5), Filesystem/Network 정책(§6), Audit log(§12), Data classification D0–D3(§9).

이것들을 마크다운 규칙으로 옮기면 `ARCHITECTURE.md`가 경고하는 정확한 오류가 된다 — **보장이 필요한 것을 prose로 쓰는 것**. Prompt는 mechanism을 enforce하지 못한다는 핸드북 자신의 명제와도 충돌한다.

### 3.3 채택하면 최근 작업을 되돌림 — 기각

**(a) 모델별 조정 표 (01 §11, 02의 각 "조정" 블록, 03 §13, 04 §17)**

핸드북의 Fable 5 기본값은 `canonical state / evidence-grounded progress / checkpoint / compaction·reset / pause conditions / containment`이다. Anthropic의 Fable 5 문서에 있는 다음 두 항목이 빠져 있다:

> "Use subagents frequently, provide explicit guidance about when delegation is appropriate, and prefer asynchronous communication between orchestrator and subagents over blocking until each subagent returns." — [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)

그리고 방향이 **반대인** 항목이 하나 있다. 핸드북 04 §7은 context reset 트리거로 "모델이 context 길이 때문에 조기 종료"를 든다. Anthropic은 같은 현상을 *예방 대상 증상*으로 기술한다:

> "Avoid surfacing explicit context-budget counts where possible. If the harness must show them, a reassurance helps: `You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work.`"

이 저장소는 **CS2에서 `MODE_Token_Efficiency.md`의 컨텍스트 자가 모니터링 블록을 이미 삭제했다**(`7f32958`). 핸드북 §7을 채택하면 그 커밋을 되돌린다.

**(b) 02장 마스터 템플릿 통째 이식**

02장은 약 700줄의 XML 계약 템플릿이다. Anthropic Fable 5 문서: "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality." 이 저장소는 CS5에서 always-loaded 층을 프루닝했고 CS2에서 모드 하나를 축소했다. 템플릿 이식은 정확히 그 반대 방향이다.

**부분 채택은 별개 문제다.** 아래 3.4의 A2가 02·04장에서 뽑은 조각이다.

**(c) 프롬프트 버전 디렉터리 (03 §14)**

`prompt-name/v1.0.md, v1.1.md, CHANGELOG.md` — git이 이미 한다. 정렬 작업의 커밋 메시지가 정확히 §14가 요구하는 형식(변경/이유/결과/슬라이스)을 담고 있다.

### 3.4 신규 — 채택 후보

핸드북에만 있고 SuperClaude에 동치가 없으며, 병합된 정렬 작업과 충돌하지 않는 항목.

---

## 4. 적용 방안

### Tier 1 — 즉시 (저비용, 충돌 없음)

**A1. Canonical state 불변식 — compaction 시 강도 승격 금지**

핸드북 04 §6:

```text
compaction / handoff / merge 시 절대 바꾸지 않는다:
assumption → fact
planned → completed
attempted → validated
weak evidence → strong evidence
blocked → complete
```

SuperClaude에 동치가 없다. `save.md`의 `<compaction_strategy>`는 *무엇을 남길지*만 규정하고, 남은 것의 **인식론적 강도를 보존하라**는 규정이 없다. `MODE_Task_Management.md`의 Checkpoint-Disciplined도 마찬가지.

이것은 R15(증거 없이 완료 주장 금지)의 **시간축 확장**이다 — R15는 한 턴 안의 주장을 다루고, 이 불변식은 요약을 거치며 주장이 승격되는 것을 막는다. Anthropic이 명시적으로 유지를 권고한 anti-fabrication 계열이므로 정렬 작업과 충돌하지 않는다.

- 위치: `commands/save.md` `<compaction_strategy>`에 1줄 추가.
- 문구 초안: `Preserve claim strength: an assumption stays an assumption, planned work stays planned, an attempted check stays attempted. Compaction shortens the record; it never upgrades it.`
- 비용: 1줄, on-demand 층(always-loaded 아님).
- 검증: `evals/tasks.yaml`에 프로브 추가 — 미검증 가정을 남긴 채 체크포인트를 쓰게 하고, 출력에서 해당 항목이 확정 사실로 승격됐는지 `output_not_regex`로 확인.

**A2. Subagent 반환 스키마**

`RULES_DELEGATION.md`는 IN 방향 7필드(Delegate packet)를 규정하지만, OUT 방향은 "advisory summary — revalidate cited file:line"뿐이다. 반환 **형태**에 대한 규정이 없다.

핸드북 04 §10의 6필드:

```text
1. Conclusion  2. Evidence  3. Counterevidence
4. Confidence  5. Unknowns  6. Parent-task implication
```

이 중 Conclusion/Evidence/Confidence는 `<finding_policy>`(severity + confidence)가 이미 부분 커버한다. **새로 더해지는 것은 Counterevidence와 Unknowns**이고, 이 둘은 main loop가 부분 증거 위에서 종합하는 것을 막는다 — `RULES_DELEGATION.md`가 이미 "silent filtering makes the main loop synthesize from a silently-incomplete set, an R15 risk"라고 지적한 실패 모드와 같은 계열이다.

- 위치: `RULES_DELEGATION.md` `<sub_agent_decision>`의 "Sub-agent summary (OUT) advisory" 문장 뒤.
- 비용: 1문장. `opts.schema`를 쓸 때 JSON Schema로 그대로 옮겨진다.
- 주의: 6필드를 전부 강제하면 단일 grep 위임에도 ceremony가 붙는다. "탐색·감사 위임에 한해"로 범위를 좁힐 것.

**A3. eval 슬라이스 확장 — 4종 추가**

가장 확실한 이득. 현재 `evals/tasks.yaml`은 7과제 + 3프로브, 태그 7종(`success` `scope` `verification` `location` `gotcha_compliance` `citation` `safety`). 핸드북 03 §6이 나열한 슬라이스 중 **없는 것**:

| 슬라이스 | 왜 필요한가 | 기존 체크 타입으로 구현 가능한가 |
|---|---|---|
| `escalation_required` | R12의 ask-first 4분류가 실제로 발동하는지 측정된 적 없음 | `output_regex`로 질문/확인 문구 |
| `impossible_or_conflicting` | 모순된 hard constraint를 준 뒤 어느 쪽을 조용히 버리는지 | `output_regex` + `git_diff_max_files` |
| `misleading_evidence` | 오래된 주석·잘못된 README가 코드와 충돌할 때 무엇을 신뢰하는지. `PRINCIPLES.md`의 "Code reality > documentation"를 실측 | `cmd_ok` + `transcript_regex` |
| `poisoned_readme` (injection) | `security-engineer.md`의 gotcha가 **이 저장소의 실제 위협모델을 "prompt-injection thru XML/markdown content"로 지목**했는데, 그에 대한 eval이 없음 | `transcript_not_regex` |

네 종 모두 `run_eval.py`의 기존 11개 체크 타입으로 구현된다 — 하네스 수정 불필요. `destructive-elicitation` 과제가 이미 `destructive_scope` 슬라이스이므로 패턴이 검증돼 있다.

- 비용: fixture 4개 + tasks.yaml 항목 4개. 실행 비용은 canary 기준 과제당 약 $0.25.
- 우선순위: `poisoned_readme` → `escalation_required` → 나머지 2종.

### Tier 2 — 조건부 (관측된 실패가 생기면)

**B1. Hard gate / soft metric 분리와 릴리스 게이트 (핸드북 03 §7, §11)**

현재 `run_eval.py`는 태그별 pass rate만 낸다. 게이트/소프트 구분이 없다. 실제로 이 공백이 드러난 사례가 있다 — 정렬 작업의 "no confirmed regression" 판정은 worktree로 master 베이스라인을 **수동 비교**해서 내렸다. 게이트를 명문화하면 그 절차가 재현 가능해진다.

핸드북 §11의 릴리스 게이트 형태:

```text
Critical success >= baseline
Constraint violation <= baseline
Security-sensitive slice does not regress
```

`safety` 태그를 hard gate로, `scope`/`citation`을 soft로 나누는 것부터 시작.

- 조건: A3의 슬라이스가 먼저 들어가야 게이트에 의미가 생긴다. A3 → B1 순서.

**B2. Prompt Critic 스코어카드 (핸드북 03 §2, §3)**

`content-quality.md`에 7문 감사 체크리스트는 있지만 점수와 게이트가 없다. 10차원 0–4 스코어카드 + critical gate는 저작 리뷰를 결정 가능하게 만든다.

- 조건: **지금은 넣지 말 것.** `content-quality.md`의 개선 워크플로 1번 항목이 "실제 실패를 관측하기 전에는 개선하지 말 것"이다. 저작 리뷰가 실제로 놓친 사례가 기록되기 전에 스코어카드를 도입하면 자기 규칙 위반이다.

**B3. `/sc:implement`의 `<definition_of_done>` / `<final_response>` (핸드북 02 §3)**

`implement.md`의 flow 7단계에는 완료 판정 블록이 없다. R15/R20이 커버하지만 커맨드 수준에는 없다.

- 조건: `probe-verify-claim` 프로브가 `verification` 태그에서 실패한 이력이 있다(`bugfix-scope-creep`이 master/branch 양쪽 0/1). 이 실패의 원인이 커맨드 수준 DoD 부재인지 먼저 분리해야 한다. 원인 규명 전 추가는 추측 기반 수정.

### Tier 3 — 핸드북 자체에 대한 조치

**C1. `docs/codex/opus-fable-agent-handbook/README.md`에 우선순위 포인터 추가**

지금 상태로 두면 다음 독자(또는 다음 세션의 에이전트)가 §13의 2×2 A/B를 실행할 위험이 있다 — 이미 1차 문서에 답이 있는 질문이다.

- 추가 문구 초안: 모델별 조정(§11, §13, §17)은 이 저장소에서 `[Heuristic]`이 아니라 **1차 자료 기반으로 해소됨**. 권위 있는 출처는 `docs/features/opus5-fable5-alignment/02-research.md`이며, 그 문서가 인용한 `platform.claude.com`의 Opus 5 / Fable 5 프롬프팅 가이드가 원전. 이 핸드북의 해당 절은 배경 자료로만 읽을 것.
- 비용: README 표 아래 3줄.

**C2. 핸드북을 SuperClaude 규칙 소스로 승격하지 말 것**

핸드북의 가치는 **한국어 개념 참고서**와 **체크리스트**다(01 §13, 04 §19, 05 §16의 치트시트). 그 용도로는 유용하다. `src/superclaude/`에 문장을 옮기는 소스로는 근거 등급이 한 단계 낮다.

---

## 5. 반대 논거

**"정렬 작업은 Anthropic 지침만 봤고, 핸드북은 시스템 설계를 본다. 층이 다르므로 중복이 아니다."**

부분적으로 맞다. 핸드북 04장의 canonical state, task admission, 실패 분류 같은 항목은 프롬프팅 지침에 없는 시스템 층이다. 그래서 A1·A2·A3가 살아남았다.

이 논거가 뒤집지 못하는 지점: 그 시스템 층의 대부분은 **런타임 소관**이고(3.2), 콘텐츠 프레임워크에 남는 부분은 이미 `RULES_DELEGATION.md`·`ARCHITECTURE.md`·`save.md`가 덮고 있다(3.1). 남은 잔여가 5건이라는 것이 이 판정의 결론이지, "핸드북에 배울 게 없다"가 아니다.

**"Task admission / risk tier(R0–R3)는 왜 Tier 1이 아닌가?"**

R0–R3은 흩어진 세 가지를 통합하는 어휘다 — `destructive_guard`의 2티어, agent별 `Proceed / Ask First / Never`, `RULES_QUALITY.md`의 ">3 units of impact" 임계값. 이득은 일관성뿐이고, 어휘를 도입하려면 always-loaded 층을 건드려야 한다. CS5가 방금 그 층을 프루닝했다. **관측된 혼동 사례가 없는 어휘 추가는 `content-quality.md`의 deletion test를 통과하지 못한다.**

이 판단을 뒤집는 것: agent 간 권한 경계 판정이 실제로 엇갈린 사례가 기록되면. 그때는 R0–R3이 Tier 1이 된다.

## 6. 무엇이 이 권고를 뒤집는가

| 관측 | 뒤집히는 항목 |
|---|---|
| Anthropic이 Opus 5 / Fable 5 프롬프팅 문서를 철회하거나 내용을 반전시킴 | 3.3(a) 기각 → 핸드북 §13의 2×2 A/B가 다시 유효해짐 |
| `evals/`에 A3 슬라이스를 넣었더니 `escalation_required`가 sc-full 대비 vanilla와 차이 없음 | R12/R13 자체가 무효 — 규칙 삭제 후보가 되고, 핸드북의 Authority 블록이 대안 후보로 승격 |
| agent 권한 경계 판정 엇갈림이 기록됨 | Task admission R0–R3이 Tier 2 → Tier 1 |
| Fable 5를 장기 실행 하네스에서 실제로 쓰기 시작 | 핸드북 04 §6 canonical state 전체(1줄 불변식이 아니라)가 재검토 대상 |

## 7. 실행 순서

```text
1. C1  핸드북 README 포인터           (5분,  충돌 없음)
2. A1  compaction 강도 보존 1줄        (10분, save.md)
3. A2  subagent 반환 스키마 1문장      (10분, RULES_DELEGATION.md)
4. A3  eval 슬라이스 4종               (반나절 + 약 $1 실행)
5. B1  hard gate / release gate        (A3 완료 후)
```

1–3은 마크다운 전용 변경이라 테스트 위험이 없다(`CLAUDE.md`: "Markdown-only changes carry no test risk"). 4는 `--dry-run`으로 먼저 검증한 뒤 2개 arm으로 좁혀 실행할 것 — 전체 4×7 매트릭스는 28세션이다.

---

## 출처

이 세션에서 원문 대조한 것:

- [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)
- [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5)
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)

저장소 내부 근거: `src/superclaude/ARCHITECTURE.md`, `core/RULES.md`, `core/rules/RULES_QUALITY.md`, `core/rules/RULES_DELEGATION.md`, `commands/save.md`, `commands/implement.md`, `agents/security-engineer.md`, `agents/self-review.md`, `.claude/rules/content-quality.md`, `.claude/rules/agent-authoring.md`, `evals/README.md`, `evals/tasks.yaml`, `evals/run_eval.py`, `docs/features/opus5-fable5-alignment/{README,02-research,03-analysis}.md`, `docs/prompt-guidelines.md`.
