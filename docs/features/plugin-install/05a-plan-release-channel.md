---
status: draft
revised: 2026-10-05
---

# 릴리스 채널: master HEAD 대신 릴리스를 설치하게 하기

**문제:** 1단계 README(`6d51a4be`)는 `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git`을 안내하는데, 이 URL에는 ref가 없다. 그래서 사용자는 master HEAD를 받는다. master는 개발 브랜치이기도 해서, 병합된 커밋이 릴리스 전에 그대로 사용자에게 간다. CI가 끝나기 전의 커밋도 마찬가지다. 이때 `superclaude --version`은 마지막 릴리스 번호를 보여 주지만, 설치된 내용은 그 버전과 다르다.

**Goal:**
- 사용자는 릴리스만 받는다. 릴리스는 태그 `v<version>`과 GitHub Release(본문은 CHANGELOG 최신 절)로 만들고, `stable` 브랜치를 그 커밋으로 옮긴다.
- README는 `@stable`을 설치한다. 그래서 `uv tool upgrade superclaude`는 계속 "최신 릴리스로 올리기"로 동작한다.
- 버전에서 `+ajitta` 접미사를 없앤다(2026-10-05 사용자 결정). 첫 릴리스는 `v4.20.1`이다.
- 개발 흐름(기능 브랜치 → master)은 바꾸지 않는다.

## 근거

측정일: 2026-10-05.
- 현재 태그와 GitHub Release가 하나도 없다. `git ls-remote --tags origin`과 `gh release list`가 모두 비어 있다. 로컬에 있는 `v4.1.x`/`v4.2.0` 태그는 upstream 것이다. 지금까지 릴리스는 `chore/version-*` 브랜치의 bump 커밋을 master에 병합하는 것이 전부였다(`05cd65b3`, `c515e8b5`).
- 영향 크기: 4.19.0 bump(`c515e8b5`, 10-03 21:45)와 4.20.0 bump(`05cd65b3`, 10-04 23:07) 사이에 `src/superclaude`를 바꾼 커밋이 10개 있었다. 그동안 git URL로 설치한 사용자라면 이 커밋들을 4.19.0+ajitta라는 이름으로 받았을 것이다. 4.20.0 bump 이후에는 `src/superclaude`와 `pyproject.toml` 변경이 0건이라 아직 어긋난 것은 없다.
- uv 동작(scratch clone에서 측정, uv 0.12.17):
  - ref 없이 설치하면 `uv tool upgrade`가 master의 새 커밋을 받는다(1단계 Task 1.1).
  - `@stable`로 설치하면 master가 움직여도 `upgrade`는 그대로다. `stable`을 fast-forward하면 `upgrade`가 그 커밋을 받는다.
  - 태그(`@v4.20.0+ajitta`)로 설치하면 `+`가 `%2B`로 인코딩되어 설치는 된다. 하지만 태그는 움직이지 않으므로 `upgrade`로는 다음 버전으로 가지 않는다.
  - 이미 설치한 tool의 ref를 바꾸려면 `uv tool install … @stable`을 다시 실행하면 된다. `--force`는 필요 없다.
- `+ajitta` 접미사(PEP 440 local version):
  - uv/pip 설치에는 문제가 없다(`superclaude==4.20.0+ajitta` 설치 확인).
  - PyPI 업로드는 거부한다.
  - 태그와 URL에 `+`가 들어가 `%2B` 인코딩이 생긴다.
  - 코드는 버전을 같은지만 비교한다(`cli/doctor.py:149`, `cli/install_components.py:377`). 그래서 접미사를 빼도 순서 비교가 깨지는 곳이 없다.
  - 버전 문자열이 있는 곳: `pyproject.toml:7`, `src/superclaude/__init__.py:7`, `README.md:8`(badge), `README.md:64`, `src/superclaude/commands/sc.md:74`, `CHANGELOG.md:5`(버전 규칙 문장). README와 sc.md는 테스트가 pyproject 버전과 맞춘다(`test_version_consistency.py`).
