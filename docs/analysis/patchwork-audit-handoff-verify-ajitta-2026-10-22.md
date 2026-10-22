---
status: complete
revised: 2026-10-22
---

# 누더기 감사 정리 — 독립 검증

대상: `verify/roadmap-proof-handoff-6` @ 174c23cc, 기준 `git diff f0a78d56 HEAD`. 적용 표는 믿지 않고 파일과 실행으로 다시 확인했다.

**판정: 조건부 통과. Critical 0, Important 0, Suggestion 4.** 출하 문장은 맞다. 이제 단계 파일로 한 작업도 /sc:test → /sc:reflect를 거쳐 인덱스의 Plan-Close로 간다. `implement.md`, `RULES_DOCS.md`와도 어긋나지 않는다. 다만 새 가드는 고친 그 말("stands for that index")을 지키지 않아서, 감사 1의 원래 문장으로 되돌려도 green이다. 그리고 옛 assert 셋이 기록 없이 빠지거나 약해졌다.

## 실행

- `uv run pytest -q`: 3866 passed, 3 skipped, exit 0. `make lint`: All checks passed. `make typecheck`: 54 files, no issues.
- 변이 31개(`$TMPDIR/verify6-mut/mutate.py`, 하나씩 적용 → `test_docs_ssot_guards.py` → `git checkout HEAD -- <file>`). red 17, green 14. 끝난 뒤 `git status` 깨끗함.

## 감사 1–8, 5차 S1–S2

| 항목 | 판정 | 근거 |
|---|---|---|
| 감사 1 정의가 단계 파일 작업을 reflect 밖으로 보냄 | 해결 | 세 곳 모두 "…; a split plan's phase file, one its index lists with a checkbox, stands for that index". 가드는 못 지킴(N1) |
| 감사 2 기록이 되돌린 규칙을 현재형으로 적음 | 해결(일부 빠짐) | 상단 줄은 HEAD에서 참이고 표시 다섯 개도 맞다. 2차 표 3번 행에는 표시가 없다. 크기 31,085B(N4) |
| 감사 3 가드가 assert를 하나씩 더하며 자람 | 해결(손실 있음) | assert 12 → 5, 앵커는 `_GATE_ANCHORS`로 옮겼고 부정 고정과 라운드 주석은 없앴다. 옛 assert 셋이 빠지거나 약해짐(N2) |
| 감사 4 CHANGELOG 한 항목 | 해결 | 네 항목. 기여자 줄에 `reflect-plan-close-no-record` |
| 감사 5 roadmap no-op 절 | 안 함 | 소유자 ★ 보류 |
| 감사 6 docstring | 바꿔 쓰기만 함 | "every hook goes through build_parser (… the hooks do not)": 한 문장 안에서 모순(N3) |
| 감사 7 review 핸드오프 5개 | 안 함 | 소유자 ★ 유지 |
| 감사 8 plan Save "source" | 안 함 | 대기 목록 |
| 5차 S1 reflect README 문장 무가드 | 해결 | 앵커 추가. 3차 문장으로 되돌리면 red(R6). 조건을 뒤에 붙이면 green(R7, 알려진 한계) |
| 5차 S2 되돌림 표시 | 해결 | 1차·2차-4·3차-1·3차-2·3차-4 행에 표시 |

## 규칙 목록

| 규칙 | HEAD 위치 | 가드 |
|---|---|---|
| plan 문서 정의(05-plan, `05<letter>`, docs/plans) | reflect:19, test:17, RULES_DOCS:87 | `05<letter>` 앵커 ×3 (T4 red) |
| 단계 파일 = 인덱스 | 같은 세 곳 | 주어 "split plan's phase file"만 지킨다. 술어는 무가드(N1) |
| README `complete` = plan (index) 하나 | reflect:19, RULES_DOCS:33 | 긍정 앵커 둘. "with task boxes" 부정 고정은 제거(P1 green) |
| roadmap Proof 꼬리말 | roadmap:17 | "`` `## Proof` footer ``"만. 완화와 부정은 green(N2) |
| roadmap → implement만 / review → design | roadmap:68, review:76 | 그대로 |
| RULES_DOCS roadmap 관문 | RULES_DOCS:84 | 화살표만. "Roadmap document committed"는 빠짐(N2) |
| verifier 경로 | test:40 | "the plan doc the work ran from"만. "pass it that path"는 빠짐(N2) |
| implement 첫 박스 | implement:19 | Integrate 줄의 "when it is not already further" (범위가 줄로 좁아져 더 정확함) |

옛 assert → 새 가드: ① Proof 문장 → 짧은 구절(약해짐) ② roadmap 핸드오프 → 같음 ③ review /sc:design → 같음 ④–⑥ 정의 ×3 → 앵커 둘 ×3(술어 없음) ⑦ 관문+"Roadmap document committed" → 화살표만 ⑧ README 매핑 → 같음 ⑨ "with task boxes" 부정 → 삭제(감사가 의도한 것) ⑩ "compares with the plan doc…" → 앞말 없이 ⑪ "pass it that path" → **삭제(감사안에도 기록에도 없음)** ⑫ "to `implementing` when…" → Integrate 앵커.

## 다시 쓰기 A 점검

