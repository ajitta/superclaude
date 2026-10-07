---
status: draft
revised: 2026-10-08
---

# portable-skills 단일 플러그인 Implementation Plan

**Goal:** portable-skills의 두 스킬을 플러그인 하나(`socratic`)와 마켓플레이스 항목 하나로 합치고, 기존 `socratic-brainstorm@ajitta-socratic`, `socratic-elenchus@ajitta-socratic` 설치는 `renames`로 새 플러그인에 자동 이전한다.

**Architecture:** 원본 폴더 `portable-skills/<skill>/`은 지금처럼 일반 Agent Skill로 둔다(Codex, 복사 설치). `package.py`가 manifest 하나와 모든 스킬을 묶어 `plugins/socratic/`(`.claude-plugin/plugin.json` + `skills/<skill>/`)와 `releases/socratic.zip`을 생성한다. `marketplace.json`은 항목 하나와 최상위 `renames` 맵을 가진다. 근거는 [02-research.md](./02-research.md)의 경우 A–D.

**Tech Stack:** Python stdlib(`package.py`), pytest(`tests/unit/test_portable_skills.py`), `claude plugin validate`, Claude Code 2.1.292 격리 설정 probe.

Branch: `feat/portable-skills-single-plugin` (이 계획 문서 커밋이 첫 커밋).

## Decisions (기본값, `/sc:implement` 전에 바꿀 수 있음)

- 플러그인 이름 `socratic`. 슬래시 명령은 `/socratic:socratic-brainstorm`, `/socratic:socratic-elenchus`. 마켓플레이스 이름 `ajitta-socratic`은 그대로 둔다. 바꾸면 모든 설치 id와 `renames` 조회가 깨진다.
- 버전: `plugin.json`이 자기 버전을 갖고 `1.0.0`에서 시작한다. 각 SKILL.md의 `metadata.version`(3.2.1, 1.2.1)은 claude.ai·Codex 복사 사용자와 이력을 위해 유지한다. 스킬 내용을 바꾸면 그 스킬 버전과 플러그인 버전을 함께 올린다. Claude Code는 플러그인 버전이 바뀔 때만 업데이트한다.
- manifest 파일은 `portable-skills/plugin-manifest.json` 하나로 하고 `plugin-manifests/`는 지운다.
- `renames`: `{"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}`. append-only로 영구 유지하고 테스트로 고정한다. 지우는 플러그인이 없으므로 `forceRemoveDeletedPlugins`는 쓰지 않는다.
- 이전 zip 두 개는 claude.ai 업로드 확인(Task 5)이 통과한 뒤에 지운다.

## Scope

In: `package.py`, `test_portable_skills.py`, manifest, 생성물(`plugins/`, `releases/`), `.claude-plugin/marketplace.json`, `portable-skills/README.md`, `docs/index.html`의 `#plugins` 섹션, 이 기능 폴더의 README.

Out: SKILL.md 본문과 스킬 버전(동작 변경 없음), Codex 사이드카 `agents/openai.yaml`, 과거 기록(`docs/features/socratic-brainstorm-skill/`, CHANGELOG의 지난 항목, `.claude/insights.jsonl`). 새 CHANGELOG 줄은 다음 버전 bump 때 넣는다(Handoff). `test_version_consistency`가 Unreleased 제목을 거부한다.

## Tasks

### Task 1: 단일 플러그인 생성
**Files:** Create: `portable-skills/plugin-manifest.json` | Modify: `portable-skills/package.py`, `tests/unit/test_portable_skills.py` | Delete: `portable-skills/plugin-manifests/`, `portable-skills/plugins/socratic-brainstorm/`, `portable-skills/plugins/socratic-elenchus/` | Generate: `portable-skills/plugins/socratic/`, `portable-skills/releases/socratic.zip`
- [ ] Step 1: 테스트를 새 구조로 바꾼다. 스킬별 검사(validator, frontmatter, Codex 이름, 원본 폴더의 `skills/`·`bin/`·`.claude-plugin/` 금지)는 그대로 둔다.
  - manifest: 새 `validate_manifest()`가 파일 없음, 잘못된 JSON, `name`·`version`·`description` 누락, `skills` 키를 오류로 낸다. `test_validator_rejects_missing_manifest`와 `test_validator_reads_version_not_a_lookalike_key`를 이 함수 기준으로 다시 쓴다. lookalike 테스트는 `spec-version`만 있는 SKILL.md가 `metadata.version missing`을 내는지 본다.
  - zip: `releases/socratic.zip`이 모든 스킬로 다시 빌드한 결과와 바이트 단위로 같다(OS 독립 테스트 포함). 최상위 폴더는 `socratic/` 하나다. `socratic/.claude-plugin/plugin.json`의 `name`은 manifest와 같다. 스킬마다 `socratic/skills/<skill>/SKILL.md`가 있다. `socratic/SKILL.md`는 없어야 한다(있으면 단일 스킬로 로드된다). `socratic/bin/`도 없어야 한다.
  - 플러그인 폴더: `plugins/socratic/`이 `plugin_files()`와 같고, `plugins/` 아래에는 `socratic/`만 있다.
