---
status: complete
revised: 2026-10-13
---

# Phase C: `skills` 디렉터리 컴포넌트

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C5 표.

현재 상태 (`4a379a32`):
- `install_paths.py:27-39` `COMPONENTS`에 skills 없음. `:45` `SHARED_TARGET_COMPONENTS = ("agents", "output-styles")`, `:56` `shipped_md_names`
- 하위 디렉터리 단위 처리는 `templates`만, 세 곳에 따로: `install_components.py:183-211` (copytree), `install_inventory.py:107-115` `_source_dir_names` + `:181-187` (집계)
- `verify_drift.py:64-102` `_check_component`는 최상위 `*.md` + `core/rules/`만 비교. `:7-10` docstring과 `main.py:509-510` 도움말이 "templates/ … NOT drift-checked"라고 말함
- 공유 디렉터리 처리: `install_git_exclude.py:110-113` (파일 단위 항목), `install_inventory.py` `_uninstall_shared_component` (파일 단위 삭제, 빈 디렉터리만 제거)

설계 결정: 모양 두 가지를 상수로 둔다.
- `DIRECTORY_COMPONENTS = ("templates", "skills")`: 소스의 하위 디렉터리 하나가 설치 단위
- `SHARED_TARGET_COMPONENTS = ("agents", "output-styles", "skills")`: 대상 디렉터리를 사용자·다른 도구와 공유 → 배포한 이름만 건드림
- 둘을 잇는 함수 `shipped_names(component) -> set`: 디렉터리 컴포넌트면 하위 디렉터리 이름, 아니면 `.md` 파일 이름. 공유 대상 처리 코드는 이것만 부른다

### Task C1: 실패하는 테스트

**Files:** Create: `tests/unit/test_install_skills_component.py` | Modify: `tests/integration/test_cross_directory_refs.py:174-186`

- [x] Step 1: 레지스트리
  - `COMPONENTS["skills"][:2] == ("skills", "skills")`
  - `DIRECTORY_COMPONENTS == ("templates", "skills")`, `"skills" in SHARED_TARGET_COMPONENTS`
  - `shipped_names("skills") == {"sc-author"}`, `shipped_names("agents") == shipped_md_names("agents")`
  - `test_cross_directory_refs.py:184` 기대 집합에 `"skills"` 추가
- [x] Step 2: install (`install_component("skills", base, ...)`, `tmp_path`)
  - 설치 후 `base/skills/sc-author/references/fields.yaml` 존재, 소스와 같은 바이트
  - `base/skills/other/SKILL.md`를 미리 심음 → 설치 후 그대로
  - 대상이 있고 `force=False` → skipped 1, 내용 그대로. `force=True` → 교체
  - 대상 `skills/sc-author`가 `base` 밖을 가리키는 symlink → failed, 링크 대상 안 지움 (`_safe_target_path` 유지. Windows에서 symlink 생성 권한이 없으면 `pytest.skip`)
- [x] Step 3: uninstall (`uninstall_all` 또는 `_uninstall_shared_component("skills", ...)`)
  - `skills/sc-author/` 제거, `skills/other/SKILL.md` 남음
  - `sc-author`만 있었으면 빈 `skills/`도 제거
  - dry-run → 아무것도 안 지우고 `Would remove` 메시지
- [x] Step 4: git-exclude (`_collect_entries("local")`)
  - `.claude/skills/sc-author/` 포함, `.claude/skills/` 단독 항목 없음
  - `_collect_entries("project")`는 변화 없음
- [x] Step 5: verify-drift (`verify_drift(base)`)
  - 설치 직후 `skills`·`templates` 모두 OK만
  - 설치본 `skills/sc-author/references/fields.yaml` 수정 → 키 `sc-author/references/fields.yaml` DRIFTED
  - `skills/sc-author/extra.md` 추가 → EXTRA. `skills/other/SKILL.md` → 보고 안 됨
  - `skills/sc-author/` 삭제 → 그 안의 소스 파일마다 MISSING
- [x] Step 6: inventory (`list_all_components`, `superclaude install --list-all`이 씀)
  - `skills`: available = 소스 하위 디렉터리 수, installed = 설치된 그 이름 디렉터리 수. `skills/other/`는 세지 않음
- [x] Step 7: `uv run pytest tests/unit/test_install_skills_component.py tests/integration/test_cross_directory_refs.py -v` → 새 테스트 FAIL

### Task C2: 레지스트리 (`install_paths.py`)

**Files:** Modify: `src/superclaude/cli/install_paths.py:20-59,185-198`

- [x] Step 8: `COMPONENTS`에 `"skills": ("skills", "skills", "Skills (user-invoked; /sc-author)")`. `:20-26` 주석의 대상 종류 설명에 skills와 디렉터리 단위 처리 추가
- [x] Step 9: `DIRECTORY_COMPONENTS` 추가, `SHARED_TARGET_COMPONENTS`에 `"skills"`. `:41-44` 주석: 공유 대상에서는 배포 이름만 지우고 local scope는 이름 단위로 exclude, 디렉터리 컴포넌트의 이름은 디렉터리
- [x] Step 10: `install_inventory.py:107-115` `_source_dir_names`를 `install_paths.dir_names(directory)`로 옮기고 `shipped_names(component)` 추가. `install_inventory.py`는 새 함수를 import
- [x] Step 11: `:185-186` 주석 "SuperClaude ships no skills now, so there is no source dir to diff against" → "Legacy skill names are listed literally because their sources were deleted; the current `skills` component never ships these names." `LEGACY_SKILL_NAMES`는 그대로 (C5 legacy prune)

