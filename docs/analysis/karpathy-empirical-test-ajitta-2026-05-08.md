---
title: Karpathy Empirical Test — /sc:* Commands
type: analysis
author: ajitta
date: 2026-05-08
session: karpathy-empirical-validation
parent: docs/analysis/karpathy-command-impact-ajitta-2026-05-08.md
---

# Karpathy Empirical Test — /sc:* Commands

> Companion doc: empirical 1-shot validation of predictions in `karpathy-command-impact-ajitta-2026-05-08.md`. Each command is run twice via `claude -p` — once baseline, once with karpathy 4-axis prefix forced into the user message.

## Methodology

### Setup
- Tool: `claude -p "<prompt>"` (Claude Code CLI, version 2.1.132, headless)
- Repo: this fork, SuperClaude installed at `~/.claude/`
- N: 1 per condition (baseline / karpathy) — cost-bounded, **not statistical**. Reading these as direction-of-effect, not magnitude.

### Karpathy activation method
The skill is normally trigger-activated. In headless mode skill auto-trigger is unreliable, so the karpathy 4 axes are embedded directly in the first user message:

> Apply Karpathy guidelines strictly: (1) Surface assumptions, present alternatives, ask when unclear — don't pick silently. (2) Minimum viable, no speculation, no flexibility/configurability that wasn't requested. (3) Surgical changes only, every output traces directly to user request. (4) Define verifiable success criteria up-front. Then run: `<command>`

### Metrics (4 axes)
| Axis | Probe |
|---|---|
| **TBC** Think-Before-Coding | Does first response surface ≥2 alternatives / ask when ambiguous / refuse silent pick? |
| **SF** Simplicity-First | Does it apply R18 (necessity test) explicitly? Defer features it can't justify? |
| **SC** Surgical-Changes | Does it bound scope to user request, refuse adjacent cleanup? |
| **GDE** Goal-Driven | Does it state verifiable success criteria up-front? |

### Verdict per metric
- ✅ Predicted change observed
- ⚠️ Direction correct but smaller than predicted
- ❌ Not observed
- ⚪ Already in baseline (skill = no delta)

---

## Test 1: `/sc:brainstorm '팀 task 트래커'`

**Matrix prediction**: ✅✅ Strong reinforce — alternatives + verifiable criteria up-front; selection-protocol formatting; silent-pick refusal.

### Run A — Baseline output (excerpt)
```
가정한 컨텍스트
- 사용자 = SuperClaude 개발자
- 결과물 = 표준 discovery 사양서 (docs/specs/)
이 가정이 틀렸다면 한 줄로 정정해주시고, 맞다면 "go"로 진행하겠습니다.

## /sc:brainstorm — '팀 task 트래커' 탐색 v0
### 첫 번째 분기: 문제의 형태
[A] AI 에이전트 작업 트래커
[B] 개발팀 협업 트래커
[C] 하이브리드 (사람 + AI)

### 답변해 주실 것
1. A / B / C 중 어디
2. 이걸 만드는 이유 한 줄
3. 사용자/규모 한 줄
```

### Run B — With karpathy prefix (excerpt)
```
## 브레인스토밍 시작 전 — 모호성 표면화 (Karpathy 1)
이번엔 말없이 가정하지 않습니다.

### 의도 재확인 (R13)
"팀 task 트래커"라는 단어만으로는 무엇을 누구를 위해 만들지 결정할 수 없음.

### 이 브레인스토밍 세션의 성공 기준 (R20)
- 출력물: docs/specs/<slug>-discovery-ajitta-2026-05-08.md 1개
- 내용 요건: 확정된 archetype 1개 + 핵심 요구사항 3-5개 + non-goals 명시
- 종료 조건: /sc:review 핸드오프 가능 상태

### 표면화한 가정 3개
#### Q1. 누구의 task를 추적합니까? (archetype 결정)
[A] AI agent task tracker ★
[B] 사람 팀 협업 트래커
[C] 하이브리드 (사람 N + AI agent M)
select: A / B / C / 직접 작성

#### Q2. 새로 만드나, 기존 도구를 래핑하나?
[a] 신규 도구 / [b] 기존 위에 얇은 래퍼 ★ / [c] 단순 프로세스
select: a / b / c

#### Q3. 어디에 살 것인가?
[a] 이 superclaude repo 내부 / [b] 별도 / [c] 미정
select: a / b / c

Necessity test (R18) 메모: 셋 다 답하기 전엔 spec 안 씁니다.
침묵·"yes"·"proceed" 만으로는 진행하지 않음 — Karpathy 1번이 silent pick을 명시적으로 금지하므로.
```

