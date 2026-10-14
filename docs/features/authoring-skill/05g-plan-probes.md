---
status: complete
revised: 2026-10-13
---

# Phase G: 효과·명시 호출 프로브

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C7 "효과", "명시 호출" 행. 리뷰 I5: 비교는 `sc-full` arm 안에서 평문 vs `/sc-author`.

전제:
- 로컬 `claude -p` (구독 OAuth, API 키 없음). Fable로 돌리지 않는다 (AGENTS.md: headless Fable은 사용 크레딧 과금)
- Claude Code 세션 안에서 실행하면 `--runs-dir`를 `~/.claude` 밖의 새 디렉터리로 (AGENTS.md Canary 항목)
- `run_eval.py:164`가 작업 공간마다 `superclaude install --force --scope project`를 돌리므로 C 이후 `sc-full` arm에는 스킬이 설치된다. 실행 전 `uv run python -c "import superclaude; print(superclaude.__file__)"`이 이 worktree를 가리키는지 확인 (gotcha `venv-inherited-by-worktree`)
- 픽스처는 저장소 밖 임시 작업 공간으로 복사된다 (gotcha `probe-observer-effect`)

### Task G1: 픽스처와 과제

**Files:** Create: `evals/fixtures/sc-author/README.md`, `evals/fixtures/sc-author/migrations/001_init.sql` | Modify: `evals/tasks.yaml` (`implement-checkpoint` 뒤)

- [x] Step 1: 픽스처: 작은 프로젝트 하나 (README에 "SQL migrations live in `migrations/`" 한 줄, SQL 파일 하나). `.claude/`는 넣지 않음 (arm이 설치)
- [x] Step 2: 과제 두 개. 둘 다 `canary: true`, `canary_only: true` (선례 `implement-checkpoint`: 기본 4-arm 행렬에서 빠지고 `--canary`에서 `sc-full`로만 돈다, `run_eval.py:669-674`)
  - 공통: `fixture: fixtures/sc-author`, 다른 과제와 같은 git `setup`, `allowed_tools: [Bash, PowerShell, Read, Edit, Write, Grep, Glob, Skill]`, `max_turns: 20`
  - `sc-author-skill`: prompt `/sc-author agent a subagent at .claude/agents/sql-migration-reviewer.md that reviews SQL migrations in migrations/ for destructive statements`
  - `sc-author-plain`: prompt `Create a subagent at .claude/agents/sql-migration-reviewer.md that reviews SQL migrations in migrations/ for destructive statements.`
  - checks (둘 다)
    - `{type: file_exists_glob, tag: success, pattern: '.claude/agents/sql-migration-reviewer.md'}`
    - `{type: cmd_ok, tag: success, cmd: [superclaude, author-check, .claude/agents/sql-migration-reviewer.md]}` — `sc-author-skill`은 통과해야 하고, `sc-author-plain`은 측정값 (차이가 스킬에서 나오는지)
  - checks (`sc-author-skill`만): `{type: transcript_regex, tag: verification, pattern: 'author-check'}` — 스킬의 Check 단계가 실제로 돌았는지 (`transcript_regex`는 Bash·PowerShell 명령 입력만 봄, `run_eval.py:380-392`)
  - checks (`sc-author-plain`만): `{type: transcript_not_regex, tag: scope, pattern: 'author-check'}` — 평문 요청에서 스킬이 발동하지 않음 (C7 "명시 호출", D4)
  - `gate:`는 붙이지 않는다 (`tests/unit/test_eval_harness.py:183` 하드 게이트 집합 고정)
  - 헤드리스에서 승인 턴이 없으므로 스킬의 "diff → 승인 후 쓰기"에서 멈출 수 있다. 첫 실행에서 파일이 안 생기면 prompt 끝에 `Approved: write the file without asking.`를 붙이고 이 변경을 `## Deviations`에 기록 (`implement-checkpoint` 주석의 headless 승인 설명 참고)
- [x] Step 3: `uv run pytest tests/unit/test_eval_harness.py -v` → PASS (`test_every_fixture_dir_exists`, `test_all_check_types_implemented`)
- [x] Step 4: `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain --dry-run` → 작업 공간 두 개 생성, `.claude/skills/sc-author/SKILL.md` 존재

### Task G2: 실행과 기록

- [x] Step 5: `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain --runs-dir <새 디렉터리>` (sonnet, 기본 effort). 한 번 실행
- [x] Step 6: 아래 Results에 기록: 과제별 check 결과, `author-check` 출력의 error·warning 수, turns·duration
- [x] Step 7: 판정
  - 성공 조건: `sc-author-skill`의 `cmd_ok`·`transcript_regex` 통과, `sc-author-plain`의 `transcript_not_regex` 통과
  - `sc-author-skill`이 실패 → 원인을 transcript에서 찾는다 (스킬 미확장 → `allowed_tools`·prompt 형식, 승인 대기 → Step 2 마지막 줄, 검사기 error 반복 → 3회 상한 동작 확인). 원인과 수정은 `## Deviations`
  - `sc-author-plain`도 `cmd_ok` 통과 → 효과 주장이 이 프로브로는 증명되지 않음. 숨기지 않고 Results에 그대로 쓰고 최종 보고에 올린다