- [ ] Step 2: `uv run pytest tests/unit/test_portable_skills.py -q` → 새 테스트가 red인지 확인
- [ ] Step 3: 구현
  - `package.py`: `MANIFEST = ROOT / "plugin-manifest.json"`. `validate()`에서 `_validate_manifest` 호출을 빼고 `validate_manifest()`를 따로 둔다. `plugin_files(skills)`는 `.claude-plugin/plugin.json`과 `skills/<skill>/<rel>`을 반환한다. `write_plugin_dir(skills)`와 `package(skills)`는 스킬 목록을 받고, zip 최상위 폴더는 manifest `name`으로 한다. `main()`은 플러그인 하나를 빌드한다. 모듈 docstring의 레이아웃 그림과 `FORBIDDEN_DIRS` 주석도 새 구조에 맞춘다.
  - `plugin-manifest.json`: `name: socratic`, `displayName: Socratic`, `version: 1.0.0`, 두 스킬을 한 문장으로 설명하는 `description`, 기존과 같은 `author`·`license`·`homepage`.
  - `git rm -r` 대상: `plugin-manifests`, 이전 `plugins/` 폴더 두 개. 그다음 `uv run python portable-skills/package.py`. 이전 zip은 더 이상 생성되지 않지만 Task 5까지 남겨 둔다.
- [ ] Step 4: Task 1 테스트 green, `claude plugin validate portable-skills/plugins/socratic` → `✔ Validation passed`, `make format && make lint`. 마켓플레이스 테스트는 Task 2 전까지 red가 정상이다.
- [ ] Step 5: 커밋하지 않고 Task 2로 넘어간다.

### Task 2: 마켓플레이스 항목 하나와 renames
**Files:** Modify: `.claude-plugin/marketplace.json`, `tests/unit/test_portable_skills.py`
- [ ] Step 1: `test_marketplace_lists_every_portable_skill`를 둘로 나눈다.
  - 항목은 정확히 하나다. `name`은 manifest `name`과 같고, `source`는 `./portable-skills/plugins/socratic`이며, `version` 키는 없다.
  - `renames`는 `{"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}`를 포함한다. 모든 값은 현재 항목 이름이거나 `null`이고, 현재 항목 이름과 같은 키는 없다. docstring에 02-research 경우 A를 근거로 적는다.
- [ ] Step 2: red 확인
- [ ] Step 3: `marketplace.json`에 `socratic` 항목 하나(`description`, `category: productivity`)와 `renames`를 넣는다. 마켓플레이스 `description`은 "두 스킬을 담은 플러그인 하나"로 고친다.
- [ ] Step 4: `claude plugin validate .` → `✔ Validation passed`, 전체 `uv run pytest` exit 0, `make lint`
- [ ] Step 5: 커밋 `feat(portable-skills): ship both skills as one socratic plugin`

### Task 3: 실제 저장소로 이전 경로 probe
**Files:** 없음 (scratchpad만 사용, 결과는 Proof에 기록)
- [ ] Step 1: 02-research의 경우 B를 이 저장소로 반복한다. 격리된 `CLAUDE_CONFIG_DIR`을 쓰고, scratchpad의 bare clone에서 `main`을 master 커밋으로 둔다. `http://127.0.0.1:8765/<repo>.git`으로 등록하고 `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.file:///<scratch>/.insteadOf GIT_CONFIG_VALUE_0=http://127.0.0.1:8765/`로 연결한다.
- [ ] Step 2: `socratic-brainstorm@ajitta-socratic`, `socratic-elenchus@ajitta-socratic`을 설치한다. `git update-ref refs/heads/main <branch HEAD>`로 브랜치 HEAD로 옮긴다(hook이 `push -f`를 막는다). 이어서 `claude plugin marketplace update ajitta-socratic`, 그리고 `claude -p "say ok"`를 한 번 실행한다(로그인 확인 전에 설치가 일어난다).
- [ ] Step 3: `claude plugin list`에 `socratic@ajitta-socratic ✔ enabled`만 있고, `claude plugin details socratic@ajitta-socratic`가 `Skills (2)  socratic-brainstorm, socratic-elenchus`를 보이는지 확인한다. 다르면 멈추고 Deviations에 기록한다.

