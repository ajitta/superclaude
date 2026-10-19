PASS WITH FIXES — W-1 데이터 손실은 세 scope와 모든 명령에서 고쳐졌고 회귀도 없다. 남은 것은 테스트 공백 둘, 오류 경로에서 사라지는 안내 한 줄, 문구 하나다(모두 Low, 머지를 막지 않음).

# W-1 독립 검증 — `fix/retired-skill-user-files` @ f36d4a0d

## 실행 결과

모든 CLI 실행은 `$REVIEW_DIR/sandbox/<case>/` 안에서 했다. `HOME`/`CLAUDE_CONFIG_DIR`/`UV_CACHE_DIR`/`PATH`(stub `claude`)를 sandbox로 두고, 프로세스 안에서 `realpath(HOME) != /home/ubuntu`를 assert했다. 실제 `~/.claude`(목록에서 `backups` 제외, `settings.json` md5, `skills/`)와 `~/.config` 가드는 matrix, old-release, pytest 실행 전후 모두 **clean**이었다. master는 `git archive 782996c3 src`로 `$REVIEW_DIR/src-master/`에 풀어 같은 하네스로 돌렸다(`harness/sb.py`, `matrix.py`, `oldrel.py`).

| # | 검사 | 결과 |
|---|---|---|
| 1 | 데이터 손실 matrix: user/project/local × `install`, `install --force`, `update`, `uninstall -y`, `uninstall --dry-run` × 15 cases | branch **225/225 OK**. master는 user-file·edited-helper·nested·symlink·DS_Store 계열 108건 실패(사용자 파일 삭제, symlink dir에서 rc=1) |
| 2 | 실제 옛 설치기로 설치 → branch로 업그레이드 | 102 revision(retired skill을 건드린 모든 커밋, cd2f8aab, era fixture 커밋과 그 부모, v4.1.9/v4.2.0/v4.3.0) × 3 scope × LF/CRLF. **first-parent와 태그 revision은 전부** 한 번에 완전 제거되고, 두 번째 install은 조용하며, verify-drift에 RETIRED가 없음. 예외는 X-4 |
| 3 | 생성 표 재생성(full clone `$REVIEW_DIR/regen`, 1805 commits) | `gen_shipped_names.py 782996c3`: `retired_skill_files.py` **byte-identical**, fixture는 `generated_from` 라벨만 다름(rev 인자 표기) |
| 4 | verify-drift / doctor | 모든 case에서 install 동작과 일치(아래) |
| 5 | era fixture stub→blob | 58 entry 전부 stub sha256 == blob bytes이고, era 커밋의 `git show` blob과 byte-identical. 다른 키는 바뀌지 않았고 `_blobs.json` 기존 키도 그대로(16개 추가) |
| 6 | 회귀 테스트가 잡는가 | 수정 hunk 3파일을 master로 되돌리면 `-k w1` **61 failed / 28 passed**(빌더 보고와 같음). call site(rmtree)만 되돌리면 54 failed |
| 7 | `uv run pytest`(HOME=sandbox) | **exit 0, 4364 passed, 3 skipped** |
|   | `ruff format --check src tests` / `ruff check src tests` / `make typecheck` | 239 files already formatted / All checks passed / Success, 54 files |
|   | `git diff 782996c3 HEAD -- src/superclaude/core src/superclaude/hooks` | 0줄 → canary 불필요 |

### matrix 세부(branch, scope 셋 모두 같은 결과)

- **shipped-only**(VS@cf5119f8 5파일), **CRLF**, **cc-placeholder**(confidence-check@802e847a, 옛 설치기와 같은 방식으로 `{{SKILLS_PATH}}`/`{{SCRIPTS_PATH}}`를 scope별로 치환), **placeholder+CRLF**: 디렉터리 전체 제거, Kept 줄 없음. verify-drift는 rc 1(RETIRED) → rc 0, doctor `retired` advisory는 1 → 0.
- **user-file / nested-user-dir / edited-helper / edited-helper-cc**: 사용자 파일만 원래 bytes 그대로 남고, 빈 `references/`는 지워지며, `Kept N` 수가 맞는다. 이후 verify-drift rc 0, doctor advisory 없음.
- **user-copy-of-shipped-elsewhere**(`backup/SKILL.md` = shipped 본문): 남는다. 경로까지 함께 비교한다는 뜻이다.
- **edited-skill-md**, **symlinked SKILL.md**(바깥 shipped 본문을 가리킴): 아무것도 지우지 않고 RETIRED도 아니며 출력도 없다(편차 1에 맞음).
- **symlinks-inside**(dir link → 바깥 shipped 파일 묶음, shipped 경로에 file link, broken link, 상대경로 link): link 4개 보존, `outside/` 불변, shipped 파일만 제거.
- **symlinked skill dir**: 손대지 않고 rc 0(master: `❌ Legacy skill cleanup`, rc 1).
- **.DS_Store + `scripts/__pycache__/*.pyc`**: 남고 Kept 2(편차 7).
- **빈 사용자 디렉터리**: 제거됨(과제의 "dirs only when empty"에는 맞지만 X-5 참고).
- `uninstall --dry-run`: 트리가 바뀌지 않고, `Would keep N`이 실제 실행 결과와 같다.
- install/`--force`/update 두 번째 실행: 트리 불변, `pre-removal`/`Kept` 줄 없음.

