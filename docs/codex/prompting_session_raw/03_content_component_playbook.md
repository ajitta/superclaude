---
title: 콘텐츠 구성요소 개선 플레이북
status: working-guide
last_verified: 2026-08-22
applies_to:
  - src/superclaude/CLAUDE_SC.md
  - src/superclaude/core
  - src/superclaude/agents
  - src/superclaude/commands
  - src/superclaude/modes
  - src/superclaude/mcp
  - src/superclaude/skills
---

# 콘텐츠 구성요소 개선 플레이북

## 1. 공통 개선 루프

```text
관찰된 실패
→ component/delivery path 분류
→ 현재 SSOT와 테스트 확인
→ 실패 원인 분류
→ 최소 변경 가설
→ 구조·연결 gate
→ 실제 행동 비교
→ 회귀 없을 때 채택
```

추측으로 “더 좋은 문장”을 추가하지 않는다. 다음 중 하나가 있어야 개선 작업을
시작한다.

- 재현 가능한 잘못된 선택·행동
- source와 install/artifact의 drift
- 저작 규칙과 validator의 모순
- dead reference, unmapped content, stale instruction
- 측정된 context/token 비용
- 새로운 upstream contract에 대한 1차 근거

## 2. 먼저 올바른 타입을 고른다

| 질문 | 선택 |
|---|---|
| 모든 세션이 반드시 알아야 하는 invariant인가? | `core` kernel |
| 특정 상황에서만 필요한 framework rule인가? | `core/rules` |
| 사용자가 호출하는 순서 있는 workflow인가? | `command` |
| 독립된 domain 전문성이 필요한가? | `agent` |
| 사고·표현·우선순위의 자세만 바꾸는가? | `mode` |
| hook·script·invocation control 같은 CC-native capability인가? | `skill` |
| MCP를 SC workflow에서 언제/어떻게 조합할지 설명하는가? | `mcp` |

새 요소를 만들기 전에 인접 요소에서 중복·침전·무효 문장을 삭제하거나 기존
contract를 좁혀 해결할 수 있는지 확인한다.

## 3. 공통 리뷰 계약

### Hard gates

- 원래 intent와 explicit constraint가 보존된다.
- frontmatter/XML은 해당 타입의 현행 규칙과 validator에 모두 맞는다.
- source file, catalog/README, handoff, loader, installer edge가 끊기지 않는다.
- component가 읽히지 않는 경로에 존재하는 dead content가 아니다.
- side effect와 permission boundary가 사용자 권한을 넘지 않는다.
- 완료·검증 주장은 실제 실행 증거에 연결된다.
- 치명적 행동 회귀가 없다.

### Soft metrics

- description/body token cost
- trigger precision과 recall
- 불필요한 질문, tool call, delegation, file change
- latency와 실행 비용
- 문장 또는 block을 제거했을 때의 성능 차이

## 4. `CLAUDE_SC.md`와 `core/`

### 분석 질문

1. 이 지시는 항상 필요하며 손실 비용이 큰가?
2. 이미 kernel 또는 on-demand module에 같은 답이 있는가?
3. rule이 실제로 `context_loader`를 통해 필요한 prompt에 전달되는가?
4. prose로 선언한 제약 중 hook으로 강제해야 할 것이 있는가?
5. 다른 core 문장과 임계값·우선순위가 모순되지 않는가?

### 변경 규칙

- always-loaded chain은 가능한 작게 유지한다.
- 자세한 verification/delegation/docs/interaction 규칙은 기존 on-demand module을
  SSOT로 사용한다.
- rule ID, flag, threshold를 추가하면 정의·참조·loader·README를 함께 갱신한다.
- framework-wide 금지는 반복 실패와 behavioral regression evidence가 있을 때만
  추가한다.

### 필수 검증

```bash
uv run pytest tests/unit/test_context_loader.py -v
uv run pytest tests/unit/test_content_usage.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
uv run pytest tests/unit/test_eval_harness.py -v
```

현재 `core/`에는 전용 authoring guide와 완전한 structural validator가 없다.
따라서 core 변경은 관련 behavioral task 또는 새 canary 없이는 완료로 보지 않는다.

## 5. `agents/`

SSOT: `.claude/rules/agent-authoring.md`.

### 분석 질문

- 이 전문성이 built-in Explore/Plan/general-purpose와 구별되는가?
- description이 인접 agent와 선택 경계를 명확히 하는가?
- delegated session이 parent system/skill을 상속하지 않아도 self-contained인가?
- tool/permission/model/memory가 최소 권한이며 scope rewrite와 맞는가?
- output이 결론, 근거, 반대 근거, 미확인 사항, parent implication을 제공하는가?

### 개선 체크리스트

- filename, `name`, component name을 동일하게 유지한다.
- source의 `memory`는 project를 기준으로 하고 installer rewrite를 검증한다.
- `tools`와 `disallowedTools` 중 하나만 선택한다.
- `effort`/model override는 측정 근거가 없으면 생략한다.
- description에서 과거 작업·경험을 암시해 context hallucination을 유발하지 않는다.
- memory와 gotcha는 미래 실행을 실제로 바꾸는 정보만 남긴다.
- agent가 코드를 읽는다면 symbolic exploration guidance가 현재 도구 계약과
  일치하는지 확인한다.

### 필수 검증

```bash
uv run pytest tests/unit/test_agent_structure.py -v
uv run pytest tests/unit/test_cross_references.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
```

구조 테스트만으로는 agent 선택 정확도를 알 수 없다. 인접 agent positive/negative,
no-agent, compound-domain prompt를 behavioral fixture로 검증한다.

