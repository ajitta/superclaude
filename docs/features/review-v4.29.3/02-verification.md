PASS WITH FIXES — R-1~R-8은 모두 실제로 고쳐졌고 전체 테스트·ruff도 통과하지만, 새 `make typecheck`가 mypy의 차단 오류(syntax 등)를 "오류 감소"로 읽어 통과시키므로(V-1) 병합 전에 한 줄 수정이 필요하다.

# fix/review-v4.29.3-findings 독립 검증

- 대상: `00e88353..ff562580` (5 commits, 15 files, +352/−11), detached worktree. 추적 파일은 수정하지 않았다(`git status` clean).
- 환경: Linux, `.venv` Python 3.11, gawk 5.2.1 / mawk 1.3.4 / BusyBox 1.36.1 awk (`nawk`는 gawk 링크). BSD/one-true-awk와 Python 3.10 인터프리터는 없음.

## 실행 결과

| 명령 | exit | 결과 |
|---|---|---|
| `uv run pytest -q -rs` | 0 | **3878 passed, 3 skipped** (기존 3871 + 7). skip 3건은 기존과 같음(`AB_E2E`, Windows `.cmd` 2건) |
| `uv run ruff format --check src tests` / `uv run ruff check src tests` | 0 / 0 | 235 files already formatted / All checks passed |
| `make typecheck` (실제) | 0 | `mypy: 34 errors (baseline 34)`; `uv run mypy src` → `Found 34 errors in 16 files (checked 53 source files)` |
| `make help` | 0 | 22개 타깃, `typecheck` 줄 포함 |
| release awk, 실제 CHANGELOG (gawk·mawk·busybox) | — | 세 구현 md5 동일. 4.29.3 **365 B**, 4.29.2 **1945 B**, 4.29.1 1039 B, `4.19.0+ajitta` 4253 B(마지막 항목, EOF까지), `4.20.0` 0 B, `""` 0 B |
| release awk, 경계 사례 (세 구현 동일) | — | `4.29.1` vs `4.29.10` 각각 자기 항목만, `4.29`(접두사) 0 B, `4.20.0`은 `[4.20.0+ajitta]`에 매치 안 됨, `4.20.0+ajitta`는 매치 |
| `make release`, scratch 복사본, `git`/`gh`/`make` PATH 스텁 | 0 / 2 / 2 | V=4.29.3: gh 1회(`NOTES_BYTES=365`), push 1회, 잔여 파일 없음. V=4.29.4(항목 없음)·V=9.9.9(제목만, 본문 공백): `❌ CHANGELOG.md has no entry for …`, **gh 0회, push 0회**, `.release-notes.md` 없음 |
| `GH_REPO` 유도 (같은 스텁) | — | `git@github.com:o/r.git`, `git@github.com:o/r`, `https://github.com/o/r`, `…/o/r.git`, `ssh://git@github.com/o/r.git` → 모두 `o/r`. 미리 설정한 `GH_REPO=someone/else`는 유지. `…/o/r/` → `o/r/`, origin 없음 → 빈 값 |
| `gh release view v4.29.1` (읽기 전용) | — | `GH_REPO=ajitta/superclaude` → ajitta URL; 미설정·빈 값 → `release not found`(이 VM의 `gh repo set-default --view` = `SuperClaude-Org/SuperClaude_Framework`); `o/r/` → `expected the "[HOST/]OWNER/REPO" format`; make 경유 → `GH_REPO=[ajitta/superclaude]`, ajitta URL |
| `gh release view v4.29.{2,3} -R ajitta/superclaude --json body` | 0 | 앞뒤 공백 제거 후 awk 추출과 **바이트 단위 동일** (1940 / 362 chars) |
| `tests/unit/test_release_recipe.py` + master `Makefile` (scratch) | 1 | **6 failed** — 01-fixes의 "6 tests red on the old Makefile" 사실 |
| `make typecheck`, `uv` 스텁 8가지 | — | 34→rc 0, 35→rc 2, `Success: no issues found`→N=0 rc 0, `Found 1 error in 1 file`→N=1 rc 0, traceback·spawn 실패→`❌ mypy did not report a result` rc 2, **`Found 1 error in 1 file (errors prevented further checking)`→rc 0** (V-1) |
| 실제 mypy, scratch `src`에 syntax 오류 파일 추가 | 0 | mypy rc 2, `Found 2 errors in 1 file (errors prevented further checking)` → `mypy: 2 errors (baseline 34)`, **make rc 0** (V-1) |
| author-check 코퍼스, master 코드 vs branch 코드, 같은 입력(tracked `*.md` 573개) | — | 파일별 추론 format, `_blank_tags` 결과 해시, 단독 `check()` 전체 finding, 같은 디렉터리 load set의 N3/N4: 2730줄, **diff 0**. xml 추론 79개 |
| 코퍼스 내 줄을 넘는 TAG_RE 매치 수 | — | **1건**(`03d-analysis-agents-second-1.md`, 양쪽 모두 거부). 코퍼스는 이 코드 경로를 사실상 거치지 않음 → diff 0은 약한 증거 |
| `_is_multiline_tag` 적대적 프로브 21건 (master/branch) | — | 아래 V-3 및 "문제 없음" 참고 |
| `superclaude context explain "/sc:analyze --delegate …"` (`SUPERCLAUDE_PATH=src/superclaude`) | 0 | 4 files ~8323/12000 tokens, QUALITY 3245→3271. `pytest tests/unit/test_context_loader.py -k "headroom or budget"` 8 passed |
| `ast.parse(..., feature_version=(3,10))` 변경 py 3개 | 0 | 통과. 3.11+ 전용 API 사용 없음 |