## 발견 사항

### X-1 — CRLF 정규화를 고정하는 테스트가 없음
- **Severity** Low(테스트 공백) · **Confidence** 높음(돌려서 확인)
- **위치** `src/superclaude/cli/install_paths.py:534`, `:502-503`(`_shipped_digest`)
- **근거**: scratch clone에서 두 곳의 `.replace(b"\r\n", b"\n")`를 모두 지워도 **전체 suite가 4364 passed**다. 한 곳만 지우면 다른 곳이 정규화를 맡아 결과가 같다. Windows에서 `core.autocrlf=true` 개발 트리로 설치한 사본은 CRLF다. 정규화가 회귀하면 SKILL.md가 매칭되지 않아 retired 디렉터리가 통째로 남는다(SKILL.md 쪽은 master부터 있던 공백이다). 동작 자체는 맞다: matrix의 CRLF case와 old-release의 CRLF 변형 전부 OK.
- **수정**: `tests/unit/test_install_upgrade_scenarios.py:1265` `W1_CASES`에 case를 하나 추가하고, `_plant_w1_skill`에서 `case.get("crlf")`일 때 `text.replace("\n", "\r\n")`로 쓴다(`newline=""`라 CRLF가 그대로 보존된다).
  ```python
  "shipped-only-crlf": {"add": {}, "edit": {}, "kept": set(), "ours": True, "crlf": True},
  ```

### X-2 — "경로까지 일치" 규칙을 고정하는 테스트가 없음
- **Severity** Low(테스트 공백) · **Confidence** 높음
- **위치** `src/superclaude/cli/install_paths.py:451`
- **근거**: `if rel in shipped and _is_shipped_skill_file(path, shipped[rel], forms)`를, 경로를 무시하고 그 skill의 모든 digest와 비교하도록 바꿔도 관련 테스트 347개가 모두 통과한다. 이 mutation이 들어가면 사용자가 skill 안에 둔 shipped 파일 사본(`backup/SKILL.md`)이 지워진다. 현재 코드는 이 사본을 남긴다(matrix에서 확인).
- **수정**: `W1_CASES`에 다음을 추가한다.
  ```python
  "copy-elsewhere": {"add": {"backup/SKILL.md": <shipped SKILL.md>}, "edit": {}, "kept": {"backup/SKILL.md"}, "ours": True},
  ```
  `add` 값은 `_w1_shipped()["SKILL.md"]`가 필요하므로, `_plant_w1_skill`에서 `add`의 값이 `None`이면 같은 이름의 shipped 본문으로 채우는 식으로 구현한다.

### X-3 — 중간 `OSError`에서 앞선 skill의 Kept 안내가 사라지고, 다시 나오지도 않음
- **Severity** Low(데이터 손실 없음, 안내 누락) · **Confidence** 높음(재현함)
- **위치** `src/superclaude/cli/install_components.py:679-687`, `src/superclaude/cli/install_inventory.py:403-412`
- **근거**(sandbox `perm-branch`): `brainstorming`(shipped SKILL.md + `my-notes.md`)과, 읽을 수 없는 하위 디렉터리(`chmod 0`)가 든 `verbalized-sampling`을 함께 두고 install했다. 첫 실행 결과는 `❌ Legacy skill cleanup: [Errno 13] …`, rc 1이다. brainstorming의 SKILL.md는 이미 지워졌고 `my-notes.md`만 남았지만, `notices`는 loop가 끝난 뒤에야 `messages`에 붙으므로 **brainstorming의 Kept 줄은 출력되지 않았다**. 권한을 되돌리고 다시 실행하면 brainstorming은 더 이상 매칭되지 않아(SKILL.md 없음) 끝내 안내되지 않는다.
- **수정**: notice를 loop 안에서 바로 `messages`에 넣는다(두 파일 모두).
  ```python
  for d in stale_skills:
      kept = remove_legacy_skill(d)
      if kept:
          notices.append(...)
  ```
  위 코드를 다음처럼 `try/finally`로 감싼다.
  ```python
  try:
      for d in stale_skills: ...
  finally:
      messages.extend(notices)
  ```
  `🧹 Removed` 줄은 지금처럼 성공했을 때만 낸다. 회귀 테스트로는 `os.chmod(<vs>/locked, 0)` case를 추가하고 POSIX에서만 돌린다.

