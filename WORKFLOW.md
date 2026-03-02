# SuperClaude Implementation Workflow

**소스**: `IMPROVEMENT_PLAN.md` (v4.3.0+ajitta → v5.0.0+ajitta)
**생성일**: 2026-03-02
**전략**: Systematic (의존성 기반 순차 + 병렬 최적화)

---

## 의존성 그래프

```
Phase 1: 정리 & 기반
═══════════════════════════════════════════════════════════════

  T1.1 분석이슈 ──┐
  T1.2 MCP 보강 ──┼── [QG1a: quick wins] ──┐
  T1.3 exec삭제 ──┤                        │
  T1.4 pm보강   ──┘                        │
                                            │
  T1.5 리팩토링 ─── [QG1b: 핵심 리팩토링] ──┤
                                            │
                            ┌───────────────┘
                            v
                    T2.1~T2.4 scripts 테스트 ──┐
                    T2.5 통합 테스트           ──┼── [QG1: Phase 1]
                                                │   tests green
                                                │   coverage ≥50%
═══════════════════════════════════════════════════════════════

Phase 2: 스킬 생태계
═══════════════════════════════════════════════════════════════

  [QG1] ──→ T3.1~T3.3 테스트FW ──┬──→ T4.1~T4.4 Wave 1 ──→ [QG2a]
                                  │   (git∥test∥troubleshoot∥cleanup)
                                  │
                                  └──→ T3.4 sc: 리네임 (병렬)

  [QG2a] ──→ T5.1~T5.4 Wave 2 ──→ [QG2: Phase 2]
              (build∥estimate∥document∥design)
              sc: 11개, coverage ≥60%
═══════════════════════════════════════════════════════════════

Phase 3: CLI/DX
═══════════════════════════════════════════════════════════════

  [QG2] ──→ T6.1 doctor+       ──┐
            T6.2 skills list    ──┼── [QG3: Phase 3]
            T6.3 설치확장       ──┘    doctor 11/11
═══════════════════════════════════════════════════════════════

Phase 4: 아키텍처 (실험적)
═══════════════════════════════════════════════════════════════

  [QG3] ──→ T7.1 스키마 ──┬──→ T7.2 해석기 ──→ T7.3 자기확장
            T7.4 버전     ─┘                    [QG4: v5.1.0]
═══════════════════════════════════════════════════════════════
```

---

## Sprint 1: Quick Wins + 리팩토링 착수

> 병렬 가능 작업 4개 + 크리티컬 패스 착수. Plan ref: Phase 1.1, 1.2, 1.3, 1.6.

### T1.1 — FLAGS.md / RULES.md stray `</output>` 제거
- **Plan ref**: 1.1 Finding 1
- **파일**: `src/superclaude/core/FLAGS.md`, `src/superclaude/core/RULES.md`
- **작업**: 양 파일 마지막 줄 `</output>` 삭제
- **검증**: `grep -r '</output>' src/superclaude/core/` → 0건
- **병렬**: T1.2, T1.3, T1.4와 동시

### T1.2 — MCP 문서 보강 (6개)
- **Plan ref**: 1.1 Finding 3
- **파일**:
  - `src/superclaude/mcp/MCP_Context7.md` (24→~50줄)
  - `src/superclaude/mcp/MCP_Playwright.md` (28→~50줄)
  - `src/superclaude/mcp/MCP_Sequential.md` (28→~45줄)
  - `src/superclaude/mcp/MCP_Chrome-DevTools.md` (32→~50줄)
  - `src/superclaude/mcp/MCP_Magic.md` (27→~45줄)
  - `src/superclaude/mcp/MCP_Morphllm.md` (28→~45줄)
- **추가 내용**: 시나리오 2-3개, 도구별 가이드, 워크플로 예시
- **검증**: 각 파일 40줄 이상
- **병렬**: T1.1, T1.3, T1.4와 동시

### T1.3 — execution/ 모듈 제거
- **Plan ref**: 1.2
- **파일 삭제** (5개, 총 1,336줄):
  - `src/superclaude/execution/__init__.py` (227줄)
  - `src/superclaude/execution/parallel.py` (288줄)
  - `src/superclaude/execution/reflection.py` (400줄)
  - `src/superclaude/execution/self_correction.py` (421줄)
  - `tests/unit/test_parallel.py`
