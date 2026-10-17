---
feature: reframing-anchoring
phase: intent
owner: ajitta
created: 2026-10-17
updated: 2026-10-17
related: ../prompt-content-audit/, ../over-engineering-audit/, ../../research/persona-anchoring-framing-audit-chosh1179-2026-09-14.md
---

# Reframing · anchoring 축 재구성 (의도 인식)

현행 모델(Sonnet 5.5 / Opus 5.5 / Fable 5.1)이 지시 없이도 잘 하는 것을 걷어내고, 스스로 하지 못하는 것 — 행위 지시 뒤의 궁극 목적 인식, anchoring·context reframing — 을 구조로 만드는 재구성. 계획: `.hermes/plans/2026-10-17_190849-reframing-anchoring-restructure.md` (v3).

## Status

Phase 6 완료: `purpose_before_action`을 `core/RULES.md`에 반영(`123c6a22`), `make canary-gates` 7/7 통과([07-release-gate.md](./07-release-gate.md)). 브랜치 `feature/reframing-anchoring`, 기준 HEAD `7a6f771f`. 세션 172/180 사용(기준선 20 + 판별력 24 + 확장 100 + 파일럿 24 + 게이트 4). 남은 것: 머지·푸시·릴리스(각각 지시 때), Q3 lean 삭제(보류). 6개 콘텐츠 분류·2개 ponytail 보고서 수신 후 핵심 판정 검증; [03-analysis.md](./03-analysis.md)의 정정·보류 판정이 개별 보고서의 심각도·삭제 권고에 우선한다.

R3 첫 줄 검사는 프롬프트의 명시적 yes/no 요구와 충돌하므로 판단 실패의 증거에서 제외했다. I0 개입은 파일럿 1회(규칙 1개, 과제 2개, 모델 2개, 3회)로만 측정했다 — 일반화·Fable·일상 요청에의 부작용은 미측정. 최신 문헌 추가 조사·MCP/출력 스타일 의미 감사 등 잔여 범위가 있으며, 전체 연구·감사가 끝났다는 뜻은 아니다. 대량 삭제·푸시·릴리스는 미실행.

## Documents

- [00-intent.md](./00-intent.md): 요청자의 말로 적은 문제·결과·범위·제약·미결 질문
- [01-baseline.md](./01-baseline.md): 기존 canary 5개 × vanilla/sc-full × sonnet·opus 기준선 (전부 천장) 과 비용 차이
- [02-discriminability.md](./02-discriminability.md): 최초 판별력 측정 (예비 해석; 02a의 정정 우선)
- [02a-measurement.md](./02a-measurement.md): 유지한 120세션 집계, 측정 한계와 해석 정정
- [03-analysis.md](./03-analysis.md): 종합 판정, 직접 재현, 보고서 권고의 채택·보류 기준
- [03a-analysis-core.md](./03a-analysis-core.md): core 분류 원자료
- [03b-analysis-modes-skills.md](./03b-analysis-modes-skills.md): modes·skills 분류 원자료
- [03c-analysis-agents-first.md](./03c-analysis-agents-first.md), [03d-analysis-agents-second.md](./03d-analysis-agents-second.md): agents 분류 원자료
- [03e-analysis-commands-first.md](./03e-analysis-commands-first.md), [03f-analysis-commands-second.md](./03f-analysis-commands-second.md): commands 분류 원자료
- [04-ponytail-audit.md](./04-ponytail-audit.md): 구현 6축 감사·복구 보고서 검증 원자료
- [04a-ponytail-lean-recovered.md](./04a-ponytail-lean-recovered.md): 2026-10-17 00:35 세션 복구본; 04에서 검증, 삭제 승인 아님
- [04b-ponytail-content-structure.md](./04b-ponytail-content-structure.md): 콘텐츠 구조 lean adaptation 원자료
- [05-options.md](./05-options.md): 4개 재구성 대안, 권한 경계, 실험 예산, Q1–Q4 결정 기록
- [06-pilot.md](./06-pilot.md): `purpose_before_action` 커널 규칙 파일럿 (sc-full vs sc-candidate, 24세션): 0/12 → 11/12, 경계 검사, 비용
- [07-release-gate.md](./07-release-gate.md): 커널 변경 후 `make canary-gates` 결과 (7/7 hard gates, sonnet)
