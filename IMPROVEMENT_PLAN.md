# SuperClaude 향상 계획 — 상세 스펙

**버전**: v4.3.0+ajitta → v5.0.0+ajitta (목표)
**작성일**: 2026-03-02
**갱신일**: 2026-03-02 (분석 결과 반영, 커맨드→스킬 전환 전략 추가, sc: prefix 네이밍 + Anthropic 공식 스킬 분리)
**방향**: 개인 포크 유지, 업스트림 독립 진화
**원칙**: Orient-Step-Learn (각 Phase 완료 후 평가/피드백)

---

## 현황 기준선 (Baseline)

| 지표 | 현재 값 (검증 완료) | 목표 |
|------|---------------------|------|
| 테스트 | 737 passed (1.33s) | 유지 + 확장 |
| 커버리지 | 37% | Phase 1 후 50%+, Phase 2 후 60%+ |
| 커맨드 | 30개 (.md) | 22개 유지 + 8개 sc: 스킬 리다이렉트 스텁 |
| 에이전트 | 20개 (.md) | 유지 |
| 스킬 (sc:) | 3개 (sc:ship, sc:confidence-check, sc:simplicity-coach) | Phase 2 후 11개 (3 기존 리네임 + 8 전환) |
| 스킬 (공식) | 0개 | Anthropic 공식 스킬 활용 (code-review, skill-creator 등) |
| 모드 | 7개 | 유지 |
| MCP 문서 | 8개 (6개 얕음: Context7, Playwright, Chrome-DevTools, Magic, Morphllm, Sequential) | Phase 1 후 균일 |
| execution/ | 1,336줄 (레거시, 외부 import 0건) | Phase 1에서 제거 |
| scripts/ | context_loader.py 495줄, 전부 0% 커버리지 | Phase 1 후 핵심 3개 테스트 |
| 미해결 이슈 | ANALYSIS_REPORT 2 moderate (Finding 2 false → 삭제) | Phase 1에서 해결 |

---

## Phase 1: 정리 & 기반 다지기

> 목표: 기술 부채 해소, 커버리지 37% → 50%+
> 예상 작업량: 중간
> 선행 조건: 없음

### 1.1 ANALYSIS_REPORT Moderate Findings 해결

**상태**: 즉시 실행 가능

#### Finding 1: FLAGS.md / RULES.md stray `</output>` 태그

- **위치**: `src/superclaude/core/FLAGS.md` 마지막 줄, `src/superclaude/core/RULES.md` 마지막 줄
- **문제**: `</component>` 다음에 매칭되지 않는 `</output>` 태그가 존재. CLAUDE.md 인젝션 체인에서 `<output>` 래핑의 잔재.
- **수정**: 양 파일에서 stray `</output>` 줄 삭제
- **영향**: 설치된 `~/.claude/superclaude/core/` 파일에도 동일 적용 필요

```diff
# FLAGS.md 마지막
  </component>
- </output>

# RULES.md 마지막
  </component>
- </output>
```

#### ~~Finding 2: FLAGS.md `<priority_rules>` 들여쓰기~~ — 삭제 (오분석)

> 분석 결과: FLAGS.md의 모든 섹션이 `<component>` 내부에서 일관된 2칸 들여쓰기를 사용하고 있음을 바이트 수준에서 확인 완료. `<priority_rules>` 포함 전체 섹션이 동일한 들여쓰기. 이 finding은 false positive.

#### Finding 3: MCP 문서 깊이 불균형

- **현황**:
  - 심층 (78-119줄): Serena (119L), Tavily (78L)
  - 얕음 (24-32줄): Context7 (24L), Magic (27L), Morphllm (28L), Playwright (28L), Sequential (28L), Chrome-DevTools (32L)
- **수정 방침**: 얕은 **6개** MCP 문서를 40-60줄 수준으로 보강
  - 각 문서에 추가: 구체적 사용 시나리오 2-3개, 도구별 선택 가이드, 일반적 워크플로 예시
- **우선순위**: Context7 > Playwright > Sequential > Chrome-DevTools > Magic > Morphllm (사용 빈도순)

**검증**: `superclaude doctor` 실행 + 설치 후 context_loader.py의 인젝션 테스트

---

### 1.2 execution/ 모듈 정리

**상태**: 사용자 확인 완료 — 레거시, 외부 import 0건 확인

#### 대상 파일

| 파일 | 줄 수 | 커버리지 | 용도 |
|------|-------|----------|------|
| `execution/__init__.py` | 227 | — | 모듈 export |
| `execution/parallel.py` | 288 | — | ThreadPoolExecutor 기반 병렬 실행 |
| `execution/reflection.py` | 400 | — | 3-Stage Pre-Execution 체크 |
| `execution/self_correction.py` | 421 | 28% | 자기 수정 패턴 |
| **합계** | **1,336** | | |

#### 수정 계획

1. **참조 확인**: execution/ 모듈을 import하는 다른 코드가 있는지 grep — **완료: 0건 확인**
2. **테스트 확인**: execution/ 관련 테스트 파일 식별 → 같이 제거
   - `tests/unit/test_parallel.py` — execution/parallel.py import → **삭제 대상**
3. **__init__.py 정리**: `src/superclaude/__init__.py`에서 execution 관련 export 제거 (현재 없으므로 영향 없을 것)
4. **디렉토리 삭제**: `src/superclaude/execution/` 전체 제거
5. **pyproject.toml**: 불필요한 의존성 확인 (scipy는 dev/test optional dep — execution 전용 아님, 유지)

#### 주의사항

- `execution/reflection.py`와 `pm_agent/reflexion.py`는 이름이 비슷하지만 별개 모듈
  - reflection = 3-stage pre-execution (레거시)
  - reflexion = cross-session error learning (활성 — 유지)
- parallel.py의 Wave→Checkpoint→Wave 패턴이 다른 곳에서 참조되는지 반드시 확인 — **완료: 0건**
- `tests/unit/test_context_loader.py` 이미 존재 — 1.4에서 테스트 추가 시 기존 커버리지 확인 후 중복 방지

#### 삭제 대상 최종 목록 (5+1 파일)

```
src/superclaude/execution/__init__.py
src/superclaude/execution/parallel.py
src/superclaude/execution/reflection.py
src/superclaude/execution/self_correction.py
tests/unit/test_parallel.py
```

#### 예상 효과

- 1,336줄 코드 + 관련 테스트 파일 제거
- 커버리지 분모 감소 → 자동으로 2-3% 상승
- 유지보수 부담 감소

---

### 1.3 context_loader.py 리팩토링 (상세 설계)

**상태**: 가장 큰 단일 파일 (495줄) + skill_activator.py (210줄)의 트리거 시스템 통합

#### 현재 문제점

1. `context_loader.py` (495줄)에 3개의 독립적 관심사가 혼재
2. `skill_activator.py` (210줄)가 별도의 트리거 시스템을 운영 (hooks.json에서 별도 호출)
3. 두 스크립트가 동일한 stdin을 각각 읽고 파싱 (중복 I/O)
4. 모드 파일이 항상 full .md로 인젝션 (토큰 낭비 가능)
5. `_extract_prompt()` 함수가 양쪽에 중복 존재

#### 설계 결정 요약

| 결정 | 근거 |
|------|------|
| 통합 트리거 맵 (skills + modes + MCP + core) | 단일 우선순위 체계, 중복 제거 |
| 모드 하이브리드 로딩 (flag → full, NL → compact) | 토큰 절약 (~30-50%), 컨텍스트 효율 |
| hooks.json에서 skill_activator.py 제거 | 단일 UserPromptSubmit 훅으로 통합 |
| skill_activator.py → skill_metadata.py 리네임 | 트리거 로직 분리 후 메타데이터 유틸리티로 역할 명확화 |
| 모드 파일 kebab-case 리네임 | MODE_Brainstorming.md → brainstorming.md |

#### 리팩토링 후 파일 구조

```
src/superclaude/scripts/
├── context_loader.py          # 495줄 → ~50줄 엔트리포인트
├── context_trigger_map.py     # NEW: ~250줄, 통합 트리거 맵 + 매칭
├── context_injection.py       # NEW: ~200줄, 하이브리드 인젝션 엔진
├── context_session.py         # NEW: ~70줄, 세션 상태 + 경로 + 설정
├── skill_metadata.py          # RENAMED from skill_activator.py (~160줄, 트리거 로직 제거)
├── token_estimator.py         # 변경 없음
└── session_init.py            # 변경 없음
```

