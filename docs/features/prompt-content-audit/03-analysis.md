# 03 — 종합 분석: 공통 패턴과 제안

영역별 상세 발견사항은 03a–03f에 있다. 이 문서는 영역을 가로지르는 패턴, 오케스트레이터 재평가로 판정이 바뀐 항목, 우선순위별 제안을 다룬다.

## 1. 기계적 지표 (오케스트레이터 측정, 2026-10-15)

| 지표 | 결과 |
|---|---|
| 대문자 강조어(NEVER/MUST/ALWAYS/CRITICAL/IMPORTANT) | agents 0, modes 0, mcp 0, core 1, skills 6 |
| 화살표·이모지 기호 | core 158, agents 74, mcp 66, modes 45, skills 4 |
| agents에 쓰인 R-ID 태그 | 22개 파일, 약 60회. 가장 많은 것은 `[R06 Scope]` 25회, `[R15 Verification]` 10회, `[R18 Necessity Test]` 9회, `[R02 Status Check]` 9회 |
| `<handoff next="/sc:…">`가 있는 agent | 24/24. 참조하는 명령은 모두 `commands/`에 실재 |
| description에 "Use proactively/immediately"가 있는 agent | 21/24 |
| 구세대 관용구 ("You are an expert", "think step by step", "ultrathink") | 0회. sc-prompt가 이를 제거 대상으로 설명하는 문장만 있음 |

## 2. 공통 패턴 (우선순위순)

### P-1. 저장소 전용 내용이 사용자 프로젝트로 배포됨 — High

- 재확인한 원문: `agents/security-engineer.md:71`, "superclaude = markdown content framework, not web app — skip web-vuln scans". 조건 없이 적혀 있다.
- 문제: 사용자의 웹앱을 감사할 때도 웹 취약점 스캔을 건너뛸 수 있다. 같은 파일 :49 체크리스트 "OWASP Top 10 reviewed"와도 정면으로 충돌한다.
- 같은 패턴이 있는 곳:
  - `backend-architect.md:67-68` ("SC CLI use Click…")
  - `frontend-architect.md:71-72`
  - `RULES_DOCS.md`의 "Legacy pre-cutoff (2026-05-18)"와 `-ajitta-` 파일명 예시
  - `RULES_DELEGATION.md:15,25`의 저장소 이력 ("caught 3 critical reversals")
  - `verifier.md:64-66`의 예시 파일명
- 비교: `project-initializer.md:89-90`은 이미 "when the target repo is superclaude itself" 조건을 붙여 두었다. 이 형태가 모범이다.
- 처리: agent 3개는 P0에서 조건을 붙였다. RULES_DOCS/RULES_DELEGATION은 P1.

### P-2. 대화형 설계가 단발 서브에이전트 안에 있음 — High

- 원문: `project-initializer.md:40`, "Present interactive task menu… Accept user selection". socratic-mentor와 requirements-analyst는 다회차 문답을 전제한다. 24개 agent 모두에 "Ask First"가 있다.
- 문제: 서브에이전트는 실행 중에 사용자에게 물을 수 없다. 모델은 두 경로 중 하나로 간다.
  - 메뉴나 질문 목록만 돌려주고 끝낸다.
  - 사용자 선택을 스스로 가정하고 진행한다. 이 경우 Ask First를 위반한다.
- 관련 사실: 저장소의 `.claude/rules/agent-authoring.md`는 "Body run two modes"를 명시한다. 같은 파일이 서브에이전트로도, `claude --agent` 메인 스레드로도 실행된다. 대화형 본문은 후자에서만 성립한다.
- 제안(P1): 24개 공통으로 한 줄을 넣는다. 예: "When running as a subagent and an Ask First item applies, put the proposed action and the question in the final report and stop; an explicit parent request counts as confirmation." 두 실행 모드 모두에서 읽히는 문장이어야 한다.

### P-3. 도구 권한과 본문 서술의 불일치 — High → 일부 재평가

