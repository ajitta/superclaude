# 03h — `.claude/rules/` 저장소 작성 규칙·gotchas 감사

## 대상과 성격

**대상**
- `.claude/rules/` 아래 9개: `{agent,command,mode,mcp,skill,output-style}-authoring.md`, `xml-prose-format.md`, `content-quality.md`, `schemas.yaml`
- `.claude/rules/gotchas/` 아래 4개: `{general,authoring,hooks,README}.md`

**성격**
- 배포되지 않는다.
- 이 저장소를 유지보수하는 에이전트가 배포 콘텐츠를 작성할 때 보는 규칙이다.
- `paths:`가 있는 파일은 해당 경로를 편집할 때만 로드된다. `gotchas/general.md`는 `paths:`가 없어 매 세션 로드된다.

**감사 방법**
- 1차 감사에서는 격리 원칙에 따라 제외했고, 이번에 별도로 감사했다.
- 감사자 3명이 맡았다: authoring A, authoring B, gotchas.
- 감사 시점은 커밋 `9a247cb6`이다.

**수정 커밋**
- `72445b09`: 의미 수정과 gotcha 정리
- `3d1475ce`: 전보체 문법 복원. 의미는 바꾸지 않았다.

## 요약

- 형식 규칙은 실제 콘텐츠와 잘 맞는다.
  - 단일 루트 80/80
  - snake_case 위반 0
  - 크기 목표 초과 0
  - 모드 4축 8/8
  - Symbolic-First 분류 일치
- 문제 1: 규칙이 실제 동작을 틀리게 설명한다.
  - MCP 문서는 기본 설정에서 본문이 주입되지 않는다.
  - 의도적으로 제거된 maxTurns를 여전히 요구한다.
  - 서브에이전트가 core 규칙을 전혀 못 본다고 단정한다.
- 문제 2: 구세대 관행과 해로운 명령을 가르친다.
  - "Use proactively"를 정본 문형으로 가르친다. 배포된 에이전트 21/24가 이를 그대로 복제했다.
  - 동기화 방법으로 `install --force`와 `make deploy`를 안내한다.
- 문제 3: 커밋 `b196673b`의 "caveman" 압축 문체가 오독을 낳는다. 같은 문체가 배포 콘텐츠로 번졌다.
  - 예: "Technical writer make clear, full docs", "Plan doc make"

## 작성 규칙 발견사항

