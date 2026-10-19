PASS WITH FIXES — C-20, C-21, 안내 문구 통일, doctor 비용은 sandbox에서 모두 재현됐고 회귀도 없다. W-2는 제품 결함이 아니라는 결론이 옳지만 그 근거 문장("모든 era가 forward slash")은 틀렸고, 실제 Windows 설치를 지켜 주는 `str` 경로는 어떤 테스트도 고정하지 않는다. 그 밖의 발견은 기존 결함(Medium 1)과 Low뿐이며 머지를 막지 않는다.

# install file fidelity 독립 검증 — `fix/install-file-fidelity` @ 9f1bd89d

## 실행 결과

모든 CLI 실행은 `$TMPDIR/verify-file-fidelity-run/sandbox/<case>/` 안에서 했다. `HOME`/`USERPROFILE`/`CLAUDE_CONFIG_DIR`/`UV_CACHE_DIR`를 sandbox로 두고, `PATH`는 stub `claude`가 든 sandbox `bin` 뒤에 `/usr/bin:/bin`만 붙였다. 각 프로세스 안에서 `realpath(HOME) != /home/ubuntu`이고 `superclaude.__file__`이 검증 대상 트리인지 assert했다. branch는 `git archive HEAD src`, master(28b19c57 = fcc3bd31 + memory 커밋 하나)는 `git archive master src`로 풀어 같은 하네스로 돌렸다(`harness/sb.py`, `c20.py`, `c21.py`, `mutate.py`). 실제 `~/.claude`(SC 관련 파일·디렉터리 해시, `settings.json` md5, `.claude.json`의 `mcpServers`)와 repo의 `.claude/`, `git status`, `~/.config`는 전체 작업 전후 **clean**이었다. 바뀐 것은 Claude Code가 직접 쓰는 `backups/`와 `plugins/`뿐이다.