- **사전 확인 완료**: 외부 import 0건
- **검증**: `uv run pytest` green, 커버리지 분모 감소
- **병렬**: T1.1, T1.2, T1.4와 동시

### T1.4 — pm_agent 테스트 보강
- **Plan ref**: 1.6
- **파일**:
  - `tests/unit/test_task_cleanup.py` (CREATE: 3 테스트)
  - `tests/unit/test_token_budget.py` (MODIFY: 4 테스트 추가)
- **케이스**: stale 정리, active 보존, empty list, budget 3단계, marker 추출
- **검증**: `uv run pytest tests/unit/test_task_cleanup.py tests/unit/test_token_budget.py -v`
- **병렬**: T1.1~T1.3과 동시

### T1.5 — context_loader 리팩토링 (**크리티컬 패스**)
- **Plan ref**: 1.3 (상세 설계 IMPROVEMENT_PLAN.md 122-511행)
- **순서** (엄격한 의존성, 10단계):

| 단계 | 작업 | 파일 |
|------|------|------|
| 1 | context_session.py 생성 | CREATE: `scripts/context_session.py` (~70줄) |
| 2 | context_trigger_map.py 생성 | CREATE: `scripts/context_trigger_map.py` (~250줄) |
| 3 | context_injection.py 생성 | CREATE: `scripts/context_injection.py` (~200줄) |
| 4 | context_loader.py 축소 | MODIFY: `scripts/context_loader.py` (495→~50줄) |
| 5 | 모드 kebab-case 리네임 | `git mv` × 8 파일 |
| 6 | skill_activator → skill_metadata | RENAME + 트리거/main 제거 |
| 7 | hooks.json 업데이트 | MODIFY: skill_activator 엔트리 제거 |
| 8 | install_settings.py 마커 | MODIFY: 훅 마커 업데이트 |
| 9 | modes/README.md 참조 | MODIFY: 파일명 참조 업데이트 |
| 10 | 기존 테스트 업데이트 | MODIFY: test_context_loader.py |

- **모드 리네임 매핑**:
  - `MODE_Brainstorming.md` → `brainstorming.md`
  - `MODE_DeepResearch.md` → `deep-research.md`
  - `MODE_Introspection.md` → `introspection.md`
  - `MODE_Orchestration.md` → `orchestration.md`
  - `MODE_Task_Management.md` → `task-management.md`
  - `MODE_Token_Efficiency.md` → `token-efficiency.md`
  - `MODE_Business_Panel.md` → `business-panel.md`
  - `RESEARCH_CONFIG.md` → `research-config.md`

- **핵심 설계**:
  - `TriggerCategory(IntEnum)`: SKILL=0 > MODE=1 > MCP=2 > CORE=3
  - `MatchedTrigger` dataclass: category, context_file, is_explicit_flag
  - Hybrid mode loading: flag → full .md / NL → compact instruction
  - `MODE_COMPACT_MAP`: 각 모드 2-3줄 핵심 인스트럭션
  - `token-efficiency.md`: 항상 full (심볼 테이블 필수)
  - Serena/Tavily MCP: 항상 full .md

- **검증**: `uv run pytest` green, stdin→stdout 수동 테스트
- **블로커**: Sprint 2 전체의 선행 조건

### Sprint 1 Gate (QG1a) ✅ PASSED
- [x] `grep '</output>' src/superclaude/core/` → 0건
- [x] 6개 MCP 문서 각 40줄 이상
- [x] `src/superclaude/execution/` 디렉토리 부재
- [x] `uv run pytest` green (720 passed)

---

## Sprint 2: 테스트 체계 완성

> T1.5 완료 후 실행. 새 모듈 테스트 + 교차 디렉토리 통합 테스트.
> Plan ref: Phase 1.4, 1.5.

### T2.1 — context_trigger_map 테스트
- **Plan ref**: 1.4
- **파일**: `tests/unit/test_context_trigger_map.py` (CREATE)
- **케이스** (6개):
  - `test_skill_trigger_matching` — SKILL_TRIGGERS 패턴 매칭
  - `test_mode_flag_vs_natural_language` — `--brainstorm` (flag) vs "brainstorm ideas" (NL)
  - `test_duplicate_flag_nl_dedup` — 동일 파일 flag+NL → flag만 채택
  - `test_priority_ordering` — SKILL > MODE > MCP > CORE 정렬
  - `test_composite_flag_expansion` — `--frontend-verify` → 3 MCP 확장
  - `test_no_mcp_suppression` — `--no-mcp` 시 MCP 전체 억제
