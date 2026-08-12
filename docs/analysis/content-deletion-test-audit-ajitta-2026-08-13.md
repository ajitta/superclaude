---
status: draft
revised: 2026-08-13
---

# commands / skills / core — deletion test 감사

`.claude/rules/content-quality.md`의 deletion test로 `src/superclaude/`의 세 콘텐츠 영역을 감사했다.
기준은 하나다 — **"이 문장을 지운 출력이 남긴 출력과 같으면, 그 문장은 필요 없다."**

대상: core 9파일(37KB), skills 13파일(43KB), commands 36파일(125KB). 네 개의 독립 감사로 나눠 읽고,
반환된 주장은 전부 file:line을 직접 재검증했다. 아래에 남긴 것은 재검증을 통과한 것뿐이다.

## 판정 요약

프루닝 후보보다 **라이브 결함이 먼저다.** 여섯 곳에서 커맨드가 다른 파일이 금지한 것을 지시하거나,
아무도 생산하지 않는 값을 게이트로 걸고 있다. 이건 "지우면 좋을 문장"이 아니라 지금 잘못된 출력을
만드는 코드다.

프루닝 대상은 실재하지만 분포가 진단적이다. 모델이 유도할 수 없는 주제를 다루는 파일
(`auto-improve.md`, `insight.md`, `RULES_DELEGATION.md`, `RULES_INTERACTION.md`)은 거의 손댈 게 없고,
일반적인 엔지니어링 판단을 다루는 파일(`spec-panel.md`, `cleanup.md`, `roadmap.md`, `PRINCIPLES.md`)에
집중된다.

---

## 1. 라이브 결함 (여섯 건)

### D1 — `/sc:agent`가 스킬이 만들 수 없는 숫자로 게이트를 건다

```
commands/agent.md:29   - @confidence-check (pre-impl score ≥0.90 required)
commands/agent.md:32   - Phase 3 - Iterate: Track confidence; no impl below 0.90; escalate if stalled
commands/agent.md:67   <never>speculate without research and impl below 0.90 confidence.</never>

skills/confidence-check/SKILL.md:42   <never>score/percent compute, runtime check, modify artifact.</never>
```

스킬은 Proceed/Stop만 반환하고 점수 계산이 **금지돼 있다.** `/sc:agent`를 실행한 모델은 게이트를 통과하려면
숫자를 지어내는 수밖에 없다. `≥0.90`은 71줄 안에 다섯 번 나온다(`:29 :32 :40 :45 :67`).
덧붙여 `@confidence-check`는 에이전트 위임 문법인데 `agents/confidence-check.md`는 존재하지 않는다
(같은 목록의 `@deep-researcher`, `@repo-index`는 실재).

**지우면**: 실행이 스킬의 실제 Yes/No 판정으로 진행된다. 남기면 날조된 `0.92`가 근거로 보고된다.

### D2 — `/sc:design`이 아무도 계산하지 않는 커버리지로 게이트를 건다

```
commands/design.md:18   6. Validate: Requirements coverage ≥90%, maintainability check
```

`"Requirements coverage"`는 저장소 전체에서 **이 줄 하나**다. flow 1단계 `Analyze: Requirements + existing context`는
요구사항을 열거하지 않으므로 분모가 없다. `maintainability check`도 도구·산출물을 지목하지 않는다. D1과 같은 형태.

### D3 — `/sc:troubleshoot`가 커널 규칙을 뒤집는다

```
commands/troubleshoot.md:14   5. Test: Write failing test reproducing exact bug (required before any fix)
commands/troubleshoot.md:15   6. Fix: Apply single change addressing root cause
commands/troubleshoot.md:10   <syntax>... [--trace] [--fix]</syntax>
```

`--fix` 플래그가 선언돼 있는데 flow 5~7단계에 `(if --fix)` 조건이 없다. `build.md:16`이
`4. Optimize: Artifacts + bundle size (if --optimize)`로 하우스 컨벤션을 보여주는데 여기만 빠졌다.
그리고 description은 증상 서술만으로 자동 발동한다.

충돌 상대는 항상 로드되는 커널이다 — `core/RULES.md:15`: *"the deliverable is the assessment: report findings and stop."*
사용자가 "API가 가끔 타임아웃 난다"고만 말해도 모델이 테스트를 쓰고 코드를 고친다.

