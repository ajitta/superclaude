---
feature: agent-roster-audit
phase: verify
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
---

# 02. 독립 검증 — agent roster audit (`0f1608ab` vs master `f467012c`)

판정: PASS-with-fixes

업그레이드 경로(C3), 테스트·린트·타입(C7), pm_context(C4)는 재현됐다. 은퇴 이름이 `src/`에 남지 않은 것(C1)도 확인했다. 고칠 것은 문서와 명령의 정합성이다. 그리고 근거 하나("서브에이전트는 다른 서브에이전트를 띄울 수 없다")가 현재 Claude Code 문서와 맞지 않는다. critical·high 결함은 없다.

## Findings

### 1. [medium] "서브에이전트는 다른 에이전트를 띄울 수 없다"는 근거가 현재 문서와 어긋난다

- 증거: code.claude.com/docs/en/sub-agents (2026-10-20, `curl …/sub-agents.md`):
  - 1051행: "By default, a subagent can spawn subagents of its own, up to three layers below the main conversation."
  - 524행: "In a subagent definition, listing `Agent` in `tools` lets that subagent spawn subagents of its own while the depth limit allows it"
- 이 주장이 쓰인 곳:
  - `.claude/rules/agent-authoring.md:178`: "a subagent cannot spawn or hand work to another agent"
  - `src/superclaude/agents/README.md` Escalation 절: "a subagent cannot spawn another subagent"
  - `00-intent.md` Evidence 절: "A subagent cannot spawn another one, so in that position the instruction could never run."
- 같은 트리 안에서도 모순이다. `self-review.md:6`은 `tools: Read, Grep, Glob, Agent`이고, `deep-researcher`와 `business-panel-experts`는 `disallowedTools: NotebookEdit`라 Agent를 상속한다. 또 README는 self-review를 "read-only tools"라고 부르지만, Agent 도구로 편집 권한이 있는 `general-purpose`를 띄울 수 있다.
- 결론에는 영향이 없다. sibling escalation 제거는 sibling이 은퇴했으니 맞다. 틀린 것은 근거 문장이고, 이 문장이 작성 규칙으로 굳어진다는 점이 문제다.
- 수정 제안:
  - 세 곳의 근거를 바꾼다. 예: "형제 에이전트로 넘기지 않는다: 열린 항목은 메인 세션이 결정한다(중첩 spawn은 가능하나 의도적으로 쓰지 않는다)".
  - self-review의 `Agent` 도구는 유지 여부를 정하고, read-only를 주장하려면 제거한다.

### 2. [medium] 남은 명령들이 여전히 '도메인/전문가 에이전트'로 라우팅한다고 약속한다

소유자 결정은 "focuses become lenses"였다. 아래 위치는 존재하지 않는 대상을 가리킨다.

- `src/superclaude/commands/improve.md:14` "Plan: Pick approach + delegate to relevant agent". `--type performance|quality`에 대응하던 에이전트가 없다.
- `src/superclaude/commands/roadmap.md:15` "Consult: Domain agents may be consulted for analysis"
- `src/superclaude/commands/task.md:17` "delegate where a specialist fits"
- `task.md:2`와 `agent.md:2`의 gate "specialist waves — /sc:pm". `/sc:pm`은 이제 `general-purpose` 스트림이다.
- `src/superclaude/commands/brainstorm.md:14` "multi-agent coordination with domain expertise"
- `src/superclaude/commands/README.md:89` "`agents/` — Domain expert agents commands route to"
- `src/superclaude/modes/README.md:52` "`agents/` — Domain expert agents (modes shape mindset, agents shape expertise)"
- `src/superclaude/ARCHITECTURE.md:67` "They route to agents"(경미)

재현: `grep -rnE -i 'domain agent|specialist|relevant agent|Domain expert' src/superclaude --include=*.md`

수정 제안:
- `/sc:analyze`의 `<focus_delegation>`처럼 "독립 스트림이면 스트림마다 `general-purpose` 하나, 도메인 체크는 프롬프트에"로 통일한다.
- 두 README의 agents/ 한 줄을 "isolated workers"로 바꾼다.
- `description` 변경은 `test_description_overlap` 대상이니 해당 테스트를 다시 돌린다.

### 3. [medium] `<finding_policy>`가 `/sc:analyze` 메인 세션 경로에는 없다