#### 1. context_loader.py — 엔트리포인트 (~50줄)

stdin 파싱과 오케스트레이션만 담당. hooks.json 경로 유지.

```python
"""UserPromptSubmit hook entrypoint. Parses stdin, orchestrates trigger matching + injection."""

def _extract_prompt(stdin_data: str) -> str:
    """JSON prompt extraction (유일한 _extract_prompt 구현)."""

def main() -> None:
    """
    Flow:
    1. Read stdin -> extract prompt
    2. context_trigger_map.match_triggers(prompt) -> list[MatchedTrigger]
    3. context_injection.generate_output(matches) -> stdout
    """
```

**Import 의존성**: `context_trigger_map`, `context_injection`, `context_session`

#### 2. context_trigger_map.py — 통합 트리거 맵 + 매칭 (~250줄)

skill_activator.py의 트리거 패턴 + context_loader.py의 TRIGGER_MAP을 하나로 통합.

```python
"""Unified trigger map: skills > modes > MCP > core."""

from enum import IntEnum
from dataclasses import dataclass

class TriggerCategory(IntEnum):
    SKILL = 0      # 최고 우선순위
    MODE = 1
    MCP = 2
    CORE = 3

@dataclass
class MatchedTrigger:
    category: TriggerCategory
    context_file: str           # 상대 경로 (e.g., "modes/brainstorming.md")
    is_explicit_flag: bool      # --brainstorm (True) vs "brainstorm ideas" (False)

    @property
    def sort_key(self) -> tuple[int, int]:
        return (self.category.value, 0 if self.is_explicit_flag else 1)
```

**통합 트리거 정의** — 각 엔트리: (compiled_regex, category, context_file, is_flag_pattern)

```python
SKILL_TRIGGERS = [
    # confidence-check (기존 skill_activator.py에서 이동)
    (r"(check confidence|confidence check|/confidence-check|--confidence)", "skills/hint:confidence-check", True),
    (r"(am i ready|ready to start|verify before|before implementing)", "skills/hint:confidence-check", False),
    (r"(readiness check|readiness-check)", "skills/hint:confidence-check", True),
    # 향후 Phase 2 전환 스킬들이 여기에 추가
]

MODE_TRIGGERS = [
    # 명시적 플래그 (is_flag=True) — full .md 인젝션
    (r"--brainstorm|--bs", "modes/brainstorming.md", True),
    (r"--research", "modes/deep-research.md", True),
    (r"--introspect", "modes/introspection.md", True),
    (r"--orchestrate", "modes/orchestration.md", True),
    (r"--task-manage", "modes/task-management.md", True),
    (r"--uc|--ultracompressed|--token-efficient|--safe-mode", "modes/token-efficiency.md", True),
    (r"--business-panel", "modes/business-panel.md", True),
    # 자연어 트리거 (is_flag=False) — compact 인젝션
    (r"brainstorm|ideate|explore ideas", "modes/brainstorming.md", False),
    (r"deep.?research|investigate thoroughly|comprehensive search", "modes/deep-research.md", False),
    (r"introspect|self.?analysis|analyze reasoning", "modes/introspection.md", False),
    (r"orchestrat|coordinate|multi.?tool", "modes/orchestration.md", False),
    (r"task.?manage", "modes/task-management.md", False),
    (r"business.?panel|expert.?panel|christensen|porter|drucker|godin|taleb", "modes/business-panel.md", False),
    # token-efficiency: 자연어 트리거에서도 full 인젝션 (심볼 테이블 필수)
    (r"token.?efficient", "modes/token-efficiency.md", True),  # is_flag=True로 강제
]

MCP_TRIGGERS = [
    # 기존 TRIGGER_MAP MCP 엔트리 전부, 경로 동일
    (r"--c7|--context7", "mcp/MCP_Context7.md", True),
    (r"context7|c7|library docs|framework docs", "mcp/MCP_Context7.md", False),
    # ... (8개 MCP 서버 모두)
]

CORE_TRIGGERS = [
    (r"business.?symbol|strategic.?symbol|--structured", "core/BUSINESS_SYMBOLS.md", False),
    (r"research.?config|hop.?config", "modes/research-config.md", False),
]

COMPOSITE_FLAGS = {
    "--frontend-verify": [("mcp/MCP_Playwright.md", TriggerCategory.MCP), ...],
    "--all-mcp": [("mcp/MCP_Context7.md", TriggerCategory.MCP), ...],
}
```

```python
def match_triggers(prompt: str) -> list[MatchedTrigger]:
    """
    통합 트리거 매칭.

    처리 순서:
    1. --no-mcp 체크 (MCP 카테고리 전체 억제)
    2. 복합 플래그 확장 (--frontend-verify, --all-mcp)
    3. SKILL -> MODE -> MCP -> CORE 순으로 패턴 매칭
    4. 세션 캐시 기반 중복 제거 (context_session.get_loaded_contexts)
    5. 동일 파일 flag+NL 양쪽 매칭 시 flag만 채택
    6. sort_key 기준 정렬 후 반환

    Returns:
        list[MatchedTrigger] sorted by (category, is_explicit_flag)
    """
```

**우선순위 체계**:

| 순위 | 카테고리 | 플래그 | 인젝션 모드 | 예시 |
|------|----------|--------|-------------|------|
| 0-a | SKILL | explicit | hint | `--confidence`, `/confidence-check` |
| 0-b | SKILL | natural | hint | "am i ready to start" |
| 1-a | MODE | explicit (flag) | full .md | `--brainstorm` |
| 1-b | MODE | natural | compact | "brainstorm ideas" |
| 2-a | MCP | explicit (flag) | instruction/full | `--c7`, `--serena` |
| 2-b | MCP | natural | instruction/full | "library docs" |
| 3 | CORE | any | instruction | "business symbols" |

**중복 방지 규칙**: 동일 context_file에 대해 flag + NL 양쪽 매칭 시, flag 버전만 채택 (full 인젝션이 compact를 대체).

#### 3. context_injection.py — 하이브리드 인젝션 엔진 (~200줄)

매칭 결과를 받아 적절한 형식으로 stdout 출력.

```python
"""Hybrid injection engine: full .md, compact instruction, or skill hint."""

# MCP 컴팩트 인스트럭션 (기존 INSTRUCTION_MAP 이동)
MCP_INSTRUCTION_MAP = {
    "mcp/MCP_Context7.md": "Context7 MCP: resolve-library-id -> query-docs ...",
    "mcp/MCP_Sequential.md": "Sequential Thinking MCP: sequentialthinking tool ...",
    "mcp/MCP_Playwright.md": "Playwright MCP: Browser automation and E2E testing ...",
    "mcp/MCP_Morphllm.md": "Morphllm MCP: Pattern-based bulk code transformations ...",
    "mcp/MCP_Magic.md": "Magic MCP (21st.dev): Modern UI component generation ...",
    "mcp/MCP_Chrome-DevTools.md": "Chrome DevTools MCP: Core Web Vitals ...",
    # Serena, Tavily: NOT in map -> full .md 인젝션 유지
}

# 모드 컴팩트 인스트럭션 (NEW)
MODE_COMPACT_MAP = {
    "modes/brainstorming.md": (
        "Brainstorming mode: Socratic probing questions, non-presumptive collaborative "
        "discovery. Synthesize insights into structured briefs. Never prescribe solutions "
        "before fully exploring the problem space."
    ),
    "modes/deep-research.md": (
        "Deep Research mode: Systematic investigation with evidence chains and inline citations. "
        "Activates deep-research-agent + Tavily search. Progressive: broad first, then drill. "
        "Every claim needs verification."
    ),
    "modes/introspection.md": (
        "Introspection mode: Self-analysis and reasoning transparency. Expose thinking chain, "
        "identify biases, track error patterns."
    ),
    "modes/orchestration.md": (
        "Orchestration mode: Multi-tool coordination and parallel execution. Batch independent "
        "operations, optimize tool selection matrix."
    ),
    "modes/task-management.md": (
        "Task Management mode: Progressive enhancement with delegation. Use TaskCreate/TaskUpdate "
        "for tracking. Delegate when >3 steps, >2 dirs, or >3 files."
    ),
    "modes/business-panel.md": (
        "Business Panel mode: Multi-expert synthesis (Christensen/disruption, Porter/competitive, "
        "Drucker/management, Godin/marketing, Taleb/risk). Use business symbols for analysis."
    ),
    # token-efficiency: NOT in compact map -> 항상 full .md (심볼/약어 테이블이 핵심)
}

# 코어 + 스킬 인스트럭션
CORE_INSTRUCTION_MAP = {
    "core/BUSINESS_SYMBOLS.md": "Business symbols + expert selection: ...",
}

SKILL_HINT_MAP = {
    "skills/hint:confidence-check": (
        "INSTRUCTION: Use /confidence-check skill before implementation. "
        "Assess: duplicates, architecture, docs, OSS refs, root cause."
    ),
}
```

