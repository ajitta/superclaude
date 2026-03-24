# Serena-First Agent Exploration

**Date**: 2026-03-24
**Author**: chosh1179
**Status**: Reviewed — Ready for Planning
**Scope**: 19 agent files (of 22) + RULES.md + agent-authoring.md = 21 files

---

## Problem Statement

SuperClaude 에이전트가 sub-agent로 동작할 때, Serena MCP의 심볼릭 도구(get_symbols_overview, find_symbol, find_referencing_symbols) 대신 native Read/Grep/Glob을 사용하여 코드를 탐색한다.

**토큰 비효율**: Read는 파일 전체를 읽지만, Serena는 심볼 수준 탐색으로 필요한 정보만 추출.
**구조적 이해 부재**: Grep은 텍스트 매칭만, Serena는 심볼 관계(참조, 호출, 상속)까지 파악.

## Research Findings

### MCP 도구 상속 (공식 문서 확인)

> "By default, subagents inherit all tools from the main conversation, **including MCP tools**."
> — [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)

**결론**: Sub-agent는 부모 세션의 Serena MCP 도구를 **이미 상속받고 있음**. 접근 권한은 문제가 아님.

### `mcpServers` vs `<mcp servers="...">`

| 항목 | `mcpServers` (YAML frontmatter) | `<mcp servers="...">` (XML body) |
|------|-------------------------------|----------------------------------|
| 출처 | Claude Code 공식 필드 | SuperClaude 자체 문서화 컨벤션 |
| 런타임 효과 | **있음** — sub-agent에 MCP 서버 명시적 스코핑 | **없음** — 순수 문서 표현 |
| 용도 | 부모에 없는 MCP 서버 추가, 또는 sub-agent 전용 스코핑 | 에이전트 설계 의도 표현 |
| 현재 사용 | agent-authoring.md에 미문서화 | 22개 에이전트 body에 사용 중 |

### Sub-agent 프롬프트 구성

| 구성 요소 | Sub-agent 주입 여부 | 근거 |
|-----------|-------------------|------|
| 에이전트 `.md` body | ✅ 주입됨 | CC native 동작 |
| MCP 서버 instruction | ✅ 주입됨 | MCP 서버 자체 제공 |
| MCP 도구 접근 | ✅ 상속됨 | 공식 문서 확인 |
| `.claude/rules/*.md` | ⚠️ 불확실 | 커뮤니티 보고 상충 |
| RULES.md (@import chain) | ⚠️ 불확실 | CLAUDE_SC.md 체인 — sub-agent 주입 미보장 |

### 핵심 인사이트: ACCESS ≠ BEHAVIOR

Sub-agent는 Serena 도구에 **접근 가능**하지만 **사용하지 않는다**. 원인:
1. Serena MCP instruction은 일반적: "Serena 도구를 우선 사용하라"
2. 에이전트 `<tool_guidance>`는 구체적: "Read schemas, analyze APIs" (native 도구 동사)
3. 모델은 **더 구체적인** 에이전트 지시를 따름 → native 도구 선택
4. 22개 에이전트 중 **1개만** (simplicity-guide) tool_guidance에서 Serena를 명시

## Root Cause Analysis

| 레이어 | 현재 상태 | 문제 |
|--------|----------|------|
| MCP 도구 접근 | ✅ Sub-agent가 부모 MCP 상속 (공식 확인) | **접근은 정상** |
| Serena MCP instruction | "Serena 우선 사용" 명시됨, sub-agent에도 주입 | 일반적 지시 — 에이전트별 구체 지시에 밀림 |
| 에이전트 `<tool_guidance>` | 22개 중 **1개만** Serena 명시 (simplicity-guide) | **핵심 격차** — 도메인 지시가 native 도구를 유도 |
| 에이전트 `<mcp servers="...">` | 22개 중 7개만 serena 포함 | 문서적 의도 표현 부재 (런타임 무관) |
| RULES.md | 코드 탐색 도구 선호 규칙 없음 | 메인 세션 가이드 부재 (sub-agent 주입 미보장) |
| agent-authoring.md | tool_guidance 템플릿에 Serena 패턴 없음 | 새 에이전트에 패턴 미전파 |