- [x] Step 8: `make format && make lint && uv run pytest` → 모두 exit 0
- [x] Step 9: 커밋 `test(evals): add sc-author effect and explicit-invocation probes` (Results 포함)

## Results

실행 2026-10-14, `--canary --task sc-author-skill --task sc-author-plain`, sonnet, 기본 effort, 로컬 `claude -p`, runs-dir `%TEMP%/superclaude-evals/sc-author-run2`.

| task | checks | turns | 시간 | out tokens | cost | 결과 파일 | `author-check` |
|---|---|---|---|---|---|---|---|
| sc-author-skill | 3/3 | 11 | 51.1s | 3,562 | $0.30 | md 본문 32줄 | 0 errors, 0 warnings |
| sc-author-plain | 3/3 | 6 | 34.8s | 2,652 | $0.24 | XML `<component>` 본문 64줄 | 0 errors, 0 warnings |

판정 (Step 7):
- 성공 조건 충족: 스킬 run이 `author-check`를 실제로 실행했고(transcript), 평문 run은 실행하지 않음 → `disable-model-invocation` 동작 확인
- 효과 주장은 이 프로브로 증명되지 않음: 평문 run도 `author-check`를 통과. 차이는 검사기 밖에 있음 — 평문 run은 프로젝트의 기존 agent를 보고 이 저장소 고유 XML 골격(`<component>`, `<tool_guidance>`, `[R06 Scope]` 태그 인용 포함)을 그대로 복사, 스킬 run은 references 기준의 짧은 md 본문
- 관찰된 설계 긴장 (D21로 해소, 아래): 첫 실행(run1)에서 스킬은 "프로젝트 agent 24개가 XML인데 새 파일은 md 기본"이라며 `--xml` 여부를 물었음. Resolve의 "새 파일은 md"(D2)와 Load의 "프로젝트 관례 우선"(D19)이 형식 기본값에서 부딪힘

D21 적용 후 재실행 (2026-10-14, `--canary --task sc-author-skill`, run3): 3/3, 결과 파일은 프로젝트 agent와 같은 XML 본문 58줄, `author-check --format xml` → 0 errors, 0 warnings. 위 "설계 긴장"은 D21로 해소

D22 적용 후 효과 재측정 (2026-10-14, run4, 두 과제, sonnet, 기본 effort, runs-dir `C:/tmp/sc-evals/sc-author-run4`). `author-check`만으로는 두 run이 갈리지 않으므로(run2) 두 과제에 골격 검사를 추가: 결과 파일에 `<component`, `<mission>`, `<bounds>`, `[Rnn`이 없어야 통과 (`evals/tasks.yaml`, D22 "구조는 references")

| task | checks | turns | 시간 | out tokens | cost | 결과 파일 | `author-check` | 골격 검사 |
|---|---|---|---|---|---|---|---|---|
| sc-author-skill | 4/4 | 12 | 64.5s | 3,318 | $0.30 | XML 본문 31줄, `<agent>/<role>/<task>/<return>` | 0 errors, 0 warnings | 통과 |
| sc-author-plain | 3/4 | 7 | 31.4s | 1,994 | $0.23 | XML 본문 50줄, `<component>`·`<mission>`·`<bounds>` | 0 errors, 0 warnings | 실패 (설치된 SC agent 골격 복사) |

판정: 효과가 이 프로브에서 처음으로 측정됨. 두 run 모두 프로젝트 형식(XML)을 따르지만, 스킬 run만 references의 구조를 쓰고 평문 run은 설치된 SC agent 골격을 복사한다. 1회 실행이라 비율이 아닌 관찰이다. 검사는 SC 골격의 부재만 보며, 문서 품질 전반을 재지는 않는다

나머지 유형 (2026-10-14, run5, 과제 8개, sonnet, 기본 effort, runs-dir `C:/tmp/sc-evals/sc-author-run5`). 유형마다 같은 쌍에 reference에서 가져온 검사 하나를 실행 전에 정해 추가 (command: `name` 필드 없음 · output-style: `keep-coding-instructions: true` · skill: description에 "Use when" · rules: frontmatter는 `paths`만)

| 유형 | skill run | plain run | 차이 |
|---|---|---|---|
| command | 5/5, md 19줄 | 5/5, md 41줄 | 검사로는 없음. 평문 run도 SC command 골격을 복사하지 않음 |
| output-style | 5/5, 22줄 | 5/5, 38줄 | 검사로는 없음 (설치된 `plain-language.md`가 이미 reference 형태) |
| skill | 4/5, 20줄 | 5/5, 28줄 | 스킬 run 실패는 검사가 좁아서: description이 "Use before applying migrations, or when asked…" (언제 쓰는지는 있음) |
| memory (rules) | 5/5, 6줄 | 5/5, 10줄 | 검사로는 없음. 스킬 run만 규칙마다 이유와 확인 가능한 표지(`-- ROLLBACK:`)를 씀 |