```python
def _resolve_injection_mode(trigger: MatchedTrigger) -> str:
    """
    MatchedTrigger -> 인젝션 모드 결정.
    Returns: "full" | "compact" | "instruction" | "hint"

    Rules:
    - SKILL -> "hint" (항상)
    - MODE + explicit flag -> "full"
    - MODE + NL + in MODE_COMPACT_MAP -> "compact"
    - MODE + NL + not in MODE_COMPACT_MAP -> "full" (token-efficiency 등)
    - MCP + in MCP_INSTRUCTION_MAP -> "instruction"
    - MCP + not in map -> "full" (Serena, Tavily)
    - CORE -> "instruction"
    """

def generate_output(matches: list[MatchedTrigger]) -> None:
    """
    매칭 결과를 stdout으로 출력.

    출력 형식:
    - hint: 단순 텍스트 (스킬 힌트)
    - instruction: <sc-context src="...">instruction</sc-context>
    - compact: <sc-context src="..." mode="compact">instruction</sc-context>
    - full: <context-inject file="..." tokens="~N">full content</context-inject>

    토큰 예산: MAX_TOKENS_ESTIMATE 초과 시 낮은 우선순위부터 스킵.
    MCP 폴백 알림: MCP 인젝션 시 가용성 체크 (hooks.mcp_fallback).
    스킬 서머리: 프롬프트마다 1회 (SHOW_SKILLS_SUMMARY 의존).
    """
```

#### 4. context_session.py — 세션 상태 + 설정 (~70줄)

모든 상태/경로/설정을 한 곳에서 관리. 다른 3개 모듈의 리프 의존성.

```python
"""Session state, path resolution, and configuration constants."""

# --- 설정 상수 (환경 변수에서 읽기) ---
INJECT_MODE: bool           # CLAUDE_CONTEXT_INJECT (default: True)
MAX_TOKENS_ESTIMATE: int    # CLAUDE_CONTEXT_MAX_TOKENS (default: 8000)
USE_INSTRUCTIONS: bool      # CLAUDE_CONTEXT_USE_INSTRUCTIONS (default: True)
SHOW_SKILLS_SUMMARY: bool   # CLAUDE_SHOW_SKILLS (default: True)
CHARS_PER_TOKEN: int = 4

# --- 경로 해석 ---
def get_base_path() -> Path:
    """SUPERCLAUDE_PATH -> ./.claude/superclaude -> ~/.claude/superclaude"""

# --- 세션 캐시 ---
SESSION_ID: str             # hashlib.md5(cwd) 기반
CACHE_FILE: Path            # ~/.claude/.superclaude_hooks/claude_context_{SESSION_ID}.txt

def get_loaded_contexts() -> set[str]: ...
def mark_as_loaded(contexts: str | list[str]) -> None: ...
def estimate_tokens(content: str) -> int: ...
```

#### 5. skill_activator.py → skill_metadata.py 리네임 (~160줄)

트리거 로직 제거, 메타데이터 유틸리티만 유지.

| 유지 | 제거 (이동 대상) |
|------|------------------|
| `get_skill_directories()` | `check_skill_triggers()` → context_trigger_map SKILL_TRIGGERS |
| `find_skill_manifest()` | `_extract_prompt()` → context_loader.py 단일 구현 |
| `get_agent_for_skill()` | `main()` → hooks.json에서 제거 |
| `should_fork_context()` | |
| `get_skill_inline_hooks()` | |
| `VALID_AGENTS` | |

#### 모드 파일 kebab-case 리네임

| 현재 | 변경 후 |
|------|---------|
| `modes/MODE_Brainstorming.md` | `modes/brainstorming.md` |
| `modes/MODE_DeepResearch.md` | `modes/deep-research.md` |
| `modes/MODE_Introspection.md` | `modes/introspection.md` |
| `modes/MODE_Orchestration.md` | `modes/orchestration.md` |
| `modes/MODE_Task_Management.md` | `modes/task-management.md` |
| `modes/MODE_Token_Efficiency.md` | `modes/token-efficiency.md` |
| `modes/MODE_Business_Panel.md` | `modes/business-panel.md` |
| `modes/RESEARCH_CONFIG.md` | `modes/research-config.md` |
| `modes/README.md` | `modes/README.md` (유지) |

**영향 범위**: context_trigger_map.py (신규 파일, 새 경로 사용), modes/README.md (내부 참조 업데이트), install_paths.py (COMPONENTS["modes"] 소스 경로 동일, 파일명만 변경)

#### hooks.json 변경

```diff
 "UserPromptSubmit": [
   {
     "hooks": [
-      {
-        "type": "command",
-        "command": "python3 {{SCRIPTS_PATH}}/skill_activator.py",
-        "timeout": 5
-      },
       {
         "type": "command",
         "command": "python3 {{SCRIPTS_PATH}}/context_loader.py",
         "timeout": 5
       }
     ]
   }
 ]
```

**효과**: UserPromptSubmit당 프로세스 1개, stdin 1회 파싱, 단일 우선순위 체계

#### 데이터 흐름

```
stdin (JSON: {"prompt": "..."})
  |
  v
context_loader.py (main)
  |-- _extract_prompt(stdin) -> prompt: str
  |
  |-- context_trigger_map.match_triggers(prompt)
  |     |-- context_session.get_loaded_contexts() -> dedup set
  |     |-- SKILL_TRIGGERS 매칭 (category=0)
  |     |-- MODE_TRIGGERS 매칭 (category=1)
  |     |-- MCP_TRIGGERS 매칭 (category=2, --no-mcp 체크)
  |     |-- CORE_TRIGGERS 매칭 (category=3)
  |     |-- COMPOSITE_FLAGS 확장
  |     |-- 중복 제거 (동일 파일: flag > NL)
  |     +-- 정렬 -> list[MatchedTrigger]
  |
  |-- context_injection.generate_output(matches)
  |     |-- 스킬 서머리 (SHOW_SKILLS_SUMMARY)
  |     |-- MCP 폴백 알림 (hooks.mcp_fallback)
  |     |-- 각 match: _resolve_injection_mode -> hint|instruction|compact|full
  |     |-- 토큰 예산 추적 (MAX_TOKENS_ESTIMATE)
  |     +-- context_session.mark_as_loaded(new_contexts)
  |
  +-- stdout
```

#### 마이그레이션 실행 순서

1. `context_session.py` 생성 (의존성 없음, 리프 모듈)
2. `context_trigger_map.py` 생성 (`context_session` import)
3. `context_injection.py` 생성 (`context_session` + `hooks.mcp_fallback` import)
4. `context_loader.py` 리팩토링 (3개 모듈 import, ~50줄로 축소)
5. 모드 파일 kebab-case 리네임 (`git mv`)
6. `skill_activator.py` → `skill_metadata.py` 리네임 + 트리거/main 제거
7. `hooks.json`에서 `skill_activator.py` 엔트리 제거
8. `install_settings.py`의 훅 마커 업데이트 (skill_activator 참조 제거)
9. `modes/README.md` 내부 참조 업데이트
10. 기존 테스트 (`test_context_loader.py`) 업데이트 + 신규 테스트 추가

#### 주의사항

- hooks.json의 `"command": "python3 {{SCRIPTS_PATH}}/context_loader.py"` 경로 유지
- 환경 변수 인터페이스 변경 없음 (`CLAUDE_CONTEXT_INJECT`, `CLAUDE_CONTEXT_MAX_TOKENS` 등)
- MCP fallback import 경로 유지 (`hooks.mcp_fallback`)
- `skill_metadata.py`를 import하는 기존 코드 경로 확인 필요 (inline_hooks.py 등)
- `token-efficiency.md`는 compact 미지원 (심볼/약어 테이블이 핵심) — 항상 full .md
- Serena, Tavily MCP는 기존과 동일하게 full .md 인젝션 유지 (행동 패턴/통합 플로우 포함)
- `_extract_prompt()` 중복 제거: context_loader.py에만 유일한 구현 유지