## 발견 사항

### V-1 — Medium — 확신도 높음(실제 mypy로 재현): `make typecheck`가 mypy 차단 오류를 통과시킨다

- 위치: `Makefile:88-90`
- 증거: `@OUT=$$(uv run mypy src 2>&1) || true;` 로 종료 코드를 버리고, `sed -n 's/^Found \([0-9][0-9]*\) errors* in .*/\1/p'`가 `Found 2 errors in 1 file (errors prevented further checking)`에서 `2`를 뽑는다. scratch에서 `src`에 `def broken(:` 파일을 넣으면 mypy는 rc 2로 나머지 검사를 하지 않는데, 타깃은 `mypy: 2 errors (baseline 34)`, rc 0.
- 이유: 게이트의 목적은 "개수가 조용히 바뀌지 않게"인데, 검사가 멈춘 실행이 오히려 개선처럼 보인다. 게다가 새 AGENTS.md 줄 "lower the baseline when you fix errors"를 따르면 이 숫자로 baseline을 2까지 내리라고 유도한다. CI 밖 타깃이고 syntax 오류는 pytest/ruff가 잡으므로 Medium.
- 수정: 종료 코드를 보존하고 2 이상이면 실패시킨다.
  ```make
  @OUT=$$(uv run mypy src 2>&1); RC=$$?; \
  [ $$RC -le 1 ] || { printf '%s\n' "$$OUT" | tail -5; echo "❌ mypy stopped (exit $$RC)"; exit 1; }; \
  ```
  (그 아래 `Success`/`Found` 파싱은 그대로. `uv`가 mypy를 못 찾는 경우도 rc 2라 같은 분기로 간다.) `uv` 스텁 테스트를 하나 추가하면 회귀를 막는다.

### V-2 — Low — 확신도 높음: release 레시피 위 주석이 옛 동작을 설명

- 위치: `Makefile:119`
- 증거: `# Release master HEAD: run Tests (make ci), GitHub release v<version> (notes = newest CHANGELOG section), then move stable to it.` — 바로 이 "newest section" 동작이 R-1 원인이었고, 레시피는 이제 버전 키로 추출한다.
- 수정: `(notes = the CHANGELOG entry for <version>; refuses an empty one)`로 바꾼다.

### V-3 — Low — 확신도 높음(프로브): R-2 수정은 보고된 형태만 막고, 인접한 두 형태는 여전히 xml + X2

- 위치: `src/superclaude/cli/author_check.py:220-222`
- 증거(branch 코드):
  - `"<draft notes for the team\n> quoted reply\n…"` → md, error 없음 (고쳐짐). `"<draft x=1 notes\n> quoted reply\n"`도 md.
  - `"<draft\n> quoted reply\n\nSome prose here.\n"` → **xml, `X2@1`** (첫 줄 나머지가 빈 문자열이라 attribute-shaped로 통과)
  - `"<draft x=1\n> quoted reply\n"` → **xml, `X2@1`**
  - 반대 방향 동작 변화: `"<component hidden\n  name=\"x\">…"` (첫 줄의 값 없는 속성) master xml → branch **md** (X 검사가 조용히 꺼짐). 연속 줄은 이미 같은 규칙이었으므로 일관성 있는 변화이고 이 저장소 스타일에는 값 없는 속성이 없다.
- 이유: CHANGELOG 문구("a line-leading `<word prose…` line")는 정확하므로 거짓 주장은 아니다. 다만 원 리뷰가 제안한 근본 조건(연속 줄의 bare `>` 뒤에 같은 줄 텍스트가 이어지면 blockquote)은 적용되지 않았다. 실제 트리에 해당 파일 없음.
- 수정(선택): `_is_multiline_tag`에서 마지막 연속 줄이 bare `>`이고 원문에서 `match.end()`부터 줄 끝까지 공백 아닌 텍스트가 있으면 `False`. `infer_format("<draft\n> quoted reply\n") == "md"` 테스트 추가. 하지 않을 경우 01-fixes에 남은 형태로 기록.