### X-4 — 생성기가 first-parent만 따라가서 SKILL.md revision 3개가 표에 없음(기존부터 있던 문제, W-1 회귀 아님)
- **Severity** Info/Low · **Confidence** 높음
- **위치** `scripts/gen_shipped_names.py:89-101`(`touching`, `--first-parent`)
- **근거**: `git rev-list HEAD`(전체)의 retired skill blob 중 표에 없는 것은 `c69190a2`/`19d6e329`의 `confidence-check/SKILL.md`와 `0fb95e7f`의 SKILL.md 4개뿐이다. **helper blob은 하나도 빠지지 않았다.** 앞의 둘은 `23a8c32a "Merge branch 'master' of github.com:ajitta/superclaude"`의 2nd parent 쪽, 즉 2026-01-05 16:17–22:33에 공개 origin/master에 있던 상태다. 이 커밋들로 설치하면 디렉터리가 매칭되지 않아 통째로 남는다. master도 같으므로 데이터 손실은 없고, skill이 계속 남아 auto-invoke된다는 것이 영향이다.
- **수정(후속, 이 브랜치 범위 밖)**: `retired_digests`/`retired_skill_files`에 한해 `touching` 대신 `git log --format=@%h <rev> -- <path>`(first-parent 없이)를 쓰거나, pull-merge의 2nd parent를 포함한다. 그 뒤 재생성한다.

### X-5 — CHANGELOG 문구가 실제 동작보다 넓다
- **Severity** Nit · **Confidence** 높음
- **위치** `CHANGELOG.md:13` "a folder of your own … stay"
- **근거**: 사용자가 만든 **빈** 디렉터리는 제거된다(matrix `empty-user-dir`, `_remove_empty_dirs`).
- **수정**: "a folder of your own" → "a folder of yours with files in it".

## 확인했으나 문제 없음

- **Deviations 1–10** 모두 타당하다. 1: edited/symlinked SKILL.md이면 아무것도 지우지 않음을 확인. 2: SKILL.md를 마지막에 지우는 순서는 mutation으로 `test_w1_skill_md_is_removed_last`가 잡고, 중단 후 재실행으로 완료됨을 확인(X-3 sandbox). 3: symlink dir은 손대지 않고 rc 0(master는 rc 1), mutation 6 red. 4: fixture 충실(검사 5). 5: 단일 출처와 재생성 일치. 6: placeholder 되돌리기는 무해하고 raw 본문도 비교함. 이를 빼는 mutation은 9 red. 7: DS_Store/pycache 보존 확인. 소유자가 판단할 사안이지 결함은 아니다. 8: local scope에서 남은 파일이 `git status`에 `?? .claude/skills/verbalized-sampling/my-notes.md`로 보임을 확인. 삭제보다는 낫다. 9, 10 확인.
- 다른 rmtree 경로(`install_component` 디렉터리 component, `find_unshipped`, uninstall의 shared dir)는 retired skill 이름에 닿지 않는다(`skills`는 `SHARED_TARGET_COMPONENTS`).
- `_entries`/`_remove_empty_dirs`/`_is_shipped_skill_file`은 symlink를 따라가지 않는다(outside 트리는 모든 case에서 불변). broken link는 보존된다.
- 읽을 수 없는 하위 디렉터리: `legacy_skill_files`가 삭제 전에 전체 목록을 만들므로 그 skill에서는 아무것도 지워지지 않고, 권한을 되돌리면 다음 실행이 마무리한다.
- project scope 옛 설치(cd2f8aab–e064b436 등 19 revision)에서 non-force `install`이 rc 1로 거절하는 것은 master에도 있는 agent `memory: user` 가드 때문이다(같은 출력). 안내대로 `update --scope project`를 실행하면 모두 완전 제거되고, 두 번째 실행은 조용하다.
- `test_w1_retired_skill_files_module_is_generated_from_the_fixture`가 표, fixture, `retired_skill_digests`의 일치를 고정한다.
- CHANGELOG `[Unreleased]` `### Fixed`는 X-5를 빼면 사실과 맞는다.
- **4.30.1 패치 릴리스가 적절하다**: 버그 수정이고 CLI 표면은 안내 줄 추가뿐이다. `core/`·`hooks.json` 변경이 없어 `CANARY_OK` 없이 `make release`가 통과한다. 권장 순서: X-1~X-3 반영 → 머지 → 4.30.1.

## 검증하지 못한 것

- Windows: junction 감지(`os.path.isjunction`은 Python ≥3.12에서만 있음. 3.10/3.11에서는 skill dir 안의 junction을 일반 dir로 보고 들어간다. 그래도 지우는 것은 경로와 본문이 shipped와 같은 파일뿐이다), 백슬래시 경로가 든 Kept 줄, cp949 콘솔. macOS의 실제 `.DS_Store` 생성.
- PyPI/wheel로 배포된 옛 릴리스: `git archive` 소스로 옛 설치기를 실행했다. wheel 내용이 git 트리와 다를 가능성은 확인하지 않았다.
- `c733413d`(최초 CLI)의 project/local: 그때는 scope를 지원하지 않았다.
- 옛 설치기 실행에는 현재 venv(Python 3.13)를 썼다. 당시 Python과 의존성 버전은 재현하지 않았다.