**이 저장소에서 프레임워크가 있는 쪽이 없는 쪽보다 나쁘게 행동하는 유일한 지점이다.**

같은 파일 안의 2차 모순: `:59` `<safe>Typos, missing imports, simple config errors</safe>`는 자동 수정 가능이라 하는데,
`:14`는 "any fix 전에 실패 테스트 필수"라고 한다. 빠진 import를 재현하는 실패 테스트는 쓸 수 없다.

### D4 — `test`/`build`가 금지된 파일 출력을 선언하고, 금지 규칙은 그때 로드되지 않는다

```
commands/test.md:34    - Write: Coverage reports + summaries
commands/build.md:34   - Write: Build reports

core/rules/RULES_DOCS.md:28   Inline only (no file output): test, build, cleanup — console + tool artifacts
```

두 커맨드의 `<outputs>` 표에는 모델이 쓰는 파일이 한 줄도 없다. 그런데 결정적인 건 로더다 —
`scripts/context_loader.py:175`의 정규식은
`/sc:(document|plan|design|brainstorm|roadmap|index|index-repo|estimate|save|research|promote-feature)`이고
**`test`와 `build`가 없다.** 금지 규칙이 컨텍스트에 아예 없는 상태에서, 모델이 보는 유일한 파일 출력 지시가
`Write:`다. 중복이 결함으로 바뀌는 지점이 여기다.

### D5 — `/sc:brainstorm`의 handoff가 같은 파일이 금지한 경로를 제시한다

```
commands/brainstorm.md:26   Direct route to /sc:plan from step 5 forbidden.
commands/brainstorm.md:83   <handoff next="/sc:review /sc:plan /sc:design /sc:research"/>
```

`<handoff next>`는 모델이 읽는 다음 단계 계약이다. 금지된 경로가 아무 표시 없이 필수 경로 옆에 있다.
(`<handoff>`를 권한이 아닌 네비게이션 안내로 읽으면 모순이 아니라는 반론이 성립한다 — 이 건은 여섯 중 가장 약하다.)

### D6 — `/sc:select-tool`이 정의되지 않은 점수로 도구를 고른다

```
commands/select-tool.md:14   2. Score: multi-dim complexity
commands/select-tool.md:25   - Threshold >0.6: Serena (accuracy)
commands/select-tool.md:26   - Threshold <0.4: Native tools (speed)
```

차원도 가중치도 공식도 없다. 저장소 어디에도 complexity score 정의가 없다(연구 신뢰도 점수는 다른 값).
D1·D2와 같은 형태로, 세 번째 사례다.

**부수**: `commands/index.md:17` `5. Maintain: Preserve <!-- MANUAL --> marked sections` —
`MANUAL`은 저장소 전체에서 이 줄 하나다. 마커를 만드는 곳이 없다.

---

## 2. deletion test를 통과하지 못하는 것들

### P1 — 항상 로드되는 층의 모델 네이티브 재진술

이번 세션이 실측한 것이 여기에 걸린다. 프레임워크 없는 vanilla 아암이 네 행동을 동일하게 수행했다.

| 위치 | 텍스트 | 상태 |
|---|---|---|
| `core/RULES.md:15` | "the deliverable is the assessment: report findings and stop" | `problem-statement-not-request` 픽스처가 이 문장을 겨냥 — vanilla 동점 |
| `core/PRINCIPLES.md:4` | `Code reality > documentation` | `misleading-evidence` 픽스처가 이 줄을 인용 — vanilla 동점 |
| `commands/review.md:67` | `no-unsolicited-fixes: flag issue but no fix unless asked` | 위 커널 문장의 세 번째 사본 |

**과승격 금지.** 측정은 n=1, 프롬프트 4종, sonnet 1종, 전부 쉬운 케이스였고, *문장 하나*가 아니라
*프레임워크 전체*를 뺀 비교였다. 삭제 근거로는 부족하다. 다만 이 저장소가 요구하는 증거의 형태이기는 하다.

### P2 — 하네스가 더 높은 권위로 이미 말하는 것

```
core/RULES.md:27   Project-level rules and conventions (CLAUDE.md, project gotchas, docs conventions)
                   override general defaults and personal style.
```