### Task 4: 문서
**Files:** Modify: `portable-skills/README.md`, `docs/index.html` (`#plugins` 섹션), `docs/features/portable-skills-single-plugin/README.md`
- [ ] Step 1: `portable-skills/README.md`
  - 표의 Upload zip 열 대신 표 아래에 "두 스킬은 플러그인 `socratic` 하나로 배포된다"와 `releases/socratic.zip` 링크를 둔다.
  - Layout: `plugin-manifest.json`, `plugins/socratic/skills/<skill>/`, `releases/socratic.zip`. "SKILL.md at its root … single skill" 문장은 "생성된 플러그인은 스킬마다 `skills/<skill>/`에 두고 원본 폴더는 일반 스킬로 남긴다"로 바꾼다.
  - Install: claude.ai 업로드는 `socratic.zip`, 마켓플레이스는 `/plugin install socratic@ajitta-socratic`. 복사 설치 행은 스킬별 그대로.
  - Invoke: 플러그인 행을 `/socratic:<skill>`로.
  - 새 절 "Moving from the two plugins": Claude Code는 `/plugin marketplace update ajitta-socratic`을 실행하면 다음 세션에서 `socratic`으로 넘어간다. `/plugin`이 `Plugin "socratic-brainstorm" not found in marketplace`를 보이면(renames를 모르는 이전 버전) 두 플러그인을 `/plugin uninstall`한 뒤 `/plugin install socratic@ajitta-socratic`. claude.ai 업로드 사용자는 Customize › Plugins에서 이전 두 개를 지우고 `socratic.zip`을 올린다. 지우지 않으면 같은 스킬이 두 번 로드된다.
  - Validate and package 절: 스킬을 고치면 그 스킬의 `metadata.version`과 `plugin-manifest.json`의 `version`을 함께 올린다.
- [ ] Step 2: `docs/index.html`: 제목을 단수로, 소개를 "두 스킬을 담은 플러그인 하나"로. 설치 단계는 `/plugin install socratic@ajitta-socratic` 한 줄. 사용 예는 `/socratic:socratic-brainstorm`, `/socratic:socratic-elenchus`. "이전 두 플러그인을 쓰고 있었다면 `/plugin marketplace update ajitta-socratic`" 힌트 한 줄을 추가한다.
- [ ] Step 3: 기능 README: `phase: implementing`, `updated`, Documents 항목.
- [ ] Step 4: 전체 `uv run pytest` exit 0 (Markdown 구조 테스트 포함)
- [ ] Step 5: 커밋 `docs(portable-skills): install and migrate the single socratic plugin`

### Task 5: claude.ai 업로드 확인, 이전 zip 제거
**Files:** Delete: `portable-skills/releases/socratic-brainstorm.zip`, `portable-skills/releases/socratic-elenchus.zip` | Modify: `tests/unit/test_portable_skills.py`
- [ ] Step 1 (사용자): claude.ai › Customize › Plugins에서 기존 업로드 두 개를 지우고, Add › Upload plugin으로 `portable-skills/releases/socratic.zip`을 올린다. 두 스킬이 모두 보이는지, "소크라테스 대화법으로 따져줘: 사내 점심 메뉴 추천 앱"이 elenchus로 "…이란 무엇인가요?"로 시작하는지 확인한다. 업로드가 거부되면 멈춘다. 이전 zip은 남기고 Deviations에 기록한 뒤, 머지 전에 claude.ai 경로를 다시 계획한다.
- [ ] Step 2: `test_releases_hold_only_the_plugin_zip`(`releases/`에는 `socratic.zip`만) 추가 → red
- [ ] Step 3: `git rm` 이전 zip 두 개 → green, 전체 `uv run pytest` exit 0
- [ ] Step 4: 커밋 `chore(portable-skills): drop the per-skill release zips`

### Task 6: 마무리
- [ ] Step 1: `uv run python portable-skills/package.py --check`, 전체 `uv run pytest`, `make lint`를 다시 실행하고 Proof에 출력을 기록한다.
- [ ] Step 2: 이 계획의 체크박스와 Deviations를 코드와 맞추고 `status: complete`.
- [ ] Step 3: 머지 전에 Handoff의 GitHub 경로 확인용 격리 설정을 만들고 이전 두 플러그인을 설치해 둔다. master 머지와 push는 사용자 요청이 있을 때만 한다.

## Risks