| 심각도 | 위치 | 근거 | 문제 | 처리 |
|---|---|---|---|---|
| High | mcp-authoring:101,24,103,119 | "INSTRUCTION_MAP: one-line summary … Claude read before body land" | `context_loader.py`는 기본 설정에서 이 문자열을 본문 **대신** 주입한다. tool MCP는 TIER_0_MAP을 쓴다. TRIGGER_MAP에만 등록된 파일은 Tier 2로 본문 전체가 주입되므로 "Unregistered files dead"도 틀렸다 | **적용**: tier 동작을 사실대로 기술 |
| High | agent-authoring:104-110, 252 | "Set `maxTurns`", 표 | 2718f713에서 모든 agent에서 의도적으로 제거했다(0/24) | **적용**: 표 삭제, 체크리스트에 "omit" 명시 |
| High | agent-authoring:26, 55-62, 250 | `description: Expert X. Use proactively for Y…` | 템플릿이 그대로 복제되어 라우팅 신호가 사라졌다. content-quality §1 "when THIS one and not the adjacent one?"과도 충돌한다 | **적용**: "Use when <구분 신호>" + "Not for …" 템플릿. proactive는 무요청 실행이 필요한 agent에만 |
| High | agent/mcp/xml 전반 | "Make agent for domain expertise that CC auto-delegate" 등 | 압축 문체가 배포 콘텐츠로 번졌다 | **적용**(3d1475ce): 문법만 복원. 배포 콘텐츠의 잔여 전보체는 P2 |
| High | command-authoring:49, :135 (+mode, mcp, agent 체크리스트) | "`superclaude install --force --scope user`", "Run `make deploy`" | `install --force`는 설치가 없는 곳에도 설치를 새로 만든다(gotcha sync-scope-creates). `make deploy`는 CLI만 설치한다 | **적용**: `superclaude doctor --scope <s>`를 먼저 실행하도록 하는 공통 문장으로 |
| Med | agent-authoring:12, 219, 234 | "core rules never reach them" | sc-author는 서브에이전트가 CLAUDE.md를 받을 수 있다고 쓴다(`omitClaudeMd` 필드). 규칙 자신도 R-ID를 허용한다 | **적용**: CLAUDE.md 전달 여부는 설정에 따른다고 쓰고, on-demand 모듈은 전달되지 않는다고만 단정 |
| Med | agent-authoring:83-89 | "Read-only + web … **preferred**", "(e.g., git-workflow)" | preferred 패턴을 쓰는 agent가 0/24다. git-workflow에는 tools 필드가 없다 | **적용**: "preferred"와 예시를 삭제하고 672055ce의 이유(MCP 상속 손실)를 명시 |
| Med | agent-authoring:159 | "- Ask First: actions requiring confirmation" | 서브에이전트는 사용자에게 물을 수 없다 | **적용**: 위임 실행이면 멈추고 '확인 필요'로 보고 |
| Med | agent-authoring:203 | "not instructions addressed to model" | 근거가 틀렸다 | **적용**: 저장소 관례(일관성)로 근거를 교체 |
| Med | agent-authoring:137-191 | "(3-5 items)", "(4-5 steps)" | 개수 할당이 채우기용 문장을 부른다(11개 섹션 24/24) | 보류(P1) |
| Med | mode-authoring:35-36, 55 | "directives joined by \" \| \"" | 축약체를 유도한다("Ask q's > give answers") | **적용**: 온전한 단어로, 약어 금지 |
| Med | mcp-authoring:80, 91 | Context7 resolve→get, token cap 예외 | MCP_Context7.md는 4aea453d에서 삭제됐다 | **적용**: 삭제 |
| Med | command-authoring:116-125 (+mode, mcp, agent) | "Inherited from xml-prose-format.md" | 같은 로드 세트 안에서 규칙이 6개 중복된다 | **적용**: 포인터 한 줄로 |
| Med | xml-prose-format:94, command:112, agent:200 | "session `S390`, not in git" | 검증할 수 없는 근거다 | **적용**: 관찰 내용 한 줄로 교체 |
| Med | xml-prose-format:7, 34, 40, 49, 194-202 | "Derive from Claude.ai system-prompt…", `<claude_behavior>`, `critical_child_safety_instructions`, `{{currentDateTime}}`, `'claude-opus-4-7'` | Claude.ai에서 옮겨 온 흔적이다. 실제 콘텐츠 사용은 0건이다 | **적용**: 삭제하거나 이 저장소 예시로 교체 |
| Med | xml-prose-format:16, 59, 91, 287 | "drop hedging … as optional", "`<never>` (absolute prohibition…)" | 배포 sc-author quality.md("Give the reason", "Strong emphasis over-triggers")와 반대 방향이다 | **적용**: "Direct voice: 행동과 (필요하면) 이유를 쓰고, hedging은 선택을 모델에 맡길 때만" |
| Med | content-quality:31 | "Hide future steps" | 단일 명령 본문의 `<flow>`와 `<handoff>` 구조에서는 달성할 수 없다 | **적용**: 별도 파일로 단계를 분리하는 Phase isolation으로 |
| Med | content-quality:66 | "never improve speculatively" | §4 sediment 삭제와 충돌한다 | **적용**: 추가나 재작성에만 실패 관찰을 요구하고, 삭제는 grep 근거로 충분 |
| Med | command-authoring:46; schemas.yaml:15, 22 | "1% of the context window…", "CC v2.1.69+", "CC 2.1.111+" | 버전에 묶인 사실은 저절로 낡는다 | **적용**: fields.yaml로 포인터, 버전 삭제 |
| Med | command-authoring:131, 144 | "`/menu`" | Claude Code에 `/menu`가 없을 가능성이 높다(확신도 약 75%) | **적용**: "`/` command picker and the skill listing" |
| Low | xml-prose-format:43 vs :98, :280 | 깊이 세는 기준이 다름 | — | **적용**: "below the root" 기준으로 통일 |
| Low | xml-prose-format:126-153 | 바깥 ```xml 블록 안에 ```python | 렌더링이 깨진다 | **적용**: 바깥 펜스를 4백틱으로 |
| Low | xml-prose-format:173 | "≤30 chars" vs `next=` | 실제 43건이 30자를 넘는다 | **적용**: `next` 예외 명시 |
| Low | output-style-authoring:32 | "Declarative present tense" | 실제 스타일은 명령형이다 | **적용**: "Imperative or declarative, no hedging" |
| Low | mode-authoring:85 | "`MODE_PascalCase.md`" | 다단어 이름 5개 중 4개가 `_`를 쓴다 | **적용**: `_` 형식, DeepResearch는 예외로 명시 |
| Low | xml-prose-format:55 | "No markdown headers" | Business_Panel과 Token_Efficiency가 위반한다. 테스트 없음 | 보류(P2) |
| Low | agent-authoring:14, 112, 129 | "Explore (… Haiku)", "~500 tokens", "200 lines / 25KB" | 버전에 묶인 사실 | 보류 |

