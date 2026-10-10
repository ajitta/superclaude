---
status: implementing
revised: 2026-10-10
---

# Plain Language 구조 측정 기록

[05-plan.md](./05-plan.md)의 측정 결과다. 측정 방법, 지표 정의, 판정 기준은 계획 문서를 따르고, 여기에는 환경, 계획과 달라진 점, 수치만 적는다.

## 환경

- **Claude Code:** 2.1.296
- **모델:** `claude-sonnet-5-5` (`claude -p "hi" --output-format json`의 `modelUsage` 키). 계획은 Opus 5.5였으나 구현 전에 사용자 지시로 바꿨다.
- **플러그인 차단:** 통한다. `$S_DEF`로 물으면 claude-mem, context-mode 언급이 "없음"이고, `--settings` 없이 물으면 claude-mem의 work_state 안내 문장이 인용된다. 그래서 기본 조건은 Task 1의 `out-base` 것을 재사용할 수 있다(`claude --version`이 같을 때).
- **스타일 주입:** `$S_STY`에서는 "Write natural, direct prose in the user's language."가 인용되고, `$S_DEF`에서는 output-style 지시가 없다고 답한다.
- **훅 환경:** user scope 훅(caveman native-hook, serena auto-approve, context-mode-cache-heal, paseo)은 두 조건 모두에서 켜져 있다. 기본 조건 응답이 SessionStart 훅 문장 "Build simplest complete system."을 인용했으므로, 간결성 쪽 추가 지시가 두 조건에 똑같이 들어간다.
- **소요 시간:** 48회 호출에 17분(17:21~17:39), 호출당 약 21초.

## 계획과 달라진 측정 도구

- **`offer` 정규식:** 계획의 정규식(`let me know|if you want|want me to|원하시면|드릴까요|드릴게요`)은 스모크 답변 12개의 마지막 문단에 있는 제안 7개를 하나도 잡지 못했다. 예: "If you'd like, I can scaffold this…", "데이터 규모를 알려주시면 더 구체적으로 추천해 드리겠습니다." 그래서 아래로 넓혔다. 넓힌 뒤 스모크에서 7개를 모두 잡고, 제안이 없는 마지막 문단 5개는 잡지 않았다.

  ```text
  (?i)let me know|if you want|want me to|if you'?d like|for you\b|\bI can\b(?!'t| not)|원하시면|알려주시면|드릴까요|드릴게요|드리겠습니다|드릴 수 있습니다
  ```

- **손 검증(Task 1 Step 3):** 목록 답변 `en-steps.default.1`은 headers 9, step_heads 7, bullets 6, 나머지 0으로 스크립트와 같다. 코드 블록 안의 YAML 목록은 제외됐다. 표 답변 `ko-compare.style.1`은 tables 1이고, `sent_len` 분할은 표 줄을 빼고 목록 항목 2개를 별도 문장으로 셌다(문장 11개). 이 스모크에는 문단 위주 답변이 없어서, 그 경우는 기준선의 `ko-steps.style.1`로 확인했다. 단계는 헤딩 7개이고 하위 단계 내용은 헤딩 아래 문단으로 쓰여 `nested` 0, `bullets` 0이다.

## 프롬프트

| id | prompt |
|---|---|
| en-steps | Walk me through setting up a new Python project from scratch with uv: virtual environment, dev dependencies, pre-commit hooks running ruff, and pytest with coverage. |
| ko-steps | uv로 새 파이썬 프로젝트를 처음부터 세팅하는 과정을 알려줘. 가상환경, 개발 의존성, ruff를 돌리는 pre-commit 훅, 커버리지 포함 pytest까지. |
| en-compare | Compare SQLite, PostgreSQL and DuckDB for a single-user local analytics tool on setup effort, concurrent writes, analytical query speed, and on-disk size. |
| ko-compare | 단일 사용자용 로컬 분석 도구에 쓸 DB로 SQLite, PostgreSQL, DuckDB를 설치 난이도, 동시 쓰기, 분석 쿼리 속도, 디스크 크기 기준으로 비교해줘. |
| en-causes | What are the common causes of intermittent 502 errors from nginx in front of gunicorn? |
| ko-causes | gunicorn 앞에 둔 nginx에서 502가 간헐적으로 나는 흔한 원인들을 알려줘. |
| en-narrative | Why did Python choose significant indentation instead of braces? |
| ko-narrative | 파이썬은 왜 중괄호 대신 들여쓰기로 블록을 구분하게 됐어? |

