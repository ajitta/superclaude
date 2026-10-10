---
status: draft
revised: 2026-10-10
---

# Plain Language 구조 복원 Implementation Plan

**Goal:** Plain Language 스타일에서 단계는 번호 목록(하위 단계는 중첩), 비교는 표, 병렬 항목은 불릿으로 나오게 하고, 측정으로 확인된 경우에만 문장 길이 규칙도 고친다.

**Architecture:** 스타일 파일은 Claude Code가 시스템 프롬프트로 그대로 보내는 Markdown 본문이다. 따라서 수정은 문구 교체뿐이다. 효과는 headless `claude -p` A/B 측정으로 판정한다(기존 연구 문서 §3 방식). 본문은 598/600단어여서 문장을 추가할 수 없고, 모든 수정은 기존 문장을 바꾸는 방식으로 한다.

**Tech Stack:** Markdown 출력 스타일, `claude -p` (`claude-opus-5-5`), pytest (`tests/unit/test_output_style_structure.py`), Python 측정 스크립트(커밋하지 않음)

**Branch:** `fix/plain-language-structure`. 모든 명령은 저장소 루트에서 Git Bash로 실행한다.

## 배경과 근거

- 사용자 보고(2026-10-10): 문장이 지나치게 길게 이어지고, 표·리스트·스텝·서브 스텝이 소설처럼 긴 문단으로 나온다.
- 구조를 줄이는 문장: `:3`(description, 매 요청에 주입되는지는 확인 안 됨), `:7` "Write natural, direct prose", `:23` "Use paragraphs by default", "headings only", "bold only", "Do not force groups of three", `:33` "Do not invent categories or lists", `:48` "unnecessary formatting are gone". 구조를 허용하는 문장은 `:23` "bullets for parallel items or steps" 하나다. 표와 하위 단계는 문서 어디에도 나오지 않는다.
- 측정 근거: `docs/research/plain-language-output-style-chosh1179-2026-09-11.md` §3. 스타일을 켜면 불릿은 대체로 줄었다. Opus 5에서는 en-explain이 14→6, ko-testing이 5→2로 줄었고, en-debug는 0→5로 늘었다. Fable 5.1에서는 en-debug가 9→6, ko-testing이 4→0으로 줄었다. 단어 수는 Opus 5에서 같거나 5~31% 줄었고, Fable 5.1에서는 3~23% 늘었다. Opus에서 분량이 늘지 않았으므로, 만연체는 문장 하나의 길이 문제일 가능성이 있다. 다만 문장 길이는 측정한 적이 없다.
- 설계 의도: `:23`은 Fable 5.1 가이드("replace it with a rule that says when specific formatting is appropriate")에 따라 긍정형으로 쓴 규칙이다(연구 문서 15행). 이 계획은 그 방향을 표와 하위 단계까지 넓힌다.

## 측정 방법 (모든 Phase 공통)

연구 문서 §3 방식에 지표를 더한다. 측정 디렉터리는 저장소와 `~/.claude` 밖에 둔다. 모델이 작업 디렉터리의 파일을 환경 정보로 읽기 때문이다. 계획이 끝나면 디렉터리를 지운다.

**플러그인 상태.** user scope에 `claude-mem`과 `context-mode`가 켜져 있다(`~/.claude/settings.json` `enabledPlugins`). `claude-mem`은 실행할 때마다 기록이 쌓이므로, 실행 시점마다 주입 내용이 달라질 수 있다. 측정 기록이 사용자 메모리 DB에 쌓이는 문제도 있다. 그래서 측정할 때는 `--settings`로 두 플러그인을 끈다. 이 방법이 실제로 통하는지는 Task 1 Step 2에서 확인한다.