---

### 1.4 scripts/ 핵심 테스트 추가

**대상**: 0% 커버리지인 scripts/ 중 가장 중요한 3개

> 참고: `tests/unit/test_context_loader.py` 이미 존재. 아래 테스트 추가 시 기존 파일의 커버리지를 먼저 확인하고, 중복되지 않는 케이스만 추가할 것.

#### context_injection 테스트 (`tests/unit/test_context_injection.py`) — 1.3 리팩토링 후

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_injection_mode_full_md` | MODE + explicit flag → full .md 인젝션 |
| `test_injection_mode_compact` | MODE + NL trigger → compact instruction 인젝션 |
| `test_injection_mode_instruction` | MCP → instruction string 인젝션 |
| `test_injection_mode_hint` | SKILL → hint 텍스트 출력 |
| `test_token_efficiency_always_full` | token-efficiency는 NL에서도 full .md |
| `test_serena_tavily_always_full` | Serena/Tavily MCP는 항상 full .md |
| `test_token_limit_enforcement` | MAX_TOKENS 초과 시 낮은 우선순위부터 스킵 |
| `test_session_dedup` | 동일 컨텍스트 중복 인젝션 방지 |
| `test_skills_summary_output` | 기존 format_skills_summary 테스트 (test_context_loader.py에서 이동) |

#### session_init 테스트 (`tests/unit/test_session_init.py`)

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_hook_tracker_init` | 세션 ID 생성 확인 |
| `test_old_session_cleanup` | 24h 이상 세션 정리 |
| `test_git_status_format` | git 상태 포맷팅 |
| `test_pr_status_check` | PR 리뷰 상태 표시 |

#### skill_metadata 테스트 (`tests/unit/test_skill_metadata.py`) — 리네임 반영

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_skill_directory_discovery` | 스킬 디렉토리 검색 |
| `test_agent_routing` | 스킬의 agent 필드 → 유효 에이전트 라우팅 |
| `test_invalid_agent_rejected` | 잘못된 에이전트 이름 거부 |
| `test_fork_context_detection` | context: fork 감지 |

#### context_trigger_map 테스트 (`tests/unit/test_context_trigger_map.py`) — 1.3 리팩토링 후

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_skill_trigger_matching` | SKILL_TRIGGERS 패턴 매칭 (기존 skill_activator에서 이동) |
| `test_mode_flag_vs_natural_language` | --brainstorm (flag) vs "brainstorm ideas" (NL) 구분 |
| `test_duplicate_flag_nl_dedup` | 동일 파일 flag+NL 동시 매칭 시 flag만 채택 |
| `test_priority_ordering` | SKILL > MODE > MCP > CORE 정렬 확인 |
| `test_composite_flag_expansion` | --frontend-verify → 3개 MCP 확장 |
| `test_no_mcp_suppression` | --no-mcp 시 MCP 카테고리 전체 억제 |

---

### 1.5 교차 디렉토리 통합 테스트

**설계 문서**: `docs/test-design-cross-ref-integration.md` (상세 스펙 별도 관리)
**위치**: `tests/integration/test_cross_directory_refs.py`

6개 디렉토리(core/, agents/, modes/, mcp/, hooks/, scripts/) 간 교차 참조 무결성 검증:

| 테스트 클래스 | 검증 대상 | 예상 테스트 수 |
|--------------|----------|--------------|
| `TestPersonaAbbreviations` | FLAGS.md persona_index → 에이전트 파일 존재 | ~10 |
| `TestMCPWiring` | FLAGS.md MCP 플래그 → MCP 문서 존재, 에이전트 mcp 속성 → 선언 | ~12 |
| `TestTriggerMapPaths` | TRIGGER_MAP 경로 → 실제 파일 존재 | ~15 |
| `TestHooksScriptPaths` | hooks.json 스크립트 경로 → 실제 스크립트 존재 | ~7 |
| `TestAgentModeMapping` | 에이전트 permissionMode → FLAGS.md 선언 | ~8 |
| `TestSkillAgentRouting` | SKILL.md agent 필드 → VALID_AGENTS 포함 | ~5 |
| `TestInstallPathsMapping` | COMPONENTS dict → 소스 디렉토리 존재 | ~6 |
| `TestModeFileNaming` | 모드 파일 kebab-case 컨벤션 | ~8 |
| `TestCoreImportChain` | CLAUDE_SC.md → core/ @-참조 유효성 | ~5 |

> 참고: `skill_activator.VALID_AGENTS`에 7개 에이전트 누락 발견 (business-panel-experts, simplicity-guide, self-review, requirements-analyst, socratic-mentor, learning-guide, technical-writer). 1.3 리팩토링의 skill_metadata.py에서 수정.

---

### 1.6 pm_agent 테스트 보강

#### task_cleanup.py (현재 0%)

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_cleanup_stale_tasks` | 24h 초과 태스크 정리 |
| `test_cleanup_preserves_active` | 활성 태스크 보존 |
| `test_cleanup_empty_list` | 빈 태스크 리스트 처리 |

#### token_budget.py (현재 25%)

| 테스트 케이스 | 설명 |
|--------------|------|
| `test_budget_simple` | simple 복잡도 → 200 토큰 |
| `test_budget_medium` | medium → 1000 |
| `test_budget_complex` | complex → 2500 |
| `test_budget_from_marker` | pytest marker에서 복잡도 추출 |

### Phase 1 완료 기준

- [ ] 1.1: ANALYSIS_REPORT moderate 모두 resolved (Finding 2 false → 삭제 완료)
- [ ] 1.2: execution/ 디렉토리 + test_parallel.py 완전 제거
- [ ] 1.3: context_loader.py → 4개 파일 분리 + skill_activator 통합 + mode kebab-case 리네임
- [ ] 1.3: hooks.json에서 skill_activator.py 제거 (단일 UserPromptSubmit 훅)
- [ ] 1.4: scripts/ 핵심 테스트 추가: context_trigger_map, context_injection, skill_metadata
- [ ] 1.5: 교차 디렉토리 통합 테스트 (`test_cross_directory_refs.py`)
- [ ] 1.6: pm_agent 테스트 보강 (task_cleanup, token_budget)
- [ ] 전체 테스트 green
- [ ] 커버리지 ≥ 50%

---

## 커맨드 → 스킬 전환 전략

> Anthropic "Don't Build Agents, Build Skills Instead" (AI Engineering Code Summit) 철학 반영
> Phase 2의 핵심 전략으로 채택

### 네이밍 컨벤션: `sc:` prefix

SuperClaude에서 만든 스킬과 Anthropic 공식 스킬을 구분하기 위해 `sc:` prefix 사용:

| 출처 | prefix | 예시 | 호출 |
|------|--------|------|------|
| **SuperClaude** | `sc:` | sc:ship, sc:git, sc:test | `/sc:ship`, auto-trigger |
| **Anthropic 공식** | 없음 | code-review, skill-creator | `/code-review`, auto-trigger |

이점:
- 네임스페이스 충돌 방지 (SuperClaude `sc:review` vs Anthropic `code-review`)
- 기존 `/sc:name` 커맨드 호출과 자연스러운 연속성
- 스킬 출처 즉시 식별 가능

### Anthropic 공식 스킬 활용

Anthropic이 공식 제공하는 스킬은 직접 구현하지 않고 활용:

| 공식 스킬 | 용도 | SuperClaude 전략 |
|-----------|------|-----------------|
| `skill-creator` | 스킬 생성/수정/평가 | 그대로 사용 — Phase 4.2 자기 확장의 enabler |
| `code-review` | PR diff 코드 리뷰 | 그대로 사용 — 별도 구현 불필요 |
| (향후 추가) | — | 공식 스킬 우선, 부족하면 sc: 스킬로 보완 |

> **원칙**: Anthropic이 공식 제공하는 영역은 공식 스킬 사용. SuperClaude는 프로젝트 특화 워크플로(git, test, build 등)에 집중.

### 근거

기존 battle-tested 커맨드를 스킬로 전환하는 것이 신규 스킬 개발보다 ROI가 높은 이유:

1. **검증된 워크플로**: 커맨드는 이미 사용자 피드백을 거친 실전 워크플로
2. **스킬 이점 획득**: auto-triggering (description 기반), 훅 통합, 스크립트 실행, 도구 제한, 에이전트 라우팅
3. **Anthropic 아키텍처 정합성**: 모듈식 확장 구조와 직접 대응

### 커맨드 vs 스킬 아키텍처

```
Command (.md):  description, allowed-tools, model, argument-hint → 사용자 호출 /sc:name
Skill (SKILL.md): name, description (트리거 구문), version, metadata → auto-triggered + /sc:name
```

### 전환 분류 (30개 커맨드 분석)

| 분류 | 수 | 커맨드 |
|------|-----|--------|
| 스킬 전환 후보 (강) | 8 | git, test, troubleshoot, cleanup, build, estimate, document, design |
| 커맨드 유지 | 16 | agent, pm, spawn, task, workflow, business-panel, spec-panel, research, help, sc, implement, improve, analyze, load, save, select-tool |
| 보류 (중간) | 6 | brainstorm, index, index-repo, recommend, explain, reflect |

### 전환 판단 기준

**스킬 전환 적합**: 독립적 워크플로, 명확한 트리거 구문, 자동 감지 이점이 큰 경우
**커맨드 유지 적합**: 오케스트레이션 역할, 다른 커맨드 호출, 사용자 명시적 의도 필요

### 하위 호환성 전략

원본 커맨드 .md 파일을 thin stub으로 유지하여 `/sc:name` 호출을 보존. 스킬이 auto-triggering 담당.

```markdown
<!-- commands/git.md (stub) -->
---
description: "Git operations — redirected to sc:git skill"
allowed-tools: []
---
> This command has been migrated to the `sc:git` skill.
> Use `/sc:git` directly or let it auto-trigger from your prompt.
```

---

## Phase 2: 스킬 생태계 확장

> 목표: sc: 스킬 3개 → 11개 (기존 3 리네임 + 8 전환), 스킬 품질 보증 체계
> 선행 조건: Phase 1 완료
> 근거: Anthropic "Don't Build Agents, Build Skills Instead" 철학
> 참고: code-review, skill-creator는 Anthropic 공식 스킬 사용 (직접 구현 안 함)

### 2.1 스킬 테스트 프레임워크

**배경**: Anthropic 공식 가이드의 "평가 우선" 원칙. 스킬을 만들기 전에 능력 격차를 식별하고, 만든 후에는 품질을 보증해야 함. 모든 전환/신규 스킬의 선행 조건.

#### 구현 범위

```
src/superclaude/skills/
├── _testing/                     # NEW: 스킬 테스트 프레임워크
│   ├── __init__.py
│   ├── skill_linter.py           # SKILL.md 유효성 검증
│   ├── trigger_validator.py      # 트리거 충돌 감지
│   └── skill_test_runner.py      # 스킬 통합 테스트 실행
```

#### skill_linter.py 스펙

검증 항목:

| 규칙 | 설명 | 심각도 |
|------|------|--------|
| `frontmatter-required` | name, description 필수 | ERROR |
| `frontmatter-types` | metadata 필드 타입 검증 | ERROR |
| `component-structure` | `<component type="skill">` 래핑 | WARNING |
| `flow-section` | `<flow>` 섹션 존재 | WARNING |
| `bounds-section` | `<bounds>` 섹션 존재 | INFO |
| `examples-section` | `<examples>` 섹션 존재 | INFO |
| `file-references` | 참조된 파일 실제 존재 여부 | ERROR |

```python
# 예시 인터페이스
class SkillLintResult:
    skill_name: str
    errors: list[LintIssue]
    warnings: list[LintIssue]
    info: list[LintIssue]
    is_valid: bool  # errors == 0

