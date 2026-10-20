---
status: draft
revised: 2026-10-20
---

# 남은 작업 (2026-10-20, v4.34.0 이후)

2026-10-19–20에 작업 세 갈래를 마쳤다.
- 설치·업그레이드 감사와 Windows 실기 검증: v4.30.5까지 릴리스.
- `CLAUDE_CONFIG_DIR` 지원(ADR-0002, v4.31.0).
- 압박 프로브 측정: hurry 프로브에서 sc-full 30/30 vs vanilla 20/30, p = 0.0004. 이때 eval arm 격리 결함 두 개를 찾아 고쳤다.
- 에이전트 감사: 24개 중 19개 폐기, 5개 유지(v4.32.0, [agent-roster-audit](../features/agent-roster-audit/README.md)).

그 뒤 같은 날 v4.32.2–v4.34.0을 릴리스했다: `/sc:intent`의 `Done when:` 줄, `--through`(의도 한 줄로 체인 끝까지), 독립 검증 세 번과 반영, `/sc:plan`의 design 승인, command 본문 릴리스 게이트(`make canary-commands`), `--through --ask`(결과를 좌우하는 결정만 한 번 묻기). 기록은 [goal-chain](../features/goal-chain/README.md) 06–06g에 있다.

다음 세션이 바로 할 일은 0절의 두 항목이다. 둘 다 소유자 결정이 필요하다. 남은 것은 다음 릴리스에 함께 나갈 변경, 다음 모델이 나올 때 할 일, 보류 항목, 정리 작업이다. 지난 목록은 [remaining-work-ajitta-2026-10-19](./remaining-work-ajitta-2026-10-19.md)이고, 이 문서가 그것을 대체한다.

항목마다 소유자 결정이 필요한지와 추천안(★)을 적는다. 세션 상태는 `.claude/memories/session_2026-10-20_master.md`의 Next actions에 같은 목록이 짧게 있다.

## 0. 다음 세션에서 진행할 것 — goal-chain 후속

시작: `cd ~/superclaude && git fetch origin && git checkout master && git merge --ff-only origin/master`, 그다음 [goal-chain 06g](../features/goal-chain/06g-ask-review-applied.md)와 [06e](../features/goal-chain/06e-ask-checkpoint.md)의 Limits를 읽는다. 두 항목 모두 command·agent 본문을 바꾸므로 릴리스 전에 `make canary-commands`를 돌린다(4.33.2부터 게이트가 요구한다).

### 0-1. brainstorm 결정 모드: 선택지 밖의 직접 답(Other)

- [ ] 현상: `--ask` 체크포인트는 "답이면 Other 텍스트도 `confirmed`"로 정했다(`commands/intent.md` Checkpoint 단계). 그런데 `/sc:brainstorm`의 `<decision_modes>`(`commands/brainstorm.md`)에는 Other나 자기 말로 쓴 답에 대한 규칙이 없다. 라벨도 라벨 단어도 아니면 "When neither rule clearly applies, tag delegated"로 떨어진다. 사용자가 직접 새 선택지를 말해도 `delegated`로 기록되고, `--audit-delegated` 감사가 그 행을 모델끼리 다시 정한다. 사용자의 말이 모델 판단으로 덮일 수 있다는 뜻이다. 근거: [06f](../features/goal-chain/06f-verify-ask.md) 발견 3과 "이 브랜치 밖의 메모", run 24의 `D3 기타: …` 답(06e).
- 결정: 규칙.
  - ★(a) 하나의 구체적인 선택을 말하는 Other/자기 말 답은 `confirmed`로 두고, 그 텍스트를 선택지로 기록한다. 질문·망설임·조건부("잘 모르겠는데 아마 b?")는 `delegated`.
  - (b) 항상 `delegated`로 두고 감사에 맡긴다. 단순하지만 위의 덮어쓰기 문제가 남는다.
  - (c) 새 선택지로 받아 적은 뒤 한 번 더 확인 질문을 한다. 정확하지만 왕복이 하나 늘어난다.
- 작업(★a일 때): `brainstorm.md` `<decision_modes>`의 confirmed 정의에 한 줄을 더한다. intent Checkpoint의 "even where the /sc:brainstorm Decision-mode tag step would say delegated" 예외가 필요 없어지면 그 구절도 정리한다. 보류 중인 "결정 모드 판정 프로브"(4a절)에 Other 사례를 넣을지 함께 정한다. `uv run pytest tests/unit/test_command_structure.py`, 전체 suite, `make canary-commands`.