| # | 검사 | 결과 |
|---|---|---|
| 1 | C-20 matrix: user/project/local × 13 CLAUDE 파일(LF, CRLF, mixed 두 방향, no-final-newline LF/CRLF, 앞뒤 blank run LF/CRLF, 한글·일본어·악센트, 줄 끝 공백·탭, `x\n\n`, `# superclaude notes`, 기존 SC 블록) × `install` → `install` → `install --force` → `update` → `uninstall --dry-run` → `uninstall -y` | branch **38/39 OK**. 남은 1건은 일부러 만든 비현실 case다(CLAUDE.local.md 안의 user-scope import 줄). master도 같은 결과다. 잔여물은 문서에 적힌 하나뿐이다: final newline 없던 파일은 newline 하나가 남는다(6건). 두 번째 install, `--force`, `update`는 파일을 건드리지 않고, dry-run은 트리를 바꾸지 않는다. master는 **25/39 실패**(CRLF→LF, blank run 압축, 앞뒤 strip, 줄 끝 공백 제거) |
| 2 | C-21 layout matrix: user/project/local × 16 layout × mode 0644/0600, 같은 명령 순서 | branch **60/96 byte-identical**, mode는 모든 case에서 유지. 나머지 36건: 문서에 적힌 잔여(compact 한 줄, 중첩 inline) 12건, 문서에 없는 재직렬화(`1e3`→`1000.0`, `\/`→`/`) 6건(Y-6), 사용자의 `{}`/0바이트/공백만 있는 파일을 uninstall이 지움 18건(master와 같은 기존 동작). master는 **0/96** |
| 3 | 읽기 전용 settings: 0444/0400 × fresh/installed × `install`, `install --force`, `update`, `uninstall -y`, `uninstall --dry-run` × 3 scope | branch **60/60** exit 1, 쓰기 0건(sandbox 전체 snapshot 비교). 54건은 파일 이름을 대고 거절했다. 나머지 6건은 fresh `update`로, 파일 이름 대신 "install이 없다"는 이유로 먼저 거절했다(역시 exit 1, 쓰기 0건). master는 60건 모두 실패했고 그중 54건이 exit 0이었다(0444 파일을 교체) |
| 4 | 새 settings 파일(umask 027) | branch mode 0640, 끝 newline 있음. master 0600, newline 없음 |
| 5 | symlink settings.json, 읽기 전용 디렉터리, 읽기 전용·symlink·0600 CLAUDE 파일 | 아래 Y-1, Y-3. CLAUDE 파일의 symlink와 0600 mode는 유지되고, 대상 파일 bytes는 round-trip에서 그대로다 |
| 6 | W-2: 옛 설치기의 placeholder 치환 기록과 Windows 형태 재현 | 결론(제품 결함 아님)은 맞다. 근거 문장은 틀렸다: Y-2 |
| 7 | Windows CI | run 39212220068: headSha 8ded7e99, `workflow_dispatch`, 4 job 모두 success, Windows 380 passed / 4 skipped. 이후 HEAD까지 바뀐 것은 `04a-handoff.md` 한 줄뿐이다 |
| 8 | 회귀 테스트가 잡는가(mutation 19개) | **17/19 red**. 살아남은 둘: m16(fixture `HOME`을 `str(home)`으로 되돌림, Linux에서는 원래 검출 불가, Y-5)과 m17(`_placeholder_forms`에서 `str` form 제거, 어느 플랫폼에서도 검출 안 됨, Y-2) |
| 9 | doctor 비용 | fresh(14 files) best 0.11 s / mean 0.11 s. 42,014 files(사용자 skill 2,000개 × 20 + shipped dir 안 2,000개) best 0.15 s / mean 0.16 s. drift advisory "2000 extra"가 출력됐다. rc 1은 PATH probe 때문이다(빌더 보고와 같음) |
| 10 | `uv run pytest`(HOME=sandbox) | **exit 0, 4458 passed, 3 skipped** |
|    | `ruff format --check src tests` / `ruff check src tests` / `make typecheck` | 239 files already formatted / All checks passed / Success, 54 files |
|    | `git diff master HEAD -- src/superclaude/core src/superclaude/hooks` | 0줄 → canary 불필요 |

### mutation 세부(테스트 파일 5개, 570 tests)

| mutation | 결과 |
|---|---|
| m1 install text-mode 읽기·쓰기 / m2 블록을 항상 LF로 | 3 red / 3 red (`test_c20_install_appends_…`) |
| m3 uninstall을 master의 압축+strip으로 / m4 heading 위 빈 줄을 남김 / m5 빈 줄 run 전체 제거 | 8 / 15 / 5 red |
| m6 `os.chmod` 제거 / m7 새 파일 0600 | 4 / 1 red |
| m8 master layout / m9 trailing newline 무시 / m10 ensure_ascii 고정 / m11 CRLF 무시 / m12 한 줄 → indent | 18 / 6 / 3 / 3 / 3 red |
| m13 읽기 전용 검사 제거 / m14 doctor도 mode 검사 | 12 / 3 red |
| m15 `newline=None` | 1 red (`test_settings_json_writer_pins_newline_and_encoding`) |
| m18 verify-drift 안내 / m19 legacy-scripts 안내를 `install --force`로 | 3 / 1 red |
| m16 fixture `HOME`=`str(home)` / m17 `_placeholder_forms`의 `str` 제거 | **0 red** |

## 발견 사항

