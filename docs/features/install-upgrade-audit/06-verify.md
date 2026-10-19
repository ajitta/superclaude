PASS WITH FIXES — S1/S2 수정 19건은 모두 master에서 재현되고 브랜치에서 해소되며 회귀 테스트도 각 수정을 지킨다. 다만 새 retired-agent 삭제 규칙이 사용자 자신의 `pm-agent.md`·`deep-research-agent.md`·`skills/using-superclaude/`를 내용과 무관하게 지운다(V-1, 새 데이터 손실). merge 전에 V-1을 고쳐야 한다.

# P7 독립 검증 — `fix/install-upgrade-audit` @ 1c8b6f19

검증자: P7. 빌더 보고서는 주장으로만 다뤘다. 실행은 모두 `$REVIEW_DIR/sandbox/` 안에서 했다(HOME, CLAUDE_CONFIG_DIR, UV_CACHE_DIR, PATH 모두 sandbox, stub `claude` 사용, real-HOME guard는 매 배치 전후 `GUARD: clean`). 추적 파일은 수정하지 않았다(`git status` 깨끗함). `make sync-*`, `uv sync`, `claude -p`는 쓰지 않았다.

## 실행 결과

| 항목 | 결과 |
|---|---|
| `uv run pytest` (전체) | exit 0: **4214 passed, 3 skipped** (68s) |
| `uv run ruff format --check src tests` | 238 files already formatted |
| `uv run ruff check src tests` | All checks passed |
| `make typecheck` | Success: no issues found in 53 source files |
| `make help` | rc 0 |
| `git diff --stat master...HEAD -- src/superclaude/core src/superclaude/hooks` | 비어 있음 → canary 불필요 |
| 변경된 `.py` 파일의 `\x08` 바이트 | 모두 0 (p5-g3의 inline-python 편집 포함) |
| `scripts/gen_shipped_names.py` 재실행 (scratch clone) | `shipped_names_history.json`이 `generated_from` 줄을 빼고 바이트 단위로 동일 |
| 브랜치의 `test_install_upgrade_scenarios.py`를 **master 소스**에서 실행 | 97 failed / 46 passed. 통과한 46건은 fixture·era 빌드·history 가드와, 빌더가 "pass while red"로 밝힌 케이스(C-03 2건, C-05 8 era, C-08 guard 2건, C-09 force 2건, C-12 guard, C-15 기본값)뿐이다. 실패는 실제 assertion이다(UnicodeDecodeError, 잘못된 출력, `docssee`). 예외는 `KeyError: 'advisories'` 4건으로, master에 advisory tier가 없어서 생긴다 |
| 수정 hunk 단위 되돌리기 18건 (scratch-b) | **18/18 모두 해당 테스트가 red가 됨** (아래 표) |
| sandbox CLI 재현 (master 대 branch) | C-04, C-05, C-06, C-07, C-13, C-14, C-15, C-08/C-09(일부), C-12(일부): master에서 결함 재현, branch에서 해소 |

### 수정 되돌리기 → red 확인 (`$REVIEW_DIR/sandbox/mutate.py`)

| 되돌린 hunk | 결과 |
|---|---|
| `uninstall_all`의 preflight (C-01/02/03) | 20 failed |
| `install_all`의 preflight (C-03) | 11 failed |
| `SC_IMPORT_RE` → 옛 비앵커 regex (C-07) | 2 failed |
| `_runs_registry_command` 검사 (C-13) | 3 failed |
| `uninstall_all`의 `claude_cli_missing` (C-14) | 1 failed |
| `update`의 `has_install` 거부 (C-04) | 2 failed |
| verify-drift remediation의 `scope_command` (C-05) | 3 failed |
| `if force: return None` (C-06) | 1 failed |
| `_is_shipped_skill` digest 게이트 (C-08) | 2 failed |
| `_strip_retired_hooks` 호출 (C-09) | 4 failed |
| install drift 안내 / doctor advisories (C-10) | 1 / 4 failed |
| shared-dir EXTRA 필터 (C-11) | 4 failed |
| user `{}` 삭제 / 빈 memory dir 삭제 (C-12) | 1 / 2 failed |
| `CLAUDE_CONFIG_DIR` 경고 (C-15) | 1 failed |
| `_holds_local_block` 보고 (C-18) | 1 failed |
| exclude preflight (C-19) | 1 failed |

## 발견 사항

### V-1 — High (확신도 높음): retired agent와 `using-superclaude`가 이름만으로 삭제되어 사용자 소유 파일이 사라진다

