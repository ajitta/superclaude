# 03e — MCP 문서 + sc-prompt 스킬 감사

**대상**
- MCP 문서: `mcp/MCP_Chrome-DevTools.md`, `MCP_Playwright.md`, `MCP_Tavily.md`, `mcp/README.md`
- 스킬: `skills/sc-prompt/SKILL.md`, `skills/sc-prompt/references/*` (evidence, fable-5-1, opus, sonnet-5-5)

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- **MCP 문서 본문은 기본 설정에서 거의 전달되지 않는다.**
  - Playwright와 DevTools는 1줄 힌트만 들어간다(`context_loader.py:230` TIER_0).
  - Tavily는 요약 지시문만 들어간다.
  - 본문 전체는 `--verbose-context`일 때만 주입된다.
  - 그래서 본문 결함의 영향은 제한적이다. 하지만 정확히 그 플래그를 쓰는 상황(짧은 지시로 오동작할 때)에 모순이 드러난다.
- **MCP 문서의 핵심 위험:** use/never와 fallback 간 모순, 설치되지 않는 파일 참조, 기본 caps에 없는 도구를 쓰는 예시.
- **sc-prompt의 핵심 위험:**
  - "이전 모델 섹션으로 대체 금지" 규칙을 mirror 파일 스스로 어긴다.
  - 원문을 주지 않은 "documented block"을 모델이 지어낼 소지가 있다.
  - 근거 없이 단정한 모델 주장이 섞여 있다.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 (모델 인식 관점) | 제안 | 상태 |
|---|---|---|---|---|---|
| High | sc-prompt/SKILL.md:32 ↔ references/opus.md:11, sonnet-5-5.md:19 | "Never read an earlier model's section in place of a missing one" ↔ "for Opus 5 … carries it to 'claude-opus-5-5'", "carried from Sonnet 5" | 규칙이 금지한 이월을 mirror가 수행한다. 모델은 어느 쪽을 따를지 판단할 수 없고, 5.5 대상에 Opus 5 방향(검증 지시 삭제 등)이 적용된다 | 이월한 행마다 "(Opus 5 유래, 5.5 미확인)" 표시, 또는 SKILL:32에 예외 명시 | 재확인, P1 |
| High | SKILL.md:54, fable-5-1.md:15, 17, 20 | "documented autonomy block", "the one-sentence batching nudge", "single-limit note" | 원문 없이 의역만 있어서 모델이 문안을 지어낸다. Step 6 "An addition with no source is deleted"와 충돌한다. Opus/Sonnet은 `[FILL: guide]`로 처리했는데 Fable만 누락됐다 | 원문을 인용하거나 `[FILL: …]` 슬롯으로 통일 | P1 |
| Med | SKILL.md:29 ↔ context_loader.py:925, 955 | "glob … under the `.claude` directories" | hook은 `/sc-prompt` 리터럴이 입력될 때만 실행된다. description으로 자동 호출되면 hook 안내가 없다. 게다가 `.claude` glob은 temp 아래의 bundled 사본을 찾지 못하고, mirror로 대체된다(Gotcha 105가 금지한 결과) | glob 범위에 bundled-skills 경로 추가, 또는 "못 찾으면 보고"로 완화 | P1 |
| Med | SKILL.md:29-30 | "names … each model's line ranges" ↔ "never by line number" | hook이 줄 범위를 주면서 줄 기준으로 읽지 말라고 한다. 범위를 무시할지 쓸지 모호하다 | "범위는 위치 안내용, heading으로 확인" 한 줄 추가 | P2 |
| Med | MCP_Tavily.md:8 ↔ :38 | "never>single-page extract (use native `WebFetch`)" ↔ "Prefer … `tavily-extract`" | 같은 문서가 단일 페이지 추출을 금지하면서 동시에 권장한다 | never를 "MCP 경로에서만"으로 한정 | P1 |
| Med | MCP_Tavily.md:3, 12 ↔ :38 | mission = MCP, "Prefer the Tavily Agent Skills … the primary integration" | 최우선 권고가 `<fallback>` 슬롯에 있다. 모델은 `<choose>`를 먼저 읽고 MCP를 고른다 | skills 우선 권고를 `<choose>`로 이동 | P1 |
| Med | MCP_Tavily.md:12 | "install per `mcp/README.md`" | README는 설치 대상에서 제외된다(`install_components.py:142`). 사용자 프로젝트에서는 존재하지 않는 참조다 | 설치 명령을 인라인으로 쓰거나 URL로 | P1 |
| Med | MCP_Playwright.md:50-53 ↔ :13-17, install_mcp.py:54 | `browser_route`, `browser_network_state_set`, `browser_cookie_set` | 이 도구들은 opt-in caps에 속하는데 superclaude는 `--caps` 없이 설치한다. 예시 4개 중 3개가 기본 환경에 없는 도구를 쓰고, 모델은 그것을 모방한다 | 해당 행에 `(--caps=network/storage)` 표기 | P1 |
| Med | MCP_Chrome-DevTools.md:7 ↔ :8, MCP_Playwright.md:59 | INP 측정(인터랙션 필요) ↔ "never … live browser interact"; Playwright fallback "Chrome DevTools MCP for browser work" | 절대 표현을 문자 그대로 따르면 INP 측정 중에 Playwright로 전환한다. 두 파일의 fallback 방향도 서로 반대다 | never를 "E2E 시나리오 작성"으로 좁히고 이유 추가 | P1 |
| Med | SKILL.md:58 | "caps starve reasoning on hard problems" | 출력 길이 상한이 추론을 굶긴다는 것은 thinking이 없던 3.x 시절의 CoT 논리다. 대상 모델은 thinking 블록에서 추론하므로 근거가 낡았다 | 근거를 "범위·깊이 판단 왜곡" 등으로 교체하거나 행 재검토 | P2 |
| Med | SKILL.md:20, 49-50, 66 | "Claude Code already injects …", `reasoning_extraction` decline, Fable "cannot turn thinking off", "prefill errors on every target" | 구체적인 사실 주장인데 mirror나 evidence에 근거가 없다(opus.md, fable-5-1.md에 해당 내용 없음). Step 6의 "documented model behavior"를 단정으로 채우게 된다 | 행마다 출처 섹션을 표기하거나 mirror로 옮겨 적기 | P1 |
| Med | opus.md:35 | "64K 'has worked well'" … "`(Opus 5.5 prompting guide)`: 128,000" | Step 7은 하한 하나를 요구하는데 값이 둘이고 선택 규칙이 없다 | Sonnet처럼 용도별 규칙을 명시 | P2 |
| Low | SKILL.md:3, 107 ↔ skills/sc-author/SKILL.md:46 | `/claude-api prompt-audit` ↔ `/doctor prompt-audit` | 같은 저장소 감사 명령이 프레임워크 안에서 두 가지로 지칭된다. 위임 대상의 실재를 확인할 수 없다 | 하나로 통일하고 실재 확인 | P2 |
| Low | MCP_Tavily.md:15 | "`include_domains:[arxiv,github]`" | 도메인이 아닌 이름이라 그대로 모방하면 잘못된 파라미터가 된다 | `arxiv.org`, `github.com` | P2 |
| Low | MCP_Chrome-DevTools.md:7, Playwright:3; sonnet-5-5.md:32; SKILL 전반의 †/‡ | "flows on diff pages", "Browser auto", "retries only `cyber` and `frontier_llm`, on Sonnet 5" | 축약 때문에 뜻이 모호하다. "diff"가 different인지 비교인지, "on Sonnet 5"가 대상인지 fallback 모델인지 알 수 없다. 기호의 정의도 흩어져 있다 | 축약을 풀어 쓰기 | P2 |

