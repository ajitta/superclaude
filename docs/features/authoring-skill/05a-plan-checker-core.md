---
status: draft
revised: 2026-10-13
---

# Phase A: 검사기 코어 — `fields.yaml`, 인터페이스, F/R/S/X

Index: [05-plan.md](./05-plan.md). 계약: [04a-design-checker.md](./04a-design-checker.md) 인터페이스·규칙표, [04-design.md](./04-design.md) C3 `fields.yaml` 행.

### Task A1: `fields.yaml`

**Files:** Create: `src/superclaude/skills/sc-author/references/fields.yaml` | Test: `tests/unit/test_author_check.py`

- [ ] Step 1: 실패하는 테스트 `TestFieldsYaml`
  - `yaml.safe_load` 성공, 최상위 키 `sources`, `tool_names`, `types`
  - `sources`: 비어 있지 않은 목록, 항목마다 `url`(https)과 `retrieved`(`YYYY-MM-DD`)
  - `types`의 키 집합 = `{skill, agent, command, output-style, memory}` (generic은 행 없음, 04b §2)
  - 유형마다 `location`(목록), `frontmatter`(`required|optional`), `required`, `optional`, `unsupported`(목록), `limits`(dict)
  - 한 필드가 `required`·`optional`과 `unsupported`에 동시에 있지 않음
  - `tool_names`는 비어 있지 않고 `Bash`, `PowerShell`, `Read`를 포함
- [ ] Step 2: `uv run pytest tests/unit/test_author_check.py -k FieldsYaml -v` → FAIL (파일 없음)
- [ ] Step 3: 문서를 다시 조회해 채운다 (D12, 조회일 기록)
  - skill: `code.claude.com/docs/en/skills` frontmatter 표. `limits: {name_chars: 64, description_chars: 1536, body_lines: 500}`
  - agent: `code.claude.com/docs/en/sub-agents`. `name`의 `:` 금지는 F5 코드가 맡는다
  - command: 같은 skills 문서의 commands 설명. `unsupported: [name, paths]` (04-design C3 함정. 문서에서 다시 확인하고 다르면 문서를 따르고 `## Deviations`에 기록)
  - output-style: `code.claude.com/docs/en/output-styles`. `keep-coding-instructions` 포함
  - memory: `code.claude.com/docs/en/memory`. `frontmatter: optional`, `optional: [paths]`, `limits: {body_lines: 200}`
  - `tool_names`: `code.claude.com/docs/en/tools-reference`의 도구 이름 전부
  - 파일 맨 위 주석: 누가 읽는지(`/sc-author` Resolve, `author-check` F1–F7·N2), 미등록 필드는 F4 warning
- [ ] Step 4: 같은 명령 → PASS

### Task A2: 추론과 마스킹

**Files:** Create: `src/superclaude/cli/author_check.py` | Test: `tests/unit/test_author_check.py`

- [ ] Step 5: 실패하는 테스트
  - `TestInferType` (parametrize, 경로는 `as_posix()`로 비교해 Windows에서도 같음): `x/.claude/skills/foo/SKILL.md`→skill, `x/.claude/agents/a.md`→agent, `x/.claude/commands/g/c.md`→command, `x/.claude/output-styles/s.md`→output-style, `CLAUDE.md`·`CLAUDE.local.md`·`AGENTS.md`·`x/.claude/rules/r.md`·`x/.claude/rules/sub/r.md`→memory, `docs/MODE_X.md`→generic
  - `TestInferFormat`: frontmatter + 빈 줄 + `<!-- c -->` + `@docs/a.md` 뒤 첫 줄이 `<root>` → xml. 첫 줄이 `# Title` → md. 첫 줄이 `<3 items` → md
  - `TestTagRecognition`: `<3`, `<5KB`, `<=`, `a < b`는 태그 아님. `<role>`, `</role>`, `<br/>`, `<example kind="x">`는 태그. 코드 펜스 안과 인라인 코드 안의 `<role>`은 무시 (마스킹 후 줄 번호 보존)
- [ ] Step 6: `uv run pytest tests/unit/test_author_check.py -k "Infer or TagRecognition" -v` → FAIL
- [ ] Step 7: 구현
  - 상수 `TAG_RE = re.compile(r"</?[a-z][a-z0-9_]*(\s[^>]*)?/?>")` (04a 인터페이스)
  - `mask_code(text) -> str`: 코드 펜스 줄과 인라인 코드 내용을 같은 길이의 공백으로 바꿈 → 줄·열 번호 유지
  - `split_frontmatter(text) -> (dict | None, error | None, body, body_start_line)`: `yaml.safe_load` 사용 (04a, 남의 저장소 문서)
  - `infer_type(path)`, `infer_format(body)`
  - `load_fields()`: `install_paths._get_package_root() / "skills/sc-author/references/fields.yaml"` (설치본이 아니라 패키지 사본, 04-design §3.1)
- [ ] Step 8: 같은 명령 → PASS

### Task A3: F/R/S/X 규칙

**Files:** Modify: `src/superclaude/cli/author_check.py` | Test: `tests/unit/test_author_check.py`

