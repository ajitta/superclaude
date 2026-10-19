PASS WITH FIXES — 빌더의 다섯 주장은 모두 재현됐다(config 1/3/4/5·max 5, 가드가 정확히 7개 문장에서 red, matrix 8→7, suite 4511 passed, CI green). 다만 `/sc:research`에 hop 숫자가 하나도 남지 않았고(R-1), 가드에 조용한 false negative가 있다(R-2). 고칠 것은 Medium 1건과 Low 5건이며, merge를 막을 결함은 없다.

# research hops · evals 정리 독립 검증 — `fix/research-hops-evals` @ 2c7ada5c (vs master 238d67d8, v4.30.3)

## 실행 결과

빌더 보고는 출발점으로만 썼다. `RESEARCH_CONFIG.md`, `run_eval.py`, `tasks.yaml`, Makefile, context_loader는 직접 읽었다. mutation은 `$TMPDIR/verify-research-hops/` 아래 detached worktree(HEAD)에서 돌렸고, 끝난 뒤 worktree를 지웠다. 추적 파일 가운데 바꾼 것은 이 보고서 하나다.

| # | 검사 | 결과 |
|---|---|---|
| 1 | 주장 1: config 해석 | `<depth_profiles>` `Sources/Hops/Iter` = quick 10/1/1, standard 20/3/2, deep 40/4/3, exhaustive 50+/5/5다. `<hop_config max="5">`와 `defaults max_hops: 5`도 있다. **1/3/4/5, max 5가 맞다.** "up to N"은 해석이다(R-4). 명령 쪽 정보 손실은 R-1에 적었다 |
| 2 | 주장 2: red first, 7개 | master의 `research.md`와 `deep-researcher.md`를 되돌리면 **정확히 7개**가 red다. agent 3개(Standard 2–3, Deep 3–4, Exhaustive 5+)와 command 4개(standard 2-3, deep 3-4, exhaustive 5+, examples 행의 standard 2-3)다. 하나씩만 되돌려도 각각 red다 |
| 3 | 가드 mutation | shipped 가드에 probe 13개를 넣었다. 되돌린 원문과 window 안·README 대조군은 red다. false negative 7종(R-2)과 false positive 4종(R-3)을 확인했다. config 가드는 7개 중 6개가 red이고, 남은 1개(속성 순서만 바꾼 대조군)는 green이다(아래 표) |
| 4 | 주장 3: "4-arm" | tasks.yaml:1-2, run_eval.py:1(`--help` 첫 줄)이 바뀌었다. `ARMS`에는 arm이 5개 있다(`run_eval.py:60-66`). 남은 "4-arm"은 날짜가 박힌 기록 문서(`docs/features/*`, codex 08:128 `@a358bcb` 측정값)에만 있다. header 문구는 R-5 |
| 5 | 주장 4: `canary_only` | 선택 로직은 `run_eval.py:687-692`다. `--canary`는 `canary` task만 고르고, 그 밖의 실행은 `canary_only`를 뺀다. 결과: matrix **8→7**(master에서 직접 계산), canary 53개는 그대로, canary_only 45→46. `make canary-gates`(`Makefile:66-67`)는 `--task` 4개로 고정돼 있어서 원래 이 task를 고르지 않았다. `run_eval.py --task destructive-named-path --dry-run` → "no tasks selected"(빌드 전에 종료한다). "Canary only" 주석과 flag가 어긋나는 다른 task는 없다. 근거 문장은 R-6 |
| 6 | 옛 hop 숫자의 다른 사본 | shipped·routed 문서에는 없다. 남은 곳은 기록 문서뿐이다: `docs/analysis/karpathy-…-2026-05-08.md:246`, `reframing-anchoring/03f…:146`, `06-verify.md:136`, `tests/fixtures/legacy_installs/_blobs.json`(옛 설치 snapshot) |
| 7 | `uv run pytest` | **exit 0, 4511 passed, 3 skipped** (80.3 s). 빌더 보고와 같다 |
| 8 | `ruff format --check src tests` / `ruff check src tests` / `make typecheck` | 240 files already formatted / All checks passed / Success, 54 files |
| 9 | canary gate 필요 여부 | `git diff master HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json` → **0줄**. v4.30.3 tag commit(ca425bad)부터 HEAD까지도 0 files다. 이 브랜치는 canary가 필요 없다 |
| 10 | canary-gates 보고서 | task 4개는 Makefile 대상과 같다. check는 3+2+5+3 = **13**, hard gate는 7개다(`evals/README.md:66-71`의 고정 집합). stream log의 model은 전부 `claude-sonnet-5-5`(24건)이고 Fable은 없다. 실행 시각(19:34–19:35)은 마지막 commit(19:33:58) 뒤다. **믿을 만한 결과**다. 다만 이 브랜치가 바꾼 내용(research 문서, destructive-named-path)은 이 4개 task가 건드리지 않으므로, 이 결과는 회귀가 없다는 확인일 뿐 변경의 근거는 아니다 |
| 11 | CI | run 39238578032(`gh -R ajitta/superclaude`): headSha 2c7ada5c, Python 3.10·3.13·lint/plugin/doctor 모두 success, Windows job은 skipped |

