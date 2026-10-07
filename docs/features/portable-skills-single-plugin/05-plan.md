---
status: draft
revised: 2026-10-08
---

# portable-skills 단일 플러그인 Implementation Plan

**Goal:** portable-skills의 두 스킬을 플러그인 하나(`socratic`)와 마켓플레이스 항목 하나로 합치고, 기존 `socratic-brainstorm@ajitta-socratic`, `socratic-elenchus@ajitta-socratic` 설치는 `renames`로 새 플러그인에 자동 이전한다. 설치되는 파일에는 한국어가 없어야 하고, Pages(`docs/index.html`) 설명도 새 구조에 맞춘다.

**Architecture:** 원본 폴더 `portable-skills/<skill>/`은 일반 Agent Skill로 남는다(Codex, 복사 설치). `package.py`가 manifest 하나와 모든 스킬을 묶어 `plugins/socratic/`(`.claude-plugin/plugin.json` + `skills/<skill>/`)와 `releases/socratic.zip`을 생성한다. `marketplace.json`은 항목 하나와 최상위 `renames`를 가진다. 근거는 [02-research.md](./02-research.md)의 경우 A–D.

**Tech Stack:** Python stdlib(`package.py`), pytest(`tests/unit/test_portable_skills.py`), `claude plugin validate`, `claude -p --plugin-dir`(라우팅 probe), Claude Code 2.1.292 격리 설정(이전 probe).

Branch: `feat/portable-skills-single-plugin` (계획 문서 커밋이 첫 커밋).

## Decisions (기본값, `/sc:implement` 전에 바꿀 수 있음)

- 플러그인 이름 `socratic`. 슬래시 명령은 `/socratic:socratic-brainstorm`, `/socratic:socratic-elenchus`. 마켓플레이스 이름 `ajitta-socratic`은 그대로 둔다. 바꾸면 모든 설치 id와 `renames` 조회가 깨진다.
- 버전: `plugin.json`은 `1.0.0`에서 시작한다. 각 SKILL.md의 `metadata.version`은 유지하고, 한국어 제거로 description의 트리거 문구가 바뀌므로 minor를 올린다(brainstorm 3.3.0, elenchus 1.3.0). 이후 스킬을 고칠 때는 스킬 버전과 플러그인 버전을 함께 올린다. Claude Code는 플러그인 버전이 바뀔 때만 업데이트한다.
- 한국어 없음: 설치되는 파일(`plugins/socratic/` 전체와 `releases/socratic.zip`)에 한글이 한 글자도 없어야 하며 테스트로 고정한다. 플러그인은 원본 폴더의 복사본이라 원본 SKILL.md와 references도 영어로 바꾼다. Codex와 복사 설치 사용자도 같은 파일을 받는다. 응답 언어는 기존 규칙 7("Reply in the user's language")이 맡는다. 설치되지 않는 `portable-skills/README.md`와 `docs/`의 한국어 호출 예시는 그대로 둔다.
- manifest는 `portable-skills/plugin-manifest.json` 하나로 하고 `plugin-manifests/`는 지운다.
- `renames`: `{"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}`. append-only로 영구 유지하고 테스트로 고정한다. 지우는 플러그인이 없으므로 `forceRemoveDeletedPlugins`는 쓰지 않는다.
- 이전 zip 두 개는 claude.ai 업로드 확인(Task 8)이 통과한 뒤에 지운다.

## Scope

In: `package.py`, `test_portable_skills.py`, manifest, 생성물(`plugins/`, `releases/`), `.claude-plugin/marketplace.json`, 두 스킬의 SKILL.md와 references(한국어 제거와 버전만, 동작 변경 없음), `portable-skills/README.md`, `docs/index.html`의 nav와 `#plugins` 섹션, 이 기능 폴더 README.

Out: Codex 사이드카 `agents/openai.yaml`(한글 없음), 과거 기록(`docs/features/socratic-brainstorm-skill/`, CHANGELOG 지난 항목, `.claude/insights.jsonl`). 새 CHANGELOG 줄은 다음 버전 bump 때 넣는다(Handoff). `test_version_consistency`가 Unreleased 제목을 거부한다.

## Tasks