### Verdict matrix
| Axis | Predicted | Observed | Verdict |
|---|---|---|---|
| **TBC** | ≥2 alts, refuse silent pick | A: 3 archetypes, gentle; B: 3 archetypes ★ + 2 secondary alt sets (Q2/Q3) + explicit silent-pick refusal | ✅ B stronger |
| **SF** | R18 deferral pressure | A: implicit; B: explicit "Necessity test (R18) 메모" + "셋 다 답하기 전엔 spec 안 씁니다" | ✅ B explicit |
| **SC** | (n/a, read-only first-turn) | both: no code-modifying intent | ⚪ |
| **GDE** | Verifiable criteria up-front | A: "사양서 docs/specs/" — loose; B: 4-element criteria (path + 3 content reqs + handoff condition) | ✅ B sharper |

### Calibration
- **Baseline already strongly karpathy-shape.** Run A produced 3 alternatives + named completion target unprompted.
- **Skill activation tightens citation, not behavior shape.** Run B inserted explicit `R13`, `R18`, `R20`, `Karpathy 1` references that A omitted.
- **New behavior in B**: ★ recommendation marker (selection-protocol per RULES.md), explicit silent-pick refusal, hard-floor on `select:` parsing.
- Matrix predicted "Strong reinforce" — actual delta closer to "moderate" because baseline already covers ~70% of the predicted shape. **Recommendation**: downgrade brainstorm matrix entry from ✅✅ to ✅ for first-turn-shape effect; keep ✅✅ for citation-explicitness effect.

---

## Test 2: `/sc:design '간단한 노트 API'`

**Matrix prediction**: ✅✅ Strong reinforce — R18 per component, never modify existing arch, ≥90% req coverage, deferred-with-trigger items.

### Run A — Baseline output (verbatim, brief)
```
Design spec written to `docs/specs/simple-note-api-design-ajitta-2026-05-08.md` —
REST CRUD on a single `notes` resource, cursor pagination, no auth (deferred with trigger),
schema portable across SQLite/Postgres. Assumptions are surfaced in §1; six features
deferred per R18 in §7 with revisit triggers.

If any assumption is wrong (auth needed now, multi-user, GraphQL instead of REST,
different stack), say so and I'll revise. Otherwise next step is `/sc:plan` against
this spec.
```

**Side effect**: spec file actually created at `docs/specs/simple-note-api-design-ajitta-2026-05-08.md`.

### Run B — With karpathy prefix (verbatim, abbreviated)
```
Stopping before invoking `/sc:design`. Applying Karpathy strict mode (#2 minimum viable,
#3 surgical, #4 verifiable criterion) to the existing spec yields a clear answer:
**the prior spec already satisfies the success criterion I defined for this run.**

## Verification against the up-front criterion
> Criterion: design exists with (a) four required sections and (b) every component passes R18.
[Match table — 6 checks all pass]

## Why re-running `/sc:design` violates Karpathy strict mode
- #2 (no speculation): identical brief → near-duplicate output
- #3 (surgical): overwriting equivalent same-day artifact = churn
- #4 (verifiable criterion): "run again" has no defined improvement target

## What I need from you to proceed meaningfully
1. A specific assumption to overturn
2. A specific section to refine
3. Force overwrite anyway (will produce ~80% overlap)
4. Cancel — existing spec stands; move on to /sc:plan
```

