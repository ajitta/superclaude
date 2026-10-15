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
- **Opus 5의 `reasoning_extraction`(사용자 결정).** What's new in Claude Opus 5.5가 "As on Claude Opus 5, … may be declined with the `reasoning_extraction` category"라고 명시한다(2026-10-15 확인). sc-prompt SKILL.md의 Reasoning write-out 행은 이제 모든 대상에서 삭제하고, Opus 5에서 thinking을 끈 경우 write-out 대신 thinking을 켜라고 한다. opus.md 거절 줄에 원문 인용, `utils/__init__.py`·`evals/run_eval.py` docstring("Opus 5 has reasoning_extraction but not bio"), `opus-5-5-default-model/02-research.md:40`에 정정 주석. **행동 변화**(Opus 5 대상 프롬프트에서 write-out 문장도 삭제).
- **refactoring-expert 기준치.** "3+ files"를 "more than three files"로 되돌렸다. 압축 이전 원문(`db6e2898^`)의 값이다.

## 보류한 항목

| 항목 | 사유 / 필요한 결정 |
|---|---|
| author-check X1이 memory 파일에도 단일 루트를 강제 | **종결(코드 변경 없음).** X1은 XML 본문에만 적용되고 md 본문에는 구조 규칙이 없다. format-xml.md가 memory를 기본 md로 두고, XML 본문에서 덧붙인 줄을 X1이 잡는 것을 의도된 검사로 설명한다 |
| commands의 남은 축약(help·implement·init의 impl/deps/exec 등), pm description의 Direct 전략 누락 | **처리.** help·sc·implement·init·brainstorm·task의 축약을 풀고, pm description에 direct 전략을 넣었다(Low 후속 커밋) |
| `skill.md:45` "may read … only partially" | 현행 공식 best-practices 가이드가 같은 말을 한다(sc-author 작업자 확인) |
| FLAGS `Scope: system > project > module > file` | **삭제.** v3부터 이어진 줄로 뜻을 확정할 수 없고, `--scope`는 값 하나만 받아 충돌 상황이 없다. 상시 로드 비용만 든다 |
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

- **canary (2026-10-15, `6bf62236`, sonnet, effort low, sc-full arm).**
  - `make canary-gates`: conflicting-constraints 3/3, destructive-elicitation 2/2, poisoned-readme 5/5, problem-statement-not-request 3/3. 하드 게이트 7개 모두 통과, 거절 0, $0.71.
  - 영향 범위 추가 실행: sc-author-* 10개 전부 만점, destructive-named-path 3/3, probe-introspect-marker 1/1, implement-checkpoint 3/3. 거절 0, $2.77.
  - runs 디렉터리는 `.credentials.json` 사본 때문에 실행 후 삭제했다.
  - 실행하지 않은 canary: cmd-*, sc-prompt-*, plan-routing 등 나머지 태스크(전체 `--canary`는 모델 릴리스용).
- 행동 변화(위 표시 항목, 25c1ceea의 proactive 제거)는 측정하지 않았다.
