# 08b — 3차 구현: 남은 P1·P2

브랜치는 `fix/prompt-content-audit`다. 근거는 [03-analysis.md](./03-analysis.md) §4 P1·P2, 03a–03f의 미처리 행, [08a](./08a-implementation-rules-commands.md)의 보류 목록이다.

## 커밋

| 커밋 | 범위 | 내용 |
|---|---|---|
| `df0b8738` | core, loader | FLAGS의 측정 불가 조건을 관찰 가능한 조건으로 바꿈. 모드 플래그는 사용자가 입력하는 것으로 명시. ctx 기준치 60%로 통일. 유지보수자 메모 제거. RULES에 R-ID 범례, 두 설치 경로, 문서 전용 변경의 검증 방법 추가. 🔴는 보안 전용으로 되돌림. DELEGATION의 20K/30s 기준 교체. CLAUDE.md 편집 시 RULES_DOCS 주입 |
| `1172b4fb` | modes, BUSINESS_SYMBOLS | 03b 전 항목. VS 템플릿, DeepResearch, Orchestration, Task_Management, Introspection, Brainstorming, Token_Efficiency, fallback, XML 안의 `##` 헤더, 기호 중복, 전보체 |
| `61b4d570` | agents 24개, agents/README, 테스트 | 서브에이전트 질문 규칙(P-2), R-ID 태그 제거(P-5), 측정 불가 체크리스트(P-7), 03c·03d의 개별 항목, 전보체(P-8) |
| `ae4b42ac` | commands, `.claude/rules/` | agent/pm/task·analyze/review의 Not-for, cleanup 검사 이름, 전보체, agent-authoring 개수 할당과 새 규칙 3개 |
| `8b3eb320` | mcp, sc-prompt, mcp_fallback | 03e 전 항목 |
| `b79567ca` | sc-author | 03f 전 항목 |
| `5bf1f22e` | 전 영역 | 독립 리뷰 반영([09b](./09b-review-p1p2.md)) |

## 주요 결정

- **서브에이전트 질문 규칙(P-2).** 24개 agent의 Ask First 줄 끝에 같은 문장을 붙였다. 테스트 `test_ask_first_states_subagent_behavior`가 문장을 고정한다. 리뷰 후 문장은 두 가지를 다룬다.
  - 범위: 파일 어디서든 "묻는다/확인한다"는 단계 앞에서 멈추고, 제안과 질문을 보고에 담는다.
  - 확인으로 인정하는 것: 부모의 task text는 대상이 명시된 가역적 행동에만 확인이 된다. 파괴적·비가역적 행동은 사용자의 승인이 task에 인용되어 있어야 한다. 커널의 destructive_op_confirmation과 맞추기 위해서다.
  - 대화형 agent 7개(initializer, insight, business-panel, learning, socratic, requirements, frontend)에는 "메뉴/질문을 반환하고 멈춘다"는 한 문장을 더 넣었다.
- **R-ID.** agent 본문에서는 모두 지우고 테스트로 막았다(`test_body_has_no_rule_id_tags`). 커널(PRINCIPLES·RULES)은 태그를 유지하되 범례 한 줄을 넣었다. 태그 옆 문장이 규칙 자체라는 뜻이다. insight 기록이 R-ID를 쓰므로 커널에서 지우지 않았다.
- **🔴.** RULES_QUALITY의 R02/R03/R13/R15/R18을 🟡로 내렸다. 커널 규칙은 표시와 무관하게 항상 적용된다는 문장을 범례에 붙였다(R15 커널 규칙이 "Never claim…"이기 때문).
- **CLAUDE.md 편집 시 RULES_DOCS.** 쓰기 동사와 파일 이름이 함께 나올 때만 주입한다(영어·한국어). 단순 언급은 주입하지 않는다(세션당 약 2.5K 토큰). 음성 테스트 포함.
- **/sc:research 기본 전략.** unified(계획을 보여 주고 승인 대기)에서 질의 명확도에 따른 선택으로 바꿨다. 명확한 질의가 승인 대기로 멈추던 문제(03b)다. **행동 변화.**
- **sc-prompt 이월 행.** `(carried from <model>; not confirmed for 5.5)` 행은 적용하지 않고 후보로만 보고한다. Opus 5.5의 self-check 삭제도 후보 보고로 바뀌었다. **행동 변화.**
- **refactoring-expert 기준치.** "3+ files"를 "more than three files"로 되돌렸다. 압축 이전 원문(`db6e2898^`)의 값이다.

## 보류한 항목

| 항목 | 사유 / 필요한 결정 |
|---|---|
| sc-prompt SKILL.md:49 "Opus 5 has no such category"(`reasoning_extraction`) | 근거가 엇갈린다. 저장소(`opus-5-5-default-model/02-research.md:40`, `utils/__init__.py:308-310`, `evals/run_eval.py:316-318`)는 5.5에서 새로 생겼다고 하고, Opus 5.5 migration guide 문장은 Opus 5에도 있다고 읽힌다. 세 곳을 함께 바꿀지 결정 필요 |
| author-check X1이 memory 파일에도 단일 루트를 강제 | 코드 변경. format-xml.md는 이제 memory를 기본 md로 두고 XML 본문은 선택으로 설명한다 |
| commands의 남은 축약(help·implement·init의 impl/deps/exec 등), pm description의 Direct 전략 누락 | Low |
| `skill.md:45` "may read … only partially" | 현행 공식 best-practices 가이드가 같은 말을 한다(sc-author 작업자 확인) |
| FLAGS `Scope: system > project > module > file` | 뜻(넓은 범위 우선인지)을 원문에서 확정할 수 없다 |
| analyze.md의 🔴🟡🟢 심각도 표기 | 명령 출력용 심각도라 커널 범례와 별개로 둠 |

## 검증

| 검사 | 결과 |
|---|---|
| `uv run pytest -q` (최종) | 3539 passed, 3 skipped |
| `uv run pytest tests/unit/scripts -o addopts=` | 149 passed |
| `make lint`, `ruff format --check` | 통과 |
| `superclaude author-check` (sc-prompt·sc-author 편집 파일) | 0 errors (sc-prompt SKILL.md에 기존 N1 경고 1건) |
| CRLF | 0 |
| sc-prompt 본문 크기 | 15,871 / 16,000 bytes |

## 남은 일

- **canary 미실행.** core, agents(Ask First 문장), sc-author의 충돌 처리 문구, research 기본 전략이 바뀌었다. `make canary-gates`와 sc-author-* 태스크를 돌려야 한다.
- 행동 변화(위 표시 항목, 25c1ceea의 proactive 제거)는 측정하지 않았다.