Claude Code는 CLAUDE.md를 주입하면서 system-reminder로 감싼다 — *"These instructions OVERRIDE any default
behavior and you MUST follow them exactly as written."* 같은 세션, 같은 지시, 더 높은 권위.
(단, 같은 블록의 `.claude/rules/gotchas/` 캡처 제안은 하네스에 없는 내용이라 남는다.)

### P3 — 파일 내부 자기중복

- `core/rules/RULES_QUALITY.md:61-69` — `<thresholds>` 6줄 중 5줄이 **같은 파일** 안(20줄 위)을 가리킨다.
  파일은 통째로 주입되므로 포인터가 가리키는 대상이 이미 컨텍스트에 있다.
- `core/PRINCIPLES.md:13` `Restraint-First: build only what asked` — `RULES.md:15`가 같은 import 체인에서
  더 구체적으로 말한다(네 번째 사본은 `RULES_QUALITY.md:11`, 다섯 번째는 `implement.md:47`).
- `commands/promote-feature.md` — slug-collision 4회(`:16 :47-51 :61 :70`).
- `commands/brainstorm.md` — self-review 게이트 5회.

### P4 — 아무것도 지목하지 않는 flow 단계

```
commands/task.md:18      6. Validate: Quality gates + completion verification
commands/roadmap.md:17   5. Validate: Quality gates + workflow completeness
```

`"quality gate"`는 저장소 전체에서 이 두 줄뿐이고 정의가 없다. 같은 유형:
`git.md:12-18`(4단계 전부), `cleanup.md`(1·2·5단계), `spec-panel.md`(5단계 전부가 아래 섹션의 재진술),
`select-tool.md:14`.

대조군으로 `index-repo.md:18` `6. Validate: both files exist + size <5KB each` — 파일과 측정 가능한 한계를
지목하므로 남는다.

### P5 — 15개 파일의 동일 보일러플레이트

```
<fallback>Ask user for guidance when uncertain.</fallback>
```

`command-authoring.md:91`은 이 슬롯을 *"escalation path; use when out-of-scope handling is non-obvious"*로
한정한다. "모르면 물어봐"는 non-obvious의 반대다. 제대로 쓴 네 곳이 대조군이다 —
`load.md:60`(Serena 없을 때 대체 경로를 명시), `improve.md:38`(경계를 지목).

**반론이 가장 강한 항목이다.** 15개에서 빼면 코퍼스 구조가 불균일해진다. `content-quality.md:80`은
일관성보다 deletion test를 우선하라고 하지만, 여기서 갈리는 판단은 합리적이다.

### P6 — 시스템 프롬프트가 이미 가진 로스터

`commands/sc.md`(33줄)와 `commands/help.md`(31줄)가 같은 커맨드 목록을 다른 문구로 각각 들고 있다.
`command-authoring.md:36`이 왜 죽은 텍스트인지 설명한다 — *"Commands install as CC skills — the harness
exposes each `description` to the model."* 35개 description이 이미 시스템 프롬프트에 있다.

**두 로스터 다 이미 낡았다** — 실제 커맨드는 35개인데 33개와 31개다. `sc.md:79`의 자체 gotcha
(`stale-list: Command list may go outdated`)가 예고한 그대로다.

### P7 — 죽은 참조 한 건 (확인 완료)

```
skills/README.md:74   okf/superclaude/skills/index.md — OKF v0.1 catalog: 5 skills as concept docs
```

`okf/superclaude/`에 `skills/`만 없다. 형제 포인터(`commands/index.md`, `core/index.md`)는 살아 있다.
서브에이전트는 부분 체크아웃 때문에 판정을 보류했고, 전체 트리에서 확인한 결과 이 한 건만 sediment다.

### P8 — 명세끼리 충돌하는 두 곳

- `core/FLAGS.md:13` `--token-efficient: ctx >75%` vs `:42` `--uc: ... trigger >=60% ctx`.
  `:13`이 `(see <output> --uc)`로 둘을 같다고 선언하면서 임계값은 다르다. 65% 지점에서 반대 답이 나온다.
- `skills/README.md:11` `Tool restriction (allowed-tools) | Only skills whitelist tools at runtime` vs
  `.claude/rules/skill-authoring.md:146` `permission-grant, not access-restriction — non-listed tools
  remain callable but require user approval`. 둘 다 맞을 수는 없고, README를 믿은 저자는 진짜 제한을
  만드는 hook을 추가하지 않는다.

---

## 3. 실제로 무게를 지고 있는 것