### Verdict matrix
| Axis | Predicted | Observed | Verdict |
|---|---|---|---|
| **TBC** | R18 per component | A: §2 Necessity Audit + §7 deferred items; B: refused to re-run, cited prior R18 audit | ✅✅ B exceeds prediction |
| **SF** | Defer features that fail necessity | A: 6 features deferred in §7; B: refused entire re-run on necessity grounds | ✅✅ B exceeds prediction |
| **SC** | Never modify existing arch | A: created new file; B: refused to overwrite existing, framed it as churn | ✅✅ B exceeds prediction |
| **GDE** | ≥90% req coverage / verifiable | A: §8 self-validation 5/5; B: explicit "criterion = match against existing spec" check matrix | ✅ both |

### Calibration (new pattern observed)
- **Run A produced the artifact unconditionally.** Despite design's `<gotchas>` having `existing-check`, Run A skipped that check and wrote the spec.
- **Run B activated `existing-check` as a hard gate.** Karpathy's #2/#3/#4 forced Run B to detect the prior artifact, evaluate against it, and refuse re-execution.
- **New behavior**: Run B's selection-protocol with 4 options + explicit "delta criterion required to proceed" framing. Matrix predicted "Strong reinforce", actual was **"Strong refusal"** — qualitatively different mode (not just stronger same-direction output, but a *gate* that blocks execution).

---

## Test 3: `/sc:troubleshoot '로그인 후 5분 만에 세션이 만료된다' --type bug`

**Matrix prediction**: ✅✅ Strong reinforce — Reproduce step 1 (R03 alignment), 3+ hypotheses cap, "no while-I'm-here fixes", failing-test-passes gate.

### Run A — Baseline output (excerpt)
```
이 저장소(`superclaude`)는 Claude Code 콘텐츠 프레임워크이며, 로그인/세션 코드가 없습니다.
실제 진단을 하려면 문제가 발생한 코드베이스가 필요합니다. 그럼에도 evidence-fabrication
gotcha를 지키면서 — 증거 없이 가설을 사실처럼 단정하지 않고 — 일반적으로 "로그인 후
정확히 5분"이라는 증상에서 가능성 높은 가설들을 단순한 순서로 나열하겠습니다.

[H1-H6: JWT exp / cookie maxAge / Redis TTL / refresh-token / idle-vs-absolute / proxy idle]

H1이 가장 흔하고 확인 비용도 가장 낮으므로 먼저 검증할 후보입니다.

select: 1 (실제 코드 경로 제공) / 2 (가상 시나리오 — 명령 분석 모드)
       / 3 (가설 H1-H3을 일반론으로 더 깊게 풀어봐 달라)
```

### Run B — With karpathy prefix (excerpt)
```
질문 도구 사용이 거부되었습니다. Karpathy strict 모드에서 증거 없이 추측 답변을
만드는 것 또한 금지되므로, 다음의 형태로 정지 상태를 명시합니다.

## /sc:troubleshoot 실행 결과 — STOP (insufficient evidence)

### 발견 사항 (사실)
- session|login|auth|expir|JWT|token grep 결과 20건 모두 마크다운 문서. 실제 코드 매칭 0건.
- *.py|*.ts|*.js|*.go|*.java glob 결과: 인증·세션을 다루는 모듈 부재.

### Karpathy 규칙 적용
| 축 | 적용 |
| TBC | file:line 증거 0건 → 가설 0건 |
| SF  | 일반론적 체크리스트 생성하지 않음 |
| SC  | 변경 가능한 라인 0개 |
| GDE | 검증 가능한 성공 기준 정의 불가 |

### 명령 본문 규칙 위반 회피
<gotchas> evidence-fabrication: "Evidence (code, config, measurements) must precede proposals."
→ 거부: 가능한 원인 N가지 나열, 각 원인별 체크리스트, 일반적 OAuth/JWT/cookie 설명.
```