### 0-2. self-review 에이전트의 메모리 폴더가 사용자 저장소에 남는다

- [ ] 현상: run 28(opus, 06e)에서 branch review를 맡은 `self-review` 에이전트가 `.claude/agent-memory/self-review/review_patterns.md`를 썼다. 이 폴더는 커밋되지 않은 채 남았고, `--through`는 지우지 않고 사용자에게 물었다(삭제는 확인 규칙에 맞는 행동이다). 원인: 에이전트 소스는 모두 `memory: project`이고, project 설치에서는 `.claude/agent-memory/<agent>/`에 쓴다(`.claude/rules/agent-authoring.md` § memory). canary 작업공간은 `WS_GITIGNORE`(`evals/run_eval.py`)가 이 경로를 무시하므로, 새 clean-tree 검사도 이 경우를 보지 못한다.
- 관련: 4a절 N4 항목이 이미 "`self-review`가 `memory: project`라서 같은 스펙에 대한 이전 판정을 읽을 수 있다"를 독립성 위험으로 적어 두었다.
- 결정: 처리 방식. 시작 전에 현재 Claude Code 문서에서 `memory` 범위(user/project/local)와 local 범위가 git에서 어떻게 다뤄지는지 확인한다.
  - ★(a, 잠정) `self-review`(와 `verifier`)는 독립 검토자이므로 이전 판정을 기억하지 않게 한다. superclaude는 `memory` 필드를 필수로 요구하므로(`agent-authoring.md`) 규칙과 installer의 `_rewrite_agent_memory_scope`도 함께 바꿔야 한다.
  - (b) project 설치에서도 검토 에이전트만 `memory: local`로 둔다. 폴더가 `.claude/agent-memory-local/`로 바뀌므로 git에서의 처리를 문서로 먼저 확인한다.
  - (c) 동작은 그대로 두고, `--through`의 Run 단계가 메모리 쓰기를 해당 단계 커밋에 포함하게 한다. CC 설계상 project 메모리는 공유용이지만 feature diff에 무관한 파일이 섞인다.
- 함께 할 일: 어떤 안이든 probe가 이 경우를 보게 한다. 예: `intent-through-*` probe의 clean-tree 검사가 `.claude/agent-memory/`를 무시하지 않도록 하거나, 별도 검사를 둔다.

## 1. 다음 릴리스에 함께 나갈 것 — 완료

- [x] CHANGELOG `[Unreleased]`의 contributor용 항목 세 개(eval arm 격리, `sc-command-only` core import 제거, `probe-verify-claim` grader)는 v4.32.0에 함께 나갔다.

## 2. 압박 프로브 후속 — [pressure-readout](../features/pressure-readout/README.md)

- [ ] dictated-fix와 sunk-cost 프로브는 sonnet low에서 두 arm 모두 ceiling(9–10/10)이라 arm을 가르지 못한다. 결정: (a) regression guard로만 유지 / (b) 더 어려운 변형을 설계. ★(a). 다음 모델 canary에서 다시 본다.
- [ ] opus와 auto permission mode 측정. 결정: 할지 말지. ★보류. 한다면 격리된 harness에서 새로 pre-register한다. 측정을 시작하기 *전에* 커밋한다.
- [ ] 행렬 task `bugfix-scope-creep`은 아직 느슨한 `pytest|python -m pytest` grader를 쓴다. 결정: 시점. ★다음 모델의 행렬 run 때 맞춘다. 어차피 그때 기준선을 새로 잡는다.

## 3. 모델 세대 재감사(축 B)

- [ ] 다음 Claude 모델이 나오면 `superclaude-model-release` 절차로 진행한다. 이번에 처음으로 격리된 canary 기준선이 생겼다(`make canary-gates`, 2026-10-20, 7/7 gates). 그 전 run은 계정 콘텐츠가 실린 상태라 비교 기준으로 쓰지 않는다.

결정: 시점. ★다음 모델 출시 때. Fable 계열은 headless `claude -p`로 돌리지 않는다(사용 크레딧 청구, `evals/README.md`).

## 4. 보류 항목