### Y-1 — symlink인 settings 파일이 일반 파일로 바뀐다(기존 결함, 이 브랜치의 회귀 아님)
- **Severity** Medium · **Confidence** 높음(branch와 master 모두 재현)
- **위치** `src/superclaude/utils/__init__.py:106`, `:116` (`atomic_write_text`)
- **근거**: `settings.json`을 `$SB/dotfiles/settings.json`(0644)을 가리키는 symlink로 두고 install했다. 세 scope 모두 link가 hooks를 담은 일반 파일로 바뀌었고, 원래 대상 파일은 hooks를 받지 못했다. uninstall 뒤에도 link는 복원되지 않는다(대상 bytes는 그대로). master도 같다. 다만 이 브랜치는 바로 이 함수를 고쳐 쓰고 있고, CHANGELOG는 "keep your `settings.json` … as you had it"이라고 약속한다. dotfiles 관리자(stow, chezmoi)로 settings를 symlink하는 사용자는 저장소 쪽 파일과 실제 설정이 말없이 갈라진다. mode는 `path.stat()`이 link를 따라가므로 대상 파일의 것이 새 일반 파일에 복사된다.
- **수정**: 쓰기 전에 link를 풀어 대상 파일을 교체한다(temp 파일도 대상 디렉터리에 만든다).
  ```python
  path = Path(path)
  if path.is_symlink():
      path = Path(os.path.realpath(path))
  ```
  회귀 테스트로 `test_c21_settings_keep_their_layout_across_install_and_uninstall` 옆에 symlink case를 추가한다(`skipif` Windows 권한 없음). install 뒤 `settings.is_symlink()`이고 대상에 `hooks`가 있으며, uninstall 뒤 대상 bytes가 원본과 같은지 assert한다. 머지 전에 넣지 않는다면 CHANGELOG에 "symlink된 settings 파일은 일반 파일로 바뀐다"를 적는다.

### Y-2 — W-2 근거의 "모든 era가 forward slash"는 사실이 아니고, 실제 Windows 설치를 지키는 `str` 경로는 테스트가 없다
- **Severity** Low(문서 오류 + 테스트 공백, 제품 동작은 맞음) · **Confidence** 높음
- **위치** `docs/features/install-upgrade-audit/03-findings.md:125` ("a mixed form no installer wrote: every era resolved its placeholders to forward slashes on every platform"), `tests/unit/test_install_upgrade_scenarios.py:84` (`fixture_tokens` docstring "(cd2f8aab → b806c61c)"), 같은 파일 `:1275`, `src/superclaude/cli/install_paths.py:521`
- **근거**: `git show cd2f8aab:src/superclaude/cli/install_components.py:33-34`의 `_resolve_template_paths`는 user scope와 local scope에서 `str((base_path / "skills").resolve())`를 썼다. `757e3649`(2026-02-21, "use forward slashes in template paths to prevent YAML parse errors on Windows")가 이를 `.as_posix()`로 바꿨다. 그 사이 8개 커밋(cd2f8aab..e1b2fbe7)으로 Windows에 설치하면 SKILL.md는 `C:\Users\me\.claude\skills/confidence-check/scripts/…`가 된다. 이것도 혼합 형태다. 게다가 `write_text`가 text mode라 CRLF다. 이 구간에는 release tag가 없다(`cd2f8aab`를 담은 첫 tag `v4.20.1`은 `757e3649`도 담는다). 하지만 git master에서 설치한 사용자는 있을 수 있다. 그 형태를 재현해 보았다: 16개 SKILL.md(8 커밋 × confidence-check/simplicity-coach)를 Windows `str` 경로와 CRLF로 렌더링하고 제품의 `_is_shipped_skill_file`에 넣었다. `str` form이 있으면 **16/16 매칭**, 없으면 **0/16**이다. 따라서 "실제 Windows 사용자는 영향 없음"이라는 결론은 맞지만, 그 이유는 `_placeholder_forms`의 `str` 항목이지 "모든 era가 forward slash"가 아니다. 그런데 m17(`for form in (Path.as_posix,)`)은 전체 관련 테스트에서 살아남고, Windows CI에서도 잡히지 않는다. fixture가 as_posix 형태만 쓰고, str 구간 era fixture가 없기 때문이다. hook 명령은 주장대로다: settings.json 병합은 `49286ed4`부터 `.replace("\\", "/")`, `{{PYTHON_BIN}}`은 `77b5821c`부터 같은 방식이다. `702dc25f` 이후의 `hooks/hooks.json` 복사본도 `str` 형태였지만, 현재 install이 그대로 덮어쓰고 uninstall이 지우는 build output이라 영향이 없다.
- **수정**:
  1. 03 W-2 행과 `fixture_tokens` docstring을 바로잡는다. 예: "cd2f8aab → e1b2fbe7 wrote `str(...resolve())` (backslashes on Windows, CRLF), 757e3649 → b806c61c `as_posix()`; `_placeholder_forms` undoes both". `:1275`의 "(cd2f8aab → b806c61c)"도 같은 식으로 고친다.
  2. `test_v1_a_retired_skill_with_a_relative_skills_path_still_goes`(`:1271`)와 같은 모양의 테스트를 추가한다. user/local scope에서 `shipped.replace("$HOME/.claude/skills", str((base / "skills").resolve()))`를 CRLF로 쓰고 uninstall 뒤 디렉터리가 사라지는지 본다. Linux에서는 as_posix와 같은 값이라 중복이지만, `windows-scenarios` job에서 `str` 항목을 고정한다.