내용 감사 (run4·run5 결과 파일 10개, `quality.md` 감사 표와 유형 reference 기준):

- agent: 평문 run에 모순 1 (`DROP TABLE`은 critical인데 `DROP ... IF EXISTS`는 low), 출력 형식 불일치 1 (Confidence를 정의하고 행 형식에는 없음), 중복 1 (`<mindset>`과 `<never>`). 스킬 run은 이런 결함이 없고, "Ask for a rollback note"에서 누구에게 묻는지 모호한 문장 1
- command: 두 run 모두 사용 가능. 스킬 run은 `DROP INDEX`를 전부 잡고 여러 줄에 걸친 문장을 다루지 않음. 평문 run은 결과가 없어도 "Review HIGH findings…" 줄을 출력하고, 마지막 문장 "Say so if the scan covered no such cases"가 모호함
- output-style: 스킬 run이 더 나쁨. "Open every reply with the findings"가 세션의 모든 응답에 걸려, 리뷰가 아닌 응답에도 findings를 먼저 쓰라고 함. 평문 run은 "When reviewing a SQL migration"으로 범위를 좁히고 코드 작업을 따로 다룸
- skill: 둘 다 사용 가능. 평문 run의 `allowed-tools: Read, Grep, Glob`는 권한 프롬프트가 없는 도구라 no-op이고, 건너뛸 규칙 하나가 탐지 목록 안에 들어 있음. 스킬 run의 "only the not-yet-applied ones"는 적용 여부를 알 방법을 주지 않음
- memory: 둘 다 올바름. 스킬 run은 이유를 붙이고(quality.md "Give the reason") 표지를 정함, 평문 run은 이유 없는 짧은 규칙

감사 후 조치 (2026-10-14):
- output-style 범위 과잉 → `references/output-style.md` Pitfalls에 "스타일은 세션의 모든 응답에 걸린다, 한 종류의 응답용 규칙은 언제 적용되는지 밝힌다" 한 줄 추가. 재실행(run6, `sc-author-output-style-skill`, runs-dir `C:/tmp/sc-evals/sc-author-run6`): 5/5, 본문이 "When you review a migration"과 "Everything else"(리뷰 밖에서는 평소대로) 절로 나뉨
- skill 검사가 좁음 → 정규식을 `use (when|before|for|after)`로 넓힘. run5 스킬 run 파일에 다시 돌려 통과. 검사를 결과를 본 뒤 고친 것이므로 `tasks.yaml` 주석에 그 사실을 적음

- command 하위 폴더 누락 (reflect에서 발견) → run5 스킬 run이 `.claude/commands/*.md`만 찾아 `.claude/commands/sc/`의 XML command를 못 보고 md로 씀 (D21 위반). `references/command.md`·`agent.md`를 `**/*.md`로 (CC 문서: command 하위 폴더는 네임스페이스, `.claude/agents/`는 재귀 스캔), `author-check`의 agent 경로 추론도 하위 폴더 허용. 재실행(run7, `sc-author-command-skill`, runs-dir `C:/tmp/sc-evals/sc-author-run7`): 5/5, `.claude/commands/sc/explain.md`를 읽고 XML 본문(`<instructions>/<context>/<steps>`, SC 골격 없음)으로 씀

판정: references 구조의 효과는 agent에서만 검사로 보임. 나머지 유형은 평문 run도 SC 골격을 복사하지 않아 같은 검사로는 갈리지 않음. 내용 품질은 agent·memory에서 스킬 쪽이 낫고, command·skill은 비슷하며, output-style은 평문 쪽이 나음 (스킬 run이 범위를 과하게 잡음). 각 1회 실행

## Deviations

- 대상 경로를 `.claude/agents/`에서 `agents/sql-migration-reviewer.md`로 옮김: 첫 실행(run1)에서 평문 run의 Write가 권한 프롬프트로 막힘. `.claude`는 protected path라 headless에서 프롬프트 없이 쓰려면 `bypassPermissions`가 필요하고, 문서는 그 모드를 컨테이너·VM용으로 한정함 → 권한을 올리지 않고 경로를 옮김. 검사기는 `/agents/*.md`를 agent로 추론하므로 검사 내용은 같음
- 두 prompt에 같은 사전 승인 문장("Approved in advance: write the file without asking for confirmation.")을 붙임 (Step 2 마지막 줄의 대비책): run1에서 스킬 run이 diff 승인을 기다리며 멈춤
- run1 결과: skill 0/3 (승인 대기), plain 1/3 (권한 차단). run2가 위 두 변경 후의 결과
