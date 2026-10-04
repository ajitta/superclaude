---
status: complete
revised: 2026-10-04
---

# 항상 skip되는 cross-ref 테스트 제거 Implementation Plan

**Goal:** `uv run pytest`의 skip을 25개에서 1개(`AB_E2E` opt-in)로 줄인다. 이미 삭제된 구조를 검사하던 테스트 2개를 지운다.

**Architecture:** 변경 파일은 `tests/integration/test_cross_directory_refs.py` 하나다. 죽은 테스트 2개와 그 테스트만 쓰던 헬퍼, 상수를 함께 지우고, 이 파일에서 테스트를 지울 때 남기던 `# NOTE: ... removed` 주석을 한 줄 남긴다.

**Tech Stack:** pytest, ruff

## 근거

| 테스트 | skip 수 | 죽은 이유 |
|---|---|---|
| `TestAgentModeMapping::test_agent_mcp_abbreviations_are_valid` (:194-207) | 23 | `672055ce`(2026-04-03)에서 모든 agent의 `<mcp servers>` 필드를 제거해 파서가 항상 `[]`를 반환함 |
| `TestMCPWiring::test_mcp_config_doc_pairing` (:128-146) | 1 | `899b0b74`(2026-04-12)에서 `src/superclaude/mcp/configs/`를 삭제함 |

유지: `tests/integration/test_parallel_ab_e2e.py:24`. `claude -p` 인증이 필요해서 의도적으로 opt-in으로 둔 테스트다.

## 범위 확인 결과

- `docs/test-design-cross-ref-integration.md`는 master에 들어온 적이 없다. `f70e5ab7`(2026-03-02)에서 추가됐지만 이 커밋은 병합되지 않은 `feature/workflow-v5-implementation` 브랜치(local, origin)에만 있다(`git merge-base --is-ancestor f70e5ab7 HEAD` 실패). 그래서 master에서 정리할 문서는 없고, master에서 이 문서를 가리키는 곳은 모듈 docstring :7 한 줄뿐이다. master에서는 이 줄이 늘 없는 파일을 가리켰으므로 같은 커밋에서 지운다. 미병합 브랜치에 있는 문서는 건드리지 않는다.
- 저장소 전체를 검색해도 두 테스트 이름이나 헬퍼 이름을 언급하는 문서가 없다. `docs/codex/prompting_session_raw/0{2,3,5}_*.md`는 파일 경로만 참조하므로 그대로 유효하다. 종료된 `over-engineering-audit` 계획 문서의 `:243` 같은 줄 번호는 당시 기록이므로 고치지 않는다.
- `.py` 파일 수가 바뀌지 않으므로 `codex-module-count-drift` 테스트에는 영향이 없다.

## Phase 1: 죽은 테스트 제거 (커밋 1개)

**Files:** Modify: `tests/integration/test_cross_directory_refs.py`

삭제만 하는 변경이라 "실패하는 테스트 먼저" 단계는 해당하지 않는다. 대신 전후 skip 수로 검증한다.

- [x] Step 1: 기준선 기록
  `uv run pytest -rs -q` → `2635 passed, 25 skipped`
- [x] Step 2: 다음 블록 삭제. 테스트를 먼저 지우고 헬퍼와 상수를 나중에 지운다. 반대 순서로 지우면 편집 후 자동 실행되는 테스트 훅이 중간 상태에서 `NameError`(collection error 또는 23 failed)를 낸다. 최종 결과에는 영향이 없다
  - :6-7 docstring의 `Design doc: docs/test-design-cross-ref-integration.md` 줄과 그 위 빈 줄
  - :33-55 `parse_flags_mcp_section()`: :202 외에는 쓰는 곳 없음
  - :57-63 `parse_agent_mcp_servers()`: :199 외에는 쓰는 곳 없음
  - :103 `AGENT_FILES`: :197 외에는 쓰는 곳 없음. `tests/unit/test_agent_structure.py`에 있는 같은 이름은 그 파일의 별도 상수다
  - :128-147 `test_mcp_config_doc_pairing`
  - :194-209 `class TestAgentModeMapping` 전체
  - `import re`는 유지한다(:75, :91, :274에서 사용)
- [x] Step 3: 이 파일의 관례대로 NOTE 주석 추가(기존 :156-158 위치 옆)
  ```python
  # NOTE: TestAgentModeMapping and test_mcp_config_doc_pairing removed — agent
  # <mcp servers> tags (672055ce) and mcp/configs/ (899b0b74) no longer exist.
  ```
- [x] Step 4: 검증 (결과: `2635 passed, 1 skipped`, ruff `All checks passed!`, `make format` 253 files unchanged)
  - `uv run pytest -rs -q` → `2635 passed, 1 skipped`. 남은 skip은 `test_parallel_ab_e2e.py:24` 하나뿐이어야 한다
  - `uv run ruff check tests/integration/test_cross_directory_refs.py` → 위반 0
  - `make format` 후 diff에 이 파일 외의 변경이 없어야 한다
- [x] Step 5: 커밋
  - 브랜치: `chore/drop-dead-skip-tests`
  - 스테이징은 이 테스트 파일과 이 계획 문서만 한다. 작업 트리에 커밋되지 않은 `README.md` 변경(claude-mem 섹션 제거)이 있으니 함께 쓸려 들어가지 않게 한다
  - 메시지: `test: drop two always-skipped cross-ref tests`
  - `--no-ff` merge → push → master CI 확인 → 브랜치 삭제

## 완료 기준

- `uv run pytest` 종료 코드 0, `2635 passed, 1 skipped`
- passed 수가 그대로여야 한다. 삭제한 24개는 모두 skip이었으므로 passed가 줄면 다른 테스트를 잘못 지운 것이다
- 되돌리기: `git revert <merge>`