**핵심 원인**: 에이전트의 `<tool_guidance>` Proceed 섹션이 "Read", "Analyze", "Scan" 같은 native 도구 동사를 사용 → 모델이 더 구체적인 에이전트 지시를 따라 native 도구 선택. **접근 권한이 아니라 행동 지침의 격차.**

## Design Specification

### Layer 1: Agent `<tool_guidance>` 업데이트 (19 files) — PRIMARY FIX

에이전트를 코드 탐색 빈도별 3티어로 분류하고, 티어별 디렉티브를 적용.

#### Tier Classification

| Tier | 기준 | 에이전트 | 디렉티브 |
|------|------|---------|---------|
| **HIGH** (11) | 코드 분석이 핵심 업무 | backend-architect, frontend-architect, python-expert, refactoring-expert, performance-engineer, quality-engineer, security-engineer, root-cause-analyst, system-architect, repo-index, self-review | Full Serena-first |
| **MEDIUM** (8) | 코드 탐색이 보조 업무 | project-manager, project-initializer, simplicity-guide, devops-architect, technical-writer, learning-guide, socratic-mentor, requirements-analyst | Conditional Serena |
| **LOW** (3) | 코드 탐색 거의 없음 | deep-researcher, business-panel-experts, git-workflow | No change |

#### Directive Templates

**HIGH tier** — `<tool_guidance>` Proceed에 추가:
```
- Serena-First: For code exploration, use get_symbols_overview → find_symbol(include_body=True) before Read. Reserve Read for non-code files (config, docs, data). Use find_referencing_symbols for impact analysis.
```

**MEDIUM tier** — `<tool_guidance>` Proceed에 추가:
```
- Serena-First: When exploring code, prefer Serena symbolic tools (get_symbols_overview, find_symbol) over Read for token efficiency.
```

**LOW tier** — 변경 없음. 코드 탐색이 핵심 업무가 아닌 에이전트에 불필요한 지시는 noise.

**참고**: simplicity-guide는 이미 tool_guidance에 Serena를 상세 명시 (`Serena: find_referencing_symbols, get_symbols_overview`). 이 기존 문구가 MEDIUM 템플릿보다 **더 구체적**이므로 기존 문구를 **유지** — 표준 디렉티브로 교체하면 다운그레이드. 실제 변경 대상은 18개 에이전트 (HIGH 11 + MEDIUM 7, simplicity-guide 제외).

#### `<mcp servers="...">` 업데이트 (문서적)

이 태그는 **런타임 효과 없음** — 순수 문서화 컨벤션. 에이전트 설계 의도 표현을 위해 업데이트.

HIGH/MEDIUM tier 에이전트 중 `serena`가 빠진 경우 추가:

| 에이전트 | 현재 | 변경 후 |
|---------|------|---------|
| backend-architect | `seq\|c7` | `seq\|c7\|serena` |
| frontend-architect | `magic\|play\|perf` | `magic\|play\|perf\|serena` |
| python-expert | `c7\|seq` | `c7\|seq\|serena` |
| performance-engineer | `perf\|seq\|play` | `perf\|seq\|play\|serena` |
| quality-engineer | `play\|seq` | `play\|seq\|serena` |
| security-engineer | `seq\|c7` | `seq\|c7\|serena` |
| system-architect | `seq\|c7` | `seq\|c7\|serena` |
| devops-architect | `seq\|c7` | `seq\|c7\|serena` |
| technical-writer | `c7\|seq` | `c7\|seq\|serena` |
| learning-guide | `c7\|seq` | `c7\|seq\|serena` |
| socratic-mentor | `seq\|c7` | `seq\|c7\|serena` |
| requirements-analyst | `seq` | `seq\|serena` |
| project-initializer | `seq` | `seq\|serena` |

**mcp tag 변경 불필요** (이미 serena 포함, HIGH/MEDIUM): repo-index, simplicity-guide, self-review, refactoring-expert, project-manager, root-cause-analyst

**전체 변경 불필요** (LOW tier): git-workflow, business-panel-experts

**mcp tag 변경 불필요** (LOW tier, 이미 serena 포함하나 코드 탐색이 아닌 메모리/세션 용도): deep-researcher

