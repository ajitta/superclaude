---
name: superclaude-best-command-flow-kr
type: example
triggers: [best-flow, command-flow, flags-agents]
description: "SuperClaude 실전 명령어/플래그/에이전트 조합 1페이지 가이드 (KR)"
category: examples
complexity: reference
mcp-servers: [context7, sequential, serena, tavily, playwright, magic]
---

<document type="example" name="superclaude-best-command-flow-kr"
          triggers="best-flow, command-flow, flags-agents">

# SuperClaude 잘 쓰는 명령어 플로우 (1페이지, src 기준)

## 0) 세션 시작

```text
/sc:help
/sc:load
```

## 1) 플래그 프리셋

| 상황 | 추천 플래그 | 목적 |
|---|---|---|
| 일반 구현/분석 | `--think --c7` | 기본 사고 + 공식 문서 확인 |
| 복잡한 구조 변경 | `--think-hard --seq --c7` | 다단계 추론 + 문서 기반 설계 |
| 대규모 작업 | `--ultrathink --all-mcp --delegate auto` | 최대 깊이 + 병렬 위임 |
| UI 검증 | `--frontend-verify --play --magic` | UI 생성 + 브라우저/E2E 검증 |
| 버그 추적 | `--seq --validate` | 원인 분석 + 변경 전 검증 |
| 토큰 압박 | `--uc` (`--token-efficient`) | 컨텍스트 절약 |
| MCP 배제 재현 | `--no-mcp` | 네이티브 도구만으로 재검증 |

## 2) 작업 유형별 골든패스

### A. 신규 기능 개발

```text
/sc:brainstorm "문제/아이디어" --brainstorm
/sc:design "확정한 방향" --think-hard --c7
/sc:workflow "실행 계획" --strategy systematic --depth deep
/sc:implement "기능명" --with-tests --c7 --seq
/sc:test --type unit --coverage
/sc:git
/sc:save
```

### B. 버그/장애 대응

```text
/sc:troubleshoot "증상" --type bug --trace --seq --validate
/sc:analyze "영향 범위" --focus quality --think
/sc:implement "수정안" --with-tests --safe-mode
/sc:test --type integration
/sc:git
/sc:save
```

### C. 기술조사/의사결정

```text
/sc:research "비교/조사 주제" --depth deep
/sc:spec-panel "설계안 리뷰" --mode critique
/sc:design "선택한 방향" --type architecture --format spec
/sc:workflow "실행 단계" --strategy systematic
/sc:implement "적용 기능" --with-tests
/sc:test --coverage
/sc:save
```

## 3) 에이전트 조합 프리셋

| 상황 | 추천 에이전트 조합 |
|---|---|
| 요구사항 → 설계 | `@agent-requirements-analyst` + `@agent-system-architect` |
| API/백엔드 구현 | `@agent-backend-architect` + `@agent-security-engineer` + `@agent-quality-engineer` |
| UI/프론트 구현 | `@agent-frontend-architect` + `@agent-performance-engineer` + `@agent-quality-engineer` |
| 장애 원인 분석 | `@agent-root-cause-analyst` + `@agent-performance-engineer` |
| 리팩토링/품질 개선 | `@agent-refactoring-expert` + `@agent-simplicity-guide` + `@agent-self-review` |
| 문서화/온보딩 | `@agent-technical-writer` + `@agent-learning-guide` |

예시:

```text
@agent-backend-architect "결제 API 경계/에러 모델 설계"
@agent-security-engineer "인증/인가 위협모델 검토"
@agent-quality-engineer "통합 테스트 시나리오 제안"
```

## 4) 막힐 때 공용 탈출 루트

```text
/sc:recommend "현재 상황 + 막힌 지점"
```

## 5) 세션 종료

```text
/sc:test --coverage
/sc:git
/sc:save
```

## 6) 최소 운영 규칙

- 구현 시작 전 문제정의: `brainstorm` 또는 `troubleshoot` 선행
- 완료 주장 전 검증: `test` 결과 없는 완료 선언 금지
- 큰 작업 분해: `workflow`로 단계화
- 세션 종료 시 상태 보존: `save` 필수

</document>

