# 03a — core 감사

**대상**
- 항상 로드: `CLAUDE_SC.md`, `core/FLAGS.md`, `core/PRINCIPLES.md`, `core/RULES.md`
- on-demand: `core/rules/RULES_{QUALITY,DELEGATION,DOCS,INTERACTION}.md`, `core/BUSINESS_SYMBOLS.md`
- 프롬프트로 로드되지 않음: `core/README.md`

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- `CLAUDE_SC.md`가 import하는 것은 FLAGS·PRINCIPLES·RULES 3개다. 약 10.5KB, 대략 2.7k 토큰으로 추정한다.
- **가장 큰 위험: 항상 로드되는 텍스트가 on-demand 내용을 전제한다.** R-ID, 모드 동작, 검증 단계표가 여기에 해당한다. `context_loader.py:166-182`의 트리거는 `/sc:` 명령과 플래그에만 반응한다. 그래서 평범한 자연어 세션에서는 이 참조들이 빈 상태가 된다.
- **그다음 위험:**
  - "언제 질문하나"가 PRINCIPLES와 R12 사이에서 서로 반대다.
  - 모델이 측정할 수 없는 수치 조건(ctx %, risk 0.7)이 있다.
- 구식 관용구는 없다. 근거(why)가 붙은 규칙이 많아 전반적인 품질은 높다.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 (모델 인식 관점) | 제안 | 상태 |
|---|---|---|---|---|---|
| High | PRINCIPLES.md:11 ↔ RULES_QUALITY.md:12 | "ask when 2+ readings are valid" vs "Default bounded-proceed; ask reserved for…" | 평범한 세션에서는 PRINCIPLES만 보이므로 모호하면 항상 질문한다. 작성자 의도(가역적이면 가정을 밝히고 진행)와 반대다 | PRINCIPLES에 R12의 가역성 분기를 한 줄로 넣기 | 재확인, **P0 적용** |
| High | FLAGS.md:6-15, 47 | "--task-manage: >3 steps, >2 dirs…", "user flags > auto-detection" | 모델은 모드를 스스로 켤 수 있다고 읽는다. 하지만 모드 본문은 사용자 입력의 키워드가 맞을 때만 주입되므로 "persistent memory", "phase checkpoints"를 즉흥으로 만든다 | 이 항목이 사용자가 입력하는 플래그라고 명시하거나, 자동 감지 시 해당 MODE 파일을 Read하도록 지시 | P1 |
| High | PRINCIPLES.md:8,11,32; RULES.md:14,20,28 | "([R01 Workflow])", tags="[R06 Scope] [R18…]" | 항상 로드되는 텍스트가 정의가 없는 ID를 가리킨다. 모델은 의미를 추측하거나 무시한다 | ID 옆에 한 줄 의미를 쓰거나 ID 표기 제거 | P1 |
| Med-High | RULES.md:16 | "describes a problem… the deliverable is the assessment: report findings and stop" | Claude Code에서 "CI 테스트가 깨져" 같은 문제 서술은 흔히 수정 요청이다. 모델이 문자 그대로 따라 멈출 수 있다 | "요청 형태가 불명확할 때"로 한정하고 이유 추가 | **재평가 후 보류** (03-analysis §3) |
| Med | FLAGS.md:13 ↔ 40 | "ctx >75%" vs "Manual/proactive trigger >=60% ctx" | 같은 Token_Efficiency인데 기준치가 다르다 | 하나로 통일 | P1 |
| Med | FLAGS.md:33-34 | "risk >0.7, usage >75%" | 모델은 risk 점수를 계산할 수 없다. "usage"가 컨텍스트인지 쿼터인지도 불명확하다 | 관찰 가능한 조건(prod 대상, 파괴적 명령 등)으로 교체 | P1 |
| Med | FLAGS.md:18, 29, 35, 40 | "Connector-provided (not a `superclaude mcp` server)… so no MCP doc ships", "loader no clamp", "INSTRUCTION_MAP", "ultracode" | 유지보수자용 메모와 미정의 용어(ultracode는 commands/task.md에만 있음)가 매 세션 토큰을 쓰지만 모델 행동에는 쓸모가 없다 | 제거하거나 README로 이동 (상시 비용 약 15~20% 절감 추정) | P1 |
| Med | RULES_QUALITY.md:9,10,13,18 ↔ RULES.md:7 | R02/R03/R13/R18 "🔴" | 범례상 🔴는 "Security, data safety — always protect"다. 보안이 아닌 규칙이 "항상" 등급이 되어 R02 상태 확인과 R03 환경 점검이 사소한 수정에까지 과적용된다 | 등급 의미를 분리하거나 🟡로 조정 | P2 |
| Med | RULES.md:21 ↔ RULES_QUALITY.md:85 | "Never claim work complete without running… (tests, build…)" | 평범한 세션에서는 검증 단계표의 Level 0(문서 변경은 정적 검사만)이 보이지 않는다. 그래서 오타 수정에도 테스트를 돌린다 | 커널에 "docs-only = inspection" 한 구절 추가 | P1 |
| Med | RULES.md:9 | "include the user request verbatim… leaves out the rationale… that come with the artifact rather than in it" | "verbatim"과 "제외"가 충돌하는 것처럼 읽히고 구문 파싱도 어렵다. 둘을 화해시키는 규칙(마커 치환)은 on-demand에만 있다 | "verbatim, 단 리뷰 위임 시 판정부는 마커로 치환"으로 명시. 위치도 priority_system 밖으로 이동 | P1 |
| Med | RULES.md:34 | "installed under .claude/superclaude/core/rules/" | user 범위로 설치하면 경로가 `~/.claude/...`다(install_components.py:236). 모델이 프로젝트 상대경로로 Read하다 실패한다 | 두 경로를 모두 명시. 핵심 지시가 `note` 속성 안에 있으므로 본문으로 승격 | P1 |
| Med | RULES_DOCS.md:27, 67, 74; RULES_DELEGATION.md:15, 25 | "Legacy pre-cutoff (2026-05-18)", "…-ajitta-2026-03-20.md", "caught 3 critical reversals", "reviewing the project's own framework/config" | 이 저장소의 이력과 사용자명이 다른 사용자 프로젝트로 배포된다. 날짜 cutoff는 다른 프로젝트에서 의미가 없다 | 일반화하거나 삭제 | P1 |
| Low-Med | RULES_QUALITY.md:12 | "ask reserved for four trigger classes" | 본문에는 3개(혹은 5개)만 나열되어 개수가 맞지 않는다 | 개수를 고치거나 목록화 | P2 |
| Low-Med | RULES_QUALITY.md:32 ↔ 13 | Intent Verification 예시가 "…Correct?"로 끝남 | 규칙은 "해석을 밝히고 진행"인데 예시는 질문으로 끝나서, 예시를 따라 과하게 확인한다 | 예시를 "state + proceed"로 바꾸거나, auth는 보안이므로 묻는다는 이유를 명시 | P2 |
| Low-Med | BUSINESS_SYMBOLS.md:7/12-13, 16-18 ↔ 49-51; 45 ↔ 55 | 🎪/🌊 중복, 🕸️ = Meadows이자 Patterns, 💬 = Doumont이자 Clarity, 🧭 = Drucker이자 Next growth areas; "comprehensive: all" vs "max=5" | 기호 하나에 의미가 둘이라 출력이 모호하다. 전문가 9명과 상한 5가 충돌한다 | 기호를 고유하게 하고 comprehensive 예외를 명시 | P2 |
| Low | RULES_QUALITY.md:21 | "askuserquestion-rejection-fallback" | src 어디에도 정의가 없다. 정의는 저장소 로컬 `.claude/rules/gotchas/general.md`에만 있어 배포본에서는 해석되지 않는다 | 삭제하거나 인라인 정의 | P1 |