```bash
P=~/sc-probes/plain-language-2026-10-10
M=claude-opus-5-5
S_DEF='{"enabledPlugins":{"claude-mem@thedotmack":false,"context-mode@context-mode":false}}'
S_STY='{"outputStyle":"Plain Language","enabledPlugins":{"claude-mem@thedotmack":false,"context-mode@context-mode":false}}'
mkdir -p "$P/default" "$P/style/.claude/output-styles"

# measure <label> <tsv> <conds>   conds: "default style" 또는 "style"
measure() {
  local label=$1 tsv=$2 conds=$3 out="$P/out-$1"
  mkdir -p "$out"
  cp src/superclaude/output-styles/plain-language.md "$P/style/.claude/output-styles/"
  cp src/superclaude/output-styles/plain-language.md "$out/style-under-test.md"
  claude --version > "$out/VERSION"
  for run in 1 2 3; do
    while IFS=$'\t' read -r id prompt <&3; do
      for c in $conds; do
        if [ "$c" = style ]; then s=$S_STY; else s=$S_DEF; fi
        (cd "$P/$c" && claude -p "$prompt" --model "$M" --output-format text \
           --settings "$s" < /dev/null > "$out/$id.$c.$run.md")
      done
    done 3< "$tsv"
  done
  uv run python "$P/metrics.py" "$out" > "$out/metrics.tsv"
}
```

- **표준 입력:** `claude -p`는 파이프로 들어온 표준 입력을 프롬프트에 합친다. 그래서 TSV는 fd 3으로 읽고, `claude`의 표준 입력은 `/dev/null`로 막는다.
- **결과 디렉터리:** 측정마다 `out-<label>`을 새로 만들고 덮어쓰지 않는다. 측정한 스타일 파일도 `style-under-test.md`로 함께 남긴다.

`$P/prompts.tsv` (탭 구분, 8개, 언어 2개 × 모양 4개):

| id | prompt | 기대 모양 |
|---|---|---|
| en-steps | Walk me through setting up a new Python project from scratch with uv: virtual environment, dev dependencies, pre-commit hooks running ruff, and pytest with coverage. | 단계 + 하위 단계 |
| ko-steps | uv로 새 파이썬 프로젝트를 처음부터 세팅하는 과정을 알려줘. 가상환경, 개발 의존성, ruff를 돌리는 pre-commit 훅, 커버리지 포함 pytest까지. | 단계 + 하위 단계 |
| en-compare | Compare SQLite, PostgreSQL and DuckDB for a single-user local analytics tool on setup effort, concurrent writes, analytical query speed, and on-disk size. | 표 |
| ko-compare | 단일 사용자용 로컬 분석 도구에 쓸 DB로 SQLite, PostgreSQL, DuckDB를 설치 난이도, 동시 쓰기, 분석 쿼리 속도, 디스크 크기 기준으로 비교해줘. | 표 |
| en-causes | What are the common causes of intermittent 502 errors from nginx in front of gunicorn? | 불릿 또는 번호 목록 |
| ko-causes | gunicorn 앞에 둔 nginx에서 502가 간헐적으로 나는 흔한 원인들을 알려줘. | 불릿 또는 번호 목록 |
| en-narrative | Why did Python choose significant indentation instead of braces? | 문단 (과교정 감시용 대조군) |
| ko-narrative | 파이썬은 왜 중괄호 대신 들여쓰기로 블록을 구분하게 됐어? | 문단 (과교정 감시용 대조군) |

### 지표 (`$P/metrics.py`)