## sc-prompt 모델 주장의 신뢰성

- **출처 표기는 대체로 좋다.**
  - mirror 파일에 `sources`와 retrieved 날짜가 있다.
  - 가이드에서 온 줄은 `(Opus 5.5 prompting guide)`로 구분한다.
  - 로컬에 없는 문단은 지어내지 않고 `[FILL: URL]`로 남긴다. 정직한 설계다.
- **evidence.md가 이 묶음에서 가장 정직하다.** "None of these rows rests on a controlled Claude measurement"라고 근거의 강도를 스스로 밝힌다. 다만 근거 자체는 약하다.
  - 블로그 1건과 링크 없는 자체 결과가 전부다.
  - 표본이 n=3, 2/2로 작다.
  - 측정 대상이 'claude-opus-5'다(5.5가 아님).
- **한국어 전용 신호(SKILL:57, :63)는 작성자 환경이 섞여 들어간 것이다.** 다른 사용자에게 해는 없지만 근거는 빈약하다.
- **표 안에 출처 없는 단정이 있다** (위 표의 Med 행). "documented"를 요구하는 스킬이 자기 출처 규칙을 어기는 셈이다.
- **구세대 흔적:**
  - Numeric caps 행의 근거는 3.x 시절 논리다.
  - Severity filters와 Step choreography 행은 4.x 시절 일반론으로 보이는데 근거 표기가 없다.
  - 반대로 다음 방향은 현행 모델과 맞다: thinking 주문(incantation) 삭제, prefill을 structured outputs로 대체, effort를 조절 수단으로 사용.
- **자기 일관성:** 본문은 "Emphasis inflation"과 "Prohibition walls"를 제거 대상으로 정했다. 그런데 자기 Gotchas와 Steps에서 `Never`를 8회 이상 쓴다. 대부분 이유가 함께 있어 심각하지는 않다.

## 강점

- **DevTools:** "it excludes performance — traces carry that", "the audit has no category filter"처럼 이유를 함께 적어 잘못된 도구 선택을 예방한다. CWV 임계값 표가 정확하다.
- **Playwright:** `<cli_vs_mcp>`의 판단 조건이 명시되어 있고 서버가 비활성일 때의 경로까지 다룬다.
- **sc-prompt:**
  - description에 트리거와 제외 범위가 명확하다.
  - references를 대상 모델별로 필요할 때만 읽어 단계적 로딩이 잘 되어 있다.
  - "Clean prompt → no diff", "Context is never cruft"가 억지 diff를 막는다.
  - Opus와 Sonnet에서 검증 지시 방향이 반대라는 것을 명시한다.

## 미확인 범위

실제 MCP 도구 이름의 실재 여부(heap snapshot, `browser_network_state_set` 등)는 저장소 밖 자료가 필요해 확인하지 않았다. sc-prompt의 모델 주장을 원문 가이드와 대조하는 작업도 같은 이유로 하지 않았다.
