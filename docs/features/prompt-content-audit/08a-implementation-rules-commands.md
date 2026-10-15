# 08a — 2차 구현: rules·commands·output-style

브랜치는 `fix/prompt-content-audit`이다. 근거가 된 분석은 [03g](./03g-analysis-core-rules.md), [03h](./03h-analysis-repo-rules.md), [03i](./03i-analysis-commands.md)이다.

## 커밋

| 커밋 | 범위 | 내용 |
|---|---|---|
| `9a247cb6` | `src/superclaude/core/rules/` | 03g 적용 항목 전부. 모순, 해석되지 않는 참조, 측정 불가 조건, 저장소 이력 누수를 고쳤다 |
| `72445b09` | `.claude/rules/`, gotchas, `tests/unit/test_cross_references.py` | 03h 의미 수정. gotcha 정리(21→14항목, 이동·병합·삭제). 테스트 허용 목록 정리 |
| `3a1f6285` | `scripts/context_loader.py`, `tests/unit/test_context_loader.py`, `ARCHITECTURE.md` | `--structured`가 BUSINESS_SYMBOLS를 불러오는 경우를 `/sc:business-panel`로 한정하고, 회귀 테스트를 추가했다 |
| `3d1475ce` | `.claude/rules/` 10개 | `b196673b`가 축약한 문체를 문법적인 영어로 복원했다. 의미는 바꾸지 않는다 |
| `17204cb6` | `commands/` 30개 파일, `output-styles/plain-language.md`, `modes/RESEARCH_CONFIG.md`, `agents/deep-researcher.md` | 03i 적용 항목 전부 |
| `f2da52b1` | 배포 콘텐츠 | 독립 리뷰 반영([09a](./09a-review-rules-commands.md)) |
| `ce239738` | `.claude/rules/` | 독립 리뷰 반영 |

## 작업 방식

- **core/rules와 loader**
  - 오케스트레이터가 원문을 직접 확인한 뒤 수정했다.
  - 이 저장소의 canary와 테스트가 보호하는 문구는 수정 전에 확인했다(`bugfix-scope-creep`, `problem-statement-not-request`).
- **commands와 output style**
  - 파일 묶음이 겹치지 않는 작업자 3명에게 감사 결과와 교체 문안을 주어 병렬로 수정했다.
  - 오케스트레이터가 diff를 검토한 뒤 커밋했다.
- **문법 복원**
  - 작업자 2명이 `git show b196673b^:<path>`의 원문을 참고해 복원했다.
  - 리뷰어가 약 110개 문장을 표본으로 확인했고, 의미가 바뀐 4건을 찾았다. 2건은 되돌렸고 2건은 의도한 수정이었다(09a).

## 의도적으로 보류한 항목

| 항목 | 사유 |
|---|---|
| ~~RULES_DOCS phase↔status enum 매핑~~ | **후속 처리.** 사용자가 위임해 오케스트레이터가 정했다(아래 '후속 결정') |
| Durability routing이 CLAUDE.md 편집 때 주입되지 않음 | TRIGGER_MAP 코드 변경이 필요하다. 트리거를 넓히면 다른 프롬프트에도 주입되므로 따로 설계해야 한다 |
| ~~research·reflect description의 tier~~ | **후속 처리.** research는 예외로 Auto 유지(사용자 결정). reflect는 동의 후에만 기록하므로 규칙상 Auto |
| agent/pm/task 사이의 "Not for" 구분 | P1 |
| ~~배포된 agent의 "Use proactively"~~ | **후속 처리.** 23개 description을 재작성했다(사용자 결정) |
| agent-authoring 템플릿의 개수 할당("3-5 items") | P1 |
| 배포 콘텐츠에 남은 전보체 | 손댄 파일 범위만 고쳤다. 나머지는 P2 |
| DELEGATION의 ">20K tokens", "under 30s" | P2 |
| cleanup R1(이제 R3에만 의존하는 검사) | 구조 정리는 P2 |

## 후속 결정 (사용자 지시)

**1. phase 매핑** (RULES_DOCS, implement, promote-feature)
- README `phase:`는 폴더가 도달한 가장 먼 단계이며, 뒤로 가지 않는다.
- 문서 슬롯별: 00-intent → intent, 01-discovery → discovery, 04-design → design, 05-plan → planning.
- 실행 단계: plan 첫 체크박스 → implementing(plan `status: implementing`도 함께), plan(index) `status: complete` → complete.
- 02/03/06+ 문서와 deprecated 문서는 phase를 바꾸지 않는다. abandoned는 사용자가 말할 때만.
- 근거: phase enum과 문서 슬롯이 이미 1:1로 대응한다. 그동안 `status: implementing`으로 바꾸는 명령이 없어서 implement에 그 전환을 넣었다. promote-feature는 무조건 `discovery`였던 것을 옮긴 문서 기준으로 바꿨다.

**2. tier 정책** (command-authoring)
- 휴리스틱을 '기본 동작으로 커밋 산출물을 쓰면 on-request'로 좁혔다. 플래그(analyze `--format`)나 동의(reflect)가 있어야 쓰는 명령은 Auto다.
- research는 명시적 예외다. 보고서가 요청의 산출물이고, 자기 문서 외에는 수정하지 않는다. 새 예외도 같은 두 조건을 요구한다.

**3. agent description 23개 재작성** (verifier는 이미 모범이라 제외)
- "Use proactively/proactive" 21개를 제거했다. security-engineer만 사건을 명시한 "Use immediately after a change touches authentication, encryption, secrets or input validation"을 유지했다.
- 무요청 실행이 사라진 agent: project-manager(구현 후 패턴 기록), quality-engineer, insight-analyst, repo-index(세션 시작), project-initializer, simplicity-guide 등. 이제 요청이나 구체적 신호가 있을 때만 위임된다.
- 모든 description에 이웃 agent를 가리키는 "Not for … — <neighbor>"를 넣었다(backend↔system↔devops, performance↔root-cause, learning↔socratic↔technical-writer, refactoring↔simplicity, quality↔verifier, self-review↔verifier/security 등).
- 전보체 persona("Security engineer find vulns", "Technical writer make clear")를 문법적 문장으로 바꿨다. mission 단어 30% 공유 테스트와 금지 어휘 테스트는 통과했다.
- 발견: 콜론-공백(`: `)이 든 description 2개가 YAML 오류였는데 기존 테스트가 잡지 못했다(`md_helpers.parse_frontmatter`는 줄 단위 분리라서). `tests/unit/test_frontmatter_yaml.py`를 추가했고, 깨진 파일로 실패하는 것을 확인했다.

## 검증

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` (최종) | 3416 passed, 3 skipped |
| `make lint` | All checks passed |
| 출력 스타일 단어 수 | 600/600 (`test_output_style_structure.py`) |
| gotcha 항목 길이 | 모두 320자 이하 (`test_gotcha_budget.py`) |
| CRLF | 0 (`file … \| grep -i crlf`) |
| 사용자명 잔존 (`grep -rn ajitta src/superclaude --include=*.md`) | 저장소 URL(`sc.md:75`)과 hooks README의 경로 예시만 남음 |

## 남은 일

- **canary 미실행.** core(`RULES_*`, `PRINCIPLES.md`)가 바뀌었으므로, `make release` 전에 `make canary-gates`를 실행해야 한다. RULES_INTERACTION의 메뉴 조건, R12/R21 문구, plan과 review의 게이트가 주요 확인 대상이다.
- **행동 변화 미측정.** 이번 수정은 정적 감사와 독립 리뷰에 근거한다. 모델 행동이 실제로 바뀌었는지는 측정하지 않았다.