파일마다 TSV 한 줄을 출력한다. 파일명 `id.cond.run.md`에서 id, cond, run을 읽는다. 코드 블록(```` ``` ```` 사이)은 모든 지표에서 뺀다.

| 지표 | 정의 |
|---|---|
| `numbered` | `^\s*\d+[.)]\s` 줄 수 |
| `step_heads` | `^(#{1,6}\s+\|\*\*)(\d+[.)]\|Step\s+\d+\|\d+\s*단계)` 줄 수. 헤딩이나 굵은 글씨로 쓴 단계 |
| `nested` | `^\s{2,}(\d+[.)]\|[-*])\s` 줄 수 |
| `bullets` | `^\s*[-*]\s` 줄 수 |
| `tables` | `^\|`로 시작하는 연속 줄 묶음 가운데 구분 행(`^\|[\s:\|-]+\|\s*$`)이 있는 묶음 수 |
| `headers` | `^#{1,6}\s` 줄 수 |
| `words` | 공백으로 나눈 단어 수 |
| `sent_len` | 아래 절차로 구한 문장 평균 길이 |
| `emdash` | `—` 개수 |
| `offer` | 마지막 문단이 `(?i)let me know\|if you want\|want me to\|원하시면\|드릴까요\|드릴게요`와 맞으면 1 |

- **단계와 하위 단계:** "단계 있음"은 `numbered + step_heads > 0`이다. "하위 단계 있음"은 `nested > 0`이거나, `step_heads > 0`이면서 `bullets > 0`인 경우다. 헤딩으로 쓴 단계 아래에 오는 목록은 들여쓰기가 없어도 하위 단계로 센다.
- **`sent_len` 절차:**
  1. 코드 블록, 표 줄(`^\|`), 헤딩 줄을 지운다.
  2. 목록 줄은 기호(`^\s*([-*]|\d+[.)])\s+`)만 떼고, 각 항목을 별도의 단위로 둔다.
  3. 나머지 줄은 빈 줄을 기준으로 문단으로 묶고, 문단 안의 줄바꿈은 공백으로 바꾼다.
  4. 단위마다 `(?<=[.!?])\s+`로 나누고, 빈 조각은 버린다.
  5. 문장 길이는 `en-*`이면 단어 수, `ko-*`이면 공백을 뺀 글자 수로 센다. 모든 문장의 평균을 낸다.

### 판정 기준

한 셀에서 어떤 모양이 "있음"이라는 것은 3회 실행 중 2회 이상 나왔다는 뜻이다. 실행마다 편차가 크기 때문이다(연구 문서 64행). 판정이 경계에 걸리면 그 셀만 3회 더 돌려 6회 중 4회로 판정한다.

**구조 기준(S1~S3)은 같은 측정의 기본 조건과 비교한다.** 기본 조건에 그 모양이 있는 셀만 판정 대상이다. 그런 셀에서는 스타일 조건에도 그 모양이 있어야 한다. 기본 조건에 그 모양이 없는 셀은 판정에서 빼고, 뺐다는 사실을 기록한다.

| 기준 | 스타일 조건의 통과 조건 |
|---|---|
| S1 steps | `*-steps`: 기본 조건에 단계가 있으면 스타일에도 단계가 있음. 하위 단계도 같은 방식 (en, ko 각각) |
| S2 compare | `*-compare`: 기본 조건에 `tables`가 있으면 스타일에도 있음 (en, ko 각각) |
| S3 causes | `*-causes`: 기본 조건에 `bullets` 또는 `numbered`가 있으면 스타일에도 있음 |

**회귀 기준(S4~S6)은 수정 전 스타일(Task 1의 `out-base` 스타일 조건)과 비교한다.** 이번 수정이 만든 변화만 회귀로 보기 위해서다. Task 1에서는 이 값을 기록만 하고 판정하지 않는다.

| 기준 | 수정 후 스타일의 통과 조건 |
|---|---|
| S4 과교정 감시 | `*-narrative`: 3회 모두 `tables` = 0. `headers` 평균 ≤ max(1, 수정 전 평균). `numbered`와 `bullets` 평균은 각각 수정 전 평균 + 1 이하 |
| S5 기존 규칙 회귀 | 프롬프트별 `emdash` 평균 ≤ 수정 전 평균 + 1. 스타일 답변 24개의 `offer` 합계 ≤ 수정 전 합계 + 1 |
| S6 분량 | 8개 프롬프트의 `words` 평균을 합한 값 ≤ 수정 전 합계 × 1.10 |

**문장 길이(L1).** 프롬프트마다 비율 r = 스타일 `sent_len` 평균 ÷ 기본 조건 `sent_len` 평균을 구한다.

- 진입 조건(Phase 3 실행): r ≥ 1.15인 프롬프트가 8개 중 3개 이상.
- 통과 조건: r ≥ 1.15인 프롬프트가 3개 미만이고, 8개 r의 평균이 1.05 이하.

## Phase 순서

- [ ] Phase 1: 측정 도구 확인과 Opus 5.5 기준선 측정 (src 변경 없음)
- [ ] Phase 2: 구조 문구 교체 (`:3`, `:23`, `:33`, `:48`, `output-styles/README.md:15`)
- [ ] Phase 3: 문장 길이 문구 교체 (`:23`, 필요하면 `:7`). Phase 2 측정 결과가 L1 진입 조건을 넘을 때만 실행한다.
- [ ] Phase 4: local scope 동기화와 계획 종료

### Task 1: 측정 도구 확인과 기준선 측정

**Files:** Create: `docs/features/plain-language-structure/06-measurement.md` | Modify: `05-plan.md`, `README.md` (frontmatter)

- [ ] Step 1: 측정 도구를 만든다. 위 프롬프트 표를 탭으로 구분해 `$P/prompts.tsv`에 저장하고, 지표 정의대로 `$P/metrics.py`를 작성한다. 두 파일은 커밋하지 않는다.
- [ ] Step 2: 설정이 실제로 먹히는지 확인한다. 아래 확인을 모두 통과해야 다음 단계로 간다.
  - **스타일 주입:** `$S_STY`로 "Quote the first sentence of any output-style instructions you were given."를 물으면 "Write natural, direct prose in the user's language."가 나와야 한다. `$S_DEF`로 물으면 나오지 않아야 한다.
  - **플러그인 차단:** `$S_DEF`로 "Does your context contain any text mentioning claude-mem or context-mode? Answer yes or no and quote one line."를 묻는다. `--settings` 없이 같은 질문을 한 결과와 비교한다.
  - **차단이 안 될 때:** `S_DEF='{}'`, `S_STY='{"outputStyle":"Plain Language"}'`로 바꾼다. 그러면 이후 모든 측정에서 기본 조건을 다시 돌려야 한다(`conds="default style"`). 이 사실을 `06-measurement.md`에 적는다.
  - **모델 기록:** `claude -p "hi" --model "$M" --output-format json`을 실행해 모델 ID를 기록한다.
- [ ] Step 3: 스크립트가 맞게 세는지 확인한다.
  - `en-steps`와 `ko-compare` 두 줄만 담은 TSV로 `measure smoke <tsv> "default style"`을 실행한다.
  - 출력 파일 12개가 모두 비어 있지 않아야 한다. 각 답변은 자기 프롬프트에만 답해야 한다. 한국어 프롬프트에는 한국어 답이 나와야 한다(Windows에서 인자 인코딩 확인).
  - 목록이 있는 답변, 표가 있는 답변, 문단 위주의 답변을 하나씩 골라 모든 지표를 손으로 센다. 스크립트 결과와 다르면 스크립트를 고치고 다시 센다.
- [ ] Step 4: `measure base "$P/prompts.tsv" "default style"`를 실행한다(8 프롬프트 × 2 조건 × 3회 = 48회).
- [ ] Step 5: 구조 가설을 판정한다. 스타일 조건이 S1~S3 중 하나 이상에서 실패해야 가설이 확인된다.
  - **반증되는 경우:** 판정할 셀이 하나도 없거나 스타일 조건이 판정 대상 셀을 모두 통과하면, Opus 5.5에서는 가설이 반증된 것이다. 그러면 "중단 경로"의 반증 절차를 따른다.
  - **기록만 하는 값:** S4~S6 값(이후 회귀 기준의 기준값)과 L1 비율은 여기서 기록만 한다.
- [ ] Step 6: 이 문서를 `status: implementing`, README를 `phase: implementing`으로 바꾼다. `06-measurement.md`에 아래를 기록한다. README `## Documents`에 항목을 추가하고 `updated:`를 갱신한다.
  - `claude --version`과 모델 ID
  - 플러그인 차단 여부
  - 프롬프트 표
  - `out-base/metrics.tsv`의 조건별 평균 표
  - S1~S3 판정과 판정에서 뺀 셀
  - S4~S6 기준값과 L1 비율
- [ ] Step 7: Commit `docs(plain-language): record the Opus 5.5 structure baseline`

### Task 2: 구조 문구 교체

**Files:** Modify: `src/superclaude/output-styles/plain-language.md:3,23,33,48`, `src/superclaude/output-styles/README.md:15` | Test: `tests/unit/test_output_style_structure.py`

교체 문구(첫 시도). 단어 수는 테스트와 같은 방식(frontmatter를 떼고 `split()`)으로 셌다.

| 줄 | 현재 | 교체 | 단어 변화 |
|---|---|---|---|
| `:3` | `description: Direct, specific prose in the user's language, without AI mannerisms or decorative structure` | `description: Direct, specific prose in the user's language, without AI mannerisms` | frontmatter라 본문 단어 수와 무관 |
| `output-styles/README.md:15` | Purpose 칸: "…without AI mannerisms or decorative structure" | `:3`의 새 description과 같은 문구 | 스타일 본문 아님. 이 사본이 같은지 확인하는 테스트는 없다 |
| `:23` 둘째 문장 | Use paragraphs by default, bullets for parallel items or steps, headings only when they help navigation, and bold only for a term the reader must find again. | Use numbered steps for sequences, with sub-steps nested, bullets for parallel items, tables for comparisons, paragraphs for reasoning, headings only when they help navigation, and bold only for a term the reader must find again. | 27 → 35 (+8) |
| `:23` 마지막 문장 | Do not force groups of three or symmetry. | (삭제, `:33`으로 합침) | −8 |
| `:33` 둘째 문장 | Do not invent categories or lists to make a simple point appear comprehensive. | Do not force threes or symmetry, or invent categories to look comprehensive. | 13 → 12 (−1) |
| `:48` | 4. Template transitions, ornamental contrasts, and unnecessary formatting are gone, and the wording reads as native. | 4. Template transitions and ornamental contrasts are gone, form fits content, and the wording reads as native. | 16 → 17 (+1) |

- **단어 수:** 본문은 598단어에서 그대로 598단어다.
- **"for sequences":** 번호 목록을 쓸 조건이다. 이 조건이 없으면 모든 답을 번호 목록으로 쓰라는 뜻으로 읽힐 수 있다.
- **`:33`에서 "lists"를 뺀 이유:** 목록을 피하라는 신호를 한 번 더 주기 때문이다.
- **`:48`의 "form fits content":** 비유가 아닌 문자 그대로의 표현이다.

- [ ] Step 1: 실패하는 테스트는 Task 1의 기준선이다(S1~S3 중 실패한 기준).
- [ ] Step 2: 위 표대로 교체한다. `README.md:15`도 같은 커밋에서 바꾼다.
- [ ] Step 3: `uv run pytest tests/unit/test_output_style_structure.py -q`를 실행한다. 단어 한도 테스트와 언어 중립 테스트가 통과해야 한다.
- [ ] Step 4: 다시 측정한다. `measure p2-1 "$P/prompts.tsv" "style"`을 실행한다. 두 번째, 세 번째 시도는 `p2-2`, `p2-3`이다.
  - **기본 조건 재측정:** 플러그인 차단이 안 됐거나 `claude --version`이 Task 1과 다르면 `"default style"`로 기본 조건도 다시 돌린다. 이때 S1~S3과 L1은 같은 측정의 기본 조건과 비교한다. 그렇지 않으면 `out-base`의 기본 조건을 쓴다.
  - **판정:** S1~S6이 모두 통과해야 한다.
  - **실패할 때:** 단어 한도 안에서 문구를 바꿔 다시 측정한다. 시도는 최대 3회이고, 시도마다 문구와 수치를 `06-measurement.md`에 남긴다(연구 문서 §5 방식). 3회 안에 통과하지 못하면 "중단 경로"의 실패 절차를 따른다.
- [ ] Step 5: L1 진입 조건을 판정한다. Step 4에서 통과한 문구로 측정한 값을 쓴다. 목록과 표가 늘면 긴 문장도 같이 줄어들 수 있기 때문이다.
  - **진입 조건을 넘으면:** Task 3을 실행한다.
  - **넘지 않으면:** Phase 3 줄과 Task 3의 모든 단계를 `- [x] ~~…~~`로 표시하고, `## Deviations`에 L1 비율과 함께 이유를 적는다.
- [ ] Step 6: `uv run pytest`가 0으로 끝나고 `make lint`가 통과해야 한다.
- [ ] Step 7: Commit `fix(output-style): name the shapes that take lists and tables in Plain Language`. `06-measurement.md`도 이 커밋에 함께 넣는다.

### Task 3: 문장 길이 문구 교체 (조건부)

**Files:** Modify: `src/superclaude/output-styles/plain-language.md:23` (필요하면 `:7`) | Test: `tests/unit/test_output_style_structure.py`

간결성 보호 장치 두 개(`:7` "abrupt", `:23` "fragments")를 한 번에 없애지 않기 위해 두 번에 나눠 시도한다.

| 시도 | 줄 | 현재 | 교체 | 본문 단어 수 |
|---|---|---|---|---|
| A | `:23` 첫 문장 끝 | do not turn concision into fragments | split a sentence that joins two conditions | 598 → 599 |
| B (A로 부족할 때) | `:7` 둘째 문장 | Keep enough detail to be useful; brevity must not make the response abrupt or incomplete. | Keep the detail the request needs and no more. | 599 → 593 |

- [ ] Step 1: 실패하는 테스트는 Task 2 Step 5에서 r ≥ 1.15였던 프롬프트들이다.
- [ ] Step 2: 시도 A를 적용한다.
- [ ] Step 3: `uv run pytest tests/unit/test_output_style_structure.py -q`가 통과해야 한다.
- [ ] Step 4: `measure p3-a "$P/prompts.tsv" "style"`을 실행한다(기본 조건 재측정 규칙은 Task 2 Step 4와 같다).
  - **판정:** L1 통과 조건을 만족하고, S1~S6이 계속 통과해야 한다.
  - **L1만 실패하면:** 시도 B를 더해 `p3-b`로 다시 측정한다.
  - **과교정:** 스타일 `words` 합계가 기본 조건 합계의 70% 아래로 떨어지면 과교정이다. 이 경우 B를 되돌린다.
  - **실패할 때:** A와 B 모두 통과하지 못하면 "중단 경로"의 실패 절차를 따른다.
- [ ] Step 5: `uv run pytest`가 0으로 끝나고 `make lint`가 통과해야 한다.
- [ ] Step 6: Commit `fix(output-style): split long sentences in Plain Language`, `06-measurement.md` 포함.

### Task 4: 동기화와 계획 종료

**Files:** Modify: `docs/features/plain-language-structure/README.md`, `05-plan.md` (frontmatter)

- [ ] Step 1: 브랜치에서 local scope 설치를 갱신한다(gotcha `sync-scope-creates`, `windows-make-sync-broken`).
  - `superclaude doctor --scope local`로 local 설치가 있는지 확인한 뒤 `superclaude install --force --scope local`을 실행한다.
  - 설치는 작업 트리에서 하므로, 이때 설치되는 내용은 병합될 내용과 같다.
  - `.claude/output-styles/plain-language.md`가 저장소 파일과 같아야 한다(`diff`의 출력이 없어야 함).
- [ ] Step 2: 이 문서의 체크박스를 모두 체크했는지 확인하고 `status: complete`로 바꾼다. README는 `phase: complete`로 바꾼다.
- [ ] Step 3: 브랜치에서 Commit `docs(plain-language): close the structure plan`. 측정 디렉터리 `$P`를 지운다.

**체크리스트 밖의 마무리:**
- 닫는 커밋 다음에 `master`로 `--no-ff` 병합하고 푸시한다. 병합 단계를 체크박스로 두지 않은 이유는, 병합보다 먼저 만드는 닫는 커밋에서는 이 박스를 체크할 수 없기 때문이다.
- CHANGELOG 항목은 다음 버전 bump 커밋에서 `### Changed` 아래에 쓴다. 예: "Plain Language output style: steps come out as numbered lists with nested sub-steps, comparisons as tables."

## 중단 경로

- **가설 반증 (Task 1 Step 5):** 아래 순서로 계획을 닫고 사용자에게 보고한다.
  1. Phase 2·3 줄, Task 2·3의 모든 단계, Task 4 Step 1을 `- [x] ~~…~~`로 표시한다.
  2. `## Deviations`에 판정 수치를 적는다.
  3. Task 1 Step 6·7과 Task 4 Step 2·3을 실행한다(`status: complete`, README `phase: complete`).
  4. src는 바꾸지 않았으므로 병합할 커밋은 문서 커밋뿐이다.
- **시도 3회 실패 (Task 2 Step 4, Task 3 Step 4):** 아래 순서로 정리하고 멈춘 뒤, 다음 방향은 사용자가 정한다.
  1. src 변경을 되돌린다(`git restore src/superclaude/output-styles/`).
  2. 시도별 수치를 `06-measurement.md`에, 실패 사실을 `## Deviations`에 적고 문서만 커밋한다.
  3. `status: implementing`은 그대로 둔다.

## Risks

- **측정 해석 (가장 위험한 단계, Task 2 Step 4):** 실행마다 편차가 크다(같은 문구에서 헤더가 0개였다가 5개). 3회 측정으로는 방향만 알 수 있고 크기는 알 수 없다(연구 문서 64행). 회귀 기준은 합계와 허용 폭을 두어 우연한 실패를 줄였다. 그래도 경계에 걸리는 판정은 6회 중 4회 규칙으로 다시 본다.
- **측정 도구 결함:** 스크립트가 잘못 세면 모든 판정이 틀린다. 그래서 Task 1 Step 3에서 실제 답변을 손으로 세어 대조한다.
- **플러그인 차단 실패:** `--settings`의 `enabledPlugins`가 user scope 값을 덮어쓰지 못하면, 측정 시점마다 `claude-mem`이 주입하는 내용이 달라질 수 있다. 이 경우 같은 측정 안에서 기본 조건을 다시 돌려 비교 시점을 맞춘다(Task 1 Step 2).
- **과교정:** 표 규칙 때문에 대조군 질문에도 표나 목록이 생길 수 있다. S4로 감시한다. 연구 문서 70행의 "bold as inline heading" 잔여 문제가 커질 수도 있다.
- **기존 규칙 회귀:** 표와 목록이 늘면 레이블 뒤 대시(연구 문서 §5)와 끝맺음 제안이 다시 나타날 수 있다. S5로 감시한다.
- **단어 예산:** Phase 2가 끝나도 여유는 2단어다. Phase 3 시도 A 뒤에는 1단어, B까지 하면 7단어다. 다시 쓰는 문구도 600단어를 넘으면 안 된다.
- **사용자 노출:** `description`은 `/config` picker에 보이는 문구다. `name`은 바꾸지 않으므로 기존 `outputStyle` 설정은 그대로 동작한다.
- **모델 범위:** Opus 5.5만 측정한다. Fable 5.1은 기본 조건에서도 헤더가 0개였으므로 효과가 다를 수 있다.

## Alternatives not taken

- **`MAX_BODY_WORDS` 상향:** `output-style-authoring.md`의 "~600 words" 규칙과 테스트를 같이 바꿔야 하고, 매 요청 비용이 늘어난다. 기존 문장을 합쳐서 예산 안에 맞췄다.
- **`evals/tasks.yaml` canary 추가:** `evals/`에는 outputStyle을 설정하는 코드가 없다(grep 0건). 하네스를 확장하는 일은 이번 범위 밖이다. 출력 스타일의 회귀가 세 번째로 나오면 다시 검토한다.
- **측정 스크립트 커밋:** 기존 연구도 측정 파일을 scratch에 두었다. 대신 프롬프트, 지표 정의, `sent_len` 절차를 이 문서에 그대로 적어 재현할 수 있게 했다.
- **`--bare`로 플러그인 끄기:** keychain을 건너뛰기 때문에 구독 인증이 깨진다.
- **한국어 연결어미 규칙:** 언어 중립 테스트(`test_language_neutral`)가 막는다. 사용자별 CLAUDE.md에 둘 일이다.
- **`:23` "paragraphs by default"만 삭제:** 표와 하위 단계를 쓸 시점을 지정하지 못한다.
- **구조와 문장 길이를 한 커밋에서 수정:** 어느 변경이 효과를 냈는지 구분할 수 없다. 그래서 Phase를 나눴다.
- **회귀 기준을 기본 조건과 비교:** 현재 문구로 한 기존 측정에서도 이미 실패하는 사례가 있다(연구 문서 51행: 대시 1→3, 59-60행: 단어 417→513). 이 실패는 이번 수정과 관계없다.
- **Fable 5.1 측정:** headless Fable은 사용 크레딧이 청구된다(AGENTS.md).

## Proof

- `uv run pytest tests/unit/test_output_style_structure.py -q`: 모두 통과해야 한다. 단어 한도 테스트는 598(Phase 3 시도 A 뒤 599, B 뒤 593) ≤ 600이라서 통과한다.
- `uv run pytest`: 0으로 끝나야 한다.
- 마지막 측정의 `metrics.tsv`: S1~S6을 통과해야 하고, Phase 3을 했다면 L1 통과 조건도 만족해야 한다. 판정 표는 `06-measurement.md`에 기록한다.
- `diff src/superclaude/output-styles/plain-language.md .claude/output-styles/plain-language.md`: 출력이 없어야 한다.
- `grep -rn "decorative structure" src/`: 출력이 없어야 한다(description 사본까지 모두 바뀌었다는 확인).

## Deviations

(없음)
