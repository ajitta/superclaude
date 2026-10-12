---
status: complete
revised: 2026-10-12
---

# 포크 우선 설치 가이드 — Implementation Plan

**Goal:** README.md와 Pages의 설치 안내에서 "포크해서 자기 프레임워크로 커스텀"을 추천 경로로 맨 앞에 둔다. 릴리스 그대로 설치는 두 번째 경로로 두고, 기여자 안내는 없앤다.
**Architecture:** 문서 두 개(`README.md`, `docs/index.html`)의 섹션 순서와 문구만 바꾼다. 코드 변경은 없다. 새 테스트 파일 하나가 "추천 경로가 먼저"와 "기여자 문구 없음"을 고정한다.
**Tech Stack:** Markdown (GitHub 렌더링), 정적 HTML (GitHub Pages, `stable` 브랜치), pytest

## 입력

- 사용자 (2026-10-12): "나의 추천 가이드는 포크해서 자신만의 프레임워크로 커스텀하는 거였다. contributors는 의미 없다. 아무도 없으니" → "추천 설치를 최우선으로 추가하는 방안"
- 현재 상태 (master @2cc98fda):
  - README: `## 📖 For developers & contributors`(47-60, 저장소 파일 표) → `## ⚡ Quick Installation`(62-) → 그 안 끝부분 `**For contributors/developers:**`(177-209, `git clone -b master` + make 표). 13행 "PRs welcome" 배지
  - Pages: nav `Framework · Install · Commands · Plugin · Develop`, 섹션 순서 `#framework → #install → #commands → #plugins → #develop`. `#develop`("Customize your own copy", 278-325)에 포크 흐름이 이미 있지만 맨 끝, 그리고 포크는 선택 사항("To keep your changes on GitHub, fork it first")
  - Pages `#develop`에는 첫 설치 단계(`superclaude install`)가 없다. 앞의 `#install`을 거쳤다고 가정한 흐름 → 추천 경로를 맨 앞으로 옮기면 이 단계가 필요

## 결정 (plan 기본값 — 리뷰에서 바꿀 수 있음)

| # | 사안 | 기본값 |
|---|---|---|
| P1 | 추천 경로의 시작 | GitHub에서 Fork → 자기 포크를 clone. 포크할 때 "Copy the stable branch only" 그대로 둬도 됨 (master 불필요) |
| P2 | 작업 브랜치 | 포크의 기본 브랜치(`stable`)에서 바로 작업. 새 릴리스는 `upstream`의 `stable`을 merge |
| P3 | Quick Installation | 남긴다 (두 번째 경로, "릴리스를 고치지 않고 그대로 쓰기"). 근거: 모르는 사용자도 설치함(auto memory `fork-unknown-users`), `@stable` URL 테스트가 두 문서에 이 경로를 요구 |
| P4 | 기여자 문구 | README: 배지·두 섹션 제목·"Working on SuperClaude itself?" 제거. Pages: PR 안내 문장, "contributor guidance" 제거 |
| P5 | 저장소 파일 표(CLAUDE.md, ARCHITECTURE.md, rules …) | 버리지 않고 추천 섹션 안 "커스텀 전에 읽을 파일"로 옮김 — 포크 주인에게 필요한 정보 |
| P6 | Pages `#develop` id | 유지 (외부 링크 보존), 보이는 제목·nav 라벨만 바꿈 |
| P7 | `.github/PULL_REQUEST_TEMPLATE.md` | 범위 밖. 남겨 둠 (아래 "범위 밖") |
| P8 | `make`가 없는 사용자 (Windows 기본 환경 등) | 추천 경로의 명령은 `uv`·`git`·`superclaude`만 쓴다. `make` 표(기존 README 203-209)는 옮기지 않고 삭제, 대신 README 산문 한 줄: "Have `make`? `make deploy`, `make sync-user` and `make test` wrap the same commands (see `Makefile`)." Pages에는 `make` 언급 없음. 테스트가 추천 섹션의 `make` 명령 줄을 막음 |

## 파일 지도

| 파일 | 변경 |
|---|---|
| `README.md` | 추천 섹션 신설(Quick Installation 앞), 기여자 섹션 2개 흡수·삭제, 배지 1개 삭제, Quick Installation 첫 줄에 "그대로 쓰기" 안내 |
| `docs/index.html` | `#develop` 섹션을 `#install` 앞으로 이동 + 제목·단계 수정, nav 순서, hero 버튼 대상, `#install` 안내 문장, origin 문장 |
| `tests/unit/test_install_docs.py` (신규) | 순서 가드 + 기여자 문구 가드 |
| CHANGELOG | 이번 브랜치에서는 안 씀 → 다음 version-bump 커밋에 아래 "Release note" |

