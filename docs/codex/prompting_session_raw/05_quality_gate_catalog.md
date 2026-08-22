---
title: SuperClaude 품질 게이트 카탈로그
status: working-guide
last_verified: 2026-08-22
measured_at: 5b6dc5b
---

기준선 수치는 이 문서에 두지 않는다. 현재 baseline과 재측정 명령은
[`08_current_findings_and_backlog.md`](08_current_findings_and_backlog.md)의 `F-006`,
`F-009`, `F-014`가 소유한다.

# SuperClaude 품질 게이트 카탈로그

## 1. 판정 규칙

| 판정 | 의미 |
|---|---|
| PASS | 적용되는 hard gate가 모두 통과했고 알려진 회귀가 없음 |
| REVISE | hard failure는 없지만 증거·coverage가 부족하거나 soft regression이 있음 |
| FAIL | 하나 이상의 hard gate가 실패함 |
| NOT RUN | 필요한 gate를 실행하지 않음; PASS로 표현 금지 |
| N/A | 변경 표면에 적용되지 않으며 이유를 기록함 |

hard gate를 먼저 적용한 뒤 soft metric을 본다. Security, explicit constraint,
artifact 누락, false completion, required test failure는 평균 점수로 상쇄하지 않는다.

## 2. 공통 게이트

### G0 — 변경 계약과 admission

**목적:** 잘못된 문제를 정교하게 해결하는 것을 막는다.

Hard gate:

- 관찰된 실패 또는 명시적 요구가 있다.
- component와 delivery path가 식별됐다.
- hard constraint, authority, success evidence가 정의됐다.
- 변경이 runtime 소관인지 prose 소관인지 구분됐다.
- 같은 답의 기존 SSOT를 먼저 찾았다.

증거: `01_session_to_repository_principles.md`의 change schema.

### G1 — 정적 형식과 저작 규약

**목적:** parser가 읽을 수 있고 타입 contract가 유지되는지 확인한다.

```bash
uv run ruff check .
uv run ruff format --check <changed-python-paths>
uv run pytest tests/unit/test_rules_schemas.py -v
```

콘텐츠 타입별로 `test_*_structure.py`를 추가한다. Markdown-only guide 변경에는
Python formatting gate를 N/A로 둘 수 있다.

현재 전체 `uv run ruff format --check .`는 실패한다. 대상 파일 목록과 마지막 관측은
[`08_current_findings_and_backlog.md`](08_current_findings_and_backlog.md)의 `F-009`에
있다. 새 변경의 실패와 기존 baseline을 분리해서 보고하되, 릴리스 전체 gate로 쓰려면
baseline부터 정리해야 한다.

### G2 — graph와 wiring 무결성

**목적:** 파일은 존재하지만 전달되지 않는 dead content와 dangling edge를 막는다.

```bash
uv run pytest tests/unit/test_cross_references.py -v
uv run pytest tests/unit/test_content_usage.py -v
uv run pytest tests/unit/test_context_loader.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
```

확인 edge:

```text
file ↔ filename/component name
file ↔ README/catalog
handoff/reference ↔ target
mode/MCP/core module ↔ loader tier
component ↔ installer target
hook config ↔ script
skill ↔ supporting files
source component ↔ tracked OKF resource
source payload ↔ plugin manifest/artifact
```

현재 graph 검사는 모든 edge를 다루지 않는다. skills/MCP handoff, agent의 문장형
trigger overlap, supporting file link는 별도 확인이 필요하다.

### G3 — deterministic unit behavior

**목적:** 가장 좁은 falsifying test에서 코드 contract를 확인한다.

```bash
uv run pytest <affected-test-file> -v
uv run pytest -k '<affected-behavior>' -v
```

`scripts/auto_improve` 또는 `scripts/parallel_ab` 변경은 기본 suite에서 제외되므로:

```bash
make test-scripts
```

### G4 — integration과 scope

**목적:** 여러 요소가 연결된 상태와 scope-specific delivery를 검증한다.

```bash
uv run pytest tests/integration/ -v
uv run pytest tests/unit/test_cli_install.py -v
uv run pytest tests/unit/test_install_settings.py -v
uv run pytest tests/unit/test_scope_paths.py -v
```

설치 변경은 임시 환경에서 user/project/local 각각 install→reinstall→uninstall을
실행하고 사용자 sentinel과 durable state 보존을 검사한다.

### G5 — behavioral·security outcome

**목적:** prose/trigger/model 변화가 실제 workload에서 의도한 행동을 만드는지
확인한다.

```bash
uv run pytest tests/unit/test_eval_harness.py -v
uv run python evals/run_eval.py --dry-run
uv run python evals/run_eval.py \
  --arms vanilla,sc-full \
  --task <task-id> \
  --model <pinned-model>
```

모델·core·광범위 routing 변경은 canary 또는 full matrix를 조건부로 실행한다.

```bash
uv run python evals/run_eval.py --canary --model <pinned-model>
uv run pytest tests/integration/test_skill_canary.py -m canary -v
```

인증·비용이 없는 환경에서는 NOT RUN으로 기록하며 dry-run을 행동 통과로
승격하지 않는다.

### G6 — distribution parity

**목적:** source/editable install과 실제 wheel/sdist가 동일한 기능을 제공하는지
확인한다.

Hard gate:

- expected source payload가 wheel과 sdist에 모두 존재한다.
- clean wheel install에서 console/pytest entry point가 동작한다.
- wheel-installed CLI로 component 설치가 성공한다.
- placeholder가 설치본에 남지 않는다.
- 핵심 활성화 실패가 process nonzero로 전파된다.
- OKF 또는 plugin처럼 선언된 파생 경로는 tracked inventory와 clean build가
  source taxonomy와 일치하거나, 지원 중단이 명시된다.