- CHANGELOG 최신 절이 pyproject 버전과 같은지는 이미 테스트가 지킨다(`test_version_consistency.py:176`). 따라서 CI가 green이면 릴리스 노트로 쓸 절이 있다.
- CI(`test.yml:3-7`)는 `master`와 `integration` push에서만 돈다. `stable` push는 CI를 다시 돌리지 않는다. 같은 커밋을 이미 master에서 검사했으므로 필요도 없다.
- `CLAUDE.md:44`와 `AGENTS.md:69`에는 `master ← integration ← feature/*`라고 적혀 있다. 그러나 origin에 `integration` 브랜치가 없고, 실제로는 기능 브랜치를 master에 바로 병합한다.

## 선택지

| 방식 | 사용자 업데이트 | 유지 비용 | 판단 |
|---|---|---|---|
| A. 태그 + GitHub Release + `stable` 브랜치 | `uv tool upgrade` 그대로 | 릴리스마다 `make release` 한 번 | **채택** |
| B. 태그 + Release만 쓰고 README는 `@v<version>`으로 고정 | 릴리스마다 README의 새 install 줄을 다시 실행해야 함. `upgrade`는 아무것도 안 함(측정) | bump마다 README 태그 갱신(테스트로 고정 가능) | 1단계에서 안내한 `uv tool upgrade`가 쓸모없어짐 |
| C. 문서대로 `integration`을 개발 브랜치로 쓰고 master는 릴리스 때만 병합 | ref 없는 URL 그대로 | 모든 병합 대상이 바뀜. Pages(`master:/docs`)와 계획·gotcha 문서의 "master에 병합" 절차를 모두 고쳐야 함 | 변경 범위가 가장 큼 |

A를 고른 이유: B의 태그(특정 버전 고정, 롤백)와 C의 "ref 하나로 최신 릴리스"를 함께 얻으면서 개발 흐름은 그대로 둔다.

## 범위 밖

- PyPI 배포(`superclaude` 이름은 upstream이 쓰고 있음)와 wheel을 Release asset으로 올리는 일. 접미사를 없애면 다른 배포 이름으로 PyPI에 올릴 길은 열리지만, 이번 계획은 git URL 설치만 다룬다.
- 이미 릴리스된 CHANGELOG 제목(`[4.20.0+ajitta]`, `[4.19.0+ajitta]`)과 과거 문서·메모리에 남은 `+ajitta`. 당시 실제 버전 이름이므로 고치지 않는다.
- `stable` 브랜치 보호 규칙, GitHub Pages(`master:/docs`)가 릴리스 전 기능을 소개하는 문제, `test.yml`의 `integration` 트리거(없는 브랜치를 가리켜도 해가 없음).

## Phase 0: 브랜치와 `stable` 선생성

- [ ] master에서 `git switch -c docs/release-channel`.
- [ ] `git push origin 0ad12f69:refs/heads/stable`.
  - 이 커밋의 `src/superclaude`와 `pyproject.toml`은 4.20.0 bump(`05cd65b3`)와 같다(`git diff --quiet 05cd65b3 0ad12f69 -- src/superclaude pyproject.toml`).
  - README가 `@stable`을 가리키기 전에 브랜치가 있어야 한다. 그래야 Phase 1 push부터 첫 릴리스까지 설치가 실패하는 구간이 없고, 그동안 `@stable`은 4.20.0 코드를 준다.

## Phase 1: release 절차, README, 브랜치 문서 (브랜치 `docs/release-channel`, 커밋 1개)

### Task 1.1: `make release`

**Files:** Modify: `Makefile` (`.PHONY`, 새 target, `help` 목록 한 줄)

