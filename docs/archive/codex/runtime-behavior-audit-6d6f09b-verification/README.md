---
status: gaps_found
verified_commit: 6d6f09bae93f32ce25e694f886a22b82585e6b5e
verified_against: first-parent
verified_at: 2026-08-22
---

# Runtime behavior audit merge content verification

## 결론

`6d6f09bae93f32ce25e694f886a22b82585e6b5e`가 `src/superclaude/**`에 넣은 실제 동작을 검증했다. 병합 커밋의 존재, 부모 관계, 충돌 여부 같은 **병합 상태는 판정 대상이 아니다**. 판정은 `gaps_found`다.

전체 자동 테스트는 기준선을 유지했지만, 통합 경계와 실패 경로에서 13개 이슈를 확인했다.

| 심각도 | 수 | 의미 |
|---|---:|---|
| P1 | 4 | 사용자 상태 손실, 의도하지 않은 설치, 반복 동작 방해, 파괴 작업 승인 오해 가능성 |
| P2 | 6 | 잘못된 훅 구성, 침묵하는 기능 실패, 오탐 또는 데이터 품질 문제 |
| P3 | 3 | 진단의 false green, 잘못된 상태 표시, 복합 입력 누락 |

가장 먼저 고쳐야 할 항목은 다음 네 가지다.

1. 혼합 hook entry에서 `--force`/uninstall이 사용자 hook까지 삭제한다.
2. bare install 도중 EOF 또는 Ctrl-C가 발생하면 기본 user-scope 설치로 전환될 수 있다.
3. project/local 설치의 자체 런타임 캐시가 git working tree를 dirty로 만들어 read-only 세션도 Stop hook으로 차단한다.
4. `/sc:git` 설명이 명령 호출 자체를 history rewrite 승인으로 읽히게 하여 같은 파일의 별도 승인 규칙과 충돌한다.

## 토픽별 문서

| 문서 | 주요 내용 |
|---|---|
| [01-hook-installation-and-inventory.md](./01-hook-installation-and-inventory.md) | hook 병합·강제 갱신·제거·등록 진단 |
| [02-installer-and-agent-memory.md](./02-installer-and-agent-memory.md) | unattended 설치, 취소 처리, agent memory, scope 표시 |
| [03-command-contracts-and-resolution.md](./03-command-contracts-and-resolution.md) | `/sc:git` 안전 계약, retired flag 오탐, command-name 처리 |
| [04-runtime-state-and-insight.md](./04-runtime-state-and-insight.md) | 캐시의 git 오염, Stop hook 판정, INSIGHT 수확 품질 |
| [05-test-evidence-and-residuals.md](./05-test-evidence-and-residuals.md) | 테스트 결과, 정상 확인 항목, 자동 검증의 잔여 공백 |

## 검증 범위와 방법

- 비교 범위: `6d6f09b^1..6d6f09b`
- 대상: 해당 범위에서 바뀐 `src/superclaude/**` 24개 파일
- 방식: 요구사항을 실제 관찰 가능한 동작으로 환원한 뒤 정적 연결 추적, 격리된 임시 디렉터리 재현, 관련 테스트, 전체 테스트를 조합했다.
- 독립 검증: 별도 verifier가 같은 commit 범위를 읽기 전용으로 검토했고, 핵심 재현과 전체 테스트 결과가 일치했다.
- 저장소 수정: 이 검증 문서만 추가했다. `src/superclaude/**`는 수정하지 않았다.

심각도는 발생 확률만이 아니라 피해 범위까지 함께 본다. 예를 들어 혼합 hook entry는 흔하지 않을 수 있지만 사용자 명령을 조용히 삭제하므로 P1이다. 반대로 `hooks_registered`의 false green은 실제 실행 경로를 직접 바꾸지는 않아 P3로 두었다.

## 판정 요약

이번 merge가 의도한 session별 cache 분리, runtime state pruning, Stop hook JSON 계약, 정상적인 신규 hook 추가 경로는 동작한다. 그러나 설치와 런타임을 함께 놓고 보면 “사용자 hook 보존”, “세션이 코드를 바꿨을 때만 INSIGHT 요청”, “취소는 설치하지 않음”, “등록 상태의 정확한 진단”이라는 핵심 불변조건을 아직 만족하지 못한다.
