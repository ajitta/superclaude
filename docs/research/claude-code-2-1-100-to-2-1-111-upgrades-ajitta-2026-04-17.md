# Claude Code 2.1.100 → 2.1.111 변경 영향 분석

**Scope**: SuperClaude 콘텐츠 프레임워크(`src/superclaude/`) 및 저작 규칙(`.claude/rules/`)에 적용 가능한 항목 식별·분류.
**Source**: 로컬 `/release-notes` 출력 (외부 검색 불필요, 1차 자료 그대로).
**Method**: 각 버전 변경 읽고 → 프레임워크 impact 여부 평가 → 증거 기반 파일·라인 매핑.

---

## Executive Summary

| 버전 | 핵심 영향 | Priority |
|------|----------|----------|
| 2.1.105 | **Skill description cap 250→1,536자 확대**, **PreCompact hook 차단 기능 추가**, plugin `monitors` manifest 키 | P0 |
| 2.1.108 | **Model이 built-in slash command를 Skill tool로 자동 호출 가능**, `/recap` 추가 | P1 |
| 2.1.110 | **`/tui`**, **`autoScrollEnabled` setting**, `Ctrl+O` 의미 변경 (transcript verbose vs `/focus`) | P1 |
| 2.1.111 | **Opus 4.7 + `xhigh` effort 레벨**, `/less-permission-prompts` skill, `/ultrareview`, Auto mode 기본 허용 | P0 |
| 2.1.101, 107, 109 | 내부 UX/버그 수정 중심 | P3 (반영 불필요) |

**Bottom line**: P0 2건 (문서 hard-lock 수정) + P1 3건 (신규 기능 문서화) + P2 2건 (신규 콘텐츠 기회) = **총 7개 실행 항목**.

---

## Category A: 즉시 반영 필요 — 저작 규칙 문서 업데이트 (P0)

권위 있는 저작 가이드가 구버전 CC 동작을 가정하고 있어 **사실 오류**가 된 항목.

### A1. Skill description 자수 상한 완화 [2.1.105]

**변경**: `/skills` 메뉴 listing cap이 250 → **1,536 chars**로 확대. "raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated" (v2.1.105).

**영향 파일**: `.claude/rules/skill-authoring.md` 3개 위치
- Line 63: `description: One-line purpose.    # 권장 | ≤250 chars 실용 상한`
- Line 105: `- 개별 description은 listing에서 ~250 chars로 잘림 — 트리거 키워드는 첫 100 chars 안에`
- Line 179: `2. \`description\` + \`when-to-use\` 분리, 합쳐서 ≤250 chars 지향`

**제안 수정**:
- 250 → 1,536 숫자 업데이트
- "트리거 키워드는 첫 100 chars 안에" 권장은 유지 (listing에서 우선 노출되는 영역 관점에서 여전히 유효)
- startup warning이 생긴 것도 명시 → "자수 초과 시 기동 시 경고 발생"

**Action**: `skill-authoring.md` 3곳 Edit.

---

### A2. PreCompact hook 차단 기능 추가 [2.1.105]

**변경**: "PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision":"block"}`" (v2.1.105).

**영향 파일**: `src/superclaude/hooks/README.md` Line 27
- 현재: `| \`PreCompact\` | Before conversation compaction | **No** | Context preservation |`
- 수정: `Can Block?` 컬럼을 `Yes (exit 2 or {"decision":"block"})` 로 변경

**Action**: `hooks/README.md` 표 1개 셀 수정.

---

### A3. `xhigh` effort 레벨 추가 [2.1.111]

**변경**: Opus 4.7 전용 `xhigh` 레벨 도입 (`high`와 `max` 사이). `/effort`, `--effort`, 프론트매터에 적용 가능. 다른 모델은 `high`로 fallback.

**영향 파일**: `.claude/rules/agent-authoring.md` effort 표
- 현재 값: `low|medium|high|max` (+ precedence 설명)
- 수정: `low|medium|high|xhigh|max` + "xhigh는 Opus 4.7에서만 효과, 다른 모델은 high로 fallback" 주석