## 기준선 (`out-base`, 수정 전 스타일)

조건별 평균이다. `ko-steps`는 하위 단계 판정이 경계(기본 조건 2/3)에 걸려 3회를 더 돌렸으므로 6회 평균이다.

| id.cond | numbered | step_heads | nested | bullets | tables | headers | words | sent_len | emdash | offer |
|---|---|---|---|---|---|---|---|---|---|---|
| en-steps.style | 0 | 5.67 | 0 | 1.00 | 0 | 6.00 | 360.67 | 11.38 | 0 | 0.33 |
| en-steps.default | 0 | 6.33 | 0 | 4.67 | 0.33 | 8.33 | 408.00 | 9.67 | 0 | 1.00 |
| ko-steps.style | 0 | 5.67 | 0 | 0.50 | 0.17 | 6.33 | 241.50 | 39.84 | 0 | 0 |
| ko-steps.default | 0 | 7.00 | 0 | 4.33 | 1.00 | 9.17 | 284.50 | 34.57 | 0 | 0.33 |
| en-compare.style | 0 | 0 | 0 | 2.67 | 1.00 | 0 | 425.67 | 13.43 | 0 | 0 |
| en-compare.default | 0 | 0 | 1.00 | 4.00 | 1.00 | 0 | 438.33 | 14.27 | 0 | 1.00 |
| ko-compare.style | 0 | 0 | 0 | 2.00 | 1.00 | 0 | 317.00 | 38.42 | 0 | 0 |
| ko-compare.default | 0 | 0 | 3.33 | 6.33 | 1.00 | 1.00 | 323.67 | 34.38 | 0 | 1.00 |
| en-causes.style | 0 | 0 | 0 | 10.00 | 0 | 0 | 466.33 | 13.38 | 0 | 0.33 |
| en-causes.default | 4.00 | 6.67 | 2.33 | 19.67 | 0 | 3.00 | 579.33 | 9.92 | 0 | 1.00 |
| ko-causes.style | 3.67 | 5.00 | 0 | 13.67 | 0 | 0 | 406.67 | 41.93 | 0 | 0.33 |
| ko-causes.default | 3.33 | 7.33 | 4.00 | 22.67 | 0 | 9.33 | 415.00 | 48.85 | 0 | 1.00 |
| en-narrative.style | 0 | 0 | 0 | 1.00 | 0 | 0 | 228.67 | 16.27 | 0 | 0 |
| en-narrative.default | 3.00 | 0 | 0 | 3.67 | 0 | 0 | 272.33 | 13.31 | 0 | 0 |
| ko-narrative.style | 0 | 0 | 0 | 1.67 | 0 | 0 | 189.67 | 40.83 | 0 | 0 |
| ko-narrative.default | 0 | 3.67 | 0 | 4.67 | 0 | 3.33 | 217.00 | 32.75 | 0 | 0 |

### S1~S3 판정 (기본 조건 → 스타일, 모양이 나온 실행 수)

