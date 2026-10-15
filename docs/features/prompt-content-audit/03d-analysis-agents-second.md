# 03d — agents 후반 12개 감사 + 라우팅 충돌

**대상**
- `agents/` 아래 12개: quality-engineer, refactoring-expert, repo-index, requirements-analyst, root-cause-analyst, security-engineer, self-review, simplicity-guide, socratic-mentor, system-architect, technical-writer, verifier
- `agents/README.md`
- 라우팅 충돌 비교에는 24개 전체의 description을 썼다.

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- verifier, self-review, root-cause-analyst는 출력 형태와 종료 조건이 분명해서 현행 모델이 거의 의도대로 따를 것이다.
- High 위험:
  - superclaude 자체에 대한 gotcha가 사용자 프로젝트로 배포된다. security-engineer의 웹 취약점 스캔 생략 지시가 대표적이다.
  - 일부 본문 지시를 tools 설정으로는 수행할 수 없다(Bash 없음).
  - 대화형 agent가 단발 서브에이전트로 실행된다.
- 라우팅: "Use proactively / immediately after"가 구현 직후와 auth 작업에 몰려 있어 여러 agent가 동시에 호출된다.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 | 제안 | 상태 |
|---|---|---|---|---|---|
| High | security-engineer.md:71-72 | "superclaude = markdown content framework, not web app — skip web-vuln scans" | 조건이 없어서 사용자의 웹앱에서도 OWASP/웹 취약점 스캔을 건너뛴다. :49 체크리스트 "OWASP Top 10 reviewed"와 정면으로 충돌한다 | 삭제하거나 "when the target repo is superclaude itself"로 조건 부여 (project-initializer:89처럼) | 재확인, **P0 적용** |
| Med | (전반부) backend-architect.md:67-68, frontend-architect.md:71-72 | "SC CLI use Click…", "no-frontend-on-sc" | 같은 누수 패턴이다. 사용자 프로젝트에서는 무의미한 토큰이고 잘못 일반화될 위험이 있다 | 조건 부여 또는 저장소 로컬 규칙으로 이동 | **P0 적용** |
| High | self-review.md:6 vs :44, :65, :70 | `tools: Read, Grep, Glob, Agent` / "'42/42 pass' requires running tests" | Bash가 없어 테스트를 실행할 수 없다. 모델은 UNVERIFIED를 남발하거나 부모가 전한 주장을 증거로 받아들인다 | 테스트 실행은 verifier 담당으로 명시하거나 읽기 전용 Bash 허용 | 재확인, **P0 적용** (출력이 손에 없으면 UNVERIFIED라고 명시) |
| High → Low | simplicity-guide.md:6, :55, :86, :91 | "docs check delegated via Agent" | 서브에이전트는 하위 서브에이전트를 띄울 수 없고 WebSearch/WebFetch도 없다 | tools에 Web 계열 추가, 또는 "서브에이전트 모드에서는 unverified로 보고"를 기본으로 | **재평가로 강등**: `--agent` 모드의 정식 패턴이고 :55에 "else reports it unverified"가 이미 있다 (03-analysis §3) |
| High | socratic-mentor.md:22-27, requirements-analyst.md:24 | "Lead with observation questions…", "Drive structured discovery questions" | 서브에이전트는 요약 하나만 반환한다. 다회차 문답이 불가능해 답을 지어내거나(:42 "assume unstated reqs" 금지 위반) 질문 목록만 반환한다 | description에 "invoke via `claude --agent` / main thread"(project-manager 방식)를 넣거나 "질문 목록 반환 후 종료"를 명시 | P1 |
| Med | repo-index.md:22 vs :66, :29-30 vs :65 | "under 7 days old, confirm + stop" vs "always regen… never reuse cached" | 내부 모순이라 7일 이내 인덱스를 다시 만들지 모델이 임의로 고른다. 출력 경로도 :30은 미지정, :65는 docs/reports/로 엇갈린다 | "fresh면 재사용하되 내용은 기억이 아니라 파일을 다시 읽어 확인"으로 정리하고, 경로를 docs/reports/PROJECT_INDEX.*로 명시 | P1 |
| Med | technical-writer.md:3 vs :67 | "Use proactive for… READMEs" vs "no make README.md… unless asked" | description은 README를 선제적으로 만들라고 하고 본문은 금지한다 | description을 "Use when the user asks to write or update docs"로 | P1 |
| Med | socratic-mentor.md:3 vs :62 | "direct explanation… belongs to learning-guide" vs 예시 "teach me SOLID" | 예시가 description의 경계와 반대라서 learning-guide 영역을 침범한다 | 예시를 "quiz me toward SOLID" 류로 교체 | P1 |
| Med | quality-engineer.md:38, security-engineer.md:38, self-review.md:37 | "never pre-filters under guidance like 'focus on real issues'" | 사용자가 "critical만"이라고 명시해도 무시하는 것으로 읽힌다. 직접 호출하면 걸러 줄 후속 단계가 없어 사소한 지적까지 목록으로 쏟아진다 | "사용자가 범위를 명시하면 따르고 제외한 건수만 보고" 예외 추가 | P1 |
| Med | refactoring-expert.md:23, :48 | "Grab baseline complexity metric", "Post-change metric better than baseline" | 측정 도구가 지정되지 않았는데 개선을 요구한다. 모델이 cyclomatic 수치를 지어낼 위험이 크다 | 도구(radon/lizard 등) 실행 출력만 인정, 없으면 "estimated" 표기 | P1 |
| Med | refactoring-expert.md:40 vs :77 | "3+ files" vs "3+ modules" | Ask First 기준이 다르다 | 하나로 통일 | P1 |
| High | 공통: Ask First / "ask user" (12개 전부) | "Ask First: modify CI/CD…", "ask user when…" | 서브에이전트는 실행 중에 물을 수 없다. 멈출지, 진행할지, 무엇을 반환할지 정의되어 있지 않다 | 공통 한 줄: "Ask First에 해당하면 제안 행동과 질문을 최종 보고에 담고 중단" | P1 |
| Med | 전보체: technical-writer.md:3, :10-11 / socratic-mentor.md:3 / security-engineer.md:3 / root-cause-analyst.md:3 / simplicity-guide.md:12 | "Technical writer make clear, full docs", "Claude no simplify what no understand" | 뜻은 대체로 복원되지만, 사용자용 문서나 PRD, 학습 대화가 깨진 문장으로 나올 위험이 있다. verifier, system-architect와 문체가 다르다 | 사용자 대면 출력을 내는 agent부터 정상 문법으로 | P2 |
| Low | technical-writer.md:68 | "core/rules/RULES_DOCS.md" | 사용자 프로젝트의 서브에이전트에서는 경로가 해석되지 않는다(규칙 내용이 인라인되어 있어 피해는 작다) | 경로 참조 삭제 | P2 |
| Med | [R06]·[R15] 등 22곳 이상, socratic-mentor.md:39 [R17] | "[R06 Scope]" | 서브에이전트에서 해석되지 않는 태그다. 대부분 문장 자체가 뜻을 담아 무해한 잡음이다 | 유지하거나 제거로 토큰 절약 | P1 (03-analysis P-5) |
| Low | verifier.md:3, :64-66 | 4문장 description / "foo-ajitta-2026-10-07.md", "intent-command" | description이 길지만 부정 조건 덕분에 라우팅 품질은 높다. 예시는 저장소 고유 이름이다 | 예시를 `<slug>` 등으로 일반화 | P1 |