- 가장 위험한 단계는 Task 2를 master에 머지하는 순간이다. 사용자가 이전되면 그들의 `enabledPlugins`에는 `socratic@ajitta-socratic`만 남는다. 그 뒤 마켓플레이스를 되돌리면 같은 사용자가 경우 A로 다시 깨진다. 그래서 롤백은 앞으로 고치는 것뿐이고, `socratic` 항목과 `renames`는 지우지 않는다. Task 3을 머지 전에 두는 이유다.
- `renames`를 모르는 Claude Code 버전에서는 마켓플레이스를 업데이트하면 경우 A가 된다. 최소 버전은 문서에 없다. 완화책은 Task 4의 수동 이전 안내다.
- claude.ai가 두 스킬 zip을 받는지는 확인되지 않았다. Task 5를 머지 전 게이트로 둔다.
- claude.ai Add marketplace 경로에서 `renames`가 적용되는지는 머지 뒤에야 확인할 수 있다. 적용되지 않으면 그 경로의 사용자는 이전 플러그인이 사라지고 `socratic`을 직접 추가해야 한다. Task 4의 안내가 이 경우도 다룬다.
- 한쪽 스킬만 설치했던 사용자도 두 스킬을 받는다. 의도 기록이 원한 결과다.
- 플러그인 버전을 올렸는지는 테스트가 확인하지 않는다. 스킬 버전을 테스트하지 않는 지금과 같은 수준의 빈틈이다.

## Alternatives not taken

- 이전 두 항목을 유예 기간 동안 함께 두기: "마켓플레이스도 하나의 플러그인"과 충돌하고, 둘 다 설치한 사용자에게 스킬이 두 번 로드된다.
- 이전 이름 하나(`socratic-brainstorm`)를 통합 플러그인으로 재사용: 그 이름의 사용자는 그대로 업데이트되지만 이름이 내용을 잘못 설명하고, elenchus 사용자에게는 결국 `renames`가 필요하다.
- `forceRemoveDeletedPlugins`만 쓰기: 이전 플러그인을 지우기만 하고 새 플러그인을 설치하지 않아 "기존 설치가 깨지면 안 됨"을 어긴다.
- 이전 이름을 `dependencies`로 새 플러그인에 연결하는 shim 플러그인: 마켓플레이스 항목이 셋이 된다.
- `plugins/socratic/skills/`에서 원본 폴더로 symlink: Windows에서는 Developer Mode나 관리자 권한이 필요하고, zip 업로드에는 symlink를 담을 수 없다. 지금의 복사 생성 방식을 유지한다.

## Deviations

(없음)

## Proof

- `uv run pytest tests/unit/test_portable_skills.py -q` → 전부 통과. 전체 `uv run pytest` → exit 0 (통과 수 기록, 기준선 2953 passed, 1 skipped). `make lint` → `All checks passed!`
- `uv run python portable-skills/package.py --check` → 스킬 두 개 `ok`, 오류 없음
- `claude plugin validate portable-skills/plugins/socratic`와 `claude plugin validate .` → `✔ Validation passed`
- Task 3: `claude plugin list` → `socratic@ajitta-socratic ✔ enabled` 하나, `claude plugin details` → `Skills (2)`
- Task 5: claude.ai 업로드에서 두 스킬이 보이고 elenchus 트리거가 동작함 (사용자 확인)

## Handoff

- 다음 버전 bump 커밋에 넣을 CHANGELOG 줄: `### Changed` (두 portable 스킬이 플러그인 `socratic` 하나로 배포되고 슬래시 명령이 `/socratic:<skill>`로 바뀜)와 `### Upgrade notes` (`/plugin marketplace update ajitta-socratic`, claude.ai 업로드 사용자의 교체 절차).
- 실제 GitHub 경로 확인: 머지 전에 격리된 `CLAUDE_CONFIG_DIR`(push 때까지 남는 경로)에서 `claude plugin marketplace add ajitta/superclaude`로 이전 두 플러그인을 설치해 둔다. push 뒤 같은 설정에서 `claude plugin marketplace update ajitta-socratic`, `claude -p` 한 번, `claude plugin list` → `socratic@ajitta-socratic ✔ enabled`. 마켓플레이스를 지웠다가 다시 추가하면 그 플러그인도 함께 제거되므로 그 방법은 쓰지 않는다. 이 기기의 `socratic-brainstorm@synced`(3.2.0), `socratic-elenchus@synced`(1.2.0)는 claude.ai 업로드가 동기화된 사본이라 마켓플레이스 이전과 무관하다. Task 5 Step 1에서 claude.ai 업로드를 교체하면 함께 바뀐다.