## 공통 패턴

- **로딩 경계 누수:** 항상 로드되는 텍스트가 on-demand 정의(R-ID, 모드 동작, 검증 단계표)에 기댄다. 트리거가 명령과 플래그 중심이라 일반 대화에서는 참조가 빈 상태다. README:9의 "implement/review work에서 로드" 설명도 실제 정규식과 맞지 않는다.
- **유지보수자 주석 혼입:** 구현 세부(INSTRUCTION_MAP, 프로세스 상한, connector 출처)와 저장소 이력이 모델 지시문에 섞여 있다.
- **측정 불가 수치:** ctx %, risk 0.7, "under 30s".
- **압축 문법의 비용:** "Scope: system > project > module > file", "notify on first use → auto fallback"처럼 동사가 빠진 규칙은 우선순위의 방향과 대상이 모호하다.
- **등급 기호 남용:** 🔴가 보안 등급 범례와 "중요함" 표시로 동시에 쓰인다.

## 강점

- 근거를 붙인 규칙이 일반화에 유리하다. 예: delegate_packet의 "a persuasive rationale flips a reviewer's verdict", Model 항목의 Fable 과금 이유, Durability의 expiry test.
- R12의 가역성 기반 질문 분기는 현행 모델의 과잉 질문과 과잉 진행을 모두 막는 좋은 보정이다.
- 파괴적 작업 규칙이 구체적이다. `git clean -n`, `stash -u` 같은 가역적 대안을 제시한다.
- Before/After 예시가 구체적이고 짧다.
- 구식 관용구가 없다. 유일한 강한 절대 표현인 FLAGS:31 "Do not stop early"는 사용자가 `--iterations`로 명시 요청한 맥락이라 타당하다.
- kernel/module 분리로 상시 비용이 약 2.7k 토큰 수준에 머문다.
