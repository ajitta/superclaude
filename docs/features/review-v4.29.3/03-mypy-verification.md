PASS WITH FIXES — 코드 변경은 런타임 동작을 바꾸지 않고 `mypy src`가 로컬·CI 모두 clean이지만, 이 커밋으로 거짓이 된 live 문서 한 곳(codex backlog F-014)을 갱신해야 한다.

## 실행 결과

검증 대상: `1f50d5cd` (`fix/mypy-clean`, 부모 `c4b415bf`), detached worktree, 기존 `.venv`(mypy 2.4.0).

| 명령 | rc | 결과 |
|---|---|---|
| `uv run mypy src` | 0 | `Success: no issues found in 53 source files` |
| `make typecheck` | 0 | `uv run mypy src` → 같은 결과 |
| `make help` | 0 | `make typecheck - Type-check src/ with mypy (CI runs it; must be clean)` |
| `uv run ruff format --check src tests` | 0 | `235 files already formatted` |
| `uv run ruff check src tests` | 0 | `All checks passed!` |
| `uv run pytest` (전체) | 0 | `3885 passed, 3 skipped in 37.21s` |
| 부모 트리(`git archive HEAD~1`) `mypy src` | 1 | `Found 34 errors in 16 files` — 34건 모두 이 diff의 hunk에 하나씩 대응 |
| 부모 트리에 plain-mypy recipe 적용 | make 2 | 오류가 있으면 새 타깃이 실패함을 확인 |
| override 제거 config(`mypy-noov.ini`) | 1 | `import-untyped` 3건뿐(`spec_loader.py:9`, `eval_runner.py:16`, `author_check.py:24`) |
| override 제거 + `types-PyYAML`·`types-jmespath` stubs(`MYPYPATH`) | 0 | `Success: no issues found in 53 source files` |
| override 유지 + stubs | 0 | 같은 결과(`warn_unused_configs` 경고 없음) |
| stub 적용 probe(`reveal_type(yaml.safe_load)`) | — | `def (stream: ...) -> Any`. stubs가 실제로 로드됨 (`x: int = yaml.dump({})`는 오류로 잡힘) |
| `uv run mypy src/superclaude`, `... cli utils hooks` | 0 | 둘 다 `Success` (F-014 기록과 다름, V-1) |
| `superclaude context explain "--brainstorm ..."` | 0 | `modes/MODE_Brainstorming.md <- matched "--brainstorm"` — 컴파일된 `TRIGGER_MAP` 경로 정상 |

CI run `39163819326`: `success`, headSha `1f50d5cd11e0…`, `workflow_dispatch`. job은 2개가 아니라 3개다.
- `Lint, plugin and doctor checks` ✓ 11s — `Run mypy` 단계 출력 `Success: no issues found in 53 source files` (Python 3.10.22, mypy==2.4.0 fresh resolve)
- `Test on Python 3.13` ✓ — `3885 passed, 3 skipped`
- `Test on Python 3.10` ✓ — `3885 passed, 3 skipped`

## 발견 사항

### V-1 · Low · confidence High — codex backlog F-014의 mypy 절이 이 커밋으로 거짓이 됨
- 위치: `docs/codex/prompting_session_raw/08_current_findings_and_backlog.md:284-300` (요약 표 `:37` F-014 행 포함)
- 증거: 문서는 "`uv run mypy src/superclaude` → exit 2", "`... cli utils hooks` → Found 35 errors"를 기록하고 "“mypy clean”을 이미 존재하는 hard gate로 주장하지 않는다"고 쓴다. 지금은 두 명령 모두 rc 0 `Success`이고 CI `checks` job이 `mypy src`를 hard gate로 돌린다. 이 문서는 `:13-15`에서 "mypy 오류는 이 문서가 소유한다… `git log <SHA>..HEAD -- src/`가 비어 있지 않으면 재측정한다"고 스스로 밝힌다. exit 2 기록은 이 커밋 전부터 낡아 있었다(부모에서도 53 files 검사). "hard gate가 아니다"는 문장은 이 커밋 때문에 거짓이 됐다. 테스트가 이 문서를 지키지 않으므로 suite는 green이다.
- 수정: `:284-300`의 mypy 블록을 다음으로 바꾼다. "`uv run mypy src` → `Success: no issues found in 53 source files` @1f50d5cd. `make typecheck`와 CI `checks` job(`.github/workflows/test.yml` `Run mypy`)이 같은 명령을 hard gate로 실행한다. 이전 35/43건 기록은 폐기." F-014 요약 행(`:37`)은 mypy 절반을 해결로 표시하고 coverage(`fail_under` 없음)만 남긴다.

