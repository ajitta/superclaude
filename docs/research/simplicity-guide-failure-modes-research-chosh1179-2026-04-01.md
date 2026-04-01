# Simplicity-Guide Failure Modes Research

**Date:** 2026-04-01  
**Author:** chosh1179  
**Purpose:** Research findings on simplicity-guide agent failure modes and improvement strategies  
**Sources:** Web research (Tavily), sequential analysis, verbalized sampling (k=5)

---

## 1. Problem Statement

simplicity-guide 에이전트가 3가지 실패 모드를 보임:
- **FM1**: 너무 단정적으로 판단 (overconfident assertions)
- **FM2**: 코드의 목적/제약을 오해 (context misunderstanding)
- **FM3**: 최신 best practice를 모름 (stale knowledge)

근본 원인: "complexity immune system"으로 설계된 에이전트가 도메인 지식 없이 일괄적으로 단순화를 추진 → autoimmune disease 패턴.

---

## 2. Research: AI Agent Epistemic Humility (2025-2026)

### 2.1 Uncertainty-Marker Taxonomy
- "Virtually Certain / Highly Confident / Moderately Confident / Speculative / Unknown" (Calibrated Confidence Prompting)
- "Architecting Trust in Epistemic AI Agents" (arXiv, Mar 2026): AI가 "established fact, logical inference, subjective opinion, speculation"을 구분해야 함
- 프롬프트 수준 적용: "If you are unsure, say so and explain what additional context would resolve the uncertainty"

### 2.2 Self-Calibration 한계
- Verbalized confidence는 체계적으로 과대평가됨 — GPT-4o 49.7% 정확도에서 39.3% 보정 오차 (Spivack, 2025)
- 완화 패턴: (a) 신뢰도의 **근거** 요구 (b) "무엇이 답을 바꿀 수 있는가" 명시 (c) multi-agent deliberation
- SCOPE framework (arXiv, Dec 2025): confidence threshold를 프롬프트에 내장 가능 (전략적 결정 0.85, 자동 수락 0.5)

### 2.3 Code Review False Positive 감소
- 2026 합의: repository-wide context 필수 — 파일 수준 분석은 noise 생성
- 프롬프트 패턴: (a) 플래그된 패턴이 프로젝트 컨벤션인지 확인 (b) **왜** 문제인지 설명 요구 (c) 변경 코드 경로만 대상
- Source: Cubic.dev, CodeAnt AI (2026)

### 2.4 Domain Uncertainty Handling
- AI Agent Index (arXiv, Feb 2026): "Not available" / "Not applicable" / "UNSURE" / "TODO" 표준화
- **ask-before-assuming 패턴**: 관찰 → 불확실한 점 명시 → 확인 요청 → 행동
- "Architecting Uncertainty" (2025): 불확실성을 결함이 아닌 "first-class architectural element"로 취급

### Sources
| Source | Date | Credibility |
|--------|------|-------------|
| Architecting Trust in AI Epistemic Agents (arXiv) | Mar 2026 | 4/5 |
| Agentic Confidence Calibration (arXiv) | Jan 2026 | 4/5 |
| Why AI Systems Can't Catch Their Own Mistakes (Spivack) | 2025 | 3/5 |
| SCOPE: Prompt Evolution (arXiv) | Dec 2025 | 4/5 |
| AI Agent Index (arXiv) | Feb 2026 | 4/5 |

---

## 3. Research: YAGNI/Simplicity-First Pitfalls

### 3.1 YAGNI가 역효과를 내는 경우
- **Cross-cutting concerns** 사후 적용 비용이 높음: i18n, timezone, structured logging, audit trails, CI pipelines
- Southwest Airlines 승무원 스케줄링 붕괴 (~$1B 피해) — 단순화 지름길의 누적이 catastrophic brittleness 초래
- **패턴: YAGNI는 features에 적용, infrastructure/invariants에는 부적합**

### 3.2 Orient-Step-Learn 비판
- Dave Thomas의 *Simplicity* 책 (Pragmatic Bookshelf, June 2025)이 OSL을 공식화
- 직접적 비판은 문헌에 없음 (책이 2025년 6월 출간으로 너무 최근)
- HN 토론: "simplest thing possible vs. simplest thing that could possibly work" — 후자가 규모/보안/운영 우려를 편리하게 무시하는 수단이 될 수 있음
- **핵심: 도메인 인식 없는 OSL = 필수 복잡성을 미루는 변명**

