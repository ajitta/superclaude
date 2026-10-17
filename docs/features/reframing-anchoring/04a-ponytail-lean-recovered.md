---
feature: reframing-anchoring
phase: input
owner: ajitta
created: 2026-10-17
updated: 2026-10-17
---

# 04a. ponytail-audit (lean only) — recovered report, 2026-10-17 00:35

Source: Hermes session `20261017_003505_fbbe88` ("ponytail 스킬로 프로젝트 감사"), final assistant message, recovered verbatim from the Hermes session store on 2026-10-17. Base: `master` `7a6f771f` (4.27.2). Four sub-agents audited cli / hook scripts + utils / eval tooling / packaging + CI + tests for over-engineering only (no bug, security, load, test or speed axis). Items the 2026-10-03 audit decided to keep were excluded by the auditor.

Status: **unverified input** for Phase 3 of the reframing-anchoring plan. No file was changed by the audit. Every item below is re-checked with a whole-tree grep in `04-ponytail-audit.md` before any cut.

---


ponytail-audit로 감사한 결과, 줄일 수 있는 분량은 **약 −5,100줄로 추정되고 의존성은 1개(pytest-cov)**입니다. 이 가운데 약 3,400줄은 오래된 문서와 지난 실험 산출물이고, 코드는 약 1,100줄, 테스트는 약 600줄입니다.

- **기준:** `master` HEAD `7a6f771f` (4.27.2). 영역 4개를 서브에이전트가 나눠 감사했고, 각 발견은 저장소 전체 `git grep` 근거를 붙인 뒤 스스로 한 번 반박해 봤습니다.
- **재검증:** 큰 항목은 제가 직접 grep으로 다시 확인했습니다.
- **제외한 것:** 10-03 감사에서 유지하기로 결정한 항목은 다시 올리지 않았습니다. 파일은 하나도 수정하지 않았습니다.

## 큰 항목 (줄이는 폭 순)

| # | 태그 | 대상 → 대체 | 위치 | 추정 줄 수 |
|---|---|---|---|---|
| 1 | delete | 일회성 실험 폴더 (파일 41개). 다른 곳에서 참조 0건이고, `api_probe.py`는 선언되지 않은 `anthropic`을 import함 → 삭제하거나 `docs/archive/`로 이동 | `docs/experiments/sc-prompt-opus55-probe-2026-09-23/` | −2,627 ✅ |
| 2 | delete | `SECURITY.md` 757줄. 원본 저장소에서 물려받은 상투 문구이고, 현재 지원 버전을 "4.1.x"로 적고 있음 (실제는 4.27.2) → 비공개 신고 링크만 남긴 30줄 정도 | `SECURITY.md:158,724` | −720 ✅ |
| 3 | shrink | 테스트 함수 안 import 381개. 이 중 43개는 파일 상단 import와 중복이고 89개는 stdlib → 파일 상단으로 올림 | `test_cli_install.py`, `test_insight_writer.py` 등 | −250 |
| 4 | shrink | 리터럴 값만 다른 복붙 테스트 → `@pytest.mark.parametrize` | `test_install_settings.py:23-70`, `test_file_size_guard.py:58-110` 등 | −233 |
| 5 | yagni | parallel_ab의 6개 모듈은 한 줄로 이어지는 파이프라인이고 각 모듈의 호출처가 1곳씩 → 1개 모듈로 합침. 같이 걷어낼 것: obs JSON을 디스크에 썼다가 다시 읽어 `validate()`하는 왕복, runner가 채우지 않는 필드(`axes`, `files_touched`), stream-json만 요청하는데 남아 있는 `json`·`tools_used` 파싱 분기 | `src/superclaude/scripts/parallel_ab/` | −210 |
| 6 | yagni | `auto_improve/guards.py`의 `GuardVerdict`와 guard 클래스 4개. `.reason`은 테스트에서만 읽음 ✅ → bool 식 또는 함수 | `guards.py:20-114` | −70 |
| 7 | delete | `run_eval.py`가 따로 들고 있는 `_detect_refusal` 복사본과 이를 고정하는 테스트 ✅ → `superclaude.utils.detect_refusal` 사용 | `evals/run_eval.py:311-336` | −48 |
| 8 | shrink | `.github/workflows/README.md` 54줄 중 대부분이 AGENTS.md·Makefile과 중복 → 5~10줄 | | −44 |
| 9 | shrink | 훅 스크립트 7개가 각자 stdin을 읽어 JSON 파싱 → `utils.read_hook_input()` 하나 | `scripts/*.py` (`isatty()` 7건) | −30 |
| 10 | shrink | autouse `sandbox_home`이 있는데도 테스트마다 가짜 HOME을 직접 만듦 (29곳) → fixture를 이름으로 받아 쓰기 | `test_scope_paths.py` 등 | −40 |
| 11 | delete | `.gitignore` 중복 19개 ✅, 이미 무시되는 폴더의 하위 경로 4개, 제거된 black의 흔적 `.black/` | `.gitignore:183-208` 등 | −30 |
| 12 | delete | `pytest-cov`와 `[tool.coverage.*]`. CI·Makefile·테스트 어디서도 돌리지 않음 ✅ → 필요할 때 `uv run --with pytest-cov`로 실행 | `pyproject.toml:44,95-116` | −26, 의존성 −1 |
| 13 | shrink | 테스트 frontmatter 파서 7개 (그중 2개는 바이트 단위로 동일) → `md_helpers`에 통합 | | −30 |
| 14 | shrink | git repo를 만드는 fixture가 3벌 → conftest의 `git_repo` 하나 | | −30 |
| 15 | native | `_resolve_git_exclude_file`이 `.git` 포인터를 직접 파싱 → `git rev-parse --git-path info/exclude` | `install_git_exclude.py:189-242` | −40 |
| 16 | shrink | doctor와 install이 `probe_console_script()` 결과로 같은 세 가지를 따로 검사 → 공용 함수 하나 | `doctor.py:101-166`, `install_components.py:421-461` | −30 |
| 17 | delete | `make verify`: 다른 대상과 겹치는 19줄 배너 → `make test-plugin` + `make doctor` | `Makefile:70-88` | −21 |
| 18 | yagni | `insight_writer`의 `-from-hook` 분기가 argv를 다시 만들어 argparse로 되돌림 → `Namespace`를 직접 만들어 호출 | `insight_writer.py:839-907` | −20 |
| 19 | shrink | `insight_writer`의 자체 JSONL 읽기/쓰기 루프 3벌 → `_read_pending`과 `_write_jsonl` 하나 | | −20 |
| 20 | shrink | 줄 단위로 나열한 확장자·플래그 set 리터럴 → `frozenset("a b c".split())`. 줄 수만 주는 외형 정리 | `file_size_guard`, `test_runner_hook`, `context_loader` | −100 |