def lint_skill(skill_dir: Path) -> SkillLintResult: ...
def lint_all_skills(skills_root: Path) -> list[SkillLintResult]: ...
```

#### trigger_validator.py 스펙

- 모든 설치된 스킬의 description에서 트리거 키워드 추출
- 스킬 간 트리거 중복/충돌 감지
- 커맨드와 스킬 간 트리거 충돌 감지

```python
class TriggerConflict:
    skill_a: str
    skill_b: str
    conflicting_triggers: list[str]
    severity: Literal["overlap", "exact_match"]

def validate_triggers(skills_root: Path, commands_root: Path) -> list[TriggerConflict]: ...
```

#### CLI 통합

```bash
superclaude doctor --skills        # 기존 doctor에 스킬 검증 추가
superclaude skills lint            # 전체 스킬 린트
superclaude skills lint <name>     # 단일 스킬 린트
```

---

### 2.2 커맨드→스킬 전환 Wave 1 — P0+P1

**대상**: git, test, troubleshoot, cleanup (가장 독립적이고 auto-trigger 이점이 큰 4개)

#### 전환 템플릿

```yaml
# skills/sc-{name}/SKILL.md
---
name: sc:{name}
description: This skill should be used when the user asks to "{trigger1}", "{trigger2}", "{trigger3}".
version: 1.0.0
metadata:
  context: inline
  agent: {agent-from-command}
---
<component name="sc:{name}" type="skill">
  # Content migrated from commands/{name}.md
  # + added: <flow>, <bounds>, <exclusions> where needed
</component>
```

#### Wave 1 전환 스펙

| 커맨드 | → 스킬 | 에이전트 | 핵심 추가사항 |
|--------|--------|----------|--------------|
| `/sc:git` | `sc:git` | general-purpose | 브랜치 검증 훅, safety checks (sc:ship 확장) |
| `/sc:test` | `sc:test` | quality-engineer | 테스트 러너 감지, 커버리지 리포팅, 환경 설정 |
| `/sc:troubleshoot` | `sc:troubleshoot` | root-cause-analyst | 3-cycle 가설 제한, 에스컬레이션 게이트 |
| `/sc:cleanup` | `sc:cleanup` | refactoring-expert | 안전성 검증 훅, before/after diff |

---

#### 2.2.1 프로토타입: sc:git 상세 설계 (Wave 1 템플릿)

> 이 설계는 8개 전환 모두의 레퍼런스 구현으로 사용됨.
> 소스: `src/superclaude/commands/git.md` (94줄)
> 대상: `src/superclaude/skills/sc-git/SKILL.md`

##### A. SKILL.md 전체 스펙

```yaml
---
name: sc:git
description: >-
  This skill should be used when the user asks to
  "commit my changes with a conventional message",
  "check PR review status",
  "push changes to remote",
  "create a feature branch",
  "resume work from a PR",
  "smart commit",
  "git workflow operations",
  "branch naming conventions",
  "recover from git conflicts".
version: 1.0.0
metadata:
  context: inline
  agent: general-purpose
  mcp: seq
  allowed-tools:
    - Bash
    - Read
    - Grep
    - Glob
  hooks:
    PreToolUse:
      - matcher: "Bash"
        hooks:
          - type: command
            command: "python3 {{SKILLS_PATH}}/sc-git/scripts/validate_git_safety.py"
            timeout: 5