프루닝 목록만 보면 그림이 왜곡되므로 반대편도 적는다.

**남는 것의 공통 성질은 "모델이 주장할 수 있는 것을 제약한다"이다.** Anthropic 지침이 유지·강화를 권고한
범주이고, deletion test를 통과한다.

- `core/RULES.md:19` — 증거 없이 통과를 주장하지 말 것, 실제 출력을 인용할 것
- `core/RULES.md:23` — 파괴적 작업 확인
- `core/rules/RULES_DELEGATION.md` — 거의 전부. 검사한 모든 줄이 구별 가능한 제약을 담는다
- `core/rules/RULES_INTERACTION.md` — 6줄 전부가 렌더링 출력 계약. 지우면 화면이 바뀐다
- `core/rules/RULES_DOCS.md` — 명명·위치 컨벤션
- `commands/auto-improve.md` — 코퍼스에서 가장 깨끗하다. PID 파일 위치, `--eval-cmd` blast radius,
  mutator의 도구 표면 — 전부 모델이 유도할 수 없는 운영 사실
- `commands/insight.md`, `commands/research.md`, `commands/index-repo.md`, `commands/improve.md`, `commands/reflect.md`
- `skills/ship`, `skills/finishing-a-development-branch`의 **hook** — 각각 전역 `destructive_guard.py`에 없는
  커버리지를 추가한다(전역은 `main|master` 강제 푸시만 하드 차단, ship은 모든 브랜치; 전역은
  `git branch -D`를 warn 티어로, 이쪽은 하드 차단). ARCHITECTURE의 Enforcement Boundary가 말하는
  "가치가 강제되는 층에 있는" 사례
- `skills/verbalized-sampling` — 분포 수준 프롬프팅은 모델 네이티브가 아니다. 다만 자체 파라미터 규칙을
  여섯 곳에서 반복하고 16KB 레퍼런스의 로드 조건이 무조건적이거나 없다

**패턴**: 지키는 값은 *주장 제약*과 *유도 불가능한 운영 사실*에 있고, 죽은 무게는 *권고형 레지스터*
("범위를 지켜라", "코드를 믿어라", "병렬로 생각하라")에 몰려 있다. `PRINCIPLES.md`가 그 농도가 가장 높다 —
36줄 중 `<directive>` 절, `Restraint-First`, `Parallel-Thinking`, `<decisions>` 대부분이 걸린다.

---

## 4. 한 가지 구조적 레버

D1·D2·D6은 같은 형태다 — **커맨드가 시스템의 어느 단계도 생산하지 않는 숫자나 토큰으로 게이트를 건다.**
`tests/unit/test_command_structure.py`에 기계적 검사 하나를 더하면 셋 다, 그리고 D5의
`init.md` 9개 옵션(`RULES_INTERACTION.md:8`의 max 7 위반)까지 잡힌다.

> 커맨드 본문의 모든 수치 임계값과 리터럴 토큰 매처는, 비교 대상 값을 생산하는 단계나 파일을 명시해야 한다.

D4는 다른 축이다. `context_loader.py`의 `TRIGGER_MAP`을 각 커맨드 본문과 대조해서, 커맨드가 의존하거나
모순되는 규칙을 로더가 그 커맨드에 배달하지 않으면 결함으로 본다 — 이쪽도 기계적으로 검사 가능하다.

---

## 5. 이 감사가 하지 않은 것

- **행동 실행 없음.** D1~D6을 제외한 모든 deletion effect는 텍스트에서 추론한 것이다. D3·P5·P6이 실제
  프로브 가치가 가장 높다. 프로브는 저장소 **바깥**에서 돌려야 한다(`gotchas/authoring.md`의
  `probe-observer-effect`).
- **P1의 측정은 상속된 것이다.** n=1, sonnet, 프롬프트 4종. 문장 단위가 아니라 프레임워크 단위 제거였다.
  문장 단위로 증명하려면 그 문장만 뺀 아암이 필요하다.
- **검색 위치 효과 미측정.** P3은 "컨텍스트 안에 있으면 동등하게 접근된다"를 가정한다. 표준 가정이지만
  이 저장소에서 검증된 적은 없다.
- **얕게 본 것**: `core/BUSINESS_SYMBOLS.md`의 심볼 표, `verbalized-sampling/references/examples.md` 본문,
  `agents/` 전체(범위 밖).