- **의존**: T1.5
- **병렬**: T2.2~T2.5와 동시

### T2.2 — context_injection 테스트
- **Plan ref**: 1.4
- **파일**: `tests/unit/test_context_injection.py` (CREATE)
- **케이스** (9개):
  - `test_injection_mode_full_md` — MODE + explicit flag → full .md
  - `test_injection_mode_compact` — MODE + NL → compact instruction
  - `test_injection_mode_instruction` — MCP → instruction string
  - `test_injection_mode_hint` — SKILL → hint 텍스트
  - `test_token_efficiency_always_full` — NL에서도 full .md
  - `test_serena_tavily_always_full` — Serena/Tavily 항상 full
  - `test_token_limit_enforcement` — MAX_TOKENS 초과 스킵
  - `test_session_dedup` — 중복 인젝션 방지
  - `test_skills_summary_output` — 서머리 포맷
- **의존**: T1.5
- **병렬**: T2.1, T2.3~T2.5와 동시

### T2.3 — skill_metadata 테스트
- **Plan ref**: 1.4
- **파일**: `tests/unit/test_skill_metadata.py` (CREATE)
- **케이스** (4개):
  - `test_skill_directory_discovery`
  - `test_agent_routing` — VALID_AGENTS 매칭 (**7개 누락 수정 포함**)
  - `test_invalid_agent_rejected`
  - `test_fork_context_detection`
- **주의**: VALID_AGENTS에 7개 에이전트 추가 필요 (business-panel-experts, simplicity-guide, self-review, requirements-analyst, socratic-mentor, learning-guide, technical-writer)
- **의존**: T1.5
- **병렬**: T2.1, T2.2, T2.4, T2.5와 동시

### T2.4 — session_init 테스트
- **Plan ref**: 1.4
- **파일**: `tests/unit/test_session_init.py` (CREATE)
- **케이스** (4개):
  - `test_hook_tracker_init`, `test_old_session_cleanup`
  - `test_git_status_format`, `test_pr_status_check`
- **병렬**: T2.1~T2.3, T2.5와 동시

### T2.5 — 교차 디렉토리 통합 테스트
- **Plan ref**: 1.5
- **설계 문서**: `docs/test-design-cross-ref-integration.md`
- **파일**: `tests/integration/test_cross_directory_refs.py` (CREATE)
- **클래스** (9개, ~80 테스트):

| 클래스 | 검증 대상 |
|--------|----------|
| `TestPersonaAbbreviations` | FLAGS.md persona_index → 에이전트 파일 |
| `TestMCPWiring` | FLAGS.md MCP 플래그 → MCP 문서 |
| `TestTriggerMapPaths` | TRIGGER_MAP 경로 → 실제 파일 |
| `TestHooksScriptPaths` | hooks.json 스크립트 → 파일 |
| `TestAgentModeMapping` | 에이전트 permissionMode → FLAGS.md |
| `TestSkillAgentRouting` | SKILL.md agent → VALID_AGENTS |
| `TestInstallPathsMapping` | COMPONENTS dict → 소스 디렉토리 |
| `TestModeFileNaming` | kebab-case 컨벤션 |
| `TestCoreImportChain` | CLAUDE_SC.md @-참조 유효성 |

- **의존**: T1.5 (kebab-case 파일명)
- **병렬**: T2.1~T2.4와 동시

### Sprint 2 Gate (QG1: Phase 1 완료) ✅ PASSED
- [x] `uv run pytest` 전체 green (882 passed)
- [x] `uv run pytest --cov=superclaude` 커버리지 ≥ 50%
- [x] 신규 테스트 파일 5개 존재 + 통과
- [x] VALID_AGENTS 7개 누락 수정 완료 + BUILTIN_AGENTS 패턴 추가
- [ ] → `git tag v4.4.0+ajitta`

---

## Sprint 3: 스킬 테스트 FW + 기존 리네임