## Phase 1: README

**Files:** Modify: `README.md:13`, `README.md:47-76`, `README.md:177-209` | Create: `tests/unit/test_install_docs.py`

- [x] Step 1: 실패하는 테스트 작성 — `tests/unit/test_install_docs.py`
  - `test_readme_recommends_fork_first`: `## 🍴 **Recommended: fork and make it your own**`의 위치 < `## ⚡ **Quick Installation**`의 위치 (둘 다 존재해야 함)
  - `test_install_doc_has_no_contributor_path[README.md]`: `re.search(r"contributor|pull request|PRs-welcome", text, re.I)` 없음
  - `test_fork_path_needs_no_make[README.md]`: 추천 섹션(새 제목 ~ `## ⚡`) 안에 `re.search(r"(?m)^\s*make\s", section)` 없음 — 코드 블록의 `make` 명령 줄만 걸리고, 산문의 인라인 `` `make deploy` `` 안내 한 줄은 통과
  - 문서 목록은 `_INSTALL_DOCS = {"README.md": ...}` 형태로 두고 Phase 2에서 Pages를 추가
- [x] Step 2: `uv run pytest tests/unit/test_install_docs.py -q` → 3 failed 확인 (`no_make`는 섹션이 없어 실패 — 섹션 부재도 실패로 처리)
- [x] Step 3: README 수정
  - 13행 "PRs welcome" 배지 삭제
  - 47-60 `## 📖 For developers & contributors` 삭제 → 표는 새 섹션으로 이동
  - Quick Installation 바로 앞에 새 섹션:
    ```
    ## 🍴 Recommended: fork and make it your own
    한 줄: superclaude는 출발점 → 포크해서 markdown을 고치고 자기 버전을 돌리는 것이 권장 사용법
    1. Fork → clone your fork      git clone https://github.com/<your-account>/superclaude.git
    2. Environment                 uv venv -p 3.13 / uv pip install -e ".[dev]"  (uv sync 금지 한 줄)
    3. CLI from your clone         uv tool install --force --editable .  (clone 이동·삭제 시 CLI·hook 깨짐)
    4. First install               superclaude install --scope user  (project / local 대안 한 줄)
    5. Edit → sync                 src/superclaude/ 수정 → superclaude update --scope user → Claude Code 재시작
    6. Test                        uv run pytest
    7. Pull new releases           git remote add upstream https://github.com/ajitta/superclaude.git (한 번)
                                   git pull --no-rebase upstream stable → 충돌 해결 → 3, 5 다시
    + "Files to read before you customize" 표 (기존 47-60 표)
    + 산문 한 줄: make가 있으면 같은 명령의 단축 (P8). make 표는 옮기지 않음
    ```
  - 단계의 모든 명령은 `make` 없이 실행 가능해야 함 (P8): 제거는 `superclaude uninstall --scope <s>` + `uv tool uninstall superclaude` (Quick Installation의 Uninstall 절 재사용, 링크만)
  - Quick Installation 첫 문단 앞에 한 줄: "Use the release as-is, without editing it. To customize, see *Recommended* above."
  - 74행 끝 "Working on SuperClaude itself? See *For contributors/developers* below." 삭제
  - 177-209 `**For contributors/developers:**` 블록 + 표 삭제 (새 섹션으로 흡수됨 — 같은 명령을 두 곳에 두지 않음)
- [x] Step 4: `uv run pytest` → exit 0 (`test_version_consistency.py`의 `@stable` URL·버전·개수 테스트 포함)
- [x] Step 5: Commit `docs(install): recommend forking first in the README`

## Phase 2: Pages

**Files:** Modify: `docs/index.html:125-131`, `:142`, `:170-177`, `:278-325`, `:335` | Test: `tests/unit/test_install_docs.py`

- [x] Step 1: 실패하는 테스트 추가
  - `test_pages_recommends_fork_first`: `id="develop"` 위치 < `id="install"` 위치, nav에서 `href="#develop"` < `href="#install"`, hero `class="button" href="#develop"`
  - `_INSTALL_DOCS`에 `docs/index.html` 추가 → 기여자 문구·`make` 테스트가 Pages도 검사. Pages의 추천 섹션 = `id="develop"`부터 다음 `<section` 전까지, 검사 패턴 `<code>make\s`