**관련 에이전트 재검토 권장**:
- `business-panel-experts` (effort: max) — 멀티 전문가 통합 추론, Opus 4.7 전제면 `xhigh`가 더 적합할 수도
- `deep-researcher` (effort: max) — 동일

단 `max`도 Opus 4.7에서 유효한 레벨로 남아 있으므로 **지금 바꿀 필요는 없음**. 규칙 문서만 업데이트하고 에이전트별 재평가는 선택 사항.

**Action**: `agent-authoring.md` effort 표 `xhigh` 행 추가 (1 곳).

---

## Category B: 신규 기능 인식/문서화 (P1)

SuperClaude 동작에 직접 영향은 없지만, 사용자·에이전트가 알면 유용한 변화.

### B1. Model이 built-in slash command를 Skill tool로 자동 호출 [2.1.108]

**변경**: "The model can now discover and invoke built-in slash commands like `/init`, `/review`, and `/security-review` via the Skill tool" (v2.1.108).

**SuperClaude 관점**:
- SuperClaude의 `/sc:*` 커맨드들은 **built-in이 아님** (사용자 커스텀 커맨드) — 직접적 영향 없음
- 그러나 CC built-in `/review`, `/security-review`와 SuperClaude `/sc:review`, `security-engineer` 에이전트 간 **역할 중첩**이 심화됨
- 에이전트 라우팅 규칙(RULES.md `<agent_routing>`)에 "CC built-in /review vs /sc:review" tie-breaker 추가 고려

**Action**: 즉시 반영 불요. 다음 `<agent_routing>` 업데이트 시 행 추가만 검토.

---

### B2. `/tui fullscreen` 및 `/focus` 분리, `Ctrl+O` 의미 변경 [2.1.110]

**변경**:
- `/tui fullscreen` 명령으로 동일 세션 내 flicker-free rendering 전환
- `Ctrl+O` = transcript normal/verbose 토글 전용 (이전에는 focus view 포함)
- focus view는 별도 `/focus` 명령으로 분리
- `autoScrollEnabled` 설정 추가

**영향**: 직접적인 콘텐츠 프레임워크 impact 없음. 단 **CLAUDE.md 사용자 가이드 섹션**에 키바인딩을 언급하는 곳이 있다면 갱신 필요.

**검증 필요**: `src/superclaude/` 내 `Ctrl+O`, `focus view` 언급 검색.

**Action**: grep 후 발견 시 업데이트. (보통 없을 가능성 높음)

---

### B3. Auto mode 기본 허용 [2.1.111]

**변경**: "Auto mode no longer requires `--enable-auto-mode`" + "Auto mode is now available for Max subscribers when using Opus 4.7"

**영향**: `core/FLAGS.md`에 auto mode 관련 플래그 기술된 곳이 있으면 리비전.

**검증 필요**: `auto-mode` 또는 `--enable-auto-mode` 언급 검색.

**Action**: 없으면 스킵. SuperClaude 플래그 체계와 독립적 가능성 높음.

---

## Category C: 신규 콘텐츠 기회 (P2)

SuperClaude에 **새 agent/skill/command 추가 후보**. 즉시 구현은 불요하지만 설계 근거로 기록.

### C1. `/less-permission-prompts` 영감 [2.1.111]

**CC 신규 기능**: transcript 스캔 → 자주 쓰이는 read-only Bash/MCP 호출 식별 → `.claude/settings.json` allowlist 우선순위 제안하는 skill.

**SuperClaude 각도**: 프로젝트의 `.claude/settings.json` 개인화를 돕는 skill 또는 `/sc:*` 명령으로 구현 가능. 단 CC built-in이 이미 있으므로 **중복 회피**가 원칙 — 추가하지 않는 것이 YAGNI (R06, R18).

**판단**: **Skip**. CC에 이미 있는 기능을 재구현할 필요 없음.

---

### C2. `/ultrareview` 패턴 검증 [2.1.111]

**CC 신규 기능**: 클라우드에서 parallel multi-agent 분석·비판으로 comprehensive code review 실행.