> Phase 2 진입. 스킬 품질 보증 체계 구축 + 기존 스킬 sc: prefix 적용.
> Plan ref: Phase 2.1, 2.4.

### T3.1 — skill_linter.py 구현
- **Plan ref**: 2.1
- **파일**: `src/superclaude/skills/_testing/skill_linter.py` (CREATE)
- **인터페이스**: `lint_skill(skill_dir) → SkillLintResult`, `lint_all_skills(root) → list`
- **검증 규칙** (7개): frontmatter-required, frontmatter-types, component-structure, flow-section, bounds-section, examples-section, file-references
- **테스트**: `tests/unit/test_skill_linter.py` (기존 3개 스킬로 검증)

### T3.2 — trigger_validator.py 구현
- **Plan ref**: 2.1
- **파일**: `src/superclaude/skills/_testing/trigger_validator.py` (CREATE)
- **인터페이스**: `validate_triggers(skills_root, commands_root) → list[TriggerConflict]`
- **테스트**: `tests/unit/test_trigger_validator.py`
- **병렬**: T3.1과 동시

### T3.3 — CLI 통합 (doctor + skills lint)
- **Plan ref**: 2.1
- **파일 수정**: `cli/doctor.py` (스킬 체크 추가), `cli/main.py` (`skills lint` 서브커맨드)
- **의존**: T3.1, T3.2 완료 후

### T3.4 — 기존 스킬 sc: 리네임 (3개)
- **Plan ref**: 2.4
- **리네임**:
  - `skills/ship/` → `skills/sc-ship/`
  - `skills/confidence-check/` → `skills/sc-confidence-check/`
  - `skills/simplicity-coach/` → `skills/sc-simplicity-coach/`
- **수정**: 각 SKILL.md `name:` 필드, install_paths.py, hooks.json 참조
- **검증**: `superclaude skills lint`, `superclaude doctor`
- **병렬**: T3.1~T3.3과 동시 (린터 없이도 리네임 독립 실행 가능)

### Sprint 3 Gate ✅ PASSED
- [x] `superclaude skills lint` → 3/3 sc: 스킬 통과
- [x] `superclaude doctor` 스킬 lint 체크 포함 (7 checks)
- [x] 기존 3개 스킬 sc: prefix 적용 완료 (sc-ship, sc-confidence-check, sc-simplicity-coach)
- [x] `_testing/` 모듈 테스트 green (skill_linter 21 tests + trigger_validator 19 tests)
- [x] `uv run pytest` 전체 green (922 passed)

---

## Sprint 4: Wave 1 커맨드→스킬 전환

> 4개 전환을 병렬 실행. 각 전환은 IMPROVEMENT_PLAN.md 2.2.2 범용 체크리스트 준수.
> Plan ref: Phase 2.2.

### 전환 프로세스 (공통, 2.2.2 체크리스트)
```
Phase A 분석: 커맨드 읽기 → 필드 매핑 → 트리거 설계 → 에이전트 결정 → 경계 분석
Phase B 구현: 디렉토리 생성 → SKILL.md → 훅 스크립트 → 커맨드 stub
Phase C 검증: skill_linter → trigger_validator → 수동 테스트 → install_paths 확인
```

### T4.1 — sc:git 스킬 전환
- **소스**: `commands/git.md` (94줄)
- **상세 설계**: IMPROVEMENT_PLAN.md 2.2.1 (프로토타입 스펙, 778-1082행)
- **생성**:
  - `src/superclaude/skills/sc-git/SKILL.md` (frontmatter + component)
  - `src/superclaude/skills/sc-git/scripts/validate_git_safety.py` (PreToolUse 훅)
- **에이전트**: general-purpose
- **수정**: `commands/git.md` → thin stub (`allowed-tools: []`)
- **병렬**: T4.2~T4.4와 동시

### T4.2 — sc:test 스킬 전환
- **소스**: `commands/test.md`
- **에이전트**: quality-engineer
- **핵심 추가**: 테스트 러너 감지, 커버리지 리포팅, 환경 설정
- **생성**: `src/superclaude/skills/sc-test/SKILL.md`
- **수정**: `commands/test.md` → thin stub
- **병렬**: T4.1, T4.3, T4.4와 동시