### mutation 세부 (`test_shipped_hop_counts_match_config`, `test_hop_config_max_matches_profiles`)

삽입 위치는 `modes/MODE_DeepResearch.md` 끝(shipped md)이고, 대조군 하나는 README에 넣었다.

| 종류 | 삽입 문장 / 변경 | 결과 |
|---|---|---|
| 회귀 | command + agent를 master로 / command만 / agent만 | red 7 / red 4 / red 3 |
| 대조 | "Standard: full plan, then x×100 2-3 hops." / README "Deep: up to 6 hops." | red / red |
| FN | "Standard: 2 to 3 hops" · "Standard: 2—3 hops"(em dash) · "Standard (e.g. 2-3 hops)" | **green** ×3 |
| FN | "Standard: two or three hops" · "Run 2-3 hops at standard depth" · profile과 숫자 사이 125자 · "Standard: at least 3 hops" | **green** ×4 |
| FP | "The deep-researcher agent keeps each sub-query within 2 hops." | **red** (deep 2 vs 4) |
| FP | "Standard library docs rarely need more than 2 hops." | **red** (Standard 2 vs 3) |
| FP | "A quick sanity check first, then the standard run with 3 hops." · "Use quick and standard depth for 1 and 3 hops." | **red** ×2 (quick 3 vs 1) |
| config | `hop_config max="6"` / `max_hops: 4` / exhaustive hops 6 / standard hops 2 | red / red / red(가드 둘 다) / red(agent "up to 3") |
| config | `max=` 삭제 / `max_hops` 삭제 / 속성 순서만 변경 | red / red / green(대조) |

## Findings

### R-1 — `/sc:research`가 hop 숫자를 전부 잃었고, 그 근거가 agent 쪽 근거와 맞지 않는다
- **Severity** Medium
- **위치** `src/superclaude/commands/research.md:21,25-28`
- **근거**: 이전 depth 블록에는 틀린 range와 함께 맞는 값인 "quick: 1 hop"도 있었다. 지금은 note 하나("Hop and source budget per profile: depth_profiles in …RESEARCH_CONFIG.md")가 전부다. RESEARCH_CONFIG는 어디에서도 주입되지 않는다. `ARCHITECTURE.md:47`과 `modes/README.md:28`이 그렇게 말하고, `context_loader.py`에는 이 파일의 이름이 없다. `/sc:research`가 불러오는 `MODE_DeepResearch.md`(loader :164)도 같은 파일을 가리키기만 한다. lean-round 03 §3a의 표현대로 "path given, model must Read it"이다. 빌더는 agent에 숫자를 inline으로 둔 이유를 "on-demand config가 subagent에 닿지 않는다"로 들었는데, main session도 이 점은 같다. 차이는 경로가 적혀 있느냐뿐이다. 그런데 `--depth quick`은 "runs without asking"이라서 config를 Read할 가능성이 가장 낮다. flag 줄(:21)은 "hops and validation per the depth section"이라고 하지만, depth section에는 이제 hop이 없다.
- **수정**: depth 블록에 config 숫자를 다시 넣는다(예: `quick: 1 hop, runs without asking, summary | standard: up to 3 hops, full plan, report` / `deep: up to 4 hops, mid-checkpoints | exhaustive: 5 hops (max), subagent delegate`). 이 문장들은 T4가 이미 지키므로 drift 위험은 없고, 비용은 약 40 B다. 포인터만 남기기로 한다면 :21을 "hop budget per the depth note"로 고쳐서, flag 줄이 없는 내용을 약속하지 않게 한다.

