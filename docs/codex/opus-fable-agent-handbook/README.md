# Opus / Fable Prompt & Agent Engineering Handbook

참조 대화 **“프롬프팅 트렌드 설명”**을 시간순으로 잘라 붙이지 않고, 주제별로 재편집한 Markdown 핸드북입니다.

중복된 설명은 제거하고, 후속 정정과 최신 공개 자료를 우선했습니다. 공식 사실, 이 세션에서 만든 설계 체계, 검증이 필요한 경험적 가설을 다음과 같이 구분합니다.

```text
[Confirmed]
공식 공개 자료로 직접 확인된 내용

[Framework]
공식 원칙을 production engineering 관점으로 재구성한 체계

[Heuristic]
실제 workload의 eval로 검증해야 하는 가설
```

## 모델 명칭 (2026-08-12 검증 기준)

> **정정 이력**: 이 문서의 이전 판은 “Claude Opus 5는 공개 자료에서 확인되지 않음”이라고 기술했습니다.
> **이는 오류였습니다.** Claude Opus 5는 2026-07-24에 정식 출시됐습니다. 2026-08-12 검증에서
> 공식 발표 페이지와 플랫폼 문서로 확인해 아래와 같이 수정했습니다.
> 원인은 검증 시점의 검색 실패였고, “검색되지 않음”을 “존재하지 않음”으로 승격시킨 것이 판정 오류입니다.
> 부재 주장(negative claim)은 검색 도달 범위에 의존하므로 `[Confirmed]` 등급을 받을 수 없습니다.

**[Confirmed]** 공식 발표 및 플랫폼 문서로 확인된 현행 모델:

| 모델 | 모델 ID | 출시 | 가격(input/output per MTok) | 위치 |
|---|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | 2026-06-09 | $10 / $50 | 최상위. Mythos 5와 동일 모델, 차이는 안전장치 |
| Claude Opus 5 | `claude-opus-5` | 2026-07-24 | $5 / $25 | Fable 5에 근접하되 절반 가격. 에이전틱 코딩·엔터프라이즈 중심 |
| Claude Sonnet 5 | `claude-sonnet-5` | — | $2 / $10 | 속도·지능 균형 |
| Claude Opus 4.8 | `claude-opus-4-8` | 2026-05-28 | — | 레거시. 마이그레이션 비교용 |

**[Confirmed]** 운영상 반드시 알아야 할 사실:

- Fable 5와 Mythos 5는 **동일 모델**이며 차이는 안전장치뿐입니다. Fable 5는 고위험 사이버·생물·화학
  요청에서 분류기가 발동하면 **Opus 4.8로 폴백**합니다. 보안 eval 결과가 어느 모델의 것인지 기록하세요.
- Fable 5는 2026-06-12 수출통제로 **전 사용자 접근이 중단**됐다가, 통제 해제 후 전용 분류기를 추가해
  2026-07-01 재배포됐습니다. 기반 모델 가용성은 규제로 사라질 수 있습니다.

이 문서에서 모델 이름을 다루는 방식:

- 모델의 **존재와 사양**은 `[Confirmed]` — 위 표가 근거입니다.
- 모델별 **프롬프트 조정 가설**(“Opus는 verification ceremony를 줄인다” 등)은 여전히 `[Heuristic]`입니다.
  존재 확인은 조정 효과 확인이 아닙니다.
- 배포 전 동일 workload에서 generic prompt와 model-adapted prompt를 A/B 평가하세요.

공식 확인 링크:

