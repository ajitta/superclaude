# 09b — 3차 수정 독립 리뷰

리뷰어 3명이 커밋을 나눠 읽기 전용으로 검토했다. 수정 근거는 주지 않고 감사 결과(03a–03f, 08a 보류 목록)를 수용 기준으로만 전달했다. 반영은 `5bf1f22e`에서 했다. 리뷰어가 인용한 줄은 오케스트레이터가 원문에서 다시 확인했다.

- 리뷰어 A: `df0b8738`(core·loader), `1172b4fb`(modes)
- 리뷰어 B: `61b4d570`(agents)
- 리뷰어 C: `ae4b42ac`(commands·작성 규칙), `8b3eb320`(mcp·sc-prompt), `b79567ca`(sc-author)

## 판정 요약

대부분 해결로 판정됐다. 리뷰어 B는 24개 agent의 모든 hunk를 읽었고, description이 바이트 단위로 같음을 확인했다. 리뷰어 C는 문법 재작성 약 45문장을 표본으로 봤고, 의미가 바뀐 곳은 1건이었다.

## 지적과 반영

| 심각도 | 지적 | 반영 |
|---|---|---|
| High (새 문제) | Ask First 문장의 "unless the task text already names that action"이 부모의 문장만으로 파괴적 작업을 허용한다. RULES.md destructive_op_confirmation과 충돌 | task text는 대상이 명시된 가역적 행동에만 확인이 된다. 파괴적·비가역적 행동은 사용자 승인 인용 필요 |
| Med (누락) | 20개 `<fallback>`의 "ask the user", root-cause·simplicity의 질문 단계는 문장 범위 밖 | 문장 범위를 "wherever this file says to ask or confirm"로 넓힘 |
| Med (새 문제) | 핵심 산출물이 Ask First에 있어 서브에이전트가 산출물 없이 멈춘다 (requirements 우선순위, security 권고, learning 경로) | 제안은 Proceed, 확정·적용만 Ask First. 작성 규칙에도 추가 |
| Med (새 문제) | git-workflow의 commit 예시와 체크리스트가 서브에이전트 규칙과 어긋남 | 예시와 체크리스트에 서브에이전트 분기 |
| High (새 문제) | sc-prompt SKILL.md:32의 이월 예외가 금지 규칙을 다시 연다(Opus 5.5 행 11개 전부 이월) | 이월 행은 적용하지 않고 후보로 보고. Opus 5.5 self-check 삭제도 후보로 |
| Med (의미 변화) | brainstorm `<does>` "self-review precede impl handoff"가 "runs a self-review"로 바뀌어 :18 "/sc:review 대신 스스로 리뷰하지 않는다"와 충돌 | "routes the spec to /sc:review before the plan handoff" |
| Med-High (새 문제) | FLAGS의 "When one fits … Read the MODE file"이 약한 신호로 모드 파일을 읽게 한다. `<Name>` 추측도 실패 | 설명은 트리거가 아님. 플래그 없으면 한 줄 제안만. 플래그를 입력했는데 본문이 없을 때만 Read. 파일 이름 목록 |
| Med (새 문제) | loader 트리거가 CLAUDE.md 단순 언급에도 RULES_DOCS를 주입. canary sc-author-memory 쌍의 비교 기준을 바꿈 | 쓰기 동사 + 파일 이름일 때만. 음성 테스트 4건 |
| Med (새 문제) | Orchestration의 "min(16, cpu-2), both in core/FLAGS.md"가 삭제된 FLAGS 내용을 가리킴 | 하네스 자체 한도로 서술 |
| Low-Med (새 문제) | R15가 🟡가 되어 커널 "Never claim…"과 등급이 충돌 | 범례에 "커널 규칙은 표시와 무관하게 적용" |
| Low-Med (새 문제) | --validate/--safe-mode 조건이 관찰 가능해져 모델이 스스로 켤 수 있다(canary destructive-named-path 위험) | execution 첫 줄에 "사용자가 입력할 때 효력" |
| 부분 | RULES.md Intent Propagation의 verbatim과 제외가 여전히 나란히 있음 | 마커 치환을 커널에 명시 |
| 미해결 | `/sc:research` 기본 unified가 명확한 질의를 승인 대기로 멈춤 | 질의 명확도로 선택 |
| 부분 | tier-1 단일 출처 예외가 replan에만 있고 gates·DeepResearch에는 없음 | 두 곳에 추가 |
| 부분 | fallback이 붙여넣은 텍스트 속 플래그를 다루지 않음 | quoted/pasted/code 텍스트 포함 |
| 미해결 | Business_Panel의 market(Discussion) ↔ 라우팅 표(Debate), 2-3 ↔ min=3 | 라우팅 표가 우선. 전문가 수 2-3으로 통일, innovation 행에 Taleb |
| Low | RULES.md "text-only" 범위, 컨텍스트 수치 추정 금지, FLAGS 요약 범위, RULES_DOCS loading 설명, 측정 불가 체크리스트(frontend·security), PROJECT_INDEX 경로, business-panel 예시, backend 문법, Playwright fallback, sc-author 무선택 기본값, review step 8 전보체, brainstorm gotcha | 모두 반영 |