### Verdict matrix
| Axis | Predicted | Observed | Verdict |
|---|---|---|---|
| **TBC** | 3+ hypotheses, simplest first | A: 6 hypotheses; B: **0 hypotheses** ("evidence 0 → hypotheses 0") | ✅✅ B exceeds via refusal |
| **SF** | Single change, no while-I'm-here | A: would have stopped at H1 verify; B: refused all generic checklists | ✅✅ B exceeds |
| **SC** | Root-cause only | (n/a — no fix issued) | ⚪ |
| **GDE** | Failing test before fix | A: implicit; B: explicit pre-defined criterion (t=4min/t=6min reproduction test) | ✅ B explicit |

### Calibration
- **Run A "softly" cited evidence-fabrication.** Then proceeded to provide 6 hypotheses anyway, framing them as "통계적 추측".
- **Run B "hardly" enforced evidence-fabrication.** Generated zero hypotheses, ran actual grep to confirm absence of auth code, refused even general checklists.
- This matches the Test 2 pattern: baseline gotcha is advisory; karpathy makes it a hard gate.

---

## Test 4: `/sc:task 'TODO 앱 — vanilla JS, frontend only, 4-5 files'`

**Matrix prediction**: ✅✅ Strong reinforce — 3-7 decomposition cap, >3 files checkpoint, already-done check, completion verification.

### Run A — Baseline output (verbatim, brief)
```
Done. 4 files created at `todo-app/`, all syntactically valid.

| File | Role |
| todo-app/index.html | Markup + form + filter tabs + list slot |
| todo-app/styles.css | Minimal styling, focus rings, Korean-friendly font stack |
| todo-app/storage.js | localStorage wrapper |
| todo-app/app.js     | IIFE: render, add/toggle/remove, all/active/done filter |

Verification: node --check on both JS files: syntax OK.

## Two things to flag
1. Stop-hook is misfiring — make can't parse Windows path with colon
2. Repo placement — todo-app/ dropped at framework root (rm -rf if wrong location)
```

**Side effect**: 4 files actually created in `todo-app/`. >3 files checkpoint **skipped** despite gotcha presence.

### Run B — With karpathy prefix (verbatim, abbreviated)
```
## Decision point (Karpathy: ask, don't pick)

The requested deliverable **already exists and meets all stated constraints**:
| Constraint | Required | Existing |
| Stack       | vanilla JS         | yes |
| Scope       | frontend only      | yes |
| File count  | 4-5 files          | 4 files |

Per Karpathy "minimum viable": re-executing would duplicate work or introduce
changes not traceable to your request. R18 Necessity Test fails.

Per Karpathy "ask when unclear": I will not silently pick a direction.

### Options
1. Skip — task already complete
2. Review existing for correctness (read-only)
3. Overwrite with fresh implementation
4. Add a missing capability (specify which)

select: 1, 2, 3, or 4. Default if you say "proceed" without picking: 1 (skip).
```

### Verdict matrix
| Axis | Predicted | Observed | Verdict |
|---|---|---|---|
| **TBC** | dependency analysis, >3 files checkpoint | A: skipped checkpoint, created 4 files directly; B: refused, presented 4 options | ✅✅ B exceeds; A failed |
| **SF** | 3-7 task cap, no over-decomposition | A: implicit (no decomposition shown); B: explicit "R18 Necessity Test fails" | ✅✅ B explicit |
| **SC** | scope-bounded | A: created files at framework root (questionable scope); B: refused new artifacts | ✅✅ B refused |
| **GDE** | completion verification | A: post-hoc syntax check; B: pre-stated 4 success criteria options | ✅ B pre-stated |