**SuperClaude 각도**: SuperClaude는 이미 `/sc:review` + `quality-engineer`/`security-engineer`/`refactoring-expert` **multi-agent dispatch** 패턴을 보유 (RULES.md `<sub_agent_decision>` 참조). Anthropic이 같은 아키텍처 패턴을 flagship 기능으로 공식화했다는 것은 **기존 접근법의 외부 검증**.

**판단**: **변경 없음**. 현재 패턴이 공식 방향과 일치 — 자신감 가지고 유지.

---

## Category D: 참고만 — 반영 불요 (P3)

직접적인 프레임워크 영향 없는 내부 UX/버그 수정.

| 항목 | 버전 | 이유 |
|------|------|------|
| OS CA cert store trust 기본값 | 2.1.101 | 설치 런타임 동작, 콘텐츠와 무관 |
| 여러 `--resume` 복구 버그 수정 | 2.1.101, 105, 108 | 세션 영속성, 콘텐츠 무관 |
| thinking indicator 회전 표시 | 2.1.107, 109 | 순수 UI |
| `ENABLE_PROMPT_CACHING_1H` | 2.1.108 | 사용자 환경변수, 문서화 범위 아님 |
| `/recap` 명령 | 2.1.108 | CC built-in, `/sc:*`과 독립 |
| `/doctor` 개선 | 2.1.105, 110 | `make doctor`와 독립 |
| `Ctrl+U/L/Y` 재매핑 | 2.1.111 | 키바인딩, 콘텐츠 무관 |
| `OTEL_LOG_RAW_API_BODIES` | 2.1.111 | 디버깅 환경변수 |
| 플러그인 `monitors` manifest 키 | 2.1.105 | 플러그인 배포 모델을 쓰지 않음 (설치 경로: `src/superclaude/` → `~/.claude/`) |
| Windows PowerShell tool rollout | 2.1.111 | 플랫폼 특화, 콘텐츠 무관 |

---

## Implementation Plan (P0 항목만)

### 변경 파일 3개, 총 5곳 Edit

1. **`.claude/rules/skill-authoring.md`** (3 edits, ~2분)
   - Line 63, 105, 179: `250` → `1,536`
   - Line 63: 범위 제한 문구 수정

2. **`src/superclaude/hooks/README.md`** (1 edit, ~30초)
   - Line 27 PreCompact 행: `No` → `Yes (exit 2)`

3. **`.claude/rules/agent-authoring.md`** (1 edit, ~1분)
   - effort 표에 `xhigh` 행 추가 (Opus 4.7 전용 주석)

### 검증
```bash
uv run pytest tests/unit/test_skill_structure.py tests/unit/test_agent_structure.py -v
```

### 테스트 베이스라인
- 1,807 collected, ~1,628 passing (12 pre-existing failures)
- 위 3개 파일은 markdown만 → 테스트 위험 없음 (CLAUDE.md의 "docs-change-safe" 보장)

---

## Open Questions (사용자 확인 필요)

1. **B1** (CC built-in `/review` vs `/sc:review` 라우팅 규칙): 지금 추가할지, 실제 중첩 케이스가 보고될 때 추가할지?
2. **A3** (`business-panel-experts`, `deep-researcher`를 `max` → `xhigh` 하향): 비용/속도 vs 품질 trade-off — 지금은 **유지 권장** (실사용 피드백 없음).
3. **C1/C2** (새 콘텐츠 추가): Skip이 기본값 — 별도 요청 있을 때만 재검토.

---

## Citations

모든 인용은 로컬 `/release-notes` 출력 (세션 컨텍스트 내). 버전별 라인 위치는 릴리스 노트 본문의 `Version 2.1.XXX:` 헤더 하위에 일치.

## Confidence

- P0 항목 (A1, A2, A3): **High** — 릴리스 노트의 명시적 문구 + 로컬 grep으로 영향 위치 확인됨.
- P1 항목 (B1-B3): **Medium** — 영향 가능성은 있으나 현재 SuperClaude에 대응 코드가 없어 검증 여지.
- P2 항목 (C1, C2): **High** (Skip 판단) — YAGNI/중복회피 원칙에 기반한 명확한 결정.
