---
status: complete
researched_at: 2026-08-22
---

# 조사 범위와 방법

## 검증 질문

이번 조사는 다음 질문을 분리했다.

1. `@modelcontextprotocol/server-sequential-thinking`의 최신 배포판은 무엇이며 실제로 무엇을 하는가?
2. SuperClaude의 `--seq`는 서버를 켜는가, 아니면 사용 힌트만 넣는가?
3. Opus 5와 Fable 5의 native thinking에 더해 이 도구를 쓰면 추가 가치가 있는가?
4. 비용·지연·개인정보·거부 위험은 무엇인가?
5. 공개 통제 실험과 커뮤니티 경험은 무엇을 보여 주는가?

## 증거 등급

| 등급 | 정의 | 사용 방식 |
|---|---|---|
| A | 공식 문서, 배포 패키지, 업스트림 소스, 직접 재현 | 사실 판정의 주 근거 |
| B | 재현 절차가 있는 이슈, 공식 프로젝트의 기술 논의 | 구현·유지보수 보조 근거 |
| C | 사용자 경험담, 블로그, 비통제 사례 연구 | 가설과 경향만 도출 |
| D | 이 문서의 추론 | 반드시 `[추론]` 또는 미측정으로 표시 |

별·다운로드·디렉터리 등재 수는 효능 증거에서 제외했다. 많이 설치된 도구와 결과를 개선하는 도구는 같은 개념이 아니기 때문이다.

## 수행한 조사

- 저장소의 `MCP_Sequential.md`, `FLAGS.md`, `context_loader.py`, MCP 설치 레지스트리, README, 기존 Opus 5/Fable 5 정렬 문서를 정적으로 추적했다.
- npm registry에서 최신 버전과 수정 시각을 조회하고 tarball의 `package.json`과 `dist/lib.js`를 직접 확인했다.
- MCP `initialize`, `tools/list`, `tools/call`을 실제 실행해 프로토콜 응답, 도구 스키마, 기본 stderr 로깅을 재현했다.
- Anthropic의 Opus 5, Fable 5, adaptive thinking, 도구 사용, `think` 도구 문서를 교차검토했다.
- GitHub 이슈·PR, Reddit, 사례 글을 긍정과 부정으로 나누어 검색했다.

주요 검색식은 `"Sequential Thinking MCP" "Opus 5"`, `"sequential-thinking" "Fable 5"`, `"Sequential Thinking MCP" "adaptive thinking"`, `server-sequential-thinking benchmark`, `site:github.com/modelcontextprotocol/servers sequentialthinking`이었다.

## 조사 도구의 제한

심층 조사를 위해 `tavily-research --model pro`를 먼저 실행했으나 계정 사용 한도 초과로 요청이 거절됐다. 이후 공식 문서와 원문을 직접 검색·열람하는 방식으로 전환했다. 따라서 이 결과물은 Tavily가 생성한 연구 보고서가 아니라 수동 교차검증 결과다.

## 이번에 하지 않은 것

Opus 5/Fable 5에 대해 `native` 대 `--seq` 반복 유료 모델 A/B를 새로 실행하지 않았다. 현재 저장소에도 이 비교를 위한 고정 fixture와 평가 지표가 없다. 단발성 예제 두세 개는 모델 분산보다 약한 증거가 될 가능성이 커서, 사실처럼 인용하지 않고 [07-evaluation-plan.md](./07-evaluation-plan.md)에 반복 가능한 실험으로 설계했다.

따라서 최종 판정의 범위는 다음과 같다.

- 서버 동작·버전·로깅·SuperClaude 플래그 의미: 직접 검증 완료.
- 최신 모델의 공식 권장 방향: 1차 문서로 확인 완료.
- Opus 5/Fable 5에서의 순수 품질 효과 크기: 공개 직접 증거 부재, 로컬 반복 실험 필요.