| 기준 | 셀 | 기본 | 스타일 | 판정 |
|---|---|---|---|---|
| S1 | en-steps 단계 | 3/3 | 3/3 | 통과 |
| S1 | en-steps 하위 단계 | 3/3 | 1/3 | **실패** |
| S1 | ko-steps 단계 | 6/6 | 6/6 | 통과 |
| S1 | ko-steps 하위 단계 | 4/6 | 1/6 | **실패** |
| S2 | en-compare 표 | 3/3 | 3/3 | 통과 |
| S2 | ko-compare 표 | 3/3 | 3/3 | 통과 |
| S3 | en-causes 목록 | 3/3 | 3/3 | 통과 |
| S3 | ko-causes 목록 | 3/3 | 3/3 | 통과 |

판정에서 뺀 셀은 없다. S1 하위 단계가 두 언어 모두 실패했으므로 구조 가설은 Sonnet 5.5에서 확인됐다. 스타일은 단계를 헤딩으로 남기지만, 하위 단계 내용은 헤딩 아래 문단으로 풀어 쓴다. 표와 목록은 이번 프롬프트에서 사라지지 않았다. 다만 목록 길이는 줄었다(en-causes bullets 19.67 → 10.00).

### S4~S6 기준값 (이후 회귀 판정용)

- **S4:** narrative 스타일의 tables는 6회 모두 0이다. headers 평균은 en 0, ko 0이고, numbered 평균은 en 0, ko 0이다. bullets 평균은 en 1.00, ko 1.67이다.
- **S5:** emdash는 모든 프롬프트에서 평균 0이다. 스타일 답변의 offer 합계는 3이다(`ko-steps` 추가 3회는 모두 0).
- **S6:** 스타일 `words` 평균의 합은 2636.2이고, 상한은 2899.8(×1.10)이다.

### L1 비율 (기록만)

| id | 스타일 | 기본 | r |
|---|---|---|---|
| en-steps | 11.38 | 9.67 | **1.177** |
| ko-steps | 39.84 | 34.57 | **1.152** |
| en-compare | 13.43 | 14.27 | 0.941 |
| ko-compare | 38.42 | 34.38 | 1.117 |
| en-causes | 13.38 | 9.92 | **1.349** |
| ko-causes | 41.93 | 48.85 | 0.858 |
| en-narrative | 16.27 | 13.31 | **1.222** |
| ko-narrative | 40.83 | 32.75 | **1.247** |

r ≥ 1.15인 프롬프트가 5개이고 평균 r은 1.133이다. 수정 전 스타일에서 이미 L1 진입 조건(3개 이상)을 넘는다. 계획대로 진입 판정은 Task 2를 통과한 문구로 측정한 값으로 한다. 스타일의 단어 수 합계는 기본 조건의 0.897배다. 분량은 줄었는데 문장은 길어졌으므로, 만연체 보고는 문장 하나의 길이 문제라는 가설과 맞는다.

## Task 2 시도 (모두 실패, 중단)

기본 조건은 `out-base`를 썼다(플러그인 차단이 되고 `claude --version`이 2.1.296으로 같다). 회귀 기준값은 위 기준선의 스타일 조건이다.

| 시도 | `:23` 등 문구 (계획 표 대비 바뀐 부분) | 본문 단어 |
|---|---|---|
| p2-1 | 계획 표 그대로: "Use numbered steps for sequences, with sub-steps nested, bullets for parallel items, tables for comparisons, paragraphs for reasoning, …" | 598 |
| p2-2 | "with sub-steps nested" → "nesting sub-steps as lists", "tables for comparisons" → "tables to compare options" | 600 |
| p2-3 | 서식 목록을 `:23`에서 `:7` 첫 문장으로 옮겼다: "Write natural, direct text in the user's language, matching form to content: numbered steps with nested sub-steps for sequences, bullets for parallel items, tables to compare options, paragraphs for reasoning." `:23`에는 "Use headings only when …"만 남기고, `:48`의 "form fits content,"는 뺐다 | 600 |