## 작은 항목 (각 −2~−20줄)

- **delete**
  - 테스트에서만 쓰는 함수: `_count_shipped_hooks`, `_count_registered_hooks` ✅ (`install_inventory.py:62-87`)
  - 빈 set이라 절대 실행되지 않는 분기: `MCP_DOCS_SKIP` ✅ (`install_components.py:46,216`)
  - 제거된 `target` scope의 흔적
  - 아무도 읽지 않는 결과 키: `source_path`, `passed`, `total_ok`
  - 쓰이지 않는 상수: `author_check.TYPES`, `FORMATS`
  - 늘 0인 `skipped` 반환값
  - 첫 원소가 항상 입력 prompt 그대로인 `resolve_flags`의 `(corrected, notes)` 튜플 ✅
  - PostToolUse 훅의 `stop_hook_active` 검사 ✅. 이 값은 Stop/SubagentStop 입력에만 있습니다.
  - `WorktreeManager.cleanup`, `init_results_tsv`
  - `make test`의 `-m "not canary"` ✅. canary marker가 등록돼 있지 않습니다.
  - CI가 `addopts`와 같은 옵션을 한 번 더 넘김
- **stdlib**
  - `line_of` → `bisect`
  - `verify_drift`의 개별 합계 → `Counter`
  - 손으로 짠 중복 제거 → `dict.fromkeys`
  - `_now_iso` → `isoformat(timespec="seconds")`
  - `check_claude_md_import`의 정규식 → `in`
  - `temp_dir` fixture → `tmp_path`
  - `importlib.spec_from_file_location` → 일반 import
- **native**
  - CI의 `curl | sh`로 uv 설치 + 확인 스텝 → `astral-sh/setup-uv`
- **yagni**
  - 호출처가 하나인 래퍼·파라미터: `_mask_secrets_in_args`, `max_age_days`, `verify_drift(verbose=)`, `roots=`·`search_bundled`, `RunnerCfg.cli`(허용값이 `claude -p` 하나뿐), `Mutator` 클래스, `status_mode(config)`
- **shrink**
  - `uninstall`이 `uninstall_all`을 두 번 호출
  - `session_init`과 `loop_guard`의 발생할 수 없는 except 분기와 반복되는 앞부분
  - `results_tsv._coerce`
  - `run_eval`의 `_run` 중복과 `_result_subtype` 재파싱
  - Makefile help 목록 → `##` 주석을 grep해서 자동 생성
  - 테스트의 경로 상수 18벌, `_all_output` 중복

## 검증하면서 뺀 것

- **`CLAUDE_CONTEXT_MAX_TOKENS` 제거 제안:** 지난 감사 계획(`05f-plan-b6:184`)에 "유지해야 함"으로 적혀 있어 뺐습니다.
- **훅의 `{"decision":"approve"}` 출력:** 지우면 권한 프롬프트 동작이 바뀝니다. 과잉 설계 문제가 아니라 동작·보안 결정이라 감사 범위 밖이고, 따로 검토할 일입니다.
- **eval 하네스 3개 통합:** 구조가 서로 달라서 기각했습니다. 실제로 중복된 건 7번 `detect_refusal` 하나입니다.
- **`evals/fixtures`와 tasks:** 고아 파일이 없습니다.
- **기존 결정과 겹쳐 뺀 것:** `uninstall_legacy.sh`, 문서화된 env 스위치, auto-improve CLI 플래그, `pytest-asyncio`.

## 손대지 않은 범위

- 마크다운 콘텐츠(commands·agents·modes)와 `.claude/rules/` 사이 중복은 보지 않았습니다.
- `tests/unit/scripts`의 깊은 부분과 eval 실행(`claude -p`)은 돌리지 않았습니다.

**net: 약 −5,100줄(추정), 의존성 −1 가능.**

지난 감사처럼 `docs/features/<slug>/`에 보고서를 남기고 배치별로 구현할 수 있습니다. 보고서만 남길지, 1·2·12·11번처럼 바로 지울 수 있는 것부터 브랜치에서 처리할지 정해 주세요.