- **위치**
  - `src/superclaude/cli/install_paths.py:379` (`RETIRED_AGENT_FILES`에 `deep-research-agent.md`, `pm-agent.md` 추가)
  - `install_paths.py:414-421` (`find_retired_agents`: 이름만 비교)
  - `install_paths.py:317`, `:442` (`using-superclaude`는 digest가 없어 `_is_shipped_skill`가 항상 True)
  - 호출 지점: `install_components.py:686-697` (`find_unshipped` → `unlink`), `install_inventory.py:405-414`
- **근거** (`sandbox/a1.sh`, `sandbox/pa.sh`)
  - 사용자 소유 `~/.claude/agents/pm-agent.md`("my own project-manager agent")와 `deep-research-agent.md`, `skills/using-superclaude/SKILL.md`("MY NOTES ABOUT SC")를 두고 **non-force** `install --scope user`를 실행했다. master는 셋 다 유지했다. branch는 `🧹 Removed 2 file(s) this release no longer ships` / `Removed 2 skill(s)`을 출력하고 셋 다 삭제했다. 백업은 없다.
  - project scope에서는 팀이 커밋한 `.claude/agents/pm-agent.md`가 지워진다: `git status` → ` D .claude/agents/pm-agent.md`. master에서는 변화가 없다.
  - 대조군: digest로 보호한 `brainstorming/`, `writing-plans/`(사용자 텍스트)와 `my-skill/`, `my-agent.md`는 유지된다.
  - `pm-agent`는 흔한 이름이고, upstream SuperClaude도 같은 이름을 쓴다. 빌더는 obra/superpowers 이름에 대해 바로 이 위험(“S1 data loss by this audit's own scale”)을 이유로 digest 게이트를 넣었는데, agent 두 개와 `using-superclaude`에는 적용하지 않았다.
  - 같은 이름이 `verify_drift.py:46`의 `_RETIRED_FILES`에도 들어 있다. 그래서 위 삭제를 막더라도 사용자 자신의 `pm-agent.md`는 verify-drift에서 영원히 EXTRA, 즉 exit 1이 된다(C-11 재발).
- **수정**
  - `gen_shipped_names.py`에 `retired_agent_digests`를 추가한다. 은퇴한 agent 파일마다 모든 리비전의 LF 정규화 sha256을 모은다.
  - `install_paths.py`에 `RETIRED_AGENT_DIGESTS`를 추가하고, `find_retired_agents`가 `_is_shipped_skill`와 같은 방식으로 내용이 일치할 때만 반환하게 한다.
  - `using-superclaude`(가능하면 기존 5개 skill도)를 `RETIRED_SKILL_DIGESTS`에 넣는다.
  - `verify_drift`의 EXTRA 판정에도 같은 게이트를 적용한다.
  - 테스트를 추가한다: 이름은 같고 내용이 다른 agent와 skill이 U/P/L × install, `install --force`, `update`, `uninstall`에서 모두 남고, verify-drift가 exit 0인지 확인한다. `test_q10_guarded_skill_digests_cover_every_shipped_revision`를 agent까지 확장한다.

### V-2 — Low (확신도 높음): CHANGELOG의 보존 약속이 실제보다 넓다

- **위치**: `CHANGELOG.md:38` — "A skill of the same name that is not superclaude's text stays."
- **근거**: `using-superclaude`와 기존 5개 이름(`finishing-a-development-branch` 등)은 내용과 무관하게 삭제된다(V-1 실험에서 `finishing-a-development-branch`는 master와 branch 모두 삭제). agent에 대해서는 보존 문구가 아예 없다. Upgrade note(`:49`)는 "If you edited … copy it under another name first"라고 SC 파일을 편집한 경우만 다루고, 이름만 같은 사용자 자신의 파일은 다루지 않는다.
- **수정**: V-1을 고치면 문장을 "an agent or skill of the same name whose text superclaude never shipped stays"로 바꾼다. V-1을 고치지 않을 거라면 그 문장을 열 개의 process skill로 한정하고, upgrade note에 "같은 이름의 사용자 파일도 삭제된다"고 명시한다.

### V-3 — Low (확신도 높음, 회귀 아님): `update --scope local`이 커밋되지 않은 project install 위에 local install을 만든다

- **위치**: `src/superclaude/cli/main.py:440` (`if not has_install(base_path):`). `has_install`은 scope를 보지 않는다(`install_paths.py:199-207`).
- **근거** (`sandbox/a4.sh` S3): project install을 커밋하지 않은 상태에서 `update --scope local`을 실행하면 rc 0이다. 결과는 `Hooks merged to …/settings.local.json`, `CLAUDE.local.md created`, `agent-memory-local/` 생성이다. 즉 Q4의 "update … creates nothing"과 달리 다른 scope를 만든다. master도 같으므로 회귀는 아니다. 커밋된 project에서는 memory 가드가 막는다(S3b).
- **수정**: project/local scope에서는 `detect_scope(base_path.parent) != scope`일 때도 같은 메시지로 거부한다(`found_installs_lines`가 실제 scope를 안내한다). 테스트: project install(미커밋) → `update --scope local` → exit 1, `settings.local.json`과 `CLAUDE.local.md`가 생기지 않음.

### V-4 — Low (확신도 중간): 0바이트이거나 공백뿐인 `settings.json`이 거부된다

- **위치**: `install_settings.py:178-193` (`_unwritable_settings`)
- **근거** (`sandbox/a3.sh` zero/ws × U/P/L): branch는 install, doctor, uninstall 모두 exit 1이고 `is not valid JSON (Expecting value…)`를 출력한다. master도 install이 실패했으나 내용을 먼저 쓴 뒤 실패해 부분 설치가 남았다. 따라서 branch가 엄격히 낫다. 다만 `touch settings.json`은 흔하고 데이터가 없으므로 거부할 이유가 약하다.
- **수정(선택)**: `data.strip() == b""`이면 `{}`로 간주한다. 거부를 유지하겠다면 그대로 두어도 데이터 손실은 없다.

### V-5 — Low (확신도 높음): 사용자에게 보이는 동작 변경 하나가 CHANGELOG에 없다

- **위치**: `src/superclaude/cli/doctor.py:225-250`
- **근거**: legacy 등록의 script copy가 사라진 경우 doctor가 이제 **실패**(exit 1)한다. 이것은 p5-g3의 deviation이다. 그런데 `[Unreleased]` Changed는 "advisories that do not change its exit code"만 말하고, 이 새 실패 조건은 어디에도 없다.
- **수정**: Changed에 다음 bullet을 추가한다. "`doctor` fails when a pre-console-entry hook registration runs a script copy under `superclaude/scripts/` that is gone (it would exit 2 and block prompts); `update --scope <s>` rewrites it."

## 확인했으나 문제 없음

- **데이터 손실 시도 (V-1 외)**
  - user hook이 retired event(`Setup`, `TeammateIdle`)에 있거나 retired와 비슷한 명령(`python3 ~/tools/session_init.py`, `~/bin/skill_activator.py`, 다른 `jq … rm -rf` blocker, `~/insight_writer.py pending-count`)을 써도 install과 uninstall 뒤에 그대로 남았다.
  - digest skill에 사용자 텍스트가 있으면 유지된다.
  - `docs@superclaude/wiki`, `See @superclaude/NOTES.md`, 사용자 `# superclaude` 제목이 있는 CLAUDE.md는 branch에서 바이트 단위로 보존된다(master는 `docsSee`로 훼손).
  - local/project 전체 트리 diff에서 사용자 agent, skill, `agent-memory-local/` 내용, `.git/info/exclude`의 사용자 줄, 팀 `CLAUDE.md`(“# Claude Code Configuration” + 본문), `CLAUDE.local.md`, `.mcp.json`이 보존됐다. 남은 차이는 settings 재직렬화(C-21, S3)뿐이다.
  - MCP: 같은 이름에 명령이 다른 `playwright`는 `⏭️ Kept`로 남고, SC 명령인 `tavily`만 제거된다(master는 둘 다 제거). `claude`가 없으면 아무것도 지우지 않고 exit 1로 끝난다(master는 전부 지운 뒤 traceback).
  - user scope의 heading-only `CLAUDE.md`와 `{}` settings 삭제는 SC import나 hook을 실제로 제거한 경우에만 일어난다(`content == original_content` 조기 반환, `cleaned_any`).
- **Preflight 오거부 (항목 3)**: 다음 입력은 U/P/L에서 install, doctor, uninstall 모두 rc 0이었다. 한국어가 든 UTF-8(BOM 없음), CRLF settings와 CLAUDE, HTML 주석이 있는 CLAUDE.md, `{}`, settings 없음, symlink `~/.claude`, symlink settings와 CLAUDE, dangling symlink settings, git 밖 local, CRLF나 UTF-8 한국어 `info/exclude`. (settings symlink가 일반 파일로 바뀌는 것은 master와 같은 기존 동작이다.)
- **Scope 안전 (항목 4)**
  - local-only 상태에서 `update`를 실행하면 exit 1이고 `~/.claude`가 만들어지지 않는다. 안내는 `update --scope local from <proj>`이다.
  - 하위 디렉터리에서 실행해도 거부되고, 중첩 `.claude`가 생기지 않는다.
  - verify-drift remediation은 `'superclaude install --force --scope local' from <proj>`이다.
  - `install --force`가 새 scope를 만들 때 경고한다.
  - `CLAUDE_CONFIG_DIR` 경고는 install과 doctor에서 나오고, 그 디렉터리에는 쓰지 않는다.
- **C-06 deviation**
  - era project install에서 install은 거부되고 `update --scope project` 안내에 `--scope user`가 없다.
  - `update`는 통과하고 24개 agent를 `memory: project`로 바꾸며 move notice를 출력한다. sandbox HOME은 비어 있는 채로 남는다.
  - `$HOME`에서 실행한 project install(같은 base)은 여전히 거부된다.
  - 소유자의 의도(“advice … update --scope project, which rewrites memory”)와 맞고, advice가 루프에 빠지지 않게 하려면 필요하다. 정당하다.
- **Deviations (항목 5)**
  - g1: exclude BOM 거부는 보수적인 선택이고 소유자 결정 대기다(04a). `.gitignore`를 preflight에서 뺀 것, project scope exclude 검사, 거부된 dry-run의 exit 1, `--keep-settings`, 옛 Tavily 유지(upgrade note 있음)는 모두 정당하다.
  - g2: C-15를 user scope로 한정한 것, C-18을 막지 않고 보고만 하는 것, test contract 변경 2건은 정당하다.
  - g3: process skill digest와 serena digest는 정당하다. E3 형식을 unsupported로 둔 것은 Q14 b와 맞다. gone-script를 실패로 다루는 것은 정당하나 문서가 없다(V-5). agent를 이름만으로 처리한 것은 결함이다(V-1).
  - p6: `test.yml` job과 `.ps1` 추가는 정당하다.
- **CHANGELOG (항목 6)**: V-2와 V-5를 빼면 Changed, Fixed, Upgrade notes의 각 주장이 diff와 sandbox 결과에 맞다.
  - **버전은 minor (4.30.0)이어야 한다.** 이번 변경은 동작 계약을 바꾸고 사용자 조치를 요구한다. `update`가 성공하던 곳에서 exit 1을 내고, preflight가 거부하고, dry-run exit code가 바뀌고, install이 retired 콘텐츠를 지우고, doctor에 새 실패 검사가 생겼으며, Upgrade notes 6개가 붙는다.
  - repo의 관례도 같다. Changed/Removed와 Upgrade notes가 있는 릴리스는 minor다(4.21.0–4.27.0, `/sc:sc`를 제거한 4.29.0). patch(4.29.x)는 작은 Fixed와 Added다. major로 올린 전례는 없다.
- **Workflow (항목 8)**
  - YAML이 파싱된다.
  - `windows-scenarios`는 `if: github.event_name == 'workflow_dispatch' && inputs.windows`이고 `inputs.windows`는 boolean, 기본값 false다. 따라서 PR에서는 건너뛰고, `make ci`(`gh workflow run Tests --ref master`, 입력 없음)에서도 건너뛴다. 이 job이 green-run 재사용 로직에 주는 영향도 없다.
  - action pin은 기존 job과 같다.
- **기타**: `core/`와 `hooks.json`은 변경되지 않았다. `.ps1`은 USERPROFILE, HOME, CLAUDE_CONFIG_DIR를 sandbox로 돌리고, `Path.home()` 가드를 거치며, real `~\.claude`를 실행 전후로 비교한다(정적 검토).

## 검증하지 못한 것

- **빌더 harness의 전체 matrix (run 1: 21/78, run 2: 89/10)는 다시 돌리지 않았다.** 옛 릴리스 설치는 `uvx --offline`과 실제 uv cache가 필요한데, UV_CACHE_DIR를 sandbox로 두라는 제약 때문에 쓰지 않았다. 대신 master 소스로 시나리오 모듈을 실행했고, hunk 되돌리기와 직접 CLI 재현을 했다.
- C-10, C-11, C-18, C-19의 CLI 재현은 테스트와 hunk 되돌리기로만 확인했다. sandbox 직접 재현은 하지 않았다.
- Windows: dispatch job은 GitHub에서 실행하지 않았다(push 금지). `.ps1`은 실행하지 않았다(`pwsh` 없음). cp949 콘솔과 `cmd /c` MCP 경로도 확인하지 못했다.
- Claude Code가 BOM 붙은 `settings.json`이나 `info/exclude`를 실제로 받아들이는지는 확인하지 못했다. 그래서 Q16의 BOM 거부가 Windows 사용자에게 주는 실제 비용을 평가하지 못했다.
- doctor가 매번 verify-drift를 돌리는 비용을 큰 `skills/` 트리에서 측정하지 않았다.