현재 `skills/` 누락으로 이 gate는 실패한다. `F-001` 참조.

### G7 — 전체 회귀와 증거 봉인

**목적:** narrow pass를 전체 pass로 오인하지 않고 재현 가능한 릴리스 기록을 남긴다.

```bash
make test
make test-scripts
make lint
uv run python evals/run_eval.py --dry-run
git diff --check
```

`git diff --check`는 untracked 새 파일을 검사하지 않는다. tracked diff와 별도로
신규 문서를 명시해서 frontmatter, 상대 링크, code fence, trailing whitespace를
검사한다. 신규 파일 목록은 `git status --short`에서 확정하며 glob이 새 파일을
조용히 빠뜨리지 않게 한다.

```bash
git status --short
git diff --check
! rg -n '[[:blank:]]+$' <new-markdown-files>
uv run python - <new-markdown-files> <<'PY'
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

for raw_path in sys.argv[1:]:
    path = Path(raw_path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"missing frontmatter: {path}"
    _, frontmatter, body = text.split("---", 2)

    import yaml

    yaml.safe_load(frontmatter)
    fences = sum(line.lstrip().startswith("```") for line in body.splitlines())
    assert fences % 2 == 0, f"unbalanced code fence: {path}"
    assert not any(re.search(r"[ \t]+$", line) for line in text.splitlines()), (
        f"trailing whitespace: {path}"
    )

    for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", body):
        if link.startswith("#") or urlparse(link).scheme:
            continue
        target = unquote(link.split("#", 1)[0]).strip("<>")
        assert (path.parent / target).exists(), f"broken link: {path} -> {link}"
PY
```

추가 조건:

- critical slice는 baseline보다 나빠지지 않는다.
- constraint violation, false completion, security violation은 증가하지 않는다.
- 변경된 behavior에는 regression fixture가 있다.
- 실제 실행한 명령, 결과 수, NOT RUN 이유, artifact 위치를 기록한다.
- `make verify`/`make test-plugin`은 exit propagation이 수정되기 전 evidence-only다.

## 3. 구성요소별 gate matrix

`R`은 필수, `C`는 변경 내용에 따라 조건부, `—`는 보통 비적용이다.

| 변경 표면 | G0 | G1 | G2 | G3 | G4 | G5 | G6 | G7 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `CLAUDE_SC.md`, core kernel | R | R | R | C | R | R | R | R |
| `core/rules` | R | R | R | C | C | R | C | R |
| agent | R | R | R | C | C | R | C | R |
| command | R | R | R | C | C | R | C | R |
| mode | R | R | R | C | C | R | C | R |
| MCP doc | R | R | R | C | C | C | C | R |
| skill | R | R | R | R | R | R | R | R |
| hook/safety script | R | R | R | R | R | R | R | R |
| CLI/install/utils | R | R | R | R | R | C | R | R |
| template | R | R | R | R | R | C | R | R |
| pytest plugin | R | R | C | R | R | — | R | R |
| source README/guide | R | C | C | — | — | — | C | C |

## 4. 타입별 정확한 narrow commands

| 타입 | 명령 |
|---|---|
| agent | `uv run pytest tests/unit/test_agent_structure.py -v` |
| command | `uv run pytest tests/unit/test_command_structure.py -v` |
| skill | `uv run pytest tests/unit/test_skill_structure.py -v` |
| mode | `uv run pytest tests/unit/test_mode_structure.py -v` |
| MCP/mode common | `uv run pytest tests/unit/test_content_structure.py -v` |
| cross refs | `uv run pytest tests/unit/test_cross_references.py -v` |
| context delivery | `uv run pytest tests/unit/test_content_usage.py tests/unit/test_context_loader.py -v` |
| hooks | `uv run pytest tests/unit/test_hooks.py tests/unit/test_safety_hooks.py -v` |
| runtime paths | `uv run pytest tests/unit/test_scope_paths.py -v` |
| install | `uv run pytest tests/unit/test_cli_install.py tests/unit/test_install_settings.py -v` |
| template | `uv run pytest tests/unit/test_init_docs_scaffold.py -v` |
| drift | `uv run pytest tests/unit/test_verify_drift.py -v` |
| eval schema | `uv run pytest tests/unit/test_eval_harness.py -v` |
| package metadata | `uv run pytest tests/unit/test_version_consistency.py -v` |
| OKF/plugin delivery | tracked inventory parity + `make build-plugin` clean artifact check |

## 5. Gate evidence schema

```yaml
gate_id: G#
status: passed|failed|not-run|not-applicable
applies_because: 변경 경로/행동
command: 실제 실행한 명령 또는 review 절차
exit_code: 숫자 또는 null
result: pass/fail 수, diff, artifact 등
evidence_path: 로그/리포트/fixture
failure_class: SPEC|CONTEXT|MODEL|TOOL|TASK|EVAL|DIST|null
residual_risk: 남은 불확실성
waiver:
  owner: null
  reason: null
  expires: null
```

## 6. Release record 최소 형식

```markdown
## Change
- Intent:
- Component/delivery path:
- Observed failure:
- Hypothesis:

## Hard gates
| Gate | Status | Evidence |
|---|---|---|

## Behavioral delta
| Slice | Baseline | Candidate | Verdict |
|---|---:|---:|---|

## Soft metrics
- Tokens:
- Tool calls:
- Latency:
- Diff scope:

## Residual risk
- NOT RUN:
- Unknowns:
- Rollback trigger:
```