- `git-workflow.md:44`의 "(Edit + Write disallowed)":
  - frontmatter에 `disallowedTools`가 없다. 커밋 `672055ce`에서 의도적으로 제거됐다(tools 계열 필드가 MCP 상속을 끊는 문제, #13898).
  - 본문만 이미 막혀 있다고 주장하므로 모델은 차단을 믿는다.
  - P0에서 본문을 사실대로 고쳤다. 도구 설정은 Edit/Write를 막지 않으므로 행동 규칙으로 지킨다고 적었다.
- `self-review.md`의 `tools: Read, Grep, Glob, Agent`:
  - Bash가 없는데 gotcha가 "'42/42 pass' requires running tests"를 요구한다.
  - P0에서 고쳤다. 테스트 출력이 손에 있어야 하고, 이 agent는 테스트를 실행할 수 없으므로 출력이 없으면 UNVERIFIED다.
- **재평가로 판정을 바꾼 항목: `simplicity-guide.md`의 Agent 위임.**
  - 서브에이전트 감사는 "서브에이전트는 Agent를 쓸 수 없어 경로가 막힌다"(High)고 판정했다.
  - 그러나 `.claude/rules/agent-authoring.md`의 Tool access 표는 `Read, Grep, Glob, Agent`를 정식 패턴으로 둔다. `--agent` 메인 스레드 모드에서는 Agent가 동작한다.
  - 본문 :55도 이미 "else reports it unverified"로 서브에이전트 모드의 대체 경로를 적고 있다.
  - 그래서 Low로 낮추고 수정하지 않았다.

### P-4. 예시가 규칙과 반대 — High

현행 모델은 규칙 문장보다 예시와 출력 템플릿을 우선 모방한다. 아래 네 곳 모두 원문에서 재확인했고 P0에서 고쳤다.

| 위치 | 규칙 | 충돌하는 예시·템플릿 |
|---|---|---|
| `MODE_Business_Panel.md` | :20 "Synthesis-First: Integrate… before show individual views". 라우팅 표: Market entry = Porter + Kim, Debate | :54 Porter → Kim → Taleb → Synthesis 순서. Taleb 추가, Debate 구조 없음 |
| `MODE_Verbalized_Sampling.md` | :21 "attach probabilities… only AFTER the text exists" | :60 `### Response N (p={probability})` 헤더. 모델은 위에서 아래로 생성하므로 확률을 먼저 쓴다 |
| `sc-author/references/quality.md` | :116 표 "claude-opus-5-5: not stated as a default" | :75 "Opus 5 and Opus 5.5 already verify" |
| `project-initializer.md` | :95 `<never>auto-execute without menu` | :84 예시 "runs … together" |

### P-5. 로딩 경계 누수 — High (구조 문제, P1)

- **agents의 R-ID:** R-ID는 on-demand 모듈 `RULES_QUALITY.md`에만 정의되어 있다. agent 본문의 R-ID는 서브에이전트 세션에서 해석되지 않는다. 저장소 규칙도 "subagent session hold only markdown body"라고 명시한다.
  - 대부분은 문장 자체가 뜻을 담고 있어 무해한 잡음이다.
  - 다만 `project-initializer.md:89-90`처럼 R06을 도구 선택 규칙에 잘못 붙인 곳은 오해를 부른다.
- **PRINCIPLES와 R12의 질문 기준 충돌:** `PRINCIPLES.md:11`의 "ask when 2+ readings are valid"는 `RULES_QUALITY.md:12` R12의 가역성 분기("Default bounded-proceed")와 반대였다.
  - 평범한 세션에는 on-demand 모듈이 주입되지 않는다. `context_loader.py`의 트리거가 `/sc:` 명령과 플래그 중심이기 때문이다. 그래서 모델은 PRINCIPLES만 보고 모호하면 항상 질문하게 된다.
  - P0에서 PRINCIPLES에 가역성 분기를 넣었다.
- **FLAGS의 모드 목록:** `FLAGS.md:6-15`를 모델은 "내가 모드를 켤 수 있다"로 읽는다. 하지만 모드 본문은 사용자 입력의 키워드나 플래그가 맞을 때만 주입된다. 그러면 "persistent memory", "phase checkpoints" 같은 동작을 즉흥적으로 지어내게 된다.
- **설치 경로 불일치:** `RULES.md:34`의 on-demand 파일 경로가 "installed under .claude/superclaude/core/rules/"로 프로젝트 기준만 적혀 있다. user 범위로 설치하면 `~/.claude/...`라서 Read가 실패한다.
- **경로 없는 참조:** `MODE_DeepResearch.md:3`과 `deep-researcher.md`가 RESEARCH_CONFIG.md를 경로 없이 참조한다. 이 파일은 loader가 주입하지 않는다.

### P-6. "Use proactively" 남발과 라우팅 충돌 — Med-High (P1)

- 24개 중 21개 agent의 description에 있다. 현행 모델은 이 문구를 문자 그대로 따르고, 모든 agent에 있으니 우선순위 신호로 작동하지 않는다.
- 겹치는 지점:
  - **구현 직후:** quality-engineer, refactoring-expert, security-engineer, project-manager가 동시에 호출된다.
  - **auth 작업:** security, system-architect, quality, simplicity, self-review, backend 6개가 겹친다.
  - **세션 시작:** repo-index, project-initializer, 내장 Explore가 겹친다.
- 모범 사례: verifier의 "Not for…" 부정 조건이 라우팅 품질을 높인다. 다른 agent description의 템플릿으로 쓸 만하다.
- 저장소 규칙과의 충돌: 저장소의 `agent-authoring.md`는 "Use proactively for…"를 표준 트리거 문형으로 가르친다. 이 제안은 그 규칙의 개정을 뜻한다. 규칙과 `tests/unit/test_agent_structure.py::TestAgentDescriptionInterface`(트리거 문형 존재 검사)를 함께 바꿔야 한다.

### P-7. 모델이 측정할 수 없는 조건 — Med (P1)

- core:
  - `FLAGS.md:33-34`의 "risk >0.7, usage >75%"
  - `FLAGS.md:13`의 "ctx >75%"와 :40의 ">=60%"가 같은 Token_Efficiency를 가리키는데 수치가 다르다.
- agents:
  - `refactoring-expert`의 "baseline complexity metric": 측정 도구가 지정되지 않았다.
  - `frontend-architect`의 "LCP under 2.5s"
  - `devops-architect`의 "rehearsed at least once"
- 문제: 체크리스트를 채우려는 압력 때문에 **수치나 검증 완료를 지어낼** 위험이 있다.
- 제안: "측정했으면 수치와 출처를, 못 했으면 '미검증'이라고 쓴다."

### P-8. 전보체 문법 — Low-Med (P2)

- 예: "Technical writer make clear, full docs", "Claude no simplify what no understand", "Collab… reqs".
- 대부분 해독은 된다. 하지만 두 가지 비용이 있다.
  - 사용자용 출력(문서, PRD, 학습 대화)으로 문체가 옮겨갈 수 있다.
  - `MODE_Token_Efficiency.md:42`가 금지하는 "dropped articles, invented abbreviations"와 같은 문체라서, 두 모드를 함께 켜면 신호가 충돌한다.
- 이력: 저장소에는 이미 "chatspeak sweep" 커밋(`592457b0`)이 있었다. 사용자 대면 출력을 내는 agent·mode가 남은 대상이다.

### P-9. 🔴 기호의 의미가 둘 — Med (P2)

- 정의: `RULES.md:7` 범례는 🔴를 "Security, data safety — always protect"로 둔다.
- 다른 용도: `RULES_QUALITY.md`는 R02(Status Check), R03(Diagnosis), R13, R18에도 🔴를 붙였다.
- 결과: 보안이 아닌 규칙이 "항상" 등급으로 읽혀 사소한 수정에까지 과하게 적용된다.

## 3. 재평가로 보류한 항목

| 원 판정 | 항목 | 보류 사유 |
|---|---|---|
| Med-High (core) | `RULES.md:16` "describes a problem… the deliverable is the assessment: report findings and stop"이 "CI 깨졌어" 같은 수정 요청을 막는다 | 원문이 이미 "rather than requesting a change"로 한정한다. canary `problem-statement-not-request`(`evals/tasks.yaml`)가 이 행동을 보호한다. 관찰된 실패가 없다. 저장소의 `content-quality.md` Improvement Workflow는 "Observe a real failure — never improve speculatively"를 요구한다 |
| High (agents 후반) | simplicity-guide의 Agent 위임 불가 | P-3 참조. `--agent` 모드의 정식 패턴이고, 서브에이전트용 대체 경로가 이미 적혀 있다 |
| High (agents 전반) | git-workflow에 `disallowedTools` 복구 | `672055ce`에서 의도적으로 제거됐다. memory가 켜진 agent에서 Write/Edit를 deny하면 MEMORY.md 쓰기와 충돌할 수 있는지 확인되지 않았다. 본문만 사실대로 고쳤다 |

## 4. 제안

### P0 — 적용 완료 (브랜치 `fix/prompt-content-audit`)

1. security·backend·frontend의 superclaude 전용 gotcha에 "when the target repo is superclaude itself" 조건을 붙였다. security에는 "그 밖의 저장소는 웹 취약점 포함 전체 검토"를 명시했다.
2. git-workflow 본문의 거짓 차단 주장을 고쳤다. self-review의 테스트 실행 요구를 tools 설정과 맞췄다.
3. 예시·템플릿과 규칙의 충돌 4건을 고쳤다: Business_Panel, Verbalized_Sampling, sc-author `quality.md`, project-initializer.
4. `PRINCIPLES.md:11`에 R12의 가역성 분기를 넣었다.

### P1 — 구조

5. 24개 agent 공통으로 서브에이전트 실행 규칙 한 줄을 넣는다(P-2).
6. "Use proactively"는 2~3개만 남기고, 나머지는 "Use when the user asks…" + "Not for…" 형태로 바꾼다. `agent-authoring.md`와 description 테스트를 함께 개정한다(P-6).
7. agent 본문의 R-ID 태그를 지우거나 한 줄 근거 문장으로 바꾼다. initializer의 R06 오기부터 처리한다(P-5).
8. FLAGS의 측정 불가 조건을 관찰 가능한 조건(prod 대상, 파괴적 명령 등)으로 바꾸고, ctx 기준치를 하나로 통일한다(P-7).
9. FLAGS의 모드 항목에 "사용자가 입력하는 플래그"임을 명시하거나, 자동 감지 시 해당 MODE 파일을 Read하도록 지시한다. `RULES.md:34`에 user 범위 설치 경로를 추가한다(P-5).
10. RULES_DOCS/RULES_DELEGATION의 저장소 이력과 사용자명을 일반화한다(P-1).
11. 영역별 Med 항목(03a–03f)을 처리한다. 대표 항목:
    - repo-index 7일 재사용 규칙 vs "always regen" 모순
    - technical-writer description vs 본문 모순
    - Tavily never/prefer 모순
    - sc-prompt mirror의 이월 규칙 위반
    - sc-author checker를 새 파일에 실행할 수 없음

### P2 — 품질

12. 사용자 대면 출력을 내는 agent·mode부터 전보체를 정상 문장으로 바꾼다(P-8).
13. 🔴를 보안 전용으로 되돌리고 등급 표기를 분리한다(P-9).
14. sc-author의 구세대 관습을 조건부로 완화한다: 예시 3~5개 의무, 문서 전체를 루트 요소 하나로 감싸기, 100줄 넘으면 목차 필수(03f).
15. 확신도 낮은 사실 주장을 재확인한다: `/doctor prompt-audit`의 실재 여부, memory import "four hops", `fields.yaml`의 일부 필드(03f).

### 릴리스 전 필수

core(`PRINCIPLES.md`)가 바뀌었다. `make release` 전에 `make canary-gates`를 돌리고 보고서를 확인해야 한다(AGENTS.md). 이번 작업에서는 canary를 실행하지 않았다.
