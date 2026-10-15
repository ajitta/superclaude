# 09 — P0 수정 리뷰와 반영

P0 커밋 `aa5b0e87`(content)과 `1ff751be`(docs)를 서로 독립된 서브에이전트 두 개가 리뷰했다.

- **리뷰어 A — 수정 검토.** 받은 것: 사용자 요청 원문, 각 수정이 해결해야 할 문제(수용 기준), 저장소 작성 규칙의 위치. 받지 않은 것: 수정 근거와 자체 평가.
- **리뷰어 B — 문서 사실 검증.** 문서의 인용·줄 번호·수치를 커밋 `0c63688d` 원문과 대조했다.

리뷰어가 보고한 주요 사실(정규식, 줄 위치, 형제 파일의 순서 규칙, verifier의 호출 조건)은 오케스트레이터가 원문에서 다시 확인했다.

## 리뷰어 A: 수정별 판정

수정 9건 중 해결 5, 부분 해결 4, 퇴행 0이었다. 대신 **새 문제 1건(High)**이 나왔다.

| # | 판정 | 지적 | 반영 |
|---|---|---|---|
| 1 security | 부분 | "the target repo is superclaude itself"는 관찰할 수 없는 조건이다. 사용자 프로젝트에도 `.claude/superclaude/`가 설치되므로 오적용될 수 있다. "Every other repo gets the full review"는 지정된 범위(R06)를 넘을 수 있다 | 조건을 관찰 가능한 형태로 바꿨다: "root `pyproject.toml` has `name = "superclaude"`; a copy installed under `.claude/` does not count". 끝 문장은 "Other repos get the normal review of the named scope, web vulnerabilities included [R06 Scope]" |
| 2 backend/frontend | 부분 | 같은 조건 문제 | 같은 조건으로 변경 |
| 3 git-workflow | 해결 | "nothing in the tool settings blocks Edit or Write"는 유지보수자 대상 설명이고, 모델에게는 "써도 된다"는 신호로 읽힐 수 있다 | "editing is outside this agent's job; file changes belong to the user or the implementing agent"로 변경 |
| 4 self-review | 부분 | `--agent` 모드에서는 Agent 도구로 테스트 실행을 위임할 수 있는데, "cannot run tests"가 그 경로를 막는다. 리뷰어는 verifier 위임을 제안했다 | "The agent's **own** tools cannot run tests"로 한정해 위임 경로를 열어 두었다. verifier 위임은 반영하지 않았다: verifier description이 "Use when the user explicitly asks"라서 자동 위임이 그 라우팅 조건과 충돌한다 |
| 5 project-initializer | 해결 | "onboarding preset"이 어디에도 정의되지 않아 모델이 지어낼 수 있다 | 정의되지 않은 용어를 삭제 ("preselected"만 남김) |
| 6 Business_Panel | 부분 | 아래 "새 문제" 참조 | 아래 참조 |
| 7 VS | 해결 | "(CoT adds a brief **Reasoning** line)"의 위치가 모호하다 | "CoT puts a brief **Reasoning** line before the text."로 명시 |
| 8 quality.md | 해결 | — | — |
| 9 PRINCIPLES | 부분 | "proceed when the step is reversible"이 먼저 나와서, 가역적이면서 >3 files인 작업에 진행·질문 조건이 동시에 걸린다. R12의 "minimal change, surface diff"도 빠졌다 | 순서를 바꿨다: ask-first 조건을 먼저 쓰고 "otherwise proceed with the smallest change and show the diff". 모호 시 질문을 기대하는 eval은 없음을 리뷰어가 확인했다 |

### 새 문제 (High): Business_Panel 출력 순서

P0는 예시를 규칙 :20 "Synthesis-First: Integrate across frameworks before show individual views"에 맞춰 Synthesis를 앞에 두었다. 그런데 다른 곳은 모두 Synthesis를 **마지막**에 둔다.

- 같은 파일의 Discussion 흐름(Insights → Cross-pollination → Synthesis)
- `agents/business-panel-experts.md:36`(Panel → Synthesis → Next Steps)
- `core/BUSINESS_SYMBOLS.md`의 Debate 템플릿(Resolution → Solution)
- `commands/business-panel.md`의 flow(Analyze → Synthesize → Present)

결과적으로 충돌이 모드 파일 안에서 모드와 형제 파일 사이로 옮겨갔을 뿐이다. Socratic 예시에서 결론을 먼저 말하는 것도 질문 주도 흐름을 깬다.

`git log -S`로 보면 규칙 :20과 원래 예시는 같은 커밋(`4229ecb0`)에서 함께 들어왔다. 그래서 어느 쪽이 의도인지 이력으로는 판단할 수 없다. **다수 관례(Synthesis는 마지막)를 택했다.**

- 규칙 :20을 "Synthesis-Driven: Integrate across frameworks while analyzing, so each lens section feeds one conclusion; the output closes with that synthesis"로 바꿨다. 통합은 분석 과정에서 하고, 출력은 종합으로 끝난다는 뜻이다.
- 두 예시를 Synthesis가 마지막에 오도록 다시 썼다.
- 페르소나 서술("Porter takes a position")을 렌즈 서술("the Five Forces lens (Porter) argues")로 바꿨다. `<never>expert persona impersonation`과의 긴장을 없애기 위해서다.