- [x] Step 2: `uv run pytest tests/unit/test_install_docs.py -q` → Pages 2건 failed 확인 (`no_make[Pages]`는 현재도 통과 — 현재 Pages 커스텀 섹션에 `make` 없음)
- [x] Step 3: `docs/index.html` 수정
  - `<section id="develop" …>` 블록 전체(278-325)를 `<section id="install" …>`(170) 바로 앞으로 이동
  - 제목 "Customize your own copy" → "Make it your own (recommended)", 소개 문단에 "권장 사용법" 한 줄
  - "Clone the repository" 단계 → "Fork, then clone your fork": `git clone https://github.com/<your-account>/superclaude.git`. hint: GitHub 계정이 없으면 `git clone -b stable https://github.com/ajitta/superclaude.git`. PR 문장("Sending pull requests? …") 삭제
  - "Run the CLI from your clone" 다음에 단계 추가 "Install the content": `superclaude install --scope user` (+ project/local 한 줄)
  - "Update to a new release": `git remote add upstream https://github.com/ajitta/superclaude.git` (한 번) + `git pull --no-rebase upstream stable`
  - "Developer guide in the README ↗" → 라벨 "Full guide in the README ↗", href `#-recommended-fork-and-make-it-your-own`
  - nav: `Framework · Make it yours(#develop) · Install · Commands · Plugin`
  - hero: 버튼 `href="#develop"` 라벨 "Make it your own", 옆에 텍스트 링크 "or install the release as-is" → `#install` (GitHub 링크 유지)
  - `#install` 소개의 "Want to change the framework and run your own version? See …" → "This installs the release unchanged. To customize it, see Make it your own."
  - origin 335행 "contributor guidance" → "the customization guide"
- [x] Step 4: `uv run pytest` → exit 0 (`test_portable_skills.py::test_install_docs_match_the_marketplace`, `@stable` URL 테스트 포함)
- [x] Step 5: 브라우저 확인 — `docs/index.html`을 로컬로 열어: nav 순서, hero 버튼 이동 대상, 섹션 순서, 375px 폭에서 가로 스크롤 없음, 라이트·다크 둘 다
- [x] Step 6: Commit `docs(pages): put the fork-and-customize path first`

## Phase 3: 재구성 — Quick → Clone → Fork (사용자 피드백 2026-10-12)

사용자: "마음에 들지 않는다.. 1. QUICK INSTALL, 2. CLONE INSTALL, 3. FORK INSTALL 이순서로 하자. 다음 스텝을 '/btw'로 제안받는 팁을 추가하자 '/goal'을 이용하는 방법 서술 앞에. 예시를 포함하여"

Phase 1-2의 "포크를 맨 앞" 배치(P1·P6, hero 버튼)를 대체한다. 기여자 문구 제거(P4)와 `make` 없는 경로(P8)는 유지.

**Files:** Modify: `README.md`, `docs/index.html` | Test: `tests/unit/test_install_docs.py`

- [x] Step 1: README — `## ⚡ Quick Installation` → `## 📥 Clone install`(7단계 + 커스텀 전에 읽을 파일 표) → `## 🍴 Fork install (recommended)`(Clone install과 다른 점 4개: fork, 자기 포크 clone, `git push`, `upstream`에서 릴리스). Quick Installation 첫머리에 세 경로 번호 목록
- [x] Step 2: Pages — 섹션 `#install` → `#develop`(Clone install) → `#fork`(신규, Fork install). nav `Install · Clone · Fork`, hero 버튼은 원래대로 `#install` "Get started"
- [x] Step 3: `/btw` 팁 — README·Pages 모두 `/goal` 서술 바로 앞, 예시 `/btw based on what we just did, which /sc command should I run next, and why?`. 내용 근거: code.claude.com/docs/en/interactive-mode "Side questions with /btw"(대화 기록에 안 남음, 대화 전체를 봄, 도구 없음, 작업 중에도 실행)
- [x] Step 4: 테스트 교체 — 순서(README 제목 3개, Pages 섹션·nav), 기여자 문구, Clone·Fork 구간의 `make` 명령 줄 (6건)
- [x] Step 5: `uv run pytest` exit 0 · `make lint` · `ruff format --check` · 헤드리스 Chrome 320px 305 / 375px 360(넘침 없음) + 데스크톱 스크린샷
- [x] Step 6: Commit `docs(install): order the install paths quick, clone, fork; add the /btw tip`

