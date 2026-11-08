---
feature: portable-skills-single-plugin
phase: complete
owner: ajitta
created: 2026-10-07
updated: 2026-10-08
related: ../socratic-brainstorm-skill/
---

# portable-skills 단일 플러그인

**4.34.4(2026-11-08)에서 제거됨.** 소유자가 더 이상 쓰지 않아 `socratic` 플러그인과 `portable-skills/` 전체를 저장소에서 지웠다. 마지막 버전은 태그 [v4.34.3](https://github.com/ajitta/superclaude/tree/v4.34.3/portable-skills)에 있다. `.claude-plugin/marketplace.json`은 빈 마켓플레이스로 남는다: `renames`가 `socratic`을 `null`로 보내고 `forceRemoveDeletedPlugins: true`가 설치된 기기에서 플러그인을 지운다. 이 폴더의 [02-research.md](./02-research.md)가 확인한 대로, 항목만 지우면 설치본이 `not found in marketplace`로 남기 때문이다.

portable-skills의 두 스킬(socratic-brainstorm, socratic-elenchus)이 별도 플러그인과 마켓플레이스 항목으로 나뉘어 있는 것을 하나의 플러그인으로 합치려는 요청. 의도 기록, 기존 설치를 깨지 않는 이전 방법을 확인한 probe 결과, 구현 계획이 있다.

## Documents

- [00-intent.md](./00-intent.md): 문제, 원하는 결과, 영향 대상, 제약을 요청자의 말 그대로 적은 의도 기록
- [02-research.md](./02-research.md): 마켓플레이스 항목을 지울 때와 `renames`로 이름을 옮길 때 기존 설치가 어떻게 되는지 로컬 probe로 확인한 결과
- [05-plan.md](./05-plan.md): 단일 `socratic` 플러그인 생성, 마켓플레이스 `renames` 이전, 설치 파일의 한국어 제거와 라우팅 probe, README와 Pages 갱신, claude.ai 업로드 게이트까지의 구현 계획