### Layer 2: RULES.md 업데이트 (1 file) — SUPPLEMENTARY

> **Caveat**: RULES.md는 CLAUDE_SC.md @import 체인으로 로드됨. 메인 세션에는 확실히 적용되지만, sub-agent 주입은 **미보장** (커뮤니티 보고 상충). Layer 1이 primary fix인 이유.

`<core_rules>` 섹션에 새 규칙 추가:

```
[R17] Serena-First 🟢: code exploration → prefer Serena symbolic tools (get_symbols_overview, find_symbol) over Read; reserve Read for non-code files, unknown formats, or when Serena unavailable
```

`<core_rules>` examples 테이블에 추가:

```
| Exploring unfamiliar class | Read entire 500-line file | get_symbols_overview → find_symbol(depth=1) | Serena-First 🟢 |
| Finding function callers | grep "functionName" across repo | find_referencing_symbols(functionName) | Serena-First 🟢 |
| Reading YAML config | Use Serena symbolic tools | Use Read (non-code file) | Serena-First 🟢 |
```

**우선순위**: 🟢 (Optimization) — Serena가 없는 환경에서도 기능적 문제 없음.

### Layer 3: agent-authoring.md 업데이트 (1 file)

#### Template 업데이트

`<tool_guidance>` 템플릿 예시에 Serena-first 패턴 추가:

```xml
<tool_guidance>
- Proceed: [domain actions] | Serena-First: prefer symbolic tools for code exploration
- Ask First: [confirmation-required actions]
- Never: [prohibited actions]
</tool_guidance>
```

#### `mcpServers` 공식 필드 문서화

Frontmatter 필드 레퍼런스에 추가 (현재 미문서화):

```yaml
mcpServers:                                # optional | MCP servers scoped to this subagent
  - serena                                 # string reference: uses parent's existing connection
  - custom-server:                         # inline definition: starts new server for subagent
      type: stdio
      command: npx
      args: ["-y", "@custom/mcp-server"]
```

**참고**: `mcpServers`는 MCP 서버 **스코핑**용. Sub-agent는 기본적으로 부모의 모든 MCP 도구를 상속하므로, 일반적으로 지정 불필요. 부모에 없는 서버를 sub-agent 전용으로 추가하거나, 명시적 스코핑이 필요한 경우에만 사용.

#### 신규 섹션: "Code Exploration Pattern"

`## Validation` 앞에 추가:

```markdown
## Code Exploration Pattern

Agents that explore source code should include a Serena-first directive in `<tool_guidance>`:

| Agent Tier | Directive | When |
|-----------|-----------|------|
| Code-centric (architect, engineer, analyst) | Full: `get_symbols_overview → find_symbol → find_referencing_symbols` | Always |
| Code-adjacent (manager, writer, mentor) | Light: `prefer symbolic tools for code exploration` | When code may be read |
| Non-code (researcher, business) | None | Skip |

**Rationale**: Serena symbolic tools provide significant token reduction vs Read for code exploration (symbol overview vs full file read), plus structural understanding (references, types, inheritance).

**Note**: `<mcp servers="...">` is a documentation-only convention (no runtime effect). The official CC field `mcpServers` (frontmatter) provides actual MCP server scoping. Sub-agents inherit parent MCP tools by default — `mcpServers` is only needed for adding non-inherited servers or explicit scoping.
```

### Layer 4: Graceful Degradation

모든 디렉티브에 "when available" 또는 "prefer" 사용:
- "prefer Serena symbolic tools" (NOT "always use Serena")
- "reserve Read for non-code files" (NOT "never use Read")

Serena가 설치되지 않은 프로젝트에서 에이전트가 Read/Grep으로 자연스럽게 fallback.

## Change Summary

| 파일 그룹 | 파일 수 | 변경 유형 | 줄 수 (예상) |
|-----------|--------|----------|-------------|
| HIGH tier agents | 11 | tool_guidance 1줄 + mcp tag | +2줄/파일 |
| MEDIUM tier agents (simplicity-guide 제외) | 7 | tool_guidance 1줄 + mcp tag | +2줄/파일 |
| simplicity-guide | 1 | 기존 Serena 지시 유지 (변경 없음) | 0 |
| LOW tier agents | 3 | 없음 | 0 |
| RULES.md | 1 | [R17] + examples 3줄 | +6줄 |
| agent-authoring.md | 1 | 템플릿 + mcpServers 문서화 + 신규 섹션 | +30줄 |
| **합계** | **21 files** | | **+74줄** |