### Task 1: 단일 플러그인 생성
**Files:** Create: `portable-skills/plugin-manifest.json` | Modify: `portable-skills/package.py`, `tests/unit/test_portable_skills.py` | Delete: `portable-skills/plugin-manifests/`, `portable-skills/plugins/socratic-brainstorm/`, `portable-skills/plugins/socratic-elenchus/` | Generate: `portable-skills/plugins/socratic/`, `portable-skills/releases/socratic.zip`
- [x] Step 1: 테스트를 새 구조로 바꾼다. 스킬별 검사(validator, frontmatter, Codex 이름, 원본 폴더의 `skills/`·`bin/`·`.claude-plugin/` 금지)는 그대로 둔다.
  - manifest: 새 `validate_manifest()`는 파일 없음, 잘못된 JSON, `name`·`version`·`description` 누락, `skills` 키를 오류로 낸다. `test_validator_rejects_missing_manifest`는 이 함수 기준으로 다시 쓴다. `test_validator_reads_version_not_a_lookalike_key`는 `spec-version`만 있는 SKILL.md가 `metadata.version missing`을 내는지 본다.
  - zip: `releases/socratic.zip`이 모든 스킬로 다시 빌드한 결과와 바이트 단위로 같다(OS 독립 테스트 포함). 최상위 폴더는 `socratic/` 하나다. `.claude-plugin/plugin.json`의 `name`은 manifest와 같고, 스킬마다 `socratic/skills/<skill>/SKILL.md`가 있다. `socratic/SKILL.md`(있으면 단일 스킬로 로드된다)와 `socratic/bin/`은 없다.
  - 플러그인 폴더: `plugins/socratic/`이 `plugin_files()`와 같고 `plugins/` 아래에는 `socratic/`만 있다.
- [x] Step 2: `uv run pytest tests/unit/test_portable_skills.py -q` → 새 테스트 red 확인
- [x] Step 3: 구현
  - `package.py`: `MANIFEST = ROOT / "plugin-manifest.json"`. `validate()`에서 `_validate_manifest` 호출을 빼고 `validate_manifest()`를 둔다. `plugin_files(skills)`는 `.claude-plugin/plugin.json`과 `skills/<skill>/<rel>`을 반환한다. `write_plugin_dir(skills)`와 `package(skills)`는 스킬 목록을 받고, zip 최상위 폴더는 manifest `name`이다. `main()`은 플러그인 하나를 빌드한다. 모듈 docstring의 레이아웃 그림과 `FORBIDDEN_DIRS` 주석도 맞춘다.
  - `plugin-manifest.json`: `name: socratic`, `displayName: Socratic`, `version: 1.0.0`, 두 스킬을 한 문장으로 설명하는 영어 `description`, 기존과 같은 `author`·`license`·`homepage`.
  - `git rm -r`로 `plugin-manifests`와 이전 `plugins/` 폴더 두 개를 지우고 `uv run python portable-skills/package.py`를 실행한다. 이전 zip은 더 이상 생성되지 않지만 Task 8까지 남겨 둔다.
- [x] Step 4: Task 1 테스트 green, `claude plugin validate portable-skills/plugins/socratic` → `✔ Validation passed`, `make format && make lint`. 마켓플레이스 테스트는 Task 2 전까지 red가 정상이다.
- [x] Step 5: 커밋하지 않고 Task 2로

### Task 2: 마켓플레이스 항목 하나와 renames
**Files:** Modify: `.claude-plugin/marketplace.json`, `tests/unit/test_portable_skills.py`
- [x] Step 1: `test_marketplace_lists_every_portable_skill`를 둘로 나눈다.
  - 항목은 정확히 하나다. `name`은 manifest `name`, `source`는 `./portable-skills/plugins/socratic`, `version` 키는 없다.
  - `renames`는 `{"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}`를 포함한다. 모든 값은 현재 항목 이름이거나 `null`이고, 현재 항목 이름과 같은 키는 없다. docstring에 02-research 경우 A를 근거로 적는다.