### Task C3: install·git-exclude

**Files:** Modify: `src/superclaude/cli/install_components.py:183-211`, `src/superclaude/cli/install_git_exclude.py:92-128`

- [x] Step 12: `install_components.py:183-185` `if component == "templates":` → `if component in DIRECTORY_COMPONENTS:`. 주석: "Directory components install one source subdirectory per unit (templates for /sc:init, skills for /sc-author)". 본문 그대로
- [x] Step 13: `install_git_exclude.py:110-113` 반복이 `shipped_names`를 부르고, 디렉터리 컴포넌트 이름 뒤에 `/`. `_collect_entries` docstring의 "Agents and output styles are listed per-file" → 공유 대상 세 개, skills는 디렉터리 이름 단위

### Task C4: uninstall·inventory

**Files:** Modify: `src/superclaude/cli/install_inventory.py:152-231,234-287,381-390`

- [x] Step 14: `list_all_components` 집계 `:181-187`: `if component in DIRECTORY_COMPONENTS:` (`dir_names` 사용). 주석의 "templates" → "directory components"
- [x] Step 15: `_uninstall_shared_component`: `present`를 `shipped_names`로 만들고, 디렉터리 컴포넌트면 `is_dir()` + `shutil.rmtree`, 아니면 지금처럼 파일 삭제. docstring에 skills 추가. dry-run 메시지 형식 유지
- [x] Step 16: `uninstall_all` 3단계 주석 `:381-382` "(agents/, output-styles/)" → "(agents/, output-styles/, skills/)"

### Task C5: verify-drift

**Files:** Modify: `src/superclaude/cli/verify_drift.py:1-22,64-102`, `src/superclaude/cli/main.py:501-511`

- [x] Step 17: `_check_component`에 디렉터리 컴포넌트 분기: `shipped_names`의 이름마다 소스 하위 디렉터리를 `rglob("*")`로 걸어 파일마다 `_compare_files`, 키는 `<dir>/<posix 상대 경로>`. EXTRA는 같은 이름의 대상 디렉터리 안에서만 (다른 스킬은 절대 안 봄). 무시 패턴은 install의 `shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")`와 같게 → 상수로 두고 두 모듈이 공유
- [x] Step 18: 모듈 docstring `:7-10`과 `main.py` `verify-drift` docstring `:509-510`: "Not checked: templates/ and the merged hooks.json" → "Not checked: the merged hooks.json". 둘을 같이 고친다 (docstring이 "keep the two in step")

### Task C6: 인벤토리 문서 카운트

**Files:** Modify: `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` §1 표, `tests/unit/test_codex_component_map.py:69-104`

- [x] Step 19: 표에 행 `` | `skills/*` | 1 | 사용자가 호출하는 스킬 디렉터리 (`/sc-author`) | ``
- [x] Step 20: `_actual_counts`에 `"skills/*": len(dir_names(_component_dir("skills")))`, `_ROW_KEYS`에 `` "`skills/*`": "skills/*" ``

### Task C7: 검증과 커밋

- [x] Step 21: `uv run pytest tests/unit/test_install_skills_component.py tests/integration/test_cross_directory_refs.py tests/unit/test_verify_drift.py tests/unit/test_cli_install.py tests/unit/test_install_git_exclude.py tests/unit/test_codex_component_map.py -v` → PASS
- [x] Step 22: `make format && make lint && uv run pytest` → 모두 exit 0
- [x] Step 23: 커밋 `feat(install): add the skills directory component and drift-check directory components`

## Deviations

- Step 2 symlink 테스트는 Windows에서 skip (`sys.platform == "win32"`, symlink 생성 권한). 로컬 결과 1 skipped, CI(Linux)에서 실행됨
- 무시 패턴을 `install_paths.DIRECTORY_IGNORE` 상수로 두고 install(copytree)과 drift(`_files_under`)가 공유 (Step 17의 "상수로 두고 두 모듈이 공유"를 그대로 따름, 위치만 `install_paths`)
- Phase gate 추가 확인 (plan Proof 4를 앞당겨 실행): scratchpad의 임시 git 프로젝트에 `.claude/skills/other/SKILL.md`를 심고 `superclaude install --scope local --force` → `86 installed, 0 failed`, `.claude/skills/{other,sc-author}`, exclude에 `.claude/skills/sc-author/` 한 줄. `verify-drift --scope local` → `templates 4/4 OK`, `skills 1/1 OK`. `uninstall --scope local --yes` → `Removed: 1 SC skills dir(s) … (preserved non-SC files)`, `other/SKILL.md` 내용 그대로