이 선택은 규칙 문구를 바꾼다. 의도가 반대였다면(출력을 종합으로 시작) 형제 파일 4곳을 고치는 쪽이 맞다.

### 반영하지 않은 지적

| 지적 | 사유 |
|---|---|
| 렌즈 수 불일치: 예시 2개, BUSINESS_SYMBOLS `min=3`, agent "3-6" (Med) | 모드 자체 규칙(:18 "Apply 2-3 frameworks", 라우팅 표의 전문가 2명)과는 맞는다. 원래부터 있던 형제 파일 간 불일치이므로 P1로 기록 |
| 저장소 전용 gotcha 6건을 `.claude/rules/gotchas/`로 이동 (Low) | 서브에이전트는 본문만 받는다(`agent-authoring.md`). 옮기면 superclaude 저장소 안에서도 효과가 사라진다. 관찰 가능한 조건을 붙인 채 유지 |
| `MODE_Introspection.md:9`의 "Check vs superclaude standards" (Low) | P1 후보로 기록 |
| self-review :72 premature-approval과 :70의 중복 | 이번 수정 범위 밖. P2로 기록 |

## 리뷰어 B: 문서 사실 검증

인용과 줄 번호 약 150건을 `0c63688d` 원문과 대조했다. 약 143건이 정확했다(±2줄 허용). 테스트 수, author-check, lint, 커밋 이력, 규칙 인용은 모두 일치했다.

다음 오류를 문서에 직접 정정했다.

| 문서 | 오류 | 정정 |
|---|---|---|
| 03-analysis §1 | agents의 R-ID 태그 "약 60회, R06 25회…"는 core 정의 줄까지 함께 센 값이다 | 44회, R06 22 / R02 7 / R15 5 / R18 5와 재현 명령 |
| 03-analysis P-1 | "caught 3 critical reversals"의 출처 파일이 틀렸다 | `RULES_DOCS.md:74`로 정정. RULES_DELEGATION:15,25는 실제 문구로 교체 |
| 03-analysis P-6 | `TestAgentDescriptionInterface`도 바꿔야 한다고 썼다 | 테스트 정규식이 "Use when"을 이미 허용한다(:68). 규칙 문서만 개정하면 된다 |
| 03-analysis P-3, §3 | simplicity-guide 재평가 근거가 부정확했다 | Spawn restrictions 절(`--agent` 모드에서만 효력)로 근거를 교체. Web 도구 부재는 남은 문제로 명시 |
| 03-analysis §4 | 03a 커널 R-ID(High), 03b VS 템플릿 모호성(High), 03e Fable 미인용 문안(High)이 누락됐다. High 항목이 "Med 항목"으로 묶여 있었다 | P1 11번으로 High 미처리 항목을 분리하고 커널 R-ID를 7번에 추가. verifier 예시를 10번에 추가 |
| 03-analysis, README | "현행 모델은 예시를 우선 모방한다" 등을 측정하지 않았는데 단정했다 | 추정·판단으로 표시 |
| 03a | context_loader 트리거가 명령·플래그에"만" 반응한다고 썼다 | "대부분"으로 완화하고 자연어 트리거 예를 추가. RULES_QUALITY는 명령·플래그 전용이라 결론은 유지 |
| 03a | ultracode 출처, user 범위 설치 경로의 인용 | 정정 (`context_loader.py:84-85`) |
| 03c | 원문에 없는 문구 "question progression adapts to user"를 인용했다 | learning-guide:63 원문으로 교체 |
| 03c | planning-only 등이 "미정의"라고 썼다 | RESEARCH_CONFIG.md에 정의되어 있다. 문제는 경로가 없다는 것으로 정정 |
| 03c | handoff 명령 17개 | 16개 (`/sc:pm`은 본문에만 등장) |
| 03c ↔ 03d | 같은 항목의 심각도가 문서마다 달랐다 | 통일: backend/frontend 누수 Med, 서브에이전트 Ask First High, agent R-ID Med |
| 03e | Playwright 예시 수, `Never` 횟수, 의역 인용 | 6개 중 3개, 6회(대문자 2), 원문 인용으로 정정 |
| 08 | quality.md 변경 설명, "새 규칙 없음" | Sonnet 판정은 기존 문구였다. PRINCIPLES는 R12를 커널로 복제한 새 규칙이라고 명시 |
| README | 재확인 High 10건 | 11건 |

## 검증 (리뷰 반영 후)

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` | 3415 passed, 3 skipped |
| `uv run superclaude author-check src/superclaude/skills/sc-author/references/quality.md` | 0 errors, 0 warnings |
| `make lint` | All checks passed |
| 바뀐 규칙명 "Synthesis-First"와 옛 조건 문구 잔존 (`git ls-files` 전체 grep) | src에는 없음. 이 폴더 문서의 인용(감사 시점 원문, 1차 수정 기록)에만 남아 있으며, 이력 기록이므로 유지 |

core(`PRINCIPLES.md`)가 다시 바뀌었으므로 릴리스 전 `make canary-gates`가 필요하다는 점은 08과 같다.
