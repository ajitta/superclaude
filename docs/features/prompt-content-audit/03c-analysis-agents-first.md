# 03c — agents 전반 12개 감사

**대상**
- `agents/` 아래 12개: backend-architect, business-panel-experts, deep-researcher, devops-architect, frontend-architect, git-workflow, insight-analyst, learning-guide, performance-engineer, project-initializer, project-manager, python-expert
- 실행 형태: Claude Code 서브에이전트다. 부모가 frontmatter description을 보고 선택하고, 본문이 서브에이전트의 시스템 프롬프트가 된다. 같은 파일을 `claude --agent`로 메인 스레드에서 실행할 수도 있다.

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- **라우팅 신호:** 12개 모두 같은 골격(role / focus / actions / tool_guidance / bounds)을 쓰고, description에 "Use proactively… / Use when…"이 있다. 대체로 명확하다.
- **가장 큰 위험:** 서브에이전트는 한 번 실행하고 끝나는데, 본문에는 메뉴 제시, 사용자 확인, 소크라테스식 문답 같은 대화형 절차가 많다. 모델이 멈추거나 사용자 선택을 지어낸다.
- **다음 위험 세 가지:**
  - git-workflow의 도구 차단이 본문에만 적혀 있다.
  - "Use proactively"가 12개 모두에 있다.
  - superclaude 전용 gotcha가 사용자 프로젝트로 배포된다.
- **그 밖:** 내부 수치 모순, 측정 불가 체크리스트, 서브에이전트에서 해석되지 않는 rule ID.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 (모델 인식) | 제안 | 상태 |
|---|---|---|---|---|---|
| High | git-workflow.md:44 (frontmatter 1-6) | "modify source files (Edit + Write disallowed)" | frontmatter에 `disallowedTools`가 없다(`672055c`에서 삭제). 실제로는 막혀 있지 않은데 본문이 막혀 있다고 믿게 해서, 스스로 조심할 근거가 약해진다 | `disallowedTools: Edit, Write, NotebookEdit` 복구, 또는 괄호 문구 삭제 후 행동 규칙으로 기술 | 재확인, **P0 적용(본문 수정)**. 복구는 보류 (03-analysis §3) |
| High | project-initializer.md:40-41, :32; git-workflow.md:43, :65; insight-analyst.md:27, :39; business-panel-experts.md:28; learning-guide.md:63; frontend-architect.md:38 | "Present interactive task menu… Accept user selection", "asks confirm, runs commit", learning-guide:63 "validates prior knowledge before each step" | 서브에이전트는 실행 도중 사용자 답을 받을 수 없다. 모델은 ① 메뉴나 초안만 반환하고 끝내거나 ② 선택과 확인을 스스로 가정하고 진행한다. ②는 Ask First 위반이다 | "서브에이전트로 실행되면 제안과 선택지를 반환하고 종료한다. 부모 요청이 명시적이면 그것을 확인으로 본다"는 분기 추가 | P1 |
| High | project-initializer.md:3 vs :84 vs :95 | "Use proactively when entering a new repository" / 예시 "runs structure-analysis, claude-md…together" / "never auto-execute without menu" | 첫 턴에 자동 호출되어 사용자의 실제 요청을 가로챌 수 있다. 예시가 bounds를 직접 위반하고, 모델은 예시를 따른다 | proactive를 제거해 명시 호출 전용으로. 예시는 "메뉴와 추천 프리셋 반환"으로 수정 | 재확인. **예시는 P0 적용**, proactive 제거는 P1 |
| High | python-expert.md:3; project-manager.md:3; 12개 모두 | "Use proactive for Python impl", "Use proactively after implementations" | Python 저장소에서는 거의 모든 구현이 위임되어 부모가 맥락을 잃는다. 구현이 끝날 때마다 PM이 문서를 바꾼다. 모든 agent가 proactive라서 우선순위 신호로 작동하지 않는다 | proactive는 2-3개로 제한하고 "Do NOT use for…"(단순 수정, 단일 파일) 추가 | P1 |
| Med | backend-architect.md:67-68; frontend-architect.md:71-72; project-initializer.md:89-90 | "superclaude = content framework… SC CLI use Click", "no-frontend-on-sc", "make deploy" | 다른 사용자 프로젝트로 배포된다. "SC"가 무엇인지 정의되지 않아 잡음이 되고, 사용자 CLI 조언을 Click/동기 쪽으로 편향시킬 수 있다 | 저장소 로컬로 이동하거나 조건 부여 | backend/frontend **P0 적용(조건 부여)**. initializer는 이미 조건이 있음 |
| Med | backend:67-68, business:78-79, deep:90, devops:68-69, frontend:71-72, learning:68, perf:67-68, initializer:88-90, pm:76, python:11, 68-69 | "[R06 Scope]", "[R02 Status Check]", "[R13 Intent Verification]" | 정의는 on-demand인 core/rules/RULES_QUALITY.md에만 있어 서브에이전트에서 해석되지 않는다. 본문 문장으로 의미는 대부분 통하지만 initializer:89-90은 R06을 도구 선택에 잘못 붙였다 | ID를 지우거나 한 줄 근거 문장으로 교체 | P1 |
| Med | business-panel-experts.md:28 vs :34, :57 vs :74 | "Debate: 2-4 opposing lenses" / "select 3-6 lenses" / 예시 "Porter vs Kim-Mauborgne" | 수치가 서로 모순되고, 렌즈 2개짜리 예시가 체크리스트(3-6개)를 위반한다. 출력 형식도 :36과 :44-46 두 가지가 공존한다 | 모드별 렌즈 수를 정하고 출력 스펙을 하나로 통일 | P1 |
| Med | devops-architect.md:49; frontend-architect.md:50; learning-guide.md:47 | "rehearsed at least once", "Core Web Vitals targets met: LCP under 2.5s", "Working examples tested" | 서브에이전트가 검증할 수 없는 조건이다. 체크리스트를 채우려는 압력 때문에 "검증됨"을 거짓 보고할 위험이 있다 | "측정했으면 수치를, 아니면 '미검증'이라고 쓸 것" | P1 |
| Med | project-manager.md:30 vs :48, :22 | "write to docs/memory/patterns/" / Ask First "create docs/memory/patterns/" / "Session start: read prior context" | 구현 후 proactive 호출과 Ask First가 충돌해 멈추거나 무시하게 된다. 세션 중간에 생성된 서브에이전트에게 "Session start" 생애주기는 무의미하다 | 실행 위치(메인 스레드 / 서브에이전트)별로 절을 분리 | P1 |
| Med | git-workflow.md:17, :30 | "context load via `--from-pr`" | 실제로는 `claude --from-pr`(CLI 플래그, commands/git.md:52)다. 모델이 `gh`/`git`에 이 플래그를 지어내 붙일 수 있다. 상태값도 :30 REVIEW_REQUIRED, :36 pending, :66 PENDING으로 섞여 있다 | `gh pr checkout <n>`으로 명시하고 상태값 통일 | P1 |
| Med | frontend-architect.md:38, :15/:49/:77 | "Forbidden defaults: Inter/Roboto/Arial/system fonts", "WCAG 2.1 AA" | 절대 금지라서 기존 디자인 시스템이 Inter를 써도 거부할 수 있다. 대시보드나 개발 도구에는 시스템 폰트가 적절한 경우가 많다. 현행 WCAG는 2.2다 | "기존 디자인 시스템이나 사용자 지정이 없을 때만" 조건 추가, 2.2 AA로 갱신 | P1 |
| Low | deep-researcher.md:25, :27/:43 | "planning-only, intent-planning, unified", "RESEARCH_CONFIG.md" | 세 용어는 `modes/RESEARCH_CONFIG.md`의 `<strategies>` 표(:19-21)와 :7에 정의되어 있지만, agent 본문은 그 파일의 경로를 주지 않아 서브에이전트가 찾지 못한다(본문에 등급 정의가 있어 피해는 작다) | 정의하거나 삭제, 파일 참조 제거 | P2 |
| Low | insight-analyst.md:3 vs :40; :27, :67 | "Use proactively…" / "Never: auto-trigger on session start"; "`--stats`" | proactive와 자동 트리거 금지가 긴장 관계다. annotation 스키마는 ref_ts만 있어 다른 필드를 지어낼 수 있다. `--stats`의 출처가 불명확하다 | 필수 필드(type/text/ts/author) 명시, `/sc:insight --stats`로 표기 | P2 |
| Low | python-expert.md:64 vs performance-engineer.md:63; learning-guide.md:67 | "optimize slow database queries"; "check user memory for expertise" | 두 agent의 라우팅이 겹친다. 서브에이전트는 agent memory만 볼 수 있어서 "user memory"가 무엇을 가리키는지 불명확하다 | python 예시 교체, "agent MEMORY.md / 부모가 전달한 맥락"으로 수정 | P2 |
| Low | git-workflow.md:3, :29; learning-guide.md:3 | "user wants learn concept", `<safety_rules>`(내용은 PR 연동) | 라우팅 표면의 문법이 생략되고 태그 이름이 오해를 부른다. 해석은 되지만 신호가 약해진다 | description은 완전한 문장으로, 태그는 `<pr_integration>`으로 | P2 |

