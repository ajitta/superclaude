PASS — V-1~V-5는 모두 닫혔다(재현 스크립트, 전체 이력 digest 대조, CLI 매트릭스로 확인). 새로 찾은 W-1(Low)은 master에도 있는 기존 동작이라 merge를 막지 않는다.

# P7 재검증 (round 2) — `fix/install-upgrade-audit` @ 87dc7ebd

빌더의 `p7-fix-report.md`는 주장으로만 다뤘다. CLI는 모두 `$REVIEW_DIR/r2/sandbox/`에서 실행했다. HOME, CLAUDE_CONFIG_DIR, UV_CACHE_DIR, PATH를 sandbox로 돌렸고 `claude`는 stub이며, HOME이 `/home/ubuntu`로 풀리면 중단하게 했다. real-HOME guard는 r2 시작 시점의 baseline과 비교했고, 매 배치 뒤 `GUARD: clean`이었다. 추적 파일은 바꾸지 않았다(`git status` 깨끗함). `make sync-*`, `uv sync`, `claude -p`는 쓰지 않았다. master 비교에 쓴 `$REVIEW_DIR/src-master`는 `.py` 파일 전부가 `master`와 md5로 같다는 것을 확인했다. 로그는 `r2/logs/`, 스크립트는 `r2/sandbox/`에 있다.

## 실행 결과

| 항목 | 결과 |
|---|---|
| `uv run pytest` (전체, sandbox HOME) | exit 0, **4275 passed, 3 skipped** (70s) |
| `ruff format --check src tests` | 238 files already formatted |
| `ruff check src tests` | All checks passed! |
| `make typecheck` | Success: no issues found in 53 source files |
| `git diff master...HEAD -- src/superclaude/core src/superclaude/hooks` | 0줄. canary 불필요 |
| 변경된 `.py`의 `\x08` 바이트 | 0 |
| `scripts/gen_shipped_names.py` 재생성 (`r2/clone`, 1799 commits, full clone) | `shipped_names_history.json`이 `generated_from` 한 줄만 다르다(`e69b3f1b`→`87dc7ebd`) |
| fixture ↔ `install_paths.py` 표 | `retired_agent_digests` 3개 이름(33/19/32)과 `retired_skill_digests` 16개 이름(130개)이 16-hex prefix 단위로 정확히 같다. fixture `names` 블록의 retired 이름 목록과도 같다 |
| 전체 이력 digest 대조 (`r2/sandbox/digest_check.py`) | 모든 ref(`--all`)와 41개 `v*` tag에서 retired 경로의 blob 222개를 모았다. 표에 있는 214개는 U/P/L × {LF, CRLF, `memory:` rewrite(+CRLF), `{{SKILLS_PATH}}` 상대/절대 resolve(+CRLF)} 조합을 실제 파일로 심어 `find_retired_agents`/`find_legacy_skills`로 판정했고 **미인식 0건**이었다. 표에 없는 8개는 아래 "확인했으나 문제 없음"에 정리했다 |
| V-1 CLI 매트릭스 (`r2/sandbox/v1.sh`) | 24/24 기대대로 (아래 표) |
| 라운드 1 `a1.sh` 재실행 | master: 사용자 `finishing-a-development-branch` 삭제. branch: 아무것도 지우지 않음 |
| 라운드 1 `a3.sh` (preflight) | branch는 28행 모두 install, doctor, uninstall rc 0. `zero`/`ws` × U/P/L 포함 |
| 라운드 1 `a4.sh` + `v3.sh` (V-3) | 아래 V-3 항목 참고 |
| `v5.sh` (V-5) | 아래 V-5 항목 참고 |

### V-1 매트릭스 (`r2/logs/v1.log`)

- **사용자 소유 파일**: `pm-agent.md`(`memory: project` 포함), `deep-research-agent.md`, CRLF `deep-research.md`, `skills/using-superclaude/`(+`notes.txt`), `finishing-a-development-branch`, `confidence-check`, `brainstorming`를 심었다.
  - U/P/L × `install` / `install --force` / `update` / `uninstall -y` 12건 모두 rc 0이고 **7개 파일이 전부 남았다**. `notes.txt`도 남았다.
  - verify-drift는 9건 모두 **exit 0**이다(uninstall 3건은 대상 아님). project scope `git status`에는 retired 이름이 하나도 나오지 않았다.
  - 같은 세 scope에서 `doctor --verbose`는 rc 0이고, 이 이름들을 언급하지 않는다.