- master에서는 `security-engineer.md:37`과 `quality-engineer.md:37`이 coverage-over-filtering 규칙과 severity/confidence 필드를 가졌다. `/sc:analyze --focus security|quality`가 "specialist depth"일 때 이들에 위임했다.
- 지금은 `analyze.md` `<focus_delegation>`이 이 규칙을 다중 focus의 delegate 프롬프트에만 넣는다. 메인 세션에서 도는 단일 focus 경로에는 규칙이 없다.
- `/sc:review`의 `<review_lens>`는 `--structured` 리뷰어에 lens만 넘기고 finding 규칙은 넘기지 않는다. `self-review`가 그 리뷰어라는 명시도 없다.
- 척도도 둘이다. `analyze.md` flow 3은 🔴🟡🟢를 쓰고, `<focus_delegation>`은 critical…nit를 쓴다.
- 01-carry-over 표는 "`/sc:analyze` `<focus_delegation>` puts the same rule in each per-focus delegate's prompt"라고만 적었다. 단일 focus 손실은 기록되지 않았다.
- 수정 제안:
  - Scan/Evaluate 단계에 경로와 무관하게 한 줄을 둔다: "Scan은 모든 finding을 severity·confidence와 함께 수집하고 Evaluate가 순위를 매긴다".
  - 척도 하나를 정한다.

### 4. [medium] insight-analyst의 의미 검색과 annotation 확인 절차가 옮겨지지 않았다

- master의 `insight-analyst.md`에는 다음이 있었다:
  - description의 "wants a semantic search across insights, or wants annotation links"
  - actions 3: semantic-relevance judgment
  - actions 5: "After the user confirms, append `annotation` entries"
  - gotchas: orphaned-ref-ts, stats-inflation, tz-mismatch
- 현재 `commands/insight.md`의 상태:
  - `--query`는 `key=value` 필터뿐이다(10·24·34행).
  - Mode 목록(13행)에 annotation 모드가 없다.
  - annotation은 Dedup 단계의 "also check existing ref_ts" 한 줄뿐이다.
- 그런데 `deep-researcher.md:3`은 "past project insights"를 `/sc:insight --query`로 보내고, `README.md`는 "`--list` and `--query` read later"라고 쓴다. "what did we learn about X?" 같은 자연어 질문은 key=value로 받을 수 없다.
- 01-carry-over의 "covers query and annotation"은 과장이다.
- 수정 제안: `insight.md` Read modes에 다음을 추가한다.
  - "주제 질문: `--list`/`--query`로 좁힌 뒤 메인 세션이 관련성을 판단해 근거와 함께 제시"
  - "annotation: 링크별로 ref_ts와 대상 문장을 보여 주고 승인된 것만 append(ts 오프셋 형식 일치)"

### 5. [low] security-engineer의 저장소 고유 위협 모델 gotcha가 유실됐다

- master `security-engineer.md` `<gotchas>`:
  - `sc-not-webapp`: 이 저장소에서는 웹 취약점 스캔 대신 XML/markdown 프롬프트 인젝션, install 경로 traversal, hook 명령 인젝션을 본다.
  - `sc-installer-writes`: `~/.claude` 쓰기는 의도된 동작이다.
- 현재 트리에는 없다: `grep -rnE 'sc-not-webapp|installer writes|hook command injection' src .claude/rules`의 결과가 0이다.
- 모델이 원래 아는 지식이 아니라 이 저장소에 대한 사실이다. carry-over 표에도 없다.
- 수정 제안: `.claude/rules/gotchas/general.md`(또는 `paths:` 도메인 파일)에 한 줄로 옮긴다.

### 6. [low] `agent-authoring.md` Symbolic-First 표가 은퇴 에이전트 17개를 예시로 든다

- `.claude/rules/agent-authoring.md:225-227`: "system/backend/frontend architects, python-expert, quality/performance/security engineers, refactoring-expert, root-cause-analyst …", "devops-architect, requirements-analyst, project-manager …", "git-workflow, insight-analyst, simplicity-guide".
- 결정 게이트를 고친 바로 그 파일이다.
- 수정 제안: 다섯 에이전트로만 다시 분류한다. Full은 repo-index와 self-review, Skip은 business-panel-experts, deep-researcher, verifier다.

### 7. [low] 일반 `install`만 하면 남은 5개 에이전트가 은퇴 에이전트를 계속 가리킨다

- 재현 경로: scratch `CLAUDE_CONFIG_DIR`에서 user scope로 master를 설치한 뒤, 브랜치에서 `uv run superclaude install --scope user`(non-force)를 실행했다.
- 결과:
  - 출력: "Agent definitions: 5 skipped", "13 installed file(s) differ … Run 'superclaude update'".
  - `grep -lE 'requirements-analyst|system-architect|quality-engineer' agents/*.md`가 5개 파일 모두를 반환했다. fallback은 "escalate to requirements-analyst" 같은 문장이다.
  - `update` 후에는 0개다.