## Deviations

- Phase 2 Step 3: 계획의 hint "Clone `https://github.com/ajitta/superclaude.git` with `-b stable`"는 인라인 `<code>` URL이 줄바꿈되지 않아 320px에서 가로 넘침(scrollWidth 344, master 305) → URL을 "this repository" 링크로 바꿈. 측정(헤드리스 Chrome, iframe 폭): 320px 305, 375px 360 — 넘침 없음
- Phase 2 Step 5: "라이트·다크 둘 다" 확인은 해당 없음 — Pages에 `prefers-color-scheme` 스타일이 없음(master도 0건). 라이트만 확인

## Release note (다음 version-bump 커밋의 CHANGELOG `### Changed`)

- The README and the Pages site list three install paths in order: Quick install (the release as-is), Clone install (your own copy from a local clone) and Fork install (that copy in your GitHub fork, the recommended way to customize). The clone and fork paths need only `git`, `uv` and `superclaude`, no `make`. The contributor guide is gone.
- A tip before the `/goal` example: ask `/btw` which command to run next. It answers from the session without adding to the conversation.

## 범위 밖

- `.github/PULL_REQUEST_TEMPLATE.md`: 기여자 흔적이지만 설치 가이드가 아님. 지울지는 따로 결정
- README 하단 "What's new in this fork" 등 다른 섹션, Pages 디자인(CSS) 변경. 참고: 그 안 "Scope-Explicit Deployment"(README 384-386)는 `make` 타깃만 나열함 — 설치 안내가 아닌 기능 소개라 이번엔 그대로 둠
- `make release`·Pages 재배포: Pages는 `stable`에서 나오므로 merge만으로는 사이트가 안 바뀜 — 다음 릴리스 때 반영

## Risks

- **가장 위험한 단계: Phase 2 Step 3의 섹션 이동.** 48줄 블록을 잘라 옮기다 태그 짝이 깨지거나 `class="content install develop"` 스타일이 위치에 따라 달라 보일 수 있음 → Step 5 브라우저 확인이 잡음 (테스트는 순서만 봄)
- README 앵커: Pages가 `#-recommended-fork-and-make-it-your-own`으로 링크. GitHub 슬러그 규칙(이모지 제거 → 앞 하이픈, `:` 제거)은 기존 `#-quick-installation`과 같은 방식이지만 push 전에는 확인 불가 → push 후 링크 클릭으로 확인
- `@stable` URL 테스트(`test_version_consistency.py:172`)는 두 문서에 `uv tool install …@stable`이 있어야 통과 → Quick Installation과 Pages `#install`은 그대로 남기므로 영향 없음. 포크 섹션의 clone URL은 `git+https://…` 형태가 아니라 이 테스트에 안 걸림
- 기여자 문구 테스트의 오탐: "contributor"가 다른 맥락(예: 업스트림 저자 소개)에 들어가면 실패. 현재 README·Pages의 일치는 제거 대상 4곳뿐 (grep 확인 2026-10-12)
- 포크 사용자의 `superclaude update`: `install_all(force=True)`라 설치가 없어도 새로 만듦 — 문서는 첫 설치에 `install`, 이후 `update`로 나눠 적어 혼동을 줄임

## Alternatives not taken

- Quick Installation 삭제 — 모르는 사용자도 설치하며(`fork-unknown-users`), `@stable` 고정 테스트와 Pages 설치 흐름이 이 경로에 걸려 있음
- GitHub "Use this template" — 히스토리가 끊겨 `git pull upstream stable`이 unrelated histories로 실패. 포크는 히스토리를 유지해 릴리스 merge가 됨
- 별도 `CUSTOMIZE.md` — 설치 안내가 README·Pages·새 파일 세 곳으로 갈라짐. README가 이미 설치 안내의 자리
- Pages id를 `#customize`로 변경 — 기존 `#develop` 링크가 깨짐. 라벨만 바꿈

## Proof

- `uv run pytest` → exit 0, 신규 `tests/unit/test_install_docs.py` 6건 pass (문서 2개 × 순서·기여자 문구·`make` 없음, 문서별 parametrize)
- `make lint` → `All checks passed!`
- `grep -n -i "contributor\|pull request\|PRs-welcome" README.md docs/index.html` → 출력 없음
- 브라우저: Pages 로컬 파일에서 nav·hero·섹션 순서, 375px, 라이트·다크
- push 후: Pages의 "Full guide in the README ↗" 링크가 README 새 섹션으로 이동