- [x] Step 2: red 확인
- [x] Step 3: `socratic` 항목 하나(`description`, `category: productivity`)와 `renames`. 마켓플레이스 `description`은 "두 스킬을 담은 플러그인 하나"로 고친다.
- [x] Step 4: `claude plugin validate .` → `✔ Validation passed`, 전체 `uv run pytest` exit 0, `make lint`
- [x] Step 5: 커밋 `feat(portable-skills): ship both skills as one socratic plugin`

### Task 3: 설치되는 파일에서 한국어 제거
**Files:** Modify: `portable-skills/socratic-brainstorm/SKILL.md`, `portable-skills/socratic-brainstorm/references/question-bank.md`, `portable-skills/socratic-elenchus/SKILL.md`, `portable-skills/socratic-elenchus/references/elenchus-patterns.md`, `tests/unit/test_portable_skills.py` | Generate: `plugins/socratic/`, `releases/socratic.zip`
- [ ] Step 1: `test_shipped_plugin_has_no_hangul`: `plugin_files()`의 모든 파일과 `plugins/socratic/` 아래 모든 파일에 한글(U+1100–11FF, U+3130–318F, U+A960–A97F, U+AC00–D7FF)이 없다. 실패 메시지에는 파일과 줄 번호를 넣는다.
- [ ] Step 2: red 확인 (지금 네 파일에 한글 줄이 있다: 13, 9, 18, 22줄)
- [ ] Step 3: 네 파일을 영어로 바꾼다. 문장이 하던 일은 그대로 둔다.
  - description: 한국어 트리거 예시를 지우고 영어 트리거만 남긴다. 서로를 가리키는 문장은 유지한다(라우팅). 1024자 상한.
  - 멈춤·계속 신호: 영어 신호 목록 뒤에 "or the same in the user's language"를 붙인다.
  - 예시 질문, 묶음 질문, 인용, 기록 형식 예시(`(정의)`, `(동의)` 포함): 같은 요점을 보여 주는 영어 예시로 바꾼다. 인용 규칙 예시는 어미만 바뀐 인용을 영어의 같은 경우로 바꾼다.
  - question-bank와 elenchus-patterns: 영어·한국어 쌍은 영어만 남기고, 한국어만 있는 행은 번역한다.
  - SKILL.md 본문 200줄 상한 유지. `metadata.version` → brainstorm 3.3.0, elenchus 1.3.0. 플러그인 버전은 아직 배포 전이라 1.0.0 유지.
- [ ] Step 4: `uv run python portable-skills/package.py` → 테스트 전체 green, `claude plugin validate portable-skills/plugins/socratic` 통과
- [ ] Step 5: 커밋 `feat(portable-skills): ship the skill files in English only`

### Task 4: 라우팅과 응답 언어 probe
**Files:** 없음 (결과는 Proof에 기록)
- [ ] Step 1: 준비. 저장소 밖 빈 디렉터리에서 `claude -p --plugin-dir portable-skills/plugins/socratic --model sonnet --output-format stream-json --verbose`로 첫 턴만 실행하고 Skill 호출을 읽는다. init 이벤트에 `socratic-brainstorm@synced`·`socratic-elenchus@synced`(이 기기의 claude.ai 사본)가 보이면 실행하는 동안만 `claude plugin disable`로 끄고 끝나면 `enable`로 되돌린다.
- [ ] Step 2: [10-two-skills.md](../socratic-brainstorm-skill/10-two-skills.md) §3의 일곱 프롬프트를 n=1로 실행한다. 기준선은 7/7이고, 스킬 이름만 `socratic:` 접두사로 바뀐다. 한국어 프롬프트의 첫 응답은 한국어여야 한다.
- [ ] Step 3: [12-followups.md](../socratic-brainstorm-skill/12-followups.md)의 모호한 프롬프트 두 개("소크라테스식으로 해줘: 점심 앱", "소크라테스처럼 질문해줘: 코딩 교실")를 n=2로 실행한다. 어느 스킬이 로드되든 첫 메시지에 다른 스킬을 가리키는 한 줄이 한국어로 있어야 한다.
- [ ] Step 4: 멈춤 신호. 스킬마다 한 번, 한국어 첫 턴 뒤 `--resume <session> "그만"` → brainstorm은 Step 5(판정과 brief)로, elenchus는 기록으로 바로 가야 한다.
- [ ] Step 5: 기준선보다 나빠지면 멈추고 Deviations에 기록한다. 영어 트리거 문구를 고쳐 다시 실행하고, 한국어를 되돌려 넣지는 않는다.