## 6. `commands/`

SSOT: `.claude/rules/command-authoring.md`.

### 분석 질문

- 정말 `/sc:*` workflow가 필요한가, 아니면 직접 답변/도구 호출이면 충분한가?
- auto-triggerable과 explicit-only 중 어느 tier인가?
- description의 negative gate가 가장 가까운 오호출을 명시하는가?
- flow 각 단계가 구체적 artifact/state를 만들며 순서가 load-bearing인가?
- handoff가 존재하고 실제 다음 단계로 자연스러운가?

### 개선 체크리스트

- mutation, multi-agent, 장기 실행, artifact commit은 기본적으로 explicit-only다.
- guaranteed auto-block이 필요할 때만 `disable-model-invocation`을 사용한다.
- `<flow>`의 “validate”는 검사 대상과 기준을 구체적으로 적는다.
- 수치 threshold나 literal token을 쓰면 그 값을 생산하는 단계·파일을 함께
  지목한다.
- roster를 본문에 복제하지 말고 native discovery/catalog를 활용한다.

### 필수 검증

```bash
uv run pytest tests/unit/test_command_structure.py -v
uv run pytest tests/unit/test_cross_references.py -v
uv run pytest tests/unit/test_context_loader.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
```

정적 description 검사는 실제 wrong-fire를 증명하지 않는다. positive, negative,
adjacent prompt를 같은 모델·환경에서 실행하고 오호출을 hard failure로 둔다.

## 7. `modes/`

SSOT: `.claude/rules/mode-authoring.md`.

### 개선 체크리스트

- thinking, communication, priorities, behaviors 네 축을 모두 유지한다.
- step-by-step workflow는 command로, tool routing은 FLAGS로 이동한다.
- optional outcomes는 네 축에 없는 실제 directive만 담는다.
- `TRIGGER_MAP`, flag 문서, README row를 함께 갱신한다.
- neutral prompt에서 잘못 활성화되지 않고, 복합 flag에서 우선순위가 유지되는지
  확인한다.

### 필수 검증

```bash
uv run pytest tests/unit/test_mode_structure.py -v
uv run pytest tests/unit/test_content_structure.py -v
uv run pytest tests/unit/test_content_usage.py -v
uv run pytest tests/unit/test_context_loader.py -v
```

`RESEARCH_CONFIG.md`는 현재 `MODE_*.md` fixture 밖에 있으므로 별도 schema/check가
필요하다.

## 8. `mcp/`

SSOT: `.claude/rules/mcp-authoring.md`.

### 개선 체크리스트

- tool inventory가 아니라 선택·call order·integration·fallback만 둔다.
- 새 파일을 `TRIGGER_MAP`과 실제 tier policy에 등록한다.
- behavioral MCP와 tool MCP의 injection tier를 구분한다.
- server unavailable, native-tool fallback, untrusted result를 다룬다.
- 설치·version 정보는 MCP body가 아니라 installer/README 소관에 둔다.

### 필수 검증

```bash
uv run pytest tests/unit/test_content_structure.py -v
uv run pytest tests/unit/test_content_usage.py -v
uv run pytest tests/unit/test_context_loader.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
```

저작 문서, tiered loader, standalone validator가 서로 다른 injection 가정을 갖지
않도록 하나의 machine-readable mapping을 SSOT로 삼는 것이 우선 개선 후보다.

## 9. `skills/`

SSOT: `.claude/rules/skill-authoring.md`.

### 개선 체크리스트

- reference, workflow, background 중 archetype을 먼저 결정한다.
- side-effect workflow는 `disable-model-invocation: true`를 사용한다.
- trigger는 description 앞부분에 두고 인접 skill과 구별한다.
- `SKILL.md`에는 항상 필요한 절차만 두고 상세 reference를 분리한다.
- `{{SKILLS_PATH}}`, `{{SCRIPTS_PATH}}`, portable runtime variable의 적용 위치를
  확인한다.
- scripts/references/assets link가 source와 설치본 모두에서 살아 있는지 검사한다.
- hook은 narration이 아니라 실제 block/allow 결과로 검증한다.

### 필수 검증

```bash
uv run pytest tests/unit/test_skill_structure.py -v
uv run pytest tests/integration/test_cross_directory_refs.py -v
uv run pytest tests/integration/test_skill_canary.py -m canary -v
```

canary는 외부 Claude CLI를 사용하므로 비용·인증이 필요한 조건부 gate다. 최소한
auto-invoked skill은 positive와 negative case를 가져야 하고, explicit-only skill은
자동 호출되지 않는다는 case가 필요하다.

현재 authoring guide가 허용하는 `model`, `context: fork`, `agent`와 구조 테스트의
금지 정책이 충돌한다. 새 skill에서 해당 필드를 쓰기 전에
[`08_current_findings_and_backlog.md`](08_current_findings_and_backlog.md)의 `F-005`를
해결한다.

## 10. 삭제·ablation 리뷰

문장 또는 block마다 다음을 기록한다.

```yaml
content_unit: 파일과 section
claimed_behavior: 이 문장이 바꾼다고 주장하는 행동
failure_case: 없으면 삭제 후보
ablation_arm: 해당 unit만 제거한 variant
hard_gate_delta: critical 실패 변화
soft_metric_delta: token/tool/latency 변화
decision: keep|rewrite|move-to-reference|delete
```

한 문장이 전문 용어 하나로 대체 가능하거나, 제거 전후 outcome이 같거나, 다른
SSOT의 완전한 사본이면 삭제 또는 pointer 전환을 우선한다.