### V-2 · Info · confidence Medium — unpinned mypy가 이제 CI hard gate
- 위치: `pyproject.toml:46` `"mypy>=1.0"`, `.github/workflows/test.yml:86-89`
- 증거: CI는 `uv pip install --system -e ".[dev]"`로 매번 새로 resolve한다(로그 `+ mypy==2.4.0`). mypy 새 릴리스가 검사를 추가하면 코드 변경 없이 `checks` job이 red가 될 수 있다. ruff도 같은 구조이고 `.claude/rules/gotchas/general.md` `uv-lock-local-only`가 이를 의도된 동작으로 기록하므로 결함은 아니다.
- 수정(선택): 코드 수정은 필요 없다. 원하면 `uv-lock-local-only`/`lint-upgrade-attribution` gotcha에 "mypy도 같다. 갑자기 red가 되면 `uvx mypy@<old> src`로 비교한다"를 한 구절 덧붙인다.

### V-3 · Info · confidence High — CHANGELOG 문구의 사소한 부정확
- 위치: `CHANGELOG.md:13`
- 증거: "local renames"로 묶었지만 `context_loader.py`의 `TRIGGER_MAP` → `_TRIGGERS`는 module-level rename이다. 런타임 영향은 없다(아래 참조). 측정한 오류 수는 34이고 "33–34"는 환경 차이를 포함한 표현이라 맞다.
- 수정(선택): "local renames" → "renames (a local in `author_check`, the raw trigger list in `context_loader`)". 생략해도 무방하다.

## 확인했으나 문제 없음