## 반영하지 않은 지적

| 지적 | 사유 |
|---|---|
| Opus 5의 `reasoning_extraction` 범주 | 이후 사용자 결정으로 반영(08b 주요 결정). What's new in Opus 5.5의 "As on Claude Opus 5" 문장이 근거 |
| commands의 남은 축약, pm description의 Direct 전략, implement.md의 `[R02 Status Check]` | Low. implement는 메인 스레드이고 `/sc:implement`가 RULES_QUALITY를 주입하므로 태그가 해석된다 |
| `.claude/agents/frontend-architect.md`(설치본)에 WCAG 2.1 | 설치본은 추적되지 않음. `make sync-local` 대상 |

## 병합 전 최종 리뷰

브랜치 전체(`master..HEAD`)를 리뷰어 3명이 최종 상태 기준으로 다시 봤다(core·modes·loader / agents / commands·skills·docs). 세 명 모두 "수정 후 병합", Blocker·High 없음. 반영한 지적:

| 심각도 | 지적 | 반영 |
|---|---|---|
| Med | 고정 Ask First 문장의 "ask or confirm"이 '검증'의 뜻인 confirm(테스트로 확인 등)까지 멈춤 지점으로 만듦 | "ask the user or get the user's confirmation"으로 좁힘(24개 agent, 테스트, 작성 규칙) |
| Med | system-architect의 핵심 산출물(제안)이 Ask First에 남음; simplicity-guide 체크리스트의 "confirmed before any rec" | 적용만 Ask First, 제안은 산출물. 체크리스트는 "restated", 사용자 확인은 메인 세션에서 |
| Med | `/sc:research` 경로에서 단일 출처 예외가 MODE·RESEARCH_CONFIG에만 있고 command·agent에는 없음; "tier-1" 정의가 표와 괄호에서 다름 | 예외를 "primary source (공식 문서·명세·1차 기록)"로 이름 붙여 research.md, deep-researcher, MODE, RESEARCH_CONFIG에 통일 |
| Med | sc-prompt 이월 행 규칙에 대상 조건이 없어 Opus 5 자신의 delta까지 막힘 | "For a 5.5 target …; for 'claude-opus-5' the Opus rows apply as written" |
| Med | design을 거치면 plan이 draft discovery를 검사하지 않아 review 게이트 우회; README 체인이 brainstorm→design→review | plan은 출처와 무관하게 폴더의 draft discovery에서 멈춤. README 체인을 brainstorm→review(spec)→design→plan으로 |
| Med | review step 8이 delegated 행만 리뷰해 전체 리뷰 없이 Spec gate 통과 가능 | "in addition to the Review step" |
| Med | root README의 research 기본 전략(unified), --validate 기준(risk > 0.7), --task-manage, estimate, index-repo 94% | 현재 동작으로 갱신 |
| Low | loader 트리거가 `~/.claude/CLAUDE.md`, `./CLAUDE.md`를 놓침(점이 든 경로) | `(?:[^.\n]|\.(?=\S))`로 경로 안 점 허용, 양성 테스트 2건 |
| Low | BUSINESS_SYMBOLS의 삭제된 `max=5` 참조, market_entry 순서와 primary pair | 정리, "primary pair = 행의 처음 두 명" |
| Low | core/README·agents/README·commands/README 설명, docstring의 Opus 5 `bio` 단정, VS "goes in the prompt", project-manager의 `/sc:pm` 본문 로드 주장, repo-index 재편 후 신선 인덱스, verifier description 4문장, `omitClaudeMd` 템플릿 누락, review handoff에 `/sc:plan` 없음, cleanup 확인 단위, 테스트 상수 위치, root README의 RULES_DELEGATION 매트릭스 참조, 이 README의 "P1·P2 남음" | 모두 반영 |

## 검증 (반영 후)

`uv run pytest -q` 3539 passed, 3 skipped. scripts 149 passed. lint 통과.
