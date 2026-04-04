---
status: approved
revised: 2026-04-04
---

# ast-grep MCP Integration Discovery

## Summary

SuperClaude의 9번째 관리 MCP 서버로 [ast-grep MCP](https://github.com/ast-grep/ast-grep-mcp)를 추가한다. tree-sitter 기반 **구조적 AST 패턴 검색**으로 Serena(심볼 탐색)와 Grep(텍스트 검색) 사이의 갭을 채운다.

## Motivation

- RULES.md [R17] Serena-First 체인에 이미 "ast-grep MCP (if configured)"로 명시 — 미구현 상태
- 텍스트 grep은 false positive가 많고 구조를 이해 못함 (e.g., 주석 내 매치, 문자열 내 매치)
- Serena는 심볼 탐색에 특화 — "모든 빈 catch 블록 찾기" 같은 패턴 매칭은 범위 밖
- 리팩토링, 보안 감사, 코드 품질 검사에 구조적 검색이 필요

## ast-grep MCP 개요

| 항목 | 내용 |
|------|------|
| Repository | https://github.com/ast-grep/ast-grep-mcp |
| Language | Python (uvx 설치) |
| Transport | stdio |
| Prerequisites | `ast-grep` binary on PATH |
| API Key | 불필요 |

### 제공 도구 (4개)

| Tool | Purpose | When to use |
|------|---------|-------------|
| `dump_syntax_tree` | 코드 스니펫의 AST 구조 시각화 | 패턴 작성 전 AST 노드 이름 확인 |
| `test_match_code_rule` | YAML 규칙을 코드 스니펫에 테스트 | 대규모 검색 전 규칙 검증 |
| `find_code` | 구조적 패턴으로 코드베이스 검색 | 단순 패턴 매칭 (e.g., `console.log($$$)`) |
| `find_code_by_rule` | 복합 YAML 규칙으로 고급 검색 | 메타변수, 제약조건이 있는 복합 패턴 |

### 워크플로우

```
dump_syntax_tree → test_match_code_rule → find_code / find_code_by_rule
(AST 이해)        (규칙 검증)              (대규모 검색)
```

## Decisions

### D1: Flag 이름 — `--sg|--ast-grep`

| 후보 | 장단점 |
|------|--------|
| `--sg` | ast-grep CLI 이름(`sg`)과 동일, 짧음 |
| `--ast` | 직관적이나 "generic AST"와 혼동 가능 |
| `--ast-grep` | 명확하나 길음 |
| **`--sg\|--ast-grep`** | ★ 기존 패턴(--c7\|--context7, --seq\|--sequential) 준수 |

Alias: `--astgrep` → `--ast-grep` (typo correction)

### D2: 역할 포지셔닝 — 범용 AST 검색 도구

[R17] 체인에서는 탐색 fallback이지만, **패턴 매칭 작업에서는 primary**.

| Use Case | Primary Tool | Fallback |
|----------|-------------|----------|
| 심볼 탐색 (정의, 참조) | Serena | ast-grep → Grep |
| 구조적 패턴 매칭 | **ast-grep** | Grep |
| 텍스트 검색 | Grep | — |
| 안티패턴 탐지 | **ast-grep** | Grep |

### D3: 전제조건 — 경고만 (warn-only)

- `shutil.which("ast-grep")` 또는 `shutil.which("sg")` 체크
- 미설치 시: 경고 + 설치 안내 (brew/cargo/npm)
- MCP 서버 설치는 진행 (런타임 에러는 사용자 책임)
- Serena의 uv 체크와 동일 패턴 (하드코딩, 제네릭 시스템 아님)

### D4: 에이전트 통합 — Tier 1만 (3개)

| Agent | 통합 내용 |
|-------|----------|
| refactoring-expert | `<mcp>` + `<tool_guidance>`: AST 패턴으로 리팩토링 대상 식별 |
| quality-engineer | `<mcp>` + `<tool_guidance>`: 안티패턴 탐지 규칙 |
| security-engineer | `<mcp>` + `<tool_guidance>`: 취약점 패턴 스캐닝 |

Tier 2 (root-cause-analyst, performance-engineer)는 초기 범위에서 제외 — 필요 시 후속 추가.

### D5: context_loader 통합 — Tier 0 + 자동감지 키워드

**Tier: 0** (1-line hint) — ast-grep 도구 이름이 자명하므로 Tier 1 불필요.

**트리거 regex:**
```python
(r"(--sg|--ast-grep|ast.?grep|syntax.?tree|structural.?pattern|structural.?search)",
 "mcp/MCP_AstGrep.md", 2)
```

**TIER_0_MAP hint:**
```
"mcp/MCP_AstGrep.md": "ast-grep: structural AST search. dump_syntax_tree → test_match_code_rule → find_code. Use for code patterns beyond text grep."
```

**키워드 선정:**

| Keyword | Safe? | Rationale |
|---------|-------|-----------|
| `--sg`, `--ast-grep` | Safe | 명시적 flag |
| `ast.?grep` | Safe | 도구 이름 직접 매칭 |
| `syntax.?tree` | Safe | AST 전용 용어 |
| `structural.?pattern` | Safe | 복합어, 구체적 |
| `structural.?search` | Safe | 복합어, 구체적 |
| ~~`anti.?pattern`~~ | Skip | 디자인 안티패턴과 혼동 |
| ~~`AST`~~ | Skip | "LAST" 등 부분 매칭 위험 |

**추가 변경:**
- `--all-mcp` composite에 `("mcp/MCP_AstGrep.md", 2)` 추가
- `FLAG_ALIASES`: `"astgrep": ["ast-grep"]` 추가

## Changeset (7 files — reviewed, agent updates deferred)

### Phase 1: Infrastructure
| File | Action | Description |
|------|--------|-------------|
| `mcp/configs/ast-grep.json` | NEW | uvx config (reference-only, Serena 패턴) |
| `cli/install_mcp.py` | EDIT | Registry entry + prereq check (sg + ast-grep binary) |

### Phase 2: Documentation
| File | Action | Description |
|------|--------|-------------|
| `mcp/MCP_AstGrep.md` | NEW | 4 tools, 워크플로우, 사용 가이드 |
| `mcp/README.md` | EDIT | 서버 목록 + 조합 매트릭스 업데이트 |

### Phase 3: Flag System
| File | Action | Description |
|------|--------|-------------|
| `core/FLAGS.md` | EDIT | `--sg\|--ast-grep` 추가 |
| `scripts/context_loader.py` | EDIT | Trigger + TIER_0 + COMPOSITE + VALID_FLAGS + aliases |

### Phase 4: Rules
| File | Action | Description |
|------|--------|-------------|
| `core/RULES.md` | EDIT | [R17] "(if configured)" 제거 |

### Deferred (post-usage)
| File | Action | Rationale |
|------|--------|-----------|
| `agents/refactoring-expert.md` | DEFERRED | 사용 패턴 확인 후 추가 |
| `agents/quality-engineer.md` | DEFERRED | 현재 에이전트 중 `<mcp>` 태그 사용 없음 |
| `agents/security-engineer.md` | DEFERRED | 실패 시나리오 없음, 2-line edit로 추후 추가 가능 |

## Verification

```bash
uv run pytest tests/unit/test_agent_structure.py -v    # Agent 구조 검증
superclaude mcp --list                                   # Registry 확인
superclaude mcp --dry-run -s ast-grep                    # 설치 미리보기
```

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| uvx git+ URL 변경 (PyPI 배포 시) | Low | config 업데이트로 대응 |
| ast-grep 바이너리 미설치 | Medium | warn-only (D3) |
| tree-sitter 파서 미지원 언어 | Low | sgconfig.yaml로 커스텀 파서 추가 가능 |

## Out of Scope

- ast-grep YAML 규칙 라이브러리 (사용자가 직접 작성)
- Morphllm과의 자동 연계 (find → transform 파이프라인)
- 에이전트 통합 전체 (Tier 1: refactoring/quality/security + Tier 2: root-cause/performance) — 사용 패턴 확인 후
- `sgconfig.yaml` 자동 생성/관리