### Task 5: 실제 저장소로 이전 경로 probe
**Files:** 없음 (scratchpad만 사용, 결과는 Proof에 기록)
- [ ] Step 1: 02-research 경우 B를 이 저장소로 반복한다. 격리된 `CLAUDE_CONFIG_DIR`과 scratchpad bare clone(`main` = master 커밋)을 쓰고, `http://127.0.0.1:8765/<repo>.git`으로 등록한 뒤 `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.file:///<scratch>/.insteadOf GIT_CONFIG_VALUE_0=http://127.0.0.1:8765/`로 연결한다.
- [ ] Step 2: 이전 두 플러그인을 설치한다. `git update-ref refs/heads/main <branch HEAD>`로 옮긴다(hook이 `push -f`를 막는다). `claude plugin marketplace update ajitta-socratic`, `claude -p "say ok"`를 한 번 실행한다(로그인 확인 전에 설치가 일어난다).
- [ ] Step 3: `claude plugin list` → `socratic@ajitta-socratic ✔ enabled` 하나, `claude plugin details socratic@ajitta-socratic` → `Skills (2)  socratic-brainstorm, socratic-elenchus`. 다르면 멈추고 Deviations에 기록한다.

### Task 6: portable-skills/README.md
**Files:** Modify: `portable-skills/README.md`
- [ ] Step 1: 표의 Upload zip 열 대신 표 아래에 "두 스킬은 플러그인 `socratic` 하나로 배포된다"와 `releases/socratic.zip` 링크를 둔다.
- [ ] Step 2: Layout: `plugin-manifest.json`, `plugins/socratic/skills/<skill>/`, `releases/socratic.zip`. "SKILL.md at its root … single skill" 문장은 "생성된 플러그인은 스킬마다 `skills/<skill>/`에 두고 원본 폴더는 일반 스킬로 남긴다"로 바꾼다. 스킬 파일은 영어로만 쓰고 응답은 사용자 언어를 따른다는 한 줄을 넣는다.
- [ ] Step 3: Install은 claude.ai 업로드 `socratic.zip`, 마켓플레이스 `/plugin install socratic@ajitta-socratic`. 복사 설치 행은 스킬별 그대로. Invoke의 플러그인 행은 `/socratic:<skill>`.
- [ ] Step 4: 새 절 "Moving from the two plugins": Claude Code는 `/plugin marketplace update ajitta-socratic` 뒤 다음 세션에서 `socratic`으로 넘어간다. `/plugin`이 `Plugin "socratic-brainstorm" not found in marketplace`를 보이면(renames를 모르는 이전 버전) 두 플러그인을 `/plugin uninstall`하고 `/plugin install socratic@ajitta-socratic`. claude.ai 업로드 사용자는 Customize › Plugins에서 이전 두 개를 지우고 `socratic.zip`을 올린다. 지우지 않으면 같은 스킬이 두 번 로드된다.
- [ ] Step 5: Validate and package 절: 스킬을 고치면 그 스킬의 `metadata.version`과 `plugin-manifest.json`의 `version`을 함께 올린다.

