---
feature: session-memory-multi-machine
phase: planning
owner: ajitta
created: 2026-10-21
updated: 2026-10-21
---

# 여러 컴퓨터에서 쓰는 세션 메모리

같은 저장소를 두 컴퓨터에서 같은 날 같은 브랜치(`master`)로 작업한다. 지금 `/sc:save`는 `session_[date]_[branch-slug].md` 하나를 그날 계속 고쳐 쓰므로, 두 컴퓨터가 같은 파일을 고친다. pull 없이 저장하면 push가 거절되거나 병합 충돌이 난다. 또 `/sc:load`는 디스크의 파일을 읽으므로 pull 전이면 다른 컴퓨터의 마지막 상태를 못 본다.

소유자가 고른 방안(2026-10-21): (b) 파일 이름에 컴퓨터 이름을 넣는다 + (a) 명령이 원격보다 뒤처졌는지 확인하고 pull·커밋·push를 묻는다.

## Documents

| File | Content |
|---|---|
| [05-plan.md](./05-plan.md) | 결정, 범위, Phase 0–4 작업, Proof |