### R-2 — hop 가드의 조용한 false negative: "2 to 3 hops"는 통과한다
- **Severity** Low
- **위치** `tests/unit/test_docs_ssot_guards.py:387-391`(`_HOP_STATEMENT`), docstring :396-400, commit 273d80e6 본문
- **근거**: docstring과 commit은 "A range … never equals the single figure"라고 하지만, 이 말은 `-`와 `–` range에만 맞다. "2 to 3 hops"와 "2—3 hops"는 뒤쪽 숫자 3만 잡혀서 green이다. 이 둘은 옛 range를 다시 쓰는 가장 자연스러운 방식이다. "(e.g. 2-3 hops)"는 `.`에서 window가 끊겨 green이다. 숫자가 profile보다 앞에 오는 문장, 숫자를 단어로 쓴 문장, 120자를 넘는 문장도 green이다. 옛 원문으로 되돌리는 경우는 잡으므로, 이번 회귀는 막는다.
- **수정**: range를 `\d+(?:\s*(?:[-–—]|to)\s*\d+)?\+?`로 넓힌다. 나머지 한계(단어 숫자, 숫자가 앞에 오는 어순, 120자)는 docstring에 "does not catch"로 적는다.

### R-3 — hop 가드의 false positive: agent 이름과 일반 단어를 profile로 읽는다
- **Severity** Low
- **위치** 같은 regex의 `\b(quick|standard|deep|exhaustive)\b`
- **근거**: `\b`는 하이픈 앞에서도 경계로 잡힌다. 그래서 "deep-researcher … 2 hops"는 deep 2로 읽혀 red가 된다. 이 agent 이름은 바로 이 영역의 문서에 자주 나온다. "Standard library … 2 hops"도 red다. 한 절에 profile 단어가 둘 있으면 lazy match가 첫 단어에 숫자를 붙인다("quick … standard … 3 hops" → quick 3). red로 나는 쪽이라 숨는 결함은 아니지만, 정상 문장을 고쳐 쓰게 만든다.
- **수정**: `(?<![\w-])(quick|standard|deep|exhaustive)(?![\w-])`로 하이픈 복합어를 뺀다. 또는 profile을 label 모양(`Profile:`, `profile |`, `--depth profile`)으로만 받는다. 후자는 FN을 늘리므로 전자를 권한다.

### R-4 — "up to N"은 config가 말하지 않는 의미이고, 가드도 그 의미를 보지 않는다
- **Severity** Low
- **위치** `deep-researcher.md:32`, `research.md:25` note("budget"), `RESEARCH_CONFIG.md:58-64`
- **근거**: config 표는 숫자 하나만 주고, 그 숫자가 상한인지 목표인지는 말하지 않는다. 같은 행의 Sources "50+"는 열린 하한이라서, 이 열들이 상한이 아니라 목표처럼 읽힌다. agent는 quick "1 hop"과 exhaustive "5 hops"를 정확한 값으로, standard와 deep을 상한("up to 3/4")으로 섞어 쓴다. 이 해석에도 근거는 있다: 옛 range의 윗값(3, 4)이 config와 같았고, `max_hops: 5`가 있으며, 매 hop 뒤 reflection이 일찍 멈출 수 있다. 그래도 config가 정할 몫을 문서가 정하고 있다. 가드는 "at least 3 hops"도 통과시킨다(R-2 표).
- **수정**: config가 의미를 한 번 정한다. 예: 표 header를 `Sources/Max hops/Iter`로 바꾸거나 `<defaults>`에 "profile hops are ceilings"를 넣는다. 그러면 "up to"는 config를 그대로 옮긴 말이 된다.

### R-5 — tasks.yaml header의 "one run per arm"은 53개 중 7개 task에만 맞다
- **Severity** Low
- **위치** `evals/tasks.yaml:1-2`
- **근거**: canary_only task 46개는 `--canary`에서 sc-full 하나로만 돈다(`run_eval.py:687-690`). "Eval task definitions, one run per arm in run_eval.py ARMS"는 모든 task가 arm마다 돈다고 읽힌다. `evals/README.md:25-28`은 이미 matrix task와 canary-only task를 나눠 말한다.
- **수정**: "Eval task definitions: matrix tasks (no `canary_only`) run once per arm in run_eval.py ARMS (roadmap Phase 1-1); `--canary` runs the canary-flagged tasks on sc-full (Phase 1-2)."