### Task 7: docs/index.html (Pages)
**Files:** Modify: `docs/index.html` (nav 129행, `#plugins` 섹션 240–276행), `tests/unit/test_portable_skills.py`
- [ ] Step 1: `test_install_docs_match_the_marketplace`: `docs/index.html`과 `portable-skills/README.md`에 `/plugin install <entry>@<marketplace>`가 있다(값은 `marketplace.json`에서 읽는다). `renames`의 이전 이름으로 된 `/plugin install` 줄은 없다. `docs/index.html`에는 스킬마다 `/<plugin>:<skill>`이 있다. → red
- [ ] Step 2: nav 링크 문구 `Plugins` → `Plugin`. 제목 "Socratic plugins for Claude Code" → "Socratic plugin for Claude Code".
- [ ] Step 3: 소개 "Two plugins from this repository's marketplace, each holding one skill with the same name." → 이 저장소 마켓플레이스의 플러그인 하나 `socratic`이 두 스킬을 담는다는 문장. `/sc:brainstorm`과의 구분 문단은 유지한다.
- [ ] Step 4: 2단계 제목 "Install one plugin or both" → "Install the plugin", 명령은 `/plugin install socratic@ajitta-socratic` 한 줄. 3단계 힌트는 스킬 명령이 `socratic:`으로 시작한다는 설명으로 바꾸고, 예시 명령은 `/socratic:socratic-brainstorm`, `/socratic:socratic-elenchus`로 바꾼다. 스킬 설명 문단은 유지한다.
- [ ] Step 5: 2단계 아래에 이전 사용자용 힌트 한 줄: 두 플러그인을 쓰고 있었다면 `/plugin marketplace update ajitta-socratic`, 다음 세션에서 `socratic`으로 넘어간다.
- [ ] Step 6: 테스트 green, 전체 `uv run pytest` exit 0. 브라우저에서 `docs/index.html`을 열어 `#plugins` 섹션의 명령 블록이 좁은 폭(390px)에서 넘치지 않는지 본다.
- [ ] Step 7: 기능 README `phase: implementing`, `updated`. 커밋 `docs(portable-skills): install and migrate the single socratic plugin` (Task 6, 7 함께)

### Task 8: claude.ai 업로드 확인, 이전 zip 제거
**Files:** Delete: `portable-skills/releases/socratic-brainstorm.zip`, `portable-skills/releases/socratic-elenchus.zip` | Modify: `tests/unit/test_portable_skills.py`
- [ ] Step 1 (사용자): claude.ai › Customize › Plugins에서 기존 업로드 두 개를 지우고 Add › Upload plugin으로 `portable-skills/releases/socratic.zip`을 올린다. 두 스킬이 모두 보이는지, "소크라테스 대화법으로 따져줘: 사내 점심 메뉴 추천 앱"이 elenchus로 로드되어 한국어 "…이란 무엇인가요?"로 시작하는지 확인한다. 업로드가 거부되면 멈춘다. 이전 zip을 남기고 Deviations에 기록한 뒤, 머지 전에 claude.ai 경로를 다시 계획한다.
- [ ] Step 2: `test_releases_hold_only_the_plugin_zip`(`releases/`에는 `socratic.zip`만) → red
- [ ] Step 3: `git rm` 이전 zip 두 개 → green, 전체 `uv run pytest` exit 0
- [ ] Step 4: 커밋 `chore(portable-skills): drop the per-skill release zips`

### Task 9: 마무리
- [ ] Step 1: `uv run python portable-skills/package.py --check`, 전체 `uv run pytest`, `make lint`를 다시 실행하고 Proof에 출력을 기록한다.
- [ ] Step 2: 이 계획의 체크박스와 Deviations를 코드와 맞추고 `status: complete`.
- [ ] Step 3: 머지 전에 Handoff의 GitHub 경로 확인용 격리 설정을 만들고 이전 두 플러그인을 설치해 둔다. master 머지와 push는 사용자 요청이 있을 때만 한다.

## Risks

- 가장 위험한 단계는 Task 2를 master에 머지하는 순간이다. 사용자가 이전되면 `enabledPlugins`에는 `socratic@ajitta-socratic`만 남는다. 그 뒤 마켓플레이스를 되돌리면 같은 사용자가 경우 A로 다시 깨진다. 그래서 롤백은 앞으로 고치는 것뿐이고 `socratic` 항목과 `renames`는 지우지 않는다. Task 5를 머지 전에 두는 이유다.
- 한국어 트리거 문구를 지우면 한국어 요청의 라우팅이 나빠질 수 있다. 기준선은 10-two-skills §3의 7/7이다. Task 4가 머지 전 게이트다.
- 멈춤 신호가 영어 목록과 "same in the user's language"에 기대게 된다. Task 4 Step 4가 "그만"을 확인한다.
- `renames`를 모르는 Claude Code 버전에서는 마켓플레이스를 업데이트하면 경우 A가 된다. 최소 버전은 문서에 없다. Task 6의 수동 이전 안내로 완화한다.
- claude.ai가 두 스킬 zip을 받는지는 확인되지 않았다. Task 8이 머지 전 게이트다. claude.ai Add marketplace 경로의 `renames` 적용은 머지 뒤에야 확인할 수 있고, Task 6 안내가 그 경우도 다룬다.
- 한쪽 스킬만 설치했던 사용자도 두 스킬을 받는다. 의도 기록이 원한 결과다.
- 플러그인 버전을 올렸는지는 테스트가 확인하지 않는다. 지금의 스킬 버전과 같은 수준의 빈틈이다.