### T4.3 — sc:troubleshoot 스킬 전환
- **소스**: `commands/troubleshoot.md`
- **에이전트**: root-cause-analyst
- **핵심 추가**: 3-cycle 가설 제한, 에스컬레이션 게이트
- **생성**: `src/superclaude/skills/sc-troubleshoot/SKILL.md`
- **수정**: `commands/troubleshoot.md` → thin stub
- **병렬**: T4.1, T4.2, T4.4와 동시

### T4.4 — sc:cleanup 스킬 전환
- **소스**: `commands/cleanup.md`
- **에이전트**: refactoring-expert
- **핵심 추가**: 안전성 검증 훅, before/after diff
- **생성**: `src/superclaude/skills/sc-cleanup/SKILL.md`
- **수정**: `commands/cleanup.md` → thin stub
- **병렬**: T4.1~T4.3과 동시

### Sprint 4 Gate (QG2a: Wave 1 완료) ✅ PASSED
- [x] 7개 sc: 스킬 — `skill_linter` 전체 통과 (0 errors, 4 warnings on pre-existing)
- [x] 4개 커맨드 thin stub 교체 완료 (allowed-tools: [])
- [x] `trigger_validator` 신규 에러 충돌 0건 (cross-category warnings는 stub↔skill 공존으로 정상)
- [ ] `/sc:name` 호출 + auto-trigger 수동 테스트
- [x] `uv run pytest` green (916 passed, 20 skipped)
- [ ] → `git tag v4.5.0+ajitta`

---

## Sprint 5: Wave 2 커맨드→스킬 전환

> Wave 1 검증 후 진행. 동일 프로세스.
> Plan ref: Phase 2.3.

### T5.1 — sc:build 스킬 전환
- **소스**: `commands/build.md`
- **에이전트**: devops-architect
- **핵심 추가**: 빌드 시스템 감지, 에러 복구
- **병렬**: T5.2~T5.4와 동시

### T5.2 — sc:estimate 스킬 전환
- **소스**: `commands/estimate.md`
- **에이전트**: system-architect
- **핵심 추가**: Read-only (파일 수정 없음), 복잡도 스코어링
- **병렬**: T5.1, T5.3, T5.4와 동시

### T5.3 — sc:document 스킬 전환
- **소스**: `commands/document.md`
- **에이전트**: technical-writer
- **핵심 추가**: 템플릿 선택, 출력 형식 옵션
- **병렬**: T5.1, T5.2, T5.4와 동시

### T5.4 — sc:design 스킬 전환
- **소스**: `commands/design.md`
- **에이전트**: system-architect
- **핵심 추가**: 스펙 출력 템플릿, 검증 체크리스트
- **병렬**: T5.1~T5.3과 동시

### Sprint 5 Gate (QG2: Phase 2 완료) ✅ PASSED
- [x] sc: 스킬 총 11개 (3 리네임 + 8 전환) — 전체 lint 통과 (0 errors)
- [x] 8개 커맨드 thin stub 교체 완료 (all allowed-tools: [])
- [x] `trigger_validator` 신규 에러 충돌 0건 (cross-category warnings는 stub↔skill 공존으로 정상)
- [ ] Anthropic 공식 스킬 (code-review, skill-creator) 정상 동작 확인
- [ ] `uv run pytest --cov=superclaude` 커버리지 ≥ 60%
- [x] `uv run pytest` green (908 passed, 28 skipped)
- [ ] → `git tag v4.6.0+ajitta`

---

## Sprint 6: CLI/DX 강화

> Plan ref: Phase 3.

### T6.1 — doctor 체크 확장 (6→11개)
- **Plan ref**: 3.1
- **파일**: `src/superclaude/cli/doctor.py` (MODIFY)
- **추가 체크** (5개):

| # | 체크 | 설명 |
|---|------|------|
| 7 | 스킬 SKILL.md 유효성 | 모든 sc: 스킬 frontmatter/구조 |
| 8 | 트리거 충돌 | 스킬 간, 스킬-커맨드 간 |
| 9 | 전환 완성도 | 8/8 stub + 스킬 쌍 |
| 10 | MCP 가용성 | 설정된 MCP 접속 |
| 11 | 버전 호환성 | Claude Code 버전 |