## Verification Plan

1. `uv run pytest tests/unit/test_agent_structure.py -v` — 에이전트 구조 검증
2. `grep -r "Serena-First" src/superclaude/agents/` — 18개 에이전트에 디렉티브 존재 확인 (simplicity-guide는 기존 문구 유지)
3. `grep "R17" src/superclaude/core/RULES.md` — 규칙 존재 확인
4. `grep "Code Exploration Pattern" .claude/rules/agent-authoring.md` — 가이드 존재 확인
5. `uv run pytest` — 전체 테스트 스위트 회귀 확인 (기존 1,694 tests 기준)
6. `grep "find_referencing_symbols" src/superclaude/agents/simplicity-guide.md` — 기존 Serena 지시 보존 확인

## Risk Assessment

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| Serena 미설치 환경에서 혼란 | LOW | LOW | "prefer" 조건부 표현으로 graceful degradation |
| tool_guidance 길이 증가로 토큰 부담 | LOW | LOW | 1줄 추가 (~20 tokens/agent) |
| 테스트 실패 | LOW | MEDIUM | tool_guidance content 검증은 기존 테스트 범위 |
| 비코드 에이전트에 불필요한 지시 | N/A | N/A | LOW tier 제외로 예방 |
| RULES.md가 sub-agent에 미주입 | MEDIUM | LOW | Layer 1이 primary fix — RULES.md는 supplementary |

## Non-Goals

- Serena MCP 서버 instruction 자체 수정 (이미 "Serena 우선" 명시)
- context_loader.py 수정 (agent는 CC native 시스템, context_loader 무관)
- 새 테스트 파일 생성 (기존 test_agent_structure.py로 충분)
- `disallowedTools` 변경 (Serena는 MCP 도구, disallowedTools 대상 아님)
- `mcpServers` frontmatter를 모든 에이전트에 추가 (MCP 도구는 기본 상속 — 불필요)

## Decision Log

| 결정 | 근거 |
|------|------|
| 3-tier 분류 (HIGH/MEDIUM/LOW) | 비코드 에이전트에 코드 탐색 지시는 noise → 역할 기반 적용 범위 설정 |
| `<mcp servers>` 태그 업데이트 포함 | 런타임 무관하지만, 에이전트 설계 의도 문서화 — 코드 리뷰/유지보수 시 가독성 |
| RULES.md [R17]을 🟢 우선순위로 | Serena 없이도 기능 정상 — 최적화 영역 |
| RULES.md를 supplementary로 분류 | Sub-agent 주입 미보장 (커뮤니티 보고 상충) — Layer 1이 primary |
| agent-authoring.md에 `mcpServers` 문서화 | 공식 CC 필드이나 현재 SuperClaude template에 미포함 — 향후 활용 대비 |
| `mcpServers` frontmatter 일괄 추가 보류 | MCP 도구 기본 상속으로 불필요 — 행동 지침(Layer 1)이 핵심 해결책 |
| 토큰 절감 수치 미확정 | "60-80%" 클레임 미검증 → "significant reduction" 표현으로 정정 |

## Prior Art

- **Model-agnostic refactor** (725589b, Mar 23): 22개 에이전트 일괄 수정 선례 — 동일 패턴 재활용
- **simplicity-guide.md**: 유일하게 Serena 도구를 tool_guidance에 명시한 에이전트 — 이 패턴을 표준화

## Sources

- [Claude Code Sub-agents docs](https://code.claude.com/docs/en/sub-agents) — MCP inheritance, mcpServers field, supported frontmatter
- [GitHub #22430](https://github.com/anthropics/claude-code/issues/22430) — Task tool MCP access (historical, different from Agent system)
- [GitHub #23374](https://github.com/anthropics/claude-code/issues/23374) — Sub-agent MCP tool access request
- [PubNub Best Practices](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/) — "If you omit tools, the subagent inherits the thread's tools (including MCP)"