### Y-3 — 읽기 전용 CLAUDE 파일은 preflight를 통과하고, 117개를 쓴 뒤 traceback으로 끝난다(기존 결함)
- **Severity** Low(데이터 손실 없음, 부분 설치 + traceback) · **Confidence** 높음(branch와 master 모두 재현)
- **위치** `src/superclaude/cli/install_settings.py:219-237` (`input_problems`), `:850`
- **근거**: CLAUDE.md(user)와 CLAUDE.local.md(local)를 0444로 두고 `install`을 실행했다. 결과는 rc 1이다. commands, agents, settings 등 117(user)/118(local) 항목을 쓴 뒤 `update_claude_md_import`의 `write_bytes`에서 `PermissionError` traceback이 났다. CLAUDE 파일 자체는 그대로다. 이 브랜치는 읽기 전용 settings 파일을 preflight에서 거절하도록 했다. 그리고 `input_problems` docstring("What stops a command from editing this scope's settings and CLAUDE file")과 새 거절 문구("cannot read or write them safely")는 CLAUDE 파일도 대상으로 말한다. 같은 사용자 의도(파일 고정)가 settings에서는 존중되고 CLAUDE 파일에서는 traceback이 된다.
- **수정**: 읽기 전용 검사를 helper로 빼서 두 파일에 쓴다.
  ```python
  def _read_only_problem(path: Path) -> Optional[str]:
      if path.exists() and not os.access(path, os.W_OK):
          mode = stat.S_IMODE(path.stat().st_mode)
          return f"{path} is read-only (mode {mode:04o}); make it writable or move it aside"
      return None
  ```
  `_unwritable_settings`의 `check_mode` 분기와 `input_problems`의 `claude_md` 검사(`_encoding_problem` 다음)에서 이 helper를 부른다. 테스트는 `test_c21_a_read_only_settings_file_is_refused_before_any_write`를 CLAUDE 파일로 parametrize한다.

### Y-4 — hook state 새 파일의 mode가 0600에서 0644(umask)로 바뀌었는데 CHANGELOG에 없다
- **Severity** Low · **Confidence** 높음
- **위치** `src/superclaude/utils/__init__.py:107-110`. 호출처: `scripts/loop_guard.py:70`, `scripts/session_init.py:112`, `hooks/mcp_fallback.py:55`, `utils/__init__.py:641`
- **근거**: umask 022에서 `atomic_write_json`으로 새 파일을 만들면 branch는 0644, master는 0600이다. 기존 0640 파일은 branch에서 0640이 유지되고 master에서는 0600이 된다. settings 쪽에는 의도된 변화이고, 빌더도 "keeps modes for hook-state writers too"라고 적었다. 다만 hook state(PR 캐시의 branch·PR 줄, loop_guard 입력 fingerprint)는 이제 다른 사용자도 읽을 수 있게 만들어진다. CHANGELOG의 Changed 항목은 settings 파일만 말한다. 내용의 민감도는 낮다. 덧붙여 `os.umask(0)` 후 되돌리는 방식은 process 전역이라 멀티스레드에서는 경쟁이 생긴다. hook은 단일 스레드라 지금은 문제가 없다.
- **수정**: 둘 중 하나. (a) CHANGELOG Changed에 "hook state files under `.superclaude_hooks/` are created with the umask mode, not 0600"을 추가한다. (b) `atomic_write_text(path, text, new_mode: int | None = None)`로 새 파일 mode를 받게 하고, hook state 호출처는 0o600을 넘겨 예전 동작을 유지한다.