- [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)
- [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5)
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)
- [Claude 모델 개요 (플랫폼 문서)](https://platform.claude.com/docs/en/about-claude/models/overview)

---

## 이 저장소에서의 우선순위

**모델별 조정(01 §11, 02의 각 "조정" 블록, 03 §13, 04 §17)은 이 저장소에서 `[Heuristic]`이 아닙니다.**
Anthropic이 Opus 5 / Fable 5 프롬프팅 가이드를 1차 문서로 공개했고, 이 저장소는 그것을 근거로 정렬
작업을 이미 완료·병합했습니다(`c75fcd8`…`7cb858a`). 권위 순서는 다음과 같습니다.

1. [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) ·
   [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) — 원전
2. `docs/features/opus5-fable5-alignment/02-research.md` — 원전에서 도출한 저장소 적용 지침(G1–G14)
3. 이 핸드북 — 배경 개념 참고서

두 가지는 그대로 채택하면 손해입니다.

- **§13의 2×2 A/B 평가 계획을 실행하지 마세요.** 이미 1차 자료에 답이 있는 질문에 eval 예산을 씁니다.
- **04 §7의 context reset 트리거 중 "모델이 context 길이 때문에 조기 종료"**는 Anthropic이 *예방 대상
  증상*(context anxiety)으로 기술한 것입니다. 이 저장소는 해당 자가 모니터링 지시를 `7f32958`에서 이미
  삭제했으므로, 채택하면 되돌립니다.

적용 가능성 판정 전문: `docs/analysis/opus-fable-handbook-applicability-ajitta-2026-08-12.md`

## 파일 구성

| 파일 | 내용 | 주 용도 |
|---|---|---|
| [00_raw_session.md](00_raw_session.md) | 사용자·어시스턴트 발화의 시간순 보존본 | 원 대화와 수정 흐름 확인 |
| [01_frontier_prompting_principles.md](01_frontier_prompting_principles.md) | Intent, Objective, Context, Constraints, Authority, Uncertainty, Success | 핵심 이론 |
| [02_production_master_prompts.md](02_production_master_prompts.md) | Decision / Research / Coding / Long-running 복사용 템플릿 | 바로 업무에 사용 |
| [03_prompt_architect_and_evals.md](03_prompt_architect_and_evals.md) | Meta-Prompt, Critic, Scorecard, Golden Tasks, Regression, Ablation | 프롬프트 생성·검증 |
| [04_agent_runtime_architecture.md](04_agent_runtime_architecture.md) | Context, Canonical State, Compaction, Multi-Agent, Harness, Permissions | agent 시스템 설계 |
| [05_security_and_handbook.md](05_security_and_handbook.md) | Trust boundary, injection, credentials, containment, security eval, 치트시트 | 보안·운영 참고서 |

## 추천 읽기 순서

### 처음부터 이해하기

```text
01 → 02 → 03 → 04 → 05
```

### 바로 프롬프트 쓰기

```text
02 → 05의 Cheat Sheet
```

### Prompt Architect 구축

```text
01 → 03 → 02
```

### 장기 agent 시스템 구축

```text
01 → 03 → 04 → 05
```

### 보안 검토

```text
05 → 04의 Permissions / Tool / Recovery
```

### 원 대화의 발전 과정 확인

```text
00 → 관심 주제의 편집본
```

---

## 핵심 요약

```text
Intent
→ Objective
→ Context
→ Constraints
→ Authority
→ Success Criteria
```

복잡하고 agentic한 작업:

```text
+ Priorities
+ Uncertainty
+ Evidence
+ Escalation
+ Runtime State
+ Permissions
+ Evaluation
```

전체 품질:

```text
Agent Quality
=
Model
+ Task Specification
+ Context
+ Tools
+ Harness
+ Security
+ Evaluation
```

## 편집 원칙

이 문서 세트는 다음 기준으로 만들었습니다.

1. 시간순 분할 대신 주제별 재구성
2. 반복된 개념은 가장 완성된 한 버전으로 통합
3. 초기 주장과 후속 정정이 충돌하면 후속 검증 우선
4. 새 공식 확인과 충돌하면 새 확인 우선
5. `Agent Contract`, `Canonical State`, `Evidence Ledger` 같은 자체 명칭은 `[Framework]`
6. 모델별 조정은 workload eval 전에는 `[Heuristic]`
7. Markdown code block과 복사용 템플릿 보존
8. 원문 흐름은 `00_raw_session.md`에 별도 보존

## 원본 보존본의 한계

참조 대화를 읽는 연결기는 메시지 하나당 최대 20,000자를 제공합니다.

**2026-08-12 실측**: `00_raw_session.md`의 어시스턴트 답변 20건 중 **5건이 20,000자 상한에서 잘렸습니다**
(각각 20,019–20,020자에서 종료). 사용자 발화 없이 어시스턴트 블록이 3개 연속되는 지점이 있어
**사용자 턴 1건도 누락**된 것으로 보입니다. 해당 구간의 원문은 복구 불가입니다.

또한 이 파일에는 내보내기 과정에서 링크가 유실된 인용 마커 99건이 남아 있어 근거를 추적할 수 없습니다.
확인된 출처는 편집본 `01`–`05`의 것만 사용하세요.

편집본은 전체 대화의 주제 흐름과 접근 가능한 템플릿을 통합해 이 공백을 보완합니다.

## 운영 권고

- 템플릿을 그대로 모두 쓰지 말고 불필요한 블록을 삭제합니다.
- hard constraint를 추측으로 발명하지 않습니다.
- 중요한 보안 제한은 prompt가 아니라 runtime에서 enforce합니다.
- completion claim을 테스트·실제 상태와 대조합니다.
- 모델별 prompt 차이는 이름이나 인상으로 배포하지 않고 golden workload로 검증합니다.
- 프롬프트의 각 문장을 성능 개선 가설로 취급하고 ablation으로 정리합니다.

## 주요 공식 참고 자료

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude)
- [An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)
- [How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)
- [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)
- [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)

## 검증 이력

**2026-08-12 검증** — 전문 정독 + 인용 URL 12건 원문 대조 + 웹 검색 교차확인 + 파일 정량 분석.

통과:

- 인용 URL 12건 중 11건이 실재하고 내용도 일치. 날조된 출처 0건.
- `[Confirmed]` 방법론 주장 8건 전부 원문과 일치.
- `[Confirmed]` / `[Framework]` / `[Heuristic]` 3분류가 일관되게 적용됨. 자체 설계 체계를 공식 원칙으로
  위장한 사례 없음.

수정한 것:

| ID | 내용 | 반영 위치 |
|---|---|---|
| C1 | “Opus 5 미확인” 판정 오류 → 2026-07-24 출시로 정정 | README, 01, 02, 03, 04, 05 |
| C2 | “현행 Opus = 4.8” 기준 → `claude-opus-5`로 교체 | 01 §0, 03 §13, 05 §15 |
| C3 | Fable 5의 가격·폴백·가용성 중단 이력 추가 | README, 01 §0, 04 §17, 05 §15 |
| D1 | 깨진 인용 링크(블로그 인덱스) → 정확한 permalink | 03 §4 |
| D2 | 원본 보존본의 추적 불가 인용 99건 고지 | 00 머리말 |
| D3 | 잘림 고지를 실측값으로 확정 (답변 20건 중 5건) | 00 머리말, README |
| D4 | README 출처 목록 7건 → 12건 | README |

## 저장 위치

요청한 기본 저장 폴더:

```text
/Users/chosh/repos/ajitta/superclaude/docs/codex/opus-fable-agent-handbook
```