## 공통 패턴

- **대화형 설계를 단발 서브에이전트에 이식:** 6개 파일이 해당한다. 근본 원인은 "Ask First"가 실행 중에 사용자에게 묻는 것을 전제한다는 데 있다. 서브에이전트에서는 "보고 후 종료"가 되어야 한다.
- **절대 표현의 누적:** `Never:` 목록, "Use proactively" 12개, "Forbidden". 근거 없는 것이 많아 문자 그대로 적용될 위험이 있다. 예외 근거를 단 곳은 git default-branch-warn의 "Not a block; the user may have reason" 정도이며, 좋은 모범이다.
- **체크리스트가 행동 대신 주장을 요구:** 측정할 수 없는 항목이 있으면 모델은 "완료"라고 말하는 쪽으로 기운다.
- **`<handoff next="/sc:…">`:** `<handoff next>`의 16개 명령(본문에만 나오는 `/sc:pm` 포함 시 17개)이 모두 실재한다. 서브에이전트가 직접 실행할 수는 없지만, 부모에게 넘기는 메타데이터로서는 해가 없다.

## 강점

- Proceed / Ask First / Never 3단 구분이 일관되고 구체적이다. 예: backend ">2 tables", git의 fetch 범위.
- frontend description의 "perf optimization belongs to performance-engineer"는 경계를 명시적으로 나눈 사례다. project-manager는 서브에이전트로는 오케스트레이션할 수 없다는 제약을 description에 밝혀 둔다.
- memory_guide의 "verify against current state", "only if a future run would act differently"는 오래된 기억을 따르는 실수와 기록 남발을 잘 막는다.
- 예시가 출력 문장이 아니라 행동 기술이라 그대로 베낄 위험이 낮다. deep-researcher의 "never average"처럼 근거가 붙은 규칙이 좋다.
- 교차 참조한 agent 이름과 `/sc:` 명령은 모두 실재한다.