- **실제 shipped 사본**: `git show`로 가져왔다.
  - 사용한 리비전: `pm-agent.md@0f5a8cfb`(user/local에서는 `memory:`를 scope로 rewrite), `deep-research-agent.md@cb40ecc3`(CRLF), `deep-research.md@81343a67`, `using-superclaude/SKILL.md@bd683233`(CRLF), `confidence-check/SKILL.md@802e847a`(`{{SKILLS_PATH}}`를 user에서는 절대 경로, project/local에서는 `.claude/skills`로 resolve하고 CRLF), `brainstorming@1777f095`, `finishing-a-development-branch`(삭제 직전 리비전).
  - 12건 모두 명령 전 verify-drift는 exit 1(EXTRA/RETIRED)이고, 명령 후에는 **전부 제거**된다. 이후 verify-drift는 exit 0이다. project scope에서는 커밋된 7개가 ` D`로 보인다(의도된 제거).

## 발견 사항

### W-1 — Low (확신도: 메커니즘 높음, 발생 가능성 낮음, 회귀 아님): shipped `SKILL.md`가 일치하면 retired skill 디렉터리를 통째로 지워, 그 안에 사용자가 추가한 파일도 사라진다

- **위치**
  - `src/superclaude/cli/install_components.py:677` (`shutil.rmtree(d)`)
  - `src/superclaude/cli/install_inventory.py:390`
  - 게이트 `src/superclaude/cli/install_paths.py:497-527`(`_is_shipped_skill`)는 `SKILL.md`만 본다.
- **근거** (`r2/sandbox`, 시나리오 `w1`)
  - user install 위에 `skills/brainstorming/SKILL.md@1777f095`(shipped 원문)와 사용자 `my-notes.md`를 두고 non-force `install --scope user`를 실행했다.
  - 결과는 `🧹 Removed 1 skill(s) from a pre-removal release`이고, 디렉터리 전체가 사라졌다. 백업은 없다.
  - shipped retired skill에는 `SKILL.md` 말고 다른 파일도 있었다. 예: `confidence-check@cf5119f8`의 `__init__.py`, `canary.yaml`, `ship@3fdc2383`의 `references/conventions.md`. 그래서 shipped 파일이 아닌 항목을 보존하려면 파일 목록이 필요하다.
  - master는 이름만 보고 지우므로 이 경우에도 삭제한다. 따라서 이 브랜치가 엄격히 낫고 회귀는 아니다.
  - CHANGELOG `:43` "goes only when its text is one superclaude shipped. One you edited stays"는 이 경우를 다루지 않는다.
- **수정 (merge 후 후속으로 충분)**
  - `gen_shipped_names.py`가 retired skill마다 shipped된 상대 경로 집합을 `retired_skill_files`로 기록하게 한다.
  - `find_legacy_skills`가 디렉터리에 그 집합 밖의 항목이 있으면 그 skill을 제외하게 한다. 또는 shipped 경로만 지우고 빈 디렉터리만 `rmdir`하는 방식도 된다.
  - 테스트: shipped `SKILL.md`와 `my-notes.md`가 있을 때 install/update/uninstall 뒤 `my-notes.md`가 남는지 확인한다.
  - 대안: 코드를 고치지 않는다면 Upgrade note `:43`에 다음을 추가한다. "a retired skill directory whose SKILL.md is superclaude's is removed whole, with any file you added to it."

## 확인했으나 문제 없음

- **V-1 닫힘**
  - `find_retired_agents`(`install_paths.py:468-476`)는 `_is_shipped_agent` 게이트를 거친다. `_is_shipped_skill`는 16개 이름 모두에 적용되고, 이름은 있는데 digest가 없으면 False다(`RETIRED_SKILL_DIGESTS.get(..., ())`).
  - `LEGACY_SKILL_NAMES`와 `RETIRED_AGENT_FILES`는 표에서 파생된다. verify-drift의 EXTRA도 `find_retired_agents`를 쓴다(`verify_drift.py:46`, `:114-115`).
  - `memory:` undo는 실제로는 쓰이지 않는다. rewrite가 도입된 `385baaf2`(2026-04-19)가 agent 은퇴(`4c5f3d84`, 2026-03-18)보다 늦고, local scope(`bd356afa`, 2026-04-19)도 그 뒤에 생겼기 때문이다. 다만 해가 없다.
- **이름만 보는 삭제 사냥** (`git diff master...HEAD -- src`)
  - 새로 추가된 삭제 호출은 `memory_dir.rmdir()`(빈 경우만) 하나다.
  - 입력이 바뀐 기존 삭제 지점도 확인했다.
    - `find_legacy_skills`와 `find_retired_agents`: digest 게이트를 거친다.
    - `find_unshipped`: shared dir를 건너뛴다. `commands/sc`와 `superclaude/*`는 SC 소유다.
    - `settings_file.unlink()`: 비었을 때만이고, user scope는 `cleaned_any`일 때만이다.
    - `claude_md.unlink()`: SC heading만 남았을 때만이다.
    - legacy `.gitignore` 블록 마이그레이션: marker로 게이트된다.
    - MCP 제거: 명령이 같을 때만이다(라운드 1).
    - retired hook 제거: identity 기준이다(라운드 1).
  - `_uninstall_shared_component`(현재 shipped 이름은 이름으로 삭제)와 `--force`의 `rmtree(target_sub)`는 이 diff에서 바뀌지 않은 master 동작이다.
