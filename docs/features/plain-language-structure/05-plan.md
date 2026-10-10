---
status: draft
revised: 2026-10-10
---

# Plain Language 구조 복원 Implementation Plan

**Goal:** Plain Language 스타일에서 단계는 번호 목록(하위 단계는 중첩), 비교는 표, 병렬 항목은 불릿으로 나오게 하고, 측정으로 확인된 경우에만 문장 길이 규칙도 고친다.

**Architecture:** 스타일 파일은 Claude Code가 시스템 프롬프트로 그대로 보내는 Markdown 본문이다. 따라서 수정은 문구 교체뿐이다. 효과는 headless `claude -p` A/B 측정으로 판정한다(기존 연구 문서 §3 방식). 본문은 598/600단어여서 문장을 추가할 수 없고, 모든 수정은 기존 문장을 바꾸는 방식으로 한다.

**Tech Stack:** Markdown 출력 스타일, `claude -p` (Opus 5.5), pytest (`tests/unit/test_output_style_structure.py`), Python 측정 스크립트(커밋하지 않음)

**Branch:** `fix/plain-language-structure`

## 배경과 근거

- 사용자 보고(2026-10-10): 문장이 지나치게 길게 이어지고, 표·리스트·스텝·서브 스텝이 소설처럼 긴 문단으로 나온다.
- 구조를 줄이는 문장: `:3`(description, 매 요청에 주입되는지는 확인 안 됨), `:7` "Write natural, direct prose", `:23` "Use paragraphs by default", "headings only", "bold only", "Do not force groups of three", `:33` "Do not invent categories or lists", `:48` "unnecessary formatting are gone". 구조를 허용하는 문장은 `:23` "bullets for parallel items or steps" 하나다. 표와 하위 단계는 문서 어디에도 나오지 않는다.
- 측정 근거: `docs/research/plain-language-output-style-chosh1179-2026-09-11.md` §3. Opus 5와 Fable 5.1에서 스타일을 켜면 불릿이 줄었다(14→6, 5→2, 9→6, 4→0). 전체 단어 수는 같거나 5~30% 줄었다. 그러므로 만연체는 분량이 아니라 문장 하나의 길이 문제일 가능성이 높은데, 문장 길이는 측정한 적이 없다.
- 설계 의도: `:23`은 Fable 5.1 가이드("replace it with a rule that says when specific formatting is appropriate")에 따라 긍정형으로 쓴 규칙이다(연구 문서 15행). 이 계획은 그 방향을 표와 하위 단계까지 넓힌다.

## 측정 방법 (모든 Phase 공통)

연구 문서 §3 방식을 따르고 지표 두 개(구조 개수, 문장 길이)를 추가한다. 측정 디렉터리는 저장소와 `~/.claude` 밖에 둔다. 모델이 작업 디렉터리의 파일을 환경 정보로 읽기 때문이다. 작업이 끝나면 디렉터리를 삭제한다.

```bash
P=~/sc-probes/plain-language-2026-10-10
mkdir -p "$P/default" "$P/style/.claude/output-styles" "$P/out"
cp src/superclaude/output-styles/plain-language.md "$P/style/.claude/output-styles/"
claude --version > "$P/out/VERSION"
for run in 1 2 3; do
  while IFS=$'\t' read -r id prompt; do
    (cd "$P/default" && claude -p "$prompt" --model opus --output-format text > "$P/out/$id.default.$run.md")
    (cd "$P/style" && claude -p "$prompt" --model opus --output-format text \
       --settings '{"outputStyle":"Plain Language"}' > "$P/out/$id.style.$run.md")
  done < "$P/prompts.tsv"
done
uv run python "$P/metrics.py" "$P/out" > "$P/out/metrics.tsv"
```

`$P/prompts.tsv` (탭 구분, 8개, 언어 2개 × 모양 4개):

| id | prompt | 기대 모양 |
|---|---|---|
| en-steps | Walk me through setting up a new Python project from scratch with uv: virtual environment, dev dependencies, pre-commit hooks running ruff, and pytest with coverage. | 번호 목록 + 중첩 하위 단계 |
| ko-steps | uv로 새 파이썬 프로젝트를 처음부터 세팅하는 과정을 알려줘. 가상환경, 개발 의존성, ruff를 돌리는 pre-commit 훅, 커버리지 포함 pytest까지. | 번호 목록 + 중첩 하위 단계 |
| en-compare | Compare SQLite, PostgreSQL and DuckDB for a single-user local analytics tool on setup effort, concurrent writes, analytical query speed, and on-disk size. | 표 |
| ko-compare | 단일 사용자용 로컬 분석 도구에 쓸 DB로 SQLite, PostgreSQL, DuckDB를 설치 난이도, 동시 쓰기, 분석 쿼리 속도, 디스크 크기 기준으로 비교해줘. | 표 |
| en-causes | What are the common causes of intermittent 502 errors from nginx in front of gunicorn? | 불릿 또는 번호 목록 |
| ko-causes | gunicorn 앞에 둔 nginx에서 502가 간헐적으로 나는 흔한 원인들을 알려줘. | 불릿 또는 번호 목록 |
| en-narrative | Why did Python choose significant indentation instead of braces? | 문단 (과교정 감시용 대조군) |
| ko-narrative | 파이썬은 왜 중괄호 대신 들여쓰기로 블록을 구분하게 됐어? | 문단 (과교정 감시용 대조군) |

