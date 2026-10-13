---
status: complete
revised: 2026-10-13
---

# Phase B: 검사기 no-op 규칙 — `--with`, N1–N4

Index: [05-plan.md](./05-plan.md). 계약: [04a-design-checker.md](./04a-design-checker.md) N1–N4 행과 `--with` 설명, [04b-design-common-pass.md](./04b-design-common-pass.md) §3–4.

경계 (04a 마지막 줄, 04b §4): 같은 입력에 늘 같은 답이 나오는 것만. 뜻이 같은 다른 문장, 유사도 점수는 넣지 않는다.

### Task B1: `--with`와 N3·N4

**Files:** Modify: `src/superclaude/cli/author_check.py`, `src/superclaude/cli/main.py` (author-check 명령) | Test: `tests/unit/test_author_check.py`

- [x] Step 1: 실패하는 테스트
  - `RULES`에 N1–N4 추가 → `test_every_rule_has_case`가 N 케이스를 요구한다. N3·N4 케이스는 `with_texts`(load-set 문서)를 가진 `Case`로 확장
  - `TestWith`
    - `--with`에 없는 경로 → exit 2 (`click.Path(exists=True)`, `multiple=True`)
    - N3: 대상 `- Always: run the tests`, `--with` 문서 `- Never: run the tests` → 대상 줄에 N3 error. 같은 두 문서를 `--with` 없이 대상만 검사 → N3 없음
    - N3 칸 인식 (parametrize): 헤딩 `## Always` / `## Never` 아래 목록 항목, 굵은 라벨 `**Ask First**`, 라벨 줄 `- Never: a, b`의 쉼표 항목, XML `<does>`·`<never>` 요소
    - N3 정규화: `**Run** the tests.`와 `run the tests`는 같음 (소문자, Markdown·문장부호 제거, 공백 하나)
    - N3는 한 문서 안에서도 발화 (load-set 전체 = 대상 + `--with`)
    - N4: 5단어 이상 같은 문장이 대상과 `--with` 문서에 → 대상 줄에 warning. 4단어 → 없음. 코드 펜스·frontmatter 안 → 없음
- [x] Step 2: `uv run pytest tests/unit/test_author_check.py -k "With or N3 or N4" -v` → FAIL
- [x] Step 3: 구현
  - `check(path, type_=None, fmt=None, with_paths=())`. N3·N4만 `with_paths`를 본다. 다른 규칙은 `path`에만 (04a)
  - `_normalize(s)`, `_slots(text) -> list[(slot, item, line)]` (slot ∈ allow, confirm, forbid), `_sentences(text)` (마스킹 후, frontmatter 제외)
  - 칸 이름표: allow = Always·Do·Proceed·`<does>`, confirm = Ask First, forbid = Never·Don't·`<never>` (04a N3)
- [x] Step 4: 같은 명령 → PASS

### Task B2: N1·N2

**Files:** Modify: `src/superclaude/cli/author_check.py` | Test: `tests/unit/test_author_check.py`

- [x] Step 5: 실패하는 테스트
  - N1 error: Markdown 링크 대상 파일 없음 · `other.md#anchor`의 앵커가 대상 파일 헤딩에 없음 (헤딩 → 앵커 변환: 소문자, 공백 `-`, 영숫자·`-`·`_` 외 제거) · memory의 `@path` import 줄 대상 없음
  - N1 제외: SKILL.md의 참고 파일 링크는 R1만 발화 (중복 보고 없음) · `http(s)://` 링크 · 앵커만 있는 같은 파일 링크는 이 파일 헤딩으로 판정
  - N1 warning: 인라인 코드 속 `src/app/main.py`가 저장소 루트 기준으로 없음. `tmp_path`에 `git init`한 뒤 실행 → 루트 = `git rev-parse --show-toplevel`. git이 아닌 디렉터리 → 현재 디렉터리 기준
  - N1 warning 제외: `<name>/x.md`, `*.md`, `{a}/b.py`, `$HOME/x.md`처럼 자리표시자가 있는 경로 · `/`나 확장자가 없는 토큰
  - N2: agent `tools: Read, Grep` + 본문 인라인 코드 `Bash` → error. `tools` 없음 → 검사 안 함. 본문 `mcp__example__lookup`이 `tools`에 없음 → error. `tools`에 `mcp__example__lookup` 있음 → 없음. agent가 아닌 유형 → 검사 안 함
  - 도구 이름 집합은 `fields.yaml` `tool_names`에서 (A1)
- [x] Step 6: `uv run pytest tests/unit/test_author_check.py -k "N1 or N2" -v` → FAIL
- [x] Step 7: 구현. `_repo_root(path)`: `subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path.parent, capture_output=True, text=True)`, 실패·git 없음 → `Path.cwd()`. 대상 파일 하나당 한 번만 호출
- [x] Step 8: 같은 명령 → PASS

### Task B3: N 규칙 말뭉치

**Files:** Modify: `tests/unit/test_author_check_corpus.py`

- [x] Step 9: 같은 말뭉치(배포 agents·commands)에 N1·N2만 실행해 error 목록을 모은다
- [x] Step 10: 나온 error마다 파일을 열어 실제로 끊긴 것인지 확인 (C7: "말뭉치 error는 실제로 끊긴 것만")
  - 검사기 오탐(예: 정상 앵커를 못 찾음) → 검사기 수정
  - 실제로 끊긴 것 → 콘텐츠는 이 plan에서 고치지 않는다 (scope). 테스트의 `EXPECTED_N_ERRORS` 표에 `path:code`로 고정하고, `## Deviations`와 최종 보고에 "별도 수정 후보"로 남긴다
- [x] Step 11: 테스트: 말뭉치 N1·N2 error 집합 == `EXPECTED_N_ERRORS` → 새 끊김도, 고쳐진 끊김도 red로 알려 줌
- [x] Step 12: `uv run pytest tests/unit/test_author_check_corpus.py -v` → PASS

### Task B4: 검증과 커밋

- [x] Step 13: `uv run superclaude author-check --help`에 `--with`와 N 규칙이 보임
- [x] Step 14: `make format && make lint && uv run pytest` → 모두 exit 0
- [x] Step 15: 커밋 `feat(author-check): add --with load sets and the N1-N4 no-op rules`

## Deviations

- N3는 대상 문서가 낀 충돌만 보고한다. `--with` 문서끼리의 충돌은 그 문서를 대상으로 검사할 때 나온다 (같은 충돌을 매번 다시 보고하지 않음)
- N4는 대상 문서 안의 중복도 센다 (load-set에 대상 자신이 포함됨). 인라인 코드는 가리지 않는다: 코드만 다른 두 문장이 같은 문장으로 묶이지 않게
- N1 import: memory 유형에서 한 줄 전체 `@path`와 공백 뒤의 `@path.ext` 토큰. 인라인 코드 경로는 `/`와 확장자가 있어야 하고 `..`·`~` 시작은 건너뜀
- Step 10–11: 말뭉치의 N1·N2 error 0건 → `EXPECTED_N_ERRORS`는 빈 집합. warning 5건(`docs/reports/API.md` 같은 예시·런타임 경로)은 warning 등급이 맞다는 근거