## Alternatives not taken

- 이전 두 항목을 유예 기간 동안 함께 두기: "마켓플레이스도 하나의 플러그인"과 충돌하고, 둘 다 설치한 사용자에게 스킬이 두 번 로드된다.
- 이전 이름 하나(`socratic-brainstorm`)를 통합 플러그인으로 재사용: 이름이 내용을 잘못 설명하고, elenchus 사용자에게는 결국 `renames`가 필요하다.
- `forceRemoveDeletedPlugins`만 쓰기: 이전 플러그인을 지우기만 하고 새 플러그인을 설치하지 않아 "기존 설치가 깨지면 안 됨"을 어긴다.
- 이전 이름을 `dependencies`로 연결하는 shim 플러그인: 마켓플레이스 항목이 셋이 된다.
- 원본은 한국어로 두고 빌드 때만 걸러 내기: 번역은 자동으로 할 수 없고 원본과 설치본이 갈라진다. 원본을 영어로 바꾼다.
- `plugins/socratic/skills/`에서 원본 폴더로 symlink: Windows에서는 Developer Mode나 관리자 권한이 필요하고 zip에는 symlink를 담을 수 없다.

## Deviations

- Task 1 Step 4: 이전 마켓플레이스 테스트는 Task 2 전까지 red일 것으로 적었지만 green으로 남았다. 그 테스트는 항목의 `source` 폴더가 있는지 보지 않아서, 폴더가 지워진 항목도 통과시켰다. Task 2의 새 테스트에 `source` 폴더 존재 확인을 추가했다.

## Proof

- `uv run pytest tests/unit/test_portable_skills.py -q` → 전부 통과(`test_shipped_plugin_has_no_hangul`, `test_install_docs_match_the_marketplace` 포함). 전체 `uv run pytest` → exit 0(기준선 2953 passed, 1 skipped). `make lint` → `All checks passed!`
- `uv run python portable-skills/package.py --check` → 스킬 두 개 `ok`
- `claude plugin validate portable-skills/plugins/socratic`와 `claude plugin validate .` → `✔ Validation passed`
- Task 4: 명시 프롬프트 7/7, 모호한 프롬프트에 안내 줄, 한국어 응답, "그만" 처리
- Task 5: `socratic@ajitta-socratic ✔ enabled` 하나, `Skills (2)`
- Task 8: claude.ai 업로드에서 두 스킬이 보이고 elenchus가 한국어로 시작함 (사용자 확인)

## Handoff

- 다음 버전 bump 커밋에 넣을 CHANGELOG 줄: `### Changed`(두 portable 스킬이 플러그인 `socratic` 하나로 배포됨, 슬래시 명령 `/socratic:<skill>`, 스킬 파일은 영어로만 쓰이고 응답은 사용자 언어를 따름, 3.3.0 / 1.3.0)와 `### Upgrade notes`(`/plugin marketplace update ajitta-socratic`, claude.ai 업로드 교체 절차).
- 실제 GitHub 경로 확인: 머지 전에 격리된 `CLAUDE_CONFIG_DIR`(push 때까지 남는 경로)에서 `claude plugin marketplace add ajitta/superclaude`로 이전 두 플러그인을 설치해 둔다. push 뒤 같은 설정에서 `claude plugin marketplace update ajitta-socratic`, `claude -p` 한 번, `claude plugin list` → `socratic@ajitta-socratic ✔ enabled`. 마켓플레이스를 지웠다 다시 추가하면 플러그인도 함께 제거되므로 그 방법은 쓰지 않는다. 이 기기의 `socratic-brainstorm@synced`(3.2.0), `socratic-elenchus@synced`(1.2.0)는 claude.ai 업로드 동기화 사본이라 마켓플레이스 이전과 무관하고, Task 8 Step 1에서 함께 바뀐다.