### 3.3 "Remove > Add" 실패 도메인
| Domain | Why Complexity is Essential |
|--------|---------------------------|
| Security | OWASP Top 10 2025 (A09): 포괄적 로깅, 감사 추적, 알림 인프라를 **처음부터** 요구 |
| Accessibility/Compliance | a11y/GDPR 사후 적용 비용 5-10배 — 비협상 제약조건 |
| Data Modeling | 파생값(a+b) 저장 vs 원본(a, b) 보존 — 단순화 = 미래 유연성 파괴 |
| Distributed Systems | 합의, 재시도, 회로 차단기 = 안정성의 대가 |
| Infrastructure | i18n, logging, CI — 사후 적용이 초기 구축보다 비쌈 |

### 3.4 복잡성이 정당한 경우 (2025-2026 합의)
- Fred Brooks의 essential/accidental complexity 구분이 여전히 지배적 프레임워크
- **Tesler's Law (Conservation of Complexity)**: 본질적 복잡성은 제거 불가, 이동만 가능
- 판별 테스트: "이것을 단순화하면 무엇을 잃는가?" → 정확성, 안전, 감사 가능성이면 복잡성 유지
- 복잡성 정당화 조건: **domain guarantees, team boundaries, performance characteristics** 보존

### Sources
| Source | Date | Credibility |
|--------|------|-------------|
| SEI/CMU - Technical Debt Stories | 2023 | 5/5 |
| OWASP Top 10 2025 A09 | 2025 | 5/5 |
| r/programming - YAGNI exceptions | May 2025 | 2/5 |
| Dave Thomas - Simplicity book | Jun 2025 | 4/5 |
| Accidental vs Essential Complexity (Duncan) | May 2025 | 3/5 |

---

## 4. Verbalized Sampling: 5 Improvement Perspectives

| # | Perspective | p | Description |
|---|-----------|---|-------------|
| P1 | Epistemic Humility Embedding | 0.30 | Understanding Gate + confidence levels in actions flow |
| P2 | Verification Gate (MCP-enhanced) | 0.25 | Context7/Serena mandatory verification before claims |
| P3 | Domain Exception Architecture | 0.20 | Explicit protected domains where complexity is justified |
| P4 | Self-Calibration Loop | 0.15 | Meta-cognitive re-evaluation of own recommendations |
| P5 | Conditional Language Rewrite | 0.10 | Absolute statements → conditional with escape hatches |

**Selection**: P1 + P2(light) + P3 + P5 implemented. P4 skipped (redundant with P1's Understanding Gate).

---

## 5. Implementation Summary

Changes applied to `simplicity-guide.md` and `simplicity-coach/SKILL.md`:

| Defense Layer | Mechanism | Failure Mode |
|--------------|---------|----------|
| `<actions>` #2 Understanding Gate | Restate purpose before judging | FM1, FM2 |
| `<actions>` #3 Confidence levels | High/Medium/Low + basis | FM1 |
| `<anti_patterns>` conditionalized | "≠" → "→ check first" | FM1 |
| `<domain_exceptions>` | 6 protected domains + Tesler's Law | FM2 |
| `<tool_guidance>` Verify Before Judging | Context7/Serena verification | FM3 |
| `<gotchas>` 4 patterns | false-positive, overconfident, context-blind, stale | FM1+FM2+FM3 |
| `<examples>` 6 entries | New behavior demonstrations | All |
| `<checklist>` +1 item | Understanding Gate completion | FM2 |
| Skill sync | Understand + domain_exceptions + gotchas | Skill path |

---

## 6. Key Insights

1. **Immune system 비유의 한계**: "complexity immune system"은 좋은 설계 의도지만, autoimmune disease(건강한 세포 공격)로 전락할 수 있음. 해결: 면역 체계에 "self/non-self" 인식 추가 = domain_exceptions.

2. **원칙과 예외의 구조**: "Remove > Add"는 default heuristic으로 유지, domain_exceptions는 named exceptions. 모순이 아닌 계층 구조.

3. **Verbalized confidence의 과대평가**: 프롬프트 수준에서 신뢰도 숫자보다 **근거 요구**가 더 효과적 (Spivack 2025).

4. **YAGNI의 적용 범위**: features에는 적용, infrastructure/invariants에는 부적합. 이 구분이 simplicity-guide에 없었던 것이 핵심 문제.

5. **아이러니 경고**: simplicity-guide 자체를 over-engineer하면 안 됨. 변경은 2파일, +47 -14 lines로 최소화.

---

## 7. Open Questions

- Verbalized confidence가 프롬프트 수준 지시만으로 실제로 보정되는지는 controlled study 부재 (fine-tuning 대비)
- "UNSURE" 신호를 너무 많이 보내면 사용자 신뢰 저하 — 적정 빈도 미연구
- OSL 직접 비판 부재 (책이 2025년 6월 출간으로 최근) — 6개월 후 재조사 권장