`$P/metrics.py`는 파일마다 아래 값을 TSV 한 줄로 출력한다(파일명 `id.cond.run.md`에서 id, cond, run을 읽는다). 코드 블록(```` ``` ```` 사이)은 모든 지표에서 뺀다.

- `numbered`: `^\s*\d+[.)]\s` 줄 수
- `nested`: `^\s{2,}(\d+[.)]|[-*])\s` 줄 수
- `tables`: `^\|`로 시작하는 연속 줄 묶음 중 구분 행(`^\|[\s:|-]+\|\s*$`)이 있는 묶음 수
- `bullets`: `^\s*[-*]\s` 줄 수
- `headers`: `^#{1,6}\s` 줄 수
- `words`: 공백으로 나눈 단어 수
- `sent_len`: 표·목록 기호·헤더를 뺀 문단 텍스트를 `(?<=[.!?])\s+`로 나눈 문장들의 평균 길이. `en-*`는 단어 수, `ko-*`는 공백을 뺀 글자 수로 센다.
- `emdash`: `—` 개수
- `offer`: 마지막 문단이 `(?i)let me know|if you want|want me to|원하시면|드릴까요|드릴게요`와 맞으면 1

**판정 기준.** 한 셀에서 어떤 모양이 "있음"이라는 것은 3회 실행 중 2회 이상 나왔다는 뜻이다. 실행마다 편차가 크기 때문이다(연구 문서 64행).

| 기준 | 스타일 조건에서 통과 조건 |
|---|---|
| S1 steps | `*-steps`: `numbered`와 `nested` 모두 있음 (en, ko 각각) |
| S2 compare | `*-compare`: `tables` 있음 (en, ko 각각) |
| S3 causes | `*-causes`: `bullets` 또는 `numbered` 있음 |
| S4 과교정 감시 | `*-narrative`: 3회 모두 `tables` = 0, `headers` ≤ 1 |
| S5 기존 규칙 회귀 | 프롬프트별 `emdash` 평균이 Phase 1 스타일 값 이하, `offer` = 0이 3회 중 2회 이상 |
| S6 분량 | 프롬프트별 스타일 `words` 평균 ≤ 기본 조건 평균 × 1.05 |
| L1 문장 길이 | 프롬프트별 스타일 `sent_len` 평균 ≤ 기본 조건 평균 × 1.05 |

## Phase 순서

- [ ] Phase 1: Opus 5.5 기준선 측정 (src 변경 없음)
- [ ] Phase 2: 구조 문구 교체 (`:3`, `:23`, `:33`, `:48`)
- [ ] Phase 3: 문장 길이 문구 교체 (`:7`, `:23`). Phase 1 게이트를 통과할 때만 실행한다.
- [ ] Phase 4: 병합과 local scope 동기화

### Task 1: 기준선 측정

**Files:** Create: `docs/features/plain-language-structure/06-measurement.md` | Update: `docs/features/plain-language-structure/README.md`

- [ ] Step 1: 위 측정 방법으로 현재 `plain-language.md`를 측정한다(8 프롬프트 × 2 조건 × 3회 = 48회).
- [ ] Step 2: 실패를 확인한다. 기본 조건은 통과하는데 스타일 조건은 S1~S3 중 하나 이상에서 실패해야 구조 가설이 확인된다. 스타일 조건도 S1~S3을 모두 통과하면 Opus 5.5에서는 가설이 반증된 것이다. 이 경우 결과를 기록하고 Phase 2~4를 하지 않은 채 보고한다.
- [ ] Step 3: 문장 길이 게이트를 판정한다. 8개 프롬프트 중 3개 이상에서 스타일 `sent_len`이 기본 조건 × 1.15 이상이면 Phase 3을 실행하고, 아니면 Phase 3을 `- [x] ~~Phase 3~~`로 표시하고 `## Deviations`에 이유를 적는다.
- [ ] Step 4: `06-measurement.md`에 `claude --version`, 프롬프트 표, `metrics.tsv`의 조건별 평균 표, S1~S6·L1 판정을 기록한다. README `## Documents`에 항목을 추가하고 `updated:`를 갱신한다.
- [ ] Step 5: Commit `docs(plain-language): record the Opus 5.5 structure baseline`