## gotchas 정리

**결과:** general.md는 매 세션 로드되는 파일이다. 6185B에서 4178B로, 21항목에서 14항목으로 줄었다(09a 리뷰 후 compaction-drift 복원 포함).

| 항목 | 판정 | 근거 |
|---|---|---|
| compaction-drift | 삭제 → 09a 리뷰 후 복원 | "~50 turns"에 측정 출처가 없다. 상시 규칙과 중복은 아니라서 숫자 없이 복원 |
| hypothesis-before-fix | 삭제 | 항상 로드되는 PRINCIPLES:32 [R03]과 중복 |
| plan-checklist-vs-status | 삭제 | implement.md:19, :56과 test_plan_checklist.py가 같은 내용을 지킨다 |
| askuserquestion-rejection-fallback | 삭제 → 배포 RULES_QUALITY R21에 행동을 직접 씀 | 배포 콘텐츠가 이 저장소 로컬 이름을 인용하고 있었다 |
| hook-console-entry | hooks.md로 이동 | hook 편집 시에만 필요하다 |
| hook-placeholders-stale, codex-module-count-drift | authoring.md로 이동 | src 편집 시에만 필요하다 |
| uv-run-reverts-pip-upgrade + uv-lock-not-ci-pin | 병합 → uv-lock-local-only | 한국어 항목, 같은 주제 |
| rule-tag-vs-concept | 수정 | "R15 appear once"는 거짓이다(실제 8건). test_cross_references 허용 목록도 같이 수정 |
| lint-upgrade-attribution | 수정 | `make lint`는 `ruff check .`만 실행한다. format 검사는 CI에서만 한다 |
| context-leak, find-all-copies-first, windows-make-sync-broken, venv-inherited-by-worktree, size-target-no-collateral-cut, 헤더 | 수정 | 중복·전보체·한영 혼용·저장소에 없는 예시 |
| authoring.md: description-as-overeng-lever, probe-observer-effect, demand-capability-mismatch | 수정 | 미정의 표현, 해석 불가, `/sc:prompt`가 skill로 이동함 |
| README:7, :19 | 수정 | 전보체; 항목 추가와 날짜 갱신 규칙 |
| 나머지 hooks.md 17항목, general 6항목 | 유지 | 코드·테스트로 사실 확인. hooks의 `-F -`와 `--git-path`는 실측으로 확인 |

## 강점

- schemas.yaml이 단일 진실 원천이다. 테스트 3개가 실제로 이 파일을 읽는다.
- 명령 description 규칙(tier/gate/300자)이 테스트와 정확히 연결되어 있다.
- 금지 어휘를 테스트로 강제하고, 그 근거 연구 폴더가 실재한다.
- `effort`와 `model` 생략 규칙은 24/24가 지킨다.
- output-style-authoring은 짧고 이유가 붙어 있다.