### V-4 — Low — 확신도 높음: 새 release 테스트 2개는 동작이 아니라 문자열을 확인

- 위치: `tests/unit/test_release_recipe.py:84-89`, `:91-97`
- 증거: `test_empty_notes_stop_the_release_before_gh`는 `grep -q '[^[:space:]]' .release-notes.md` 문자열이 `gh release create`보다 앞에 있는지만 본다. 가드를 `… || true`로 망가뜨려도 통과한다. `git push … stable`보다 앞선다는 것도 확인하지 않는다(현재는 텍스트상 gh 뒤라 사실상 성립). `test_gh_targets_origin…`은 `export GH_REPO := $(shell git remote get-url origin` 접두사만 보므로 sed 식이 깨져도 통과한다.
- 반면 awk 4개 테스트는 레시피의 awk 프로그램을 그대로 실행하고, master Makefile에서 6개 모두 실패함을 확인했다. 가치 있는 테스트다.
- 수정: (a) 가드: 레시피에서 awk 줄과 grep 줄을 함께 추출해 빈 CHANGELOG로 `sh -c` 실행 후 exit≠0과 `.release-notes.md` 부재를 확인한다. 또는 이 검증에서 쓴 방식대로 `git`/`gh`/`make`를 PATH 스텁으로 두고 `make release`를 tmp 복사본에서 돌린다. (b) GH_REPO: `$(shell …)` 안의 sed 식을 추출해 위 URL 5종 → `o/r`을 parametrize로 확인한다.

### V-5 — Low — 확신도 높음: 두 커밋의 메시지가 자기 diff와 맞지 않음

- `ae9bd4ee` "fix(release): notes … gh targets origin via GH_REPO" — 실제로는 `typecheck` 타깃 전체와 `.PHONY` 추가도 포함한다(`git show ae9bd4ee -- Makefile | grep -c typecheck` → 2).
- `ff562580` "chore(make): typecheck target with a mypy baseline; …" — **Makefile 변경이 없다**(`git show ff562580 -- Makefile` 0줄). 대신 R-4 CHANGELOG 헤더 수정과 AGENTS.md 줄이 들어 있고 메시지에는 R-4가 없다.
- 수정: 병합 전 rebase로 typecheck hunk를 ff562580 쪽으로 옮기거나, 최소한 병합 커밋 메시지에 실제 배치를 적는다.

### V-6 — Low — 확신도 중간: R-3 annotation의 `ref_ts`가 5개 항목을 가리킴

- 위치: `.claude/insights.jsonl:184` (`"ref_ts": "2026-10-04T23:01:46+09:00"`)
- 증거: 같은 `ts`의 non-annotation 항목이 5개(scripts 제외, Serena 요구, GitHub 메타데이터 권한, `git merge -F -`, platform.claude.com `.md`). `insight_writer.py:210-212`는 존재 여부만 확인하고, 연결 키는 `ref_ts`뿐이다(`insight-analyst.md:68` "the `ref_ts` match is exact").
- 이유: `ref_ts`로 조인하는 독자나 `insight-analyst`는 무관한 4개도 superseded로 읽을 수 있다. annotation 본문이 `tests/unit/scripts`를 명시하고 `files` 필드가 있어 사람에게는 구분된다. 코드 소비자는 없다. 스키마의 한계(배치 수확으로 ts 중복 14건)가 원인이다.
- 수정: annotation 본문 첫머리에 대상 원문을 인용한다("Target: `tests/unit/scripts/` is only excluded from the default pytest run …"). append-only이므로 새 annotation으로 보완한다. 근본 해결(고유 id)은 별도 작업.

### V-7 — Info — 확신도 낮음(미재현): 테스트가 awk 출력을 locale 인코딩으로 디코드

- 위치: `tests/unit/test_release_recipe.py:43` (`text=True`)
- 증거: `test_current_version_has_notes`는 실제 CHANGELOG를 읽는다. 현재 4.29.3 항목은 ASCII라서 cp1252/cp949 모두 디코드되지만, 이후 항목에 `—` 같은 문자가 들어가면 Windows(cp949 등)에서 `UnicodeDecodeError`가 날 수 있다. CI는 ubuntu만 쓴다.
- 수정: `text=True` 대신 `encoding="utf-8"`.

## 확인했으나 문제 없음