### Y-5 — "Linux에서 Windows gate를 흉내 내는" 새 테스트 둘은 fixture 수정을 고정하지 않는다
- **Severity** Low(테스트 공백, Windows dispatch가 대신 잡음) · **Confidence** 높음
- **위치** `tests/unit/test_install_upgrade_scenarios.py:212`, `:235-254`
- **근거**: m16(`"HOME": str(home)`로 되돌림)에서 570개 모두 통과한다. `test_fixture_tokens_are_forward_slash_paths`는 `"\\" not in value`만 보는데, Linux에서는 `str(home)`에도 backslash가 없다. `test_fixture_skill_md_passes_the_gate_in_its_windows_form`은 token을 직접 `home.as_posix()`로 만들고 undo도 직접 한다(`:246`). 그래서 `fixture_tokens`도 `_placeholder_forms`도 거치지 않는다. 이 테스트가 확인하는 것은 "forward-slash 형태라면 digest 표에 있다"뿐이다. 03의 "simulate the Windows gate on Linux" 표현은 실제보다 넓다.
- **수정**: 경로 변환을 `_era_path(p: PurePath) -> str: return p.as_posix()`처럼 순수 함수로 빼고 `fixture_tokens`가 그것을 쓰게 한다. 그런 다음 `assert _era_path(PureWindowsPath(r"C:\a\home")) == "C:/a/home"`을 추가하고, windows-form 테스트도 `_era_path(home)`로 token을 만든다. 또는 03의 Regression test 칸 설명을 "digest 표 확인, fixture 수정 자체는 Windows dispatch가 고정"으로 줄인다.

### Y-6 — 문서에 없는 settings 재직렬화 잔여물, CHANGELOG 첫 문장이 실제보다 넓다
- **Severity** Low(Nit) · **Confidence** 높음
- **위치** `CHANGELOG.md:13`, `docs/features/install-upgrade-audit/03-findings.md:91`(C-21 Residuals)
- **근거**: matrix의 `floats-slash` case에서 `1e3`→`1000.0`, `1.50`→`1.5`, `"a\/b"`→`"a/b"`가 되고 uninstall 뒤에도 원래대로 돌아오지 않는다(6/6). raw 비ASCII와 `\u00e9` escape가 섞인 파일은 escape가 raw `é`로 바뀐다. 03은 compact 한 줄과 중첩 inline만 잔여로 적었고, CHANGELOG는 "keep your `settings.json` … as you had it"으로 시작한다.
- **수정**: 03 C-21 Residuals에 "number forms, `\/` and `\uXXXX` escapes in a file that also holds raw non-ASCII are re-serialised"를 추가한다. CHANGELOG 첫 문장 끝에 "; spacing inside a line, number forms and escapes are re-serialised"를 붙인다.

## 확인했으나 문제 없음

