---
feature: rule-citation-consistency
phase: implementing
owner: ajitta
created: 2026-10-14
updated: 2026-10-14
---

# 규칙 번호 인용 일관화와 중복 정리

배포 콘텐츠(`src/superclaude/`)가 규칙 번호(R01~R21)를 7가지 형식으로 인용한다. 이를 `[RNN Name]` 하나로 맞추고, 테스트가 그 형식만 허용하게 한다. 아울러 `core/RULES.md` 커널과 `core/rules/RULES_QUALITY.md`에 같은 규칙 5개가 두 벌로 실리는 중복을 줄인다.

## Documents

- [05-plan.md](./05-plan.md): 측정 근거, 결정, 범위 밖, Phase 0~2 작업과 검증 명령, 채택하지 않은 대안