- 단계 파일로 일함 → 정의에 들고 "stands for that index" → test Report가 "not done until /sc:reflect" → Plan-Close "check its plan (index)" → 인덱스의 박스가 남아 있으면 "an open box … to /sc:implement --plan". 막다른 상태 없음.
- `implement.md:13` Load(인덱스를 읽고 단계 파일은 그 단계에서 읽음), `:19` Integrate(단계 파일은 박스가 다 차면 `complete`, Proof와 README는 인덱스만)와 맞물린다. `RULES_DOCS.md:13`(인덱스에 단계마다 체크박스 하나), `:33`, `:58`과도 모순 없다. 단계 파일 `complete`는 README를 움직이지 않는다.
- 단계 파일은 첫 절("another `05<letter>-plan-*.md` plan")에도 들어맞는다. 둘째 절이 바로 그것을 인덱스로 돌리고 Plan-Close 대상도 "(index)"라서, 따로 세는 plan으로 읽힐 자리는 없다.

## 변이 (green만 개별 표기)

| 변이 | 결과 |
|---|---|
| D2/T2/R2 "stands for that index" → "is not a plan document" (세 파일) | **green** ×3 |
| D3/T3/R3 정의를 감사 전 문장으로 되돌림 (세 파일) | **green** ×3 |
| R7 reflect README 뒤에 "once every other plan in the folder is `complete`" | **green** |
| P1 RULES_DOCS 매핑 뒤에 3차 조건 덧붙임 | **green** (옛 부정 고정이면 red) |
| I4 implement: 앵커는 두고 README를 "also when it is already further"로 | **green** (인위적) |
| G2 "Roadmap document committed; " 삭제 | **green** (옛 가드면 red) |
| G3 "and ends with its Proof footer" 삭제 | **green** (옛 가드도 green) |
| Q2 "You may end the doc…" / Q3 "Do not end the doc…" | **green** ×2 (옛 가드면 red) |
| V1 "pass it that path" 삭제 | **green** (5차에서 red였음) |
| red 17: D1, D4(need not), T1, T4, R1, R4(unless), R5, R6, R8(may), R9(not), I1, I2, I3(unless), G1(/sc:task), P2, Q1, V2 | red |


## 새 발견

**N1. Suggestion — 다시 쓰기 A의 술어를 가드가 지키지 않는다.** 앵커 "split plan's phase file"은 일부러 옛 문장과 새 문장 둘 다에서 통과하게 골랐다(감사의 "앵커는 지금 문장과 다시 쓰기 A 둘 다에서 통과한다"). 그래서 감사 1의 Important 문장으로 되돌려도 green이다(D3, T3, R3). 지금 문장이 맞으므로 Suggestion이다. 수정: 세 목록(`gates`, `test Report`, `reflect Plan-Close`)의 "split plan's phase file"을 "stands for that index"로 바꾼다(각 파일에 한 번씩 나온다).

**N2. Suggestion — 옛 assert 셋이 기록 없이 빠지거나 약해졌다.** "pass it that path"(V1), "Roadmap document committed"(G2), roadmap Proof 문장(Q2, Q3: `roadmap.md`는 `_SOFTENER` 범위 밖이라 구절 앵커가 완화를 못 잡는다). 적용 표(감사 3 행)는 "옮겼다"고만 쓴다. 수정: 핸드오프 테스트에 `"pass it that path" in test_md`와 `"End the doc with a \`## Proof\` footer" in roadmap`를 돌려놓고, `gates`에 "Roadmap document committed"를 더한다. 아니면 적용 표에 뺀 것과 그 이유를 적는다.

**N3. Suggestion — 감사 6 docstring이 한 문장 안에서 모순된다.** `tests/unit/test_insight_writer.py:1824`: "every hook goes through build_parser (`superclaude insight`; the hooks do not)". 적용 표는 "훅은 build_parser를 거치지 않는다고 고쳤다"고 쓰지만, "every hook goes through"가 그대로 남아 있다. 수정: "python -OO … strips docstrings; `superclaude insight` goes through build_parser (the hooks do not), so it must not need the module's."

**N4. Suggestion — 기록의 표시 하나가 빠졌고, 추가분이 크기 경계를 넘겼다.** `command-handoff-graph-ajitta-2026-10-22.md:278`(2차 표 3번 행)은 "that is not a split plan's phase file" 정의를 적는다. 이번 정리가 바꾼 정의인데 표시가 없다. 상단 줄의 "뒤 라운드가 바꾼 행에는 표시를 달았다"와 어긋난다. 그리고 파일이 28,715 → 31,085B가 되어 `file_size_guard.py`의 30,000을 넘었다. 이제 한 번에 Read하면 막힌다. 늘어난 곳은 소유자 결정 3(상단 줄 + 행 표시만)에 없던 "5차 검증과 누더기 감사 반영" 절(약 1.8KB)이다. standalone 문서라 분할은 없다(RULES_DOCS:14). 수정: 그 행에 "(누더기 감사에서 '단계 파일은 인덱스로 센다'로 바뀜)"을 붙이고, 새 절은 두 검증 문서로 가는 링크와 한두 줄로 줄인다. 상단 줄이 이미 현재 상태를 말하므로 30,000 아래로 내려간다.

## CHANGELOG·상단 줄

`[Unreleased]` 다섯 항목은 HEAD에서 참이다. 사용자 동작으로 쓰였고, 되돌린 규칙을 현재형으로 적지 않는다. 상단 줄의 정의, README 규칙, 열린 항목도 HEAD와 맞는다.