- [ ] Step 1: target을 추가한다. 이 target은 master HEAD를 릴리스한다.
  - 미리 확인하는 조건:
    - 현재 브랜치가 master다.
    - 작업 트리가 깨끗하다.
    - HEAD가 `origin/master`와 같다.
    - 그 커밋의 Tests workflow가 success다.
  - 따로 검사하지 않는 경우: 태그가 이미 있으면 `gh release create`가 실패하고, `stable`이 HEAD의 조상이 아니면 일반 push가 거부된다.
  ```make
  # Release master HEAD: GitHub release v<version> (notes = newest CHANGELOG section), then move stable to it.
  release:
  	@set -e; \
  	V=$$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml); SHA=$$(git rev-parse HEAD); \
  	test "$$(git branch --show-current)" = master || { echo "❌ not on master"; exit 1; }; \
  	git diff --quiet HEAD || { echo "❌ uncommitted changes"; exit 1; }; \
  	git fetch -q origin master; test "$$SHA" = "$$(git rev-parse origin/master)" || { echo "❌ HEAD is not origin/master"; exit 1; }; \
  	test "$$(gh run list --commit $$SHA --workflow Tests --json conclusion --jq '.[0].conclusion')" = success || { echo "❌ Tests not green for $$SHA"; exit 1; }; \
  	awk '/^## \[/{n++; next} n==1' CHANGELOG.md > .release-notes.md; \
  	gh release create "v$$V" --target "$$SHA" --title "v$$V" --notes-file .release-notes.md; rm -f .release-notes.md; \
  	git push origin "$$SHA:refs/heads/stable"; \
  	echo "✅ v$$V released; stable → $$SHA"
  ```
  `sed`가 잡는 줄은 `pyproject.toml:7` 하나뿐이다(`^version = `로 시작하는 줄이 그것 하나다). recipe는 지금의 다른 target처럼 Git Bash `sh`에서 실행된다.
- [ ] Step 2: 실제로 실행하지 않고 확인한다.
  - `make -n release`가 recipe를 출력하는지 본다.
  - `awk '/^## \[/{n++; next} n==1' CHANGELOG.md | head -3`의 출력이 최신 절의 `### Added`로 시작하는지 본다.

### Task 1.2: README

**Files:** Modify: `README.md` (설치 1단계, Update 절)

- [ ] Step 1: install 줄을 `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable`로 바꾸고, `stable`은 최신 릴리스라고 한 문장 적는다. 특정 버전을 고정하려면 `@stable` 대신 `@v<version>`을 쓰고, 버전 목록은 Releases 페이지에 있다고 덧붙인다. 버전 숫자는 새로 적지 않는다(gotcha `stale-number-copies`).
- [ ] Step 2: Update 절의 주석을 `# pull the latest release`로 바꾼다.

### Task 1.3: README install URL 검사

**Files:** Test: `tests/unit/test_version_consistency.py`

- [ ] Step 1: README에 나오는 `git+https://github.com/ajitta/superclaude.git`의 모든 출현이 `@stable` 또는 `@v`로 끝나는지 검사한다. 첫 출현만 보지 않고 모든 출현을 본다(RULES_DOCS durability 규칙의 absence lint). 2단계 plugin 절처럼 나중에 URL을 복사해 넣는 경우를 잡기 위해서다. 테스트는 Task 1.2 전의 README로 먼저 실패하는 것을 확인한다.

### Task 1.4: 브랜치 문서

**Files:** Modify: `CLAUDE.md` (:44), `AGENTS.md` (:69)

- [ ] Step 1: 두 파일의 해당 줄을 `Branch: \`stable\` (release channel, moved only by \`make release\`) ← \`master\` ← \`feature/*\`, \`fix/*\`, \`docs/*\``로 바꾼다. 그 아래에 "Release: version-bump branch merged and green on master → `make release`" 한 줄을 둔다. 두 문장 모두 누군가 바꾸기 전까지 참이므로 항상 로드되는 문서에 두어도 된다.

### Task 1.5: 검증과 병합

- [ ] `uv run pytest` exit 0, `make format`.
- [ ] 커밋: `docs: install the latest release from the stable branch; add make release`.
- [ ] `git checkout master && git merge --no-ff docs/release-channel -m "…"`를 한 명령으로 실행한다(gotcha `editable-tool-branch-switch`). push하고 Tests workflow가 green인지 확인한다.

## Phase 2: 4.20.1 bump, `+ajitta` 삭제 (브랜치 `chore/version-4.20.1`, 커밋 1개)

접미사만 지우고 버전을 4.20.0으로 두지 않는 이유가 있다. PEP 440에서 `4.20.0`은 `4.20.0+ajitta`보다 낮은 버전이고, 같은 코드에 이름이 둘 생긴다. 새 patch 번호를 쓰면 둘 다 피할 수 있다. 이 릴리스에는 기능 변경이 없다.