- [ ] Step 9: 실패하는 테스트 `TestRules`
  - 모듈 상수 `RULES: dict[str, str]` (코드 → 기본 등급). 이 phase에서는 F1–F7, R1–R3, S1–S2, X1–X7
  - 테스트 표 `CASES = {code: Case(rel_path, type, format, bad, good)}`: 규칙 코드마다 위반 텍스트 1 + 통과 텍스트 1 (C7 "규칙 코드마다 위반 픽스처 1 + 통과 픽스처 1"). `tmp_path`에 써서 실행
  - `test_bad_fires`: bad → 그 코드가 `RULES` 등급으로 나옴. `test_good_silent`: good → 그 코드가 안 나옴
  - `test_every_rule_has_case`: `set(CASES) == set(RULES)` → 새 코드를 추가하고 케이스를 빠뜨리면 red
  - 경계 케이스
    - F6: description + when_to_use 1,536자 통과, 1,537자 error
    - S2: 대문자 강조어 2회 통과, 3회 warning
    - X1: memory xml에서 루트 앞 `@path` 줄·HTML 주석은 통과. skill xml에서 루트 밖 맨 텍스트는 error
    - X4: root → section → sub → item(4단) 통과, 5단 error
    - X5: `<example>` 안의 `#` 헤더는 통과
    - R1: SKILL.md 본문의 `${CLAUDE_SKILL_DIR}/references/x.md`는 스킬 디렉터리로 치환해 존재 확인 (04a 링크 해석)
    - R2·R3는 SKILL.md가 링크한 참고 파일을 열어서 판정 (깊이 1까지만 따라감)
- [ ] Step 10: `uv run pytest tests/unit/test_author_check.py -k Rules -v` → FAIL
- [ ] Step 11: 구현. `Finding(path, line, code, severity, message)` dataclass, 묶음별 함수 `_check_frontmatter`, `_check_refs`, `_check_size`, `_check_xml`, 진입점 `check(path, type_=None, fmt=None) -> list[Finding]`
  - 유형별 적용: generic은 F 규칙 없음, R·S2·X(xml일 때)만 (04a `--type` 설명)
  - X 규칙은 `mask_code` 결과에만. X7은 형식 감지와 무관하게 `--format xml` + output-style일 때
  - F5 skill 이름: `^[a-z0-9-]{1,64}$`. agent 이름: `:` 포함 시 error
  - F7: description이 `I `·`I'`·`You `·`We `로 시작하거나 `I can`·`You can` 포함
- [ ] Step 12: 같은 명령 → PASS

### Task A4: CLI 명령

**Files:** Modify: `src/superclaude/cli/main.py` (`verify-drift` 명령 `:492-570` 뒤에 추가) | Test: `tests/unit/test_author_check.py`

- [ ] Step 13: 실패하는 테스트 `TestCli` (`click.testing.CliRunner`)
  - error 하나 있는 파일 → 출력 줄 `path:line: CODE message`, 마지막 줄 `1 errors, 0 warnings`, exit 1
  - warning만 → exit 0. 깨끗한 파일 → `0 errors, 0 warnings`, exit 0
  - 없는 경로 → exit 2. `--type unknown` → exit 2
- [ ] Step 14: `uv run pytest tests/unit/test_author_check.py -k Cli -v` → FAIL
- [ ] Step 15: `@main.command(name="author-check")`. 인자 `path`는 `click.Path(exists=True, dir_okay=False)` (없으면 click이 exit 2), `--type`은 `click.Choice([...6개])`, `--format`은 `click.Choice(["md", "xml"])`. 명령 함수 안에서 `from .author_check import check`로 지연 import (다른 명령과 같은 방식). docstring에 규칙 코드 묶음과 exit 의미
- [ ] Step 16: 같은 명령 → PASS. `uv run superclaude author-check --help` 확인

### Task A5: XML 회귀 말뭉치

**Files:** Create: `tests/unit/test_author_check_corpus.py`

- [ ] Step 17: `src/superclaude/agents/*.md`, `src/superclaude/commands/*.md`(README 제외)를 `--format xml`로 검사해 X1–X6 error가 0인지 확인하는 parametrize 테스트. 이미 산문 속 `<3`·`<5KB`가 있는 파일: `agents/project-manager.md:77`, `commands/pm.md:43`, `commands/index-repo.md:18` (04-design C7)
- [ ] Step 18: `uv run pytest tests/unit/test_author_check_corpus.py -v`
  - 실패하면 줄을 열어 원인을 가린다: 검사기 오탐 → 검사기 수정 / 콘텐츠가 실제로 규칙 위반 → 콘텐츠는 고치지 않고 그 파일·코드를 테스트의 `KNOWN` 표에 이유와 함께 고정하고 `## Deviations`에 기록
- [ ] Step 19: PASS

### Task A6: 검증과 커밋

- [ ] Step 20: `.py` 수 재계산 → `02_component_and_delivery_map.md` §1 "전체 Python module" 행 갱신 (`author_check.py` 1개 추가)
- [ ] Step 21: `make format && make lint && uv run pytest` → 모두 exit 0
- [ ] Step 22: 커밋 `feat(author-check): add the author-check validator with frontmatter, reference, size and XML rules`