### Task 2: 구조 문구 교체

**Files:** Modify: `src/superclaude/output-styles/plain-language.md:3,23,33,48` | Test: `tests/unit/test_output_style_structure.py`

교체 문구(첫 시도). 단어 수는 `wc -w`로 셌다.

| 줄 | 현재 | 교체 | 단어 변화 |
|---|---|---|---|
| `:3` | `description: Direct, specific prose in the user's language, without AI mannerisms or decorative structure` | `description: Direct, specific prose in the user's language, without AI mannerisms` | frontmatter라 본문 단어 수와 무관 |
| `:23` 둘째 문장 | Use paragraphs by default, bullets for parallel items or steps, headings only when they help navigation, and bold only for a term the reader must find again. | Use numbered steps with nested sub-steps, bullets for parallel items, a table for comparisons across attributes, paragraphs for reasoning, headings only when they help navigation, and bold only for a term the reader must find again. | 27 → 36 (+9) |
| `:23` 마지막 문장 | Do not force groups of three or symmetry. | (삭제, `:33`으로 합침) | −8 |
| `:33` 둘째 문장 | Do not invent categories or lists to make a simple point appear comprehensive. | Do not force threes or symmetry, or invent categories to look comprehensive. | 13 → 12 (−1) |
| `:48` | 4. Template transitions, ornamental contrasts, and unnecessary formatting are gone, and the wording reads as native. | 4. Template transitions and ornamental contrasts are gone, form follows content, and the wording reads as native. | 16 → 17 (+1) |

본문은 598 → 599단어가 된다. `:33`에서 "lists"를 뺀 이유는, 이 단어가 목록을 피하라는 신호를 한 번 더 주기 때문이다.

- [ ] Step 1: 실패하는 테스트는 Task 1의 기준선이다(S1~S3 중 실패한 기준).
- [ ] Step 2: 위 표대로 교체한다.
- [ ] Step 3: `uv run pytest tests/unit/test_output_style_structure.py -q`를 실행한다. 단어 한도 테스트와 언어 중립 테스트가 통과해야 한다.
- [ ] Step 4: 같은 방법으로 스타일 조건만 다시 측정한다(기본 조건은 Task 1 값을 재사용). S1~S6이 모두 통과해야 한다. 실패하면 단어 한도 안에서 문구를 바꿔 다시 측정한다. 시도는 최대 3회이고, 시도마다 문구와 수치를 `06-measurement.md`에 남긴다(연구 문서 §5 방식). 3회 안에 통과하지 못하면 멈추고 보고한다.
- [ ] Step 5: `uv run pytest`가 0으로 끝나고 `make lint`가 통과해야 한다.
- [ ] Step 6: Commit `fix(output-style): name the shapes that take lists and tables in Plain Language`. 측정 결과는 `06-measurement.md`에 추가하고, 이 커밋에 함께 넣는다.

### Task 3: 문장 길이 문구 교체 (조건부)

**Files:** Modify: `src/superclaude/output-styles/plain-language.md:7,23` | Test: `tests/unit/test_output_style_structure.py`

| 줄 | 현재 | 교체 | 단어 변화 |
|---|---|---|---|
| `:7` 둘째 문장 | Keep enough detail to be useful; brevity must not make the response abrupt or incomplete. | Keep the detail the request needs and no more. | 15 → 9 (−6) |
| `:23` 첫 문장 끝 | do not turn concision into fragments | split a sentence that joins two conditions | 6 → 7 (+1) |

본문은 599 → 594단어가 된다.

- [ ] Step 1: 실패하는 테스트는 Task 1에서 L1을 넘은 프롬프트들이다.
- [ ] Step 2: 위 표대로 교체한다.
- [ ] Step 3: `uv run pytest tests/unit/test_output_style_structure.py -q`가 통과해야 한다.
- [ ] Step 4: 스타일 조건만 다시 측정한다. L1이 통과하고 S1~S6이 계속 통과해야 한다. `words`가 기본 조건의 70% 아래로 떨어지면 과교정으로 본다. 이 경우 `:7`을 원래 문장으로 되돌리고 `:23` 교체만 남긴 채 다시 측정한다. 시도 횟수 제한과 기록 방법은 Task 2와 같다.
- [ ] Step 5: `uv run pytest`가 0으로 끝나고 `make lint`가 통과해야 한다.
- [ ] Step 6: Commit `fix(output-style): split long sentences in Plain Language`, `06-measurement.md` 포함.