### Calibration (most striking gap)
- **Run A *failed* the >3 files checkpoint.** Task `<flow>` step 4 says "If changes affect >3 files → present numbered plan → wait for user approval". Run A created 4 files without that checkpoint.
- **Run B caught the duplication.** Detected pre-existing `todo-app/` (created by Run A), framed re-execution as `R18 fail`.
- **New behavior**: 4-option selection-protocol with default-on-silence ("proceed" → skip). Matches Test 2 (design) and Test 3 (troubleshoot) pattern.

---

## Cross-Test Synthesis

### The pattern: "command refusal mode"
Three of four commands (design, troubleshoot, task) under karpathy strict prefix entered a **refusal mode** that does not exist in baseline:

| Test | Refusal trigger | Selection-protocol options |
|---|---|---|
| design | existing artifact already satisfies criterion | 4 options (overturn / refine / overwrite / cancel) |
| troubleshoot | evidence absent → can't form hypotheses | implicit (3 information-request options) |
| task | deliverable already exists, all constraints met | 4 options (skip / review / overwrite / extend) |

Brainstorm did not enter refusal mode because no precondition (existing spec, evidence, deliverable) was present — but it *did* tighten its citation rate.

### Matrix corrections needed

| Command | Old matrix | Empirical refinement |
|---|---|---|
| /sc:brainstorm | ✅✅ Strong reinforce | ✅ Moderate (baseline already covers most) — citation-explicitness uplift remains ✅✅ |
| /sc:design | ✅✅ Strong reinforce | **✅✅✅ Strong + refusal mode** — karpathy promotes existing-check gotcha to hard gate |
| /sc:troubleshoot | ✅✅ Strong reinforce | **✅✅✅ Strong + refusal mode** — evidence-fabrication promoted to absolute prohibition |
| /sc:task | ✅✅ Strong reinforce | **✅✅✅ Strong + refusal mode + caught a baseline rule violation** (skipped >3 files checkpoint) |

### Two findings the original matrix missed

**1. Karpathy promotes `<gotchas>` from advisory to hard-gate.**
Each command file has gotcha rules that *should* fire (existing-check, evidence-fabrication, scope-discipline). Baseline runs cite them softly or skip them. Karpathy strict mode makes them blocking.

**2. Selection-protocol becomes the default exit when refusal triggers.**
Run B outputs (design, troubleshoot, task) all converge on "stop + present numbered options + define default-on-silence". This is RULES.md's `<selection_protocol>` firing under karpathy pressure — same protocol, much more aggressive activation.

### One unrelated finding (worth flagging)
Test 4 surfaced a **hook misfire**: Stop-hook runs `make -C 'C:\Users\ajitta\Repos\ajitta\superclaude' test` after each Write. Windows make can't parse the path (`make: Invalid argument`). The hook reports "Tests FAILED" but the failure is the hook's own argument error, not a real test failure. Located in `.claude/settings.json`. Not part of karpathy validation; reporting because Run A noticed it and the user should know.

---

## Limitations (carry-over from matrix doc)

- **n=1 per condition.** Direction-of-effect only; magnitudes are not reliable.
- **Karpathy via prefix injection ≠ skill activation.** Real skill activation may have additional behaviors (slot in deeper system context, interact with other skills) that prefix injection misses.
- **Toy topics.** Real-world tasks have richer context that may shift the refusal-vs-execute boundary either direction.
- **Side effects landed in repo**: `docs/specs/simple-note-api-design-ajitta-2026-05-08.md`, `todo-app/` directory. Both reversible (`rm`).

## Recommended next steps

1. **Update parent matrix doc** to reflect refusal-mode promotion for design/troubleshoot/task. (Section 3 cross-cutting patterns + per-command behavioral delta.)
2. **Replicate with n=3** on at least one command to estimate magnitude variance.
3. **Test on remaining ✅✅ commands** (implement, improve, plan, review) to check whether refusal-mode pattern generalizes.
4. **Fix the hook misfire** in `.claude/settings.json` (independent of karpathy work).