- **W-2 결론**: 제품 결함이 아니다. fixture가 만든 `C:\…\home/.claude/skills/…`(home까지 backslash, 이후 slash)는 어느 설치기도 쓰지 않은 형태다. 실제로 있었던 두 형태(`str` 구간의 `C:\…\.claude\skills/…`, 이후의 all-slash)는 모두 `_placeholder_forms`가 되돌린다(Y-2 시뮬레이션). run 39208943288의 실패 7건은 fixture 문제였다. 39212220068의 green은 fixture가 era 형태로 고쳐진 결과다.
- **C-20 세부**: CRLF·mixed 파일의 블록은 다수 줄바꿈으로 붙는다(mixed-crlf-major는 CRLF, mixed-lf-major는 LF). blank run과 앞뒤 공백, 줄 끝 공백·탭, 비ASCII는 byte 단위로 그대로다. 사용자 heading(`# superclaude notes`)은 지우지 않는다. 공백만 있는 줄이 heading 위에 있으면 그 줄은 남는다(`rstrip("\r\n") == ""`만 지움). symlink CLAUDE 파일은 link가 유지되고 대상이 round-trip한다. 0600 mode도 유지된다.
- **C-21 거절은 쓰기 전에 일어난다**: branch 60건 모두 sandbox 전체(`home`, `project`, `.git/info`) snapshot이 바뀌지 않았다. `uninstall --dry-run`도 거절한다(주장대로). `doctor`는 읽기 전용 파일에서 통과한다(m14 red로 확인).
- **새 settings 파일**: umask mode와 끝 newline을 갖는다. uninstall은 install이 만든 파일을 지운다(master와 같음).
- **사용자의 `{}`/0바이트 settings 파일을 uninstall이 지우는 것**: master와 같은 기존 동작이고, 남은 내용이 없으므로 손실도 없다.
- **읽기 전용 디렉터리**(base를 0555로): `install --force`와 `update`는 쓸 것이 없어 rc 0, 변경 0이다. `uninstall -y`는 하위 디렉터리 안의 SC 파일 109개를 지우고 rc 1로 끝난다. settings와 CLAUDE 파일은 바뀌지 않는다. master와 같고, 권한을 되돌리고 다시 실행하면 마무리된다. C-21 주장(읽기 전용 *파일*) 범위 밖이다.
- **안내 문구**: verify-drift와 legacy-scripts notice가 `update --scope <s>`를 말한다(m18/m19 red). 남은 `install --force` 문자열은 docstring, 주석, `install` help 예시뿐이다.
- **`atomic_write_json`의 `newline=""`**: `json.dumps`는 `\n`만 내므로 Windows에서도 LF다. CRLF는 `_settings_text`가 파일에서 읽었을 때만 나온다.
- **CHANGELOG `[Unreleased]`**: Y-4, Y-6을 빼면 사실과 맞는다. core/hooks.json 변경이 없어 `make release`는 `CANARY_OK` 없이 통과한다.
- **권장 순서**: Y-2(문서 정정 + 테스트), Y-6(문구) → 머지. Y-1, Y-3은 같은 브랜치에서 고치면 좋지만, 기존 결함이라 별도 후속으로 해도 된다. Y-4는 (a)나 (b) 중 하나를 고른다.

## 검증하지 못한 것

- Windows 실기: 이번 검증은 Linux(aarch64, Python 3.11)에서 했다. Windows의 `os.access` 읽기 전용 속성, Claude Code가 settings를 잡고 있을 때의 `os.replace`(04a W1), junction으로 된 settings 파일은 확인하지 않았다. Windows 동작은 CI run 39212220068의 결과에 기댄다.
- `str` 구간의 Windows 설치를 실제 옛 설치기로 실행하지는 않았다. 해당 커밋의 SKILL.md를 그 시기 코드와 같은 방식(Windows `str` 경로, text mode CRLF)으로 렌더링해 제품 matcher에 넣었다.
- root 사용자: `os.access`는 root에게 늘 True이므로 root로 실행하면 읽기 전용 거절이 동작하지 않는다(테스트도 root에서는 skip). 확인하지 않았다.
- macOS ACL, 다른 사용자 소유의 settings 파일, hardlink된 settings 파일(`os.replace`가 link를 끊음)은 재현하지 않았다.