| 지표 | 기준선 스타일 | p2-1 | p2-2 | p2-3 |
|---|---|---|---|---|
| S1 하위 단계 en / ko | 1/3 / 1/6 | 0/3 / 1/3 | 0/3 / 0/3 | 2/3 / 0/3 |
| S3 causes 목록 en / ko | 3/3 / 3/3 | 3/3 / 2/3 | 2/3 / 2/3 | 1/3 / 2/3 |
| causes tables 평균 en / ko | 0 / 0 | 1.00 / 0.67 | 1.00 / 1.00 | 1.00 / 1.00 |
| S4 narrative bullets en / ko (상한 2.00 / 2.67) | 1.00 / 1.67 | 2.00 / 1.00 | **3.00** / 1.00 | **3.67** / **4.33** |
| S5 offer 합계 (상한 4) | 3 | 2 | 3 | 3 |
| S6 words 합계 (상한 2899.8) | 2636.2 | **2911.3** | 2821.7 | **2944.0** |
| L1 r ≥ 1.15 개수 / 평균 r | 5 / 1.133 | 5 / 1.189 | 6 / 1.201 | 4 / 1.172 |
| 판정 | S1 실패 | S1, S6 실패 | S1, S4 실패 | S1, S3, S4, S6 실패 |

S2(표)는 모든 시도에서 통과했고, emdash는 모든 시도에서 0이다. 표 규칙을 넣으면 원인 목록 질문(causes)까지 표로 답해 단어 수가 늘고 목록이 줄었다. 하위 단계 규칙은 어떤 문구로도 두 언어에서 함께 살아나지 않았다.

## 원인 분리 측정 (계획 밖, steps 프롬프트만)

시도 2 문구를 바탕으로 스타일 본문을 바꾼 사본을 `en-steps`, `ko-steps`에 3회씩 돌렸다. src는 바꾸지 않았다. 수치는 하위 단계가 나온 실행 수(en / ko)다.

| 변형 | 본문 | 하위 단계 |
|---|---|---|
| p2-2 | 시도 2 문구 전체 | 0/3 / 0/3 |
| V1 | "do not turn concision into fragments" 삭제 | 0/3 / 1/3 |
| V2 | `:7` "prose" → "text" | 0/3 / 1/3 |
| V4 | "previews of what follows" 삭제 | 1/3 / 0/3 |
| V5 | AI mannerisms 절 삭제 | 0/3 / 1/3 |
| V6 | Silent revision 절 삭제 | 1/3 / 1/3 |
| V7 | Prose 절에서 `:23`만 남김 | 0/3 / 1/3 |
| V9 | Language, Work reports 절 삭제 | 1/3 / 2/3 |
| V8 | `:7`과 `:23` 두 문단만 (102단어) | 1/3 / 0/3 |
| V10 | `:7`만 | 2/3 / 2/3 |
| V11 | `:23`만 | 2/3 / 3/3 |
| V3 | "Reply in the language the user writes in." 한 문장만 | 3/3 / 3/3 |

- **스타일 기능 자체는 원인이 아니다:** 본문이 거의 빈 V3에서는 하위 단계가 모두 나온다.
- **한 문장으로 켜고 끄는 스위치가 없다:** 어느 문장이나 절 하나를 빼도(V1, V2, V4~V7, V9) 살아나지 않는다. `:7`과 `:23`도 각각만 두면(V10, V11) 대체로 나오지만, 둘을 같이 두면(V8) 사라진다. 산문 쪽 지시가 쌓이는 만큼 목록이 줄어드는 누적 효과로 보인다. 다만 셀마다 3회라 방향만 보이고 크기는 알 수 없다.
- **기본 조건의 "하위 단계"는 대부분 병렬 항목이다:** 기본 조건 답변에서 단계 헤딩 아래 불릿은 "이 명령 하나로 다음이 한꺼번에 처리됩니다" 뒤의 효과 목록이나 "Optional" 팁이다. 실제 하위 동작은 두 조건 모두 코드 블록으로 쓴다. 스타일은 이 병렬 항목을 문단으로 풀어 쓴다.