## 라우팅 충돌

- **auth 집중:** 같은 auth 작업에 6개 agent가 걸린다.
  - security-engineer("Use immediate after impls touch auth… input boundaries")
  - system-architect의 auth 예시, quality-engineer의 auth 예시
  - simplicity-guide의 "build user authentication", self-review의 "review my auth implementation"
  - backend-architect
  - 특히 "input boundaries"는 거의 모든 엔드포인트에 해당해 과호출된다.
- **구현 직후 동시 호출:** quality-engineer("immediately after new behavior added"), refactoring-expert, security-engineer, project-manager("proactively after implementations"). 기능 하나에 3~4개가 붙는다.
- **구현 전 단계:** simplicity-guide("before code is written", "dependency added"), system-architect("technology selection"), requirements-analyst("direction fuzzy"), backend("schema decisions")가 겹친다.
- **세션 시작:** repo-index("at session start when project context unclear"), project-initializer("entering a new repository"), 내장 Explore가 겹친다.
- **refactoring vs simplicity:** 둘의 구분(simplicity-guide.md:21)이 본문에만 있어 부모에게는 보이지 않는다. description에 preventive(예방) / curative(치료) 구분을 넣어야 한다.
- **테스트:** quality-engineer에 "not for running/verifying" 같은 부정 조건이 없어 verifier와 겹친다.
- **기타:** CI/CD는 quality-engineer의 "CI/CD test gates"와 devops-architect가 겹친다. 이해관계자 조율은 requirements-analyst와 business-panel-experts가 겹친다.

## 공통 패턴

- 24개 중 21개가 "Use proactive/immediately"를 쓴다. 현행 모델은 이를 문자 그대로 따르고, 트리거가 겹치니 과잉 위임이 된다. "Use when the user asks…" + "Not for…"(verifier 방식)로 낮추기를 권한다.
- README와 description이 어긋난다: README.md:71은 "Post-impl validation"인데 self-review description은 "any work product, explicit only"다.
- README.md:122의 "context >85%"는 agent가 측정할 수 없는 조건이다.
- README.md:128-135의 충돌 해소표에는 위 충돌이 하나도 없다.
- README.md:7의 "Auto-pick from task keywords"는 명시 호출 전용 agent(verifier, self-review)와 맞지 않는다.

## 강점

- **verifier:** 부정 라우팅이 명확하고 MATCH/MISMATCH/UNVERIFIED로 판정한다. diff와 untracked 파일 해시로 "편집 없음"을 검증하고, 똑같은 재시도를 금지한다.
- **self-review:** "silent PASS" 대신 UNVERIFIED를 쓰게 강제한다.
- **root-cause-analyst:** 가설 3사이클 상한(exploration_budget)이 있다.
- **simplicity-guide:** domain_exceptions에 근거가 함께 적혀 있다.
- **공통:** bounds의 does/never/fallback 구조가 일관되고, 메모리 기록 조건 "only if a future run would act differently"가 적절하다. handoff의 `/sc:` 명령은 전부 실재한다.
