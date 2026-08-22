---
status: verified
researched_at: 2026-08-22
---

# 업스트림 구현과 런타임 검증

## 최신 배포 상태

2026-08-22 npm registry 기준 최신 배포판은 `2026.7.4`, 수정 시각은 `2026-07-04T23:05:13.436Z`다. 저장소의 `src/superclaude/mcp/README.md:16`에 적힌 `2025.12.18`은 오래됐다. [npm package](https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking)와 [registry metadata](https://registry.npmjs.org/@modelcontextprotocol%2Fserver-sequential-thinking/latest)에서 확인할 수 있다.

배포는 2026년 7월에도 이뤄졌으므로 “완전히 유지보수 중단”이라고 말할 수 없다. 다만 배포판이 초기화 응답에서 여전히 `0.2.0`을 보고하는 버그가 있고, 2026-07-29에 열린 [업스트림 이슈 #4575](https://github.com/modelcontextprotocol/servers/issues/4575)에도 같은 재현이 기록돼 있다.

## 서버가 실제로 하는 일

업스트림 [도구 스키마](https://github.com/modelcontextprotocol/servers/blob/main/src/sequentialthinking/index.ts)는 모델에게 다음 값을 제출하게 한다.

- 현재 사고 문자열 `thought`
- 현재 번호와 예상 총 단계 수
- 다음 사고가 필요한지 여부
- 선택적 revision·branch 메타데이터

배포 tarball의 `dist/lib.js`를 확인한 결과 서버의 핵심 동작은 다음뿐이다.

1. `thoughtNumber > totalThoughts`이면 총 단계 수를 올린다.
2. 입력 전체를 프로세스 메모리의 `thoughtHistory` 배열에 추가한다.
3. branch 메타데이터가 있으면 `branches` 객체에 같은 입력을 추가한다.
4. 기본 설정에서는 `thought` 전문을 stderr에 출력한다.
5. 사고 번호, 총 단계 수, 다음 단계 여부, branch 목록, 이력 길이를 JSON으로 반환한다.

별도 LLM 호출, 검색, 정리, 점수화, 가설 검증 알고리즘은 없다. 업스트림 설명의 “가설을 검증하고 올바른 답을 제공한다”는 부분은 서버 코드가 수행하는 기능이 아니라 모델에게 주는 행동 지시다. 즉, 이것은 **추론 엔진이 아니라 모델 생성 텍스트를 구조화하는 stateful echo/log 도구**다.

## 로컬 MCP 재현

최신 패키지를 stdio로 실행해 다음을 확인했다.

| 검사 | 결과 |
|---|---|
| 프로토콜 초기화 | 성공, `protocolVersion: 2025-11-25` |
| 서버 보고 버전 | `0.2.0` — npm `2026.7.4`와 불일치 |
| 도구 목록 | `sequentialthinking` 1개 |
| read-only annotation | `readOnlyHint: true`, `destructiveHint: false` |
| idempotent annotation | `idempotentHint: true`, 그러나 같은 호출을 반복하면 이력 길이가 증가 |
| 단일 thought 호출 | 성공, `thoughtHistoryLength: 1` 반환 |
| 기본 로깅 | 입력한 thought 전문이 stderr에 출력됨 |

도구의 정상 실행 가능성은 확인됐지만, 이 검사는 답의 품질 향상을 측정하지 않는다.

같은 입력을 같은 프로세스에서 두 번 호출했을 때 `thoughtHistoryLength`가 `1`에서 `2`로 증가했다. 따라서 선언된 `idempotentHint: true`와 실제 stateful 동작은 일치하지 않는다. 클라이언트가 이 hint를 재시도 안전성 판단에 사용하면 중복 thought가 쌓일 수 있다.

## SuperClaude의 `--seq`가 하는 일

`src/superclaude/scripts/context_loader.py:138`은 `--seq`를 발견하면 `MCP_Sequential.md`를 선택한다. 기본 tier에서 실제 주입 내용은 `context_loader.py:258`의 한 줄이다.

```text
Sequential: multi-step reasoning chain. Use for 3+ component problems.
```

이 코드 경로에는 MCP 프로세스를 시작하거나, 설치된 서버를 turn 단위로 활성화·비활성화하는 동작이 없다. 서버 설치는 별도 CLI인 `superclaude mcp`가 `claude mcp add ...`를 실행할 때 이뤄진다.

따라서 현재 의미는 다음과 같다.

- `--seq`: 이미 클라이언트에 노출된 Sequential 도구를 쓰도록 모델에 힌트를 추가한다.
- 서버 미설치 상태의 `--seq`: 힌트와 조건부 fallback 안내만 생기며 서버는 나타나지 않는다.
- 서버 설치 상태에서 `--seq` 없음: 도구가 클라이언트 tool set에 계속 있을 수 있다.
- `--no-mcp`: SuperClaude의 MCP 문서 주입을 억제할 뿐, Claude Code에 등록된 MCP 서버를 제거하거나 turn 단위로 끄지 않는다.

README의 “MCP 서버 — turn별 opt in/out”, `--all-mcp`의 “enable all”, `--no-mcp`의 “disable all” 설명은 현재 런타임 구현보다 강하다. 이는 효능 문제와 별개의 플래그 계약 불일치다.

## 유지보수 품질 신호

- [이슈 #2332](https://github.com/modelcontextprotocol/servers/issues/2332)는 실제 로그에서 모델이 revision/branch 필드를 거의 활용하지 않았다고 보고했다. 원 로그가 공개되지 않았고 Grok 요약에 의존하므로 낮은 등급의 증거다.
- [PR #3324](https://github.com/modelcontextprotocol/servers/pull/3324)는 테스트·검증·자원 관리를 크게 보강하려는 2026년 draft PR이다. 아직 draft이므로 현 배포판의 기능으로 계산하면 안 된다.
- 현재 배포판은 `idempotentHint: true`를 선언하지만 반복 호출이 이력을 변경한다. 이는 직접 재현한 annotation·동작 불일치다.
- 최신 배포가 존재한다는 사실은 생존성 근거일 뿐, 최신 모델에서의 효과 근거는 아니다.