hunk별 런타임 동작:
- `author_check.py:121` `fields: dict = ...`, `:255` `field_lines: dict[str, int]`, `:689` `token: str` — 지역 변수 annotation은 실행 시 평가되지 않는다. 동작은 같다.
- `author_check.py:520-541` — `selfclose = bool(selfclose_mark) or is_void(name)`: 이전에는 `None`/`""`/`"/"` 또는 bool이었고 지금은 bool이다. 유일한 소비처 `if not selfclose`의 truthiness가 같다. `line` → `line_no`: 함수 앞부분 `for line in lines`(str)과 이름이 겹쳐 생긴 오류였다. 루프 뒤에는 `line`을 읽는 곳이 없다(`:543-566` 확인). `is_placeholder` 안의 `selfclose`는 별도 스코프다.
- `entry.py` `rc: int = cli()` — click group `__call__`은 standalone mode라 `sys.exit`로 끝나고 반환하지 않는다. annotation은 평가되지 않는다(`from __future__ import annotations`). 동작은 같고, hook fast path(`argv[0] == "hook"`)도 건드리지 않았다.
- `install_components.py` `install_hooks` → `Tuple[int, int, List[str]]` — 3개 return(`:356,363,408`)과 일치한다. 호출처 `install_components.py:559`와 `tests/unit/test_cli_install.py`의 7곳 모두 3-unpack이다. annotation만 바뀌었다.
- `install_inventory.py` `Optional[Path]` — `:290`에서 `None`이면 `get_base_path`. `project_root` → `mcp_root`: step 8(`:521`)의 `project_root`는 step 9 이후 읽히지 않는다. 이전 코드도 덮어쓰기만 했다. 동작은 같다.
- `install_settings.py` `Counter[...]`, `install_paths.py` `List[Path]`, `verify_drift.py` `Dict[str, str]`, `install_interactive.py` `choice: int`(`IntRange` → int), `install_mcp.py` `api_key: str`, `parallel_ab/runner.py` `result: dict` — 모두 annotation만 바뀌었다.
- `coordinator.py` assert 3개 — `_record_baseline_or_die`는 `run_baseline_only()`(`:85`)·`run()`(`:94`)에서만 호출되고, `_run_smoke`(`:105`)·`_run_mutator_cycle`(`:126`)은 `run()` 안에서만 호출된다. 두 진입점 모두 먼저 `_setup()`이 `self._worktree = self._wt_mgr.create()`(반환형 `Worktree`, non-Optional)을 실행한다. `_run_mutator_cycle`의 assert는 같은 전제로 이미 assert하는 `_invoke_mutator`(`:286`) 뒤에 온다. src/tests에서 이 private 메서드를 다른 곳에서 부르지 않는다. 테스트는 `patch.object`로 대체하거나 `run()`을 거친다. 새 실패 경로는 없다. `-O`에서 assert가 빠지는 것도 이전과 같다(전에도 검사 없음).
- `context_loader.py` — 소비처(`context_loader.py:679`, `cli/main.py:985,995` `superclaude context explain`, `tests/unit/test_context_loader.py`, `tests/unit/test_content_usage.py`)는 모두 컴파일된 `TRIGGER_MAP`을 읽는다. 이전의 raw `TRIGGER_MAP`은 같은 모듈에서 즉시 덮어써져 외부에서 접근할 수 없었다. 따라서 raw 형태의 소비처는 있을 수 없고, 실제로 `_TRIGGERS` 참조도 src/tests/evals 어디에도 없다. 소스 텍스트를 파싱하는 테스트도 없다. module-level annotation은 문자열이라 3.10에서도 평가되지 않는다. legacy `~/.claude/superclaude/scripts/` copy는 독립 실행 파일이라 영향받지 않는다. docs의 `TRIGGER_MAP` 언급은 이름이 유지되므로 모두 유효하다.
- `insight_writer.py:692` `bool(current != recorded)` — `str != Any` 비교 결과는 이미 bool이다. `:889` `rc: int`도 annotation뿐이다.
- 제거된 테스트 `test_typecheck_gate`는 삭제된 baseline 로직만 검증했다. 남은 `test_makefile_help.py`(help 문구)는 green이다. 미사용 `import os` 제거는 ruff로 확인했다.
- `MYPY_BASELINE`/baseline 동작의 잔존 참조: `git grep` 결과 CHANGELOG 4.29.4 이력과 `docs/features/review-v4.29.3/*`, `docs/features/over-engineering-audit/*` 기록에만 남아 있다(제외 대상). AGENTS.md, Makefile, workflows README, tests, src에는 없다.
- CHANGELOG `[Unreleased]` 주장: plain `mypy src`가 clean이다 ✓, CI가 실행한다 ✓, 34건 수정 ✓, annotation/rename/assert/untyped import ✓, `install_hooks` 4→3 ✓, baseline 제거 ✓. "without behavior changes"는 위 hunk 검토로 성립한다.
- override가 실제 오류를 숨기지 않는다: stubs를 쓰면 override 없이도 0건이다. override가 가리던 것은 `import-untyped` 3건뿐이다.

## 검증하지 못한 것

- Windows에서 `make typecheck`/CI 동작 (Linux에서만 실행).
- 로컬 Python 3.10 인터프리터로 mypy 실행 (로컬은 3.13 venv + `python_version = "3.10"` config. 3.10.22 실행은 CI에서만 확인).
- 미래 mypy 릴리스나 stubs 버전 변화에 대한 내성 (V-2).
- `coordinator.py`의 실제 end-to-end 실행 (`claude -p`/mutator 금지 범위. 단위 테스트와 호출 경로 분석으로 대체).