- 원인은 기존 설치기 동작이고, 안내 문구도 출력된다. 다만 이번 변경은 그 낡은 문장이 가리키는 대상이 사라지는 경우다.
- 수정 제안: CHANGELOG `[Unreleased]`의 Upgrade 항목에 "`superclaude update --scope <s>`로 남은 다섯 에이전트도 갱신"을 덧붙인다.

### 8. [low] 00-intent의 Anthropic 출처 표에 부정확한 행이 둘 있다

- 행 2(sub-agents): 내장 에이전트는 Explore, Plan, general-purpose 외에 statusline-setup과 claude-code-guide("Other" 탭)도 있다. 메인 대화 목록에 "Latency matters"가 빠졌다.
- 행 6(claude-plugins-official): "None is a language or role persona"는 너무 강하다. `code-modernization`의 `security-auditor`("You are an application security engineer…"), `test-engineer`, `architecture-critic`은 역할 이름에 "You are a …"로 시작한다. 다만 description은 job에 묶여 있다. `grader`는 `plugins/*/agents/`가 아니라 `plugins/skill-creator/skills/skill-creator/agents/`에 있다.
- 나머지 행 1·3·4·5와 output-styles(Learning, Explanatory)는 원문과 일치한다. 인용문도 그대로다.
- 수정 제안: 행 2는 "among others"로 바꾼다. 행 6은 "job으로 이름 짓고 워크플로에 묶임; 일부 code-modernization 에이전트는 역할 이름을 쓰지만 같은 워크플로에 묶임"으로 완화한다.

### 9. [low] C1을 지키는 테스트가 없고, 중복 trigger 테스트는 빈 입력으로 통과한다

- 은퇴 이름이 명령 본문에 다시 들어와도 막는 테스트가 없다. `test_cross_references.py`는 handoff 대상만 본다. C1은 이번에 grep으로만 확인됐다.
- `test_cross_references.py:92` `test_no_duplicate_triggers`는 `triggers -` 축약형을 쓰는 에이전트가 0개라서 항상 통과한다. 이 문제는 이번 변경 전부터 있었다.
- `test_agent_structure.py`와 `test_description_overlap.py`는 5개 에이전트에 대해 파일별로 parametrize되어 의미가 유지된다(5개 → agent 쌍 10개).
- 수정 제안:
  - `src/superclaude/**/*.md`에 `install_paths.RETIRED_AGENT_FILES`의 stem이 단어로 나오면 실패하는 테스트를 추가한다. `cli/install_paths.py`는 제외한다.
  - 죽은 trigger 테스트는 삭제하거나 description 기반으로 교체한다.

### 10. [nit] CHANGELOG와 README의 표현 두 군데

- CHANGELOG Removed는 `git-workflow`를 "a job that has to talk with the user"에 넣었다. 00-intent의 사유는 "no isolation need"다.
- `README.md`의 "Domain knowledge (security, performance, architecture, Python) lives in commands and rules": Python 지식은 어디에도 옮겨지지 않았다(모델 지식). "lives in the model, with checks in commands and rules" 정도로 고친다.

### 11. [info] 릴리스 전 확인 사항

- Canary가 필요하다. 마지막 태그 이후 core/hooks.json 변경은 다음 한 건이다.

  ```
  git diff --stat v4.31.1 HEAD -- src/superclaude/core src/superclaude/hooks/hooks.json
  → src/superclaude/core/rules/RULES_QUALITY.md | 2 +-
  ```

  `<thresholds>` 한 문장으로, "backend-architect uses '>2 tables'"가 "a schema change uses '>2 tables'"로 바뀌었다. hooks.json 변경은 없다. 따라서 `make release` 전에 `make canary-gates`를 실행하고(세션 안이면 `EVAL_ARGS="--runs-dir <~/.claude 밖 새 디렉터리>"`), 보고서를 읽은 뒤 `CANARY_OK=1`을 준다.
- `pyproject.toml`은 아직 `version = "4.31.1"`이다. 00-intent 결정 4("release a minor version")에 따라 version-bump 브랜치가 필요하다.
- 원격 상태:
  - `gh repo set-default --view` → `ajitta/superclaude`
  - `v4.31.1` 태그는 origin에 있다.
  - master의 마지막 Tests 워크플로는 2026-10-19 success였다.
  - 브랜치는 `origin/feature/agent-roster-audit`에 push되어 있다.
- 릴리스를 막는 외부 문제는 보지 못했다.

## C1–C7

