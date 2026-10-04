---
feature: command-local-flags
phase: complete
owner: ajitta
created: 2026-10-04
updated: 2026-10-04
---

# 명령 전용 플래그 (`<flags>`)

모든 `/sc:` 명령은 `<syntax>`의 명령 전용 플래그를 `<flags>` 섹션에 한 줄씩 정의한다. context_loader hook은 이 섹션을 그 명령이 소유한 플래그 목록으로 읽는다. 첫 계획(정의 추가와 hook 오탐 수정)은 standalone 문서로 저장했다가 병합 뒤 이 폴더로 옮겼다.

## Documents

- [05-plan.md](./05-plan.md): `<flags>` 정의 추가와 context_loader hook 오탐 수정 계획(완료)
- [05a-plan-pointer-checks.md](./05a-plan-pointer-checks.md): 단계·섹션 참조를 검사 가능한 형식으로 바꾸고, 전역 플래그 이름에 자기 값을 주는 명령을 테스트로 잡는 후속 계획