### Task 4: 병합과 동기화

**Files:** Modify: `docs/features/plain-language-structure/README.md`, `05-plan.md` (frontmatter)

- [ ] Step 1: `master`로 `--no-ff` 병합하고 푸시한다.
- [ ] Step 2: `superclaude doctor --scope local`로 local 설치가 있는지 확인한 뒤 `superclaude install --force --scope local`을 실행한다(gotcha `sync-scope-creates`, `windows-make-sync-broken`). `.claude/output-styles/plain-language.md`가 저장소 파일과 같아야 한다(`diff`의 출력이 없어야 함).
- [ ] Step 3: 이 문서의 체크박스를 모두 체크했는지 확인하고 `status: complete`로 바꾼다. README는 `phase: complete`로 바꾼다.
- [ ] Step 4: Commit `docs(plain-language): close the structure plan`. CHANGELOG 항목은 다음 버전 bump 커밋에서 `### Changed` 아래에 쓴다. 예: "Plain Language output style: steps come out as numbered lists with nested sub-steps, comparisons as tables."

## Risks

- **측정 해석 (가장 위험한 단계, Task 2 Step 4):** 실행마다 편차가 크다(같은 문구에서 헤더가 0개였다가 5개). 3회 중 2회 기준을 써도 통과와 실패가 우연일 수 있다. 판정이 경계에 걸리면 해당 셀만 3회 더 돌려 6회 중 4회로 판정한다.
- **과교정:** 표 규칙 때문에 대조군 질문에도 표나 헤더가 생길 수 있다. S4로 감시한다. 연구 문서 70행의 "bold as inline heading" 잔여 문제가 커질 수도 있다.
- **기존 규칙 회귀:** 표와 목록이 늘면 레이블 뒤 대시(연구 문서 §5)와 끝맺음 제안이 다시 나타날 수 있다. S5로 감시한다.
- **단어 예산:** Phase 2가 끝나면 여유가 1단어뿐이다. Task 2 Step 4에서 다시 쓰는 문구도 600단어를 넘으면 안 된다.
- **사용자 노출:** `description`은 `/config` picker에 보이는 문구다. `name`은 바꾸지 않으므로 기존 `outputStyle` 설정은 그대로 동작한다.
- **모델 범위:** Opus 5.5만 측정한다. Fable 5.1은 기본 조건에서도 헤더가 0개였으므로 효과가 다를 수 있다.

## Alternatives not taken

- **`MAX_BODY_WORDS` 상향:** `output-style-authoring.md`의 "~600 words" 규칙과 테스트를 같이 바꿔야 하고, 매 요청 비용이 늘어난다. 기존 문장을 합쳐서 예산 안에 맞췄다.
- **`evals/tasks.yaml` canary 추가:** `evals/`에는 outputStyle을 설정하는 코드가 없다(grep 0건). 하네스를 확장하는 일은 이번 범위 밖이다. 출력 스타일의 회귀가 세 번째로 나오면 다시 검토한다.
- **측정 스크립트 커밋:** 기존 연구도 측정 파일을 scratch에 두었다. 대신 프롬프트와 지표 정의를 이 문서에 그대로 적어 재현할 수 있게 했다.
- **한국어 연결어미 규칙:** 언어 중립 테스트(`test_language_neutral`)가 막는다. 사용자별 CLAUDE.md에 둘 일이다.
- **`:23` "paragraphs by default"만 삭제:** 표와 하위 단계를 쓸 시점을 지정하지 못한다.
- **구조와 문장 길이를 한 커밋에서 수정:** 어느 변경이 효과를 냈는지 구분할 수 없다. 그래서 Phase를 나눴다.
- **Fable 5.1 측정:** headless Fable은 사용 크레딧이 청구된다(AGENTS.md).

## Proof

- `uv run pytest tests/unit/test_output_style_structure.py -q`: 모두 통과해야 한다. 단어 한도 테스트가 599(Phase 3를 하면 594) ≤ 600으로 통과한다.
- `uv run pytest`: 0으로 끝나야 한다.
- `uv run python "$P/metrics.py" "$P/out"`: 스타일 조건이 S1~S6을 통과하고, Phase 3을 했다면 L1도 통과해야 한다. 판정 표는 `06-measurement.md`에 기록한다.
- `diff src/superclaude/output-styles/plain-language.md .claude/output-styles/plain-language.md`: 출력이 없어야 한다.

## Deviations

(없음)