- **표에 없는 blob 8개**: 모두 출시되지 않은 상태다.
  - 6개는 `0fb95e7f`, `c69190a2`(merge된 feature 브랜치 중간 커밋)와 `5463aff4`(`remotes/upstream/v5`)에 있다. 이 리비전이 담긴 `v*` tag의 트리에는 이 blob이 없다.
  - `pm-agent.md` 2개는 upstream 저장소에만 있다(`remotes/upstream/*`, upstream tag `v4.3.0`, 2026-03-22, master 조상 아님). 이 fork의 installer가 쓴 적 없는 텍스트이므로, 남기는 쪽(안전한 방향)이 맞다.
- **V-2**: CHANGELOG `:31`과 `:43`이 V-1 수정 뒤 동작과 맞다. 10개 process skill 수, 5개 옛 skill, `deep-research.md` 포함, verify-drift가 사용자 파일과 편집본을 무시한다는 설명, `:17`의 "both fail the check"(vd-before=1) 모두 맞다. 예외는 W-1 경우 하나다.
- **V-3**: `main.py:442-455`.
  - project install(미커밋) 뒤 `update --scope local`은 rc 1이다. `❌ … is a project install, not local`과 `'superclaude update --scope project' from <proj>`를 출력하고, `settings.local.json`, `CLAUDE.local.md`, `agent-memory-local/`을 만들지 않는다.
  - 반대 방향(local install 뒤 `update --scope project`)도 rc 1이고 `--scope local`을 안내한다. 커밋된 project(S3b)도 rc 1이다.
  - 오거부는 없었다.
    - SC hook을 지운 local install(`settings.local.json` 없음, `CLAUDE.local.md` import만 남음)에서 `update --scope local`은 rc 0이다.
    - local scope는 처음(`bd356afa`)부터 `settings.local.json`에 hook을 썼으므로, `detect_scope`가 옛 local install을 project로 오판할 era는 없다.
    - 빌더의 12 era guard 테스트도 통과한다.
  - 라운드 1의 S1(local-only에서 scope 없는 `update`는 거부되고 `~/.claude`를 만들지 않음)과 하위 디렉터리 거부는 그대로다.
- **V-4**
  - `_unwritable_settings`(`install_settings.py:186`)는 공백만 있으면 None을 돌려주고, 인코딩 검사가 먼저 돈다.
  - doctor는 `_load_settings`로 읽는다.
  - `a3`의 `zero`/`ws` × U/P/L는 모두 0/0/0이다.
  - 라운드 1의 유효 입력 목록(UTF-8 한국어, CRLF, `{}`, settings 없음, symlink `~/.claude`, symlink 파일, dangling, git 밖 local, exclude CRLF와 UTF-8 한국어)도 모두 rc 0이다.
- **V-5**: CHANGELOG `:16`이 사실이다. legacy `python3 <base>/superclaude/scripts/session_init.py` 등록이 있고 사본이 없으면 doctor rc 1이고, `--verbose`는 `Registrations run script copies that are gone (session_init)`과 `run 'superclaude install --scope user'`를 출력한다. 그 명령(non-force)을 실행하면 등록이 다시 쓰여 doctor가 rc 0이 된다.
- **기타**: `06-verify.md`는 커밋에 포함됐다. pytest 수(4275/3)는 빌더 보고와 같다.

## 검증하지 못한 것

- Windows 경로: `str`과 `as_posix` 두 형태의 SKILLS_PATH undo, `\` 구분자, cp949 콘솔은 확인하지 못했다(`pwsh` 없음, push 금지). Linux에서는 `str`과 `as_posix`가 같아 한 형태만 실제로 검증됐다.
- 설치 base가 나중에 옮겨진 경우(절대 경로 불일치)에는 SC 사본이 남는다. 이것은 빌더가 밝힌 안전 방향의 deviation이고 재현하지 않았다.
- 옛 릴리스 installer를 실제로 실행해 설치하는 matrix(`uvx --offline`)는 UV_CACHE_DIR 제약 때문에 돌리지 않았다. 대신 `git show` 원문에 install-time 변환을 재현해 심었다.
- doctor의 verify-drift 비용은 큰 `skills/` 트리에서 측정하지 않았다.