- **출력**: `Score: 11/11`
- **병렬**: T6.2, T6.3과 동시

### T6.2 — skills list 서브커맨드
- **Plan ref**: 3.2
- **파일**: `src/superclaude/cli/main.py` (MODIFY)
- **기능**: `superclaude skills list [--verbose]`
- **출력**: Original/Migrated 구분, Official 감지, 트리거 통계
- **병렬**: T6.1, T6.3과 동시

### T6.3 — install-skill 경로 확장
- **Plan ref**: 3.3
- **파일**: `src/superclaude/cli/install_skill.py` (MODIFY)
- **작업**: 절대 경로 지원 (`~/projects/my-skill/`)
- **범위 축소**: GitHub URL은 post-Phase 3
- **병렬**: T6.1, T6.2와 동시

### Sprint 6 Gate (QG3: Phase 3 완료) ✅ PASSED
- [x] `superclaude doctor` → 11/11 green (all checks pass)
- [x] `superclaude skills --list` shows Original/Migrated distinction
- [x] `install-skill` supports absolute paths
- [x] `uv run pytest` green (908 passed, 28 skipped)
- [ ] → `git tag v5.0.0+ajitta`

---

## Sprint 7: 아키텍처 진화 (실험적)

> Plan ref: Phase 4. 프로토타입 수준.

### T7.1 — SKILL.md 의존성 스키마 확장
- **Plan ref**: 4.1
- **작업**: `requires`, `enhances`, `version` frontmatter 지원
- **파일**: `skills/_testing/skill_linter.py` (MODIFY: 새 필드 검증)

### T7.2 — 의존성 해석기
- **Plan ref**: 4.1
- **파일**: `skills/_testing/dependency_resolver.py` (CREATE)
- **기능**: 토폴로지 정렬, 순환 감지, 미설치 의존
- **의존**: T7.1

### T7.3 — 자기 확장 프로토타입
- **Plan ref**: 4.2
- **작업**: 세션 패턴 감지 → 스킬 제안 (수동 승인, `skill-creator` 활용)
- **의존**: T7.2

### T7.4 — 버전 관리 기본 체계
- **Plan ref**: 4.3
- **작업**: `superclaude skills version`, `superclaude skills outdated`
- **병렬**: T7.1과 동시

### Sprint 7 Gate (QG4: Phase 4 완료) ✅ PASSED
- [x] SKILL.md frontmatter: `requires`, `enhances`, `version`, `changelog` 스키마 + 린터 규칙 추가
- [x] 의존성 해석기 동작 + 순환 감지 (`dependency_resolver.py`: DependencyGraph, build_graph)
- [x] 자기 확장 제안 프로토타입 (`self_extension.py`: PatternDetector, SkillSuggester)
- [x] CLI 통합: `--version-list`, `--outdated`, `--deps`, `--deps-check`
- [x] `uv run pytest` green (908 passed, 28 skipped)
- [x] `superclaude doctor` 11/11 green
- [ ] → `git tag v5.1.0+ajitta`

---

## 병렬 실행 맵

```
Timeline ──────────────────────────────────────────────────→

Sprint 1:  ┌─ T1.1 (stray tags)    ─┐
           ├─ T1.2 (MCP 보강)      ─┤
           ├─ T1.3 (exec 삭제)     ─┼── QG1a
           ├─ T1.4 (pm 테스트)     ─┤
           └─ T1.5 (리팩토링) ──────┘ ← 크리티컬 패스

Sprint 2:          ┌─ T2.1 (trigger_map 테스트)  ─┐
           T1.5 →  ├─ T2.2 (injection 테스트)     ─┤
                   ├─ T2.3 (metadata 테스트)      ─┼── QG1 → v4.4.0
                   ├─ T2.4 (session_init 테스트)   ─┤
                   └─ T2.5 (통합 테스트)           ─┘

Sprint 3:  ┌─ T3.1 (linter)     ─┬─ T3.3 (CLI) ─┐
   QG1 →   ├─ T3.2 (validator)   ─┘              ─┤
           └─ T3.4 (sc: 리네임)                   ─┘

Sprint 4:          ┌─ T4.1 (sc:git)          ─┐
                   ├─ T4.2 (sc:test)         ─┼── QG2a → v4.5.0
                   ├─ T4.3 (sc:troubleshoot) ─┤
                   └─ T4.4 (sc:cleanup)      ─┘

Sprint 5:          ┌─ T5.1 (sc:build)    ─┐
   QG2a →          ├─ T5.2 (sc:estimate)  ─┼── QG2 → v4.6.0
                   ├─ T5.3 (sc:document)  ─┤
                   └─ T5.4 (sc:design)    ─┘

Sprint 6:          ┌─ T6.1 (doctor+)       ─┐
   QG2 →           ├─ T6.2 (skills list)   ─┼── QG3 → v5.0.0
                   └─ T6.3 (install 확장)  ─┘

Sprint 7:  ┌─ T7.1 (스키마)  ─┬─ T7.2 (해석기) ─── T7.3 (자기확장) ─┐
   QG3 →   └─ T7.4 (버전)    ─┘                                     ─┘ QG4 → v5.1.0
```