| 주장 | 결과 | 증거 |
|---|---|---|
| C1 은퇴 이름이 shipped content에 없음 | 재현 | `grep -rlE '<19개 이름>' src/superclaude` → `cli/install_paths.py`만 나옴(디지스트 표). 테스트 가드는 없음(#9). 다만 은퇴 대상을 가리키는 일반 표현("Domain agents", "relevant agent")이 남음(#2) |
| C2 의존 내용이 다른 곳에 있거나 옮겨짐 | 부분 재현 | 확인됨: project-initializer→`/sc:init`, git-workflow→`/sc:git`, root-cause-analyst→`troubleshoot.md` 3-cycle, simplicity-guide→`RULES_QUALITY.md` `<anti_over_engineering>`, learning/socratic→output styles(공식 문서 확인), `self-review.md:36` finding_policy 원문. 미흡: 메인 세션 finding_policy(#3), insight 의미 검색과 annotation 확인(#4), 보안 위협 모델 gotcha(#5) |
| C3 업그레이드 안전성 | 재현 | **변이 검사**: `python-expert.md`의 디지스트 `0449792ef23d8a8c` 하나를 지우자 `pytest … -k q10` → `1 failed` (`Extra items in the right set: '0449792ef23d8a8c'`). `git checkout --` 후 `git status` 깨끗. **생성기**: HEAD의 detached worktree에서 `scripts/gen_shipped_names.py`를 다시 돌렸더니 차이는 `generated_from`과 남은 5개의 `last`(d3bfded8→0f1608ab)뿐이고 디지스트는 같음. **실제 업그레이드(user)**: master `.venv`로 설치(에이전트 24개, `memory: user`) → `my-agent.md`, 편집한 `performance-engineer.md`, 같은 이름의 내 `socratic-mentor.md`, `agent-memory/python-expert/MEMORY.md`, CRLF로 바꾼 `learning-guide.md`를 둠 → 브랜치 install → 제거 16+1(CRLF 포함), 사용자 파일 3개와 agent-memory는 남음 → `update` → `uninstall -y` 후 `my-agent.md`, `performance-engineer.md`, `socratic-mentor.md`, `agent-memory/python-expert/MEMORY.md`만 남음. **project/local**: scratch git repo에서 master install → 브랜치 `install --force` → 각각 "Removed 18", 편집한 `quality-engineer.md`, `my-agent.md`, `agent-memory/root-cause-analyst` 유지 → uninstall 후에도 유지. `memory: local` 되돌리기도 확인. 실제 `~/.claude`는 변경 없음 |
| C4 pm_context 제거로 잃는 것 없음 | 재현 | master `git grep pm_context -- src` → writer는 `agents/project-manager.md:22,73`(main-session lifecycle)뿐, 읽는 곳은 `load.md:13`뿐. `save.md`는 쓰지 않음. 기존 파일은 디스크에 남음. 참고: `claude --agent project-manager` 사용자는 session start/end 자동 처리를 잃음(`/sc:load`, `/sc:save`로 수동 대체). CHANGELOG에 pm_context 항목은 있음 |
| C5 CHANGELOG/README/ARCHITECTURE/agents README/작성 규칙 정합 | 부분 재현 | 개수 24→5, 표, 결정 게이트 갱신은 맞음. 미흡: #1(잘못된 근거), #2(명령·README 잔존), #6(authoring 표), #7(업그레이드 안내), #10 |
| C6 Anthropic 출처 인용 | 부분 재현 | 행 1·3·4·5와 output-styles는 원문 일치(Skills 블로그 2026-01-22, "Too many specialist agents…", "'Reviews code for security issues before commits' routes better than 'security expert.'", Opus 5 "delegates to subagents more readily…", "focuses Claude's behavior and tone"). 행 2·6 부정확(#8). 같은 문서가 중첩 spawn을 허용함(#1) |
| C7 pytest, lint, typecheck, format | 재현 | `uv run pytest` → `3752 passed, 3 skipped in 78.65s`, EXIT 0(skip 사유는 확인하지 않음). `make lint` → All checks passed. `make typecheck` → `Success: no issues found in 54 source files`. `ruff format --check src tests` → `222 files already formatted`. `ruff check src tests` 통과 |

검증 환경: scratch는 `/home/ubuntu/.hermes/profiles/superclaude/cache/scratch/verify-roster/`(cfg-user, cfg-project, cfg-local, proj-project, proj-local)이다. 쓴 worktree 두 개(wt-master, wt-head)는 `git worktree remove --force`로 지웠다. 저장소 `git status`는 이 보고서를 빼면 깨끗하다.