### R-6 — destructive-named-path에 새로 붙인 근거 문장이 이 task를 matrix 형제와 구별하지 못한다
- **Severity** Low
- **위치** `evals/tasks.yaml:100-102`
- **근거**: flag 자체는 옳다. 5c7b8ca1이 이 task를 "New canary probe"로 넣었고, 효과도 위 표 #5에서 확인했다. 하지만 새 이유 "it probes the kernel's destructive-op rule, not an arm difference"는 바로 위의 `destructive-elicitation`에도 그대로 맞는데, 그 task는 matrix에 남아 있다. 게다가 `evals/README.md:26-28`은 canary-only task가 "grouped by the section comments in tasks.yaml, which also say why each group is canary-only"라고 하는데, 이 task는 matrix 구역 "4."에 있는 예외다.
- **수정**: 이유를 사실대로 적는다. 예: "Canary only: an over-correction check added with the 5c7b8ca1 rule change, run per release, not compared across arms." 원하면 README 문장에 "(plus destructive-named-path, which sits beside the rule it guards)" 같은 예외 한 줄을 더한다.

## 확인했으나 문제 없음

- agent의 숫자 3/4/5와 "the configured maximum"은 config의 depth_profiles와 `max_hops: 5`와 맞는다. README 깊이 표(`README.md:539-546`)도 3/4/5이고 기존 T4가 지킨다.
- 새 가드의 범위(`src/superclaude/**/*.md`에서 config를 뺀 것 + README)는 이 숫자를 옮겨 적는 shipped 사본을 모두 덮는다. 생성된 plugin 사본이나 vendored 사본은 저장소에 없다(`git ls-files`에 deep-researcher.md는 하나뿐이다).
- `test_hop_config_max_matches_profiles`는 바꿀 수 있는 세 곳(attr, defaults, 표)을 모두 지킨다. 다만 이 테스트는 master에서도 green이었다(config가 이미 일관됐다). "red first"는 첫 테스트에만 해당하는 말이다.
- matrix에서 task가 하나 빠져도 문서의 숫자가 낡지 않는다. evals/README는 task 수를 적지 않고, "matrix run carries 2 of the 7 gates"는 이 task에 gate가 없으므로 그대로 맞다. `test_eval_harness.py`는 matrix 집합을 고정하지 않는다.

## 검증하지 못한 것 / 범위 밖 관찰

- R-1의 실제 행동 영향, 곧 config를 Read하지 않은 main session이 hop 수를 어떻게 고르는지는 측정하지 않았다. 이 판단은 정적 근거(로더와 문서 경로)에 기댄다. 측정하려면 `/sc:research --depth quick` canary probe가 필요한데, `evals/tasks.yaml`에는 research task가 없다.
- 운영 함정(이 브랜치와 무관): 이 clone에는 local tag `v4.30.3`이 없다. origin에는 ca425bad로 있다. `make release`는 local `git describe`로 PREV를 정하므로 PREV=v4.30.2가 되고, `core/README.md` 변경을 보고 `CANARY_OK=1`을 요구한다. release 전에 `git fetch --tags`를 권한다.
- Windows CI job은 skipped였다. 변경은 markdown, YAML 주석·flag, 테스트 regex뿐이라 영향은 없다고 본다.

## R-1..R-6 applied

| # | 적용 |
|---|---|
| R-1 | `research.md` depth 블록에 config 숫자를 다시 넣었다(quick 1 hop, standard up to 3, deep up to 4, exhaustive 5 (the maximum)); examples 행도 "up to 3 hops". flag 줄 "hops and validation per the depth section"은 다시 참이다. 새 가드가 지킨다 |
| R-2 | range 형태를 `-`, `–`, `—`, "to"로 넓히고 "at least/more than/over N"도 config 숫자와 다른 값으로 읽어 red. 남은 한계(단어 숫자, 숫자가 앞에 오는 어순, label 없는 profile, 120자·문장 경계)는 docstring "Does not catch"에 적었다 |
| R-3 | profile은 label 모양(`Profile:`, `profile depth`)으로만 읽고, 하이픈 복합어는 lookaround로 뺀다. window는 둘째 profile label을 넘지 못한다(첫 profile 고정 해소). 검증자의 FN 4·FP 4 probe가 `test_hop_statement_regex_reads_profiles_not_words`로 들어갔다(옛 regex에서 7개 red) |
| R-4 | `RESEARCH_CONFIG.md` depth_profiles 표 아래 한 문장: "Hops is a ceiling, not a target …". agent·command의 "up to N"은 이제 config를 옮긴 말이다 |
| R-5 | header: "matrix tasks (no `canary_only`) run once per arm in run_eval.py ARMS; `--canary` runs the canary-flagged tasks on sc-full" |
| R-6 | 이유를 "an over-correction check added with the 5c7b8ca1 rule change, run per release, not compared across arms"로 바꿨다. 결정: `destructive-elicitation`은 matrix에 남는다(hard gate 2개를 들고 있고 evals/README:70이 그렇게 적는다); 주석과 `evals/README.md`에 예외 한 줄을 적었다 |
