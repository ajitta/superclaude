---
feature: prompt-content-audit
phase: implementing
owner: ajitta
created: 2026-10-15
updated: 2026-10-15
---

# `src/superclaude` 프롬프트 콘텐츠 감사 (Opus 5.5 / Sonnet 5.5 / Fable 5.1 기준)

`src/superclaude/`의 agents, modes, core rules, mcp, skills를 감사했다. 질문은 하나다: 현행 Claude 모델이 마크다운·XML 콘텐츠를 **작성자 의도대로 인식하는가**. 코드 동작은 범위 밖이다.

## 요약

- **문체·관용구는 양호하다.** "You are an expert", "think step by step", "ultrathink" 같은 구세대 관용구가 없다. agents·modes·mcp에는 대문자 강조어(MUST/NEVER/CRITICAL)가 0회다. 상당수 규칙이 이유(why)를 함께 적고 있다. 항상 로드되는 커널은 약 2.7k 토큰이다.
- **위험은 구조에 있다.** 핵심 위험 세 가지:
  1. 어떤 문맥에서 무엇이 보이는지에 대한 가정 (로딩 경계)
  2. 예시와 규칙의 충돌 (현행 모델은 예시를 우선 모방하는 경향이 있다고 판단)
  3. 단발 서브에이전트 실행 모델과 맞지 않는 대화형 본문
- **가장 시급했던 항목**은 `security-engineer.md`의 gotcha였다. "superclaude = … not web app — skip web-vuln scans"가 조건 없이 모든 사용자 프로젝트로 배포되고 있었다. P0에서 수정했다.
- **P0(작은 수정, 큰 효과)는 브랜치 `fix/prompt-content-audit`에 적용했다** ([08-implementation.md](./08-implementation.md)). P1·P2는 [03-analysis.md](./03-analysis.md)의 제안 목록으로 남아 있다.

## 방법

- 영역별로 서브에이전트 6개가 각자 격리된 컨텍스트에서 감사했다. 영역: core / modes / agents 전반 12 / agents 후반 12 + 라우팅 / mcp + sc-prompt / sc-author.
- 공통 루브릭:
  1. 전보체 문법·기호·약어로 인한 모호성
  2. 절대 표현의 문자적 과적용과 근거 누락
  3. 파일 내부·파일 간 모순
  4. 해석되지 않는 참조 (R-ID, 파일, 플래그, 도구, 명령)
  5. 측정 불가 조건과 모델과 무관한 인프라 세부
  6. XML 구조의 의미 대 잡음
  7. 예시 과모방
  8. 저장소 전용 내용의 배포 누수
  9. 구세대 관용구
  10. 상시 로드 비용 대비 가치
- 공식 가이드와 커뮤니티 글은 상당수가 구세대 모델 기준이므로 판단 근거에서 제외했다. 웹 검색도 금지했다. 판단은 텍스트 자체와 현행 모델 행동 지식에만 근거했다.
- High 판정 중 11건은 오케스트레이터(메인 세션)가 원문에서 직접 재확인했다. 각 분석 문서에 "재확인" 표시가 있다. 나머지 High 행은 서브에이전트 판정이며, 이후 문서 사실 검증(09-review.md)에서 인용 약 150건 중 약 143건이 정확한 것으로 확인됐다.

### 격리 관련 공개

- 처음 발송할 때 루브릭 대신 자리표시 문자열이 전달됐다. 정식 브리프는 직후 steer로 보냈다.
- 그 사이 일부 서브에이전트가 저장소 자체 작성 규칙을 읽었다:
  - modes, agents ×2, mcp 담당: `.claude/rules/*-authoring.md`
  - modes 담당: `.serena/memories/` 세션 기록 1건
  - mcp 담당: `~/.claude` 아래 bundled `model-migration.md`의 heading 목록
  - sc-author 담당: 공식 문서 5개를 web_extract로 가져옴
- 각 서브에이전트는 그 내용을 판단 근거로 쓰지 않았다고 보고했다. 모든 발견사항은 `src/superclaude` 원문 인용에 근거한다.
- 서브에이전트 원본 transcript는 scratch 디렉터리(24시간 후 정리)에 있어 보존되지 않는다. 이 폴더의 문서가 그 내용을 옮긴 기록이다.

## Documents

- [03-analysis.md](./03-analysis.md): 공통 패턴 9개, 재평가로 판정이 바뀐 항목, P0/P1/P2 제안
- [03a-analysis-core.md](./03a-analysis-core.md): core (FLAGS, PRINCIPLES, RULES, core/rules/*, BUSINESS_SYMBOLS) 상세 발견사항
- [03b-analysis-modes.md](./03b-analysis-modes.md): modes 8개 + RESEARCH_CONFIG + README 상세 발견사항
- [03c-analysis-agents-first.md](./03c-analysis-agents-first.md): agents 전반 12개 상세 발견사항
- [03d-analysis-agents-second.md](./03d-analysis-agents-second.md): agents 후반 12개 + README, 24개 라우팅 충돌
- [03e-analysis-mcp-sc-prompt.md](./03e-analysis-mcp-sc-prompt.md): MCP 문서 4개 + sc-prompt 스킬, 모델 주장 신뢰성
- [03f-analysis-sc-author.md](./03f-analysis-sc-author.md): sc-author 스킬과 그것이 가르치는 작성 가이드의 건전성
- [08-implementation.md](./08-implementation.md): P0 적용 내역, 재평가로 보류한 항목, 검증 결과
- [09-review.md](./09-review.md): P0 수정에 대한 독립 리뷰와 문서 사실 검증, 반영 내역
