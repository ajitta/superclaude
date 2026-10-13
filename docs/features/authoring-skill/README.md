---
feature: authoring-skill
phase: design
owner: ajitta
created: 2026-10-10
updated: 2026-10-13
---

# `sc-author` 스킬

SuperClaude를 설치한 사용자 프로젝트에서 Claude가 읽는 Markdown 문서(skill, subagent, slash command, output style, CLAUDE.md·AGENTS.md와 `.claude/rules`)를 형식에 맞게 쓰고 고치는 스킬. 사용자가 `/sc-author`로 명시 호출할 때만 동작한다. 본문 형식은 `--md`(기본, Claude Code 공식 권장 구조)와 `--xml`(SuperClaude 컴포넌트 형식) 중 고르고, 결과는 함께 배포하는 `superclaude author-check` 검사기로 확인한다.

계기: SuperClaude 사용자 프로젝트에서 이런 문서를 추가로 만들면 형식 없이 만들어진다(2026-10-10 세션, 사용자 보고). 결정 경위는 [04-design.md](./04-design.md)의 "입력" 절.

## Documents

- [00-intent.md](./00-intent.md) — 문제, 원하는 결과, 영향 범위, 제약, 미결 질문. 설계 뒤에 04-design.md에 인용된 사용자 말로 다시 구성 (2026-10-13)
- [04-design.md](./04-design.md) — 아키텍처 설계: 스킬 구성, 검사기 인터페이스, `skills` 설치 컴포넌트 복원, 검증 방법. 2026-10-10 인터뷰와 `/sc:review` 결과 반영 (draft)
