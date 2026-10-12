---
feature: serena-removal
phase: complete
owner: ajitta
created: 2026-10-12
updated: 2026-10-12
---

# Serena 의존 제거

SuperClaude가 Serena를 이용하고 참조하면서 동작하는 부분을 배포 콘텐츠, CLI/설치 코드, 레포 개발 환경에서 찾아 없애는 작업. 사용자가 Serena를 쓰는 것은 막지 않으며, 기존 사용자 호환과 `.serena` 메모리 보존이 제약이다.

## Documents

- [00-intent.md](./00-intent.md): 요청자의 말 그대로 기록한 문제, 원하는 결과, 영향 범위, 제약, 미결 질문
- [01-discovery.md](./01-discovery.md): Serena를 필수처럼 만드는 지점 인벤토리, Q1~Q7 결정, review가 확인할 제안 P1~P10
- [05-plan.md](./05-plan.md): 구현 계획 index. 메모리 폴더·도구 중립 문구·설치기 결정, phase 순서, 위험, 채택하지 않은 대안, 완료 증명
  - [05a-plan-memory-folder.md](./05a-plan-memory-folder.md): Phase A, /sc:save·/sc:load를 `.claude/memories/` + auto memory로
  - [05b-plan-loader-flag.md](./05b-plan-loader-flag.md): Phase B, MCP 문서·주입·플래그·fallback 제거
  - [05c-plan-installer.md](./05c-plan-installer.md): Phase C, 설치기 등록 제거와 core/plugin 구분 제거
  - [05d-plan-symbolic-first.md](./05d-plan-symbolic-first.md): Phase D, 도구 중립 Symbolic-First와 가드 테스트
  - [05e-plan-repo-docs.md](./05e-plan-repo-docs.md): Phase E, 레포 문서와 local scope 재동기화
  - [05f-plan-review-fixes.md](./05f-plan-review-fixes.md): Phase F, 독립 리뷰 발견(I1~I4)과 고른 Suggestion 수정