---
```

```xml
<component name="sc:git" type="skill">

  <role>
    <mission>Git operations with intelligent commit messages and workflow optimization</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive] [--pr-status] [--from-pr PR#|URL]</syntax>

  <flow>
    1. Analyze: Run `git status` + `git diff --stat` to assess repo state and changes
    2. Validate: Check operation appropriateness (branch naming, destructive op guards)
    3. Execute: Perform git command with automation (smart commits, branch conventions)
    4. Optimize: Apply conventional commit patterns, suggest workflow improvements
    5. Report: Summarize results, recommend next steps, show handoff options
  </flow>

  <patterns>
    - SmartCommit: Analyze `git diff --cached` content, generate conventional commit message (feat/fix/docs/refactor/test/chore), present for user approval
    - Status: Parse `git status` + `git log --oneline -5`, produce actionable recommendations
    - Branch: Enforce naming conventions (feature/*, fix/*, docs/*, refactor/*, chore/*), warn on master/main direct work
    - Recovery: Guide conflict resolution with `git diff --name-only --diff-filter=U`, assist with `git stash` workflows
    - PRStatus: Run `gh pr view --json state,reviewDecision,isDraft`, map to status indicators (APPROVED/CHANGES_REQUESTED/PENDING/DRAFT)
    - FromPR: Accept PR number or URL, checkout branch via `gh pr checkout`, load PR description as session context
  </patterns>

  <safety>
    <safe>status, log, diff, add, commit, pull, fetch, branch, stash, pr-status, tag</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts, checkout -- (destructive), clean -f, branch -D</approval_required>
    <blocked>push --force to main/master (always blocked, no override)</blocked>
  </safety>

  <boundary_with_ship note="sc:ship vs sc:git">
    sc:ship = opinionated delivery workflow: stage + commit + push + optional PR (focused automation)
    sc:git = broad git operations toolkit: status, branching, recovery, PR status, smart commit, from-PR
    Overlap: both generate conventional commits. Distinction: sc:ship is "ship it now", sc:git is "git operations".
    Handoff: sc:git delegates to sc:ship when user intent is clearly "deliver these changes".
  </boundary_with_ship>

  <examples>
| Input | Output |
|-------|--------|
| `status` | State analysis + actionable recommendations |
| `commit --smart-commit` | Analyze diff, generate conventional commit, present for approval |
| `merge feature-branch --interactive` | Guided merge with conflict resolution |
| `--pr-status` | Current branch PR review state with color indicators |
| `--from-pr 123` | Checkout PR branch, load context, resume session |
| (auto-trigger) "commit my changes" | Skill activates, runs SmartCommit pattern |
| (auto-trigger) "what's the PR status" | Skill activates, runs PRStatus pattern |

  <example name="force-push-main" type="error-path">
    <input>/sc:git push --force origin main</input>
    <why_wrong>Force-pushing to main/master destroys team members' work and is irreversible.</why_wrong>
    <correct>Create a feature branch, push there, then open a PR for main.</correct>
  </example>
  </examples>

  <bounds will="intelligent git ops|conventional commits|workflow guidance|PR status checks|branch management|conflict recovery" wont="modify git config without auth|force push without confirm|complex merges requiring manual resolution|source code edits (use Edit tool)" fallback="Ask user for guidance when operation is ambiguous or destructive"/>

  <handoff next="/sc:test /sc:build /sc:ship"/>
</component>
```

##### B. 트리거 구문 설계

> description 필드가 Claude Code의 auto-trigger 판단 기준 (v2.1.3+).
> 트리거 문구는 사용자 자연어 프롬프트와 매칭되어 스킬을 자동 활성화.

| 트리거 문구 | 매칭 의도 | 오발동 리스크 |
|------------|----------|-------------|
| "commit my changes with a conventional message" | 스마트 커밋 | 낮음 — "commit" + "changes" 조합 |
| "check PR review status" | PR 상태 확인 | 낮음 — "PR" + "status" 조합 |
| "push changes to remote" | 리모트 푸시 | 낮음 — "push" + "remote" 조합 |
| "create a feature branch" | 브랜치 생성 | 낮음 — "create" + "branch" 조합 |
| "resume work from a PR" | PR 기반 작업 재개 | 낮음 — "resume" + "PR" 조합 |
| "smart commit" | 직접 키워드 | 매우 낮음 |
| "git workflow operations" | 포괄적 git 작업 | 중간 — "git" 단독은 제외 |
| "branch naming conventions" | 브랜치 네이밍 | 낮음 |
| "recover from git conflicts" | 충돌 복구 | 낮음 — "conflicts" + "recover" 조합 |

**의도적으로 제외한 트리거:**
- "git" 단독 — 너무 포괄적, 대화 중 언급만으로 발동 위험
- "status" 단독 — 서버 상태, 태스크 상태 등과 혼동
- "merge" 단독 — 코드 머지 외 다른 맥락 가능
- "rebase" — 위험한 작업, 명시적 호출만 허용

##### C. 에이전트 라우팅 결정

| 옵션 | 장점 | 단점 | 결정 |
|------|------|------|------|
| `general-purpose` | sc:ship과 일관성, git은 범용 도구 | 실제 에이전트 파일 없음 (convention) | **선택** |
| `devops-architect` | 실제 에이전트 존재, CI/CD 전문성 | git 기본 작업에 과도한 전문화 | 보류 |
| 없음 (omit) | 가장 단순 | auto-trigger 시 에이전트 컨텍스트 부재 | 부적합 |

> `general-purpose`는 Claude Code가 기본 모델 동작을 사용하는 convention.
> 에이전트 파일이 없어도 frontmatter의 `agent:` 필드는 스킬 분류 목적으로 유효.

##### D. 커맨드 stub (commands/git.md 교체)

```markdown
---
description: "Git operations — redirected to sc:git skill"
allowed-tools: []
---
> This command has been migrated to the `sc:git` skill.
> Use `/sc:git` directly or let it auto-trigger from your prompt.
>
> Auto-triggers: "commit my changes", "check PR status", "push changes",
> "create a branch", "resume from PR", "smart commit"
>
> The skill adds: auto-triggering, git safety hooks, tool restrictions,
> and all original command capabilities.
```

**stub 설계 원칙:**
- `allowed-tools: []` — stub 자체는 도구를 사용하지 않음
- description은 리다이렉트 안내 + 발견 용이성
- 사용자가 `/sc:git`을 타이핑하면 스킬이 로드됨 (stub 대신)
- stub은 스킬을 찾지 못한 경우의 fallback 안내

##### E. 커맨드 대비 스킬 추가사항

| 기능 | 커맨드 (현재) | 스킬 (전환 후) |
|------|-------------|---------------|
| 호출 방식 | `/sc:git` 수동만 | `/sc:git` + 자연어 auto-trigger |
| 안전성 | `<safety_rules>` 텍스트만 | PreToolUse 훅으로 실행 전 검증 |
| 도구 제한 | `<tools>` 권장 목록 | `allowed-tools` 강제 제한 |
| 에이전트 | 없음 | `agent: general-purpose` |
| MCP 선언 | `<mcp servers="seq"/>` | `mcp: seq` (frontmatter 선언) |
| 세션 훅 | 없음 | PreToolUse: validate_git_safety.py |
| sc:ship 경계 | 암시적 | `<boundary_with_ship>` 명시 |
| 핸드오프 | `/sc:test /sc:build` | `/sc:test /sc:build /sc:ship` |

##### F. 훅 스크립트 스펙: validate_git_safety.py

```
위치: src/superclaude/skills/sc-git/scripts/validate_git_safety.py
실행 시점: PreToolUse (matcher: "Bash")
동작: stdin으로 tool_input JSON 수신, git 명령어 안전성 검증
```

**검증 로직:**

| 패턴 | 동작 | exit code |
|------|------|-----------|
| `git push --force.*main\|master` | BLOCK + stderr 경고 | 2 |
| `git reset --hard` | WARN + stderr 안내 (진행 허용) | 0 |
| `git clean -f` | WARN + stderr 안내 | 0 |
| `git checkout -- .` | WARN + stderr 안내 | 0 |
| `git branch -D` | WARN + stderr 안내 | 0 |
| `git rebase` (non-interactive) | WARN + stderr 안내 | 0 |
| 기타 git 명령 | PASS (silent) | 0 |
| 비-git 명령 | PASS (silent) | 0 |

**global hooks.json PreToolUse/Bash와의 관계:**
- global 훅: `rm -rf /` + `git push --force main/master` 차단 (범용 안전망)
- sc:git 훅: 위 테이블의 git-specific 검증 (스킬 활성 시에만 동작)
- 중복 차단 문제 없음: 두 훅 모두 동일 명령을 차단해도 첫 번째 차단에서 중단

**스크립트 인터페이스:**

```python
#!/usr/bin/env python3
"""sc:git PreToolUse safety validation.

Reads tool_input from stdin (JSON), checks git command safety.
Exit 0 = allow, Exit 2 = block.
"""
import sys, json, re

def main():
    tool_input = json.load(sys.stdin)
    command = tool_input.get("command", "")
    # ... pattern matching against safety rules ...

if __name__ == "__main__":
    main()
```

##### G. 디렉토리 구조

```
src/superclaude/skills/sc-git/
├── SKILL.md                          # 프론트매터 + 컴포넌트 (위 A 섹션)
└── scripts/
    └── validate_git_safety.py        # PreToolUse 훅 스크립트 (위 F 섹션)
```

설치 후 (`~/.claude/skills/sc-git/`에 복사):
- `{{SKILLS_PATH}}` → `~/.claude/skills` (user scope) 또는 `.claude/skills` (project scope)
- 훅 경로: `python3 ~/.claude/skills/sc-git/scripts/validate_git_safety.py`

---

#### 2.2.2 범용 전환 체크리스트 (8개 전환 공통)

> sc:git 설계에서 추출한 재사용 가능 프로세스. 각 전환 시 이 체크리스트를 순서대로 수행.

**Phase A: 분석 (코드 작성 전)**

- [ ] 1. 소스 커맨드 .md 읽기 — 필드 매핑표 작성
  - `<role>/<mission>` → `description` 트리거 문구
  - `<tools>` → `allowed-tools`
  - `<mcp>` → `metadata.mcp`
  - `<safety_rules>` → 훅 스크립트 요구사항
  - `<handoff>` → 유지 + 확장
  - `<bounds>` → 그대로 이전
- [ ] 2. 트리거 문구 설계 — 3가지 기준 적용
  - 매칭 의도가 명확한가? (2개 이상 키워드 조합)
  - 오발동 리스크가 낮은가? (다른 스킬/커맨드와 겹치지 않는가?)
  - 사용자가 실제로 이 문구를 사용하는가? (실제 세션 패턴 기반)
- [ ] 3. 에이전트 라우팅 결정 — 판단 매트릭스
  - 실제 에이전트 파일 존재 여부 확인 (`src/superclaude/agents/`)
  - 작업 성격: 범용 → `general-purpose` / 전문 → 해당 에이전트
  - 기존 스킬과의 일관성 (ship = general-purpose)
- [ ] 4. 다른 sc: 스킬과의 경계 분석
  - 기능 중복 식별 (특히 sc:ship, sc:test)
  - `<boundary_with_X>` 섹션 필요 여부 결정
  - 핸드오프 방향 설계

**Phase B: 구현**

- [ ] 5. 스킬 디렉토리 생성: `src/superclaude/skills/sc-{name}/`
- [ ] 6. SKILL.md 작성 — 프론트매터 + 컴포넌트
  - 프론트매터: name, description, version, metadata (context, agent, mcp, allowed-tools, hooks)
  - 컴포넌트: role, syntax, flow, patterns, safety, examples, bounds, handoff
- [ ] 7. 훅 스크립트 작성 (필요한 경우)
  - `scripts/` 디렉토리 생성
  - `{{SKILLS_PATH}}` 템플릿 변수 사용
  - stdin JSON → 검증 → exit code 인터페이스
- [ ] 8. 원본 커맨드를 thin stub으로 교체
  - `allowed-tools: []`
  - 리다이렉트 안내 + auto-trigger 키워드 목록

**Phase C: 검증**

- [ ] 9. `skill_linter` 통과 확인 (Phase 2.1 선행)
  - frontmatter-required: name, description 존재
  - frontmatter-types: metadata 필드 타입 정합성
  - component-structure: `<component type="skill">` 래핑
  - file-references: scripts/ 경로 실존 여부
- [ ] 10. `trigger_validator` 충돌 검사
  - 다른 sc: 스킬과 트리거 중복 없음
  - 원본 커맨드 stub과 충돌 없음
- [ ] 11. 수동 통합 테스트
  - `/sc:{name}` 명시적 호출 → 스킬 동작 확인
  - 자연어 프롬프트 → auto-trigger 확인
  - 훅 스크립트 실행 확인 (해당 시)
  - 에러 경로 테스트 (차단되어야 할 명령 차단 확인)
- [ ] 12. `install_paths.py` 경로 매핑 확인
  - 새 스킬 디렉토리가 설치 대상에 포함되는지
  - `{{SKILLS_PATH}}` 해석이 정확한지

#### 각 전환 프로세스 (요약)

1. 기존 커맨드 .md 내용 분석 → 스킬 구조로 재구성
2. SKILL.md 작성 (frontmatter + component)
3. 트리거 구문 설정 + trigger_validator로 충돌 검사
4. 원본 커맨드를 thin stub으로 교체 (하위 호환)
5. skill_linter 통과 확인
6. 통합 테스트

---

### 2.3 커맨드→스킬 전환 Wave 2 — P2

**대상**: build, estimate, document, design (Wave 1 검증 후 진행)

| 커맨드 | → 스킬 | 에이전트 | 핵심 추가사항 |
|--------|--------|----------|--------------|
| `/sc:build` | `sc:build` | devops-architect | 빌드 시스템 감지, 에러 복구 |
| `/sc:estimate` | `sc:estimate` | system-architect | Read-only (파일 수정 없음), 복잡도 스코어링 |
| `/sc:document` | `sc:document` | technical-writer | 템플릿 선택, 출력 형식 옵션 |
| `/sc:design` | `sc:design` | system-architect | 스펙 출력 템플릿, 검증 체크리스트 |

> **참고**: 기존 Phase 2.3 document-gen 스킬은 `/sc:document` 전환으로 대체. 별도 신규 스킬 불필요.

---

### 2.4 기존 스킬 sc: 리네임

기존 3개 스킬에 `sc:` prefix 적용:

| 현재 이름 | → 새 이름 | 변경 사항 |
|-----------|----------|----------|
| `ship` | `sc:ship` | SKILL.md name 필드 변경, 폴더명 `sc-ship/` |
| `confidence-check` | `sc:confidence-check` | SKILL.md name 필드 변경, 폴더명 `sc-confidence-check/` |
| `simplicity-coach` | `sc:simplicity-coach` | SKILL.md name 필드 변경, 폴더명 `sc-simplicity-coach/` |

#### 리네임 프로세스

1. 폴더명 변경: `skills/{name}/` → `skills/sc-{name}/`
2. SKILL.md frontmatter `name:` 필드 업데이트
3. `install_paths.py` 경로 매핑 확인
4. `install_skill.py` 템플릿 변수 해석 확인
5. hooks.json 참조 업데이트 (있다면)

> **삭제된 항목**: code-review (Anthropic 공식 스킬 사용), skill-creator (Anthropic 공식 스킬 사용), document-gen (`sc:document` 전환으로 대체), investment-analysis (도메인 특화, 별도 프로젝트로 이관)

### Phase 2 완료 기준

- [ ] 스킬 린터 + 트리거 검증기 구현 및 테스트
- [ ] Wave 1 전환 완료: sc:git, sc:test, sc:troubleshoot, sc:cleanup (4개 스킬)
- [ ] Wave 2 전환 완료: sc:build, sc:estimate, sc:document, sc:design (4개 스킬)
- [ ] 기존 3개 스킬 sc: 리네임 완료 (sc:ship, sc:confidence-check, sc:simplicity-coach)
- [ ] 8개 원본 커맨드가 thin stub으로 교체
- [ ] sc: 스킬 총 11개 (3 리네임 + 8 전환)
- [ ] Anthropic 공식 스킬 (code-review, skill-creator) 정상 동작 확인
- [ ] `superclaude skills lint` 전체 통과
- [ ] 커버리지 ≥ 60%

---

## Phase 3: CLI/DX 강화

> 목표: 스킬 관리 경험 프로급
> 선행 조건: Phase 2.1 (스킬 린터)

### 3.1 `superclaude doctor` 확장

#### 현재 체크 (6개)

1. pytest plugin loaded
2. Skills installed
3. Configuration
4. Hooks in settings.json
5. CLAUDE_SC.md exists
6. CLAUDE.md import

#### 추가 체크 (5개)

| # | 체크 | 내용 |
|---|------|------|
| 7 | **스킬 SKILL.md 유효성** | 모든 설치된 스킬의 frontmatter/구조 검증 |
| 8 | **트리거 충돌** | 스킬 간, 스킬-커맨드 간 트리거 중복 |
| 9 | **스킬 전환 완성도** | 8개 전환 대상 커맨드가 모두 stub + 스킬 쌍으로 존재하는지 확인 |
| 10 | **MCP 서버 가용성** | 설정된 MCP 서버 접속 테스트 |
| 11 | **버전 호환성** | Claude Code 버전과 SuperClaude 훅 호환성 |

#### 출력 형식

```
$ superclaude doctor
SuperClaude Health Check (v5.0.0+ajitta)

[✅] Pytest plugin loaded
[✅] Skills installed (11 sc: + 2 official)
[✅] Configuration valid
[✅] Hooks installed (4 lifecycle events)
[✅] CLAUDE_SC.md exists
[✅] CLAUDE.md import chain
[✅] Skill manifests valid (11/11 sc:)              # NEW
[✅] Skill migration complete (8/8 stubs)           # NEW
[✅] Official skills available (code-review, skill-creator)  # NEW
[✅] MCP servers reachable (3/3 configured)         # NEW
[✅] Claude Code v2.1.37+ compatible                # NEW

Score: 11/11
```

---

### 3.2 `superclaude skills list`

#### 기능

```bash
superclaude skills list              # 설치된 스킬 목록
superclaude skills list --available  # 설치 가능한 스킬 (향후)
superclaude skills list --verbose    # 트리거, 에이전트, 상태 포함
```

#### 출력 형식

```
$ superclaude skills list --verbose

SuperClaude Skills (sc:) — 11 installed:

  Original:
  sc:ship               /sc:ship            general-purpose    ✅ active
  sc:confidence-check   (auto)              quality-engineer   ✅ active
  sc:simplicity-coach   (auto)              general-purpose    ✅ active

  Migrated from Commands:
  sc:git                /sc:git             general-purpose    ✅ active
  sc:test               /sc:test            quality-engineer   ✅ active
  sc:troubleshoot       /sc:troubleshoot    root-cause-analyst ✅ active
  sc:cleanup            /sc:cleanup         refactoring-expert ✅ active
  sc:build              /sc:build           devops-architect   ✅ active
  sc:estimate           /sc:estimate        system-architect   ✅ active
  sc:document           /sc:document        technical-writer   ✅ active
  sc:design             /sc:design          system-architect   ✅ active

Anthropic Official Skills — 2 detected:
  code-review           /code-review        (official)         ✅ active
  skill-creator         /skill-creator      (official)         ✅ active

Triggers: 64 unique, 0 conflicts
```

---

### 3.3 외부 스킬 설치

#### 기존 `install-skill` 확장

현재 `superclaude install-skill <path>`는 로컬 경로만 지원. Phase 3에서는 로컬 경로 확장에 집중:

```bash
superclaude install-skill ./my-skill/           # 로컬 (기존)
superclaude install-skill ~/projects/my-skill/  # 절대 경로 확장
```

> **범위 축소**: GitHub URL 설치 (`https://github.com/...`)는 post-Phase 3로 이관. 로컬 경로 확장을 먼저 안정화.

### Phase 3 완료 기준

- [ ] `superclaude doctor` 11개 체크 전부 동작 (스킬 전환 완성도 체크 포함)
- [ ] `superclaude skills list` 기본 + verbose 모드 (네이티브/전환 구분 표시)
- [ ] 로컬 경로 스킬 설치 안정화
- [ ] 기존 CLI 테스트와 통합

---

## Phase 4: 아키텍처 진화

> 목표: 자기 확장 기반 마련
> 선행 조건: Phase 2 + Phase 3
> 성격: 실험적 / 프로토타입

### 4.1 스킬 의존성 모델링

#### SKILL.md frontmatter 확장

```yaml
---
name: investment-analysis
description: ...
metadata:
  context: inline
  agent: deep-research-agent
  requires:                    # NEW: 필수 의존성
    - skills: ["yt-analyze"]   # 다른 스킬
    - mcp: ["tavily"]          # MCP 서버
  enhances:                    # NEW: 선택적 강화
    - skills: ["sc:document"]
  version: "1.0.0"             # NEW: 시맨틱 버전
---
```

> **참고**: 전환된 스킬은 원본 커맨드의 MCP 서버 의존성을 상속할 수 있음. 예: `sc:git` 스킬은 별도 MCP 불필요하지만, `sc:troubleshoot` 스킬은 `--seq` (Sequential) MCP와 시너지가 있을 수 있음. 의존성 모델링 시 이를 명시적으로 선언.

#### 의존성 해석기

```python
# skills/_testing/dependency_resolver.py
class DependencyGraph:
    def resolve(self, skill_name: str) -> list[str]:
        """설치 순서를 토폴로지 정렬로 반환"""

    def check_circular(self) -> list[tuple[str, str]]:
        """순환 의존성 감지"""

    def missing_dependencies(self) -> list[tuple[str, str]]:
        """미설치 의존 스킬 목록"""
```

#### CLI 통합

```bash
superclaude skills deps                    # 의존성 그래프 표시
superclaude skills deps --check            # 미충족 의존성 체크
superclaude install-skill <name> --with-deps  # 의존 스킬 함께 설치
```

---

### 4.2 자기 확장 프로토타입

**비전**: Anthropic "agents writing their own Skills from experience"

#### 접근: 세션 패턴 감지 + 스킬 제안

```
세션 중 반복 패턴 감지
  ↓
"이 작업 패턴을 스킬로 만들까요?" 제안
  ↓
사용자 승인
  ↓
Anthropic 공식 skill-creator 호출
  ↓
새 sc: 스킬 생성 + 린트 + 설치
```

> Anthropic 공식 `skill-creator`가 이 프로세스의 핵심 enabler. 향후 커맨드→스킬 전환도 이 도구로 자동화 가능.

#### 구현 범위 (프로토타입)

- **패턴 감지기**: 세션 내에서 유사한 명령어 시퀀스가 2회 이상 반복되면 플래그
- **스킬 제안기**: 감지된 패턴을 skill-creator 입력 형식으로 변환
- **사용자 확인**: 항상 사용자 승인 필수 (자동 생성 금지)

#### 제약

- Phase 4.2는 프로토타입 수준
- 프로덕션 자기 확장은 Claude의 에이전트 능력 진화에 의존
- 현 단계에서는 "제안"까지만, "자동 생성"은 향후

---

### 4.3 스킬 버전 관리

#### SKILL.md 버전 필드

```yaml
---
name: sc:ship
version: "1.2.0"
changelog:
  - "1.2.0: PR 템플릿 개선, --dry-run 추가"
  - "1.1.0: 시크릿 스캔 추가"
  - "1.0.0: 초기 릴리스"
---
```

#### 업그레이드 경로

```bash
superclaude skills version                # 현재 스킬 버전 표시
superclaude skills outdated               # 업데이트 가능 스킬 (향후 레지스트리 연동 시)
```

### Phase 4 완료 기준

- [ ] SKILL.md frontmatter에 requires/enhances/version 지원
- [ ] 의존성 해석기 구현 + 순환 감지
- [ ] 자기 확장 프로토타입: 패턴 감지 → 제안 (수동 승인)
- [ ] 버전 관리 기본 체계

---

## 실행 순서 요약

```
Phase 1 ──→ Phase 2 ──────────────────→ Phase 3 ──→ Phase 4
정리/기반    스킬 확장 (sc: prefix)        CLI/DX      아키텍처

1.1 분석이슈  2.1 테스트FW                 3.1 doctor+  4.1 의존성
1.2 exec삭제  2.2 Wave1(sc:git,sc:test,    3.2 list     4.2 자기확장
1.3 리팩토링      sc:troubleshoot,         3.3 설치확장  4.3 버전관리
1.4 테스트        sc:cleanup)
1.5 통합테스트 2.3 Wave2(sc:build,
1.6 pm보강
                  sc:estimate,
                  sc:document,sc:design)
              2.4 기존 3개 sc: 리네임
              ── Anthropic 공식: code-review, skill-creator 활용 ──

각 Phase 완료 후 → Orient (평가) → Step (다음 Phase) → Learn (피드백 반영)
```

---

## 리스크 & 완화

| 리스크 | 영향 | 완화 |
|--------|------|------|
| execution/ 제거 시 숨은 의존성 | 런타임 에러 | grep으로 모든 import 확인 후 제거 (확인 완료: 0건) |
| context_loader 리팩토링 시 훅 깨짐 | 세션 시작 실패 | 기존 테스트 + 수동 통합 테스트 |
| 스킬 린터가 기존 스킬을 reject | 워크플로 중단 | 기존 3개 스킬로 먼저 검증 후 배포 |
| 자기 확장이 불필요한 스킬 제안 | 사용자 피로 | 항상 opt-in, 빈도 제한 |
| 커맨드 stub 리다이렉트 혼동 | /sc:name 호출 시 스킬과 동작 불일치 | stub에 명확한 안내 메시지 + 문서화 |
| 전환된 스킬 간 트리거 중복 | 잘못된 스킬 발동 | trigger_validator.py (Phase 2.1)가 선행 조건으로 감지 |
| 8개 동시 전환 품질 저하 | 불완전한 전환 | Wave 1 (4개) 먼저 → 검증 → Wave 2 (4개) 순차 진행 |

---

## 버전 전략

| 마일스톤 | 버전 |
|----------|------|
| Phase 1 완료 | v4.4.0+ajitta |
| Phase 2 Wave 1 (sc:git, sc:test, sc:troubleshoot, sc:cleanup) | v4.5.0+ajitta |
| Phase 2 Wave 2 (sc:build, sc:estimate, sc:document, sc:design) + 기존 리네임 | v4.6.0+ajitta |
| Phase 3 완료 | v5.0.0+ajitta (major: CLI 인터페이스 변경) |
| Phase 4 완료 | v5.1.0+ajitta |