- [ ] C-16: `19091b37` 시기의 `python .claude/hooks/x.py` 설치. install이 아무 말도 하지 않고, `session_init`이 두 번 돌고, uninstall이 명령 3개와 `hooks/*.py`를 남긴다([04a-handoff §2](../features/install-upgrade-audit/04a-handoff.md)).
- [ ] C-17: `bd356afa` → `52b5517e` 시기의 local/project hook 상태가 `~/.claude/.superclaude_hooks/`에 남는다. local·project uninstall은 그 디렉터리에 닿지도 않고 보고하지도 않는다.
- [ ] opus 후속 라운드(N2/N5): `purpose_before_action`의 opus D3a는 양(+)이지만 검정력이 부족했다(13/20 vs 8/20, p = 0.103). 그 run에는 계정 콘텐츠가 실려 있었다([purpose-opus 04](../features/purpose-opus/04-readout.md)의 caveat 참조). 재개한다면 격리된 harness에서 새로 pre-register하고, arm당 50–55회가 필요하다.
- [ ] "참조가 가리키는 파일을 연다" 규칙 문구 시험([purpose-generalization 04](../features/purpose-generalization/04-readout.md) §2).
- [ ] `origin/fix/plain-language-structure`: 10-10에 멈춘 문장 길이·구조 작업이다. 병합되지 않은 WIP 커밋 10개가 있다.

결정: 각각 재개 여부. ★모두 보류 유지. C-16/C-17은 해당 시기에 설치한 경우가 드물어 비용 대비 효과가 낮다. opus 라운드는 실행 비용이 크다.

## 4a. 약점 감사 후속 — [completion-proof](../features/completion-proof/README.md) (v4.32.1)

v4.32.1로 N1–N6을 릴리스했다. 남은 것은 측정과 보류 항목이다. 근거는 [약점 감사](../research/superclaude-weakness-audit-ajitta-2026-10-20.md) §4와 completion-proof의 `06-verify.md`에 있다.

- [ ] N4 효과 프로브: 격리된 draft 스펙 리뷰어가 `00-intent.md`와 스펙 사이의 반전을 잡는지 잰다. `self-review`가 `memory: project`라서 같은 스펙에 대한 이전 판정을 읽을 수 있는 경로도 함께 본다. 결정: 시점. ★다음 모델 canary 때. 서브에이전트를 관찰해야 해서 설계 비용이 크다.
- [ ] 결정 모드 판정 프로브: "2번", "1번으로", "a로 가자", "추천대로", "not the local cache"를 넣은 여러 턴짜리 프로브. ★보류. 실제로 잘못 분류된 사례가 나오면 그때 만든다.
- [ ] "유효한 RED"와 "통과시키려고 기대 결과를 바꾸면 따로 검토" 조항: 관찰된 실패가 없어 보류(`content-quality.md`). ★보류.
- [x] 원격 브랜치 `origin/docs/superclaude-weakness-research`: 내용이 master에 병합돼 있어 소유자 확인 후 삭제했다(2026-10-20).

## 5. 결정이 필요 없는 정리 작업

- [ ] Windows 설치를 최신 릴리스로 맞춘다(`superclaude doctor --scope <s>` → `make sync-*`). 소유자가 Windows 세션에서 한다.
- [ ] `docs/features/docs-ssot-audit/06-verify.md`가 약 29 KB로 Read 가드(30,000바이트)에 가깝다. 다음에 크게 덧붙일 때 `06b-…`로 나눈다.
- [ ] Windows에서 `0xC0000409` 중단이 다시 나오면 `git revert 3e64dc82`를 하고, `tests/unit/scripts/parallel_ab/`를 동시 부하에서 bisect한다(AGENTS.md Tests).

## 남겨 둔 알려진 한계

고치지 않기로 받아들인 동작이다. 근거는 [03-findings](../features/install-upgrade-audit/03-findings.md)의 C-20·C-21 행에 있다.

- 끝 줄바꿈이 없던 CLAUDE 파일은 install 후 uninstall을 거치면 줄바꿈이 하나 생긴다.
- `settings.json`의 한 줄 안 공백, 숫자 표기(`1e3`), 이스케이프(`\/`)는 다시 직렬화된다.
- 2026-10-20 이전의 eval 결과에는 claude.ai 계정 콘텐츠가 세션마다 다르게 실려 있었다. 다시 돌리지 않고, 격리된 run과 pool하지 않는다.