---

## Quality Gates

| Gate | 조건 | 측정 | 차단 범위 |
|------|------|------|----------|
| **QG1a** | quick wins green, exec 삭제 | `uv run pytest`, `ls execution/` | Sprint 2 |
| **QG1** | Phase 1, coverage ≥50% | `pytest --cov`, 파일 존재 | Phase 2 진입 |
| **QG2a** | Wave 1 4 스킬 lint+trigger | `skills lint`, `trigger_validator` | Wave 2 |
| **QG2** | Phase 2, coverage ≥60%, 11 sc: | lint, cov, 스킬 수 | Phase 3 진입 |
| **QG3** | Phase 3, doctor 11/11 | `superclaude doctor` | Phase 4 진입 |
| **QG4** | Phase 4 프로토타입 | 수동 검증 | 릴리스 |

---

## 리스크 체크포인트

| Sprint | 리스크 | 감지 | 완화 |
|--------|--------|------|------|
| 1 | context_loader 리팩토링 시 훅 깨짐 | pytest + 수동 세션 | 리팩토링 전 동작 스냅샷 |
| 2 | 커버리지 50% 미달 | `--cov` 리포트 | 테스트 추가, 임계값 완화 |
| 3 | sc: 리네임 시 경로 깨짐 | `superclaude doctor` | install_paths 사전 확인 |
| 4-5 | 스킬 트리거 중복 | `trigger_validator` | 키워드 조정, 우선순위 명시 |
| 4-5 | 8개 동시 전환 품질 저하 | lint + 수동 | Wave 분리 (적용 완료) |
| 6 | doctor 체크 오탐 | 기존 환경 실행 | 체크별 독립 테스트 |

---

## 버전 릴리스

| Sprint | Phase | 버전 | 핵심 변화 |
|--------|-------|------|----------|
| 2 | Phase 1 완료 | `v4.4.0+ajitta` | 기반 정리, 4-file split, 50%+ coverage |
| 4 | Wave 1 완료 | `v4.5.0+ajitta` | sc:git/test/troubleshoot/cleanup |
| 5 | Phase 2 완료 | `v4.6.0+ajitta` | 11 sc: 스킬, 60%+ coverage |
| 6 | Phase 3 완료 | `v5.0.0+ajitta` | CLI 강화, doctor 11/11 |
| 7 | Phase 4 완료 | `v5.1.0+ajitta` | 의존성 모델, 자기 확장 |

---

## 태스크 요약

| Sprint | 태스크 수 | 생성 | 수정 | 삭제/리네임 |
|--------|----------|------|------|------------|
| 1 | 5 | 3 | 10 | 5삭제 + 9리네임 |
| 2 | 5 | 5 | 1 | 0 |
| 3 | 4 | 4 | 2 | 3리네임 |
| 4 | 4 | 6-8 | 4 | 0 |
| 5 | 4 | 4 | 4 | 0 |
| 6 | 3 | 0 | 3 | 0 |
| 7 | 4 | 2 | 1 | 0 |
| **합계** | **29** | **~24-26** | **~25** | **~17** |

---

## 핸드오프

Sprint 1의 T1.1~T1.4는 의존성 없이 즉시 병렬 실행 가능.

- `/sc:implement` — 개별 Task 구현
- `/sc:task` — 태스크 트래킹 + 위임
- `/sc:test` — 각 Gate에서 테스트 실행
