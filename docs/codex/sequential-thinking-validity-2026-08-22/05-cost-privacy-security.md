---
status: complete
researched_at: 2026-08-22
---

# 비용·개인정보·보안 검토

## 토큰과 지연

Sequential MCP의 비용은 세 층으로 나뉜다.

1. SuperClaude `--seq` 자체는 기본 tier에서 짧은 한 줄 힌트를 세션당 한 번 주입한다.
2. MCP tool description은 서버가 클라이언트 tool set에 등록될 때 모델 컨텍스트에 들어간다. 이는 플래그보다 서버 설치·도구 검색 방식에 좌우된다.
3. 실제 사용할 때마다 `thought` 문자열, JSON tool call, tool result, 추가 model request/continuation round trip이 생긴다. 이 부분이 주 비용이다.

Anthropic의 [도구 사용 문서](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)는 client tool call마다 모델 응답, 클라이언트 실행, tool result, 다음 요청의 round trip이 필요하다고 설명한다. [thinking 문서](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models)는 native thinking 토큰도 유료라고 명시한다. Sequential을 native thinking 위에 겹치면 두 비용이 모두 발생할 수 있다.

따라서 README의 `Sequential: ... 30-50% fewer tokens` 주장은 출처와 재현이 없고 현재 구현 구조와도 맞지 않는다. 기존 가이드의 `--research --seq` 58% 절감 수치는 전체 MCP 문서를 1줄 hint로 줄인 **주입 최적화 전후 비교**이지, Sequential을 사용했을 때 native reasoning보다 58% 절약된다는 결과가 아니다.

## thought 로깅과 데이터 경계

최신 배포판은 기본적으로 `thought` 전문을 stderr에 출력한다. `DISABLE_THOUGHT_LOGGING=true`를 주면 이 터미널 출력은 멈춘다. 그러나 다음은 계속 남을 수 있다.

- 모델이 생성한 tool argument
- MCP host의 대화 transcript 또는 디버그 로그
- tool call을 전달한 API·클라이언트 계층의 보존 데이터

즉 환경 변수는 **서버의 추가 stderr 복제본**만 없앤다. reasoning-like text가 host와 모델 대화에 존재하는 사실은 바꾸지 않는다.

민감한 소스 코드, 자격 증명, 개인 데이터, 보안 가설을 `thought`에 넣지 않도록 별도 제한이 필요하다. 자유형 thought 전문은 최소권한 원칙에 맞지 않기 쉽다.

## Fable 5의 reasoning 경계

Fable 5는 raw CoT를 반환하지 않는다. Sequential의 `thought`는 숨겨진 raw CoT를 읽는 API가 아니라, 모델이 별도의 tool argument로 새로 생성한 텍스트다. 그러므로 이를 “원래 내부 사고의 정확한 감사 로그”라고 부르면 안 된다.

또한 공식 문서는 reasoning을 응답 텍스트로 전사하도록 요구하면 `reasoning_extraction` 거부가 늘 수 있다고 한다. tool argument가 동일하게 분류된다는 공개 증거는 없으므로 위험은 **미측정**이다. 이 불확실성 때문에 Fable 5에서는 기본 off와 별도 거부율 측정이 필요하다.

## 로컬 MCP와 공급망

SuperClaude 설치 레지스트리는 버전을 고정하지 않은 다음 명령을 저장한다.

```text
npx -y @modelcontextprotocol/server-sequential-thinking
```

MCP 프로젝트의 [security policy](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/SECURITY.md)는 local stdio 서버를 일반 로컬 애플리케이션과 같은 신뢰 수준으로 취급하며 클라이언트와 같은 권한으로 실행된다고 설명한다. 현재 Sequential 서버 코드는 단순하고 공식 프로젝트 소속이지만, unpinned `npx -y`는 향후 배포 코드를 자동으로 실행하는 공급망 경계다.

보존할 경우 다음이 최소 조치다.

- 검증한 package version 고정과 정기 업데이트 절차
- `DISABLE_THOUGHT_LOGGING=true` 기본 설정
- 민감 데이터와 reasoning 전문을 넣지 않는 tool 지침
- host transcript 보존·접근 정책 확인
- Fable 5에서 거부·fallback telemetry 수집

## 보안 판정

현재 Sequential 서버 자체에서 네트워크 전송이나 파일 접근은 확인되지 않았다. 그래서 즉시 데이터 유출 도구로 분류할 이유는 없다. 주 위험은 외부 전송보다 **로컬 로그·host transcript에 reasoning-like text가 불필요하게 복제되는 것**과 **unpinned 실행 공급망**이다.