- [ ] `pyproject.toml:7`, `src/superclaude/__init__.py:7`, `README.md:8`, `README.md:64`, `src/superclaude/commands/sc.md:74`를 `4.20.1`로 바꾼다. README badge는 `version-4.20.1-blue`가 된다.
- [ ] `CHANGELOG.md:5`의 "with a `+ajitta` local suffix"를 지우고, 버전은 `X.Y.Z`, 태그는 `vX.Y.Z`, 최신 릴리스는 `stable` 브랜치라고 적는다.
- [ ] CHANGELOG에 `## [4.20.1] - <date>` 절을 쓴다.
  - Changed: 버전에서 `+ajitta` 접미사를 없앴다. README가 `@stable`(최신 릴리스)을 설치한다.
  - Added: 릴리스마다 GitHub Release와 `v<version>` 태그를 만든다.
  - Upgrade notes: "`@stable` 없이 git URL로 설치했다면 그 설치는 master를 따라간다. `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable`을 한 번 다시 실행하라(`--force` 불필요)." 이후 `superclaude update --scope <s>`.
- [ ] `uv run pytest` exit 0. `test_version_consistency.py`가 다섯 곳과 CHANGELOG 제목을 pyproject와 맞춘다.
- [ ] `make format`, 커밋 `chore: bump version to 4.20.1, drop the +ajitta suffix`, 한 명령으로 병합, push, CI green 확인.
- [ ] 보류 중인 [05-plan.md](./05-plan.md)의 `4.21.0+ajitta`는 재개할 때 `4.21.0`으로 읽는다. 그 계획의 보류 메모에 이 한 줄을 같은 커밋으로 덧붙인다.

## Phase 3: 첫 릴리스 v4.20.1

- [ ] master HEAD가 4.20.1 bump 병합이고 CI가 green인 상태에서 `make release`를 실행한다.
  - `gh release view v4.20.1`의 본문이 CHANGELOG 4.20.1 절과 같은지 본다.
  - `git ls-remote origin stable`이 HEAD와 같은지 본다.
- [ ] scratch `UV_TOOL_DIR`/HOME에서 확인한다(1단계 Task 1.1과 같은 격리 방식).
  - `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git@stable`의 `direct_url.json` `commit_id`가 릴리스 커밋이고, `superclaude --version`이 `4.20.1`이다.
  - `superclaude install --scope user`, `doctor`, `verify-drift`가 통과한다.
  - `uv tool upgrade superclaude`가 커밋을 바꾸지 않는다.
- [ ] `@v4.20.1`로 한 번 더 설치해서 태그로 고정하는 경로도 확인한다.

## 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| `make release`를 잊음 | 사용자가 이전 릴리스에 머묾(안전한 쪽으로 실패) | CLAUDE.md의 Release 줄 |
| bump 병합 뒤 다른 src 커밋이 릴리스보다 먼저 병합됨 | 그 커밋이 해당 버전 이름으로 릴리스됨 | bump 병합 직후 릴리스. 의심되면 `git log <bump>..HEAD -- src/superclaude`로 확인 |
| upstream이 같은 이름의 태그를 만듦(`git fetch upstream`이 태그도 가져옴) | 로컬 태그 충돌, fetch 거부 | upstream은 4.3.x라 낮음. 충돌하면 `git fetch upstream --no-tags` |
| Windows에서 make recipe의 `sh` 문법 차이 | target 실패 | Task 1.1 Step 2의 `make -n`, Phase 3의 실제 실행 |
| ref 없는 URL로 이미 설치한 사용자 | master를 계속 따라감 | 4.20.1 Upgrade notes |

## 완료 기준

- README의 모든 설치 URL이 `@stable` 또는 `@v…`로 끝나고, 테스트가 이를 검사한다.
- 버전 문자열에 `+ajitta`가 없다(과거 CHANGELOG 제목은 예외).
- `uv run pytest` exit 0, CI green.
- `v4.20.1` GitHub Release가 있고, 본문이 CHANGELOG 4.20.1 절이다. `origin/stable`이 그 커밋을 가리킨다.
- `git+https://…@stable` scratch 설치가 4.20.1 릴리스 커밋을 받고, doctor와 verify-drift가 통과한다.