- **R-1**: awk가 세 구현에서 동일하게 동작하고, 접두사·`+ajitta` 접미사 경계도 맞다(인덱스가 `]`까지 포함). 빈 노트 가드는 gh와 `git push … stable` 둘 다 이전에 멈추고 `.release-notes.md`를 지운다. `V`가 비면(sed 실패) `## []`는 매치되지 않아 가드에 걸린다. 테스트 `test_current_version_has_notes`는 다음 bump 때 빈 항목을 잡는 실질적 회귀 방지다. 참고: 마지막(가장 오래된) 항목은 EOF까지 가므로 CHANGELOG 끝에 링크 정의를 두면 노트에 섞인다. 현재 파일에는 없다.
- **GH_REPO**: https/ssh/`ssh://`, `.git` 유무 모두 `o/r`. `ifndef`로 기존 값을 존중하고, 하위 `make ci` 호출에도 상속된다. `gh release`/`gh run`/`gh workflow`가 GH_REPO를 따른다는 것을 실제 gh 2.101.0로 확인했다(`gh repo view`는 따르지 않지만 레시피는 쓰지 않음). origin이 없으면 빈 값이 되고 gh는 이를 미설정으로 취급하므로 이전 동작과 같다. trailing slash URL은 gh가 크게 실패한다(잘못된 저장소로 조용히 가지 않음). `make help`와 `test_makefile_help.py` 정상.
- **R-2 유지되어야 할 태그**: 첫 줄에 속성 있음/없음, `/>` 닫힘(별도 줄·같은 줄), 줄을 넘는 따옴표 값, 작은따옴표, 들여쓰기, bare 값(`name=x`), 탭, 따옴표 안 `>`, 뒤 공백 — 14건 모두 master와 같이 xml, error 없음. 줄 중간 `<word`, `<3 things`, 두 줄 산문 뒤 blockquote는 여전히 md. `first[name_end:]` 계산은 이름 부분에 따옴표가 없어 `_QUOTED_RE` 치환 전후 위치가 같다. 새 테스트는 master 코드에서 실패한다(`infer_format` → xml).
- **R-3/R-4/R-6/R-8**: annotation 추가(append-only, `insight_writer` 검증 통과 형식), CHANGELOG 헤더 "Releases from 4.20.1 on are tagged", 세 authoring 규칙 문장이 `xml-prose-format.md:154,158`과 일치하고 트리에 `examples><example>` 잔존 없음, `docs/experiments/brainstorm-ab-2026-05-14/variants.yaml` 존재하며 옛 경로 잔존 없음.
- **R-5**: 정상·초과·`Success`·단수형 `Found 1 error in 1 file`·크래시·mypy 없음 분기가 의도대로 동작한다(V-1 제외). AGENTS.md 줄은 숫자를 복사하지 않아 `stale-number-copies` 규칙과 맞다.
- **R-7**: 새 문구 "Docs-only changes never escalate to Level 4; one that a test, build or linter reads runs that check."는 `RULES.md:26`의 "that no test, build or linter reads, the check is inspection"과 일치한다. `9a247cb6`의 의도(키워드·경로 문자열에 따른 Level 4 자동 승격 제거, "Judge by what the code does")를 유지하며 문서의 Level 4 승격을 되살리지 않는다. 크기 13141→13246 B, 예산 헤드룸 테스트 통과. core 변경이므로 `make release`는 `CANARY_OK=1` 없이 거부된다(01-fixes도 `make canary-gates`를 예고함).
- **CHANGELOG `[Unreleased]`**: 7개 항목 모두 diff와 일치한다. "both since filled in"은 실제 릴리스 본문이 추출과 동일함으로 확인했다. "(34)"는 Makefile 값과 같다.
- **Python 3.10**: 새 코드는 `first, *rest`, f-string, `re`/`shutil`/`subprocess`만 쓴다. `feature_version=(3,10)` 파싱 통과. (참고: CI 매트릭스는 `test.yml:17` `["3.10", "3.13"]`이며 3.11은 로컬뿐이다.)

## 검증하지 못한 것

- Python 3.10/3.13 실제 실행: 인터프리터 없음(`uv python find 3.10` 실패). 문법 파싱만 확인.
- BSD/macOS awk, one-true-awk: 없음. 프로그램은 POSIX 구문(`index`, `-v`, `exit`)만 쓴다.
- Windows에서의 테스트 실행과 V-7 재현.
- `make canary-gates`(R-7 core 변경): 지시대로 실행하지 않음. 릴리스 전 필요.
- 실제 `make release`·`make ci`: 외부 쓰기라 실행하지 않고 스텁으로만 확인.
- 참고: scratch 프로브 한 건(`tests/unit/test_release_recipe.py` + master Makefile)은 격리 디렉터리에서 `.venv/bin/python -m pytest`로 돌렸다. 저장소 쪽 검증은 모두 `uv run`으로 했다.
