---
feature: authoring-skill
phase: complete
owner: ajitta
created: 2026-10-10
updated: 2026-10-14
---

# `sc-author` 스킬

SuperClaude를 설치한 사용자 프로젝트에서 Claude가 지시·컨텍스트로 읽는 문서(skill, subagent, slash command, output style, CLAUDE.md·AGENTS.md와 `.claude/rules` 등)를 형식에 맞추고 no-op 문장을 걷어내는 스킬. 사용자가 `/sc-author`로 명시 호출할 때만 동작한다. 본문 형식은 `--md`(기본, Claude Code 공식 권장 구조)와 `--xml`(SuperClaude 컴포넌트 형식) 중 고르고, 결과는 함께 배포하는 `superclaude author-check` 검사기로 확인한다.

계기: SuperClaude 사용자 프로젝트에서 이런 문서를 추가로 만들면 형식 없이 만들어진다(2026-10-10 세션, 사용자 보고). 결정 경위는 [04-design.md](./04-design.md)의 "입력" 절.

## Documents

- [00-intent.md](./00-intent.md) — 문제, 원하는 결과, 영향 범위, 제약, 미결 질문. 설계 뒤에 04-design.md에 인용된 사용자 말로 다시 구성 (2026-10-13)
- [03-analysis.md](./03-analysis.md) — no-op 판정 기준: 이 저장소 문서 표본(rules, CLAUDE.md·AGENTS.md·core, agent, auto memory)에서 뽑은 분류, 로드 집합, 기계 판정과 판단 판정, 남길 것, 해로움 검사 (draft)
- [04-design.md](./04-design.md) — 아키텍처 설계: 스킬 구성, 검사기 인터페이스, `skills` 설치 컴포넌트 복원, 검증 방법. 2026-10-10 인터뷰와 `/sc:review` 결과 반영, 2026-10-13 예시 개수(D11)·최신 모델 가이드(D12), 공통 pass·load-set·검사기 N 규칙(D14–D17) 추가 (draft)
  - [04a-design-checker.md](./04a-design-checker.md) — C4 검사기 `superclaude author-check`: 인터페이스와 규칙 F1–F7, R1–R3, S1–S2, X1·X2·X7, N1–N4. 크기 때문에 나눔 (draft)
  - [04b-design-common-pass.md](./04b-design-common-pass.md) — 공통 pass(재형식화 + no-op 제거), load-set, 기계 판정과 `quality.md` 판단 항목의 경계 (D14–D17). 크기 때문에 나눔 (draft)
- [05-plan.md](./05-plan.md) — 구현 plan 색인: 공통 규칙, §9 미결 해소(PowerShell 허용 규칙, Fable 5.1 가이드 URL), phase 순서, 위험, 택하지 않은 안, 완료 증명, release note (draft)
  - [05a-plan-checker-core.md](./05a-plan-checker-core.md) — Phase A: `fields.yaml`, `author-check` 인터페이스·추론·F/R/S/X, XML 회귀 말뭉치
  - [05b-plan-checker-noop.md](./05b-plan-checker-noop.md) — Phase B: `--with`, N1–N4, N 규칙 말뭉치
  - [05c-plan-skills-component.md](./05c-plan-skills-component.md) — Phase C: `skills` 디렉터리 컴포넌트 (install, uninstall, git-exclude, verify-drift, inventory)
  - [05d-plan-references.md](./05d-plan-references.md) — Phase D: 유형 참고 5개, `format-xml.md`, `quality.md`, 최신성·예시 개수 테스트
  - [05e-plan-skill-body.md](./05e-plan-skill-body.md) — Phase E: `SKILL.md`, 구조 테스트, 자기 검사
  - [05f-plan-repo-docs.md](./05f-plan-repo-docs.md) — Phase F: C6 저장소 쪽 변경과 README
  - [05g-plan-probes.md](./05g-plan-probes.md) — Phase G: `evals` 효과·명시 호출 프로브와 실행 기록
